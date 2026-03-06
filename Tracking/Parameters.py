'''
Docstring for Tracking.Parameters
Ce fichier fait état de tous les paramètres qui sont utilisés pour le tracking de la larve
'''

NB_FRAMES_BACKGROUND = 1500

# Cette valeur est utilisée pour faire ressortir les différences entre background et image.
# Elle est à modifier si on change la luminosité de la vidéo.
ALPHA = 3.0
THRESHOLD_VALUE = 190

FPS = 6
MIN_AREA = 350
MAX_DISTANCE = 5
LOST_TOLERANCE = 5