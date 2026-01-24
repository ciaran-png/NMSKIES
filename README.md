# NMSkies Telescope Automation System

Automated satellite tracking and observation system for PlaneWave telescopes, developed for New Mexico Skies Observatory and the ASTRIANet collaboration with UT Austin.

## Overview

This system automates the complete satellite observation workflow:
1. **TLE Acquisition** - Fetches Two-Line Element data from N2YO API
2. **Pass Prediction** - Calculates visible satellite passes for the observatory location
3. **Mount Control** - Commands PlaneWave mount via PWI4 HTTP API
4. **Dome Control** - Operates dome via ASCOM Digital DomeWorks
5. **Image Capture** - Takes exposures via MaxIm DL
6. **Scheduling** - Automates nightly observation cycles

## Installation Location

**Windows Target Path:**
```
C:\Program Files (x86)\PlaneWave Instruments\PlaneWave Interface 4\Scripts
```

This is the default PWI4 Scripts folder. The automation code should reside here to integrate with PlaneWave software.

## Directory Structure

```
NMSKIES/
├── README.md                 # This file
├── SETUP.md                  # Installation guide
├── ANALYSIS.md               # Detailed code analysis
├── ARCHITECTURE.md           # System architecture
├── requirements.txt          # Python dependencies
├── config.sample.py          # Configuration template
│
├── src/                      # Core production modules
│   ├── pwi4_client.py       # PlaneWave API client (DO NOT MODIFY)
│   ├── api_interaction.py   # TLE fetching & scheduling
│   ├── pwi4_tle_observer.py # Observation execution
│   ├── automated2.py        # Main automation controller
│   └── cache_manager.py     # TLE caching utility
│
├── gui/                      # User interfaces
│   ├── tkinter_app.py       # Windows desktop application
│   ├── web_dashboard.py     # Plotly Dash web interface
│   └── dialogs.py           # Input dialogs
│
├── utils/                    # Utility modules
│   ├── helpers.py           # Common helper functions
│   ├── image_downloader.py  # GOES satellite imagery
│   └── observation_filter.py # Observation window adjustment
│
├── runners/                  # Automation scripts
│   ├── infinite.py          # Continuous observation daemon
│   ├── flask_dashboard.py   # Remote control server
│   └── run_scripts.bat      # Windows batch runner
│
├── templates/                # Web templates
│   └── index.html
│
├── data/                     # Sample data files
│   ├── noradid.sample.txt   # Example NORAD IDs
│   └── tleplan.sample.txt   # Example observation plan
│
├── planewave_reference/      # PlaneWave sample code
│   ├── README.txt
│   ├── pwi4_client_demo.py
│   ├── pwi4_startup.py
│   ├── pwi4_build_model.py
│   └── platesolve.py
│
└── archive/                  # Deprecated code (reference only)
    └── deprecated_dashb/
```

## Quick Start

### 1. Prerequisites

- Windows 7/10/11
- Python 3.8+
- PlaneWave Interface 4 (PWI4)
- MaxIm DL
- Digital DomeWorks
- ASCOM Platform

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/ciaran-png/NMSKIES.git
cd NMSKIES

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure settings
copy config.sample.py config.py
# Edit config.py with your API keys and paths
```

### 3. Configuration

Edit `config.py`:
```python
# N2YO API Key (get from https://www.n2yo.com/api/)
N2YO_API_KEY = "YOUR_API_KEY_HERE"

# Observatory Location
OBSERVER_LAT = 32.903      # Your latitude
OBSERVER_LNG = -105.5295   # Your longitude
OBSERVER_ALT = 2225        # Altitude in meters

# Output paths
OUTPUT_PATH = "D:\\SatelliteData"
```

### 4. Create NORAD ID List

```bash
# Copy sample and edit with your target satellites
copy data\noradid.sample.txt noradid.txt
```

### 5. Run

**Option A: Full Automation (Recommended)**
```bash
python runners/infinite.py
```
This runs continuously, waiting for sunset and executing observations nightly.

**Option B: Manual Control via GUI**
```bash
python gui/tkinter_app.py
```

**Option C: Web Dashboard**
```bash
python gui/web_dashboard.py
# Open http://localhost:8050
```

**Option D: Single Run**
```bash
# Generate observation plan
python src/api_interaction.py --non-interactive --days 1

# Execute observations
python src/automated2.py
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ tkinter_app.py  │ web_dashboard.py│ infinite.py (daemon)        │
│ (Desktop GUI)   │ (Web :8050)     │ (Headless automation)       │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                       │
         └─────────────────┼───────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CORE AUTOMATION                              │
