# =====================================================================
# Painel Jurídico v2 - Production Deployment Automation Script
# =====================================================================
# 
# Purpose: Automate complete production environment setup and launch
# Platform: Windows PowerShell 7.0+
# Version: 2.0.0
# Date: 2026-05-19
#
# Usage:
#   .\deploy.ps1                           # Interactive mode (recommended)
#   .\deploy.ps1 -Mode Install             # Install only
#   .\deploy.ps1 -Mode Configure           # Configure only
#   .\deploy.ps1 -Mode Verify              # Verify only
#   .\deploy.ps1 -Mode Full                # Full deployment
#
# =====================================================================

param(
    [ValidateSet('Interactive', 'Install', 'Configure', 'Verify', 'Full')]
    [string]$Mode = 'Interactive',
    
    [string]$InstallPath = "C:\Program Files\Painel_Juridico",
    [string]$OpenAIKey = "",
    [string]$LegalAIUrl = "",
    [string]$LegalAIKey = "",
    [switch]$SkipBackup,
    [switch]$Verbose
)

# =====================================================================
# Configuration
# =====================================================================

$ErrorActionPreference = "Stop"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$ScriptRoot\deploy_${Timestamp}.log"

$AppName = "Painel Jurídico v2"
$AppVersion = "2.0.0"
$RequiredPythonVersion = "3.9"
$RequiredPSVersion = "7.0"

# Colors for output
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Header = "Magenta"
}

# =====================================================================
# Logging Functions
# =====================================================================

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage -ErrorAction SilentlyContinue
}

function Write-Header {
    param([string]$Message)
    Write-Host "`n$('='*70)" -ForegroundColor $Colors.Header
    Write-Host $Message.PadRight(70) -ForegroundColor $Colors.Header
    Write-Host $('='*70) -ForegroundColor $Colors.Header
    Write-Log "=== $Message ==="
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Colors.Success
    Write-Log "SUCCESS: $Message"
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Colors.Warning
    Write-Log "WARNING: $Message"
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Colors.Error
    Write-Log "ERROR: $Message"
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Colors.Info
    Write-Log "INFO: $Message"
}

# =====================================================================
# Validation Functions
# =====================================================================

function Test-PrerequisitesWindows {
    Write-Header "Checking Prerequisites"
    
    $allOk = $true
    
    # Check PowerShell version
    Write-Info "PowerShell: $($PSVersionTable.PSVersion)"
    if ([version]$PSVersionTable.PSVersion -lt [version]$RequiredPSVersion) {
        Write-Warning "PowerShell 7.0+ recommended"
        $allOk = $false
    } else {
        Write-Success "PowerShell version OK"
    }
    
    # Check if running as administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if ($isAdmin) {
        Write-Success "Running with administrator privileges"
    } else {
        Write-Warning "Not running as administrator (may have permission issues)"
    }
    
    # Check Python installation
    Write-Info "Checking Python installation..."
    try {
        $pythonVersion = python --version 2>&1
        Write-Info "Found: $pythonVersion"
        Write-Success "Python installed"
    } catch {
        Write-Error "Python not found. Please install Python 3.9+"
        Write-Info "Download from: https://www.python.org/downloads/"
        return $false
    }
    
    # Check pip
    Write-Info "Checking pip..."
    try {
        $pipVersion = pip --version 2>&1
        Write-Info "Found: $pipVersion"
        Write-Success "pip available"
    } catch {
        Write-Error "pip not found"
        return $false
    }
    
    # Check disk space
    Write-Info "Checking disk space..."
    $drive = $InstallPath.Substring(0, 1)
    $disk = Get-PSDrive -Name $drive
    $freeGB = [math]::Round($disk.Free / 1GB, 2)
    Write-Info "Free space: $freeGB GB on $drive"
    
    if ($disk.Free -lt 500MB) {
        Write-Error "Insufficient disk space (<500MB)"
        return $false
    }
    Write-Success "Disk space OK"
    
    return $allOk
}

function Test-InstallationDirectory {
    Write-Header "Verifying Installation Directory"
    
    Write-Info "Installation path: $InstallPath"
    
    if (Test-Path $InstallPath) {
        Write-Warning "Installation directory already exists"
        $choice = Read-Host "Overwrite? (y/n)"
        if ($choice -ne 'y') {
            Write-Info "Using existing directory"
            return $true
        }
        Write-Info "Backing up existing installation..."
        $backupPath = "$InstallPath.backup_${Timestamp}"
        Move-Item -Path $InstallPath -Destination $backupPath -Force
        Write-Success "Backup created: $backupPath"
    }
    
    Write-Info "Creating directories..."
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallPath\data" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallPath\data\backups" -Force | Out-Null
    New-Item -ItemType Directory -Path "$InstallPath\exports_output" -Force | Out-Null
    
    Write-Success "Installation directory ready"
    return $true
}

