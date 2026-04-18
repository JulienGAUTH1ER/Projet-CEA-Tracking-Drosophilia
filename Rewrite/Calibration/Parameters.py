'''
Docstring for Calibration.Geometry
Ce code sert à définir tous les points d'interêt du Maze que nous considérons.
Ces données sont obtenues en regardant la position (px, py) sur GIMP.
'''

import numpy as np

# Points de référence sur le MASQUE (dans l'ordre)
MASK_POINTS = np.array([
    [0, 0],     # coin haut-gauche
    [888, 0],    # coin haut-droit
    [888, 1859],   # coin bas-droit
    [0, 1859],    # coin bas-gauche
], dtype=np.float32)

width_mask = 888
height_mask = 1859

# Centres des chambres dans le référentiel du masque, ils sont utilisés pour que l'utilisateur puisse mieux
# voir si la calibration est bonne
CHAMBERS_MODEL = {
    "Chambre_1_1":  (466, 352), # En haut
    "Chambre_1_2": (273, 684), # Bas gauche
    "Chambre_1_3":   (658, 696), #Bas droite
    
    "Chambre_2_1":  (466, 1248), # En haut
    "Chambre_2_2": (273, 1569), # Bas gauche
    "Chambre_2_3":   (658, 1573) #Bas droite
}

# Utilisé pour nommer les différents Maze et chambres, sert à nommer aussi les dossiers
LAB_NAMES = ["A", "B", "C", "D", "E", "F", "G", "H"]
ROOM_NAMES = ["1", "2", "3"]

# Valeur en pixels du rayon de la chambre dans le référentiel du masque
r_mask = 340

# Couleurs utilisées pour afficher les différentes chambres et la zone de décision
CHAMBERS_COLORS = {
    "Chambre_3": 'Red',      # Rouge
    "Chambre_2": 'Green',      # Vert
    "Chambre_1": 'Blue',      # Bleu
    "Decision_zone": 'White'     # Blanc
}