import requests
import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import time
import json
from datetime import datetime

# Constants
CAMERA_URL = "https://itscameras.dot.state.oh.us/images/CLE/CLE032.jpg"
CAMERA_LOCATION = "Cleveland, OH Camera CLE032"  # Hard-coded camera location
MODEL_PATH = "accident_detection_model.pth"

# Determine device (CUDA GPU or CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

def load_model(model_path):
    """
    Load the accident detection model using the ResNet50 architecture
    and replace the final fully connected layer for 2 classes.
    """
    # Initialize a ResNet50 model. Since the state dict is saved,
    # we do not need pretrained weights.
    model = models.resnet50(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2)  # Two classes: no crash (0), crash (1)
    
    # Load the state dictionary saved from your training
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model

# Define the image transformation - adjust if your training transform was different.
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def process_image(model, image):
    """
    Preprocess the image and run inference to determine if a crash is detected.
    Returns a tuple: (crash_detected, confidence)
    """
    # Convert BGR (OpenCV) to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Apply transformations as used during training.
    image_transformed = transform(image_rgb)
    image_transformed = image_transformed.unsqueeze(0)  # (1, C, H, W)
    image_transformed = image_transformed.to(device)
    
    # Inference
    with torch.no_grad():
        outputs = model(image_transformed)
        
    # Apply softmax to obtain probabilities
    probabilities = torch.nn.functional.softmax(outputs, dim=1)
    confidence, predicted = torch.max(probabilities, dim=1)
    predicted = predicted.item()
    confidence = confidence.item()
    
    # Assume class index 1 corresponds to accident/crash.
    crash_detected = (predicted == 1)
    return crash_detected, confidence

def fetch_camera_image(url):
    """
    Fetch an image from the camera URL and decode it.
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
    Visualization placeholder: Print the crash event details as JSON and write to a file.
    You can later replace this with your visualization integration.
    """
    json_output = json.dumps(crash_info, indent=4)
    print("Crash event detected:")
    print(json_output)
    
    with open("crash_event.json", "w") as outfile:
        outfile.write(json_output)

def main():
    # Load the model
    model = load_model(MODEL_PATH)
    print("Model loaded successfully on device:", device)
    
    # Define how often to check for new images (in seconds)
    check_interval = 30
    alert_sent = False  # Flag to avoid duplicate alerts; modify logic as needed.
    
    while True:
        image = fetch_camera_image(CAMERA_URL)
        if image is None:
            print("Failed to retrieve image. Retrying in", check_interval, "seconds.")
            time.sleep(check_interval)
            continue
        
        crash_detected, confidence = process_image(model, image)
        if crash_detected and not alert_sent:
            timestamp_actual = datetime.now().isoformat()
            crash_info = {
                "where": CAMERA_LOCATION,
                "when_actual": timestamp_actual,
                "confidence": confidence
            }
            # Hook your visualization system here.
            visualize_detection(crash_info)
            alert_sent = True
        else:
            print(f"{datetime.now().isoformat()}: No crash detected. Confidence: {confidence:.2f}")
            alert_sent = False
        
        time.sleep(check_interval)

if __name__ == "__main__":
    main()
