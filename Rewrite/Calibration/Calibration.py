'''
Docstring for Calibration.Calibration
Ce fichier contient tout le code "dur" pour calibrer le Maze.
C'est ce code qu'il faut modifier en cas de changement de géométrie du Maze.
'''

from pathlib import Path
import cv2
from tqdm import tqdm
import numpy as np
from Calibration.Parameters import width_mask, height_mask, LAB_NAMES
from Calibration.Models import Maze, Chamber


class ManualCalibration:

    def __init__(self, chambers_model, mask_points):

        self.homography = None
        self.auto = False

        self.chambers_model = chambers_model # Points des centres des chambres du masque
        self.mask_points = mask_points

    def compute_homography(self, frame_pts):
        '''
        :param mask_pts: Points qui ont été définis sur le masque
        :param frame_pts: Points sur lesquels l'utilisateur a cliqué, correspondant aux mask_pts
        Permet de calculer la matrice d'homographie, permettant de savoir comment agrandir le masque pour
        qu'il colle à la frame_1.
        '''
        self.homography, _ = cv2.findHomography(self.mask_points, frame_pts, cv2.RANSAC)
        return self.homography

    def project_chambers(self, homography):
        '''        
        Cette fonction permet ensuite de calculer la position du centre des chambres grâce à la matrice d'homographie.
        On créé ensuite des instances de chambres.
        '''
        chambers = {}
        for ch_id, (x, y) in self.chambers_model.items():
            pt = np.array([[[x, y]]], dtype=np.float32)
            proj = cv2.perspectiveTransform(pt, homography)
            chambers[ch_id] = Chamber(tuple(proj[0][0]))
        return(chambers)


    def decoupe_Mazes(self, labs, video_path, output):
        '''
        Docstring for decoupe_Mazes
        
        :param self: Description
        :param clicked_points: Description
        
        Cette fonction est utilisée pour découper la vidéo en 2*N_MAZES vidéos, pour que
        l'algorithme de détection des larves puisse fonctionner.
        La vidéo découpée est ensuite enregistrée.
        Comme les Mazes sont symétriques, on découpe chaque Maze en deux, pour que l'algorithme puisse se concentrer sur une moitié à la fois.
        
        Cette fonction doit être changée en fonction du choix de la géométrie du support des Mazes.
        '''

        # Dimensions de sortie de la vidéo        
        width, height = width_mask, height_mask
        middle = height // 2
        video = cv2.VideoCapture(video_path)
        
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        pbar = tqdm(total=total_frames, desc="Découpe des Mazes")
        
        lab_data = []
        
        for lab in labs:
            lab_name = LAB_NAMES[lab.id - 1]
            lab_folder = Path(output) / f"Maze_{lab_name}"
            lab_folder.mkdir(parents=True, exist_ok=True)
            
            # Attention, ici les noms sont inversés par construction 
            output_path_top = lab_folder / f"Maze_{lab_name}_bottom.mp4"
            output_path_bottom = lab_folder / f"Maze_{lab_name}_top.mp4"

            fps = video.get(cv2.CAP_PROP_FPS)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            writer_top = cv2.VideoWriter(output_path_top, fourcc, fps, (width, middle))
            writer_bottom = cv2.VideoWriter(output_path_bottom, fourcc, fps, (width, height - middle))
            
            src_points = np.array(lab.clicked_points, dtype=np.float32)
            
            zoomed_points = np.array([
            [0, 0], [width-1, 0], # coins haut-gauche et haut-droit
            [width-1, height-1], [0, height-1] # coins bas-gauche et bas droit
            ], dtype=np.float32)
            
            homography = cv2.getPerspectiveTransform(src_points, zoomed_points)
            map_x, map_y = cv2.initUndistortRectifyMap(
                np.eye(3), None, homography, np.eye(3),
                (width, height), cv2.CV_32FC1
            )

            map_x_gpu = cv2.cuda_GpuMat()
            map_y_gpu = cv2.cuda_GpuMat()
            map_x_gpu.upload(map_x)
            map_y_gpu.upload(map_y)

            lab_data.append((map_x_gpu, map_y_gpu, writer_top, writer_bottom, lab_folder, lab_name))

        gpu_frame = cv2.cuda_GpuMat()

                     
        while True:
            ret, frame = video.read()
            pbar.update(1)
            gpu_frame.upload(frame)
            if not ret:
                break
            
        for map_x_gpu, map_y_gpu, writer_top, writer_bottom, _, _ in lab_data:
    
            warped_gpu = cv2.cuda.remap(
                gpu_frame, map_x_gpu, map_y_gpu, interpolation=cv2.INTER_LINEAR
            )

            warped = warped_gpu.download()

            top_half = warped[:middle, :]
            bottom_half = warped[middle:, :]

            writer_top.write(top_half)
            writer_bottom.write(bottom_half)
            
        video.release()
        pbar.close()

        for _, _, writer_top, writer_bottom, folder, name in lab_data:
            writer_top.release()
            writer_bottom.release()

            (folder / "calibration_done.txt").write_text("done")
            print(f"Maze {name} découpé.")
    
    
    
    def calibrate_Maze(self, lab_id, clicked_points):
        '''
        :param lab_id: Identifiant du Maze considéré
        On applique les deux fonctions précédentes et on renvoie les instances de Mazes
        '''
        
        lab = Maze(lab_id)
        self.homography = self.compute_homography(np.array(clicked_points))
        lab.homography = self.homography
        lab.clicked_points = clicked_points
        chambers = self.project_chambers(self.homography)
        lab.chambers = chambers
        return lab
    



# Si jamais j'ai le temps, je pourrai essayer de rendre la calibration semi-automatique, avec 
# une vérification humaine du placement des chambres
class AutoCalibration:
    def __init__(self):
        return(None)
