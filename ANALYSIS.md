# NMSkies Codebase Analysis Report

## Executive Summary

This document provides a comprehensive analysis of every file in the NMSkies telescope automation codebase. The system was developed for automated satellite tracking at New Mexico Skies Observatory in Cloudcroft, NM, and is being prepared for sharing with ASTRIANet (UT Austin) for deployment on their telescope network.

## Installation Location (Windows 7 Machine)

**Target Path:** `C:\Program Files (x86)\PlaneWave Instruments\PlaneWave Interface 4\Scripts`

This is the default PlaneWave PWI4 Scripts folder where the automation code should reside.

---

## FILE-BY-FILE ANALYSIS

### CORE PRODUCTION FILES (Active Workflow)

#### 1. `pwi4_client.py` (774 lines) - ⭐ CRITICAL
**Status:** PRODUCTION - DO NOT MODIFY (PlaneWave Reference Implementation)
**Purpose:** HTTP API client library for communicating with PlaneWave PWI4 software
**Key Features:**
- Connects to PWI4 at `localhost:8220`
- Mount control: connect, enable, find_home, goto_ra_dec, follow_tle, tracking, park
- Focuser and rotator control
- Pointing model management
- Status parsing into structured Python objects
**Dependencies:** Python stdlib only (urllib)
**Imports From:** Nothing (standalone library)
**Used By:** automated2.py, pwi4_tle_observer.py, asteroid.py, all GUIs

