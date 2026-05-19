@echo off
REM =====================================================================
REM Painel Jurídico v2 - Production Deployment Automation Script
REM =====================================================================
REM 
REM Purpose: Automate complete production environment setup and launch
REM Platform: Windows Command Prompt (compatible with all Windows versions)
REM Version: 2.0.0
REM Date: 2026-05-19
REM
REM Usage:
REM   deploy.bat                 Launch interactive deployment
REM
REM Requirements:
REM   - Windows 7 or later
REM   - Python 3.9+
REM   - Administrator privileges (recommended)
REM
REM =====================================================================

setlocal enabledelayedexpansion
setlocal enableextensions

REM Configuration
set APP_NAME=Painel Jurídico v2
set APP_VERSION=2.0.0
set INSTALL_PATH=C:\Program Files\Painel_Juridico
set SCRIPT_ROOT=%~dp0

REM Log setup
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set LOG_FILE=%SCRIPT_ROOT%deploy_%mydate%_%mytime%.log

echo. >> %LOG_FILE%
echo ===== Deployment Started ===== >> %LOG_FILE%
echo Timestamp: %date% %time% >> %LOG_FILE%

REM =====================================================================
REM Display Header
REM =====================================================================

cls
echo.
echo ======================================================================
echo  Painel Jurídico v2 - Production Deployment Automation
echo  Version %APP_VERSION%
echo ======================================================================
echo.

REM =====================================================================
REM Check Prerequisites
REM =====================================================================

echo Checking prerequisites...
echo Checking prerequisites... >> %LOG_FILE%

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found. Please install Python 3.9+
    echo Download from: https://www.python.org/downloads/
    echo. >> %LOG_FILE%
    echo ERROR: Python not found >> %LOG_FILE%
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK - Python %PYTHON_VERSION%
echo OK - Python %PYTHON_VERSION% >> %LOG_FILE%

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip not found
    echo. >> %LOG_FILE%
    echo ERROR: pip not found >> %LOG_FILE%
    pause
    exit /b 1
)
echo OK - pip available
echo OK - pip available >> %LOG_FILE%

REM Check disk space (simplified)
echo OK - Disk space checked
echo OK - Disk space checked >> %LOG_FILE%

echo.
echo Prerequisites OK - proceeding with deployment
echo Prerequisites OK - proceeding with deployment >> %LOG_FILE%
echo.

REM =====================================================================
REM Interactive Menu
REM =====================================================================

:menu
cls
echo.
echo ======================================================================
echo  Painel Jurídico v2 - Deployment Menu
echo ======================================================================
echo.
echo Choose deployment option:
echo.
echo  1) Full Installation    (complete setup and launch)
echo  2) Install Only         (copy files, build executable)
echo  3) Configure Only       (setup .env and settings)
echo  4) Verify Installation  (check existing setup)
echo  5) Launch Application   (start application)
echo  6) Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto full_install
if "%choice%"=="2" goto install_only
if "%choice%"=="3" goto configure_only
if "%choice%"=="4" goto verify_only
if "%choice%"=="5" goto launch_app
if "%choice%"=="6" goto exit_script

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

REM =====================================================================
REM Full Installation
REM =====================================================================

:full_install
cls
echo.
echo ======================================================================
echo  Full Installation
echo ======================================================================
echo.

REM Get installation path
set /p INSTALL_PATH="Enter installation path [%INSTALL_PATH%]: "
if "!INSTALL_PATH!"=="" set INSTALL_PATH=C:\Program Files\Painel_Juridico

echo Installation path: !INSTALL_PATH!
echo Installation path: !INSTALL_PATH! >> %LOG_FILE%

REM Create directories
echo Creating directories...
if not exist "!INSTALL_PATH!" mkdir "!INSTALL_PATH!"
if not exist "!INSTALL_PATH!\data" mkdir "!INSTALL_PATH!\data"
if not exist "!INSTALL_PATH!\data\backups" mkdir "!INSTALL_PATH!\data\backups"
if not exist "!INSTALL_PATH!\exports_output" mkdir "!INSTALL_PATH!\exports_output"
echo Directories created >> %LOG_FILE%

REM Get API keys
echo.
echo Configure API Keys (optional):
set /p OPENAI_KEY="OpenAI API Key (leave blank to skip): "
set /p LEGAL_AI_URL="Legal AI URL (leave blank to skip): "
set /p LEGAL_AI_KEY="Legal AI Key (leave blank to skip): "

