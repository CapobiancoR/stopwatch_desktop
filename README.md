# Desktop Activity Tracker Widget

A modern desktop widget for Windows that tracks your daily computer activity time, distinguishing between work time and leisure time.

## Features

- **Automatic Timer**: Automatically tracks when you're active on PC (detects mouse and keyboard activity)
- **Work/Leisure Distinction**: Manual checkbox to flag when you're at the PC but not working
- **Daily History**: View activity times from the last 7 days
- **Weekly Charts**: Graphical report of activity times over the last 28 days
- **Local Database**: All data saved in a local SQLite database
- **Modern UI**: Sleek dark theme with gradient cards and smooth animations
- **Always On Top**: Widget stays on top as a floating overlay
- **System Tray**: Minimizes to system tray, stays running in background
- **Auto-save**: Data saved every 60 seconds to prevent data loss

## Modern Design

- **Frameless Window**: Borderless widget with rounded corners
- **Dark Theme**: Modern dark gradient background with vibrant accent colors
- **Gradient Cards**: Beautiful color gradients for each time counter
  - Work Time: Green gradient
  - Leisure Time: Orange gradient
  - Total Time: Blue gradient
- **Smooth Animations**: Hover effects and transitions
- **Draggable**: Drag the widget anywhere on your screen by the title bar
- **System Tray Integration**: Double-click tray icon to show/hide
- **Clean Interface**: No distracting buttons - use system tray for controls
- **Auto-save**: Data saved to database every 60 seconds

## Installation

### Option 1: Use the Executable (Recommended)

**No Python installation required!**

1. Go to the `dist` folder
2. Run `ActivityTracker.exe`
3. **Pin to Taskbar**: Right-click the .exe, select "Pin to taskbar" for easy access

### Option 2: Run from Source

1. Ensure you have Python 3.8 or higher installed
2. Install dependencies:
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Usage

### Using the Executable
Simply run:
```
dist\ActivityTracker.exe
```

### Using Python
```powershell
.venv\Scripts\python.exe main.py
```

Or use the batch file:
```powershell
.\start.bat
```

## How It Works

- The app starts and automatically begins tracking your activity
- When you move the mouse or press keys, the timer activates
- After 60 seconds of inactivity, the timer pauses
- **"I'm on leisure mode" Checkbox**: Check this when you're at the PC but not working
  - Time will be counted separately as "Leisure Time"
  - Useful for breaks, personal browsing, gaming, etc.
- **Auto-save**: Your data is saved to the database every 60 seconds

## Application Tabs

1. **Timer**: Main view with three counters
   - Work Time (green gradient)
   - Leisure Time (orange gradient)
   - Total Time (blue gradient)

2. **History**: Table with data from the last 7 days

3. **Charts**: Bar charts showing activity from the last 28 days

## Window Controls

- **Drag**: Click and drag the title bar to move the widget
- **System Tray Icon**: Blue stopwatch icon in the system tray
  - **Double-click**: Show/hide the widget
  - **Right-click**: Access menu (Show, Hide, Quit)
- **Hide to Tray**: Widget continues tracking in background
- **Quit**: Right-click tray icon and select "Quit"

## Pin to Taskbar

For quick access, pin the executable to your Windows taskbar:

1. Navigate to `dist\ActivityTracker.exe`
2. Right-click the file
3. Select **"Pin to taskbar"**
4. The app icon will appear in your taskbar
5. Click to launch anytime!

## Data Safety

- **Auto-save every minute**: Data is saved to the database every 60 seconds
- **No data loss**: Even if your PC shuts down unexpectedly, you'll lose max 1 minute of data
- **Local storage**: All data stored in `activity_tracker.db` SQLite database
- **Privacy**: All data stays on your computer, no internet connection required

## Project Structure

- `main.py`: Main GUI interface (PyQt5) with modern design
- `database.py`: SQLite database management for storing sessions
- `tracker.py`: User activity monitoring (mouse/keyboard)
- `requirements.txt`: Python dependencies
- `ActivityTracker.exe`: Standalone executable (in dist folder)
- `icon.ico`: Application icon
- `activity_tracker.db`: SQLite database (created automatically)

## Technical Details

- The tracker detects activity through mouse and keyboard listeners (pynput)
- Idle threshold: 60 seconds (customizable in `tracker.py`)
- Auto-save interval: 60 seconds
- Data is saved in real-time to prevent loss
- The app runs on Windows only
- Widget is frameless and always on top for quick visibility
- System tray integration for background operation

## Customization

You can modify the idle threshold in the `main.py` file:
```python
self.tracker = ActivityTracker(idle_threshold=60)  # seconds
```

Change the widget size in `main.py`:
```python
self.setGeometry(100, 100, 380, 520)  # x, y, width, height
```

Change auto-save interval in `main.py`:
```python
self.autosave_timer.start(60000)  # milliseconds (60000 = 1 minute)
```

## Building Your Own Executable

If you want to rebuild the executable:

```powershell
.\build_exe.bat
```

Or manually:
```powershell
.venv\Scripts\python.exe create_icon.py
.venv\Scripts\pyinstaller.exe --clean --noconfirm ActivityTracker.spec
```

The executable will be created in the `dist` folder.

## System Requirements

- Windows 7 or higher
- 100 MB disk space (for executable)
- No Python required when using the .exe file

## Tips

- The widget stays on top of all windows for easy monitoring
- Minimize to tray to keep it running without visual distraction
- The leisure mode checkbox helps you distinguish productive time from breaks
- Check the Charts tab weekly to see your activity patterns
- Pin to taskbar for instant access when you start your PC
- The app remembers your data even after restart
