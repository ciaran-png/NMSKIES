import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash.exceptions import PreventUpdate
import requests
import re
from datetime import datetime, timedelta, timezone
import time
import threading
import subprocess
import pytz
import subprocess
from loguru import logger

# Global variables (you might want to move these to a config file)
NMS_WEATHER_URL = "https://nmskies.com/weather.php"
COORDS = (32.957313, -105.742485) # Cloudcroft, New Mexico
TIMEZONE = pytz.timezone('America/Denver')
LOG_FILE = "access_log.txt"

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Configure Loguru
logger.add(LOG_FILE, format="{time} - {level} - {message}", level="INFO")


# Helper Functions

def check_observatory_status():
    """Fetches the observatory status from the NMS website."""
    try:
        response = requests.get(NMS_WEATHER_URL)
        html_content = response.text

        match = re.search(r'images/(daylight\.jpg|open\.jpg|closed\.jpg)\?', html_content)
        if match:
            img_file = match.group(1)
            if "daylight.jpg" in img_file:
                return "Daylight (Closed)"
            elif "open.jpg" in img_file:
                return "Open"
            elif "closed.jpg" in img_file:
                return "Closed"
            else:
                return "Unknown"
        else:
            return "Status image not found"

    except Exception as e:
        logger.error(f"Failed to check observatory status: {e}")
        return "Error"

def update_sun_times():
    """Fetches sunset today and sunrise tomorrow times."""
    today = datetime.now(TIMEZONE).date()
    tomorrow = today + timedelta(days=1)

    try:
        sunset_response = requests.get(f"https://api.sunrise-sunset.org/json?lat={COORDS[0]}&lng={COORDS[1]}&date={today}&formatted=0")
        sunrise_response = requests.get(f"https://api.sunrise-sunset.org/json?lat={COORDS[0]}&lng={COORDS[1]}&date={tomorrow}&formatted=0")

        if sunset_response.status_code == 200 and sunrise_response.status_code == 200:
            sunset_data = sunset_response.json()
            sunrise_data = sunrise_response.json()
            if 'results' in sunset_data and 'sunset' in sunset_data['results'] and 'results' in sunrise_data and 'sunrise' in sunrise_data['results']:
                sunset_utc = datetime.fromisoformat(sunset_data['results']['sunset'])
                sunrise_utc = datetime.fromisoformat(sunrise_data['results']['sunrise'])

                sunset_local = sunset_utc.replace(tzinfo=timezone.utc).astimezone(TIMEZONE)
                sunrise_local = sunrise_utc.replace(tzinfo=timezone.utc).astimezone(TIMEZONE)

                return sunset_local, sunrise_local
            else:
                logger.error("Malformed API response: Missing 'results' or 'sunset/sunrise' data.")
                return None, None
        else:
            logger.error(f"Failed to retrieve data from API. Status codes: {sunset_response.status_code}, {sunrise_response.status_code}")
            return None, None

    except Exception as e:
        logger.error(f"Error in update_sun_times: {e}")
        return None, None

def run_script(script_name, args=None, shutdown=False):
    """Runs a Python script in a separate process."""
    try:
        script_args = ['python', script_name] + (args if args is not None else [])
        if shutdown:
            script_args.append('shutdown')
        process = subprocess.Popen(script_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logger.error(f"Error running script '{script_name}': {stderr.decode()}")
        else:
            logger.info(f"Script '{script_name}' executed successfully: {stdout.decode()}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while running '{script_name}': {str(e)}")

def schedule_task(task_time, task_function):
    """Schedules a function to run at a specific time."""
    now = datetime.now(TIMEZONE)
    wait_time = (task_time - now).total_seconds()
    if wait_time > 0:
        threading.Timer(wait_time, task_function).start()
        logger.info(f"Task '{task_function.__name__}' scheduled for {task_time}")


# Dash Components

status_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Observatory Status", className="card-title"),
                html.P(id='observatory-status', children="Fetching status...", className="card-text"),
            ]
        ),
    ],
    color="dark",
    inverse=True,
    outline=False,
    style={"width": "18rem"},
)