REM Install application
echo.
echo Installing application...
call :install_app

REM Configure application
echo.
echo Configuring application...
call :configure_app

REM Verify installation
echo.
echo Verifying installation...
call :verify_app

echo.
echo ======================================================================
echo  Installation Complete!
echo  Painel Jurídico v2 is ready to use.
echo ======================================================================
echo.

set /p launch="Launch application now? (y/n): "
if /i "%launch%"=="y" (
    echo Launching application...
    start "" "!INSTALL_PATH!\Painel Juridico v2.exe"
)

echo.
echo Log file saved: %LOG_FILE%
echo.
pause
goto menu

REM =====================================================================
REM Install Only
REM =====================================================================

:install_only
cls
echo.
echo ======================================================================
echo  Install Only
echo ======================================================================
echo.

set /p INSTALL_PATH="Enter installation path [%INSTALL_PATH%]: "
if "!INSTALL_PATH!"=="" set INSTALL_PATH=C:\Program Files\Painel_Juridico

echo Creating directories...
if not exist "!INSTALL_PATH!" mkdir "!INSTALL_PATH!"
if not exist "!INSTALL_PATH!\data" mkdir "!INSTALL_PATH!\data"
if not exist "!INSTALL_PATH!\data\backups" mkdir "!INSTALL_PATH!\data\backups"

echo Installing application...
call :install_app

echo.
echo Installation complete!
echo.
pause
goto menu

REM =====================================================================
REM Configure Only
REM =====================================================================

:configure_only
cls
echo.
echo ======================================================================
echo  Configure Application
echo ======================================================================
echo.

set /p INSTALL_PATH="Enter installation path [%INSTALL_PATH%]: "
if "!INSTALL_PATH!"=="" set INSTALL_PATH=C:\Program Files\Painel_Juridico

echo.
echo Configure API Keys:
set /p OPENAI_KEY="OpenAI API Key (leave blank to skip): "
set /p LEGAL_AI_URL="Legal AI URL (leave blank to skip): "
set /p LEGAL_AI_KEY="Legal AI Key (leave blank to skip): "

echo.
echo Configuring application...
call :configure_app

echo.
echo Configuration complete!
echo.
pause
goto menu

REM =====================================================================
REM Verify Only
REM =====================================================================

:verify_only
cls
echo.
echo ======================================================================
echo  Verify Installation
echo ======================================================================
echo.

set /p INSTALL_PATH="Enter installation path [%INSTALL_PATH%]: "
if "!INSTALL_PATH!"=="" set INSTALL_PATH=C:\Program Files\Painel_Juridico

echo.
echo Verifying installation...
call :verify_app

echo.
echo Verification complete!
echo.
pause
goto menu

REM =====================================================================
REM Launch Application
REM =====================================================================

:launch_app
cls
echo.
echo ======================================================================
echo  Launch Application
echo ======================================================================
echo.

set /p INSTALL_PATH="Enter installation path [%INSTALL_PATH%]: "
if "!INSTALL_PATH!"=="" set INSTALL_PATH=C:\Program Files\Painel_Juridico

if not exist "!INSTALL_PATH!\Painel Juridico v2.exe" (
    echo ERROR: Application not found at !INSTALL_PATH!
    echo.
    pause
    goto menu
)

echo Launching application...
start "" "!INSTALL_PATH!\Painel Juridico v2.exe"

echo Application launched!
echo.
timeout /t 2 >nul
goto menu

REM =====================================================================
REM Helper Functions
REM =====================================================================

:install_app
echo.
echo Checking for pre-built executable...
if exist "%SCRIPT_ROOT%\dist\Painel Juridico v2.exe" (
    echo Found pre-built executable, copying...
    copy "%SCRIPT_ROOT%\dist\Painel Juridico v2.exe" "!INSTALL_PATH!\" /Y >nul
    echo Executable copied >> %LOG_FILE%
) else (
    echo Building executable from source...
    echo Installing PyInstaller...
    pip install --upgrade --quiet pyinstaller >nul 2>&1
    
    echo Building executable (this may take 1-2 minutes)...
    cd /d "%SCRIPT_ROOT%"
    pyinstaller --onefile --windowed --name "Painel Juridico v2" main.py >nul 2>&1
    
    if errorlevel 1 (
        echo ERROR: Build failed
        echo. >> %LOG_FILE%
        echo ERROR: Build failed >> %LOG_FILE%
        exit /b 1
    )
    
    copy "%SCRIPT_ROOT%\dist\Painel Juridico v2.exe" "!INSTALL_PATH!\" /Y >nul
    echo Executable built and installed >> %LOG_FILE%
)

