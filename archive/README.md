# Archived/Deprecated Code

This directory contains code that is no longer in active use. These files are preserved
for historical reference but should NOT be used in production.

## Contents

### deprecated_dashb/
Old dashboard iterations with various issues:

- **run_it_up.py** - Earlier GUI version with circular import issues
- **run_it_up1.py** - Python 2.7 compatible version (uses .format() instead of f-strings)
- **gui_setup.py** - Attempted modular GUI setup (broken imports)
- **server.py** - Flask + SocketIO server (broken imports from run_it_up2.py)
- **list_of_sats.py** - Standalone satellite pass finder (hardcoded Albuquerque coords)
- **asteroid.py** - Incomplete asteroid tracking automation
- **upload_to_dropbox.py** - Incomplete Dropbox upload (missing imports)

## Why These Were Archived

1. **Circular Imports**: Several files import from each other creating dependency loops
2. **Incomplete Code**: Missing function definitions, imports, or variable declarations
3. **Superseded**: Replaced by newer, more robust implementations
4. **Hardcoded Values**: Contains incorrect coordinates or exposed credentials

## If You Need This Code

The functionality from these files has been consolidated into:
- `gui/tkinter_app.py` - Main desktop GUI
- `gui/web_dashboard.py` - Web-based dashboard
- `utils/helpers.py` - Utility functions

Do not attempt to use the archived code without significant refactoring.