sun_times_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Sun Times", className="card-title"),
                html.P(id='sunset-time', children="Fetching...", className="card-text"),
                html.P(id='sunrise-time', children="Fetching...", className="card-text"),
            ]
        ),
    ],
    color="dark",
    inverse=True,
    outline=False,
    style={"width": "18rem"},
)

tle_updater_card = dbc.Card(
    [
        dbc.CardHeader("TLE Updater"),
        dbc.CardBody(
            [
                dbc.Button("Run TLE Updater", id='run-tle-updater', color="primary", className="mr-1"),
                html.P(id='tle-updater-status', children="Idle", className="card-text"),
            ]
        ),
    ],
    color="dark",
    inverse=True,
    outline=False,
)

observation_card = dbc.Card(
    [
        dbc.CardHeader("Observation"),
        dbc.CardBody(
            [
                dbc.Button("Run Observation", id='run-observation', color="primary", className="mr-1"),
                html.P(id='observation-status', children="Idle", className="card-text"),
            ]
        ),
    ],
    color="dark",
    inverse=True,
    outline=False,
)

automated_cycle_card = dbc.Card(
    [
        dbc.CardHeader("Automated Observation Cycle"),
        dbc.CardBody(
            [
                dbc.Button("Start Automated Cycle", id='start-automated-cycle', color="success", className="mr-1"),
                html.P(id='automated-cycle-status', children="Idle", className="card-text"),
                dcc.Checklist(
                    id='skip-tle-updater',
                    options=[{'label': 'Skip TLE Updater', 'value': 'skip'}],
                    value=[],
                    labelStyle={'display': 'inline-block'}
                ),
            ]
        ),
    ],
    color="dark",
    inverse=True,
    outline=False,
)

schedule_automation_card = dbc.Card(
    [
        dbc.CardHeader("Schedule Automated Observation Cycle"),
        dbc.CardBody(
            [
                dcc.Input(id="num-days", type="number", placeholder="Number of days", min=1, style={'width': '100px', 'marginRight': '10px'}),
                dcc.Input(id="start-time", type="text", placeholder="HH:MM (24-hour)", style={'width': '100px', 'marginRight': '10px'}),
                dbc.Button("Schedule", id='schedule-cycle', color="primary", className="mr-1"),
                html.P(id='schedule-automation-status', children="Idle", className="card-text"),
            ]
        ),
    ],
    color="dark",
    inverse=True,
    outline=False,
)

image_card = dbc.Card(
    [
        dbc.CardHeader("Live Satellite Imagery"),
        dbc.CardBody(
            [
                html.Img(id='satellite-image', src="", style={'width': '100%'}),
            ]
        ),
    ],
    color="dark",
    inverse=True,
    outline=False,
)

# Layout

app.layout = dbc.Container(
    [
        html.H1("New Mexico Skies Command Center", className="text-center mt-4 mb-4"),
        dbc.Row(
            [
                dbc.Col(status_card, width=4, align="center"),
                dbc.Col(sun_times_card, width=4, align="center"),
            ],
            justify="center",  # Center the columns horizontally
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(tle_updater_card, width=4, align="center"),
                dbc.Col(observation_card, width=4, align="center"),
            ],
            justify="center",  # Center the columns horizontally
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(automated_cycle_card, width=6, align="center"),
            ],
            justify="center",  # Center the columns horizontally
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(schedule_automation_card, width=6, align="center"),
            ],
            justify="center",  # Center the columns horizontally
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(image_card, width=12, align="center"),
            ],
            justify="center",  # Center the columns horizontally
            className="mb-4",
        ),
        dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0), # Update every minute
    ],
    fluid=True,
)

