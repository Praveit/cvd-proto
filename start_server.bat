@echo off
echo Starting CVD Risk Assessment Server...
echo.
echo Starting Python API server on port 8888...
start "Python Server" cmd /k "cd C:\Users\e\Documents && python http_server.py"

echo Waiting for Python server...
timeout /t 5 /nobreak >nul

echo Starting Next.js frontend on port 3000...
start "Next.js" cmd /k "cd C:\Users\e\Documents\clinical-dashboard && npm run dev"

echo.
echo ============================================
echo Both servers should be running now!
echo.
echo Python API: http://localhost:8888
echo Frontend:   http://localhost:3000
echo.
echo Press any key to exit this window...
pause >nul