# All imports
import time 
import cv2
import numpy as np
import csv
#import pandas as pd
from larva_class_roi_trap_n_rect import Larva
from maze_class import Maze
from datetime import date
import os
import shutil
import re

'''
Here 'init_results_files' controls the folders and files created for each experiment.
Inside 'display_images' and 'training' there are some hashtagged parts that (if not hashtagged) give a live window that is zoomed on the 
larva (most of the time), as well as a final video of the zoom. It might not work properly sometimes hence why it is hashtagged for now.
On the y-maze, the y coordinates 0 is the top of the image and y_max is the bottom. The x coordinate is normal though (from left to right).
There is an 'odorplacement' function that is currently not used since we have the seeds.
Also, there is a function at the end that could be used to zip the result files.
'''

class Experiment():

    def __init__(self, date_input, genotype, red_light, camera_par, tracking_par, odor, video_path, file_path):
        
        self.bool = 0
        self.time_all = 0
        desired_fps = 20
        self.frame_desired = 1 / desired_fps  # Time per frame in seconds
        self.previous = 0
        self.position = 0
        self.start = 0
        self.odor_time = 0
        self.chamber_time_btw = 0
        self.time_choice = 0
        self.nearby_choices = [[0,0],[0,0]]
        self.odorTT = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        self.direction = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        self.pre_stim= [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        self.post_stim= [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        self.odor = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        self.row = 0 
        self.row_chamber = 0
        self.countodor = 0
        self.chamber_odor_time = 0
        self.choicechamber = 0
        self.calibrate = False
        self.odor_info = odor
        self.Row_name = 'Choice1'
        self.video_path = video_path
        self.file_path = file_path
        seed = int(odor['Seed'])
        self.Maze = Maze(seed, self.video_path)
        self.Larva = Larva(self.Maze, tracking_par) 
        self.Camera_par = camera_par
        self.Tracking_par = tracking_par
        self.seed = seed
        self.genotype = genotype
        self.Red_light = red_light
        self.reset_attributes()
        self.Exp_datetime =  date_input
        self.Exp_ID = str(self.Exp_datetime + '_' + self.odor_info['Passage'] + '_' + self.genotype)
        self.file1 = str(self.odor_info['Odor1'] + '_' + self.odor_info['Concentration1'] + '_' + self.odor_info['Odor2'] + '_' +self.odor_info['Concentration2'] + '_' 
        + self.Red_light['Light'] + '_' + self.Red_light['Intensity'] + '_' + self.Red_light['Duration'])
        self.pairing = str(f"{self.odor_info['Pairing']}_{self.odor_info['Passage']}")
        
        # New attribute to track last validated choice time
        self.last_choice_time = 0

    def reset_attributes(self):
        self.frame_number = 0
        self.frame_numbers_array = []
        self.time_stamps = []
        self.asctimes = []
        self.Nb_choices = 0
        self.Choices_array = [] # [choice_nb, time_stamp, frame_number, time_asc]
        self.current_time = 0
        self.Larva.reset_attributes()

    def update_attributes(self):
        self.frame_numbers_array.append(self.frame_number)
        self.time_stamps.append(self.time_frame)
        self.frame_number += 1

        # Add the current centroid to the trajectory history
        if self.Larva.found[-1]:  # Optional: only if larva was found
            self.Larva.allcentroid.append(self.Larva.Centroid.copy())


    def init_results_files(self,exp_protocol):
        """
        Description function
        """
        self.files = ['Results/' + self.file_path + '_raw' + '.csv',
            'Results/' + self.file_path  +'_draw'+ "/",]  
        if not os.path.exists(self.files[1]):
            os.makedirs(self.files[1])
        with open(self.files[0], 'w', newline='') as csvfile:
            resultwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
            resultwriter.writerow([str(self.Camera_par), str(self.Tracking_par), 
              str(exp_protocol),str(self.Red_light),
              str(self.genotype), str(self.odor_info) ])
            resultwriter.writerow(['Time_stamp', 'Frame_number', 
              'Larva_found?','Larva_centroid_X', 'Larva_centroid_Y',
              'Choice chamber', 'choice_row' ,'SuccessTT','Time_between_chamber','time pre_stimulation','time_post_stimulation','ChoiceLR', 'Chamber_arrival_Time','Odor_choice_time'
              ])

    def update_raw_results(self, current_frame):
        with open(self.files[0], 'a', newline='') as csvfile:
            resultwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
            resultwriter.writerow([str(self.time_stamps[-1]) , str(self.frame_numbers_array[-1]) ,
            str(self.Larva.found[-1]) , str(self.Larva.trajectory['Cart_coord'][-1][0]) , str(self.Larva.trajectory['Cart_coord'][-1][1]) ,
            str(self.choicechamber), str(self.odor), str(self.odorTT), str(self.chamber_time_btw), str(self.pre_stim), str(self.post_stim), str(self.direction), str(self.time_chamber),str(self.odor_time)] )
    

    # def create_choices_results(self):
    #     with open(self.files[2], 'w', newline='') as csvfile:
    #         resultwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #         resultwriter.writerow(['Choice number' , 'Choice_time_stamp','Choice_Frame_number','Choice_Asctime'])
    #         for i in range(0,len(self.Choices_array)):
    #             resultwriter.writerow([self.Choices_array[i][0], self.Choices_array[i][1], self.Choices_array[i][2], self.Choices_array[i][3]])

    def display_images(self, current_frame):
        # Convert grayscale frame to BGR so colors show correctly
        frame_color = cv2.cvtColor(current_frame, cv2.COLOR_GRAY2BGR)

        # Draw larva centroid as red dot
        cv2.circle(frame_color, tuple(self.Larva.Centroid), 2, (0, 0, 255), -1)

        # Prepare a copy of background to draw the trajectory
        background_with_path = cv2.cvtColor(self.Larva.background.copy(), cv2.COLOR_GRAY2BGR)

        # Draw larva path (all past centroids) as red dots on the background copy
        for C in self.Larva.allcentroid:
            cv2.circle(background_with_path, tuple(C), 1, (0, 0, 255), -1)

        # Optionally: draw recent path on current image too
        # for C in self.Larva.allcentroid:
        #     cv2.circle(frame_color, tuple(C), 1, (0, 0, 255), -1)

        # Draw maze features if calibrating
        if self.calibrate:
            for Row in self.Maze.choicepoints:
                for i in self.Maze.choicepoints[Row]:
                    cv2.circle(frame_color, tuple(i), 5, (0, 0, 255), 1)
                for i in self.Maze.odor[Row]:
                    cv2.circle(frame_color, tuple(i), 5, (255, 255, 0), 1)
                for i in self.Maze.chamber[Row]:
                    cv2.circle(frame_color, tuple(i), 2, (255, 255, 0), 1)
        else:
            for i in self.Maze.choicepoints[self.Row_name]:
                cv2.circle(frame_color, tuple(i), 8, (0, 0, 255), 1)
            for i in self.Maze.odor[self.Row_name]:
                cv2.circle(frame_color, tuple(i), 8, (255, 255, 0), 1)
            for i in self.Maze.chamber[self.Row_name]:
                if i:
                    cv2.circle(frame_color, tuple(i), 2, (255, 255, 0), 1)

        # Show the main experiment frame
        cv2.imshow('experiment', frame_color)

        # Show the background image with red larva path
        cv2.imshow('background image', background_with_path)

        # Substrated image (unchanged)
        cv2.imshow('substrated image', self.Larva.Im_thr)
        
        # # ── NEW: live zoom window around the larva ───────────────────────
        # if hasattr(self.Larva, '_last_centroid'):
        #     cx, cy = self.Larva._last_centroid            
        # else:
        #     cx, cy = self.Larva.Centroid  
        # # cx and cy, the centers of the zoomed window, are what may fail sometimes. Either try this or:
        # # if not hasattr(self, "_last_centroid"):
        # #    self._last_centroid = (114, 385)
        # # cx, cy = self._last_centroid
        
        # hx, hy = 15, 45
        # h, w = frame_color.shape[:2]
        # x0, x1 = max(0, cx-hx), min(w, cx+hx)
        # y0, y1 = max(0, cy-hy), min(h, cy+hy)
        # zoom = frame_color[y0:y1, x0:x1]
        # scale = 5                            #scaling the zoom window
        # zoom_scaled = cv2.resize(
        #     zoom,
        #     (zoom.shape[1]*scale, zoom.shape[0]*scale),
        #     interpolation=cv2.INTER_NEAREST
        # )

        # cv2.imshow('zoom', zoom_scaled)
        # # ────────────────────────────────────────────────────────────────
        
        cv2.waitKey(1)

                
    
    def training(self, exp_protocol):
        print("In default phase, press q to end.")
        self.reset_attributes()
        self.init_results_files(exp_protocol)
        self.time_frame = 0
        self.time_chamber = 0                #TIME AT WHICH LARVA ARRIVES TO A CHAMBER

        # Initialize original draw_frame from static image (grayscale)
        self.draw_frame = cv2.imread('reference_frame.jpg')

        # Get total number of frames
        total_frames = int(self.Maze.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        # Set video capture to the last frame
        self.Maze.video_capture.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
        ret, last_frame = self.Maze.video_capture.read()
        if not ret:
            print("Could not grab last frame from video.")
            return

        # Convert last frame to BGR color if it's grayscale
        if len(last_frame.shape) == 2 or last_frame.shape[2] == 1:
            self.parallel_draw_frame = cv2.cvtColor(last_frame, cv2.COLOR_GRAY2BGR)
        else:
            self.parallel_draw_frame = last_frame.copy()

        # Draw static features on this color frame
        for Row in self.Maze.odor:
            for point in self.Maze.odor[Row]:
                if point:
                    cv2.circle(self.parallel_draw_frame, tuple(map(int, point)), 5, (0, 255, 0), -1)  # Green

        for Row in self.Maze.chamber:
            for point in self.Maze.chamber[Row]:
                if point:
                    cv2.circle(self.parallel_draw_frame, tuple(map(int, point)), 4, (255, 0, 0), 1)  # Blue

        for Row in self.Maze.choicepoints:
            for point in self.Maze.choicepoints[Row]:
                if point:
                    cv2.circle(self.parallel_draw_frame, tuple(map(int, point)), 4, (255, 0, 255), 1)  # Magenta

        # Reset frame position to 0 for the main loop
        self.Maze.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

        i = 0
        while i < 0:
            ret, frame = self.Maze.video_capture.read()
            i += 1

        # # ── PREPARE ZOOM‐ONLY VIDEO WRITER ─────────────────────────
        # zoom_hx, zoom_hy = 15, 45     # half‐width/half‐height of your ROI
        # zoom_path = os.path.join(self.files[1], 'zoom.avi')
        # fourcc     = cv2.VideoWriter_fourcc(*'XVID')
        # zoom_writer = cv2.VideoWriter(zoom_path, fourcc, 20.0, (zoom_hx*2, zoom_hy*2))
        # cv2.namedWindow('zoom', cv2.WINDOW_AUTOSIZE)
        # # ─────────────────────────────────────────────────────────────
        
        while True:
            ret, frame = self.Maze.video_capture.read()
            if not ret:                                            #end of the experiment recording
                # Save both draw frames at the end
                cv2.imwrite(self.files[1] + 'draw_frame.jpg', self.draw_frame)
                cv2.imwrite(self.files[1] + 'draw_frame_aligned.jpg', self.parallel_draw_frame)
                
                # ── VISUALIZE ZONE OF INTEREST ──────────────────────────────────────
                # Build the trapezoid using your choicepoints constants:
                threshold = 10
                xabs, yord = 16, 67
                x0, y0     = 108, 343

                # Choice1: bottom edge corners
                bl_x, _ = (x0 - 10 + threshold, y0 - 7)               # bottom‐left from first Choice1 pt
                br_x, _ = (x0 + xabs + 6 - threshold, y0 - 7)         # bottom‐right from last Choice1 pt

                # Choice6: top edge corners, shifted by threshold
                tl_x = (x0 - xabs*5) - threshold          # first Choice6 x minus threshold
                tr_x = (x0 + xabs*6) + threshold          # last Choice6 x minus threshold
                top_y = 0                                 # top at image y=0

                # bottom y is the very bottom of the image
                zone_img = self.parallel_draw_frame.copy()
                max_y = zone_img.shape[0]

                # build polygon in (x,y) order: TL→TR→BR→BL
                poly = np.array([
                    [tl_x,   top_y],
                    [tr_x,   top_y],
                    [br_x,   max_y],
                    [bl_x,   max_y],
                ], dtype=np.int32)

                # draw it
                cv2.polylines(
                    zone_img,
                    [poly],
                    isClosed=True,
                    color=(0,255,0),
                    thickness=2
                )

                # ── DRAW INITIAL, FIXED ROI BOX ────────────────────────────────────
                # center at (114,385), full size 25×67 → half‑sizes hx=12, hy=33
                init_cx, init_cy = 114, 385
                init_hx, init_hy = 15, 45

                cv2.rectangle(
                    zone_img,
                    (init_cx - init_hx, init_cy - init_hy),
                    (init_cx + init_hx, init_cy + init_hy),
                    color=(255, 0, 0),      # blue rectangle
                    thickness=2
                )
                
                # save out a figure so you can inspect it
                cv2.imwrite(self.files[1] + 'draw_frame_zone.jpg', zone_img)
                
                print("No more frames or cannot fetch frames.")
                
                # zoom_writer.release()
                # print(f"Saved zoom video to {zoom_path}")
                
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.time_frame += self.frame_desired
            current_frame = frame

            # Larva processing
            self.larvachamber()
            self.larvaodor()
            self.Larva.Tracking_Larva(current_frame, self.Maze)

            # Show overlays
            self.display_images(current_frame)

            # Draw larva trajectory on both draw frames
            self.followpath()
            
            # # ── CAPTURE AND WRITE ONE ZOOM FRAME ───────────────────
            # frame_bgr = cv2.cvtColor(current_frame, cv2.COLOR_GRAY2BGR)
            # if hasattr(self.Larva, '_last_centroid'):
            #     cx, cy = self.Larva._last_centroid
            # else:
            #     cx, cy = self.Larva.Centroid
            # x0, x1    = max(0, cx - zoom_hx), min(frame_bgr.shape[1], cx + zoom_hx)
            # y0, y1    = max(0, cy - zoom_hy), min(frame_bgr.shape[0], cy + zoom_hy)
            # zoom_roi  = frame_bgr[y0:y1, x0:x1]
            # zoom_writer.write(zoom_roi)
            # # ─────────────────────────────────────────────────────────

            # Bookkeeping
            self.update_attributes()
            self.update_raw_results(current_frame)
            self.current_time = self.time_frame

    def larvaodor(self):
        '''
        Determines when a larva is considered to have chosen an odor.
        '''
        threshold_distance = 8        
        choice_time_threshold = 0.25  # seconds or frames, adjust as needed

        # Check if larva is at odor (unchanged part)
        for i in self.Maze.odor[self.Row_name]:
            distance = np.linalg.norm(np.array(self.Larva.Centroid) - np.array(i))
            if distance < threshold_distance:
                print('LARVA AT ODOR', self.Row_name)
                if self.bool == 0:
                    if self.countodor<6:
                        print(f'ODOR NUMERO : {self.countodor + 1}')
                        self.odorTT[self.countodor] = 1
                        self.start = 0
                        self.last_choice_time = self.time_frame

        if self.calibrate != True:
            for ca, i in enumerate(self.Maze.choicepoints[self.Row_name]):
                distance = np.linalg.norm(np.array(self.Larva.Centroid) - np.array(i))
                if distance < threshold_distance:
                    # If larva detected at this choice point
                    if hasattr(self, 'current_choice_point') and self.current_choice_point == ca:
                        # Same choice point as before, check time elapsed
                        time_at_choice = self.time_frame - self.choice_start_time
                        if time_at_choice >= choice_time_threshold:
                            # Confirm choice
                            self._register_choice(ca)
                            # Reset timer so choice isn't repeatedly registered
                            self.choice_start_time = self.time_frame
                    else:
                        # New choice point detected, reset timer
                        self.current_choice_point = ca
                        self.choice_start_time = self.time_frame
                    break  # Assuming only one choice point can be active at a time
            else:
                # Larva not detected at any choice point, reset current choice
                self.current_choice_point = None
                self.choice_start_time = None

    def _register_choice(self, ca):
        self.row += 1
        self.countodor += 1
        if self.row<=6:
            self.odor[self.row - 1] = ca + self.position
            if self.odorTT[self.row - 1] != 1:
                self.odorTT[self.row - 1] = 0
            self.Maze.choicepoints[self.Row_name] = [[0, 0]]
            self.Maze.odor[self.Row_name] = [[0, 0]]
            self.chamber_odor_time = self.time_frame - self.time_chamber
            self.odor_time = self.time_frame             # TIME AT WHICH THE LARVA MADE THE ODOR CHOICE
            self.pre_stim[self.row - 1] = self.chamber_odor_time
            print('TIME BETWEEN CHAMBER AND ODOR', self.chamber_odor_time)

            if (ca % 2) == 0:
                print('Larva went Left')
                self.direction[self.row - 1] = 0
            else:
                print('Larva went Right')
                self.direction[self.row - 1] = 1

            self.last_choice_time = self.time_frame

            for c, choice in enumerate(self.Maze.choicepoints):
                if c == self.row:
                    self.position = sum([ca + 1 + self.position if ca % 2 == 1 else ca + self.position])
                    self.Maze.choicepoints[choice] = [self.Maze.choicepoints[choice][self.position], self.Maze.choicepoints[choice][self.position + 1]]
                    chamberfocus = [chamber for i, chamber in enumerate(self.Maze.chamber[choice]) if i == self.position / 2]
                    for pairing, focuschoice in enumerate(self.Maze.choicepoints[choice]):
                        odorfocus = [odor for odor in self.Maze.odor[choice] if odor == focuschoice]

                        if odorfocus != []:
                            if pairing % 2 == 1:
                                odorfocus = [[odorfocus[0][0] + 6, odorfocus[0][1] - 7]]
                            else:
                                odorfocus = [[odorfocus[0][0] - 6, odorfocus[0][1] - 7]]
                            self.Maze.choicepoints[choice] = [
                                [self.Maze.choicepoints[choice][0][0] - 6, self.Maze.choicepoints[choice][0][1] - 7],
                                [self.Maze.choicepoints[choice][1][0] + 6, self.Maze.choicepoints[choice][1][1] - 7]
                            ]
                            self.Maze.odor[choice] = odorfocus
                            self.Maze.chamber[choice] = chamberfocus
                            break
                    self.Row_name = choice
                    break

        # Reset bool after 1 time unit (unchanged from original)
        end = self.time_frame
        time_elapsed = end - self.start
        if time_elapsed >= 1:
            self.bool = 0

    def larvachamber(self):
        threshold_distance = 8.0
        self.choicechamber = 0
        for count,Row in enumerate(self.Maze.chamber[self.Row_name]):
                distance = np.linalg.norm(np.array(self.Larva.Centroid) - np.array(Row))
                if distance < threshold_distance:
                    self.row_chamber += 1
                    print('LARVA AT CHOICE CHAMBER', self.row_chamber)
                    self.choicechamber = self.row_chamber
                    self.chamber_time_btw = self.time_frame - self.time_chamber
                    self.odor_chamber = self.time_frame - self.odor_time
                    print(self.odor_chamber)
                    if 0 <= self.row < len(self.post_stim):
                        self.post_stim[self.row] = self.odor_chamber
                    self.time_chamber = self.time_frame
                    self.Maze.chamber[self.Row_name] = []
                    print(self.chamber_time_btw)     

    def followpath(self):
        if self.Larva.found and self.Larva.found[-1]:
            # ========== ORIGINAL VERSION ==========
            # Draw larva position in red on original reference frame
            cv2.circle(self.draw_frame, tuple(map(int, self.Larva.Centroid)), 2, (0, 0, 255), 1)

            # Re-draw odor points in green (in case they move)
            for Row in self.Maze.odor:
                for i in self.Maze.odor[Row]:
                    if i:
                        cv2.circle(self.draw_frame, tuple(map(int, i)), 5, (0, 255, 0), -1)

            # ========== NEW PARALLEL VERSION ==========
            # Draw larva trajectory on actual tracking background
            cv2.circle(self.parallel_draw_frame, tuple(map(int, self.Larva.Centroid)), 1, (0, 0, 255), -1)


    def odorplacement(self):
        for Row in self.Maze.choicepoints:
            for i in self.Maze.choicepoints[Row]:
                cv2.circle(self.Maze.frame_0, tuple(i), 2,(255,255,255),1)
            for i in self.Maze.odor[Row]:
                cv2.circle(self.Maze.frame_0,tuple(i), 4,(255,255,255),-1)
        print('Place the odors in the maze as follow :')
        print('Once done, press Esc')
        while(True):
            cv2.imshow('experiment', self.Maze.frame_0)
            if cv2.waitKey(1) & 0xff == 27:
                break    

    def zipfile(self):
        archived = shutil.make_archive(f'Results/{self.genotype}/{self.Exp_ID}','zip', f'{self.Exp_ID}')
