# Deployment Automation Guide - Painel Jurídico v2

**Version**: 2.0.0  
**Date**: 2026-05-19  
**Status**: Production Ready

---

## Quick Start

### Windows Users (Recommended)

**Option 1: Simple Batch Script (Maximum Compatibility)**
```batch
# Navigate to project directory
cd C:\path\to\painel_juridico_v2

# Run batch script
deploy.bat
```

**Option 2: PowerShell Script (Advanced Features)**
```powershell
# Navigate to project directory
cd C:\path\to\painel_juridico_v2

# Enable script execution if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run PowerShell script
.\deploy.ps1
```

---

## Deployment Scripts Overview

### 1. deploy.bat (Windows Command Prompt)

**Best for**: Maximum compatibility, all Windows versions 7+

**File**: `deploy.bat`

**Features**:
- ✅ Works on Windows 7, 8, 10, 11
- ✅ No PowerShell required
- ✅ Interactive menu
- ✅ Automatic logging
- ✅ Step-by-step guidance

**Usage**:
```batch
# Run from command prompt
deploy.bat
```

**Menu Options**:
1. **Full Installation** - Complete setup and launch
2. **Install Only** - Copy files and build executable
3. **Configure Only** - Setup API keys and settings
4. **Verify Installation** - Test existing setup
5. **Launch Application** - Start the application
6. **Exit** - Close deployment script

**Log File**:
- Location: Same directory as script
- Format: `deploy_YYYYMMDD_HHMM.log`
- Contains: All deployment steps and errors

---

### 2. deploy.ps1 (Windows PowerShell)

**Best for**: Advanced automation, scheduled deployments, scripting

**File**: `deploy.ps1`

**Features**:
- ✅ PowerShell 7.0+ support
- ✅ Advanced logging and formatting
- ✅ Colored output
- ✅ Parameter support for automation
- ✅ Prerequisite checking
- ✅ Error recovery

**Prerequisites**:
```powershell
# Check PowerShell version
$PSVersionTable.PSVersion  # Should be 7.0+

# Enable script execution (first time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Usage - Interactive Mode**:
```powershell
# Navigate to project directory
cd C:\path\to\painel_juridico_v2

# Run with interactive menu
.\deploy.ps1
```

**Usage - Command Line Mode**:
```powershell
# Full installation (unattended)
.\deploy.ps1 -Mode Full -InstallPath "C:\Program Files\Painel_Juridico" -OpenAIKey "sk-..." -Verbose

# Installation only
.\deploy.ps1 -Mode Install

# Configuration only
.\deploy.ps1 -Mode Configure -OpenAIKey "sk-..."

# Verification only
.\deploy.ps1 -Mode Verify

# With all options
.\deploy.ps1 -Mode Full `
    -InstallPath "C:\Apps\Painel" `
    -OpenAIKey "sk-your-key-here" `
    -LegalAIUrl "https://api.legalai.com" `
    -LegalAIKey "your-key" `
    -Verbose
```

**Parameters**:
```
-Mode (string)
    Valid values: Interactive, Install, Configure, Verify, Full
    Default: Interactive
    Example: -Mode Full

-InstallPath (string)
    Installation directory path
    Default: C:\Program Files\Painel_Juridico
    Example: -InstallPath "D:\Apps\Painel"

-OpenAIKey (string)
    OpenAI API key for AI features
    Default: (empty)
    Example: -OpenAIKey "sk-..."

-LegalAIUrl (string)
    Legal AI API URL
    Default: (empty)
    Example: -LegalAIUrl "https://api.legalai.com"

-LegalAIKey (string)
    Legal AI API key
    Default: (empty)
    Example: -LegalAIKey "your-key"

-SkipBackup (switch)
    Skip initial database backup
    Default: False
    Example: -SkipBackup

-Verbose (switch)
    Enable verbose output
    Default: False
    Example: -Verbose
```

**Log File**:
- Location: Same directory as script
- Format: `deploy_YYYYMMDD_HHMM.log`
- Contains: Detailed deployment log with timestamps

---

## Deployment Scenarios

### Scenario 1: Single User Installation

**Use Case**: Individual lawyer, single machine

**Steps**:
1. Run: `deploy.bat` (or `.\deploy.ps1`)
2. Choose: `1) Full Installation`
3. Enter: Installation path (or accept default)
4. Enter: OpenAI API key (or skip)
5. Wait for completion
6. Application launches automatically

**Time**: ~5-10 minutes (depending on internet speed)

**Result**: 
- Application installed
- Desktop shortcut created
- Database initialized
- Ready to use

---

### Scenario 2: Multiple User Deployment (Network)

**Use Case**: Law firm with 5-20 users

**Steps**:
1. Create portable version:
   ```powershell
   .\deploy.ps1 -Mode Install -InstallPath "D:\Network_Share\Painel_Juridico"
   ```

2. Copy to network share:
   ```powershell
   Copy-Item -Path "D:\Network_Share\Painel_Juridico" -Destination "\\SERVER\shared\apps\" -Recurse
   ```

