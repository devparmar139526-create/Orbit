@echo off
echo ========================================
echo    Starting Orbit Desktop App
echo ========================================
echo.

echo [1/2] Starting API Server...
start "Orbit API Server" cmd /k "cd /d "%~dp0" && .venv\Scripts\activate && python api_server.py"

echo [2/2] Waiting 3 seconds for server to start...
timeout /t 3 /nobreak > nul

echo [2/2] Starting Desktop App...
start "Orbit Desktop" cmd /k "cd /d "%~dp0orbit-desktop-app" && npm start"

echo.
echo ========================================
echo    Both windows should now be open!
echo ========================================
echo.
echo - API Server running in one window
echo - Desktop App running in another window
echo.
echo Close both windows to stop the app
echo ========================================
pause
