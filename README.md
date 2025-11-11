# ⚡ Activity Tracker

A modern, lightweight **Windows desktop application** that automatically tracks your daily computer activity time, distinguishing between work and leisure periods. Perfect for productivity monitoring, time management, and understanding your daily habits.

## ✨ Features

### 🎯 Core Functionality
- **Automatic Activity Detection** - Tracks mouse movements and keyboard input in real-time
- **Dual Mode Tracking** - Separate tracking for work and leisure time
- **Smart Pause Detection** - Automatically logs inactivity pauses (>60 seconds by default)
- **Auto-Save** - Saves progress every 60 seconds automatically
- **System Tray Integration** - Minimize to taskbar and access from tray menu

### 📊 Analytics & History
- **Daily Statistics** - View work/leisure time for each day
- **28-Day Charts** - Visual bar charts showing activity trends
- **Pause History** - Complete record of all inactivity pauses with timestamps and durations
- **Activity Logs** - All records stored in local SQLite database

### ⚙️ Customization
- **Configurable Idle Timeout** - Adjust inactivity detection threshold (10-300 seconds)
- **Dark Theme UI** - Modern, eye-friendly gradient interface
- **Taskbar Integration** - Always accessible from Windows taskbar

### 🔒 Privacy
- **100% Local** - No internet connection required, all data stored locally
- **No Cloud Sync** - Your activity data never leaves your computer
- **Open Source** - Full transparency on how it works

## 📦 Installation

