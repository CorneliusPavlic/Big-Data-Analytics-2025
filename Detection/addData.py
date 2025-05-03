import os
import glob
import requests
import cv2
import random
from datetime import datetime
from KerasVersion import fetch_cameras_list, fetch_camera_image  # import your existing functions

# configuration
API_KEY          = "c58c9ad9-31c0-41a9-8bac-b81c37935976"
REGION           = "ne‑ohio"
BASE_DIR         = "data"
SPLITS           = {
    "train": 600,
    "val":   150,
    "test":  150
}
CLASS_NAME       = "Non Accident"

def ensure_dirs():
    for split in SPLITS:
        d = os.path.join(BASE_DIR, split, CLASS_NAME)
        os.makedirs(d, exist_ok=True)

def download_non_accidents():
    cameras = fetch_cameras_list(API_KEY, REGION)
    counts = {split: 0 for split in SPLITS}
    total_needed = sum(SPLITS.values())
    saved = 0
    view_iter = 0

    for cam in cameras:
        for view in cam.get("cameraViews", []):
            if saved >= total_needed:
                return
            img = fetch_camera_image(view["smallUrl"])
            view_iter += 1
            if img is None:
                continue

            # decide which split to save into
            for split, limit in SPLITS.items():
                if counts[split] < limit:
                    out_dir = os.path.join(BASE_DIR, split, CLASS_NAME)
                    counts[split] += 1
                    saved += 1
                    # filename: NonAccident_YYYYMMDD_HHMMSS_VIEW.jpg
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = f"{CLASS_NAME.replace(' ', '')}_{ts}_{view_iter}.jpg"
                    path  = os.path.join(out_dir, fname)
                    cv2.imwrite(path, img)
                    print(f"[{split:5s}] Saved {path} ({counts[split]}/{limit})")
                    break

if __name__ == "__main__":
    ensure_dirs()
    download_non_accidents()
    print("Done. Distribution:", {k: f"{v}/{SPLITS[k]}" for k,v in counts.items()})
