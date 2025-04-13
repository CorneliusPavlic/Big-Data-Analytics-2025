import tkinter as tk
from tkintermapview import TkinterMapView

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
        activebackground="gray",
        activeforeground="white"
    )
       
    monitorButton.configure(command=lambda: onMonitorButtonPressed(monitorButton, monitor_func))
    monitorButton.place(relx=0.95, rely=0.11, anchor="ne")


# resolve button
def onResolveButtonPressed(resolveButton, resolve_func):
    resolve_func()

def add_resolve_button(parent_frame, resolve_func):
    resolveButton = tk.Button(
        parent_frame,
        text="Resolve",
        bg="#007ACC",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        bd=0,
        padx=15, pady=8,
        highlightthickness=0,
        activebackground="gray",
        activeforeground="white"
    )
    
    resolveButton.configure(command=lambda: onResolveButtonPressed(resolveButton, resolve_func))
    resolveButton.place(relx=0.95, rely=0.18, anchor="ne")


# district button
def add_district_dropbutton(parent_frame, district_list, district_func):
    selected_district = tk.StringVar()
    selected_district.set(district_list[0])
    
    district_dropdown = tk.OptionMenu(
        parent_frame,
        selected_district,
        *district_list,
        command=district_func
    )
    
    district_dropdown.config(
        bg="#007ACC",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        bd=0,
        padx=15, pady=8,
        highlightthickness=0,
        activebackground="gray",
        activeforeground="white"
    )
    
    district_dropdown.place(relx=0.95, rely=0.05, anchor="ne")


# test crash button
def onTestCrashButtonPressed(testCrashButton, test_func):
    test_func()

def add_test_crash_button(parent_frame, test_func):
    testCrashButton = tk.Button(
        parent_frame,
        text="Test Crash",
        bg="#007ACC",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        bd=0,
        padx=15, pady=8,
        highlightthickness=0,
        activebackground="gray",
        activeforeground="white"
    )
    
    testCrashButton.configure(command=lambda: onTestCrashButtonPressed(testCrashButton, test_func))
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