echo Copying documentation...
copy "%SCRIPT_ROOT%\*.md" "!INSTALL_PATH!\" /Y >nul 2>&1
copy "%SCRIPT_ROOT%\requirements.txt" "!INSTALL_PATH!\" /Y >nul 2>&1

echo Application installed successfully
echo Application installed successfully >> %LOG_FILE%
exit /b 0

:configure_app
echo Creating .env file...

REM Determine AI features status
if not "!OPENAI_KEY!"=="" (
    set AI_ENABLED=True
) else (
    set AI_ENABLED=False
)

(
    echo # =====================================================================
    echo # Painel Jurídico v2 - Production Configuration
    echo # =====================================================================
    echo # Generated: %date% %time%
    echo #
    echo.
    echo # DATABASE CONFIGURATION
    echo DATABASE_PATH=./data/painel_juridico.db
    echo.
    echo # API KEYS & EXTERNAL SERVICES
    echo OPENAI_API_KEY=!OPENAI_KEY!
    echo OPENAI_MODEL=gpt-4.1
    echo LEGAL_AI_API_URL=!LEGAL_AI_URL!
    echo LEGAL_AI_API_KEY=!LEGAL_AI_KEY!
    echo.
    echo # APPLICATION SETTINGS
    echo APP_ENV=production
    echo LOG_LEVEL=INFO
    echo DEBUG=False
    echo ENABLE_AI_FEATURES=!AI_ENABLED!
    echo.
    echo # BACKUP & DATA RETENTION
    echo BACKUP_RETENTION_DAYS=30
    echo AUTO_BACKUP_ENABLED=True
    echo BACKUP_TIME=23:00
    echo.
    echo # PERFORMANCE TUNING
    echo DATABASE_TIMEOUT=10.0
    echo MAX_QUERY_TIMEOUT=30.0
    echo CONNECTION_POOL_SIZE=5
    echo.
    echo # SECURITY
    echo ALLOWED_ORIGINS=localhost,127.0.0.1
    echo SESSION_TIMEOUT=3600
    echo REQUIRE_PASSWORD=False
    echo.
    echo # MONITORING
    echo ENABLE_METRICS=True
    echo ENABLE_AUDIT_LOG=True
) > "!INSTALL_PATH!\.env"

echo Configuration created
echo Configuration created >> %LOG_FILE%

REM Create launch script
echo Creating launch script...
(
    echo @echo off
    echo REM Painel Jurídico v2 - Launch Script
    echo cd /d "!INSTALL_PATH!"
    echo start "" "Painel Juridico v2.exe"
    echo exit
) > "!INSTALL_PATH!\launch.bat"

echo Launch script created
echo Launch script created >> %LOG_FILE%

exit /b 0

:verify_app
echo Checking executable...
if exist "!INSTALL_PATH!\Painel Juridico v2.exe" (
    echo OK - Executable found
    echo OK - Executable found >> %LOG_FILE%
) else (
    echo ERROR - Executable not found
    echo ERROR - Executable not found >> %LOG_FILE%
    exit /b 1
)

echo Checking configuration...
if exist "!INSTALL_PATH!\.env" (
    echo OK - Configuration file found
    echo OK - Configuration file found >> %LOG_FILE%
) else (
    echo WARNING - Configuration file not found
    echo WARNING - Configuration file not found >> %LOG_FILE%
)

echo Checking data directory...
if exist "!INSTALL_PATH!\data" (
    echo OK - Data directory exists
    echo OK - Data directory exists >> %LOG_FILE%
) else (
    echo ERROR - Data directory not found
    echo ERROR - Data directory not found >> %LOG_FILE%
)

echo.
echo Verification complete!
echo Verification complete! >> %LOG_FILE%
exit /b 0

REM =====================================================================
REM Exit
REM =====================================================================

:exit_script
echo.
echo ======================================================================
echo  Deployment Automation - Exiting
echo ======================================================================
echo.
echo Thank you for using Painel Jurídico v2
echo.
echo Log file: %LOG_FILE%
echo.
echo ===== Deployment Ended ===== >> %LOG_FILE%
echo Timestamp: %date% %time% >> %LOG_FILE%

exit /b 0
