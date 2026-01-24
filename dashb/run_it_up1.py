# -*- coding: utf-8 -*-
import requests
import tkinter as tk
from tkinter import messagebox, font, simpledialog, PhotoImage
import subprocess
from datetime import datetime, timezone, timedelta
import threading
import json
import pytz
import os
import re
import sys
import traceback
import urllib.request
import time
from imagefunctions import download_and_convert_image, update_image_label
from misc import speak_message, log_user_access, update_sun_times, check_observatory_status, get_part_of_day
print(sys.executable)

# Rewriting the selected code to replace f-strings with .format() for Python 2.7 compatibility

def show_button_info(info_text):
    info_popup = tk.Toplevel(app)
    info_popup.title("Information")
    info_popup.geometry("300x200")  # Adjust size as needed

    info_label = tk.Label(info_popup, text=info_text, wraplength=280)
    info_label.pack(pady=10, padx=10)

    close_button = tk.Button(info_popup, text="Close", command=info_popup.destroy)
    close_button.pack(pady=10)

def schedule_automation_function():
    # Prompt the user for the number of days
    num_days = simpledialog.askinteger("Input", "Enter number of days for observation cycle:", parent=app)
    if num_days is None or num_days <= 0:  # User cancelled or entered an invalid number
        return

    # Prompt the user for the daily start time
    daily_start_time_str = simpledialog.askstring("Input", "Enter daily start time (HH:MM):", parent=app)
    if not daily_start_time_str:  # User cancelled
        return
    
    try:
        daily_start_time = datetime.strptime(daily_start_time_str, "%H:%M").time()
    except ValueError:
        messagebox.showerror("Error", "Invalid time format. Please enter time in HH:MM format.")
        return

    # Schedule the observation cycle
    current_time = datetime.now()
    for day in range(num_days):
        cycle_datetime = current_time.replace(hour=daily_start_time.hour, minute=daily_start_time.minute, second=0, microsecond=0) + timedelta(days=day)

        if cycle_datetime < current_time:
            cycle_datetime += timedelta(days=1)

        wait_time = (cycle_datetime - current_time).total_seconds()
        threading.Timer(wait_time, automated_observation_cycle).start()

        # Print the scheduled time for the observation cycle
        print("Automated observation cycle scheduled for {0}".format(cycle_datetime.strftime('%Y-%m-%d %H:%M:%S')))

    # Update the status label
    schedule_automation_status_label.config(text="Scheduled for {0} days".format(num_days))

def run_script(script_name, status_label, shutdown=False, args=None, completion_flag=None):
    def target():
        try:
            status_label.config(text="Status: Running")
            script_args = ['python', script_name] + (args if args is not None else [])
            if shutdown:
                script_args.append('shutdown')

            subprocess.run(script_args, check=True)
            status_label.config(text="Status: Finished")
            if completion_flag is not None:
                completion_flag.set()  # Set the flag when the script completes
        except Exception as e:
            error_message = "Error running script: {0}\n{1}".format(e, traceback.format_exc())
            print(error_message)  # Print the error message in the terminal
            status_label.config(text="Status: Error")

    threading.Thread(target=target).start()

def run_apiinteraction():
    run_script('api_interaction.py', tle_updater_status_label)

def open_tleplan():
    try:
        os.startfile('tleplan.txt')
    except Exception as e:
        messagebox.showerror("Error", "Failed to open tleplan.txt: {0}".format(e))

def run_automated2():
    run_script('automated2.py', automated2_status_label)

