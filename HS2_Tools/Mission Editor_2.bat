@echo off
setlocal
cd /d "%~dp0"

title HS2 Mission Editor - Select maps folder

set "MAPS_DIR="
set "HISTORY_FILE=%~dp0mission_editor_recent_maps.txt"

for /f "usebackq delims=" %%I in (`powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0select_maps_folder.ps1" -HistoryFile "%HISTORY_FILE%"`) do set "MAPS_DIR=%%I"

if not defined MAPS_DIR exit /b 0

if not exist "%MAPS_DIR%\" (
    echo.
    echo ERROR: The selected folder no longer exists:
    echo "%MAPS_DIR%"
    echo.
    pause
    exit /b 1
)

where py >nul 2>nul
if not errorlevel 1 (
    py hs2_mission_editor.py "%MAPS_DIR%"
) else (
    python hs2_mission_editor.py "%MAPS_DIR%"
)

if errorlevel 1 (
    echo.
    echo Mission Editor exited with an error.
    pause
)

endlocal
