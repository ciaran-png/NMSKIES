# NMSkies Installation & Setup Guide

This guide walks you through setting up the NMSkies telescope automation system on a Windows machine connected to PlaneWave hardware.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Software Installation](#software-installation)
3. [Python Environment Setup](#python-environment-setup)
4. [Configuration](#configuration)
5. [Hardware Verification](#hardware-verification)
6. [First Run](#first-run)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Hardware
- [ ] PlaneWave telescope mount (L-series, CDK, or compatible)
- [ ] Digital DomeWorks compatible dome system
- [ ] CCD camera supported by MaxIm DL
- [ ] Windows PC (Windows 7, 10, or 11)

### Required Software
- [ ] PlaneWave Interface 4 (PWI4)
- [ ] MaxIm DL (licensed)
- [ ] Digital DomeWorks
- [ ] ASCOM Platform 6.x
- [ ] Python 3.8 or higher

### Required Accounts
- [ ] N2YO API key (free at https://www.n2yo.com/api/)

---

## Software Installation

### Step 1: Install ASCOM Platform
1. Download from: https://ascom-standards.org/Downloads/Index.htm
2. Run installer as Administrator
3. Restart computer after installation

### Step 2: Install PlaneWave Interface 4
1. Download from: https://planewave.com/software/
2. Install to default location: `C:\Program Files (x86)\PlaneWave Instruments\PlaneWave Interface 4`
3. Launch PWI4 and verify it connects to your mount

### Step 3: Install MaxIm DL
1. Install MaxIm DL with your license
2. Connect your camera and verify it works in MaxIm
3. Note: Camera must be accessible via ASCOM

### Step 4: Install Digital DomeWorks
1. Install DDW software for your dome
2. Verify dome control works manually
3. Note the ASCOM driver name (typically `TIDigitalDomeWorks.DomeControl`)

### Step 5: Install Python
1. Download Python 3.8+ from: https://www.python.org/downloads/
2. **Important:** Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```

---

## Python Environment Setup

### Step 1: Navigate to Scripts Folder
```cmd
cd "C:\Program Files (x86)\PlaneWave Instruments\PlaneWave Interface 4\Scripts"
```

Or if you cloned from GitHub:
```cmd
cd C:\path\to\NMSKIES
```

### Step 2: Create Virtual Environment
```cmd
python -m venv venv
```

### Step 3: Activate Virtual Environment
```cmd
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

### Step 4: Install Dependencies
```cmd
pip install -r requirements.txt
```

### Step 5: Install PyWin32 Post-Install Script
```cmd
python venv\Scripts\pywin32_postinstall.py -install
```

This is required for ASCOM/COM automation to work properly.

---

## Configuration

### Step 1: Create Configuration File
```cmd
copy config.sample.py config.py
```

### Step 2: Edit config.py

Open `config.py` in a text editor and modify:

```python
# =============================================================================
# API CONFIGURATION
# =============================================================================
# Get your free API key from https://www.n2yo.com/api/
N2YO_API_KEY = "YOUR_N2YO_API_KEY_HERE"

# =============================================================================
# OBSERVATORY LOCATION
# =============================================================================
# New Mexico Skies default coordinates
# Change these to YOUR observatory location
OBSERVER_LAT = 32.903       # Latitude in decimal degrees (+ = North)
OBSERVER_LNG = -105.5295    # Longitude in decimal degrees (- = West)
OBSERVER_ALT = 2225         # Altitude in meters above sea level

# =============================================================================
# TIMEZONE
# =============================================================================
# Use pytz timezone names: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = "America/Denver"  # Mountain Time

# =============================================================================
# OUTPUT PATHS
# =============================================================================
# Where to save captured FITS images
OUTPUT_PATH = "D:\\SatelliteData"

# =============================================================================
# PWI4 CONNECTION
# =============================================================================
PWI4_HOST = "localhost"
PWI4_PORT = 8220

# =============================================================================
# CAMERA SETTINGS
# =============================================================================
EXPOSURE_LENGTH_SEC = 0.1   # Exposure time in seconds for satellite tracking
```

### Step 3: Create NORAD ID List

Create `noradid.txt` with satellite NORAD catalog IDs:

```cmd
copy data\noradid.sample.txt noradid.txt
```

Edit to include your target satellites (comma-separated):
```
25544,20580,33591
```

Common satellites:
- **25544** - ISS (ZARYA)
- **20580** - Hubble Space Telescope
- **33591** - NOAA 19
- **46xxx-48xxx** - Starlink satellites

Find NORAD IDs at: https://www.n2yo.com/ or https://celestrak.org/

---

## Hardware Verification

### Step 1: Verify PWI4 Connection
1. Launch PlaneWave Interface 4
2. Connect to your mount
3. Verify mount status shows "Connected"
4. Test the HTTP API:
   - Open browser to: `http://localhost:8220/status`
   - You should see mount status data

### Step 2: Verify Dome Connection
1. Launch Digital DomeWorks
2. Verify dome shows "Online"
3. Test opening/closing shutter manually

### Step 3: Verify Camera Connection
1. Launch MaxIm DL
2. Connect camera
3. Take a test exposure

### Step 4: Test Python Hardware Access
```cmd
python -c "from src.pwi4_client import PWI4; p = PWI4(); print(p.status())"
```

If PWI4 is running, this should print mount status.

---

## First Run

### Option A: Full Automated Test
```cmd
# Activate virtual environment
venv\Scripts\activate

# Generate observation schedule for tonight
python src/api_interaction.py --non-interactive --days 1 --observation-window 2

# View the generated schedule
type tleplan.txt

# Run observations (will control telescope, dome, and camera!)
python src/automated2.py
```

### Option B: GUI Test
```cmd
# Activate virtual environment
venv\Scripts\activate

# Launch desktop application
python gui/tkinter_app.py
```

### Option C: Web Dashboard Test
```cmd
# Activate virtual environment
venv\Scripts\activate

# Launch web dashboard
python gui/web_dashboard.py

# Open browser to http://localhost:8050
```

---

## Troubleshooting

### "PWI4 not responding"
1. Verify PWI4 is running
2. Check port 8220: `http://localhost:8220/status`
3. Check firewall isn't blocking localhost connections

### "DDW is not running"
1. Launch Digital DomeWorks
2. Verify it shows "Online" status
3. Try reconnecting dome in DDW

### "Cannot find MaxIm.CCDCamera"
1. Verify MaxIm DL is installed
2. Run pywin32 post-install script:
   ```cmd
   python venv\Scripts\pywin32_postinstall.py -install
   ```
3. Restart computer

### "N2YO API error"
1. Verify API key in config.py
2. Check API rate limits (1000/hour free tier)
3. Test API directly: `https://api.n2yo.com/rest/v1/satellite/tle/25544?apiKey=YOUR_KEY`

### "No passes found"
1. Verify observatory coordinates in config.py
2. Try different NORAD IDs
3. Extend days parameter (--days 3)

### Import Errors
1. Ensure virtual environment is activated
2. Reinstall requirements:
   ```cmd
   pip install -r requirements.txt
   ```

### Permission Errors
1. Run command prompt as Administrator
2. Check file permissions in output directory

---

## Directory Structure After Setup

```
Scripts/
├── venv/                    # Virtual environment (created)
├── config.py                # Your configuration (created)
├── noradid.txt              # Your satellite list (created)
├── tleplan.txt              # Generated schedule (runtime)
├── cache.json               # TLE cache (runtime)
│
├── src/                     # Core modules
├── gui/                     # User interfaces
├── utils/                   # Utilities
├── runners/                 # Automation scripts
├── planewave_reference/     # PlaneWave samples
├── templates/               # Web templates
├── data/                    # Sample files
└── archive/                 # Deprecated code
```

---

## Running as a Service

To run observations automatically every night:

### Option 1: Windows Task Scheduler
1. Open Task Scheduler
2. Create new task
3. Trigger: Daily at sunset time
4. Action: Run `runners/run_scripts.bat`

### Option 2: Continuous Daemon
```cmd
# Run in background (will observe every night automatically)
python runners/infinite.py
```

Consider using `pythonw.exe` instead of `python.exe` to run without console window.

---

## Support

For issues specific to:
- **PlaneWave hardware:** Contact PlaneWave support
- **This automation code:** Open issue on GitHub
- **N2YO API:** Contact N2YO support
- **MaxIm DL:** Contact Diffraction Limited
