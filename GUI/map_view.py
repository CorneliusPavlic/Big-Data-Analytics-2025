import tkinter as tk
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk
import base64
import io


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
