'''
Suppression de toutes les vidéos du projet pour des gains de place.
Toutes les vidéos sont placées dans un dossier "Trash_videos".
'''


import shutil
from pathlib import Path

project_root = Path("..").resolve()
data_dir = project_root / "Data"
trash_dir = project_root / "Trash_videos"

trash_dir.mkdir(exist_ok=True)

video_files = list(data_dir.rglob("*.mp4"))

for video in video_files:
    destination = trash_dir / video.name
    print(f"Déplacement vers Trash : {video}")
    shutil.move(str(video), str(destination))

print("Toutes les vidéos ont été déplacées dans Trash_videos.")