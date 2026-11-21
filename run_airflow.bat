@echo off
chcp 65001 > nul
echo.

cd /d "%~dp0"

echo [1/3] Checking Docker Desktop status...
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo Docker daemon is not running! Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker to start (this might take 20-30 seconds)...
    :WAIT_DOCKER
    timeout /t 5 /nobreak > nul
    docker info > nul 2>&1
    if %errorlevel% neq 0 (
        echo Still waiting for Docker daemon...
        goto WAIT_DOCKER
    )
    echo Docker is ready!
)

echo.
echo [2/3] Starting Airflow and Data Warehouse containers...
docker compose up -d

echo.
echo [3/3] Airflow services started!
echo =====================================================================
echo  Airflow Web UI: http://localhost:8080
echo  Username:       airflow
echo  Password:       airflow
echo.
echo  Target DAG:     retail_data_warehouse_pipeline
echo =====================================================================
echo Opening Airflow in your browser...
start http://localhost:8080
echo.
pause
