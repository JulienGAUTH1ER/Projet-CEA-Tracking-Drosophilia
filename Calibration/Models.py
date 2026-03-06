'''
Docstring for Calibration.Models
Ce fichier sert à définir les objets que l'on manipule, ici des labyrinthes et des chambres
'''


class Labyrinth:
    '''
    Docstring for Labyrinth
    Quand cette classe est appelée, cela permet de donner une id et un contour pour chaque labyrinthe, ainsi que les id de ses chambres
    Attention, avec le masque choisi, un labyrinthe dans le code correspond à deux labyrinthes en réalité
    '''
    def __init__(self, lab_id):
        self.id = lab_id
        self.homography = None
        self.chambers = {}
        self.clicked_points = [] # Correspond aux points cliqués par l'utilisateur pour calibrer le labyrinthe


class Chamber:
    '''
    Docstring for Chamber
    Quand cette classe est appelée, cela permet d'instancier la calibration automatique de la chambre
    auto_xy correspond au résultat renvoyé par le placement automatique de la chambre, ce sont des coordonnées.
    '''
    def __init__(self, auto_xy):
        self.auto = auto_xy
        self.manual = None
        
        self.odor = None
        self.concentration = None

    @property
    def final(self):
        return self.manual if self.manual else self.auto
    


