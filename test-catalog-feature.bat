@echo off
echo ===============================================
echo Cost Impact Modeler - Testing Script
echo ===============================================
echo.

echo [1/4] Stopping old servers...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3003 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul

echo [2/4] Starting backend server on port 8000...
cd backend
start "Backend Server" cmd /k "python -m uvicorn main:app --reload --port 8000"
cd ..
timeout /t 5 /nobreak >nul

echo [3/4] Starting frontend server on port 3003...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..
timeout /t 5 /nobreak >nul

echo [4/4] Verifying servers...
curl -s http://localhost:8000/api/v1/health >nul
if %errorlevel% equ 0 (
    echo   ✓ Backend: http://localhost:8000 [RUNNING]
) else (
    echo   ✗ Backend: Failed to start
)

curl -s http://localhost:3003 >nul
if %errorlevel% equ 0 (
    echo   ✓ Frontend: http://localhost:3003 [RUNNING]
) else (
    echo   ✗ Frontend: Failed to start
)

echo.
echo ===============================================
echo Testing Instructions:
echo ===============================================
echo 1. Open browser: http://localhost:3003/catalogs
echo 2. Click "Upload Catalog"
echo 3. Upload: test-catalog.csv
echo 4. Name: "Q1 2024 Test Catalog"
echo 5. View impact dashboard
echo 6. Select destination: China (CN)
echo 7. Verify metrics and charts display correctly
echo ===============================================
echo.
pause
