import tkinter as tk
from map_view import create_map_widget, add_crash_marker, showIMG
from screen_buttons import add_all_buttons
import time
from queue import Queue
import os
import json
import base64

# variables
stream = "./DataStream" # location of json files
queue = Queue() # holds crash data objects
districts = ["District 1", "District 2", "District 3"] # available districts - get this info from a seperate file once we determine districts and their ranges
isMonitoring = False

# create root page
root = tk.Tk()
root.title("Motor Vehicle Collision Detection System")
root.configure(background="gray")
root.minsize(1280,720)
root.maxsize(1280,720)

# map widget
gmap_widget = create_map_widget(root)

# map marker
marker = None

# constantly checks for new crashes
def monitor():
    files = [f for f in os.listdir(stream) if f.endswith('.json')] # gather any files in stream folder
    # go through each file
    for filename in files: 
        fullPath = os.path.join(stream, filename)
        if os.path.isfile(fullPath): # check if a file
            with open(fullPath, 'r') as f:
                data = json.load(f) 
                # for below statement, change logic to check if data["longitude"] and data["latitiude"] are within the current district (variable.get())
                # will have to reference a file containing the four corner coordinates of each district
                if (True):
                    queue.put(data) # add crash to queue
            time.sleep(0.1) # delay so file closes
            os.remove(fullPath) # delete original json file
    root.after(500,monitor) # keep monitoring every 500 ms

# displays latest crash location
def startMonitoring(shouldMonitor):
    # toggles monitoring
    global isMonitoring
    if shouldMonitor is None:
        if not isMonitoring:
            return
    else:
        isMonitoring = shouldMonitor
        if not isMonitoring:
            return

    print("Monitoring!")
    # check if any crashes are present
    if (not queue.empty()):
        crash = queue.get()
        # create marker for crash
        global marker # marker displaying accident
        marker = add_crash_marker(gmap_widget, crash, lambda photo: showIMG(root, photo))
    else:
        root.after(500, lambda: startMonitoring(None)) # keep monitoring if no crash is found yet

# resolves the most recent crash, moves onto looking for the next
def resolve():
    global marker
    if marker:
        marker.delete() # delete the marker
        marker = None
        startMonitoring(None) # monitor for next crash in queue

# creates a test crash json file
def test():
    # Open the image file and encode it
    with open("image/testIMG.jpg", "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode('utf-8')  # decode to string
    # Create the dictionary
    dictionary = {
        "location": {
            "longitude": 41.144718,
            "latitude": -81.341832
        },
        "time": "14:32:06",
        "image": encoded_image
    }
    # Output to JSON file
    with open("./DataStream/test.json", "w") as json_file:
        json.dump(dictionary, json_file, indent=4)

# add screen buttons
button_data ={
    "MonitorCallback": startMonitoring,
    "ResolveCallback": resolve,
    "DistrictList": districts,
    "DistrictCallback": None,
    "TestCrashCallback": test
}
add_all_buttons(gmap_widget, button_data)

# loops
root.after(500,monitor)
root.mainloop()
