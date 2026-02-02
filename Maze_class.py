'''
Docstring for Réécriture.Maze_class

Ce fichier permet de faire l'initialisation du labyrinthe.
Il faut fournir le centre de chaque labyrinthe pour une meilleure initialisation de l'algorihme de tracking.
Ce code permet :
- D'extraire la première frame de la vidéo du labyrinthe
- De calibrer les zones de recherches pour l'algorithme de détection de position
- De nommer les différentes zones du labyrinthe selon le placement des odeurs
Pour l'instant toutes les étapes d'initialisation sont faites à la main, elles pourront cependant être automatisées par la suite.
'''

import cv2
import os


class Maze():
    '''
    Docstring for Maze
    La classe Maze doit lire la vidéo du labyrinthe et initialiser les différentes zones.
    On extrait la première frame de la vidéo pour permettre la calibration.
    On initialise ensuite deux dictionnaires qui donneront la position du centre des chambres, et les paramètres qui
    ont été choisis pour chaque chambre (odeurs / concentrations).
    '''
    def __init__(self, video_path):
        self.video_capture = cv2.VideoCapture(video_path) # Ouvre la vidéo du labyrinthe
        success, self.frame_1 = self.video_capture.read() # Extrait la première frame
        if not success:
            raise ValueError("Impossible de lire la vidéo ou d'extraire la première frame.")
        else :
            # On construit des dictionnaires où on donne un nom à chaque chambre Ex : {'Labyrinthe_1' : {'Chambre_1' : (x_1, y_1), 
            #                                                                                            'Chambre_2' : (x_2, y_2)}}
            self.chamber_placements = {}                                                                            
            self.odor_placements = {}
            

    def set_chamber(self, lab_index, chamber_index, x, y):
        if f"Labyrinthe_{lab_index}" not in self.chamber_placements:
            self.chamber_placements[f"Labyrinthe_{lab_index}"] = {}
            
        self.chamber_placements[f"Labyrinthe_{lab_index}"][f"Chambre_{chamber_index}"] = (x, y)


    def set_odor(self, lab_index, chamber_index, odor, concentration):
        if f"Labyrinthe_{lab_index}" not in self.odor_placements:
            self.odor_placements[f"Labyrinthe_{lab_index}"] = {}

        self.odor_placements[f"Labyrinthe_{lab_index}"][f"Chambre_{chamber_index}"] = (odor, concentration)


    def zone_of_interest(self, lab_index, x_larve, y_larve):
        ''' Cette fonction sert à vérifier si la larve est dans une des chambres du labyrinthe'''
        for chamber_index in self.chamber_placements[f"Labyrinthe_{lab_index}"]:
            (x, y) = self.chamber_placements[f"Labyrinthe_{lab_index}"][f"Chambre_{chamber_index}"]
            if ((x-x_larve)**2 + (y-y_larve)**2 < 70**2):
                return(True)
            else:
                return(False)

'''
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
    gui = MazeGui(MonLabyrinthe)
    gui.run()
    #print(f"First frame for {folder_name} extracted successfully.")

'''
