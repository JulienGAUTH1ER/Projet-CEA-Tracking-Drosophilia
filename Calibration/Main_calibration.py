
import cv2
from pathlib import Path
from Calibration.Parameters import MASK_POINTS, CHAMBERS_MODEL
from Calibration.Gui import GuiCalibration
from Calibration.Calibration import ManualCalibration
from Parameters import NB_LABYRINTHS



def main_calibration(video_path):
    '''
    Docstring for main_calibration
    
    :param video_path: chemin de la vidéo à calibrer
    Cette fonction permet d'exécuter toutes les étapes de la calibration.
    La calibration n'est pas refaite si les fichiers de calibration existent déjà.
    '''
    
    output = Path(video_path).parent
    if (output / "Calibration_done.txt").exists():
        print("✔ Calibration déjà effectuée.")
        return
    
    gui = GuiCalibration(video_path)

    calibration = ManualCalibration(
        chambers_model=CHAMBERS_MODEL,
        mask_points=MASK_POINTS
    )

    labs = []
    lab_id = 1

    while lab_id <= NB_LABYRINTHS:
        print(f"\n=== Calibration du labyrinthe {lab_id}/{NB_LABYRINTHS} ===")

        state, clicked_points = gui.select_labyrinth()

        if not state:
            print("Calibration annulée par l'utilisateur")
            return

        lab = calibration.calibrate_labyrinth(
            lab_id=lab_id,
            clicked_points=clicked_points
        )
        
        video = cv2.VideoCapture(video_path)
        success, frame = video.read()
        video.release()

        if not success:
            raise RuntimeError("Impossible de lire la première frame")

        key = gui.validate_calibration(frame, lab.chambers, lab_id)
        
        if key == ord('r'):
            print("↩ Recalibration du labyrinthe en cours")
            continue

        if key == 27:  # ESC
            print("Calibration interrompue")
            return

        labs.append(lab)
        lab_id += 1
        
    calibration.decoupe_labyrinths(labs, video_path, output)
    
    (output / "calibration_done.txt").write_text("done")
    print(f"\n✔ {len(labs)} labyrinthes calibrés")
    return(labs)
