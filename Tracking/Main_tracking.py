'''
Docstring for Tracking.Tracking
Cette classe sert à ordonner les différents fichiers utilisés pour le tracking de la larve.
'''



import cv2
from Tracking.Gui import GuiTracking
from Tracking.Tracking import Tracking
from utils import interactive_threshold
from pathlib import Path


def main_tracking(video_path):
    
    output_path = Path(video_path).parent.parent / "tracking_data.json"
    if (output_path).exists():
        print("✔ Tracking déjà effectué.")
        return
    
    tracker = Tracking()
    video = cv2.VideoCapture(video_path)

    # Affichage du background
    if not video.isOpened():
        print("Erreur : la vidéo ne s'ouvre pas.")
    else:
        print("Vidéo ouverte avec succès.")
    tracker.initialise_backgound(video)
    gui = GuiTracking()


    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)


    while True:
        ret, frame = video.read()
        if not ret:
            break
        # Soustraction background
        diff_frame = tracker.contrast_larva(frame)

        # Tracking
        centroid, valid_contours = tracker.tracking_larva(diff_frame)

        frame_display = gui.draw_tracking_overlay(
            frame,
            valid_contours,
            tracker.trajectory
        )
        cv2.imshow("Tracking", frame_display)
        # Quitter avec touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        
    video.release()
    cv2.destroyAllWindows()
    tracker.save_tracking_data(output_path)