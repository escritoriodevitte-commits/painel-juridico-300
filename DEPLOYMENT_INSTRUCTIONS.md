# Painel Jurídico v2 - Deployment Instructions

**Version**: 2.0.0  
**Release Date**: 2026-05-19  
**Status**: Production-Ready  
**Last Updated**: 2026-05-19

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Option A: Windows Installer (Enterprise)](#option-a-windows-installer-enterprise)
3. [Option B: Portable Version (Field/Remote)](#option-b-portable-version-fieldremote)
4. [Option C: Developer Setup (Customization)](#option-c-developer-setup-customization)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Configuration & First Run](#configuration--first-run)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance & Updates](#maintenance--updates)

---

## Quick Start

Choose your deployment method based on your needs:

| Method | Use Case | Installation Time | Complexity |
|--------|----------|-------------------|------------|
| **Windows Installer** | Enterprise, IT-managed | 5-10 min | Low |
| **Portable Version** | Remote offices, USB distribution | 2 min | Minimal |
| **Developer Setup** | Customization, development | 10-15 min | Medium |

---

## Option A: Windows Installer (Enterprise)

### Best For
- Enterprise deployments
- IT-managed installations
- Users who want Add/Remove Programs integration
- Network distribution via Group Policy

### Prerequisites
- Windows 10 or 11
- Administrator rights (for installation)
- ~500 MB free disk space
- Internet connection (optional, for AI features)

### Step 1: Build the Installer

**On your development machine:**

```powershell
# Navigate to project directory
cd C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2

# Install PyInstaller
pip install pyinstaller>=6.0

# Build executable
pyinstaller --onefile --windowed --name "Painel Juridico v2" main.py

# Verify executable created
ls dist\
```

Expected output: `Painel Juridico v2.exe` in `dist/` folder

### Step 2: Create NSIS Installer (Optional, Professional)

**For professional Windows installer:**

```powershell
# Install NSIS (Nullsoft Scriptable Install System)
# Download from: https://nsis.sourceforge.io/Download

# Create installer script (installer.nsi):
# See ADMIN_GUIDE.md for full NSIS template

# Build installer
makensis installer.nsi
```

Output: `Painel_Juridico_v2_Setup.exe`

### Step 3: Deployment

**On target machines:**

```batch
REM Option 1: Using PyInstaller exe directly
"Painel Juridico v2.exe"

REM Option 2: Using NSIS installer
Painel_Juridico_v2_Setup.exe

REM Option 3: Silent installation (for IT deployment)
Painel_Juridico_v2_Setup.exe /S /D=C:\Program Files\Painel_Juridico
```

### Step 4: Configure API Keys (Optional)

```batch
REM Create .env file in installation directory
cd "C:\Program Files\Painel Juridico"
echo OPENAI_API_KEY=sk-your-key-here > .env
echo LEGAL_AI_API_URL=https://api.legalai.com >> .env
```

### Step 5: First Launch

```batch
REM Run application
"C:\Program Files\Painel Juridico\Painel Juridico v2.exe"

REM Database initializes automatically (~3 seconds)
REM Application opens with Dashboard visible
REM 51 legal references pre-loaded
```

**Verification**: 
- Database file created: `data/painel_juridico.db`
- Backup folder created: `data/backups/`
- Application loads successfully

---

## Option B: Portable Version (Field/Remote)

### Best For
- Remote offices without IT support
- USB-portable distribution
- Field workers
- Zero-installation requirement
- Quick testing and evaluation

### Prerequisites
- Windows 10+ or any OS with Python 3.9+
- No administrator rights needed
- ~500 MB free space
- Optional: Python 3.9+ (if using developer version)

### Step 1: Create Portable Package

**On your development machine:**

```powershell
# Build executable (as above)
pyinstaller --onefile --windowed --name "Painel Juridico v2" main.py

# Create portable directory structure
mkdir painel_juridico_portable
mkdir painel_juridico_portable\data
mkdir painel_juridico_portable\exports_output

# Copy executable
cp dist\"Painel Juridico v2.exe" painel_juridico_portable\

# Create README
@"
# Painel Jurídico v2 - Portable Version

## Installation
1. Extract this folder anywhere (Desktop, USB drive, etc.)
2. Double-click "Painel Juridico v2.exe"
3. Database initializes automatically

## First Run
- Takes ~3 seconds on first launch
- Database created in 'data' folder
- 51 legal references loaded
- No installation required

## Configuration (Optional)
1. Create file: .env
2. Add: OPENAI_API_KEY=sk-your-key-here
3. Restart application

## Support
- See QUICK_START.md for usage
- See ADMIN_GUIDE.md for troubleshooting
"@ | Out-File -Encoding UTF8 painel_juridico_portable\README.txt

# Create ZIP archive
Compress-Archive -Path painel_juridico_portable -DestinationPath painel_juridico_v2_portable.zip
```

### Step 2: Distribute Portable Version

```powershell
# Option 1: Email or network share
cp painel_juridico_v2_portable.zip "\\network\share\apps\"

# Option 2: USB drive
cp painel_juridico_v2_portable.zip "E:\apps\"

# Option 3: Cloud storage (Dropbox, OneDrive, Google Drive)
```

### Step 3: User Installation (On Target Machine)

1. **Extract the ZIP**
   - Right-click `painel_juridico_v2_portable.zip`
   - Select "Extract All..."
   - Choose destination folder

2. **Run the Application**
   - Navigate to extracted folder
   - Double-click `Painel Juridico v2.exe`
   - Wait for database initialization (~3 seconds)

3. **First Launch**
   - Application opens with Dashboard
   - Database file created in `data/` folder
   - Ready to use immediately

**No installation, no admin rights, no dependencies needed!**

### Step 4: Optional Configuration

**To enable AI features:**

1. Open folder: `painel_juridico_v2_portable\`
2. Create file: `.env` (use Notepad)
3. Add content:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
4. Save and close Notepad
5. Restart application

---

## Option C: Developer Setup (Customization)

### Best For
- Customization and development
- Internal deployment
- Testing new features
- Modifying code
- Integration with other systems

### Prerequisites
- Python 3.9 or later
- Git installed
- Virtual environment support
- Administrator rights (not required)
- ~2 GB disk space

### Step 1: Clone or Download Project

```powershell
# Option 1: Clone from Git
git clone https://github.com/your-repo/painel_juridico_v2.git
cd painel_juridico_v2

# Option 2: Download ZIP
# Download from GitHub → unzip → open folder

cd painel_juridico_v2
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

Expected packages:
- customtkinter>=5.2.0
- reportlab>=4.0
- openai>=1.0

### Step 4: Verify Installation

```powershell
# Run verification script
python verify_setup.py

# Expected output:
# ✅ PASS: Database
# ✅ PASS: Calculator
# ✅ PASS: Generator
# ✅ PASS: Analytics
# ✅ PASS: Backup
# RESULT: 5/5 modules working correctly
```

### Step 5: Run Application

```powershell
# Launch application
python main.py

# Application opens with GUI
# Database initializes on first run
# Dashboard displays
```

### Step 6: Optional - Configure API Keys

**Create `.env` file in project root:**

```powershell
# Using PowerShell
@"
OPENAI_API_KEY=sk-your-key-here
LEGAL_AI_API_URL=https://api.legalai.com
LEGAL_AI_API_KEY=your-key-here
DATABASE_PATH=./data/painel_juridico.db
APP_ENV=production
LOG_LEVEL=INFO
DEBUG=False
"@ | Out-File -Encoding UTF8 .env

# Using Notepad
# 1. Open Notepad
# 2. Paste content above
# 3. Save as: .env (in project root folder)
# 4. Restart application
```

### Step 7: Run Tests

```powershell
# Run all tests
python test_final.py

# Run specific test suite
python tests/test_validators.py
python tests/test_phase2_features.py
python test_calculadora.py

# Expected: 99+ tests passing
```

### Step 8: Build Production Executable (Optional)

```powershell
# Install PyInstaller
pip install pyinstaller>=6.0

# Build executable
pyinstaller --onefile --windowed --name "Painel Juridico v2" main.py

# Executable in: dist\Painel Juridico v2.exe
```

---

## Post-Deployment Verification

### Universal Verification (All Methods)

After installation, run verification from command line:

```bash
# Navigate to installation directory
cd "C:\Program Files\Painel Juridico"  # Or portable folder, or project root

# Run verification
python verify_setup.py

# Expected output (100% pass):
# ======================================================================
# PAINEL JURÍDICO v2 - CORE FUNCTIONALITY VERIFICATION
# ======================================================================
# 1. DATABASE INITIALIZATION
#    ✅ Database initialized successfully
#    ✅ Legal references loaded: 51
# 2. CALCULATOR MODULE
#    ✅ Calculator module working
# 3. DOCUMENT GENERATOR MODULE
#    ✅ Document generator initialized
#    ✅ Supported document types: 10
# 4. ANALYTICS ENGINE
#    ✅ Analytics engine initialized
# 5. DATABASE BACKUP & RESTORE
#    ✅ Database backup created successfully
#    ✅ Backup contains 9 tables
# ======================================================================
# RESULT: 5/5 modules working correctly
# 🎉 APPLICATION READY FOR PRODUCTION
```

### Manual Verification

**Launch application and check:**

1. **Dashboard Screen** (appears on startup)
   - [ ] Application window opens
   - [ ] Dashboard shows empty statistics
   - [ ] Database initialized message appears (or silently completes)

2. **Database Initialization**
   - [ ] Database file exists: `data/painel_juridico.db`
   - [ ] Backup folder exists: `data/backups/`
   - [ ] 51 legal references loaded

3. **Sidebar Navigation**
   - [ ] All menu items visible
   - [ ] GESTÃO section (7 items)
   - [ ] INTELIGÊNCIA section (5 items)
   - [ ] CONFIGURAÇÕES section (2 items)

4. **Add Test Data**
   - [ ] Click "Clientes" → "Novo Cliente"
   - [ ] Add test client
   - [ ] Click "Processos" → "Novo Processo"
   - [ ] Add test process
   - [ ] Verify data appears in lists

---

## Configuration & First Run

### API Key Configuration (Optional)

**To enable AI-powered document generation:**

1. Get OpenAI API key
   - Visit: https://platform.openai.com/api-keys
   - Create new API key
   - Copy key (starts with `sk-`)

2. Configure in Painel Jurídico
   - Click "Configurações" → "API OpenAI"
   - Paste API key
   - Click "Salvar"
   - Status changes to "IA: Conectada (GPT-4.1)"

3. Or create `.env` file:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

### Database Location

**Default location:**
- Windows: `{installation_folder}\data\painel_juridico.db`
- Linux/Mac: `./data/painel_juridico.db`

**Custom location via .env:**
```
DATABASE_PATH=/custom/path/database.db
```

### Backup Configuration

**Automatic backups:**
- Location: `data/backups/painel_juridico_YYYY-MM-DD.json`
- Timing: At application startup
- Retention: Last 30 days

**Manual backup:**
- Menu: Dashboard → Backup Database
- Format: JSON (recommended) or CSV
- Size: ~30-50 KB per backup

---

## Troubleshooting

### Application Won't Start

**Symptom**: Error on launch or no window appears

**Solution**:
```powershell
# 1. Delete database and restart (recreates on launch)
rm data\painel_juridico.db

# 2. Check Python version (if developer version)
python --version  # Should be 3.9+

# 3. Check dependencies (if developer version)
pip list
pip install -r requirements.txt

# 4. Verify database file permissions
# Right-click file → Properties → ensure "Read-only" is NOT checked
```

### "Database Locked" Error

**Symptom**: Cannot access application or data

**Solution**:
```powershell
# 1. Close all instances of application
taskkill /IM "Painel Juridico v2.exe" /F

# 2. Restart application

# 3. If persists: Restart computer
Restart-Computer
```

### API Key Not Working

**Symptom**: AI features not generating documents

**Solution**:
```powershell
# 1. Verify API key in .env file
cat .env | grep OPENAI_API_KEY

# 2. Check OpenAI account has valid billing
# Visit: https://platform.openai.com/account/billing/overview

# 3. Verify API key starts with "sk-"
# Regenerate if unsure: https://platform.openai.com/api-keys

# 4. Restart application
```

### Slow Performance (>5000 processes)

**Symptom**: Dashboard loads slowly, searches lag

**Solution**:
```powershell
# 1. Archive old processes (see ADMIN_GUIDE.md)

# 2. Optimize database
python -c "import sqlite3; sqlite3.connect('data/painel_juridico.db').execute('VACUUM')"

# 3. Add database indexes (see ADMIN_GUIDE.md)
```

### Data Loss / Corruption

**Symptom**: Database file corrupted or data missing

**Solution**:
```powershell
# 1. Stop application

# 2. Backup corrupted file
copy data\painel_juridico.db data\painel_juridico.db.corrupt

# 3. Delete current database
del data\painel_juridico.db

# 4. Restore from backup
python -c "from core.database import restore_database; restore_database('backup_file.json')"

# 5. Start application (recreates fresh database if no backup)
```

---

## Maintenance & Updates

### Regular Maintenance

**Daily**:
- Monitor for errors in application
- Check backup completion

**Weekly**:
- Review database size (alert if >500MB)
- Check for error logs

**Monthly**:
```powershell
# Optimize database
python -c "import sqlite3; sqlite3.connect('data/painel_juridico.db').execute('VACUUM')"

# Health check
python health_report.py

# Create full backup
python -c "from core.database import backup_database; backup_database('painel_juridico_backup_$(date +%Y%m%d).json')"
```

**Quarterly**:
- Full backup to secure storage
- Test restore procedure
- Review performance metrics
- Plan updates

### Updating to New Version

**Before Update**:
```powershell
# 1. Backup database
python -c "from core.database import backup_database; backup_database('backup_before_update.json')"

# 2. Stop application
taskkill /IM "Painel Juridico v2.exe" /F

# 3. Keep backup file safe
```

**Update Process**:
```powershell
# 1. Download new version

# 2. For Windows Installer:
Painel_Juridico_v2_Setup.exe /S /D=C:\Program Files\Painel_Juridico

# 2. For Portable: Extract new zip, keep old data/ folder

# 2. For Developer:
git pull
pip install -r requirements.txt
```

**After Update**:
```powershell
# 1. Start application

# 2. Verify functionality
python verify_setup.py

# 3. Check database integrity
python health_report.py

# 4. Delete backup (if update successful)
rm backup_before_update.json
```

### Getting Help

**For Users**:
1. Check QUICK_START.md (troubleshooting section)
2. Check application Help menu
3. Review FAQ
4. Contact administrator

**For Administrators**:
1. Check ADMIN_GUIDE.md (operations section)
2. Run health_report.py
3. Review DEPLOYMENT_PLAN.md
4. Check troubleshooting guide below

**For Developers**:
1. Check code docstrings
2. Review DEPLOYMENT_PLAN.md (architecture)
3. Run tests: `python test_final.py`
4. Check git history: `git log`

---

## Next Steps

### Immediately After Deployment

1. ✅ **Verify Installation**
   ```bash
   python verify_setup.py
   ```

2. ✅ **Test Core Features**
   - Add a client (Clientes → Novo Cliente)
   - Add a process (Processos → Novo Processo)
   - View dashboard (Dashboard)

3. ✅ **Configure Optional Features**
   - Add OpenAI API key (if using AI)
   - Set database backup schedule
   - Configure monitoring

4. ✅ **Train Users**
   - Share QUICK_START.md
   - Explain main sections
   - Demonstrate common tasks

### First Week

- ✅ Monitor for errors
- ✅ Verify daily backups
- ✅ Confirm data entry works
- ✅ Test backup/restore procedure

### First Month

- ✅ Review application logs
- ✅ Optimize database (if needed)
- ✅ Full backup to secure storage
- ✅ Gather user feedback
- ✅ Plan Phase 3 features

---

## Support Resources

| Document | Purpose | Audience |
|----------|---------|----------|
| QUICK_START.md | Installation & basic usage | End users |
| README.md | Feature overview | Everyone |
| ADMIN_GUIDE.md | Operations & maintenance | Administrators |
| DEPLOYMENT_PLAN.md | Technical architecture | Developers |
| DEPLOYMENT_SUMMARY.md | Strategic overview | Managers |
| DOCUMENTATION_INDEX.md | Navigation guide | Everyone |
| PRODUCTION_READINESS_REPORT.md | Verification results | Stakeholders |
| verify_setup.py | Automated verification | Technical |

---

## Quick Reference

### Commands (Windows PowerShell)

```powershell
# Verify installation
python verify_setup.py

# Run tests
python test_final.py

# Backup database
python -c "from core.database import backup_database; backup_database('backup.json')"

# Restore database
python -c "from core.database import restore_database; restore_database('backup.json')"

# Health check
python health_report.py

# Database optimization
python -c "import sqlite3; sqlite3.connect('data/painel_juridico.db').execute('VACUUM')"

# Build executable
pip install pyinstaller
pyinstaller --onefile --windowed --name "Painel Juridico v2" main.py
```

---

## Deployment Success Criteria

✅ Application launches without errors  
✅ Database initializes on first run  
✅ All 5 core modules verified (verify_setup.py)  
✅ Dashboard displays with empty statistics  
✅ Can add clients and processes  
✅ Backup/restore working  
✅ All menu items accessible  

---

## Version Information

- **Application**: Painel Jurídico v2
- **Version**: 2.0.0
- **Release Date**: 2026-05-19
- **Status**: Production-Ready
- **Support**: See documentation files

---

**Installation Complete! Welcome to Painel Jurídico v2.**

For questions or issues, consult the appropriate documentation guide or run `python verify_setup.py` to verify your installation.
