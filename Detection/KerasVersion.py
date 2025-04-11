import requests
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import time
import json
from datetime import datetime
from PIL import Image

# Constants
CAMERA_URL = "https://itscameras.dot.state.oh.us/images/CLE/CLE032.jpg"
CAMERA_LOCATION = "Cleveland, OH Camera CLE032"  # Hard-coded camera location
MODEL_PATH = "accidents.keras"    # Path to your saved Keras model

# Check if GPU is available (TensorFlow will automatically use GPU if available)
if tf.config.list_physical_devices('GPU'):
    print("Using GPU")
else:
    print("Using CPU")

def load_keras_model(model_path):
    """
    Load the accident detection model from a .keras file.
    """
    model = load_model(model_path)
    # Optionally, you can print the model summary:
    # model.summary()
    return model

def preprocess_image(image):
    """
    Preprocess the image for the Keras model.
    Adjusted to produce an input that, through the model's convolutional layers,
    yields a flattened feature vector of size 14,400 (i.e. a feature map of 120x120).
    
    The changes here use a larger center crop.
    """
    # Convert from BGR (OpenCV) to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(image_rgb)
    
    # Resize the image to 256x256 (or whatever size you used as the initial resize during training)
    resized = pil_img.resize((256, 256))
    
    # Adjust the center crop size:
    # Previously, cropping to 240x240 produced a feature map of 112x112.
    # To get a feature map of 120x120 (i.e. flattened size of 14,400),
    # we scale the crop size by approximately 120/112 ≈ 1.0714.
    # For example, 240 * 1.0714 ≈ 257 (or 258 rounded).
    new_width, new_height = 258, 258
    width, height = resized.size
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = left + new_width
    bottom = top + new_height
    cropped = resized.crop((left, top, right, bottom))
    
    # Convert to a numpy array and scale pixel values to [0, 1]
    image_array = np.array(cropped).astype(np.float32) / 255.0
    
    # Normalize using ImageNet statistics (change these if your training used different values)
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    image_norm = (image_array - mean) / std
    
    # Expand dimensions so the shape is (1, H, W, 3)
    input_image = np.expand_dims(image_norm, axis=0)
    return input_image

def process_image_keras(model, image):
    """
    Preprocess the image, run inference using the Keras model,
    and return a tuple (crash_detected, confidence).
    Assumes the model outputs two class scores (no crash, crash),
    where class index 1 corresponds to a detected crash.
    """
    input_image = preprocess_image(image)
    
    # Run inference
    predictions = model.predict(input_image)
    
    # Apply softmax to convert logits to probabilities
    probabilities = tf.nn.softmax(predictions[0]).numpy()
    
    # Determine predicted class and its confidence
    predicted_class = np.argmax(probabilities)
    confidence = float(np.max(probabilities))
    
    # Assume class index 1 means accident/crash detected
    crash_detected = (predicted_class == 1)
    return crash_detected, confidence

def fetch_camera_image(url):
    """
    Fetch an image from the camera URL and decode it using OpenCV.
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return image
        else:
            print("Error fetching image, status code:", response.status_code)
    except Exception as e:
        print("Error fetching image:", e)
    return None

def visualize_detection(crash_info):
    """
    Visualization placeholder: Print the crash event details and write to a JSON file.
    Replace or extend this with your actual visualization/alert integration.
    """
    json_output = json.dumps(crash_info, indent=4)
    print("Crash event detected:")
    print(json_output)
    
    with open("crash_event.json", "w") as outfile:
        outfile.write(json_output)

from collections import deque

def main():
    model = load_keras_model(MODEL_PATH)
    print("Model loaded successfully.")

    check_interval = 3
    alert_sent = False

    # Rolling buffers for timing (max length = 50)
    fetch_times = deque(maxlen=50)
    inference_times = deque(maxlen=50)
    loop_times = deque(maxlen=50)

    iteration = 0

    while True:
        start_loop = time.perf_counter()

        image_fetch_start = time.perf_counter()
        image = fetch_camera_image(CAMERA_URL)
        image_fetch_end = time.perf_counter()

        if image is None:
            print(f"[{datetime.now().isoformat()}] Failed to retrieve image. Retrying in {check_interval} seconds.")
            time.sleep(check_interval)
            continue

        processing_start = time.perf_counter()
        crash_detected, confidence = process_image_keras(model, image)
        processing_end = time.perf_counter()

        total_loop_time = time.perf_counter() - start_loop

        # Save times
        fetch_times.append(image_fetch_end - image_fetch_start)
        inference_times.append(processing_end - processing_start)
        loop_times.append(total_loop_time)

        # Display crash info
        if crash_detected and not alert_sent:
            timestamp_actual = datetime.now().isoformat()
            crash_info = {
                "where": CAMERA_LOCATION,
                "when_actual": timestamp_actual,
                "confidence": confidence
            }
            visualize_detection(crash_info)
            alert_sent = True
        else:
            print(f"[{datetime.now().isoformat()}] No crash detected. Confidence: {confidence:.2f}")
            alert_sent = False

        # Print individual performance
        print(f"--- Iteration {iteration + 1} Performance ---")
        print(f"Image Fetch Time     : {fetch_times[-1]:.3f} seconds")
        print(f"Inference Time       : {inference_times[-1]:.3f} seconds")
        print(f"Total Loop Time      : {loop_times[-1]:.3f} seconds")
        
        # Average report every 50 iterations
        if len(fetch_times) == 50:
            avg_fetch = sum(fetch_times) / 50
            avg_inference = sum(inference_times) / 50
            avg_loop = sum(loop_times) / 50

            avg_report = (
                f"\n=== 50 Iteration Average Report ({datetime.now().isoformat()}) ===\n"
                f"Average Image Fetch Time : {avg_fetch:.3f} seconds\n"
                f"Average Inference Time   : {avg_inference:.3f} seconds\n"
                f"Average Total Loop Time  : {avg_loop:.3f} seconds\n"
                f"=============================================================\n"
            )

            # Print to console
            print(avg_report)

            # Append to text file
            with open("performance_report.txt", "a") as report_file:
                report_file.write(avg_report)


        iteration += 1
        time.sleep(check_interval)



if __name__ == "__main__":
    main()
