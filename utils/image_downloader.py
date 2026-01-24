import os
import subprocess
import tkinter as tk
import urllib.request  # Added to handle image downloading
from tkinter import messagebox, font, simpledialog, PhotoImage

def download_and_convert_image(url, jpg_filename, png_filename, size=(500, 500), observatory_coords=(305, 263), label_text="New Mexico Skies"):
    try:
        # Download the image
        print("Downloading image...")
        urllib.request.urlretrieve(url, jpg_filename)
        print(f"Image downloaded at: {os.path.abspath(jpg_filename)}")

        # Resize, convert, add a marker, and label to the image
        print("Processing image...")
        size_str = f"{size[0]}x{size[1]}"
        draw_str = f"circle {observatory_coords[0]},{observatory_coords[1]} {observatory_coords[0] + 4},{observatory_coords[1]}"
        label_position = "+314+263"  # Adjusted label position
        subprocess.call(['magick', jpg_filename, '-resize', size_str, '-fill', 'red', '-draw', draw_str, 
                         '-fill', 'white', '-font', 'Arial-Bold', '-pointsize', '14', '-annotate', label_position, label_text, png_filename])
        print(f"Image processed. Final image at: {os.path.abspath(png_filename)}")

        return True
    except Exception as e:
        print(f"Error processing the image: {e}")
        return False


def update_image_label(image_label):
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

    # Schedule the next update, ensuring to pass image_label again
    image_label.after(300000, lambda: update_image_label(image_label))  # Update every 5 minutes


