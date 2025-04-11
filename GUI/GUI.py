import tkinter as tk
from tkintermapview import TkinterMapView # pip install tknintermapview
from PIL import Image, ImageTk
import time
from queue import Queue
import os
import json
import base64
import io

# variables
stream = "./DataStream" # location of json files
queue = Queue() # holds crash data objects
districts = ["District 1", "District 2", "District 3"] # available districts - get this info from a seperate file once we determine districts and their ranges

# create root page
root = tk.Tk()
root.title("Motor Vehicle Collision Detection System")
root.configure(background="gray")
root.minsize(1280,720)
root.maxsize(1280,720)

# map widget
gmap_widget = TkinterMapView(root,width=1000,height=500)
gmap_widget.pack(fill="both",side="right")

# drop down menu for districts
variable = tk.StringVar(root)
variable.set(districts[0]) # default value
w = tk.OptionMenu(root, variable, *districts)
w.pack()

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

# pop up window for displaying photo of crash
def showIMG(photo):
    popup = tk.Toplevel(root)
    popup.title("Crash Image")
    popup.geometry("250x250")
    imageLabel = tk.Label(popup,image=photo)
    imageLabel.pack()

# displays latest crash location
def startMonitoring():
    # check if any crashes are present
    if (not queue.empty()):
        crash = queue.get()
        # convert base64 image to displayable image in tkinter
        B64Image = base64.b64decode(crash["image"])
        fileImage = io.BytesIO(B64Image)
        PILImage = Image.open(fileImage)
        tkImage = ImageTk.PhotoImage(PILImage)
        # create marker for crash
        global marker # marker displaying accident
        marker = gmap_widget.set_marker(crash["location"]["longitude"],crash["location"]["latitude"],text=crash["time"],command=lambda m=None: showIMG(tkImage))
    else:
        root.after(500,startMonitoring) # keep monitoring if no crash is found yet

# resolves the most recent crash, moves onto looking for the next
def resolve():
    marker.delete() # delete the marker
    startMonitoring() # monitor for next crash in queue

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


# starts monitoring for a given district
startMon = tk.Button(root,text="Start Monitoring",command=startMonitoring)
startMon.pack()

# resolves currently displayed crash
resolve = tk.Button(root,text="Resolve",command=resolve)
resolve.pack()

# creates a test crash json file
testButton = tk.Button(root,text="Create Test Crash",command=test)
testButton.pack()

# loops
root.after(500,monitor)
root.mainloop()
