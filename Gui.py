'''
Docstring for Gui [Graphic User Interface]

Ce fichier permet de contrôler tout ce qui est lié à l'interface graphique.
C'est ici que sont contrôlés quels inputs doivent être réalisés, tous les autres fichiers ont pour 
but de traiter les données récupérées par le Gui.

Mis en place des inputs pour le moment :

Maze_class :
    - Nombre de labyrinthes
    - Nombre de chambres
    - Caractéristiques de chaque chambre (odeur / concentration)
    - Placement du centre de chaque chambre

Larva_class :

'''


import cv2

class MazeGui:
    def __init__(self, maze):
        self.maze = maze
        self.lab_index = 1
        self.chamber_index = 1
        
        self.frame = maze.frame_1.copy()
        
        self.nb_labyrinthes = 0
        self.nb_chambres = 0
        
        self.last_click = None


    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Clic: ({x},{y})")
            self.last_click = (x, y)
            cv2.circle(self.frame, (x, y), 70, (0, 0, 255), -1)
            cv2.imshow("Calibration", self.frame)
            

    def run(self):
        self.nb_labyrinthes = int(input("Nombre de labyrinthes : "))
        self.nb_chambres = int(input("Chambres par labyrinthe : "))
        
        
        cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
        cv2.imshow("Calibration", self.frame)
        cv2.setMouseCallback("Calibration", self.mouse_callback)
        
        
        print("Clique sur les centres des chambres")
        print("ESC pour quitter")

        while True:
            cv2.imshow("Calibration", self.frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            
            
            if self.last_click is not None :
                (x, y) = self.last_click
                self.maze.set_chamber(self.lab_index, self.chamber_index, x, y)
                
                odor = input(f"Odeur pour Labyrinthe {self.lab_index}, Chambre {self.chamber_index} : ")
                concentration = input("Concentration : ")
                self.maze.set_odor(self.lab_index, self.chamber_index, odor, concentration)
                
                
                self.chamber_index += 1
                if self.chamber_index > self.nb_chambres:
                    self.chamber_index = 1
                    self.lab_index += 1
                    
                    if self.lab_index > self.nb_labyrinthes:
                        print("Calibration terminée")
                        break
                self.last_click = None

        cv2.destroyAllWindows()





