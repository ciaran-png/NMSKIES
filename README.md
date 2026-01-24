# NMSkies Telescope Automation System

Automated satellite tracking and observation system for PlaneWave telescopes at New Mexico Skies observatory in Cloudcroft, NM.

## Overview

This system automates the process of:
1. Fetching Two-Line Element (TLE) data for satellites from N2YO API
2. Calculating visible passes for the observatory location
3. Controlling the PlaneWave telescope mount via PWI4 HTTP API
4. Managing dome operations via ASCOM Digital DomeWorks
5. Capturing images during satellite passes using MaxIm DL
6. Providing a web dashboard for monitoring and control

## Location
- **Observatory:** New Mexico Skies, Cloudcroft, NM
- **Coordinates:** 32.957313°N, 105.742485°W
- **Altitude:** 2,225m (7,300ft)
- **Timezone:** America/Denver (MST/MDT)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Dashboard (dashapp.py)                       │
│                    http://localhost:8050                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   api_interaction.py                             │
│         Fetches TLE data from N2YO, calculates passes            │
│              Outputs: tleplan.txt                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     automated2.py                                │
│            Main automation controller                            │
│     - Starts PWI4 mount                                         │
│     - Opens dome via DDW                                        │
│     - Runs observation sequence                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  pwi4_tle_observer.py                           │
│         Executes satellite tracking observations                 │
│     - Slews mount to follow TLE                                 │
│     - Captures images via MaxIm DL                              │
│     - Saves FITS files with metadata                            │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### Core Scripts

| File | Description |
|------|-------------|
| `pwi4_client.py` | PlaneWave PWI4 HTTP API client library |
| `api_interaction.py` | Fetches TLE data from N2YO, generates observation plan |
| `automated2.py` | Main automation script - controls mount, dome, and observations |
| `pwi4_tle_observer.py` | Executes satellite tracking and image capture |

### Dashboard

| File | Description |
|------|-------------|
| `dashb/dashapp.py` | Plotly Dash web dashboard for monitoring/control |
| `dashb/server.py` | Flask server for dashboard |

### Configuration Files

| File | Description |
|------|-------------|
| `noradid.txt` | List of NORAD IDs to track (currently Starlink satellites) |
| `tleplan.txt` | Generated observation plan with TLE data and timing |
| `cache.json` | TLE data cache to reduce API calls |

### Utilities

| File | Description |
|------|-------------|
| `askfornorad.py` | GUI dialog for entering NORAD IDs |
| `platesolve.py` | Plate solving utilities |
| `dashboard.py` | Alternative dashboard implementation |

## Installation

### Requirements

- Windows 7/10/11 (for PlaneWave and ASCOM integration)
- Python 3.8+
- PlaneWave Interface 4 (PWI4)
- MaxIm DL (for camera control)
- Digital DomeWorks (for dome control)

### Python Dependencies

```bash
pip install requests loguru dash dash-bootstrap-components plotly pytz pywin32 aiohttp
```

Or use the included virtual environment:
```bash
cd Scripts
.\base\Scripts\activate
```

## Usage

### Interactive Mode (GUI)

```bash
python api_interaction.py
```
- Prompts for NORAD IDs, observation days, and window duration
- Generates `tleplan.txt` with observation schedule

### Non-Interactive Mode (Automated)

```bash
python api_interaction.py --non-interactive --days 1 --observation-window 2
```
- Uses NORAD IDs from `noradid.txt`
- Runs without user prompts

### Start Dashboard

```bash
python dashb/dashapp.py
```
- Opens at http://localhost:8050
- Shows observatory status, sun times, controls

### Run Full Automation

```bash
python automated2.py
```
- Starts mount, opens dome, runs observations
- Shuts down automatically after completing schedule

### Shutdown Only

```bash
python automated2.py shutdown
```

## API Keys

The system uses the N2YO API for satellite data:
- Current key in `api_interaction.py`: `HW52FN-38SNHM-5WKRHM-566K`
- Get your own at: https://www.n2yo.com/api/

## Output

Images are saved to: `D:\SatelliteData\{timestamp}_{satellite_name}\`

Filename format:
```
{sequence}_Azm_{azimuth}_Alt_{altitude}_Axis0Dist_{dist0}_Axis1Dist_{dist1}.fits
```

## Logs

- `telescope_automation_log.txt` - Main automation log
- `api_interaction_log.txt` - TLE fetch log  
- `access_log.txt` - Dashboard access log
- `guioperations.log` - GUI operations log

## Original PlaneWave Scripts

The following are original PlaneWave sample scripts:
- `pwi4_client.py` - API client (reference implementation)
- `pwi4_client_demo.py` - Basic usage example
- `pwi4_startup.py` - Startup sequence example
- `pwi4_build_model.py` - Pointing model builder

## Author

Ciaran Trevino - Space4All / ASTRIANet collaboration

## License

See `base/LICENSE` for PlaneWave client library license.
