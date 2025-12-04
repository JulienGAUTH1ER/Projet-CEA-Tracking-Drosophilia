import numpy as np
import cv2
import time
from collections import deque

'''
Using ref_frame_mask.png, this larva_class applies a custom mask that restricts the tracked data points to be inside the y-maze. It has the
highest noise reduction but the tracking may not be continuous sometimes.
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

        # Load PNG mask (grayscale or with alpha)
        mask_img = cv2.imread('ref_frame_mask.png', cv2.IMREAD_UNCHANGED)
        if mask_img is None:
            raise ValueError("Mask file 'ref_frame_mask.png' not found.")

        # Extract binary mask: if alpha channel exists, use it; else threshold grayscale
        if mask_img.shape[2] == 4:
            alpha = mask_img[:, :, 3]
            _, self.custom_mask = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)
        else:
            gray_mask = cv2.cvtColor(mask_img, cv2.COLOR_BGR2GRAY)
            _, self.custom_mask = cv2.threshold(gray_mask, 1, 255, cv2.THRESH_BINARY)

        # Resize mask to frame size (assuming background frame shape is known)
        if self.custom_mask.shape != self.background.shape:
            self.custom_mask = cv2.resize(
                self.custom_mask,
                (self.background.shape[1], self.background.shape[0]),
                interpolation=cv2.INTER_NEAREST
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

    def is_outlier(self, new_centroid, window=5, threshold=15, min_history=1):
        # Detect if new centroid deviates significantly from recent history
        if len(self.allcentroid) < min_history:
            return False
        past_points = np.array(self.allcentroid[-window:])
        mean_point = np.mean(past_points, axis=0)
        distance = np.linalg.norm(np.array(new_centroid) - mean_point)
        return distance > threshold

    def Tracking_Larva(self, Current_frame, Maze):
        Dist_thr = 34
        self.speed_time = time.time() - self.speed_time_ratio
        self.speed_time_ratio = time.time()

        # Background subtraction
        Im = cv2.subtract(Current_frame, self.background)

        # Thresholding and morphology
        Im_thr = cv2.adaptiveThreshold(
            Im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 21, 4
        )
        Im_thr = cv2.morphologyEx(Im_thr, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        Im_thr = cv2.morphologyEx(Im_thr, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

        # ── APPLY PNG MASK ─────────────────────────────
        Im_thr = cv2.bitwise_and(Im_thr, self.custom_mask)

        # Save masked threshold for visualization if needed
        self.Im_thr = Im_thr

        # ── FIND CONTOURS ─────────────────────────────
        contours, _ = cv2.findContours(Im_thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if contours:
            candidate_centroid = self.Find_Centroid(contours)
            self.raw_centroid.append(candidate_centroid.copy())

            if not self.is_outlier(candidate_centroid, threshold=15):
                self.Centroid = candidate_centroid
                self.allcentroid.append(self.Centroid.copy())
                self.found.append(True)
                self.bool_focus = 1
            else:
                self.found.append(False)
        else:
            self.found.append(False)

        # Trajectory, speed, background update
        self.trajectory['Cart_coord'].append(self.Centroid.copy())
        self.distance = np.linalg.norm(np.array(self.Centroid) - np.array(self.background_Last_coord))
        self.speed = self.distance / max(self.speed_time, 1e-5)

        if self.distance > Dist_thr:
            self.Update_Background(Current_frame)
            self.background_Last_coord = self.Centroid.copy()
