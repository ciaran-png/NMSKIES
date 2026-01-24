# NMSkies Setup Guide

## Prerequisites

### Hardware
- PlaneWave telescope mount (L-series or CDK)
- Digital DomeWorks compatible dome
- CCD camera supported by MaxIm DL
- Windows PC connected to all hardware

### Software
- Windows 7/10/11
- PlaneWave Interface 4 (PWI4) - https://planewave.com/software/
- MaxIm DL - https://diffractionlimited.com/product/maxim-dl/
- Digital DomeWorks - http://www.intechengineering.com/
- ASCOM Platform - https://ascom-standards.org/
- Python 3.8+ - https://www.python.org/

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/ciaran-png/NMSKIES.git
cd NMSKIES
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure N2YO API
Edit `api_interaction.py` and replace the API key:
```python
API_KEY = "YOUR_N2YO_API_KEY"  # Get from https://www.n2yo.com/api/
```

### 5. Configure observatory location
Edit the coordinates in `api_interaction.py` and `dashb/dashapp.py`:
```python
# Cloudcroft, New Mexico (default)
observer_lat = 32.903
observer_lng = -105.5295
observer_alt = 2225  # meters
```

### 6. Configure output path
Edit `pwi4_tle_observer.py`:
```python
OUTPUT_PATH = 'D:\\SatelliteData'  # Change to your preferred path
```

### 7. Create NORAD ID list
Copy the sample and edit:
```bash
copy noradid.sample.txt noradid.txt
```
Add your target satellite NORAD IDs (comma-separated).

## Running the System

### Option 1: Full Automation
```bash
# Generate observation plan
python api_interaction.py --non-interactive --days 1

# Run automation (starts mount, opens dome, observes, shuts down)
python automated2.py
```

### Option 2: Dashboard Control
```bash
python dashb/dashapp.py
# Open http://localhost:8050 in browser
```

### Option 3: Interactive Mode
```bash
python api_interaction.py
# GUI will prompt for NORAD IDs and settings
```

## Troubleshooting

### PWI4 Connection Failed
- Ensure PWI4 is running and telescope is connected
- Check PWI4 is listening on port 8220
- Verify `http://localhost:8220/status` returns data

### Dome Not Responding
- Check Digital DomeWorks is running
- Verify ASCOM connection in DDW settings
- Test dome control manually first

### N2YO API Errors
- Check API key is valid
- Verify internet connection
- Check rate limits (free tier: 1000 requests/hour)

### Camera Issues
- Ensure MaxIm DL is installed and licensed
- Check camera connection in MaxIm
- Verify ASCOM camera driver is installed

## File Locations

| File | Purpose |
|------|---------|
| `C:\Program Files (x86)\PlaneWave Instruments\PlaneWave Interface 4\Scripts\` | Default install location |
| `D:\SatelliteData\` | Default image output |
| `tleplan.txt` | Current observation schedule |
| `cache.json` | TLE data cache |

## Support

For PlaneWave hardware/software issues:
- PlaneWave Support: https://planewave.com/support/

For ASTRIANet collaboration:
- Contact: moriba@utexas.edu
