import cv2
import numpy as np
import os
from Calibration.Gui import GuiCalibration

'''
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
    MonLabyrinthe = GuiCalibration(video_path)
img = MonLabyrinthe.frame_1
adjusted = img.copy()
'''




def interactive_threshold(diff_frame):
    """
    Permet de régler le contraste, la luminosité et le seuil
    sur l'image de différence (diff_frame) pour trouver les meilleurs paramètres.
    """
    
    # Fonction de callback pour les trackbars
    def update(_=0):
        alpha = cv2.getTrackbarPos("Contrast", "Réglages") / 50.0  # 0 à 3.0
        beta = cv2.getTrackbarPos("Brightness", "Réglages") - 100  # -100 à +100
        thresh_val = cv2.getTrackbarPos("Threshold", "Réglages")   # 0 à 255

        # Ajustement contraste/luminosité
        adjusted = cv2.convertScaleAbs(diff_frame, alpha=alpha, beta=beta)

        # Seuillage
        _, thresh_img = cv2.threshold(adjusted, thresh_val, 255, cv2.THRESH_BINARY)

        cv2.imshow("Réglages", thresh_img)

    # Création de la fenêtre et des trackbars
    cv2.namedWindow("Réglages", cv2.WINDOW_NORMAL)
    cv2.createTrackbar("Contrast", "Réglages", 50, 150, update)    # alpha initial 1.0
    cv2.createTrackbar("Brightness", "Réglages", 100, 200, update) # beta initial 0
    cv2.createTrackbar("Threshold", "Réglages", 127, 255, update)  # seuil initial 127

    # Affichage initial
    update()

    print("Réglez les paramètres avec les trackbars, puis appuyez sur 'q' pour quitter.")
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Récupérer les paramètres finaux
    final_alpha = cv2.getTrackbarPos("Contrast", "Réglages") / 50.0
    final_beta = cv2.getTrackbarPos("Brightness", "Réglages") - 100
    final_thresh = cv2.getTrackbarPos("Threshold", "Réglages")

    cv2.destroyAllWindows()
    return final_alpha, final_beta, final_thresh

# Exemple d'utilisation
# alpha, beta, thresh = interactive_threshold(diff_frame)
# print("Paramètres choisis :", alpha, beta, thresh)
