# Local Verification & Application Launch Guide

**Version**: 2.0.0  
**Date**: 2026-05-19  
**Purpose**: Final verification before remote push  
**Time Required**: 10-15 minutes

---

## ✅ Pre-Launch Checklist

Before running the application, verify your environment:

```powershell
# Navigate to project directory
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# Check Python installation
python --version          # Should be 3.9 or higher

# Check pip
pip --version             # Should be present

# Check git status
git status                # Should show "nothing to commit, working tree clean"

# Check latest commit
git log --oneline -1      # Should show "Add production deployment automation scripts..."

# Check git tags
git tag -l                # Should show "v2.0.0"
```

---

## 🚀 Run Application Locally

### Option 1: Direct Python Execution (Simplest)

```powershell
# Navigate to project directory
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# Run the application directly
python main.py
```

**Expected Result:**
- Application window opens
- Dashboard displays with "Painel Jurídico v2"
- No errors in console
- Database initializes (~3 seconds first run)

---

### Option 2: Using Virtual Environment (Recommended for Development)

```powershell
# Navigate to project directory
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Deactivate when done (optional)
# deactivate
```

---

### Option 3: Using Batch Launcher Script

```powershell
# The launch.bat script was created during automation setup
# You can run it directly:

.\launch.bat

# Or double-click launch.bat from File Explorer
```

---

## 🧪 Run Verification Tests

### Comprehensive Verification

```powershell
# Navigate to project directory
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# Run complete verification
python verify_setup.py
```

**Expected Output:**
```
======================================================================
PAINEL JURÍDICO v2 - CORE FUNCTIONALITY VERIFICATION
======================================================================
1. DATABASE INITIALIZATION
   ✅ Database initialized successfully
   ✅ Legal references loaded: 51
2. CALCULATOR MODULE
   ✅ Calculator module working
3. DOCUMENT GENERATOR MODULE
   ✅ Document generator initialized
   ✅ Supported document types: 10
4. ANALYTICS ENGINE
   ✅ Analytics engine initialized
5. DATABASE BACKUP & RESTORE
   ✅ Database backup created successfully
   ✅ Backup contains 9 tables
======================================================================
RESULT: 5/5 modules working correctly
🎉 APPLICATION READY FOR PRODUCTION
```

---

### Run Unit Tests

```powershell
# Navigate to project directory
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# Run all tests
python test_final.py

# Or run specific test modules
python -m pytest test_validators.py -v
python -m pytest test_integration.py -v
python -m pytest test_phase2_features.py -v
```

**Expected Result:**
- All tests passing (99+ tests)
- 100% success rate
- No errors or warnings

---

### Health Check

```powershell
# Navigate to project directory
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# Run health report
python health_report.py
```

**Expected Output:**
```
=== Painel Jurídico v2 - Health Report ===
Generated: 2026-05-19T02:11:04

📊 Database Size: 0.15 MB ✅
🔍 Integrity: ok
📋 Record Counts:
   clientes: 0
   judges: 0
   lawsuits: 0
   settlements: 0
   legal_references: 51
   negotiation_params: 0
   generated_pieces: 0

💾 Latest Backups (1 total):
   painel_juridico_initial.json

💿 Disk Space: 450.0 GB free (85.0%)
```

---

## 📱 Application Features to Test

### 1. Dashboard
- [ ] Application launches without errors
- [ ] Dashboard screen displays
- [ ] Menu sidebar visible
- [ ] Statistics show (empty for new database)

### 2. Add Test Data
- [ ] Click "Clientes" → "Novo Cliente"
- [ ] Enter test client name
- [ ] Click "Salvar"
- [ ] Client appears in list
- [ ] Click "Processos" → "Novo Processo"
- [ ] Create test case linked to client
- [ ] Case appears in list

### 3. Navigation
- [ ] All menu items clickable:
  - [ ] Dashboard
  - [ ] Clientes
  - [ ] Processos
  - [ ] Calculadora
  - [ ] Gerador
  - [ ] Buscador
  - [ ] Dashboard Inteligência
  - [ ] Configurações
- [ ] No error messages
- [ ] Smooth transitions

