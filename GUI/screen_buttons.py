import tkinter as tk
from tkintermapview import TkinterMapView
import customtkinter as ctk

# button variables
is_monitoring = False

# monitor button
def onMonitorButtonPressed(button, monitor_func):
    global is_monitoring
    is_monitoring = not is_monitoring
    monitor_func(is_monitoring)
    if is_monitoring:
        button.configure(
            text="Stop Monitoring",
            fg_color="#28a745"
        )
    else:
        button.configure(
            text="Start Monitoring",
            fg_color="#007ACC"
        )

def add_monitoring_button(parent_frame, monitor_func):
    monitorButton = ctk.CTkButton(
        master=parent_frame,
        text="Start Monitoring",
        fg_color="#007ACC",
        bg_color="#007ACC",
        hover_color="#005A99",
        text_color="white",
        font=("Segoe UI", 12, "bold"),
        width=100,
        height=40,
        command=lambda: onMonitorButtonPressed(monitorButton, monitor_func),
    )
       
    monitorButton.place(relx=0.95, rely=0.11, anchor="ne")


# resolve button
def onResolveButtonPressed(resolveButton, resolve_func):
    resolve_func()

def add_resolve_button(parent_frame, resolve_func):
    resolveButton = ctk.CTkButton(
        master=parent_frame,
        text="Resolve",
        fg_color="#007ACC",
        bg_color="#007ACC",
        hover_color="#005A99",
        text_color="white",
        font=("Segoe UI", 12, "bold"),
        width=100,
        height=40,
        command=lambda: onResolveButtonPressed(resolveButton, resolve_func),
    )
    
    # resolveButton.configure(command=lambda: onResolveButtonPressed(resolveButton, resolve_func))
    resolveButton.place(relx=0.95, rely=0.18, anchor="ne")


# district button
def add_district_dropbutton(parent_frame, district_list, district_func):
    selected_district = tk.StringVar()
    selected_district.set(district_list[0])
    
    district_dropdown = ctk.CTkComboBox(
        master=parent_frame,
        values=district_list,
        variable=selected_district,
        command=district_func,
        width=200,
        height=40,
        font=("Segoe UI", 12, "bold"),
        state="readonly",
    )
    
    district_dropdown.configure(
        fg_color="#007ACC",
        bg_color="#007ACC",
        text_color="white",
    )
    
    district_dropdown.configure(
        dropdown_fg_color="#007ACC",
    )
    
    district_dropdown.place(relx=0.95, rely=0.05, anchor="ne")


# test crash button
def onTestCrashButtonPressed(testCrashButton, test_func):
    test_func()

def add_test_crash_button(parent_frame, test_func):
    testCrashButton = ctk.CTkButton(
        master=parent_frame,
        text="Test Crash",
        fg_color="#007ACC",
        bg_color="#007ACC",
        hover_color="#005A99",
        text_color="white",
        font=("Segoe UI", 12, "bold"),
        width=140,
        height=40,
        command=lambda: onTestCrashButtonPressed(testCrashButton, test_func),
    )
    
    testCrashButton.place(relx=0.95, rely=0.95, anchor="se")
    
    
def add_all_buttons(parent_frame, button_data):
    monitor_func = button_data["MonitorCallback"]
    add_monitoring_button(parent_frame, monitor_func)
    
    resolve_func = button_data["ResolveCallback"]
    add_resolve_button(parent_frame, resolve_func)
    
    district_list = button_data["DistrictList"]
    district_callback = button_data["DistrictCallback"]
    add_district_dropbutton(parent_frame, district_list, district_callback)
    
    test_crash_callback = button_data["TestCrashCallback"]
    add_test_crash_button(parent_frame, test_crash_callback)