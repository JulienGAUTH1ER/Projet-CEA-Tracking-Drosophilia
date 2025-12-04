'''
Some codes that can be useful. select a part and 'ctrl + :' to put or remove hashtags
'''




'''
Renames all csvs correctly for each experiment folder inside a directory (Data for example). 
'''
# from pathlib import Path

# def rename_csvs_in_subdirs(data_dir):
#     data_path = Path(data_dir)
#     if not data_path.is_dir():
#         print(f"Error: {data_dir} is not a valid directory.")
#         return

#     for sub in data_path.iterdir():
#         if not sub.is_dir():
#             continue

#         # find all CSVs in this subdirectory
#         csvs = list(sub.glob('*.csv'))
#         if not csvs:
#             print(f"  – no CSV found in {sub.name}, skipping…")
#             continue

#         # if there are multiple, you could loop or pick the first
#         old_csv = csvs[0]
#         new_name = f"{sub.name}_raw{old_csv.suffix}"
#         new_path = sub / new_name

#         # perform rename
#         old_csv.rename(new_path)
#         print(f"  ✓ Renamed `{old_csv.name}` → `{new_name}` in {sub.name}")

# rename_csvs_in_subdirs("Data")


'''
Renaming experiment subfolders inside a folder
'''

# from pathlib import Path

# def rename_subdirs(data_dir):
#     data_path = Path(data_dir)
#     if not data_path.is_dir():
#         print(f"Error: {data_dir} isn’t a valid directory.")
#         return

#     for sub in data_path.iterdir():
#         if not sub.is_dir():
#             continue

#         old_name = sub.name
#         if "SSempty-ChRim-0" in old_name:
#             new_name = old_name.replace("SSempty-ChRim-0", "SSeChR")
#             new_path = sub.parent / new_name

#             # perform rename
#             sub.rename(new_path)
#             print(f"  ✓ Renamed `{old_name}` → `{new_name}`")
#         else:
#             print(f"  – `{old_name}` doesn’t match, skipping…")
            
# rename_subdirs("Data")


'''
Sometimes the raspberry pi does not stop properly and then the video is not saved properly. You can see this because the experiment's folder will
have an Images subfolder with all the frames (which is deleted when the Video is properly done), and when you copy and paste the Data it will take
a long time because at some point all the frames are copied one by one. In that case, just put the experiment name here, delete the Video and
re do it here.
'''
import os
import cv2
import argparse
import re

def numerical_sort(fname):
    parts = re.split(r'(\d+)', fname)
    return [int(p) if p.isdigit() else p.lower() for p in parts]

def create_video_from_images(image_folder, fps=20):
    # determine parent dir & make video/ there
    parent_dir = os.path.dirname(os.path.abspath(image_folder))
    video_dir  = os.path.join(parent_dir, 'video')
    os.makedirs(video_dir, exist_ok=True)

    # grab and sort all jpgs
    imgs = [f for f in os.listdir(image_folder) if f.lower().endswith('.jpg')]
    if not imgs:
        print(f"No .jpg images found in {image_folder}")
        return
    imgs.sort(key=numerical_sort)

    # get frame size from first image
    first = cv2.imread(os.path.join(image_folder, imgs[0]))
    h, w, _ = first.shape

    # set up writer
    fourcc  = cv2.VideoWriter_fourcc(*'XVID')
    out_path = os.path.join(video_dir, 'Video.avi')
    writer  = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    # write frames
    for img_name in imgs:
        frame = cv2.imread(os.path.join(image_folder, img_name))
        writer.write(frame)

    writer.release()
    cv2.destroyAllWindows()
    print(f"✓ Video saved to {out_path}")
    
create_video_from_images("Data\EtAc_2x10-3_AIR_0_Red_150uWcm2_0_p1_1_SSeChR_2025-07-28_15-59-14_F_HL\Images")