│                    automated2.py                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ startup_pwi4 │→ │ control_ddw  │→ │ run_observer()       │  │
│  │ (mount init) │  │ (dome ops)   │  │ (observation loop)   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                 │                       │
         ▼                 ▼                       ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐
│  pwi4_client.py │ │ DDW (ASCOM)     │ │ pwi4_tle_observer.py    │
│  ↓              │ │ Dome Control    │ │ ↓                       │
│  PWI4 HTTP API  │ └─────────────────┘ │ MaxIm DL Camera         │
│  (localhost:    │                     │ ↓                       │
│   8220)         │                     │ FITS files to disk      │
└─────────────────┘                     └─────────────────────────┘
         │                                         │
         ▼                                         ▼
┌─────────────────┐                     ┌─────────────────────────┐
│ PlaneWave Mount │                     │ D:\SatelliteData\       │
│ (L-series/CDK)  │                     │ └── {timestamp}_{sat}\  │
└─────────────────┘                     │     └── *.fits          │
                                        └─────────────────────────┘
```

## Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ noradid.txt  │ ──▶ │ N2YO API     │ ──▶ │ tleplan.txt  │
│ (NORAD IDs)  │     │ (TLE data)   │     │ (schedule)   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 ▼
                     ┌──────────────────────────────────────┐
                     │ pwi4_tle_observer.py                 │
                     │ For each observation:                │
                     │   1. Parse TLE from tleplan.txt      │
                     │   2. pwi4.mount_follow_tle()         │
                     │   3. MaxIm DL exposure               │
                     │   4. Save FITS with metadata         │
                     └──────────────────────────────────────┘
                                                 │
                                                 ▼
                     ┌──────────────────────────────────────┐
                     │ D:\SatelliteData\                    │
                     │ └── 20250124_193955_STARLINK-1628\   │
                     │     ├── 0001_Azm_45.2_Alt_32.1_...   │
                     │     ├── 0002_Azm_46.1_Alt_33.2_...   │
                     │     └── ...                          │
                     └──────────────────────────────────────┘
```

## File Formats

### noradid.txt
Comma-separated NORAD catalog IDs:
```
25544,20580,33591,46027,46028,...
```

### tleplan.txt
```
BEGINLOCAL 2025-01-24 19:39:55
ENDLOCAL 2025-01-24 19:43:55
NAME STARLINK-1628
0 STARLINK-1628
1 46169U 20057BE  25022.93928310  .00090653  00000-0  85658-3 0  9996
2 46169  53.0434 106.2911 0000315 268.4288  91.6691 15.66280961275329

BEGINLOCAL 2025-01-24 19:46:35
...
```

## Observatory Details

**New Mexico Skies Observatory**
- Location: Cloudcroft, New Mexico
- Coordinates: 32.903°N, 105.5295°W
- Altitude: 2,225m (7,300ft)
- Timezone: America/Denver (MST/MDT)

## API Keys Required

1. **N2YO API** - https://www.n2yo.com/api/
   - Free tier: 1000 requests/hour
   - Used for TLE data and pass predictions

## Hardware Requirements

- PlaneWave telescope mount (L-series or CDK)
- Digital DomeWorks compatible dome
- CCD camera supported by MaxIm DL
- Windows PC connected to all hardware

## Software Requirements

- PlaneWave Interface 4 (PWI4) - https://planewave.com/software/
- MaxIm DL - https://diffractionlimited.com/product/maxim-dl/
- Digital DomeWorks - http://www.intechengineering.com/
- ASCOM Platform - https://ascom-standards.org/
- Python 3.8+ - https://www.python.org/

## Troubleshooting

### PWI4 Connection Failed
- Ensure PWI4 is running
- Check port 8220 is accessible: `http://localhost:8220/status`

### Dome Not Responding
- Verify Digital DomeWorks is running
- Check ASCOM connection

### N2YO API Errors
- Verify API key is valid
- Check rate limits (1000/hour free tier)

### Camera Issues
- Ensure MaxIm DL is installed and licensed
- Verify camera connection in MaxIm

## Authors

**Ciaran Trevino** - Space4All / ASTRIANet Collaboration
- GitHub: [@ciaran-png](https://github.com/ciaran-png)

## Acknowledgments

- **PlaneWave Instruments** - pwi4_client.py reference implementation
- **New Mexico Skies** - Observatory hosting
- **ASTRIANet / UT Austin** - Collaboration on space domain awareness
- **Moriba Jah** - ASTRIANet Principal Investigator

## License

This project contains both original code and PlaneWave reference implementations.
See individual files for specific licensing.
