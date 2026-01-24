# -*- coding: utf-8 -*-
import requests
import tkinter as tk
from tkinter import messagebox, font, simpledialog, PhotoImage
from PIL import Image, ImageDraw, ImageFont
import subprocess
from datetime import datetime, timezone, timedelta
from gui_setup import *
from gui_setup import skip_scripts_var, update_image_label
import threading
import json
import pytz
import os
import re
import sys
import traceback
import urllib.request
import time
print(sys.executable)

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
            error_message = f"Error running script: {e}\n{traceback.format_exc()}"
            print(error_message)  # Print the error message in the terminal
            status_label.config(text="Status: Error")

    threading.Thread(target=target).start()

def run_apiinteraction():
    run_script('api_interaction.py', tle_updater_status_label)

def open_tleplan():
    try:
        os.startfile('tleplan.txt')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open tleplan.txt: {e}")

def run_automated2():
    run_script('automated2.py', automated2_status_label)

# Function to determine the part of the day
def get_part_of_day(hour):
    return (
        "Good morning" if 5 <= hour <= 11
        else "Good afternoon" if 12 <= hour <= 17
        else "Good evening"
    )


def log_user_access(user_name):
    with open("access_log.txt", "a") as log_file:
        log_file.write(f"{user_name} accessed the application at {datetime.now()}\n")

def check_observatory_status():
    try:
        url = "https://nmskies.com/weather.php"
        response = requests.get(url)
        html_content = response.text

        # Use regular expression to find the image URL
        match = re.search(r'images/(daylight\.jpg|open\.jpg|closed\.jpg)\?', html_content)
        if match:
            img_file = match.group(1)
            if "daylight.jpg" in img_file:
                status = "Daylight (Closed)"
            elif "open.jpg" in img_file:
                status = "Open"
            elif "closed.jpg" in img_file:
                status = "Closed"
            else:
                status = "Unknown"
        else:
            status = "Status image not found"

        return status  # Returning the status string instead of displaying it
    except Exception as e:
        print(f"Failed to check observatory status: {e}")
        return "Error"  # Return an error status in case of an exception

def update_sun_times():
    try:
        lat, lng = 32.957313, -105.742485  # Coordinates for Cloudcroft, New Mexico
        today = datetime.now(pytz.timezone('America/Denver')).date()
        tomorrow = today + timedelta(days=1)

        # Fetch sunset time for today
        sunset_response = requests.get(f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&date={today}&formatted=0")
        # Fetch sunrise time for tomorrow
        sunrise_response = requests.get(f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&date={tomorrow}&formatted=0")

        if sunset_response.status_code != 200 or sunrise_response.status_code != 200:
            print(f"Failed to retrieve data from API. Status codes: {sunset_response.status_code}, {sunrise_response.status_code}")
            return None, None

        sunset_data = sunset_response.json()
        sunrise_data = sunrise_response.json()

        if 'results' not in sunset_data or 'sunset' not in sunset_data['results']:
            print("Malformed sunset API response: Missing 'results' or 'sunset' data.")
            return None, None

        if 'results' not in sunrise_data or 'sunrise' not in sunrise_data['results']:
            print("Malformed sunrise API response: Missing 'results' or 'sunrise' data.")
            return None, None

        sunset_utc = datetime.fromisoformat(sunset_data['results']['sunset'])
        sunrise_utc = datetime.fromisoformat(sunrise_data['results']['sunrise'])

        mountain_time = pytz.timezone('America/Denver')
        sunset_local = sunset_utc.replace(tzinfo=timezone.utc).astimezone(mountain_time)
        sunrise_local = sunrise_utc.replace(tzinfo=timezone.utc).astimezone(mountain_time)

        return sunrise_local, sunset_local
    except Exception as e:
        print(f"Error in update_sun_times: {e}")
        return None, None


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
                tle_updater_status_label.config(text=f"TLE Updater: Error ({e})")
                continue  # Skip the rest of the loop on error

        # Fetch Sunrise and Sunset Times
        print("Fetching sunrise and sunset times.")
        sunrise_time_next_day, sunset_time_today = update_sun_times()
        
        if sunrise_time_next_day and sunset_time_today:
            print(f"Sunset today and sunrise tomorrow times retrieved: {sunset_time_today}, {sunrise_time_next_day}")

            # Calculate Start and Shutdown Times
            print("Calculating start and shutdown times.")
            start_time = sunset_time_today + timedelta(minutes=5)
            shutdown_time = sunrise_time_next_day - timedelta(minutes=8)
            print(f"Start time: {start_time}, Shutdown time: {shutdown_time}")

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
