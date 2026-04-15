@echo off
setlocal enabledelayedexpansion
REM WiFi Scanner and Optimization Tool - Windows Startup Script
REM Version: v2.0.0
REM Update Date: 2026-03-29

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Change to project root directory (parent of scripts)
cd /d "%SCRIPT_DIR%.."

REM Set environment variables for proper encoding
set PYTHONIOENCODING=utf-8
set LANG=zh_CN.UTF-8

REM Set code page to UTF-8 to support Chinese display
chcp 65001 >nul 2>&1

REM Clear console
cls

echo ============================================================
echo WiFi Scanner and Optimization Tool - Windows
echo ============================================================
echo.

REM Initialize variables
set PYTHON_CMD=
set VENV_PATH=
set VENV_EXISTS=0
set OS_NAME=Windows

REM [1/6] Detect Python environment
echo [1/6] Detecting Python environment...

set "PYTHON_CMD="
set "PYTHON_VERSION="

REM Try to find Python in PATH first
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    goto check_version
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto check_version
)

REM Check common Python installation paths
if exist "C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe" (
    set "PYTHON_CMD=C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe"
    goto check_version
)

if exist "C:\Users\Administrator\AppData\Local\Programs\Python\Python39\python.exe" (
    set "PYTHON_CMD=C:\Users\Administrator\AppData\Local\Programs\Python\Python39\python.exe"
    goto check_version
)

if exist "C:\Python314\python.exe" (
    set "PYTHON_CMD=C:\Python314\python.exe"
    goto check_version
)

if exist "C:\Python39\python.exe" (
    set "PYTHON_CMD=C:\Python39\python.exe"
    goto check_version
)

REM Python not found
echo [ERROR] Python environment detection failed
echo.
echo Please install Python 3.10 or higher:
echo   Download from: https://www.python.org/downloads/
echo   Please check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:check_version
for /f "tokens=2" %%i in ('"%PYTHON_CMD%" --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [INFO] Python version: %PYTHON_VERSION% (command: %PYTHON_CMD%)

REM [2/6] Detect virtual environment
echo [2/6] Detecting virtual environment...

set VENV_EXISTS=0
set VENV_PATH=

if exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment detected: venv
    set "VENV_EXISTS=1"
    set "VENV_PATH=venv"
    goto venv_found
)

if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment detected: .venv
    set "VENV_EXISTS=1"
    set "VENV_PATH=.venv"
    goto venv_found
)

if exist "env\Scripts\activate.bat" (
    echo [INFO] Virtual environment detected: env
    set "VENV_EXISTS=1"
    set "VENV_PATH=env"
    goto venv_found
)

echo [WARNING] No virtual environment detected
echo [INFO] Creating virtual environment automatically...
echo.

"%PYTHON_CMD%" -m venv venv
if %errorlevel% equ 0 (
    echo [INFO] Virtual environment created successfully: venv
    set "VENV_EXISTS=1"
    set "VENV_PATH=venv"
    echo.
) else (
    echo [ERROR] Failed to create virtual environment
    set "VENV_EXISTS=0"
    set "VENV_PATH="
    echo.
)

:venv_found

REM [3/6] Check dependencies
echo [3/6] Checking dependencies...

if "%VENV_EXISTS%"=="1" (
    "%VENV_PATH%\Scripts\python.exe" -c "import geopy" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] geopy dependency OK
    ) else (
        echo [WARNING] geopy not installed
    )
    
    "%VENV_PATH%\Scripts\python.exe" -c "import psutil" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] psutil dependency OK
    ) else (
        echo [WARNING] psutil not installed
    )
    
    "%VENV_PATH%\Scripts\python.exe" -c "import requests" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] requests dependency OK
    ) else (
        echo [WARNING] requests not installed
    )
) else (
    %PYTHON_CMD% -c "import geopy" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] geopy dependency OK
    ) else (
        echo [WARNING] geopy not installed
    )
    
    %PYTHON_CMD% -c "import psutil" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] psutil dependency OK
    ) else (
        echo [WARNING] psutil not installed
    )
    
    %PYTHON_CMD% -c "import requests" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] requests dependency OK
    ) else (
        echo [WARNING] requests not installed
    )
)

REM [4/6] Detect operating system
echo [4/6] Detecting operating system...
echo [INFO] Operating system: Windows

REM [5/6] Set Python executable
echo [5/6] Configuring Python environment...

if "%VENV_EXISTS%"=="1" (
    set "PYTHON_EXE=%VENV_PATH%\Scripts\python.exe"
    echo [INFO] Using virtual environment Python: !PYTHON_EXE!
) else (
    set "PYTHON_EXE=%PYTHON_CMD%"
    echo [INFO] Using system Python: !PYTHON_EXE!
)

REM [6/6] Install missing dependencies
echo [6/6] Installing missing dependencies...

if "%VENV_EXISTS%"=="1" (
    "%VENV_PATH%\Scripts\python.exe" -c "import geopy" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Installing geopy...
        "%VENV_PATH%\Scripts\python.exe" -m pip install geopy -i https://mirrors.aliyun.com/pypi/simple/
    )
    
    "%VENV_PATH%\Scripts\python.exe" -c "import psutil" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Installing psutil...
        "%VENV_PATH%\Scripts\python.exe" -m pip install psutil -i https://mirrors.aliyun.com/pypi/simple/
    )
    
    "%VENV_PATH%\Scripts\python.exe" -c "import requests" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Installing requests...
        "%VENV_PATH%\Scripts\python.exe" -m pip install requests -i https://mirrors.aliyun.com/pypi/simple/
    )
) else (
    %PYTHON_CMD% -c "import geopy" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Installing geopy...
        %PYTHON_CMD% -m pip install geopy -i https://mirrors.aliyun.com/pypi/simple/
    )
    
    %PYTHON_CMD% -c "import psutil" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Installing psutil...
        %PYTHON_CMD% -m pip install psutil -i https://mirrors.aliyun.com/pypi/simple/
    )
    
    %PYTHON_CMD% -c "import requests" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [INFO] Installing requests...
        %PYTHON_CMD% -m pip install requests -i https://mirrors.aliyun.com/pypi/simple/
    )
)

