'''
Docstring for Gui [Graphic User Interface]

Ce fichier permet de contrôler tout ce qui est lié à l'interface graphique de la calibration.
C'est ici que sont contrôlés quels inputs doivent être réalisés, tous les autres fichiers de "Calibration" ont pour 
but de traiter les données récupérées par le Gui.
'''


import cv2

class GuiCalibration:
    def __init__(self, video_path):
        
        self.video_capture = cv2.VideoCapture(video_path) # Ouvre la vidéo du Maze
        success, self.frame_1 = self.video_capture.read() # Extrait la première frame
        
        self.frame_1 = cv2.cvtColor(self.frame_1, cv2.COLOR_BGR2GRAY) # Conversion en niveaux de gris
        if not success:
            raise ValueError("Impossible de lire la vidéo ou d'extraire la première frame.")
                
        self.nb_Mazes = 0
        self.nb_chambres = 0
        
        self.clicked_points = []


    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.clicked_points) < 4:
            print(f"Clic: ({x},{y})")
            self.clicked_points.append([x, y])
            cv2.circle(self.frame_1, (x, y), 10, (0, 0, 255), -1)
            cv2.imshow("Calibration", self.frame_1)
            

    def select_Maze(self):
        
        self.clicked_points = []
        clone = self.frame_1.copy()
        cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Calibration", self._mouse_callback)

        while True:
            display = clone.copy()
            for p in self.clicked_points:
                cv2.circle(display, tuple(p), 5, (0, 255, 0), -1)

            
            cv2.imshow("Calibration", display)
            key = cv2.waitKey(20)

            if key == 27:  # Echap
                cv2.destroyAllWindows()
                return False

            if len(self.clicked_points) == 4:
                break

        cv2.destroyAllWindows()
        return True, self.clicked_points       


    def draw_chambers(self, frame, chambers):
        """
        Dessine les centres de chambres sur une frame.
        
        :param frame: image sur laquelle dessiner (BGR)
        :param chambers: dict {id: Chamber}
        :param show_text: si True, affiche l'ID à côté du point
        :return: frame annotée
        """
        clone = frame.copy()
        for ch_id, chamber in chambers.items():
            x, y = map(int, chamber.final)  # utilise .final pour auto/manuel
            # Cercle rouge
            cv2.circle(clone, (x, y), 10, (0, 0, 255), -1)

            cv2.putText(
                clone,
                f"{ch_id}",
                (x + 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

        return clone

    def validate_calibration(self, frame, chambers, lab_id):
        annotated = self.draw_chambers(frame, chambers)

        cv2.namedWindow(f"Maze {lab_id}", cv2.WINDOW_NORMAL)
        cv2.imshow(f"Maze {lab_id}", annotated)

        print("Appuyez sur [Entrée] pour valider, [r] pour recommencer, [Esc] pour quitter")
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return(key)
