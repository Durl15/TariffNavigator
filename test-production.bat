@echo off
echo ========================================
echo  Testing Production Deployment
echo ========================================
echo.

echo Testing Backend Endpoints...
echo.

echo 1. Testing new Stats API:
curl -s https://tariffnavigator-backend.onrender.com/api/v1/stats/public
echo.
echo.

echo 2. Testing enhanced search with filters:
curl -s "https://tariffnavigator-backend.onrender.com/api/v1/tariff/search?code=8517&country=CN&sort_by=rate_asc&limit=3"
echo.
echo.

echo 3. Testing popular HS codes:
curl -s https://tariffnavigator-backend.onrender.com/api/v1/stats/public/popular-hs-codes
echo.
echo.

echo 4. Testing PDF generation (downloading test.pdf):
curl -o test.pdf https://tariffnavigator-backend.onrender.com/api/v1/export/test-pdf
if exist test.pdf (
    echo SUCCESS: PDF downloaded as test.pdf
    echo Check the file to verify it's a valid PDF
) else (
    echo FAILED: PDF not downloaded
)
echo.
echo.

echo ========================================
echo Frontend URL: https://tariffnavigator.vercel.app
echo Backend URL: https://tariffnavigator-backend.onrender.com
echo ========================================
echo.
echo Press any key to exit...
pause >nul
