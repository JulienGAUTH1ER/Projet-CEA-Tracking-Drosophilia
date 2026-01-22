'''
Docstring for Réécriture.Maze_class

Ce fichier permet de faire l'initialisation du labyrinthe.
Il faut fournir le centre de chaque labyrinthe pour une meilleure initialisation de l'algorihme de tracking.
Ce code permet :
- D'extraire la première frame de la vidéo du labyrinthe
- De calibrer les zones de recherches pour l'algorithme de détection de position
- De nommer les différentes zones du labyrinthe selon le placement des odeurs
'''

import cv2
import os


class Maze():
    '''
    Docstring for Maze
    La classe Maze doit lire la vidéo du labyrinthe et initialiser les différentes zones.
    On extrait la première frame de la vidéo pour permettre la calibration.
    On demande ensuite à l'utilisateur:
    - La position des chambres
    - Les caractéristiques de chaque chambre    
    '''
    def __init__(self, video_path):
        self.video_capture = cv2.VideoCapture(video_path) # Ouvre la vidéo du labyrinthe
        success, self.frame_1 = self.video_capture.read() # Extrait la première frame
        if not success:
            raise ValueError("Impossible de lire la vidéo ou d'extraire la première frame.")
        else :
            # On construit des dictionnaires où on donne un nom à chaque chambre Ex : {'Chambre_1' : [x_1, y_1]}
            self.chamber_placements = {}
            self.odor_placements = {}
            self.larva_placement = {}
            self.key_points = []
            
            self.nb_labyrinthes = 0
            self.nb_chambres = 0




    def ajouter_clicks(self, event, x, y, flags, indexes):
        lab_index, chamber_index = indexes
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Clic à : ({x}, {y})")
            self.chamber_placements[f'Labyrinthe_{lab_index}'][f'Chambre_{chamber_index}'] = (x, y)
            cv2.circle(self.frame_1, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Fenetre de calibration", self.frame_1)


    def calibrate_frame(self):
        '''
        Docstring for calibrate_frame
        Cette fonction permet de calibrer le labyrinthe en demandant à l'utilisateur de cliquer sur les points d'intérêt dans la frame extraite.
        Appuyer sur la touche "echap" permet de recommencer la calibration du labyrinthe
        '''
        # Le code est adaptatif aux différents labyrinthes qui peuvent être développés
        cv2.imshow("Fenetre de calibration", self.frame_1)
        cv2.waitKey(1)
        self.nb_labyrinthes = int(input("Combien il y a-t-il de labyrinthes ? "))
        self.nb_chambres = int(input("Combien il y a-t-il de chambres par labyrinthe ? "))
        cv2.destroyAllWindows()
        
        print("Veuillez calibrer les chambres en cliquant sur leur centre dans l'ordre.")
        
        for lab_index in range(1, self.nb_labyrinthes + 1):
            self.chamber_placements[f'Labyrinthe_{lab_index}'] = {}
            cv2.imshow("Fenetre de calibration",self.frame_1)
            for chamber_index in range(1, self.nb_chambres + 1):
                print(f"Cliquez sur le centre de la chambre {chamber_index} du labyrinthe {lab_index}.")
                self.chamber_placements[f'Labyrinthe_{lab_index}'][f'Chambre_{chamber_index}'] = None
                cv2.setMouseCallback("Fenetre de calibration", self.ajouter_clicks, (lab_index, chamber_index))
                while self.chamber_placements[f'Labyrinthe_{lab_index}'][f'Chambre_{chamber_index}'] is None:
                    cv2.waitKey(1)
                #print(self.chamber_placements)
                self.place_odors(lab_index, chamber_index)
            cv2.destroyAllWindows()
        return()
    
    def place_odors(self, lab_index, chamber_index):
        if f'Labyrinthe_{lab_index}' not in self.odor_placements:
            self.odor_placements[f'Labyrinthe_{lab_index}'] = {}
        concentration = str(input("Veuillez entrer la concentration choisie : "))
        odor = str(input("Veuillez entrer l'odeur choisie : "))
        self.odor_placements[f'Labyrinthe_{lab_index}'][f'Chambre_{chamber_index}'] = (concentration, odor)





####################################################################################################################
# Exemple d'utilisation de la classe Maze
base_dir = os.path.dirname(os.path.abspath(__file__))
print("Base directory:", base_dir)
# Les vidéos doivent être dans un dossier 'Data' à côté de ce script
# 'Data' -> Dossier de chaque expérience (libre de choisir le nom) -> 'Video' -> 'Video.avi'
data_dir = os.path.join(base_dir, 'Data')

# On parcourt toutes les vidéos dans le dossier Data
for folder_name in os.listdir(data_dir):
    folder_path = os.path.join(data_dir, folder_name)
    video_path = os.path.join(folder_path, 'Video', 'Video.avi')
    MonLabyrinthe = Maze(video_path)
    MonLabyrinthe.calibrate_frame()
    #print(f"First frame for {folder_name} extracted successfully.")

####################################################################################################################