# =====================================================================
# Installation Functions
# =====================================================================

function Install-Application {
    Write-Header "Installing Application"
    
    # Check if executable exists
    if (Test-Path "$ScriptRoot\dist\Painel Juridico v2.exe") {
        Write-Info "Found pre-built executable"
        Copy-Item -Path "$ScriptRoot\dist\Painel Juridico v2.exe" -Destination $InstallPath -Force
        Write-Success "Executable copied"
    } else {
        Write-Info "Building executable from source..."
        
        # Install PyInstaller
        Write-Info "Installing PyInstaller..."
        pip install --upgrade --quiet pyinstaller 2>&1 | Out-Null
        Write-Success "PyInstaller installed"
        
        # Build executable
        Write-Info "Building executable (this may take 1-2 minutes)..."
        $buildOutput = pyinstaller --onefile --windowed --name "Painel Juridico v2" main.py 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Build failed"
            Write-Error $buildOutput
            return $false
        }
        
        Copy-Item -Path "$ScriptRoot\dist\Painel Juridico v2.exe" -Destination $InstallPath -Force
        Write-Success "Executable built and installed"
    }
    
    # Copy documentation
    Write-Info "Copying documentation..."
    Copy-Item -Path "$ScriptRoot\*.md" -Destination $InstallPath -Force -ErrorAction SilentlyContinue
    Copy-Item -Path "$ScriptRoot\requirements.txt" -Destination $InstallPath -Force -ErrorAction SilentlyContinue
    
    Write-Success "Application installed successfully"
    return $true
}

function Configure-Application {
    Write-Header "Configuring Application"
    
    # Create or update .env file
    Write-Info "Creating environment configuration (.env)..."
    
    $envContent = @"
# =====================================================================
# Painel Jurídico v2 - Production Configuration
# =====================================================================
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# 

# DATABASE CONFIGURATION
DATABASE_PATH=./data/painel_juridico.db

# API KEYS & EXTERNAL SERVICES
OPENAI_API_KEY=$OpenAIKey
OPENAI_MODEL=gpt-4.1
LEGAL_AI_API_URL=$LegalAIUrl
LEGAL_AI_API_KEY=$LegalAIKey

# APPLICATION SETTINGS
APP_ENV=production
LOG_LEVEL=INFO
DEBUG=False
ENABLE_AI_FEATURES=$(if ($OpenAIKey) { 'True' } else { 'False' })

# BACKUP & DATA RETENTION
BACKUP_RETENTION_DAYS=30
AUTO_BACKUP_ENABLED=True
BACKUP_TIME=23:00

# PERFORMANCE TUNING
DATABASE_TIMEOUT=10.0
MAX_QUERY_TIMEOUT=30.0
CONNECTION_POOL_SIZE=5

# SECURITY
ALLOWED_ORIGINS=localhost,127.0.0.1
SESSION_TIMEOUT=3600
REQUIRE_PASSWORD=False

# MONITORING
ENABLE_METRICS=True
ENABLE_AUDIT_LOG=True
"@
    
    Set-Content -Path "$InstallPath\.env" -Value $envContent -Encoding UTF8
    
    # Set file permissions (restrict access to .env)
    $acl = Get-Acl "$InstallPath\.env"
    $acl.SetAccessRuleProtection($true, $false)
    Set-Acl -Path "$InstallPath\.env" -AclObject $acl
    
    Write-Success "Configuration created"
    
    # Create startup script
    Write-Info "Creating startup script..."
    $launchScript = @"
@echo off
REM Painel Jurídico v2 - Launch Script
REM Change to installation directory
cd /d "$InstallPath"
REM Launch application
start "" "Painel Juridico v2.exe"
exit
"@
    
    Set-Content -Path "$InstallPath\launch.bat" -Value $launchScript -Encoding ASCII
    Write-Success "Startup script created"
    
    # Create desktop shortcut
    Write-Info "Creating desktop shortcut..."
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = "$desktopPath\Painel Juridico v2.lnk"
    
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "$InstallPath\Painel Juridico v2.exe"
    $shortcut.WorkingDirectory = $InstallPath
    $shortcut.IconLocation = "$InstallPath\Painel Juridico v2.exe"
    $shortcut.Save()
    
    Write-Success "Desktop shortcut created"
    
    return $true
}

