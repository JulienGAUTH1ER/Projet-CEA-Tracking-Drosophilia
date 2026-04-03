'''
Docstring for Réécriture.Main
Ce fichier est le fichier qu'il faut faire tourner pour analyser les vidéos.
Les autres fichiers servent à définir les différentes classes pour réaliser le tracking.

Les vidéos doivent être dans un dossier 'Data' à côté de ce script
'Data' -> Dossier de chaque expérience (libre de choisir le nom) -> 'Video' -> '.mp4' (choix libre)
'''

import os
from pathlib import Path
from Calibration.Main_calibration import calibrate_video, decoupe_video
from Tracking.Main_tracking import main_tracking

# Exemple d'utilisation du programme
base_dir = os.path.dirname(os.path.abspath(__file__))
print("Base directory:", base_dir)

data_dir = Path(base_dir) / "Data"
mask_dir = Path(base_dir) / "Calibration" / "Maze_pictures"

# On parcourt toutes les vidéos dans le dossier Data
videos = []
for experiment_folder in data_dir.iterdir():
    video_dir = experiment_folder / "Video"
    for video_path in video_dir.glob("*.mp4"):
        videos.append(video_path)
        
all_labs = {}
for video in videos:
    print("Calibration :", video)
    labs = calibrate_video(video)
    if labs:
        all_labs[video] = labs

for video, labs in all_labs.items():
    print("Découpe :", video)
    decoupe_video(labs, video)        
    
for experiment_folder in data_dir.iterdir():
    video_dir = experiment_folder / "Video"
    Mazes_path = video_dir / "Mazes"
    for video_lab in Mazes_path.rglob("*.mp4"):
        print("Tracking :", video_lab)
        main_tracking(video_lab, mask_dir)


'''
video_path = "C:/Users/julie/Downloads/Projet CEA/Rewrite/Data/Experiment_4/Video/Maze_1_top.mp4"
print(video_path)
main_tracking(video_path)
'''