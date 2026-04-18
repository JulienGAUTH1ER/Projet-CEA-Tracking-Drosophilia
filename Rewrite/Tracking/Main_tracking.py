'''
Docstring for Tracking.Tracking
Cette classe sert à ordonner les différents fichiers utilisés pour le tracking de la larve.
'''



import shutil
import cv2
import numpy as np
from Tracking.Gui import GuiTracking
from Tracking.Tracking import Tracking
from pathlib import Path
from Tracking.Preprocessing import mask_preprocessing
from tqdm import tqdm
from Utils.Move_processed_videos import Move_processed_videos



def main_tracking(video_path, mask_path, video_processed_path=None):
    
    video_path = Path(video_path)
    mask_path = Path(mask_path)
    video_processed_path = video_path.with_name(video_path.stem + "_processed.mp4") if video_processed_path is None else Path(video_processed_path)
    
    mask = mask_preprocessing(video_path, mask_path)

    video_path_json = Path(video_path)
    output_path = video_path_json.with_name(video_path_json.stem + "_tracking.json")
    cancel_path = video_path.with_name(video_path.stem + "_tracking_cancelled.txt")
    if (output_path).exists() or (cancel_path).exists():
        print("✔ Tracking déjà effectué.")
        return
    
    tracker = Tracking(mask)
    video = cv2.VideoCapture(video_path)

    # Affichage du background
    if not video.isOpened():
        print("Erreur : la vidéo ne s'ouvre pas.")
    else:
        print("Vidéo ouverte avec succès.")
    background = tracker.initialise_background(video)
    gui = GuiTracking()
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(str(video_processed_path), fourcc, tracker.fps, (width, height))
    
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=total_frames, desc="Tracking")
    
    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        pbar.update(1)
        timestamp = video.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        tracker.timestamps.append(timestamp)
        
        # Redimmensionnement du masque
        tracker.mask_resize(frame)
        
        # Soustraction background
        diff_frame = tracker.contrast_larva(frame)

        # Tracking
        centroid, valid_contours = tracker.tracking_larva(diff_frame)
        
        tracker.update_background(frame)
        
        
        diff_bgr = cv2.cvtColor(diff_frame, cv2.COLOR_GRAY2BGR)
        writer.write(diff_bgr)
        
        # Quitter avec touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nTracking annulé")
            cancel_file = video_path.with_name(video_path.stem + "_tracking_cancelled.txt")
            cancel_file.write_text("Tracking annulé par l'utilisateur")
            writer.release()
            return
        
    pbar.close()
    video.release()
    cv2.destroyAllWindows()
    writer.release()
    
    project_root = Path(".").resolve()
    destination = project_root / "Processed_Videos"
    target_path = destination / video_processed_path.name
    destination.mkdir(parents=True, exist_ok=True)
    shutil.move(str(video_processed_path), str(target_path))
    print(f"Vidéo sauvegardée : {destination}")
    
    tracker.save_tracking_data(output_path)