def automated_observation_cycle(num_days=None, daily_start_time=None):
    if num_days is None:
        num_days = 1  # Default number of days
    if daily_start_time is None:
        # Default start time to current time
        daily_start_time = datetime.now().time()  

    print("Automated observation cycle started.")
    for day in range(num_days):
        if not skip_scripts_var.get():
            # Run the TLE Updater script if the checkbox is not checked
            try:
                print("Running the TLE updater script.")
                subprocess.run(['python', 'api_interaction.py', '--non-interactive', '--days', '1', '--observation-window', '2'], check=True)
                tle_updater_status_label.config(text="TLE Updater: Finished")
            except subprocess.CalledProcessError as e:
                tle_updater_status_label.config(text="TLE Updater: Error ({0})".format(e))
                continue  # Skip the rest of the loop on error

        # Fetch Sunrise and Sunset Times
        print("Fetching sunrise and sunset times.")
        sunrise_time_next_day, sunset_time_today = update_sun_times()
        
        if sunrise_time_next_day and sunset_time_today:
            print("Sunset today and sunrise tomorrow times retrieved: {0}, {1}".format(sunset_time_today, sunrise_time_next_day))

            # Calculate Start and Shutdown Times
            print("Calculating start and shutdown times.")
            start_time = sunset_time_today + timedelta(minutes=5)
            shutdown_time = sunrise_time_next_day - timedelta(minutes=8)
            print("Start time: {0}, Shutdown time: {1}".format(start_time, shutdown_time))

            # Start Observation Function
            def start_observation():
                start_check_time = datetime.now()  # Record the time when checking starts
                while True:
                    status = check_observatory_status()
                    if status == "Open":
                        print("Observatory is open. Starting the observation script.")
                        break
                    elif (datetime.now() - start_check_time).total_seconds() > 5 * 3600:
                        print("Observatory not open for 5 hours. Initiating shutdown.")
                        initiate_shutdown()
                        exit()  # Quit the script
                    else:
                        print("Observatory is not open. Checking again in one minute.")
                        time.sleep(60)

                # Run Automated2.py Script
                run_script('automated2.py', automated2_status_label)

            # Initiate Shutdown Function
            def initiate_shutdown():
                print("Initiating the shutdown sequence.")
                run_script('automated2.py', automated2_status_label, shutdown=True)

            current_time = datetime.now(pytz.timezone('America/Denver'))

            # Check if it's already past the start time
            if current_time > start_time:
                print("Already past start time. Initiating observation immediately.")
                start_observation()  # Call the start observation function directly
            else:
                print("Scheduling the start of observation.")
                schedule_task(start_time, start_observation)  # Schedule as normal

            # Schedule shutdown as normal
            print("Scheduling the shutdown of observation.")
            schedule_task(shutdown_time, initiate_shutdown)

        else:
            print("Failed to retrieve sunrise and sunset times or data is incomplete.")
            # Implement your error handling or default setting here
            pass

        print("Automated observation cycle completed.")

def schedule_task(task_time, task_function):
    # Get the current time with the same timezone as task_time
    now = datetime.now(pytz.timezone('America/Denver'))
    wait_time = (task_time - now).total_seconds()
    if wait_time > 0:
        threading.Timer(wait_time, task_function).start()

def schedule_daily_cycle(num_days, daily_start_time):
    current_time = datetime.now()
    for day in range(num_days):
        # Calculate the date and time for the next cycle
        cycle_time = current_time.replace(hour=daily_start_time.hour, minute=daily_start_time.minute, second=0, microsecond=0) + timedelta(days=day)

        # If the cycle time is in the past, schedule for the next day
        if cycle_time < current_time:
            cycle_time += timedelta(days=1)

        wait_time = (cycle_time - current_time).total_seconds()
        threading.Timer(wait_time, automated_observation_cycle).start()


app = tk.Tk()
app.title("New Mexico Skies Command Center")

# Prompt for user's first name
user_name = simpledialog.askstring("Enter Name", "Please enter your first name:")

if user_name:
    # Fetch the current time in MTC timezone
    mtc_zone = pytz.timezone('America/Denver')
    mtc_time = datetime.now(mtc_zone)
    
    # Get the part of the day
    part_of_day = get_part_of_day(mtc_time.hour)

    greeting_message = "{}, {}, welcome to the New Mexico Skies Observatory Command Station. Select an option below to initiate the command controls. Happy Observing".format(part_of_day, user_name)
    
    # Assume you have a function 'speak_message' defined elsewhere
    # Run the speak_message function in a separate thread
    threading.Thread(target=speak_message, args=(greeting_message,)).start()

    personalized_title = f"{part_of_day} {user_name},\nWelcome to New Mexico Skies Command Center"
    app.title(personalized_title)  # Ensure 'app' is your Tkinter app instance
    log_user_access(user_name)  # Assuming this function is defined elsewhere
else:
    personalized_title = "Welcome to New Mexico Skies Command Center"
    app.title(personalized_title)

# Set the window size and make it not resizable
app.geometry("575x920")

# Modern NASA-style color scheme
background_color = "#D9D9D9"  # Light grey
button_color = "#404040"  # Dark grey
text_color = "#FFFFFF"  # White

