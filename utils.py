'''
Docstring for Réécriture.Larva_class

Ce fichier a pour objectif de détecter la position de la larve dans une zone prédéfinie.

'''

import cv2
import numpy as np
from Maze_class import Maze
import os
from Maze_class import Maze

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
    MonLabyrinthe = Maze(video_path)
img = MonLabyrinthe.frame_1
adjusted = img.copy()

def update(val):
    alpha = cv2.getTrackbarPos("Contrast", "Réglages") / 50.0  # 0 à 3.0
    beta = cv2.getTrackbarPos("Brightness", "Réglages") - 100  # -100 à +100
    thresh = cv2.getTrackbarPos("Threshold", "Réglages")  # 0 à 255
    
    # Ajustement contraste/luminosité
    adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    
    # Seuillage
    _, thresh_img = cv2.threshold(adjusted, thresh, 255, cv2.THRESH_BINARY)
    
    cv2.imshow("Réglages", thresh_img)

# Créer fenêtre et trackbars
cv2.namedWindow("Réglages", cv2.WINDOW_NORMAL)
cv2.createTrackbar("Contrast", "Réglages", 50, 150, update)
cv2.createTrackbar("Brightness", "Réglages", 100, 200, update)
cv2.createTrackbar("Threshold", "Réglages", 127, 255, update)

update(0)  # afficher image initiale

cv2.waitKey(0)
cv2.destroyAllWindows()
