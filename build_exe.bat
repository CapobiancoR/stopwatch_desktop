@echo off
echo ==========================================
echo Building Activity Tracker Executable
echo ==========================================
echo.

echo Creating icon...
.venv\Scripts\python.exe create_icon.py
echo.

echo Building executable with PyInstaller...
echo This may take a few minutes...
echo.

.venv\Scripts\pyinstaller.exe --clean --noconfirm ActivityTracker.spec

echo.
echo ==========================================
if exist "dist\ActivityTracker.exe" (
    echo Build successful!
    echo.
    echo Executable location: dist\ActivityTracker.exe
    echo.
    echo You can now:
    echo 1. Run dist\ActivityTracker.exe to launch the app
    echo 2. Right-click and "Pin to taskbar" to add to Windows taskbar
    echo 3. Create a shortcut on your desktop
) else (
    echo Build failed! Check the output above for errors.
)
echo ==========================================
pause
