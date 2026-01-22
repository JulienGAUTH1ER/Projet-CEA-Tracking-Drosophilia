import numpy as np
import cv2
import time
from collections import deque

'''
This larva_class is the one currently used. It applies 2 masks to remove noise from the tracked data points. The trapezoidal mask is fixed, while
the rectangle mask creates a rectangular interest zone that follows the larva. Both are shown on the draw_frame_zone.jpg figure (with the initial
rectangle zone of interest). 
hx and hy, the rectangle mask's half length and width could be finetuned to have the best tradeoff between noise and accurate/continuous tracking.
The zoom part in experiment_class.py uses the same zoom window parameters as the rectangle here, but it is not mandatory.
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

    def is_outlier(self, new_centroid,
               trap_threshold=10,
               box_hx=15, box_hy=45):
        x, y = new_centroid

        # ── 1) TRAPEZOID TEST ───────────────────────────────────
        xabs, yord = 16, 67
        x0, y0     = 108, 343
        # bottom corners (Choice1)
        max_y = self.background.shape[0]
        bl_x, _ = (x0 - 10 + trap_threshold, y0 - 7)
        br_x, _ = (x0 + xabs + 6 - trap_threshold, y0 - 7)
        # top corners (Choice6)
        tl = ((x0 - xabs*5) - trap_threshold, 0)
        tr = ((x0 + xabs*6) + trap_threshold, 0)
        
        trap_poly = np.array([
                    tl,
                    tr,
                    [br_x,   max_y],
                    [bl_x,   max_y],
                ], dtype=np.int32)
        if cv2.pointPolygonTest(trap_poly, (int(x),int(y)), False) < 0:
            return True  # outside trapezoid

        # ── 2) MOVING BOX TEST ─────────────────────────────────
        # track our own last‑good centroid so box can't freeze
        if not hasattr(self, "_last_centroid"):
            self._last_centroid = (114, 385)
        cx, cy = self._last_centroid

        # build box polygon
        x_min, x_max = cx - box_hx, cx + box_hx
        y_min, y_max = cy - box_hy, cy + box_hy
        box_poly = np.array([
            (x_min, y_min),
            (x_max, y_min),
            (x_max, y_max),
            (x_min, y_max)
        ], dtype=np.int32)
        if cv2.pointPolygonTest(box_poly, (int(x),int(y)), False) < 0:
            return True  # outside moving box

        # ── passed both tests! update our last‑good centroid & keep
        self._last_centroid = (x, y)
        return False



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
       

        # # ── APPLY TRAPEZOIDAL MASK ─────────────────────
        # threshold = 10
        # xabs, yord = 16, 67
        # x0, y0 = 108, 343

        # bl_x = x0 - 10 + threshold
        # br_x = x0 + xabs + 6 - threshold

        # tl_x = (x0 - xabs * 5) - threshold
        # tr_x = (x0 + xabs * 6) + threshold
        # top_y = 0
        # max_y = Im_thr.shape[0]

        # poly = np.array([
        #     [tl_x, top_y],
        #     [tr_x, top_y],
        #     [br_x, max_y],
        #     [bl_x, max_y],
        # ], dtype=np.int32)

        # # Create mask and apply
        # mask_trap = np.zeros_like(Im_thr)
        # cv2.fillPoly(mask_trap, [poly], 255)
        # Im_trap = cv2.bitwise_and(Im_thr, mask_trap)

        # # # Save masked threshold for visualization if needed
        # # self.Im_thr = Im_thr
        
        # # ── MOVING BOX ROI AROUND LAST CENTROID ───────────────────────────────
        # # box half‑sizes
        # hx, hy = 25, 40
        
        # # initialize the flag on first ever call
        # if not hasattr(self, "used_first_centroid"):
        #     self.used_first_centroid = False

        # if not self.used_first_centroid:
        #     # first call ever: force the initial ROI center
        #     cx, cy = 114, 385
        #     self.used_first_centroid = True
        # else:
        #     # after that, track normally
        #     cx, cy = self.Centroid   
             
        # # compute box corners
        # x_min = int(cx - hx)
        # x_max = int(cx + hx)
        # y_min = int(cy - hy)
        # y_max = int(cy + hy)

        # # clamp to image bounds
        # h, w = Im_trap.shape
        # x_min = max(0, x_min)
        # x_max = min(w, x_max)
        # y_min = max(0, y_min)
        # y_max = min(h, y_max)

        # # build and apply mask_box
        # mask_box = np.zeros_like(Im_trap)
        # mask_box[y_min:y_max, x_min:x_max] = 255
        # Im_thr = cv2.bitwise_and(Im_trap, mask_box)
        # # ────────────────────────────────────────────────────────────────────────

        # 3) Save masked (or not) threshold for inspection
        self.Im_thr = Im_thr

        # ── FIND CONTOURS ─────────────────────────────
        contours, _ = cv2.findContours(Im_thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        

        if contours:
            candidate_centroid = self.Find_Centroid(contours)
            self.raw_centroid.append(candidate_centroid.copy())

            if not self.is_outlier(candidate_centroid):
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