3. Each user runs:
   ```batch
   \\SERVER\shared\apps\Painel_Juridico\launch.bat
   ```

**Result**:
- Shared installation
- Each machine has local database
- Centralized updates
- Individual backups

---

### Scenario 3: Automated Enterprise Deployment

**Use Case**: Large firm, Group Policy deployment

**Steps**:
1. Build portable package:
   ```powershell
   .\deploy.ps1 -Mode Full -InstallPath "C:\Program Files\Painel_Juridico" -OpenAIKey "sk-..." -SkipBackup -Verbose
   ```

2. Create deployment script:
   ```batch
   REM Deploy to all machines via Group Policy
   Painel_Juridico_v2_Setup.exe /S /D=C:\Program Files\Painel_Juridico
   ```

3. Configure Group Policy:
   - Computer Config → Software Installation → New → Package
   - Select installer
   - Deploy to OUs

**Result**:
- Automatic deployment to all machines
- Consistent configuration
- Centralized management
- Minimal user interaction

---

### Scenario 4: Unattended Installation (Server)

**Use Case**: Automated setup without user interaction

**PowerShell**:
```powershell
# Set environment variables
$env:OPENAI_KEY = "sk-your-key"
$env:LEGAL_AI_URL = "https://api.legalai.com"

# Run deployment
.\deploy.ps1 -Mode Full `
    -InstallPath "C:\Painel_Juridico" `
    -OpenAIKey $env:OPENAI_KEY `
    -Verbose

# Check result
if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful"
} else {
    Write-Host "Deployment failed"
}
```

**Batch**:
```batch
REM Set variables
set OPENAI_KEY=sk-your-key
set INSTALL_PATH=C:\Painel_Juridico

REM Run batch deployment
deploy.bat

REM Check log
if exist "%INSTALL_PATH%\.env" (
    echo Deployment successful
) else (
    echo Deployment failed
)
```

---

## Troubleshooting

### Issue: "Python not found"

**Cause**: Python not installed or not in PATH

**Solution**:
1. Install Python 3.9+: https://www.python.org/downloads/
2. Enable "Add Python to PATH" during installation
3. Restart terminal
4. Verify: `python --version`

---

### Issue: "Access denied" when installing

**Cause**: Insufficient permissions

**Solution**:
1. Right-click script → "Run as administrator"
2. Or in PowerShell: `Start-Process powershell -Verb RunAs`
3. Then: `.\deploy.ps1`

---

### Issue: "Cannot be loaded because running scripts is disabled"

**Cause**: PowerShell execution policy

**Solution**:
```powershell
# Check policy
Get-ExecutionPolicy

# Set policy (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Issue: "Build failed" during installation

**Cause**: PyInstaller failed to build executable

**Solution**:
```powershell
# Install/upgrade PyInstaller
pip install --upgrade pyinstaller

# Clear cache
rm -r build
rm -r dist

# Try again
.\deploy.ps1 -Mode Install -Verbose
```

---

### Issue: Application won't start after installation

**Cause**: Database initialization error

**Solution**:
1. Delete database: `rm data\painel_juridico.db`
2. Run verification: `python verify_setup.py`
3. Launch application

---

### Issue: Configuration file not created

**Cause**: Permission issue or installation path error

**Solution**:
1. Verify installation path exists
2. Check file permissions: `icacls C:\Program Files\Painel_Juridico`
3. Grant write permissions if needed
4. Re-run configuration: `.\deploy.ps1 -Mode Configure`

---

## Configuration Management

### After Installation

**Edit Configuration**:
```powershell
# Edit .env file
notepad "C:\Program Files\Painel_Juridico\.env"
```

**Configuration Options**:
```env
# Database
DATABASE_PATH=./data/painel_juridico.db

# API Keys
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4.1

# Application
APP_ENV=production
LOG_LEVEL=INFO
DEBUG=False
ENABLE_AI_FEATURES=True

# Backup
BACKUP_RETENTION_DAYS=30
AUTO_BACKUP_ENABLED=True
BACKUP_TIME=23:00

# Performance
DATABASE_TIMEOUT=10.0
MAX_QUERY_TIMEOUT=30.0
CONNECTION_POOL_SIZE=5
```

### Update API Keys

**Before**:
1. Stop application
2. Edit `.env` file
3. Update API keys
4. Restart application

**Alternative**:
```powershell
# Update via script
$envPath = "C:\Program Files\Painel_Juridico\.env"
(Get-Content $envPath) -replace 'OPENAI_API_KEY=.*', 'OPENAI_API_KEY=sk-new-key' | Set-Content $envPath
```

---

## Verification

### After Deployment

**Run Verification Script**:
```powershell
# Verify installation
python verify_setup.py
```

**Manual Verification**:
```powershell
# Check executable
Test-Path "C:\Program Files\Painel_Juridico\Painel Juridico v2.exe"

# Check configuration
Test-Path "C:\Program Files\Painel_Juridico\.env"

# Check data directory
Test-Path "C:\Program Files\Painel_Juridico\data"

# Launch application
Start-Process "C:\Program Files\Painel_Juridico\Painel Juridico v2.exe"
```

