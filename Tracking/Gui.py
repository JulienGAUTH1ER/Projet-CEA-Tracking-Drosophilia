'''
Docstring for Tracking.Gui
Cette classe est utilisée pour afficher tous les éléments graphiques nécessaires au tracking de la larve, notamment le background et les différentes étapes du tracking.
'''
import cv2
from Tracking.Parameters import NB_FRAMES_BACKGROUND

class GuiTracking:
    def __init__(self):
        return(None)
    
    def display_background(self, background):
        cv2.namedWindow("Background", cv2.WINDOW_NORMAL)
        cv2.imshow("Background", background)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def display_frame(self, frame, title="Frame"):
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.imshow(title, frame)
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        
    def draw_tracking_overlay(self, frame, contours, trajectory, contour_color=(255, 0, 0),contour_thickness=1, trajectory_color=(0, 255, 0), trajectory_thickness=2):
        '''
        Cette fonction dessine les contours et la trajectoire sur la frame d'étude
        Si jamais le centroïde a été perdu puis ensuite retrouvé, on trace une ligne droite entre ces deux points.
        '''
        output = frame.copy()
        cv2.drawContours(output, contours, -1,
                         contour_color, contour_thickness)

        if trajectory and len(trajectory) > 1:
            last_valid = None
            for point in trajectory:
                if point is not None:
                    if last_valid is not None:
                        cv2.line(
                            output,
                            (int(last_valid[0]), int(last_valid[1])),
                            (int(point[0]), int(point[1])),
                            trajectory_color,
                            trajectory_thickness
                        )
                    last_valid = point
        return output