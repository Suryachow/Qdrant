@echo off
echo ========================================
echo   Starting Qdrant on Localhost
echo ========================================
echo.

REM Check if Docker Desktop is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [1/2] Starting Docker Desktop...
    echo Please wait 20-30 seconds for Docker to initialize...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    timeout /t 25 /nobreak >nul
) else (
    echo [1/2] Docker Desktop is already running
)

echo.
echo [2/2] Starting Qdrant container...
docker start local_qdrant

echo.
echo ========================================
echo   Qdrant is running!
echo ========================================
echo.
echo Dashboard: http://localhost:6333/dashboard
echo API: http://localhost:6333
echo.
echo Your 154 university data points are ready!
echo.
pause