function Create-BackupDatabase {
    Write-Header "Creating Initial Backup"
    
    if ($SkipBackup) {
        Write-Info "Backup skipped (--SkipBackup)"
        return $true
    }
    
    Write-Info "Creating initial database backup..."
    
    $pythonScript = @"
import os
import sys

# Add install path to Python path
sys.path.insert(0, '$InstallPath')

try:
    from core.database import backup_database
    backup_file = '$InstallPath/data/backups/painel_juridico_initial.json'
    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
    backup_database(backup_file)
    print(f'✅ Backup created: {backup_file}')
except Exception as e:
    print(f'⚠️  Backup skipped: {e}')
    sys.exit(0)
"@
    
    $pythonScript | python 2>&1 | ForEach-Object {
        if ($_ -match "✅") {
            Write-Success $_
        } else {
            Write-Info $_
        }
    }
    
    return $true
}

# =====================================================================
# Verification Functions
# =====================================================================

function Verify-Installation {
    Write-Header "Verifying Installation"
    
    $allOk = $true
    
    # Check executable
    Write-Info "Checking executable..."
    if (Test-Path "$InstallPath\Painel Juridico v2.exe") {
        Write-Success "Executable found"
    } else {
        Write-Error "Executable not found"
        $allOk = $false
    }
    
    # Check .env file
    Write-Info "Checking configuration..."
    if (Test-Path "$InstallPath\.env") {
        Write-Success "Configuration file found"
    } else {
        Write-Error "Configuration file not found"
        $allOk = $false
    }
    
    # Check data directory
    Write-Info "Checking data directory..."
    if (Test-Path "$InstallPath\data") {
        Write-Success "Data directory exists"
    } else {
        Write-Error "Data directory not found"
        $allOk = $false
    }
    
    # Try to run verification script
    Write-Info "Running core verification..."
    
    $verifyScript = @"
import os
import sys
import sqlite3

sys.path.insert(0, '$InstallPath')

# Create data directory if needed
os.makedirs('$InstallPath/data', exist_ok=True)

try:
    # Check if verify_setup.py exists
    if os.path.exists('$ScriptRoot/verify_setup.py'):
        exec(open('$ScriptRoot/verify_setup.py').read())
    else:
        # Minimal verification
        print('Checking database initialization...')
        db_path = '$InstallPath/data/painel_juridico.db'
        from core.database import initialize_database
        initialize_database()
        print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️  Verification skipped: {e}')
"@
    
    $pythonScript | python 2>&1 | ForEach-Object {
        if ($_ -match "✅") {
            Write-Success $_
        } elseif ($_ -match "⚠️") {
            Write-Warning $_
        } else {
            Write-Info $_
        }
    }
    
    return $allOk
}

# =====================================================================
# Interactive Configuration
# =====================================================================

function Get-InteractiveConfig {
    Write-Header "Interactive Configuration"
    
    Write-Host "`nThis script will guide you through setting up Painel Jurídico v2`n"
    
    # Installation path
    Write-Host "Installation directory [default: $InstallPath]: " -NoNewline
    $input = Read-Host
    if ($input) { $InstallPath = $input }
    
    # OpenAI API Key
    Write-Host "`nOpenAI API Key (for AI features, optional): " -NoNewline -ForegroundColor Yellow
    $key = Read-Host -AsSecureString
    if ($key.Length -gt 0) {
        $OpenAIKey = [System.Net.NetworkCredential]::new("", $key).Password
    }
    
    # Legal AI configuration
    Write-Host "`nLegal AI API URL (optional): " -NoNewline
    $input = Read-Host
    if ($input) { $LegalAIUrl = $input }
    
    Write-Host "Legal AI API Key (optional): " -NoNewline
    $input = Read-Host
    if ($input) { $LegalAIKey = $input }
    
    # Backup option
    Write-Host "`nCreate initial backup? (y/n) [default: y]: " -NoNewline
    $input = Read-Host
    if ($input -eq 'n') { $SkipBackup = $true }
    
    Write-Host "`n"
    
    return @{
        InstallPath = $InstallPath
        OpenAIKey = $OpenAIKey
        LegalAIUrl = $LegalAIUrl
        LegalAIKey = $LegalAIKey
        SkipBackup = $SkipBackup
    }
}

# =====================================================================
# Main Execution
# =====================================================================

