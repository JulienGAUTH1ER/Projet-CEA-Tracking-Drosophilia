
import cv2
from pathlib import Path
from Calibration.Parameters import MASK_POINTS, CHAMBERS_MODEL, LAB_NAMES, ROOM_NAMES
from Calibration.Gui import GuiCalibration
from Calibration.Calibration import ManualCalibration
from Parameters import NB_MAZES



def main_calibration(video_path):
    '''
    Docstring for main_calibration
    
    :param video_path: chemin de la vidéo à calibrer
    Cette fonction permet d'exécuter toutes les étapes de la calibration.
    La calibration n'est pas refaite si les fichiers de calibration existent déjà.
    '''
    
    output_root = Path(video_path).parent / "Mazes"
        
    gui = GuiCalibration(video_path)

    calibration = ManualCalibration(
        chambers_model=CHAMBERS_MODEL,
        mask_points=MASK_POINTS
    )

    labs = []
    lab_id = 1

    while lab_id <= NB_MAZES:
        
        print(f"\n=== Calibration du Maze {lab_id}/{NB_MAZES} ===")
        lab_name = LAB_NAMES[lab_id - 1]
        lab_folder = output_root / f"Maze_{lab_name}"
        txt_file = lab_folder / "calibration_done.txt"
        if txt_file.exists():
            print(f"✔ Maze {lab_name} déjà calibré")
            lab_id += 1
            continue
        
        state, clicked_points = gui.select_Maze()

        if not state:
            print("Calibration annulée par l'utilisateur")
            return

        lab = calibration.calibrate_Maze(
            lab_id=lab_id,
            clicked_points=clicked_points
        )
        
        video = cv2.VideoCapture(video_path)
        success, frame = video.read()
        video.release()

        if not success:
            raise RuntimeError("Impossible de lire la première frame")

        key = gui.validate_calibration(frame, lab.chambers, lab_id)
        
        if key == ord('r'):
            print("↩ Recalibration du Maze en cours")
            continue

        if key == 27:  # ESC
            print("Calibration interrompue")
            return

        labs.append(lab)
        lab_id += 1
        
    output_root = Path(video_path).parent / "Mazes"
    output_root.mkdir(exist_ok=True)
    calibration.decoupe_Mazes(labs, video_path, output_root)
    
    return(labs)
