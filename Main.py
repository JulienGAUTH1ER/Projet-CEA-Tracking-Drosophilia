'''
Docstring for Réécriture.Main
Ce fichier est le fichier qu'il faut faire tourner pour analyser les vidéos.
Les autres fichiers servent à définir les différentes classes pour réaliser le tracking.
'''

import os
from Calibration.Main_calibration import main_calibration
from Tracking.Main_tracking import main_tracking
from pathlib import Path

'''
# Exemple d'utilisation du programme
base_dir = os.path.dirname(os.path.abspath(__file__))
print("Base directory:", base_dir)
# Les vidéos doivent être dans un dossier 'Data' à côté de ce script
# 'Data' -> Dossier de chaque expérience (libre de choisir le nom) -> 'Video' -> 'Video.avi'
data_dir = os.path.join(base_dir, 'Data')

# On parcourt toutes les vidéos dans le dossier Data
for folder_name in os.listdir(data_dir):
    folder_path = os.path.join(data_dir, folder_name)
    video_dir = os.path.join(folder_path, 'Video')
    video_path = os.path.join(folder_path, 'Video', 'Video.mp4')
    print(video_path)
    main_calibration(video_path)
    main_tracking(video_path)
'''

video_path = "C:/Users/julie/Downloads/Projet CEA/Rewrite/Data/Experiment_4/Video/Labyrinthe_1_top.mp4"
print(video_path)
main_tracking(video_path)