# Callbacks
@app.callback(Output('observatory-status', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_observatory_status(n):
    status = check_observatory_status()
    return status

@app.callback([Output('sunset-time', 'children'),
              Output('sunrise-time', 'children')],
              [Input('interval-component', 'n_intervals')])
def update_sun_times_display(n):
    sunset, sunrise = update_sun_times()
    if sunset and sunrise:
        return f"Sunset: {sunset.strftime('%H:%M')}", f"Sunrise: {sunrise.strftime('%H:%M')}"
    else:
        return "Error fetching sunset time", "Error fetching sunrise time"

@app.callback(Output('tle-updater-status', 'children'),
              [Input('run-tle-updater', 'n_clicks')],
              prevent_initial_call=True)
def run_tle_updater(n_clicks):
    if n_clicks:
        run_script('api_interaction.py', ['--non-interactive'])
        return "TLE Updater: Running..."
    raise PreventUpdate

@app.callback(Output('observation-status', 'children'),
              [Input('run-observation', 'n_clicks')])
def run_observation_script(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    run_script('automated2.py')
    return "Observation: Running..."

@app.callback(Output('automated-cycle-status', 'children'),
              [Input('start-automated-cycle', 'n_clicks'),
               Input('skip-tle-updater', 'value')])
def run_automated_cycle(n_clicks, skip_tle):
    if n_clicks is None:
        raise PreventUpdate

    if 'skip' not in skip_tle:
        run_script('api_interaction.py', ['--non-interactive', '--days', '1', '--observation-window', '2', '--force-update'])

    sunset, sunrise = update_sun_times()

    if sunset and sunrise:
        start_time = sunset + timedelta(minutes=5)
        shutdown_time = sunrise - timedelta(minutes=8)

        def start_observation():
            """Starts the observation after checking the observatory status."""
            start_check_time = datetime.now()  # Record the time when checking starts
            while True:
                status = check_observatory_status()
                if status == "Open":
                    logger.info("Observatory is open. Starting the observation script.")
                    run_script('automated2.py')  # Start the observation
                    break
                elif (datetime.now() - start_check_time).total_seconds() > 5 * 3600:
                    logger.warning("Observatory not open for 5 hours. Initiating shutdown.")
                    run_script('automated2.py', shutdown=True)  # Initiate shutdown
                    exit()  # Quit the script
                else:
                    logger.info("Observatory is not open. Checking again in one minute.")
                    time.sleep(60)

        schedule_task(start_time, start_observation)
        schedule_task(shutdown_time, lambda: run_script('automated2.py', shutdown=True))

        return f"Cycle scheduled. Start: {start_time.strftime('%H:%M')}, Shutdown: {shutdown_time.strftime('%H:%M')}"
    else:
        return "Error: Could not fetch sun times."


@app.callback(Output('schedule-automation-status', 'children'),
              [Input('schedule-cycle', 'n_clicks')],
              [State('num-days', 'value'),
               State('start-time', 'value')])
def schedule_observation_cycle(n_clicks, num_days, start_time_str):
    if n_clicks is None or not num_days or not start_time_str:
        raise PreventUpdate

    try:
        daily_start_time = datetime.strptime(start_time_str, "%H:%M").time()
    except ValueError:
        return "Error: Invalid time format."

    current_time = datetime.now(TIMEZONE)

    for day in range(num_days):
        cycle_datetime = current_time.replace(hour=daily_start_time.hour, minute=daily_start_time.minute, second=0, microsecond=0) + timedelta(days=day)

        if cycle_datetime < current_time:
            cycle_datetime += timedelta(days=1)

        schedule_task(cycle_datetime, automated_observation_cycle)

        logger.info(f"Automated observation cycle scheduled for {cycle_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    return f"Scheduled for {num_days} days starting at {start_time_str}"

def automated_observation_cycle():
    # Implementation of what should happen in an automated observation cycle
    pass

# In a real application, you would dynamically update this image URL
@app.callback(Output('satellite-image', 'src'),
              [Input('interval-component', 'n_intervals')])
def update_satellite_image(n):
    # Append a unique query parameter to bypass caching issues and fetch the latest gif
    return "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/sr/GEOCOLOR/GOES16-SR-GEOCOLOR-600x600.gif?time=" + str(time.time())

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)