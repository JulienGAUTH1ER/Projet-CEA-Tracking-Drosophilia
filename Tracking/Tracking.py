'''
Docstring for Tracking.Tracking
Cette classe a pour but de faire tous les calculs nécessaires au tracking de la larve.
'''

import numpy as np
import cv2
import time
import os
import json
from collections import deque
from Tracking.Parameters import NB_FRAMES_BACKGROUND, ALPHA, FPS, MIN_AREA, MAX_DISTANCE, LOST_TOLERANCE, THRESHOLD_VALUE

class Tracking:
    def __init__(self, mask = None):

        self.fps = FPS
        self.mask = mask

        # Parameters
        self.min_area = MIN_AREA
        self.max_distance = MAX_DISTANCE
        self.alpha_contrast = ALPHA
        self.lost_tolerance = LOST_TOLERANCE
        self.background_frames = NB_FRAMES_BACKGROUND
        self.threshold_value = THRESHOLD_VALUE

        # Background
        self.background: np.ndarray | None = None

        # Tracking state
        self.centroid: np.ndarray | None = None
        self.previous_centroid: np.ndarray | None = None
        self.frames_lost = 0
        self.distances: list[float] = []
        self.speeds: list[float] = []

        # Metrics
        self.distance = 0.0
        self.speed = 0.0

        # Data storage
        self.trajectory: list[np.ndarray | None] = []
        self.detections: list[bool] = []
            
    
    def initialise_backgound(self, video):
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
        print("Background initialisé.")


    def update_background(self, gray_frame, alpha=0.01):
        if self.mask is not None:
            gray_frame = cv2.bitwise_and(gray_frame, gray_frame, mask=self.mask)
        cv2.accumulateWeighted(gray_frame, self.background, alpha)
    
    
    def get_background(self):
        return(cv2.convertScaleAbs(self.background))


    def find_centroid(self, contours):
        # Find centroid of largest contour if available
        valid_contours = self.get_valid_contours(contours)
        if not valid_contours:
            print("No valid contours found.")
            return self.centroid, None
        areas = [cv2.contourArea(c) for c in valid_contours]
        larva_contour = valid_contours[np.argmax(areas)]
        M = cv2.moments(larva_contour)
        if M['m00'] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        return [cx, cy], valid_contours

    
    def contrast_larva(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, self.get_background())
        diff = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
        diff = cv2.convertScaleAbs(diff, alpha=self.alpha_contrast)
        _, thresh = cv2.threshold(diff, self.threshold_value, self.threshold_value, cv2.THRESH_BINARY)
        return thresh
    
    
    def tracking_larva(self, diff_frame):
        contours, _ = cv2.findContours(
            diff_frame,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        candidate, candidate_contours = self.find_centroid(contours)

        if candidate is not None:
            # Validation cinématique
            if self.centroid is None:
                valid = True
            else:
                distance = np.linalg.norm(np.array(candidate) - np.array(self.centroid))
                valid = distance <= self.max_distance
            if valid:
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
                self.trajectory.append(None)
                self.detections.append(False)
                self.distances.append(self.distance)
                self.speeds.append(None)
        else:
            self.frames_lost += 1
            self.trajectory.append(None)
            self.detections.append(False)
            self.distances.append(None)
            self.speeds.append(None)            

        # Perte prolongée
        if self.frames_lost > self.lost_tolerance:
            self.centroid = None
        return self.centroid, candidate_contours
    
            
    def _update_motion(self):
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
        return [c for c in contours if cv2.contourArea(c) > self.min_area]


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
