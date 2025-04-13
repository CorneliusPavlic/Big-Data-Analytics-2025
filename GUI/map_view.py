import tkinter as tk
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk
import base64
import io

# variable
marker = None

# create map widget
def create_map_widget(root):
    gmap_widget = TkinterMapView(root, width=1000, height=500)
    gmap_widget.pack(fill="both", side="right")
    # set map center to Ohio
    gmap_widget.set_position(40, -83)
    gmap_widget.set_zoom(7)
    
    return gmap_widget

# function to display the crash on the map
def add_crash_marker(gmap_widget, crash, show_image_func):
    # convert base64 image to displayable image in tkinter
    B64Image = base64.b64decode(crash["image"])
    fileImage = io.BytesIO(B64Image)
    PILImage = Image.open(fileImage)
    tkImage = ImageTk.PhotoImage(PILImage)
    
    # create marker for crash
    marker = gmap_widget.set_marker(crash["location"]["longitude"], crash["location"]["latitude"], 
                                    text=crash["time"], command=lambda m=None: show_image_func(tkImage))
    return marker

# pop up window for displaying photo of crash
def showIMG(root, photo):
    popup = tk.Toplevel(root)
    popup.title("Crash Image")
    popup.geometry("250x250")
    imageLabel = tk.Label(popup,image=photo)
    imageLabel.pack()

# animation for a more smooth zoom
def zoom_in_animation(gmap_widget, target_zoom, delay):
    current_zoom = gmap_widget.zoom
    if current_zoom < target_zoom:
        gmap_widget.set_zoom(current_zoom + 1)
        gmap_widget.after(delay, lambda: zoom_in_animation(gmap_widget, target_zoom, delay))

# zooms in on the crash
def zoom_in_crash(gmap_widget, crash):
    # crash location
    lat = crash["location"]["latitude"]
    lon = crash["location"]["longitude"]
    
    # set map center to crash location
    gmap_widget.set_position(lon, lat)
    zoom_in_animation(gmap_widget, target_zoom=15, delay=100)
    
# new crash data
def new_crash(gmap_widget, crash, root):
    global marker
    marker = add_crash_marker(gmap_widget, crash, lambda photo: showIMG(root, photo))
    zoom_in_crash(gmap_widget, crash)

# resolves crash
def resolve_crash(callback):
    global marker
    if marker:
        marker.delete() # delete the marker
        marker = None
    callback(None) # monitor for next crash in queue