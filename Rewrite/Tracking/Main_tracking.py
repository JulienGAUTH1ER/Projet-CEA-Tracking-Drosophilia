'''
Docstring for Tracking.Tracking
Cette classe sert à ordonner les différents fichiers utilisés pour le tracking de la larve.
'''



import cv2
import numpy as np
from Tracking.Gui import GuiTracking
from Tracking.Tracking import Tracking
from pathlib import Path
from Tracking.Preprocessing import mask_preprocessing
from tqdm import tqdm



def main_tracking(video_path, mask_path):
    
    video_path = Path(video_path)
    mask_path = Path(mask_path)
    
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
    tracker.initialise_background(video)
    gui = GuiTracking()


    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)
    
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=total_frames, desc="Tracking")
    
    while True:
        ret, frame = video.read()
        if not ret:
            break
        pbar.update(1)
        
        # Redimmensionnement du masque
        tracker.mask_resize(frame)
        
        # Soustraction background
        diff_frame = tracker.contrast_larva(frame)

        # Tracking
        centroid, valid_contours = tracker.tracking_larva(diff_frame)
        
        tracker.update_background(frame)
        
        frame_with_mask = gui.draw_mask_outline(frame, tracker.mask)
        
        frame_display = gui.draw_tracking_overlay(
            frame_with_mask, # Modifier ici par diff_frame permet de voir les contours détectés ou par frame pour ne pas voir le masque
            valid_contours,
            tracker.trajectory
        )
        cv2.imshow("Tracking", frame_display)
        
        # Quitter avec touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nTracking annulé")
            cancel_file = video_path.with_name(video_path.stem + "_tracking_cancelled.txt")
            cancel_file.write_text("Tracking annulé par l'utilisateur")
            return
        
    pbar.close()
    video.release()
    cv2.destroyAllWindows()
    tracker.save_tracking_data(output_path)