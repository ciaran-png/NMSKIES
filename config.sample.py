"""
NMSkies Configuration Template

Copy this file to config.py and fill in your values:
    copy config.sample.py config.py

IMPORTANT: config.py contains sensitive API keys and should NEVER be committed to git.
           It is already in .gitignore.
"""

# =============================================================================
# API CONFIGURATION
# =============================================================================
# N2YO API Key - Get your free key at https://www.n2yo.com/api/
# Free tier: 1000 requests/hour (sufficient for most use cases)
N2YO_API_KEY = "YOUR_N2YO_API_KEY_HERE"

# =============================================================================
# OBSERVATORY LOCATION
# =============================================================================
# Enter your observatory's geographic coordinates
# Use decimal degrees (not degrees/minutes/seconds)
# Latitude: Positive = North, Negative = South
# Longitude: Positive = East, Negative = West

# New Mexico Skies (Cloudcroft, NM) - Default values
OBSERVER_LAT = 32.903       # Latitude in decimal degrees
OBSERVER_LNG = -105.5295    # Longitude in decimal degrees  
OBSERVER_ALT = 2225         # Altitude in meters above sea level

# Example for Austin, TX (for ASTRIANet):
# OBSERVER_LAT = 30.2672
# OBSERVER_LNG = -97.7431
# OBSERVER_ALT = 149

# =============================================================================
# TIMEZONE
# =============================================================================
# Use pytz timezone names
# Reference: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = "America/Denver"  # Mountain Time (New Mexico)

# Other common timezones:
# "America/Chicago"      # Central Time
# "America/New_York"     # Eastern Time
# "America/Los_Angeles"  # Pacific Time
# "UTC"                  # Coordinated Universal Time

# =============================================================================
# OUTPUT PATHS
# =============================================================================
# Directory where FITS images will be saved
# Use double backslashes (\\) or raw strings (r"...") on Windows
OUTPUT_PATH = "D:\\SatelliteData"
# OUTPUT_PATH = r"D:\SatelliteData"  # Alternative syntax

# Subdirectory naming pattern (uses Python strftime format)
# Default creates: OUTPUT_PATH/{timestamp}_{satellite_name}/
OUTPUT_SUBDIR_FORMAT = "%Y%m%d_%H%M%S"

# =============================================================================
# PWI4 CONNECTION
# =============================================================================
# PlaneWave Interface 4 HTTP API settings
# Default values work for local installation
PWI4_HOST = "localhost"
PWI4_PORT = 8220

# Full URL constructed as: http://{PWI4_HOST}:{PWI4_PORT}/
# Test connection: http://localhost:8220/status

# =============================================================================
# CAMERA SETTINGS
# =============================================================================
# Exposure time in seconds for satellite tracking
# Shorter exposures (0.1s) prevent trailing for fast-moving satellites
EXPOSURE_LENGTH_SEC = 0.1

# Camera cooling target (degrees Celsius)
# Set to None to disable cooling management
CAMERA_COOLING_TARGET = -10

# Camera warmup target for shutdown (degrees Celsius)
CAMERA_WARMUP_TARGET = 20

# =============================================================================
# DOME SETTINGS
# =============================================================================
# ASCOM ProgID for Digital DomeWorks
# This is the COM object identifier
DDW_PROGID = "TIDigitalDomeWorks.DomeControl"

# Wait time after opening dome before starting observations (seconds)
DOME_SETTLE_TIME = 180  # 3 minutes

# =============================================================================
# OBSERVATION SETTINGS
# =============================================================================
# Minimum time gap between observations (seconds)
# Prevents scheduling conflicts
MIN_OBSERVATION_GAP = 60

# Default observation window (minutes)
# 'full' = entire visible pass
# Number = +/- minutes from pass midpoint
DEFAULT_OBSERVATION_WINDOW = 2

# Maximum days ahead to schedule (1-10)
MAX_SCHEDULE_DAYS = 10

# =============================================================================
# AUTOMATION SETTINGS
# =============================================================================
# Time after sunset to start observations (minutes)
POST_SUNSET_DELAY = 10

# Time before sunrise to stop observations (minutes)
PRE_SUNRISE_BUFFER = 8

# Maximum consecutive failures before shutdown
MAX_FAILURES = 3

# Retry wait time after failure (seconds)
RETRY_WAIT = 3600  # 1 hour

# =============================================================================
# LOGGING
# =============================================================================
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Log file paths
LOG_FILE_AUTOMATION = "telescope_automation_log.txt"
LOG_FILE_API = "api_interaction_log.txt"
LOG_FILE_GUI = "guioperations.log"

# =============================================================================
# WEB DASHBOARD (flask_dashboard.py)
# =============================================================================
# Host and port for Flask dashboard
# Use 0.0.0.0 to allow external connections
DASHBOARD_HOST = "192.168.99.1"
DASHBOARD_PORT = 5000

# HTTP Basic Auth credentials (CHANGE THESE!)
DASHBOARD_USERNAME = "admin"
DASHBOARD_PASSWORD = "password123"  # CHANGE THIS!

# =============================================================================
# PLOTLY DASH DASHBOARD (web_dashboard.py)
# =============================================================================
DASH_HOST = "localhost"
DASH_PORT = 8050
DASH_DEBUG = False

# =============================================================================
# EXTERNAL APIS
# =============================================================================
# Sunrise-Sunset API (no key required)
SUNRISE_SUNSET_API = "https://api.sunrise-sunset.org/json"

# GOES-16 Satellite Weather Imagery
GOES_IMAGE_URL = "https://cdn.star.nesdis.noaa.gov/GOES16/ABI/SECTOR/sr/GEOCOLOR/600x600.jpg"

# NM Skies Observatory Status Page
NMSKIES_WEATHER_URL = "https://nmskies.com/weather.php"