echo [INFO] Dependency installation completed

echo.
echo ============================================================
echo Environment Detection Completed
echo ============================================================
echo.
echo Current Configuration:
echo   Python Command: %PYTHON_CMD%
echo   Python Executable: %PYTHON_EXE%
if "%VENV_EXISTS%"=="1" (
    echo   Virtual Environment: %VENV_PATH%
) else (
    echo   Virtual Environment: Not used
)
echo   Operating System: %OS_NAME%
echo.
echo ============================================================
echo Starting WiFi Scanner and Optimization Tool...
echo ============================================================
echo.

REM Display function menu (using PowerShell for Chinese display)
:menu
powershell -NoProfile -ExecutionPolicy Bypass -Command "$OutputEncoding = [System.Text.Encoding]::UTF8; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Write-Host '============================================================'; Write-Host 'Please select a function:'; Write-Host '============================================================'; Write-Host '1. WiFi Network Scan'; Write-Host '2. Hardware Detection'; Write-Host '3. Projector Recommendation'; Write-Host '4. Interactive Projector Recommendation'; Write-Host '5. Full System Test'; Write-Host '6. Update Projector Database'; Write-Host '7. Update Hardware Database'; Write-Host '8. Update Hardware Data (Network Card, GPU, Projector)'; Write-Host '9. JSON File Management'; Write-Host '10. Run with Custom Parameters'; Write-Host '0. Exit'; Write-Host '============================================================'"
set /p choice=Please select a function (0-10):  

echo.

REM Execute corresponding function based on user selection
if "%choice%"=="1" goto wifi_scan
if "%choice%"=="2" goto hardware_detect
if "%choice%"=="3" goto projector_recommend
if "%choice%"=="4" goto interactive_projector
if "%choice%"=="5" goto all_in_one
if "%choice%"=="6" goto update_projector
if "%choice%"=="7" goto update_hardware
if "%choice%"=="8" goto update_mapping
if "%choice%"=="9" goto json_manage
if "%choice%"=="10" goto custom_params
if "%choice%"=="0" goto exit_program
echo [ERROR] Invalid selection
goto menu

:wifi_scan
echo [INFO] Starting WiFi network scan...
%PYTHON_EXE% wifi_scan.py
goto end

:hardware_detect
echo [INFO] Starting hardware information detection...
%PYTHON_EXE% wifi_scan.py --hardware
goto end

:projector_recommend
echo [INFO] Starting projector recommendation...
%PYTHON_EXE% wifi_scan.py --projector
goto end

:interactive_projector
echo [INFO] Starting interactive projector recommendation...
%PYTHON_EXE% wifi_scan.py --interactive
goto end

:all_in_one
echo [INFO] Starting full system test...
%PYTHON_EXE% wifi_scan.py --all-in-one
goto end

:update_projector
echo [INFO] Updating projector database...
%PYTHON_EXE% wifi_scan.py --projector --update-projector-db
goto end

:update_hardware
echo [INFO] Updating hardware performance database...
%PYTHON_EXE% wifi_scan.py --hardware --update-hardware-db
goto end

:update_mapping
echo [INFO] Updating hardware data (Network Card, GPU, Projector)...
%PYTHON_EXE% wifi_scan.py --update-mapping
goto end

:json_manage
powershell -NoProfile -ExecutionPolicy Bypass -Command "$OutputEncoding = [System.Text.Encoding]::UTF8; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Write-Host '[INFO] JSON file management...'; Write-Host ''; Write-Host 'Please select JSON management function:'; Write-Host '1. Show JSON Statistics'; Write-Host '2. Reorganize JSON Files'; Write-Host '3. Show Classification Rules'"
set /p json_choice=Please select (1-3): 

if "%json_choice%"=="1" (
    %PYTHON_EXE% wifi_scan.py --json-stats
) else if "%json_choice%"=="2" (
    %PYTHON_EXE% wifi_scan.py --organize-json
) else if "%json_choice%"=="3" (
    %PYTHON_EXE% wifi_scan.py --show-json-rules
) else (
    echo [ERROR] Invalid selection
)
goto end

:custom_params
echo [INFO] Run with custom parameters
echo.
echo Available parameters:
echo   --export PATH       Export CSV file (e.g., ./wifi_report.csv)
echo   --debug             Show debug information
echo   --hardware           Hardware detection
echo   --projector          Projector recommendation
echo   --update-projector-db Update projector database
echo   --update-hardware-db Update hardware database
echo   --budget RANGE       Projector budget range (e.g., 3000-8000)
echo   --brand BRAND        Projector brand preference (e.g., XGIMI,JMGO)
echo   --resolution RES      Projector resolution preference (e.g., 4K,1080P)
echo   --all-in-one        Run full system test
echo   --json-stats        Show JSON file statistics
echo   --organize-json     Reorganize JSON files
echo   --show-json-rules   Show JSON classification rules
echo.
set /p custom_params=Enter parameters (e.g., --hardware --debug): 
if "%custom_params%"=="" (
    echo [ERROR] No parameters entered
    goto menu
)
%PYTHON_EXE% wifi_scan.py %custom_params%
goto end

:exit_program
echo [INFO] Exiting program
exit /b 0

:end
echo.
echo ============================================================
echo [SUCCESS] Program execution completed
echo ============================================================
echo.
pause
goto menu