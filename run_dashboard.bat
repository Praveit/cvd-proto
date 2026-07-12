@echo off
echo ========================================
echo Starting CVD Risk Assessment Dashboard
echo ========================================
echo.
echo [1/3] Installing dependencies (if needed)...
cd /d C:\Users\e\Documents\clinical-dashboard
npm install
echo.
echo [2/3] Starting Python API server on port 8888...
start "Python API" cmd /k "cd /d C:\Users\e\Documents && python http_server.py"
echo.
echo [3/3] Starting Frontend on port 3000...
start "Frontend" cmd /k "cd /d C:\Users\e\Documents\clinical-dashboard && npm run dev"
echo.
echo ========================================
echo DONE! Open http://localhost:3000 in your browser
echo ========================================
pause