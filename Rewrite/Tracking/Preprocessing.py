'''
Ce fichier sert à faire du preprocessing sur le masque
'''


import cv2

def mask_preprocessing(video_path, mask_path):
    if "top" in video_path.stem.lower():
        mask_file = mask_path / "Maze_mask_top_painted.png"
    elif "bottom" in video_path.stem.lower():
        mask_file = mask_path / "Maze_mask_bottom_painted.png"
    mask_raw = cv2.imread(str(mask_file), cv2.IMREAD_UNCHANGED)
    if len(mask_raw.shape) == 3 and mask_raw.shape[2] == 4:
        # masque avec alpha
        mask = mask_raw[:,:,3]
    else:
        # masque classique
        mask = cv2.cvtColor(mask_raw, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
    if mask is None:
        raise FileNotFoundError(f"Le masque n'a pas été trouvé à : {mask_file}")
    
    return(mask)