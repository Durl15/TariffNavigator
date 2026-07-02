@echo off
echo ========================================
echo  TariffNavigator - Local Testing Setup
echo ========================================
echo.
echo This will open TWO terminal windows:
echo   1. Backend Server (port 8000)
echo   2. Frontend Dev Server (port 5173)
echo.
echo Press any key to start...
pause >nul

echo.
echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\Projects\TariffNavigator\backend && pyenv local 3.12.0 && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Dev Server...
start "Frontend Dev Server" cmd /k "cd /d C:\Projects\TariffNavigator\frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Check the new terminal windows for server output.
echo When frontend is ready, open: http://localhost:5173
echo.
echo To stop servers: Close the terminal windows
echo ========================================
