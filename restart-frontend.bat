@echo off
echo Stopping frontend...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3003 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul

echo Starting frontend with local API...
cd frontend
start "Frontend (Local API)" cmd /k "npm run dev"
cd ..

echo.
echo ✓ Frontend restarting with local API
echo ✓ API URL: http://localhost:8000/api/v1
echo.
echo Wait 5 seconds, then open: http://localhost:3003
pause
