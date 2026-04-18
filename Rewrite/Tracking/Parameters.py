'''
Docstring for Tracking.Parameters
Ce fichier fait état de tous les paramètres qui sont utilisés pour le tracking de la larve
'''

# Nombre de frames qui sont utilisées pour initialiser le background
NB_FRAMES_BACKGROUND = 100

# Cette valeur est utilisée pour faire ressortir les différences entre background et image.
# Elle est à modifier si on change la luminosité de la vidéo.
ALPHA = 2.5

# On considère que tous les pixels au dessus de cette valeur sont d'interêt
THRESHOLD_VALUE = 190

# Donne le poids des frames prises en compte pour mettre à jour le background
ALPHA_BKG = 0.00005

# Donne la taille du kernel dans lequel les contours vont se prolonger pour pouvoir fusionner entre eux
MORPH = 5

# Nombre de frames par secondes de la capture
FPS = 6

# Aire du plus petit et plus grand contour détectable
MIN_AREA = 800
MAX_AREA = 5000

# Distance à laquelle on commence à chercher un centroïde à partir du dernier centroïde détecté
D_SEARCH = 5

# Nombre de frames pendant lesquelles on va continuer à chercher un centroïde dans les alentours du dernier centroïde détecté
LOST_TOLERANCE = 150

# Toutes les "GROWING_SEARCH" frames, on augmente la taille du cercle de recherche de 1 pixel
GROWING_SEARCH = 0.5