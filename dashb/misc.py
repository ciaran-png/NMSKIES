import subprocess
from datetime import datetime, timedelta, timezone
import requests
import pytz
import re


def speak_message(message):
    subprocess.call(f'powershell -Command "Add-Type –AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{message}\');"')

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

# Function to determine the part of the day
def get_part_of_day(hour):
    return (
        "Good morning" if 5 <= hour <= 11
        else "Good afternoon" if 12 <= hour <= 17
        else "Good evening"
    )