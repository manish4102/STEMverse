
import numpy as np
import cv2

def detect_marker(image_bgr, marker_path):
    marker = cv2.imread(marker_path, cv2.IMREAD_GRAYSCALE)
    if marker is None or image_bgr is None:
        return {"found": False, "bbox": None, "score": 0.0}
    img_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img_gray, marker, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    h, w = marker.shape
    top_left = max_loc
    bottom_right = (top_left[0]+w, top_left[1]+h)
    return {"found": bool(max_val>0.55), "bbox": (top_left, bottom_right), "score": float(max_val)}
