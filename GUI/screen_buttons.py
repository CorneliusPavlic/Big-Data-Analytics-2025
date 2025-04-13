import tkinter as tk
from tkintermapview import TkinterMapView

is_monitoring = False

def onMonitorButtonPressed(button, monitor_func):
    global is_monitoring
    is_monitoring = not is_monitoring
    monitor_func(is_monitoring)
    if is_monitoring:
        button.configure(
            text="Stop Monitoring",
            bg="#28a745",
            relief="flat"
        )
    else:
        button.configure(
            text="Start Monitoring",
            bg="#007ACC",
            relief="flat"
        )

def add_monitoring_button(parent_frame, monitor_func):
    monitorButton = tk.Button(
        parent_frame,
        text="Start Monitoring", 
        bg="#007ACC",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        bd=0,
        padx=15, pady=8,
        highlightthickness=0,
        activeforeground="white"
    )
       
    monitorButton.configure(command=lambda: onMonitorButtonPressed(monitorButton, monitor_func))
    monitorButton.place(relx=0.95, rely=0.05, anchor="ne")

def add_all_buttons(parent_frame, button_functions):
    monitor_func = button_functions["Monitor"]
    add_monitoring_button(parent_frame, monitor_func)