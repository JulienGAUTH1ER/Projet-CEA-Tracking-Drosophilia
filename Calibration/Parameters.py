'''
Docstring for Calibration.Geometry
Ce code sert à définir tous les points d'interêt du labyrinthe que nous considérons.
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

# Centres des chambres dans le référentiel du masque
CHAMBERS_MODEL = {
    "Chambre_1_1":  (466, 352), # En haut
    "Chambre_1_2": (273, 684), # Bas gauche
    "Chambre_1_3":   (658, 696), #Bas droite
    
    "Chambre_2_1":  (466, 1248), # En haut
    "Chambre_2_2": (273, 1569), # Bas gauche
    "Chambre_2_3":   (658, 1573) #Bas droite
}


# Valeur en pixels du rayon de la chambre dans le référentiel du masque
r_mask = 340