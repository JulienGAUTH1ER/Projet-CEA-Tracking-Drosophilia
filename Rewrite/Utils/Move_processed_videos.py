'''
Ce script permet de déplacer les vidéos traitées (celles qui ont "_processed" dans leur nom) vers un dossier "Processed_Videos" à la racine du projet, en conservant la structure des dossiers d'origine.
Il suffit de faire tourner ce script après avoir traité les vidéos pour organiser les fichiers de manière plus propre.
Les vidéos 'processed' sont les vidéos de larves sur lesquelles nous avons fait du traitement d'image.
'''




from pathlib import Path
import shutil

def Move_processed_videos(src_root, dst_root):
    src_root = Path(src_root).resolve()
    dst_root = Path(dst_root).resolve()

    for video_path in src_root.rglob("*_processed.mp4"):

        if not video_path.is_file():
            continue

        # chemin relatif par rapport à la racine source
        relative_path = video_path.relative_to(src_root)

        # destination finale
        target_path = dst_root / relative_path

        # créer les dossiers si besoin
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # déplacer (ou copier si tu préfères)
        shutil.move(str(video_path), str(target_path))

        print(f"Déplacé : {video_path} -> {target_path}")


if __name__ == "__main__":

    project_root = Path(".").resolve()
    data_dir = project_root / "Data"
    destination = project_root / "Processed_Videos"

    Move_processed_videos(data_dir, destination)