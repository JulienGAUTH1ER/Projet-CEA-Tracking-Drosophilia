'''
Docstring for Tracking.Tracking
Cette classe a pour but de faire tous les calculs nécessaires au tracking de la larve.
'''

import numpy as np
import cv2
import json
from Tracking.Parameters import NB_FRAMES_BACKGROUND, ALPHA_BKG, FPS, MIN_AREA, MAX_AREA, MAX_DISTANCE, LOST_TOLERANCE, THRESHOLD_VALUE, ALPHA, MORPH, GROWING_SEARCH

class Tracking:
    def __init__(self, mask = None):

        self.fps = FPS
        self.mask = mask

        # Parameters
        self.min_area = MIN_AREA
        self.max_area = MAX_AREA
        self.max_distance = MAX_DISTANCE
        self.alpha_contrast = ALPHA
        self.lost_tolerance = LOST_TOLERANCE
        self.background_frames = NB_FRAMES_BACKGROUND
        self.threshold_value = THRESHOLD_VALUE
        self.alpha = ALPHA_BKG
        self.morph = MORPH
        self.search = GROWING_SEARCH

        # Background
        self.background: np.ndarray | None = None

        # Tracking state
        self.centroid: np.ndarray | None = None
        self.previous_centroid: np.ndarray | None = None
        self.initiate_position = True
        self.frames_lost = 0
        self.distances: list[float] = []
        self.speeds: list[float] = []

        # Metrics
        self.distance = 0.0
        self.speed = 0.0

        # Data storage
        self.trajectory: list[np.ndarray | None] = []
        self.detections: list[bool] = []
        
        
    def initialise_background(self, video):
        print("Initialisation du background en cours...")
        frames = []
        for i in range(self.background_frames):
            print(f"Reading frame {i}/{self.background_frames}" if i % 50 == 0 else "", end="\r")
            ret, frame = video.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(gray)
        median = np.median(np.stack(frames), axis=0)
        self.background = median.astype("float32")
        print('Background initialisé')


    def update_background(self, frame):
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_to_update = gray_frame.copy()
        cv2.accumulateWeighted(frame_to_update, self.background, self.alpha)
    

    def get_background(self):
        return(cv2.convertScaleAbs(self.background))


    def tracking_initialisation(self, candidate_contours):
        '''
        Cette fonction sert à détecter le premier plus grand contour
        '''
        if not candidate_contours:
            return None
        
        largest = max(candidate_contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        M = cv2.moments(largest)
        if M["m00"] == 0:
            return None
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
            
        if self.initiate_position and self.max_area > area > self.min_area and self.mask_test([cx, cy]):
            print('Initialisation du tracking')
            self.initiate_position = False
            return np.array([cx, cy])
        elif self.centroid is None:
            return(None)
        else :
            print('Tracking échoué, réinitialisation du tracking')
            last_detected_position = np.array(self.centroid)
            candidate = np.array([cx, cy])
            distance = np.linalg.norm(candidate - last_detected_position)**2
            search_radius = int(self.max_distance * (1 + (1/self.search)*self.frames_lost))
            if distance <= search_radius**2 and self.mask_test([cx, cy]):
                return np.array([cx, cy])
            else:
                return self.centroid
        

    def find_centroid(self, contours):

        candidate_contours = self.get_valid_contours(contours)
        if not candidate_contours:
            return None, []
        
        centroids = []

        for c in candidate_contours:
            M = cv2.moments(c)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            if self.mask_test([cx, cy]):
                centroids.append(np.array([cx, cy]))

        if self.centroid is None or not centroids:
            return(self.tracking_initialisation(candidate_contours), candidate_contours)

        # Calcul distance au dernier point
        prev = np.array(self.centroid)

        distances = [np.sum((c - prev)**2) for c in centroids]

        # index du plus proche
        min_index = np.argmin(distances)

        # vérifier la distance max autorisée
        search_radius = int(self.max_distance * (1 + (1/self.search)* self.frames_lost))
        if distances[min_index] <= search_radius**2:
            return centroids[min_index], candidate_contours
        else:
            return None, candidate_contours
        
    def contrast_larva(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, self.get_background())
        diff = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
        diff = cv2.convertScaleAbs(diff, alpha=self.alpha_contrast)
        _, thresh = cv2.threshold(diff, self.threshold_value, self.threshold_value, cv2.THRESH_BINARY)
        return thresh
    
    
    def tracking_larva(self, diff_frame):
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.morph,self.morph))
        diff_frame = cv2.dilate(diff_frame, kernel, iterations=1)
        diff_frame = cv2.morphologyEx(diff_frame, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            diff_frame,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        candidate, candidate_contours = self.find_centroid(contours)

        if candidate is not None:
            self.previous_centroid = self.centroid
            self.centroid = candidate
            self.frames_lost = 0
            
            # Calcul métriques
            self._update_motion()
            self.trajectory.append(self.centroid.copy())
            self.detections.append(True)
            self.distances.append(self.distance)
            self.speeds.append(self.speed)

        else:
            self.frames_lost += 1
            self.detections.append(False)
            self.distances.append(None)
            self.speeds.append(None)
            if self.centroid is not None:
                # On garde l'ancienne position
                self.trajectory.append(self.centroid.copy())

        return self.centroid, candidate_contours
    
            
    def mask_resize(self, frame):
        '''
        Cette fonction sert à redimensionner le masque au cas où il n'est pas au même format que la vidéo
        '''
        mask = self.mask
        
        height, width = frame.shape[:2]
        if mask.shape != (height, width):
            self.mask = cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST)
        
        
    def mask_test(self, candidate):
        '''
        Test pour savoir si le centroïde est bien dans l'aire du masque
        '''
        x, y = int(candidate[0]), int(candidate[1])
        if not (0 <= y < self.mask.shape[0] and 0 <= x < self.mask.shape[1]):
            return False
        # On vérifie si les coordonnées du candidat sont dans la zone blanche du masque
        return self.mask[y, x] > 0
            
            
    def _update_motion(self):
        '''
        Calcul de la vitesse et de la distance parcourue entre deux détections de centroïdes
        '''
        if self.previous_centroid is None:
            self.distance = 0.0
            self.speed = 0.0
            return
        self.distance = np.linalg.norm(
            np.array(self.centroid) - np.array(self.previous_centroid)
        )
        # vitesse en pixels/seconde
        self.speed = self.distance * self.fps


    def get_valid_contours(self, contours):
        '''
        Permet d'obtenir les contours respectant les critères de taille
        '''
        return [
        c for c in contours
        if self.min_area < cv2.contourArea(c) < self.max_area]

    def save_tracking_data(self, output_path):
        """
        Sauvegarde les données de tracking au format JSON.
        """

        formatted_trajectory = [
            {"x": int(p[0]), "y": int(p[1])} if p is not None else None
            for p in self.trajectory
        ]

        data = {
            "fps": self.fps,
            "parameters_python": {
                "min_area": self.min_area,
                "max_distance": self.max_distance,
                "lost_tolerance": self.lost_tolerance,
                "threshold_value": self.threshold_value,
                "alpha_contrast": self.alpha_contrast,
            },
            "tracking": [
                {
                    "frame": i,
                    "time_sec": i / self.fps,
                    "position": formatted_trajectory[i],
                    "detected": self.detections[i],
                    "distance_px": self.distances[i],
                    "speed_px_per_sec": self.speeds[i],
                }
                for i in range(len(self.trajectory))
            ]
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Tracking sauvegardé dans : {output_path}")
