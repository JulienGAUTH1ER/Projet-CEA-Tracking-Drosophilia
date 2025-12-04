import numpy as np
import cv2
import time
from collections import deque

'''
Old larva_class from Timothé Petitjean. It can be used if the other larva_class files where we improved the tracking do not work properly. If 
the tracking failed for an experiment, delete its corresponding folder from experiment, import this larva_class (or the larva_class with the
y-maze shaped ROI) at the start of experiment_class and re do the tracking.
'''

class Larva:
    def __init__(self, Maze, tracking_par):
        # Initialization of variables
        self.background_Last_coord = [0, 0]
        self.distance = 0
        self.bool_focus = 0
        self.speed_time_ratio = time.time()
        self.allcentroid = []
        self.raw_centroid = []
        self.pixel = 30  # half-width for cropping around centroid
        self.Centroid = [217, 383]

        self.reset_attributes()
        self.Initialize_Background(
            tracking_par['Backgroung_init']['size_array'],
            tracking_par['Backgroung_init']['fps'],
            Maze
        )

    def reset_attributes(self):
        # Reset tracking data
        self.trajectory = {"Cart_coord": []}
        self.found = []
        self.raw_centroid = []

    def Initialize_Background(self, size_array, fps, Maze):
        print("Creating first background.")
        Frames_array = deque()
        Frames_array_focus = deque()

        for N in range(1, fps + 1):
            ret, frame = Maze.video_capture.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_focus = self.crop_image_focus(frame)

            # Build frame buffer until we have enough frames for median background
            if len(Frames_array) < size_array:
                Frames_array.append(frame)
                Frames_array_focus.append(frame_focus)
            else:
                Background = np.median(Frames_array, axis=0).astype(np.uint8)
                Background_focus = np.median(Frames_array_focus, axis=0).astype(np.uint8)
                print("First background computed.")
                break

        self.background = Background
        self.background_focus = Background_focus
        self.Back_frames_array = Frames_array
        self.Back_frames_array_focus = Frames_array_focus

    def Update_Background(self, New_frame):
        # Update background buffer with new frame and recompute median
        self.Back_frames_array.popleft()
        self.Back_frames_array.append(New_frame)
        self.background = np.median(self.Back_frames_array, axis=0).astype(np.uint8)

    def Find_Centroid(self, contours):
        # Find centroid of largest contour if available
        if not contours:
            return self.Centroid
        areas = [cv2.contourArea(c) for c in contours]
        larva_contour = contours[np.argmax(areas)]
        M = cv2.moments(larva_contour)
        if M['m00'] != 0:
            self.Centroid = [int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])]
        return self.Centroid

    def crop_image_focus(self, frame):
        # Crop image around current centroid for focused background
        h, w = frame.shape[:2]
        x, y = self.Centroid
        x_min = max(0, x - self.pixel)
        x_max = min(w, x + self.pixel)
        y_min = max(0, y - self.pixel)
        y_max = min(h, y + self.pixel)
        return frame[y_min:y_max, x_min:x_max]

    def is_outlier(self, new_centroid, window=5, threshold=34, min_history=1):
        # Detect if new centroid deviates significantly from recent history
        if len(self.allcentroid) < min_history:
            return False
        past_points = np.array(self.allcentroid[-window:])
        mean_point = np.mean(past_points, axis=0)
        distance = np.linalg.norm(np.array(new_centroid) - mean_point)
        return distance > threshold

    def Tracking_Larva(self, Current_frame, Maze):
        Dist_thr = 34
        # Compute elapsed time since last speed calc
        self.speed_time = time.time() - self.speed_time_ratio
        self.speed_time_ratio = time.time()

        # Subtract background to get foreground (larva)
        Im = cv2.subtract(Current_frame, self.background)

        # Adaptive threshold and morphology to clean binary mask
        Im_thr = cv2.adaptiveThreshold(
            Im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 21, 4
        )
        Im_thr = cv2.morphologyEx(Im_thr, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        self.Im_thr = cv2.morphologyEx(Im_thr, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

        # Find contours in thresholded image
        contours, _ = cv2.findContours(self.Im_thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if contours:
            candidate_centroid = self.Find_Centroid(contours)
            self.raw_centroid.append(candidate_centroid.copy())

            if not self.is_outlier(candidate_centroid, threshold=2.5):
                self.Centroid = candidate_centroid
                self.allcentroid.append(self.Centroid.copy())
                self.found.append(True)
                self.bool_focus = 1
            else:
                self.found.append(False)
        else:
            self.found.append(False)

        # Update trajectory and compute speed
        self.trajectory['Cart_coord'].append(self.Centroid.copy())
        self.distance = np.linalg.norm(np.array(self.Centroid) - np.array(self.background_Last_coord))
        self.speed = self.distance / max(self.speed_time, 1e-5)

        if self.distance > Dist_thr:
            self.Update_Background(Current_frame)
            self.background_Last_coord = self.Centroid.copy()
