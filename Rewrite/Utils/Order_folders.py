'''
Ce script permet d'organiser les vidéos dans le dossier "Data" selon un format spécifique.
Les vidéos doivent être nommées de la manière suivante : "19032026_Exp3_60min.mp4".
Le script va créer des dossiers pour chaque expérience (par exemple, "Experiment_3") et déplacer
les vidéos correspondantes dans un sous-dossier "Video" à l'intérieur de chaque dossier d'expérience.
'''



import shutil
import os
from pathlib import Path


def organize_videos(data_dir):
    """
    Organise les vidéos selon le format :
    19032026_Exp3_60min.mp4 → Experiment_3_19032026/Video/
    """

    for video_path in data_dir.glob("*.mp4"):
        filename = video_path.stem  # sans extension

        parts = filename.split("_")
        if len(parts) < 2:
            print(f"Nom invalide : {filename}")
            continue

        date = parts[0]  # 19032026
        exp_part = parts[1]  # Exp3

        # Extraire le numéro d'expérience
        if exp_part.startswith("Exp"):
            exp_number = exp_part.replace("Exp", "")
        else:
            print(f"Format inattendu : {filename}")
            continue

        experiment_name = f"_Exp_{exp_number}"

        experiment_dir = data_dir / experiment_name
        video_dir = experiment_dir / "Video"
        video_dir.mkdir(parents=True, exist_ok=True)

        destination = video_dir / video_path.name

        print(f"Déplacement : {video_path.name} → {experiment_name}/Video/")
        shutil.move(str(video_path), str(destination))
        
        
project_root = Path("..").resolve()
data_dir = Path(project_root) / "Data"
organize_videos(data_dir)