#### 2. `api_interaction.py` (361 lines) - ⭐ CRITICAL
**Status:** PRODUCTION
**Purpose:** Fetches TLE (Two-Line Element) data from N2YO API and generates observation schedules
**Key Features:**
- Reads NORAD IDs from `noradid.txt`
- Queries N2YO API for visual satellite passes
- Calculates observation windows based on satellite visibility
- Generates `tleplan.txt` with scheduled observations
- TLE caching system (1-hour expiration)
- Interactive (GUI) and non-interactive (CLI) modes
- Supports `--non-interactive --days N --observation-window M` flags
**Dependencies:** requests, loguru, pytz, tkinter
**API Key:** N2YO API (needs user's own key)
**Observatory Coords:** 32.903°N, 105.5295°W, 2225m (Cloudcroft, NM)

#### 3. `pwi4_tle_observer.py` (212 lines) - ⭐ CRITICAL
**Status:** PRODUCTION
**Purpose:** Executes satellite tracking observations and captures images
**Key Features:**
- Parses `tleplan.txt` for observation schedule
- Commands mount to follow TLE via `pwi4.mount_follow_tle()`
- Controls camera via MaxIm DL (win32com)
- Camera cooler management (on at start, warm to 20°C at shutdown)
- Saves FITS files to `D:\SatelliteData\{timestamp}_{satname}\`
- Filename format: `{seq}_Azm_{az}_Alt_{alt}_Axis0Dist_{dist0}_Axis1Dist_{dist1}.fits`
- Default exposure: 0.1 seconds
**Dependencies:** pwi4_client, win32com.client (MaxIm DL)
**Output Path:** `D:\SatelliteData\` (configurable)

#### 4. `automated2.py` (328 lines) - ⭐ CRITICAL
**Status:** PRODUCTION
**Purpose:** Main automation controller - orchestrates entire observation sequence
**Key Features:**
- Startup sequence: Initialize PWI4 → Connect mount → Enable motors → Find home
- Dome operations via ASCOM Digital DomeWorks (TIDigitalDomeWorks.DomeControl)
- Opens dome shutter, enables dome slaving
- System checks: Verifies PWI4 and DDW operational (10 attempts, 5 minutes)
- Reads `tleplan.txt` and calls `run_observer()` from pwi4_tle_observer
- Shutdown sequence: Disables mount, closes dome
- Emergency shutdown if observatory not open for 5 hours
- Supports shutdown-only mode: `python automated2.py shutdown`
**Dependencies:** pwi4_client, pwi4_tle_observer, win32com.client
**Log File:** `telescope_automation_log.txt`

#### 5. `cache_manager.py` (51 lines)
**Status:** PRODUCTION (utility)
**Purpose:** Simple JSON-based caching with expiration
**Key Features:**
- File-based cache (`cache.json`)
- Configurable expiration time (default 3600 seconds)
- DateTime serialization/deserialization
**Used By:** api_interaction.py

---

### PLANEWAVE ORIGINAL/REFERENCE FILES

#### 6. `pwi4_client_demo.py` (46 lines)
**Status:** REFERENCE - PlaneWave Sample Code
**Purpose:** Demonstrates basic pwi4_client usage
**Notes:** Shows mount connection, status queries, slewing to coordinates

#### 7. `pwi4_startup.py` (56 lines)
**Status:** REFERENCE - PlaneWave Sample Code
**Purpose:** Demonstrates mount startup sequence
**Notes:** Connect → Enable motors → Find home pattern

#### 8. `pwi4_build_model.py` (142 lines)
**Status:** REFERENCE - PlaneWave Sample Code
**Purpose:** Demonstrates building a pointing model
**Notes:** Slews to grid of alt-az points, takes images, plate solves, adds to model
**Requires:** platesolve.py and PlateSolve3 with Kepler catalog

#### 9. `platesolve.py` (93 lines)
**Status:** REFERENCE - Utility for pointing model
**Purpose:** Wrapper for PlateSolve3 command-line tool (ps3cli.exe)
**Notes:** Used by pwi4_build_model.py for astrometric solving
**Requires:** PlateSolve3 installed at `~/ps3cli/ps3cli.exe`

---

### GUI APPLICATIONS (Multiple Versions - NEEDS CONSOLIDATION)

#### 10. `run_it_up2.py` (470 lines) - ⭐ CURRENT MAIN GUI
**Status:** PRODUCTION - Latest Tkinter GUI
**Purpose:** Windows desktop application for telescope control
**Key Features:**
- User login with personalized greeting
- Run TLE Updater button
- Run Observation(s) button
- Start Automated Cycle (green button)
- Start/Stop Infinite Observations
- GOES-16 weather satellite imagery display (auto-updates every 5 minutes)
- Observatory status checking via nmskies.com
- Skip TLE Updater checkbox
- Progress bars (alive_progress)
- Colorized logging (colorama, loguru)
**Dependencies:** tkinter, PIL, requests, loguru, alive_progress, colorama, pytz

#### 11. `dashb/dashapp.py` (388 lines)
**Status:** ALTERNATIVE - Plotly Dash Web Dashboard
**Purpose:** Web-based dashboard at http://localhost:8050
**Key Features:**
- Observatory status monitoring
- Sun times display (sunrise-sunset.org API)
- Control buttons: Run TLE Updater, Run Observation, Start Automated Cycle
- Automated scheduling (5 min after sunset, 8 min before sunrise)
- GOES-16 satellite imagery
**Dependencies:** dash, dash-bootstrap-components, plotly, flask, requests

#### 12. `dashb/run_it_up.py` (226 lines)
**Status:** ⚠️ DEPRECATED - Older GUI version
**Purpose:** Earlier iteration of Tkinter GUI
**Notes:** Has circular import with gui_setup.py - BROKEN
**Recommendation:** ARCHIVE

#### 13. `dashb/run_it_up1.py` (394 lines)
**Status:** ⚠️ DEPRECATED - Python 2.7 compatible version
**Purpose:** Older GUI with .format() instead of f-strings
**Notes:** Attempted Python 2.7 compatibility
**Recommendation:** ARCHIVE

#### 14. `dashb/gui_setup.py` (217 lines)
**Status:** ⚠️ DEPRECATED - Circular import issues
**Purpose:** Attempted modular GUI setup
**Notes:** Imports from run_it_up2.py which doesn't export those functions
**Recommendation:** ARCHIVE

#### 15. `askfornorad.py` (54 lines)
**Status:** PRODUCTION (utility dialog)
**Purpose:** Tkinter dialog for entering NORAD IDs, days, observation window
**Used By:** api_interaction.py in interactive mode

---

### UTILITY MODULES

#### 16. `dashb/misc.py` (85 lines)
**Status:** UTILITY
**Purpose:** Helper functions extracted from GUIs
**Functions:**
- `speak_message()` - Windows TTS via PowerShell
- `log_user_access()` - Logs user logins to access_log.txt
- `check_observatory_status()` - Scrapes nmskies.com/weather.php
- `update_sun_times()` - Gets sunrise/sunset from API
- `get_part_of_day()` - Returns "Good morning/afternoon/evening"

#### 17. `dashb/imagefunctions.py` (47 lines)
**Status:** UTILITY
**Purpose:** Downloads and processes GOES-16 weather satellite images
**Notes:** Uses ImageMagick via subprocess (alternative to PIL version in other files)

#### 18. `dashb/list_of_sats.py` (57 lines)
**Status:** ⚠️ STANDALONE TEST SCRIPT
**Purpose:** Simple satellite pass finder
**Notes:** Hardcoded Albuquerque coordinates (not Cloudcroft)
**API Key:** Exposed in file (same key)
**Recommendation:** ARCHIVE

#### 19. `oneminuteman.py` (52 lines)
**Status:** UTILITY
**Purpose:** Modifies tleplan.txt observation windows to fixed 4-minute duration centered on midpoint
**Notes:** Useful for normalizing observation windows

---

### RUNNERS/SCHEDULERS

#### 20. `infinite.py` (178 lines)
**Status:** PRODUCTION - Headless Runner
**Purpose:** Runs observation cycles indefinitely (daemon mode)
**Key Features:**
- Checks if tleplan.txt is current, updates if needed
- Fetches sunset time, waits until 10 min after sunset
- Runs automated2.py
- Failure handling with retry logic (max 3 failures)
- Waits until noon next day for next cycle
**Use Case:** Unattended nightly observations

#### 21. `dashboard.py` (119 lines)
**Status:** ALTERNATIVE - Flask Remote Control
**Purpose:** Simple Flask web server for remote control
**Features:**
- Start/stop script buttons
- View logs
- HTTP Basic Auth (admin/password123 - CHANGE THIS!)
- Uses Waitress WSGI server
**Endpoint:** http://192.168.99.1:5000

#### 22. `dashb/server.py` (50 lines)
**Status:** ⚠️ BROKEN - Import errors
**Purpose:** Flask + SocketIO server for real-time updates
**Notes:** Imports from run_it_up2.py incorrectly
**Recommendation:** ARCHIVE

#### 23. `run_scripts.bat` (14 lines)
**Status:** PRODUCTION - Windows Batch File
**Purpose:** Simple batch script to run api_interaction.py then automated2.py
**Notes:** Hardcoded Python path - may need adjustment

---

### EXPERIMENTAL/INCOMPLETE

#### 24. `dashb/asteroid.py` (173 lines)
**Status:** ⚠️ EXPERIMENTAL/INCOMPLETE
**Purpose:** Asteroid tracking automation
**Notes:** 
- Reads asteroid_observations.txt for RA/DEC coordinates
- Intended for asteroid observations (not satellites)
- Missing EXPOSURE_LENGTH_SEC definition
- Missing Dispatch import
**Recommendation:** ARCHIVE - needs significant work

#### 25. `dashb/upload_to_dropbox.py` (38 lines)
**Status:** ⚠️ INCOMPLETE
**Purpose:** Upload observation images to Dropbox
**Notes:**
- Missing `glob` import
- Missing `upload_folder_to_dropbox` function
- Access token was exposed (now redacted)
**Recommendation:** ARCHIVE - incomplete

---

### DATA/CONFIGURATION FILES

#### 26. `noradid.txt` (1 line, ~1000 IDs)
**Status:** DATA FILE
**Content:** Comma-separated NORAD catalog IDs (Starlink satellites 46027-48576)

#### 27. `noradid.sample.txt` (13 lines)
**Status:** SAMPLE/TEMPLATE
**Content:** Example NORAD IDs with documentation

#### 28. `tleplan.txt` (225 lines)
**Status:** GENERATED DATA
**Format:** Observation schedule with BEGINLOCAL, ENDLOCAL, NAME, TLE lines

#### 29. `tleplan.sample.txt` (19 lines)
**Status:** SAMPLE/TEMPLATE
**Content:** Example tleplan format with documentation

#### 30. `config.sample.py` (24 lines)
**Status:** CONFIGURATION TEMPLATE
**Content:** API keys, coordinates, paths, camera settings

#### 31. `cache.json` (large)
**Status:** RUNTIME DATA
**Content:** Cached TLE data from N2YO API

#### 32. `asteroid_observations.txt` (17 lines)
**Status:** DATA FILE
**Content:** Asteroid observation schedule (RA/DEC coordinates)

---

### LOG FILES (Runtime Generated)

- `telescope_automation_log.txt` - Main automation log
- `api_interaction_log.txt` - TLE fetching log
- `access_log.txt` - GUI user login log
- `guioperations.log` - GUI operations log
- `backup_log.txt` - Backup operations log

---

### WEB TEMPLATES

#### 33. `templates/index.html` (73 lines)
**Status:** PRODUCTION
**Purpose:** Web interface for Flask/SocketIO server
**Features:** Buttons for all operations, real-time output display

---

### IMAGE/ASSET FILES

- `resized_privateer.png` - Logo/branding image
- `weather.jpg`, `weather.png`, `weather.gif` - GOES satellite imagery (runtime)
- `image.fits` - Sample FITS file

---

### COMPILED FILES (Should be gitignored)

- `pwi4_client.pyc` - Compiled Python
- `platesolve.pyc` - Compiled Python
- `dashb/__pycache__/` - Python cache

---

## DEPENDENCY ANALYSIS

### External Dependencies
- **requests** - HTTP client for API calls
- **loguru** - Advanced logging
- **pytz** - Timezone handling
- **pywin32** - Windows COM automation (MaxIm DL, DDW)
- **dash** - Plotly Dash web framework
- **dash-bootstrap-components** - Bootstrap styling for Dash
- **plotly** - Plotting library
- **flask** - Web framework
- **flask-socketio** - WebSocket support
- **flask-httpauth** - HTTP authentication
- **PIL/Pillow** - Image processing
- **alive_progress** - Progress bars
- **colorama** - Terminal colors
- **waitress** - Production WSGI server

### Windows-Specific Requirements
- **PlaneWave PWI4** running on localhost:8220
- **MaxIm DL** with CCD camera connected
- **Digital DomeWorks (DDW)** for dome control
- **ASCOM Platform** for hardware abstraction

---

## RECOMMENDATIONS

### Files to ARCHIVE (Deprecated/Broken):
1. `dashb/run_it_up.py` - Circular imports
2. `dashb/run_it_up1.py` - Old Python 2.7 version
3. `dashb/gui_setup.py` - Broken imports
4. `dashb/server.py` - Broken imports
5. `dashb/list_of_sats.py` - Standalone test script
6. `dashb/asteroid.py` - Incomplete
7. `dashb/upload_to_dropbox.py` - Incomplete

### Files to Keep in PlaneWave Reference:
1. `pwi4_client_demo.py`
2. `pwi4_startup.py`
3. `pwi4_build_model.py`
4. `platesolve.py`

### Core Production Files:
1. `pwi4_client.py`
2. `api_interaction.py`
3. `pwi4_tle_observer.py`
4. `automated2.py`
5. `cache_manager.py`
6. `run_it_up2.py` (rename to `gui_app.py`)
7. `dashb/dashapp.py` (rename to `web_dashboard.py`)
8. `askfornorad.py`
9. `infinite.py`
10. `dashboard.py`
11. `oneminuteman.py`
12. `dashb/misc.py`
13. `dashb/imagefunctions.py`

---

## WORKFLOW DOCUMENTATION

### Primary Workflow (Automated Nightly Observations):
```
1. infinite.py (daemon) 
   └── Checks tleplan.txt currency
       └── api_interaction.py (if needed)
           └── N2YO API → tleplan.txt
   └── Waits for sunset + 10 min
   └── automated2.py
       └── startup_pwi4() → Connect, Enable, Home
       └── control_ddw() → Open shutter, Slave dome
       └── pwi4_tle_observer.run_observer()
           └── For each observation in tleplan.txt:
               └── pwi4.mount_follow_tle()
               └── MaxIm DL exposure
               └── Save FITS to D:\SatelliteData\
       └── shutdown() → Disable mount, Close dome
```

### Manual Workflow (GUI):
```
1. run_it_up2.py (Tkinter GUI)
   └── "Run TLE Updater" → api_interaction.py
   └── "Run Observation(s)" → automated2.py
   └── "Start Automated Cycle" → Full sequence with scheduling
```

### Web Workflow (Dashboard):
```
1. dashb/dashapp.py (Plotly Dash at :8050)
   └── Same buttons as GUI, accessible via browser
```