### 4. Backup Function
- [ ] Menu → "Backup Database"
- [ ] Select "JSON" format
- [ ] Backup file created in `data/backups/`
- [ ] File contains valid JSON

### 5. Search Function
- [ ] Search for test data
- [ ] Results display correctly
- [ ] Filters work

### 6. Calculator (if AI enabled)
- [ ] Click "Calculadora"
- [ ] Select case type
- [ ] Calculate debts
- [ ] Results display

---

## 🔧 Troubleshooting Local Launch

### Issue: "Python not found"

**Solution:**
```powershell
# Check if Python is installed
python --version

# If not found, install Python 3.9+
# Download from https://www.python.org/downloads/
# Make sure "Add Python to PATH" is checked during install

# Restart PowerShell and try again
python --version
```

### Issue: "ModuleNotFoundError"

**Solution:**
```powershell
# Install missing dependencies
pip install -r requirements.txt

# Or install individually
pip install customtkinter>=5.2.0
pip install reportlab>=4.0
pip install openai>=1.0
```

### Issue: "Database locked" error

**Solution:**
```powershell
# Close all instances of the application
taskkill /IM python.exe /F

# Wait 5 seconds
Start-Sleep -Seconds 5

# Delete corrupted database if needed
Remove-Item data/painel_juridico.db

# Run application again
python main.py
```

### Issue: "Port already in use" (if running as service)

**Solution:**
```powershell
# Find process using the port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual PID)
taskkill /PID <PID> /F

# Restart application
python main.py
```

### Issue: "Permission denied" on files

**Solution:**
```powershell
# Check file permissions
icacls data

# Grant write permissions if needed
icacls data /grant:r "%USERNAME%:M" /T

# Try running application again
python main.py
```

---

## 📊 Verification Checklist

### Before Pushing to Remote

- [ ] **Environment**
  - [ ] Python 3.9+ installed and working
  - [ ] pip available
  - [ ] Git configured
  - [ ] All dependencies installed

- [ ] **Code Quality**
  - [ ] `python verify_setup.py` passes (5/5 modules)
  - [ ] `python test_final.py` passes (99+ tests)
  - [ ] `python health_report.py` shows healthy state
  - [ ] No console errors or warnings

- [ ] **Application**
  - [ ] Application launches without errors
  - [ ] Dashboard displays correctly
  - [ ] Can add test data (clients, cases)
  - [ ] Can search and filter
  - [ ] Backup function works
  - [ ] All menu items accessible

- [ ] **Data Integrity**
  - [ ] Database initializes correctly
  - [ ] 51 legal references loaded
  - [ ] Test data saves and retrieves
  - [ ] Backup files created successfully
  - [ ] No data corruption errors

- [ ] **Git Status**
  - [ ] `git status` shows "nothing to commit, working tree clean"
  - [ ] `git log --oneline -1` shows latest commit
  - [ ] `git tag -l` shows v2.0.0 tag
  - [ ] No uncommitted changes

---

## 🎯 Final Verification Commands (Copy-Paste Ready)

### Quick Verification (5 minutes)

```powershell
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# 1. Check environment
echo "=== Checking Environment ==="
python --version
pip --version
git --version

# 2. Run core verification
echo "`n=== Running Core Verification ==="
python verify_setup.py

# 3. Check git status
echo "`n=== Checking Git Status ==="
git status
git log --oneline -1
git tag -l

# 4. Health check
echo "`n=== Health Check ==="
python health_report.py
```

### Complete Verification (15 minutes)

```powershell
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# 1. Environment
echo "=== ENVIRONMENT CHECK ==="
python --version
pip --version
git --version
git status

# 2. Tests
echo "`n=== RUNNING TESTS ==="
python test_final.py

# 3. Verification
echo "`n=== CORE VERIFICATION ==="
python verify_setup.py

# 4. Health
echo "`n=== HEALTH REPORT ==="
python health_report.py

# 5. Git
echo "`n=== GIT STATUS ==="
git log --oneline -5
git tag -l