# Define a new color for the 'Run all' button
run_all_button_color = "#00FF00"  # Green color

app.configure(bg=background_color)

# Modern font for the title and buttons
title_font = font.Font(family="Arial", size=18, weight="bold")
button_font = font.Font(family="Arial", size=12, weight="bold")

# Modify title label
title_label = tk.Label(app, text=personalized_title, bg=background_color, fg=text_color, font=title_font)
title_label.pack(pady=20)

button_style = {'font': button_font, 'bg': button_color, 'fg': text_color}

# Example for the TLE Updater button
tle_updater_info = (
    "TLE Updater Button:\n\n"
    "Description: The TLE (Two-Line Element) Updater fetches the visible overhead passes for selected satellites. "
    "It uses the N2YO API to process a list of NORAD satellite IDs and calculates their observation times. "
    "This script efficiently manages observation schedules by filtering out overlapping times and ensuring a minimum "
    "one-minute gap between consecutive observations.\n\n"
    "Usage:\n"
    "1. Update Existing NORAD IDs: Automatically updates observation times for previously saved satellite IDs, "
    "defaulting to a one-day-ahead observation period.\n"
    "2. Enter New NORAD IDs: Input a new list of NORAD IDs (comma-separated) and specify the number of days (1-10) "
    "for which you want to fetch observation periods.\n"
    "3. Enter the observation window for the satellite overpasses 'full' for the entire observation or ex. 2 minute "
    "observation window +/- 2 minutes from the midpoint of the observation.\n\n"
    "This tool is essential for planning and scheduling satellite tracking activities, ensuring a streamlined observation process."
)

tle_updater_frame = tk.Frame(app, bg=background_color)
tle_updater_frame.pack(pady=5)

button1 = tk.Button(tle_updater_frame, text="Run TLE Updater", command=lambda: run_apiinteraction(), **button_style)
button1.pack(side=tk.LEFT)

info_button1 = tk.Button(tle_updater_frame, text="?", command=lambda: show_button_info(tle_updater_info), font=button_font, bg=button_color, fg=text_color)
info_button1.pack(side=tk.LEFT, padx=5)

tle_updater_status_label = tk.Label(tle_updater_frame, text="Status: Idle", bg=background_color, fg=text_color, font=button_font)
tle_updater_status_label.pack(side=tk.LEFT)


# Add new button for opening tleplan.txt
see_schedule_button = tk.Button(app, text="See Observation Schedule", command=open_tleplan, **button_style)
see_schedule_button.pack(pady=10)

# Automated2.py Function Frame
automated2_info = (
    "Run Observation Button:\n\n"
    "Description: Triggers the central command script for telescope, dome, and tracking/imaging operations.\n\n"
    "Functionality:\n"
    "1. Initiates telescope and dome operations.\n"
    "2. Observation Execution: Executes observations listed in tleplan.txt through the run_observer script.\n"
    "3. Executes shutdown of equipment after run_observer concludes.\n\n"
    "Key for automated and efficient satellite observation."
)

automated2_frame = tk.Frame(app, bg=background_color)
automated2_frame.pack(pady=5)

button3 = tk.Button(automated2_frame, text="Run Observation(s)", command=lambda: run_automated2(), **button_style)
button3.pack(side=tk.LEFT)

info_button3 = tk.Button(automated2_frame, text="?", command=lambda: show_button_info(automated2_info), font=button_font, bg=button_color, fg=text_color)
info_button3.pack(side=tk.LEFT, padx=5)

automated2_status_label = tk.Label(automated2_frame, text="Status: Idle", bg=background_color, fg=text_color, font=button_font)
automated2_status_label.pack(side=tk.LEFT)

# Automated Observation Cycle Frame
automated_cycle_info = (
    "Automated Observation Cycle Button:\n\n"
    "Description: Initiates a sequential execution of three primary observation scripts.\n\n"
    "Functionality:\n"
    "1. TLE Updater: Begins with TLE updater using default NORAD IDs (in the Planewave, Scripts folder - STARLINK SATELLITES) for a one-day-ahead observation period.\n"
    "2. Observation Script Execution: Waits 10 minutes post-sunset to start the observation script.\n"
    "3. Observatory Status Check: Checks observatory status before initiating observations.\n"
    "4. Pre-Sunrise Shutdown: Sends shutdown request to the observation script 10 minutes before sunrise.\n\n"
    "Checkbox Option: Allows skipping TLE updater and filter via a checkbox below this button.\n\n"
    "Ensures a systematic and efficient observation process."
)

