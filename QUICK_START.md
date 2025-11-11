# Quick Start Guide - Activity Tracker Widget

## 🚀 Using the Executable

The executable has been created: **dist\ActivityTracker.exe**

### How to Use

#### Option 1: Run Directly
1. Navigate to the `dist` folder
2. Double-click `ActivityTracker.exe`
3. The widget will appear on your screen

#### Option 2: Pin to Taskbar (Recommended)
1. Navigate to `dist\ActivityTracker.exe`
2. Right-click on the file
3. Select **"Pin to taskbar"**
4. Now you can launch it anytime from your Windows taskbar!

#### Option 3: Create Desktop Shortcut
1. Right-click on `dist\ActivityTracker.exe`
2. Select **"Create shortcut"**
3. Drag the shortcut to your desktop
4. Rename it to "Activity Tracker" if desired

### System Tray Controls

Since the minimize/close buttons were removed, use these controls:

- **To Hide**: Right-click the system tray icon → "Hide Widget"
- **To Show**: Double-click the system tray icon OR right-click → "Show Widget"
- **To Quit**: Right-click the system tray icon → "Quit"

### Features

✅ **Auto-save every minute** - Your data is now saved to the database every 60 seconds
✅ **No data loss** - Even if the PC shuts down unexpectedly, you'll only lose max 1 minute of data
✅ **Clean interface** - No distracting buttons, just the info you need
✅ **Draggable** - Click and drag the title bar to position anywhere
✅ **Always on top** - Stays visible above other windows

### Important Notes

- The executable is completely standalone - no Python installation needed
- The database file `activity_tracker.db` will be created in the same folder as the .exe
- The app will create a system tray icon (blue stopwatch)
- All your activity data is stored locally and privately

### Troubleshooting

**Widget not showing?**
- Check the system tray (bottom-right of taskbar)
- Double-click the blue stopwatch icon

**Can't close the app?**
- Right-click the system tray icon
- Select "Quit"

**Data not saving?**
- The app auto-saves every minute
- Data is saved to `activity_tracker.db` in the same folder as ActivityTracker.exe

### File Size
The executable is approximately 100-150 MB due to included libraries (PyQt5, Matplotlib, etc.)
