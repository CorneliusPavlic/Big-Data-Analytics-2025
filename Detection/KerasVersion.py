import sys
import os
import glob
import random
import requests
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import time
import json
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO
from collections import deque

# Constants
MODEL_PATH               = "accidents-local.keras"
API_KEY                  = "c58c9ad9-31c0-41a9-8bac-b81c37935976"
CAMERAS_ENDPOINT         = "https://publicapi.ohgo.com/api/v1/cameras"
REGION                   = "ne‑ohio"
CHECK_INTERVAL           = 0.01
CRASH_SIMULATE_FOLDER    = "./Accident"
CRASH_SIMULATE_INTERVAL  = 30

def load_keras_model(path):
    return load_model(path)

def preprocess_image(image):
    """
    Resize to 256×256, scale pixels to [0,1], add batch dim.
    Matches the pipeline used by your offline test.
    """
    resized = cv2.resize(image, (256, 256))
    arr     = resized.astype(np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


def process_image_keras(model, image):
    """
    Run inference on the preprocessed image.
    Assumes model.predict returns a single sigmoid probability P(no_accident).
    Returns (crash_detected: bool, confidence: float(P_accident)).
    """
    inp = preprocess_image(image)          # shape (1, H, W, 3)
    raw = model.predict(inp)               # shape (1,1) or (1,)
    p_no_acc = float(raw.ravel()[0])       # scalar in [0,1]
    p_acc    = 1.0 - p_no_acc              # probability of accident
    crash    = (p_acc >= 0.95)              # threshold at 0.5
    return crash, p_acc



def fetch_cameras_list(api_key, region=REGION):
    resp = requests.get(
        CAMERAS_ENDPOINT,
        params={"api-key": api_key, "region": region, "page-all": "true"},
        timeout=10
    )
    resp.raise_for_status()
    return resp.json().get("results", [])

def fetch_camera_image(url):
    try:
        r = requests.get(url, stream=True, timeout=10)
        r.raise_for_status()
        buf = np.asarray(bytearray(r.content), dtype=np.uint8)
        return cv2.imdecode(buf, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def visualize_detection(lat, lon, image_bgr, out_dir="../GUI/DataStream"):
    # 1. Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)

    # 2. Encode image as base64 JPEG
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    buf = BytesIO()
    pil.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    # 3. Build payload
    payload = {
        "location": {"longitude": lat, "latitude": lon},
        "time":     datetime.now().strftime("%H:%M:%S"),
        "image":    b64
    }

    # 4. Create a unique filename per event
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # e.g. "20250416_153206_123"
    filename = f"event_{ts}.json"
    full_path = os.path.join(out_dir, filename)

    # 5. Write to its own file
    with open(full_path, "w") as f:
        json.dump(payload, f, indent=4)

    print(f"Wrote crash event to {full_path}")

def main():
    model       = load_keras_model(MODEL_PATH)
    cameras     = fetch_cameras_list(API_KEY)
    crash_paths = glob.glob(os.path.join(CRASH_SIMULATE_FOLDER, "*"))
    if not crash_paths:
        raise RuntimeError("No crash images found")
    crash_images = [cv2.imread(p) for p in crash_paths]

    print(f"Loaded model; {len(cameras)} cams, {len(crash_images)} crash imgs.")

    view_counter = 0

    while True:
        loop_start = time.perf_counter()

        for cam in cameras:
            lat, lon = cam["latitude"], cam["longitude"]
            location = cam["location"]

            for view in cam.get("cameraViews", []):
                view_counter += 1
                is_sim = (view_counter % CRASH_SIMULATE_INTERVAL == 0)

                # --- Fetch stage ---
                t0 = time.perf_counter()
                if is_sim:
                    img = random.choice(crash_images)
                else:
                    img = fetch_camera_image(view["smallUrl"])
                t1 = time.perf_counter()
                fetch_time = t1 - t0

                if img is None:
                    print(f"[{view_counter}] {location}: failed to fetch image ({fetch_time:.3f}s)")
                    continue

                # --- Inference stage ---
                t2 = time.perf_counter()
                crash, conf = process_image_keras(model, img)
                t3 = time.perf_counter()
                inf_time = t3 - t2

                # --- Visualization stage (only on crash) ---
                vis_time = 0.0
                if crash:
                    t4 = time.perf_counter()
                    visualize_detection(lat, lon, img)
                    t5 = time.perf_counter()
                    vis_time = t5 - t4

                total_view_time = time.perf_counter() - t0

                # Log all timings
                print(
                    f"[{view_counter:4d}] {location:30.30} | "
                    f"Crash={crash} @ {conf:.2f} | "
                    f"fetch={fetch_time:.3f}s, inf={inf_time:.3f}s, vis={vis_time:.3f}s, total={total_view_time:.3f}s"
                )

        loop_time = time.perf_counter() - loop_start
        print(f"--- Loop complete in {loop_time:.3f}s ---\n")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