automated_cycle_frame = tk.Frame(app, bg=background_color)
automated_cycle_frame.pack(pady=5)

# Customizing the Automated Observation Cycle button to be green
automated_cycle_button = tk.Button(automated_cycle_frame, text="Start Automated Cycle", command=automated_observation_cycle, font=button_font, bg="#00FF00", fg=text_color)  # Green background
automated_cycle_button.pack(side=tk.LEFT)

# Question mark button for Automated Observation Cycle
info_button_cycle = tk.Button(automated_cycle_frame, text="?", command=lambda: show_button_info(automated_cycle_info), font=button_font, bg=button_color, fg=text_color)
info_button_cycle.pack(side=tk.LEFT, padx=5)

automated_cycle_status_label = tk.Label(automated_cycle_frame, text="Status: Idle", bg=background_color, fg=text_color, font=button_font)
automated_cycle_status_label.pack(side=tk.LEFT)


def update_checkbox_label():
    # Update the label based on the checkbox state
    if skip_scripts_var.get():
        checkbox_status_label.config(text="Skipping TLE Updater")
    else:
        checkbox_status_label.config(text="Including TLE Updater")

# Checkbox to skip TLE Updater and One Minute Man
skip_scripts_var = tk.BooleanVar(value=False)  # Initialize with False (not checked)
skip_scripts_checkbox = tk.Checkbutton(app, text="Skip TLE Updater", variable=skip_scripts_var, onvalue=True, offvalue=False, bg=background_color, fg=text_color, font=button_font, command=update_checkbox_label)
skip_scripts_checkbox.pack(pady=10)

# Label to display the state of the checkbox
checkbox_status_label = tk.Label(app, text="Including TLE Updater", bg=background_color, fg=text_color, font=button_font)
checkbox_status_label.pack(pady=5)

# Function to handle the button click
def on_schedule_cycle_button_click():
    num_days = ask_user_for_number_of_days()  # Implement to get input from the user
    daily_start_time = ask_user_for_daily_start_time()  # Implement to get input from the user

    schedule_daily_cycle(num_days, daily_start_time)


schedule_automation_info = (
    "Schedule Automated Observation Cycle Button:\n\n"
    "Description: Allows scheduling of automated observation cycles over multiple days at specified times.\n\n"
    "Functionality:\n"
    "1. User defines the number of days for the observation cycle.\n"
    "2. User sets a daily start time for the cycle.\n"
    "3. The script automatically initiates the observation cycle at the specified time each day.\n"
    "4. Observations start 10 minutes before sunset and end 15 minutes before the next day's sunrise.\n\n"
    "Provides flexibility for extended and scheduled astronomical observations."
)
# Schedule Automated Observation Cycle Frame
schedule_automation_frame = tk.Frame(app, bg=background_color)
schedule_automation_frame.pack(pady=5)

# Schedule Automated Observation Cycle Button
schedule_automation_button = tk.Button(schedule_automation_frame, text="Schedule Automated Observation Cycle", command=lambda: schedule_automation_function(), **button_style)
schedule_automation_button.pack(side=tk.LEFT)

# Info Button for Schedule Automated Observation Cycle
info_button_schedule_automation = tk.Button(schedule_automation_frame, text="?", command=lambda: show_button_info(schedule_automation_info), font=button_font, bg=button_color, fg=text_color)
info_button_schedule_automation.pack(side=tk.LEFT, padx=5)

# Status Label for Schedule Automated Observation Cycle
schedule_automation_status_label = tk.Label(schedule_automation_frame, text="Status: Idle", bg=background_color, fg=text_color, font=button_font)
schedule_automation_status_label.pack(side=tk.LEFT)

# Load and display the image
#resized_image_path = 'resized_privateer.png'  # Path to your manually resized image
#img = PhotoImage(file=resized_image_path)  # Load the image
#image_label = tk.Label(app, image=img, bg=background_color)  # Create a label to display the image
#image_label.pack(pady=10)  # Add the label to the GUI, centered at the bottom

image_label = tk.Label(app)
image_label.pack(pady=5)

# Start the update process
update_image_label()

app.mainloop()