### Option 1: Ready-to-Use Executable (Recommended)
1. Download `ActivityTracker.exe` from the [Releases](https://github.com/CapobiancoR/stopwatch_desktop/releases) page
2. Run the executable - no installation required!
3. The app will create a local database automatically

### Option 2: Run from Source
**Requirements:**
- Python 3.12+
- Virtual environment (optional but recommended)

**Steps:**
```bash
# Clone the repository
git clone https://github.com/CapobiancoR/stopwatch_desktop.git
cd stopwatch_desktop

# Create virtual environment (optional)
python -m venv .venv
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 🚀 Usage

### Main Timer Tab (⏱️)
1. **Start Tracking** - The timer automatically starts when you move your mouse or press a key
2. **Stop Tracking** - The timer automatically stops after 60 seconds of inactivity (configurable)
3. **Switch Modes** - Check the "Leisure Mode" box to switch between work and leisure tracking
4. **View Progress** - Real-time display of today's work and leisure time

### History Tab (📅)
- **Daily Records** - View all your activity statistics by date
- **Pause History** - See all detected pauses with exact timestamps and durations
- **Refresh Data** - Click to manually refresh the history display
- **Reset Database** - Clear all data (with confirmation)

### Charts Tab (📊)
- **28-Day Overview** - Visual bar chart of your last 28 days
- **Work vs Leisure** - Compare work time (green) vs leisure time (orange)
- **Trends** - Identify patterns in your daily activity

### Settings Tab (⚙️)
- **Idle Timeout** - Adjust the inactivity detection time (slider or input box)
- **Save Settings** - Changes apply immediately
- **Range** - 10 to 300 seconds (configurable)

## 🎨 User Interface

### Modern Dark Theme
The app features a sophisticated dark gradient theme (#1e293b → #0f172a) that's easy on the eyes for extended use.

### Navigation Buttons
- **⏱️ Timer** - Main activity tracker
- **📅 History** - View past records and detected pauses
- **📊 Charts** - 28-day activity overview
- **⚙️ Settings** - Configure idle timeout threshold

### Color Coding
- 🟢 **Green (#10b981)** - Work time
- 🟠 **Orange (#f59e0b)** - Leisure time
- 🔵 **Blue (#3b82f6)** - Total time

## 💾 Data Storage

The app uses **SQLite** for local storage with the following tables:

### `activity_sessions`
Tracks individual activity sessions with start/end times and mode

### `daily_summary`
Daily aggregated statistics (work time, leisure time)

### `pause_periods`
Records all detected inactivity pauses with duration and timestamp

**Database Location:** `activity_tracker.db` (created in app directory automatically)

## 🛠️ Technical Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **GUI Framework** | PyQt5 | 5.15.10 |
| **Data Visualization** | Matplotlib | 3.8.2 |
| **Activity Detection** | pynput | 1.7.6 |
| **Database** | SQLite3 | Built-in |
| **Executable Builder** | PyInstaller | 6.16.0 |
| **Python Runtime** | Python | 3.12+ |

## 🔧 Development

### Building the Executable
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build the executable
.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm ActivityTracker.spec
```

The executable will be created in the `dist/` folder.

### Project Structure
```
stopwatch_desktop/
├── main.py                  # Main application UI & event handling
├── tracker.py              # Activity detection engine (pynput-based)
├── database.py             # SQLite database management
├── create_icon.py          # Application icon generator
├── icon.ico               # Application icon
├── app_settings.txt       # User settings (auto-generated)
├── activity_tracker.db    # SQLite database (auto-generated)
├── ActivityTracker.spec   # PyInstaller build configuration
├── ActivityTracker.manifest # Windows manifest for proper theming
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## ⚙️ How It Works

### Activity Detection Engine
1. **Continuous Monitoring** - Background thread monitors mouse position and keyboard input
2. **Idle Detection** - Tracks inactivity duration since last input
3. **Configurable Threshold** - Idle timeout is configurable (default 60 seconds)
4. **Callback System** - Triggers pause logging when user returns from inactivity

### Time Tracking Logic
1. **Session Creation** - New activity session starts when input detected
2. **Real-time Update** - Session duration updated every second
3. **Session End** - Session ends when idle threshold is exceeded
4. **Auto-Save** - Progress saved to database every 60 seconds
5. **Daily Summary** - Records aggregated daily statistics

### Pause Recording
1. **Idle Start** - Records exact timestamp when idle period begins
2. **Duration Calculation** - Computes pause duration when user returns
3. **Database Logging** - Stores pause record with date, time, and duration
4. **History Display** - Pause history available in History tab

## 📋 System Requirements

- **OS:** Windows 7, 8, 8.1, 10, 11
- **RAM:** Minimal (typically <50 MB during operation)
- **Disk Space:** ~50 MB for executable + growing database
- **Network:** Optional (app works completely offline)
- **Input Devices:** Mouse or keyboard (both supported)

## 🐛 Troubleshooting

### Activity not detecting
- Verify mouse/keyboard input is working
- Check pynput permissions (may need admin rights on some systems)
- Try adjusting idle timeout in Settings tab

### Slow startup
- First launch initializes matplotlib (cached after)
- Large databases (1+ year of data) may slow startup
- Consider resetting database if it's very large

### Taskbar icon not showing
- Verify `icon.ico` exists in application directory
- Check Windows notification settings
- Restart the application

### App not grouping in taskbar
- Ensure `ActivityTracker.manifest` is embedded
- Rebuild using PyInstaller

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 👤 Author

**Capobianco R** - [GitHub Profile](https://github.com/CapobiancoR)

## ❓ FAQ

**Q: Does this track what I'm doing?**
A: No! The app only detects mouse/keyboard activity. It doesn't capture which applications you're using or what's on your screen.

**Q: Is my data secure?**
A: Yes, 100% secure. All data is stored locally on your computer in a SQLite database. No internet connection required, no cloud sync.

**Q: Can I export my data?**
A: Currently data is stored in SQLite format. You can access it with any SQLite viewer or tool.

**Q: Why does the timer stop after 60 seconds of inactivity?**
A: This is by design - it prevents false tracking when you're away from your PC. You can adjust this in Settings (10-300 seconds).

**Q: Can I run multiple instances?**
A: Technically yes, but they won't share the same database. Use a single instance for consistent tracking.

**Q: What happens if I close the app?**
A: All unsaved data is automatically saved every 60 seconds, so you won't lose progress. Open the app again to continue.

---

**Made with ❤️ for productivity enthusiasts**
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