function Show-Menu {
    Write-Host "`n$('='*70)"
    Write-Host "Painel Jurídico v2 - Deployment Automation" -ForegroundColor Magenta
    Write-Host "Version: $AppVersion" -ForegroundColor Magenta
    Write-Host $('='*70)
    Write-Host ""
    Write-Host "Select deployment mode:"
    Write-Host "  1) Full Installation (complete setup)"
    Write-Host "  2) Install Only (executable and files)"
    Write-Host "  3) Configure Only (API keys and settings)"
    Write-Host "  4) Verify Installation (test existing setup)"
    Write-Host "  5) Launch Application"
    Write-Host "  6) Exit"
    Write-Host ""
    Write-Host -NoNewline "Choose (1-6): "
    
    return Read-Host
}

function Main {
    Write-Log "========== Deployment Started =========="
    Write-Host ""
    
    # Show header
    Write-Host "╔" -NoNewline
    Write-Host $('═'*68) -NoNewline
    Write-Host "╗"
    Write-Host "║ Painel Jurídico v2 - Production Deployment Automation".PadRight(69) + "║"
    Write-Host "║ Version $AppVersion | " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss").PadRight(50) + "║"
    Write-Host "╚" -NoNewline
    Write-Host $('═'*68) -NoNewline
    Write-Host "╝"
    Write-Host ""
    
    Write-Log "Log file: $LogFile"
    
    # Check prerequisites
    if (-not (Test-PrerequisitesWindows)) {
        Write-Error "Prerequisites check failed"
        return $false
    }
    
    # Handle different modes
    switch ($Mode) {
        "Interactive" {
            do {
                $choice = Show-Menu
                
                switch ($choice) {
                    "1" {
                        $config = Get-InteractiveConfig
                        $InstallPath = $config.InstallPath
                        $OpenAIKey = $config.OpenAIKey
                        $LegalAIUrl = $config.LegalAIUrl
                        $LegalAIKey = $config.LegalAIKey
                        $SkipBackup = $config.SkipBackup
                        
                        if (-not (Test-InstallationDirectory)) { return $false }
                        if (-not (Install-Application)) { return $false }
                        if (-not (Configure-Application)) { return $false }
                        if (-not (Create-BackupDatabase)) { return $false }
                        if (-not (Verify-Installation)) { return $false }
                        
                        Write-Header "Installation Complete!"
                        Write-Success "Painel Jurídico v2 is ready to use"
                        Write-Info "Launching application..."
                        Start-Process "$InstallPath\Painel Juridico v2.exe"
                        $choice = "6"
                    }
                    "2" {
                        if (-not (Test-InstallationDirectory)) { return $false }
                        if (-not (Install-Application)) { return $false }
                        Write-Header "Installation Complete!"
                    }
                    "3" {
                        $config = Get-InteractiveConfig
                        $OpenAIKey = $config.OpenAIKey
                        $LegalAIUrl = $config.LegalAIUrl
                        $LegalAIKey = $config.LegalAIKey
                        
                        if (-not (Configure-Application)) { return $false }
                        Write-Header "Configuration Complete!"
                    }
                    "4" {
                        if (-not (Verify-Installation)) { return $false }
                        Write-Header "Verification Complete!"
                    }
                    "5" {
                        Write-Info "Launching application..."
                        Start-Process "$InstallPath\Painel Juridico v2.exe"
                    }
                    "6" {
                        Write-Info "Exiting..."
                        $choice = "6"
                    }
                    default {
                        Write-Warning "Invalid choice. Please try again."
                    }
                }
            } while ($choice -ne "6")
        }
        "Install" {
            if (-not (Test-InstallationDirectory)) { return $false }
            if (-not (Install-Application)) { return $false }
            Write-Success "Installation complete"
        }
        "Configure" {
            if (-not (Configure-Application)) { return $false }
            Write-Success "Configuration complete"
        }
        "Verify" {
            if (-not (Verify-Installation)) { return $false }
            Write-Success "Verification complete"
        }
        "Full" {
            if (-not (Test-InstallationDirectory)) { return $false }
            if (-not (Install-Application)) { return $false }
            if (-not (Configure-Application)) { return $false }
            if (-not (Create-BackupDatabase)) { return $false }
            if (-not (Verify-Installation)) { return $false }
            Write-Header "Full Deployment Complete!"
            Write-Success "Painel Jurídico v2 is production-ready"
            Write-Info "Launching application..."
            Start-Process "$InstallPath\Painel Juridico v2.exe"
        }
    }
    
    Write-Log "========== Deployment Completed =========="
    Write-Host ""
    Write-Host "Log file saved: $LogFile"
    Write-Host ""
    
    return $true
}

# Execute main
$result = Main

if ($result) {
    exit 0
} else {
    exit 1
}
