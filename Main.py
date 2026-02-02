'''
Docstring for Réécriture.Main
Ce fichier est le fichier qu'il faut faire tourner pour analyser les vidéos.
Les autres fichiers servent à définir les différentes classes pour réaliser le tracking.
'''

import os
from Maze_class import Maze
from Gui import MazeGui

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
    print(video_path)
    MonLabyrinthe = Maze(video_path)
    gui = MazeGui(MonLabyrinthe)
    gui.run()
    
    print("Résultat calibration :")
    print(MonLabyrinthe.chamber_placements)
    print(MonLabyrinthe.odor_placements)
    #print(f"First frame for {folder_name} extracted successfully.")