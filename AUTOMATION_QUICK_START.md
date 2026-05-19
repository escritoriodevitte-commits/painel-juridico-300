# Deployment Automation - Quick Start

**3 Easy Steps to Production Deployment**

---

## Step 1: Choose Your Script

### Option A: Batch Script (Simplest, All Windows Versions)
```batch
# Works on Windows 7, 8, 10, 11 - No PowerShell needed
deploy.bat
```

### Option B: PowerShell Script (More Features, Windows 10+)
```powershell
# More control, parameter support, advanced logging
.\deploy.ps1
```

---

## Step 2: Follow Interactive Menu

Both scripts present an interactive menu:

```
1) Full Installation    → Complete setup (RECOMMENDED)
2) Install Only        → Just copy files
3) Configure Only      → Update settings
4) Verify Installation → Test setup
5) Launch Application  → Run app
6) Exit
```

**For most users**: Choose option **1) Full Installation**

---

## Step 3: Complete Configuration

The script will ask for:

1. **Installation Path** (press Enter for default)
   ```
   C:\Program Files\Painel_Juridico
   ```

2. **OpenAI API Key** (optional, skip if you don't have one)
   ```
   sk-your-key-here
   ```

3. **Legal AI Settings** (optional)

4. **Create Backup?** (press Enter for yes)

That's it! Application launches automatically when done.

---

## Total Time

- **First Run**: 5-10 minutes (builds executable)
- **Subsequent Runs**: 1-2 minutes

---

## What Gets Installed

```
C:\Program Files\Painel_Juridico\
├── Painel Juridico v2.exe      (application)
├── .env                         (configuration)
├── data/
│   ├── painel_juridico.db      (database)
│   └── backups/                (automatic backups)
├── exports_output/             (generated files)
└── launch.bat                  (quick launcher)
```

**Desktop Shortcut**: Automatically created for easy launch

---

## Verify Installation

After deployment completes:

```powershell
# Run verification
python verify_setup.py

# Should show:
# ✅ Database: OK
# ✅ Calculator: OK
# ✅ Generator: OK
# ✅ Analytics: OK
# ✅ Backup: OK
# RESULT: 5/5 modules working
```

---

## Launch Application

### After First Installation
Just click desktop shortcut or:
```powershell
start "C:\Program Files\Painel_Juridico\Painel Juridico v2.exe"
```

### Manual Launch
```batch
C:\Program Files\Painel_Juridico\launch.bat
```

---

## Next Steps

1. ✅ **Deployment complete** → Application ready
2. 📖 **Read QUICK_START.md** → Learn basic usage
3. 👥 **Add test client** → Try creating data
4. 📄 **Generate document** → Test PDF creation
5. 💾 **Create backup** → Dashboard → Backup

---

## Troubleshooting

### "Python not found"
→ Install Python 3.9+ from https://www.python.org/downloads/

### "Access denied"
→ Right-click script → "Run as administrator"

### "Cannot load script"
→ Run in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Build failed"
→ Check logs: `deploy_*.log`  
→ Re-run: `.\deploy.ps1 -Mode Install -Verbose`

---

## Support Documents

| Need Help With | See Document |
|---|---|
| Installation issues | DEPLOYMENT_AUTOMATION_GUIDE.md |
| Configuration details | PRODUCTION_SERVER_SETUP.md |
| Advanced automation | DEPLOYMENT_AUTOMATION_GUIDE.md |
| Using the application | QUICK_START.md |
| Administration | ADMIN_GUIDE.md |

---

## Script Exit Codes

```
0 = Success
1 = Failure
```

---

## One-Line Deployment (PowerShell)

For experienced users:

```powershell
.\deploy.ps1 -Mode Full -OpenAIKey "sk-..." -Verbose
```

---

## Deployment Complete! 🎉

Your Painel Jurídico v2 installation is ready.

- **Application**: Running on your system
- **Database**: Initialized and backed up
- **Configuration**: Stored in `.env`
- **Logs**: Available in `deploy_*.log`

**Next**: Open the application and start adding clients and cases!

---

## Version Info

- **Script Version**: 2.0.0
- **Release Date**: 2026-05-19
- **Compatibility**: Windows 7+
- **Status**: Production Ready
