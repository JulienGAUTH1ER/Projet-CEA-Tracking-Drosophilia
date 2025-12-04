import cv2
import pandas as pd
import os
import numpy as np

'''
Creates a sped-up movie of a given experiment video.
'''

root_folder = "Data/EtAc_10-2_AIR_0_Red_150uWcm2_0_p1_1_SSeChR_2025-07-04_16-52-21_F_D/"
root_folder_video = os.path.join(root_folder, "Video")

# Read timestamps from CSV, ignoring the first row
csv_file = os.path.join(root_folder, 'EtAc_10-2_AIR_0_Red_150uWcm2_0_p1_1_SSeChR_2025-07-04_16-52-21_F_D_raw.csv')
df = pd.read_csv(csv_file, skiprows=1)  # skip the first row
timestamps = np.round(df['Time_stamp'].values)  # get the time-stamp column as numpy array

# Open the AVI video
video_path = os.path.join(root_folder_video, 'Video.avi')
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video file: {video_path}")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
print(f'Original FPS: {fps}')

speed_factor = 3
new_fps = fps * speed_factor

# Video writer setup
fourcc = cv2.VideoWriter_fourcc(*'XVID')
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

output_path = os.path.join(root_folder_video, 'Video_speedup.avi')
out = cv2.VideoWriter(output_path, fourcc, new_fps, (frame_width, frame_height))

frame_idx = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Put white timestamp text on the frame
    if frame_idx < len(timestamps):
        text = f"{timestamps[frame_idx]}"
    else:
        text = ""

    # Parameters for the text overlay
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 255, 255)  # white color
    thickness = 2
    position = (10, frame_height - 20)  # bottom-left corner

    # Overlay the timestamp text
    cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)

    # Write the frame to the output video
    out.write(frame)

    # Show the frame for visualization (optional)
    cv2.imshow('Video (Speed-up with Timestamps)', frame)

    # Wait key according to new fps speedup (for display only)
    wait_time = int(1000 / new_fps)
    if cv2.waitKey(wait_time) & 0xFF == ord('q'):
        break

    frame_idx += 1

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Saved sped-up video with timestamps to {output_path}")