echo "`n✅ VERIFICATION COMPLETE"
```

---

## 🚀 Launch Application

### Simple Launch

```powershell
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"
python main.py
```

### Launch with Logging

```powershell
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"
python main.py | Tee-Object -FilePath "app_run.log"
```

### Launch in Background

```powershell
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"
Start-Process python -ArgumentList main.py -WindowStyle Minimized
```

---

## 📝 Testing Workflow

### 1. Initial Verification (2 min)
```powershell
python verify_setup.py
```
✅ Confirms all 5 modules working

### 2. Run Tests (3 min)
```powershell
python test_final.py
```
✅ Confirms 99+ tests passing

### 3. Health Check (1 min)
```powershell
python health_report.py
```
✅ Confirms database and disk space OK

### 4. Launch Application (1 min)
```powershell
python main.py
```
✅ Application starts and displays

### 5. Manual Testing (5 min)
- [ ] Add test client
- [ ] Add test case
- [ ] Search for data
- [ ] Create backup
- [ ] Close application

### 6. Final Verification (1 min)
```powershell
git status
git log --oneline -1
```
✅ Git shows clean working tree, all commits present

---

## ✨ Success Indicators

### Application Launches Successfully
- ✅ No Python errors
- ✅ GUI window opens
- ✅ Dashboard displays
- ✅ Database initializes

### Core Modules Working
- ✅ Database: 51 references loaded
- ✅ Calculator: Performing calculations
- ✅ Generator: Creating documents
- ✅ Analytics: Dashboard metrics
- ✅ Backup: Creating backups

### Tests Passing
- ✅ 99+ tests total
- ✅ 100% success rate
- ✅ No errors or warnings
- ✅ All modules verified

### Data Integrity
- ✅ No corruption errors
- ✅ Test data saves/retrieves
- ✅ Backups created successfully
- ✅ Database size reasonable (<1 MB)

### Ready to Push
- ✅ Git working tree clean
- ✅ All commits present
- ✅ Tag v2.0.0 created
- ✅ No uncommitted changes

---

## 🎓 Verification Output Examples

### Successful verify_setup.py Output
```
PAINEL JURÍDICO v2 - CORE FUNCTIONALITY VERIFICATION
✅ Database initialized successfully
✅ Legal references loaded: 51
✅ Calculator module working
✅ Document generator initialized
✅ Analytics engine initialized
✅ Database backup created successfully
RESULT: 5/5 modules working correctly
🎉 APPLICATION READY FOR PRODUCTION
```

### Successful test_final.py Output
```
test_validators.py ... 23 passed
test_integration.py ... 16 passed
test_phase2_features.py ... 20 passed
test_calculadora.py ... 40 passed
================== 99 passed in 2.34s ==================
```

### Successful Application Launch
```
[Application window opens]
[Dashboard displays with Painel Jurídico v2 title]
[Sidebar shows all menu options]
[No errors in console]
```

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Navigate to project | `cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"` |
| Check Python | `python --version` |
| Install dependencies | `pip install -r requirements.txt` |
| Run verification | `python verify_setup.py` |
| Run tests | `python test_final.py` |
| Health check | `python health_report.py` |
| Launch application | `python main.py` |
| Check git status | `git status` |
| View commits | `git log --oneline -5` |
| View tags | `git tag -l` |

---

## ✅ Ready to Push?

Once you complete this verification and confirm:
- ✅ Application launches successfully
- ✅ verify_setup.py shows 5/5 modules
- ✅ All tests passing (99+)
- ✅ No errors or warnings
- ✅ Git status clean

**Then you're ready to push to a remote repository using the commands in EXACT_PUSH_COMMANDS.md**

---

## 🚀 Next Steps

1. **Run Verification** → `python verify_setup.py`
2. **Run Tests** → `python test_final.py`
3. **Launch Application** → `python main.py`
4. **Test Manually** → Add data, search, backup
5. **Check Git** → `git status`
6. **Push to Remote** → Follow EXACT_PUSH_COMMANDS.md

---

**Status**: ✅ Ready for Local Verification  
**Application**: v2.0.0  
**Date**: 2026-05-19  
**Next**: Follow commands above and launch the application!
