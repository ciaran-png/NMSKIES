# NMSkies Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd "C:\Program Files (x86)\PlaneWave Instruments\PlaneWave Interface 4\Scripts"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
copy config.sample.py config.py
# Edit config.py with your N2YO API key and observatory coordinates
```

### 3. Add Target Satellites
```bash
copy data\noradid.sample.txt noradid.txt
# Edit noradid.txt with NORAD IDs (comma-separated)
```

### 4. Run
```bash
# Option A: Desktop GUI
python gui/tkinter_app.py

# Option B: Web Dashboard
python gui/web_dashboard.py
# Open http://localhost:8050

# Option C: Command Line
python src/api_interaction.py --non-interactive --days 1
python src/automated2.py

# Option D: Continuous Automation
python runners/infinite.py
```

---

## Directory Structure

```
Scripts/
├── src/              # Core modules (DON'T MODIFY pwi4_client.py)
├── gui/              # User interfaces (Tkinter + Dash)
├── runners/          # Automation scripts
├── utils/            # Helper functions
├── planewave_reference/  # PlaneWave sample code
├── data/             # Sample data files
├── templates/        # Web templates
└── archive/          # Deprecated code (reference only)
```

---

## Common Tasks

| Task | Command |
|------|---------|
| Update TLE schedule | `python src/api_interaction.py` |
| Run single observation session | `python src/automated2.py` |
| Emergency shutdown | `python src/automated2.py shutdown` |
| Check PWI4 status | Open `http://localhost:8220/status` |

---

## Key Files

| File | Purpose |
|------|---------|
| `config.py` | Your configuration (API keys, coordinates) |
| `noradid.txt` | List of satellite NORAD IDs to track |
| `tleplan.txt` | Generated observation schedule |

---

## Troubleshooting

**PWI4 not responding?**
→ Make sure PlaneWave Interface 4 is running

**No passes found?**
→ Check coordinates in config.py, try different satellites

**Camera errors?**
→ Ensure MaxIm DL is running and camera connected

**Full documentation:** See README.md, SETUP.md, ARCHITECTURE.md
