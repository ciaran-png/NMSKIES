import tkinter as tk
from tkinter import messagebox, font, simpledialog, PhotoImage
import pytz
from datetime import datetime
from run_it_up2 import open_tleplan, run_automated2, run_apiinteraction, automated_observation_cycle, log_user_access, get_part_of_day
import urllib
from PIL import Image, ImageDraw, ImageFont
import os

def download_and_convert_image(url, jpg_filename, png_filename, size=(500, 500), observatory_coords=(305, 263), label_text="New Mexico Skies"):
    try:
        # Download the image
        print("Downloading image...")
        urllib.request.urlretrieve(url, jpg_filename)
        print("Image downloaded at:", os.path.abspath(jpg_filename))

        # Open the downloaded image
        with Image.open(jpg_filename) as img:
            # Resize the image
            img = img.resize(size, Image.Resampling.LANCZOS)  # Updated line
            
            # Draw a circle and label on the image
            draw = ImageDraw.Draw(img)
            draw.ellipse((observatory_coords[0]-4, observatory_coords[1]-4, observatory_coords[0]+4, observatory_coords[1]+4), fill='red')
            
            # Load a font
            font_path = "arial.ttf"  # Ensure this path is correct or accessible on your system
            try:
                font = ImageFont.truetype(font_path, 14)
            except IOError:
                print(f"Warning: Unable to load font '{font_path}'. Using default font.")
                font = ImageFont.load_default()
            
            # Draw text
            draw.text((314, 263), label_text, fill="white", font=font)
            
            # Save the modified image as PNG
            img.save(png_filename)
        
        print("Image processed. Final image at:", os.path.abspath(png_filename))
        return True
    except Exception as e:
        print(f"Error processing the image: {e}")
        return False

def update_image_label():
    jpg_filename = "weather.jpg"
    png_filename = "weather.png"
    image_url = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/sr/GEOCOLOR/600x600.jpg"

    if download_and_convert_image(image_url, jpg_filename, png_filename):
        if os.path.exists(png_filename):
            print("PNG file exists, updating label.")
            photo = tk.PhotoImage(file=png_filename)
            image_label.config(image=photo)
            image_label.image = photo  # keep a reference
        else:
            print("PNG file does not exist.")

    # Schedule the next update
    image_label.after(300000, update_image_label)  # Update every 5 minutes


def show_button_info(info_text):
    info_popup = tk.Toplevel(app)
    info_popup.title("Information")
    info_popup.geometry("300x200")  # Adjust size as needed

    info_label = tk.Label(info_popup, text=info_text, wraplength=280)
    info_label.pack(pady=10, padx=10)

    close_button = tk.Button(info_popup, text="Close", command=info_popup.destroy)
    close_button.pack(pady=10)

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

    personalized_title = f"{part_of_day} {user_name},\nWelcome to New Mexico Skies Command Center"
    app.title(personalized_title)
    log_user_access(user_name)
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

automated_cycle_button = tk.Button(automated_cycle_frame, text="Start Automated Cycle", command=automated_observation_cycle, font=button_font, bg="#00FF00", fg=text_color)
automated_cycle_button.pack(side=tk.LEFT)

info_button_cycle = tk.Button(automated_cycle_frame, text="?", command=lambda: show_button_info(automated_cycle_info), font=button_font, bg=button_color, fg=text_color)
info_button_cycle.pack(side=tk.LEFT, padx=5)

automated_cycle_status_label = tk.Label(automated_cycle_frame, text="Status: Idle", bg=background_color, fg=text_color, font=button_font)
automated_cycle_status_label.pack(side=tk.LEFT)

def update_checkbox_label():
    if skip_scripts_var.get():
        checkbox_status_label.config(text="Skipping TLE Updater")
    else:
        checkbox_status_label.config(text="Including TLE Updater")

skip_scripts_var = tk.BooleanVar(value=False)
skip_scripts_checkbox = tk.Checkbutton(app, text="Skip TLE Updater", variable=skip_scripts_var, onvalue=True, offvalue=False, bg=background_color, fg=text_color, font=button_font, command=update_checkbox_label)
skip_scripts_checkbox.pack(pady=10)

checkbox_status_label = tk.Label(app, text="Including TLE Updater", bg=background_color, fg=text_color, font=button_font)
checkbox_status_label.pack(pady=5)

image_label = tk.Label(app)
image_label.pack(pady=5)

update_image_label()

app.mainloop()