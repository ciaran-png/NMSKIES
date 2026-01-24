# NMSkies System Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Details](#component-details)
3. [Data Flow](#data-flow)
4. [Execution Modes](#execution-modes)
5. [File Dependencies](#file-dependencies)
6. [Hardware Integration](#hardware-integration)
7. [Error Handling](#error-handling)

---

## System Overview

The NMSkies automation system consists of five main layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Tkinter GUI  │  │ Dash Web UI  │  │ Flask Remote Control     │  │
│  │ (Desktop)    │  │ (Browser)    │  │ (API)                    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                      ORCHESTRATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ automated2.py - Main Controller                              │  │
│  │ infinite.py - Daemon Scheduler                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                      BUSINESS LOGIC LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ TLE Fetching │  │ Observation  │  │ Schedule Management      │  │
│  │ (N2YO API)   │  │ Execution    │  │ (tleplan.txt)            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                      HARDWARE ABSTRACTION LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ pwi4_client  │  │ DDW (ASCOM)  │  │ MaxIm DL (COM)           │  │
│  │ (HTTP REST)  │  │ (COM)        │  │ (win32com)               │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                      PHYSICAL LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ PlaneWave    │  │ Observatory  │  │ CCD Camera               │  │
│  │ Mount        │  │ Dome         │  │                          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Core Modules (src/)

#### pwi4_client.py
**Role:** PlaneWave HTTP API Client Library
**Type:** Library (imported, not executed directly)
**API Endpoint:** `http://localhost:8220`

**Key Classes:**
- `PWI4` - Main client class with all mount/focuser/rotator methods
- `PWI4Status` - Structured response parser
- `PWI4HttpCommunicator` - Low-level HTTP communication

**Critical Methods:**
```python
pwi4.mount_connect()           # Connect to mount
pwi4.mount_enable(axis)        # Enable motor axis (0 or 1)
pwi4.mount_find_home()         # Home the mount
pwi4.mount_follow_tle(l1,l2,l3)# Track satellite by TLE
pwi4.mount_tracking_on()       # Enable sidereal tracking
pwi4.mount_stop()              # Emergency stop
pwi4.status()                  # Get current status
```

#### api_interaction.py
**Role:** TLE Data Acquisition & Schedule Generation
**Execution:** Interactive (GUI) or CLI with flags

**Input:**
- `noradid.txt` - List of NORAD satellite IDs
- User parameters (days, observation window)

**Output:**
- `tleplan.txt` - Observation schedule with TLE data
- `cache.json` - Cached TLE responses

**API Used:** N2YO REST API (`https://api.n2yo.com/rest/v1/satellite`)

**CLI Usage:**
```bash
# Interactive mode (shows GUI dialog)
python api_interaction.py

# Non-interactive mode
python api_interaction.py --non-interactive --days 1 --observation-window 2
```

**Key Functions:**
```python
fetch_tle_data(norad_id)       # Get TLE from N2YO
get_visual_passes(norad_id)    # Get pass predictions
filter_passes(passes)          # Remove overlapping observations
write_tleplan(observations)    # Generate tleplan.txt
```

#### pwi4_tle_observer.py
**Role:** Observation Execution Engine
**Execution:** Called by automated2.py

**Input:**
- `tleplan.txt` - Schedule of observations

**Output:**
- FITS images in `D:\SatelliteData\{timestamp}_{satname}\`

**Hardware Controlled:**
- PlaneWave Mount (via pwi4_client)
- MaxIm DL Camera (via win32com)

**Key Functions:**
```python
parse_tleplan()                # Read observation schedule
run_observer()                 # Main observation loop
wait_for_observation()         # Wait until start time
execute_observation(obs)       # Track satellite & capture
operate_camera(action, ...)    # Camera control
save_fits(data, metadata)      # Save image with headers
```

**FITS Filename Format:**
```
{seq:04d}_Azm_{azimuth:.1f}_Alt_{altitude:.1f}_Axis0Dist_{d0:.1f}_Axis1Dist_{d1:.1f}.fits
```

#### automated2.py
**Role:** Master Automation Controller
**Execution:** Standalone or with `shutdown` argument

**Sequence:**
1. Initialize PWI4 connection
2. System checks (PWI4 running, DDW online)
3. Startup sequence (connect → enable → home)
4. Dome operations (open shutter, enable slaving)
5. Wait for dome to stabilize (3 minutes)
6. Execute observations via pwi4_tle_observer
7. Shutdown sequence (disable mount, close dome)

**Shutdown-Only Mode:**
```bash
python automated2.py shutdown
```

**Key Functions:**
```python
startup_pwi4()                 # Initialize mount
control_ddw(action, azimuth)   # Dome control
system_check()                 # Verify all systems online
shutdown_system()              # Safe shutdown procedure
main()                         # Orchestration logic
```

#### cache_manager.py
**Role:** TLE Data Caching
**Type:** Utility library

**Features:**
- JSON-based file storage
- Configurable expiration (default: 1 hour)
- DateTime serialization support

**Usage:**
```python
cache = SimpleCache('cache.json', expiration_time=3600)
cache.set('tle_25544', tle_data)
data = cache.get('tle_25544')  # Returns None if expired
```

---

### GUI Applications (gui/)

#### tkinter_app.py (formerly run_it_up2.py)
**Role:** Windows Desktop Control Application
**Framework:** Tkinter + PIL

**Features:**
- User login with personalized greeting
- Button: Run TLE Updater → api_interaction.py
- Button: Run Observation(s) → automated2.py
- Button: Start Automated Cycle → Full workflow
- Button: Start/Stop Infinite Observations
- GOES-16 weather satellite imagery (auto-refresh)
- Observatory status indicator
- Progress bars for long operations

**Window Size:** 575x920 pixels

#### web_dashboard.py (formerly dashapp.py)
**Role:** Web-Based Control Dashboard
**Framework:** Plotly Dash + Bootstrap
**URL:** `http://localhost:8050`

**Features:**
- Same functionality as Tkinter GUI
- Browser-accessible
- Real-time status updates
- Sun times display

#### dialogs.py (formerly askfornorad.py)
**Role:** Input Dialog Components
**Type:** Utility module

**Dialogs:**
- NORAD ID entry (multi-line text)
- Days ahead selector (1-10)
- Observation window input

---

### Automation Runners (runners/)

#### infinite.py
**Role:** Continuous Observation Daemon
**Execution:** Long-running background process

**Logic:**
```
LOOP FOREVER:
  1. Check if tleplan.txt is current (today's date)
     - If not: Run api_interaction.py to update
  2. Fetch sunset time from sunrise-sunset.org API
  3. Wait until sunset + 10 minutes
  4. Run automated2.py
  5. If failed 3+ times: Shutdown and wait until noon
  6. Wait until noon next day
  REPEAT
```

**Failure Handling:**
- Retries on failure (max 3 attempts)
- 1-hour wait between retries
- Full shutdown after 3 failures
- Resumes next day at noon

#### flask_dashboard.py (formerly dashboard.py)
**Role:** Simple Remote Control Server
**Framework:** Flask + Waitress
**URL:** `http://192.168.99.1:5000`

**Endpoints:**
- `GET /` - Dashboard page
- `POST /start` - Start observation script
- `POST /stop` - Stop observation script
- `GET /logs` - View script logs

**Authentication:** HTTP Basic Auth (admin/password123)

#### run_scripts.bat
**Role:** Windows Batch Automation
**Usage:** Double-click or schedule via Task Scheduler

**Actions:**
1. Change to PWI4 Scripts directory
2. Run api_interaction.py
3. Run automated2.py

---

## Data Flow

### TLE Acquisition Flow
```
noradid.txt
    │
    ▼
┌─────────────────────┐
│ api_interaction.py  │
│ ┌─────────────────┐ │
│ │ Read NORAD IDs  │ │
│ └────────┬────────┘ │
│          ▼          │
│ ┌─────────────────┐ │
│ │ Check cache.json│ │
│ └────────┬────────┘ │
│          ▼          │
│ ┌─────────────────┐ │     ┌─────────────────┐
│ │ Query N2YO API  │◀─────▶│ api.n2yo.com    │
│ └────────┬────────┘ │     └─────────────────┘
│          ▼          │
│ ┌─────────────────┐ │
│ │ Filter passes   │ │
│ │ (remove overlap)│ │
│ └────────┬────────┘ │
│          ▼          │
│ ┌─────────────────┐ │
│ │ Write tleplan   │ │
│ └─────────────────┘ │
└─────────────────────┘
    │
    ▼
tleplan.txt
```

### Observation Execution Flow
```
tleplan.txt
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│ automated2.py                                           │
│ ┌─────────────────┐                                     │
│ │ system_check()  │ ──▶ Verify PWI4 & DDW running      │
│ └────────┬────────┘                                     │
│          ▼                                              │
│ ┌─────────────────┐     ┌──────────────────────────┐   │
│ │ startup_pwi4()  │────▶│ pwi4_client.py           │   │
│ │ - connect       │     │ - mount_connect()        │   │
│ │ - enable motors │     │ - mount_enable(0,1)      │   │
│ │ - find home     │     │ - mount_find_home()      │   │
│ └────────┬────────┘     └──────────────────────────┘   │
│          ▼                                              │
│ ┌─────────────────┐     ┌──────────────────────────┐   │
│ │ control_ddw()   │────▶│ Digital DomeWorks (ASCOM)│   │
│ │ - open shutter  │     │ - actOpenShutter()       │   │
│ │ - slave mode    │     │ - optSlaveMode = True    │   │
│ └────────┬────────┘     └──────────────────────────┘   │
│          ▼                                              │
│ ┌─────────────────┐                                     │
│ │ run_observer()  │ ──────────────────────────────┐    │
│ └─────────────────┘                               │    │
└───────────────────────────────────────────────────│────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────┐
│ pwi4_tle_observer.py                                    │
│                                                         │
│ FOR each observation in tleplan.txt:                    │
│   ┌─────────────────┐                                   │
│   │ Wait for start  │ ──▶ time.sleep() until BEGINLOCAL│
│   └────────┬────────┘                                   │
│            ▼                                            │
│   ┌─────────────────┐     ┌─────────────────────────┐  │
│   │ mount_follow_tle│────▶│ PWI4 HTTP API           │  │
│   │ (TLE line 1,2,3)│     │ /mount/follow_tle       │  │
│   └────────┬────────┘     └─────────────────────────┘  │
│            ▼                                            │
│   ┌─────────────────┐     ┌─────────────────────────┐  │
│   │ operate_camera  │────▶│ MaxIm DL (COM)          │  │
│   │ - expose        │     │ - cam.Expose(0.1, 1)    │  │
│   │ - wait ready    │     │ - cam.ImageReady        │  │
│   │ - save FITS     │     │ - cam.SaveImage(path)   │  │
│   └────────┬────────┘     └─────────────────────────┘  │
│            ▼                                            │
│   ┌─────────────────┐                                   │
│   │ Loop until      │                                   │
│   │ ENDLOCAL time   │                                   │
│   └─────────────────┘                                   │
│                                                         │
│ END FOR                                                 │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
        D:\SatelliteData\{timestamp}_{satname}\*.fits
```

---

## Execution Modes

### Mode 1: Manual Single Run
```bash
# Step 1: Generate observation schedule
python src/api_interaction.py --non-interactive --days 1

# Step 2: Execute observations
python src/automated2.py
```

### Mode 2: GUI Control
```bash
# Tkinter desktop app
python gui/tkinter_app.py

# Or web dashboard
python gui/web_dashboard.py
```

### Mode 3: Continuous Daemon
```bash
# Runs forever, handles nightly observations automatically
python runners/infinite.py
```

### Mode 4: Scheduled Task
Use Windows Task Scheduler to run `runners/run_scripts.bat` at sunset.

### Mode 5: Remote Control
```bash
# Start Flask server
python runners/flask_dashboard.py

# Access from browser: http://192.168.99.1:5000
```

---

## File Dependencies

```
pwi4_client.py (standalone library)
    ▲
    │
    ├── api_interaction.py
    │       └── cache_manager.py
    │
    ├── pwi4_tle_observer.py
    │       └── (MaxIm DL via win32com)
    │
    └── automated2.py
            ├── pwi4_tle_observer.py
            └── (DDW via win32com)

tkinter_app.py
    ├── api_interaction.py
    ├── automated2.py
    └── utils/helpers.py

web_dashboard.py
    ├── api_interaction.py
    └── automated2.py

infinite.py
    ├── api_interaction.py (subprocess)
    └── automated2.py (subprocess)
```

---

## Hardware Integration

### PlaneWave Mount
- **Protocol:** HTTP REST API
- **Port:** 8220
- **Software:** PlaneWave Interface 4 (PWI4)
- **Integration:** pwi4_client.py

### Observatory Dome
- **Protocol:** ASCOM COM
- **Software:** Digital DomeWorks
- **COM ProgID:** TIDigitalDomeWorks.DomeControl
- **Integration:** win32com.client in automated2.py

### CCD Camera
- **Protocol:** ASCOM COM
- **Software:** MaxIm DL
- **COM ProgID:** MaxIm.CCDCamera
- **Integration:** win32com.client in pwi4_tle_observer.py

---

## Error Handling

### Connection Failures
- **PWI4:** 10 retry attempts, 30 seconds between
- **DDW:** 10 retry attempts, 30 seconds between
- **N2YO API:** Uses cached data if API unavailable

### Observation Failures
- Logged to `telescope_automation_log.txt`
- Continues to next observation on failure
- Emergency stop available via GUI

### System Recovery
- `automated2.py shutdown` for safe shutdown
- infinite.py auto-recovers after 3 failures
- All errors logged with full traceback

---

## Configuration Reference

See `config.sample.py` for all configurable parameters:

```python
# API Configuration
N2YO_API_KEY = "YOUR_KEY"

# Observatory Location
OBSERVER_LAT = 32.903
OBSERVER_LNG = -105.5295
OBSERVER_ALT = 2225

# Timezone
TIMEZONE = "America/Denver"

# Output Paths
OUTPUT_PATH = "D:\\SatelliteData"

# PWI4 Connection
PWI4_HOST = "localhost"
PWI4_PORT = 8220

# Camera Settings
EXPOSURE_LENGTH_SEC = 0.1
```