**Expected Results**:
- ✅ Executable file exists
- ✅ Configuration file exists
- ✅ Data directory exists
- ✅ Application launches without errors
- ✅ Dashboard displays
- ✅ Database initializes (~3 seconds first launch)

---

## Automation Examples

### Schedule Daily Backups

**PowerShell Task**:
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "backup_scheduler.py" -WorkingDirectory "C:\Program Files\Painel_Juridico"
$trigger = New-ScheduledTaskTrigger -Daily -At "23:00"
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "Painel Daily Backup" -Action $action -Trigger $trigger -Principal $principal
```

### Deploy to Multiple Machines

**PowerShell Script**:
```powershell
# computers.txt contains list of computer names
Get-Content "computers.txt" | ForEach-Object {
    Write-Host "Deploying to $_..."
    
    Invoke-Command -ComputerName $_ -ScriptBlock {
        Set-Location C:\Temp
        .\deploy.ps1 -Mode Full -InstallPath "C:\Program Files\Painel_Juridico"
    }
    
    Write-Host "Completed: $_"
}
```

---

## Performance Tips

### Optimization

**Installation**:
- Use SSD for faster installation
- Close antivirus during build (temporarily)
- Use PowerShell for faster execution

**Post-Installation**:
- Run: `python -m compileall .` (pre-compile Python)
- Add database indexes (see ADMIN_GUIDE.md)
- Enable WAL mode for SQLite (see PRODUCTION_SERVER_SETUP.md)

---

## Support & Documentation

| Task | Script | Document |
|------|--------|----------|
| Basic installation | `deploy.bat` | QUICK_START.md |
| Advanced installation | `deploy.ps1` | PRODUCTION_SERVER_SETUP.md |
| Post-deployment | `verify_setup.py` | ADMIN_GUIDE.md |
| Operations | `health_monitor.py` | ADMIN_GUIDE.md |
| Architecture | - | DEPLOYMENT_PLAN.md |

---

## Checklist

### Pre-Deployment
- [ ] Python 3.9+ installed
- [ ] Administrator access (optional but recommended)
- [ ] 500 MB disk space free
- [ ] Internet connection (for package downloads)
- [ ] OpenAI API key (optional, for AI features)

### During Deployment
- [ ] Choose appropriate deployment mode
- [ ] Enter installation path (or accept default)
- [ ] Enter API keys if available
- [ ] Wait for completion
- [ ] Review deployment log

### Post-Deployment
- [ ] Verify installation: `python verify_setup.py`
- [ ] Test application launch
- [ ] Test core features (add client, case, generate PDF)
- [ ] Check backup creation
- [ ] Review configuration: `notepad .env`

---

## Exit Codes

**PowerShell**:
```
0 = Success
1 = Failure
```

**Batch**:
```
0 = Success
1 = Failure
```

**Usage in Scripts**:
```powershell
.\deploy.ps1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Success"
} else {
    Write-Host "Failed"
}
```

---

## Advanced Usage

### Custom Installation Path

**PowerShell**:
```powershell
.\deploy.ps1 -Mode Full -InstallPath "D:\MyApps\Painel_Juridico"
```

**Batch**:
```batch
REM When prompted, enter custom path:
D:\MyApps\Painel_Juridico
```

### Headless Installation

**PowerShell**:
```powershell
# No interactive prompts
.\deploy.ps1 -Mode Full `
    -InstallPath "C:\Painel_Juridico" `
    -OpenAIKey "sk-..." `
    -SkipBackup
```

### With Logging

**PowerShell**:
```powershell
# Save output to file
.\deploy.ps1 -Mode Full -Verbose | Tee-Object -FilePath deployment.log
```

**Batch**:
```batch
REM Automatic logging (included in script)
REM Check: deploy_YYYYMMDD_HHMM.log
```

---

## Frequently Asked Questions

**Q: Can I install on a different drive?**  
A: Yes, specify path during installation: `D:\Painel_Juridico`

**Q: How do I uninstall?**  
A: Delete installation directory or use "Add/Remove Programs"

**Q: Can I run multiple instances?**  
A: Not recommended. Install in separate directories if needed.

**Q: How do I update?**  
A: Re-run deployment script with new version files

**Q: Where is my data stored?**  
A: In `installation_path\data\` directory

**Q: Can I move the installation?**  
A: Yes, move entire folder. Database moves with it.

**Q: How do I backup?**  
A: Use Dashboard → Backup, or copy `data/` folder

**Q: What if deployment fails?**  
A: Check `deploy_*.log` file for error details

---

## Version Information

- **Script Version**: 2.0.0
- **Release Date**: 2026-05-19
- **Status**: Production Ready
- **Compatibility**: Windows 7, 8, 10, 11

---

## Support

For issues:
1. Check deployment log file
2. Review troubleshooting section above
3. See ADMIN_GUIDE.md for detailed solutions
4. Check application help menu

---

**Successfully deploying Painel Jurídico v2 is simple with these automation scripts. Choose your deployment method and follow the on-screen guidance.**
