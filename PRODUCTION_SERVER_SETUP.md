# Production Server Setup Guide - Painel Jurídico v2

**Version**: 2.0.0  
**Date**: 2026-05-19  
**Target Audience**: System Administrators, DevOps, IT Staff  
**Deployment Status**: Production Ready

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Server Requirements](#server-requirements)
4. [Installation Methods](#installation-methods)
5. [Configuration Management](#configuration-management)
6. [Database Setup](#database-setup)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Disaster Recovery](#backup--disaster-recovery)
10. [Performance Tuning](#performance-tuning)
11. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Application Stack

```
┌─────────────────────────────────────────────────────────┐
│            Painel Jurídico v2 (Desktop App)             │
├─────────────────────────────────────────────────────────┤
│                     GUI Layer (CustomTkinter)           │
├─────────────────────────────────────────────────────────┤
│  Modules: Validators | Sync | Charts | Search | Backup  │
├─────────────────────────────────────────────────────────┤
│            Database Layer (SQLite / PostgreSQL)         │
├─────────────────────────────────────────────────────────┤
│      External APIs: OpenAI, Legal AI (optional)         │
└─────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **GUI** | CustomTkinter | Desktop interface for lawyers |
| **Database** | SQLite 3.x / PostgreSQL | Case & client data storage |
| **Validators** | Python 3.9+ | Data validation (dates, documents, numbers) |
| **Calculator** | Python | Labor law calculations (CLT 2026) |
| **Document Generator** | ReportLab | PDF document creation |
| **Search** | SQLite FTS | Full-text search across cases |
| **Analytics** | Python | Dashboard metrics & KPIs |
| **External APIs** | OpenAI, Legal AI | Optional AI-powered features |

### Deployment Models

1. **Single Machine** (Recommended for <50 users)
   - Desktop app on individual machines
   - Local SQLite database
   - No server required

2. **Multi-Machine (Network Share)** (100-200 users)
   - Portable version on network share
   - Each machine has local SQLite database
   - Daily backup to network NAS

3. **Centralized Database** (200+ users, advanced)
   - Desktop app clients
   - PostgreSQL server (centralized)
   - Network-based database access
   - See [Advanced: PostgreSQL Setup](#advanced-postgresql-setup)

---

## Pre-Deployment Checklist

### Planning Phase

- [ ] Define deployment scope (# of users, offices, devices)
- [ ] Choose deployment model (single machine, network, server)
- [ ] Identify system administrator
- [ ] Plan backup strategy
- [ ] Evaluate budget for hosting/infrastructure
- [ ] Schedule deployment window (after-hours recommended)
- [ ] Plan user training schedule

### Technical Phase

- [ ] Verify all system requirements met
- [ ] Test installation on pilot machine
- [ ] Configure API keys (OpenAI, Legal AI)
- [ ] Set up monitoring system
- [ ] Create backup of existing data (if migrating from v1)
- [ ] Prepare rollback plan
- [ ] Document deployment steps

### User Preparation Phase

- [ ] Identify power users for early access
- [ ] Prepare training materials (QUICK_START.md)
- [ ] Create FAQ document
- [ ] Set up support contact info
- [ ] Plan communication schedule

---

## Server Requirements

### Minimum Specifications

| Resource | Minimum | Recommended | Large Scale |
|----------|---------|-------------|------------|
| **OS** | Windows 10 / Ubuntu 18.04 | Windows 11 / Ubuntu 22.04 | Dedicated server |
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **RAM** | 2 GB | 8 GB | 16 GB+ |
| **Storage** | 500 MB | 2 GB SSD | 100+ GB NVMe |
| **Network** | 10 Mbps | 100 Mbps | 1000 Mbps |
| **Disk I/O** | SATA | SSD | NVMe SSD |

### Network Requirements

- **Internet**: Optional (for AI features only)
  - Upload: 1 Mbps minimum
  - Latency: <100ms to OpenAI API
  - Protocol: HTTPS (443)

- **Internal Network**: Optional for shared database
  - LAN: 100 Mbps minimum
  - Latency: <10ms
  - Port: 5432 (PostgreSQL, if used)

### Browser (for remote access, optional)

- Chrome 100+
- Firefox 100+
- Edge 100+
- Safari 14+

---

## Installation Methods

### Method 1: Windows Desktop Deployment (Recommended)

**Best for**: 1-50 users, single office, IT-managed machines

#### Step 1: Prepare Installation Media

```powershell
# On development machine
cd C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2

# Install PyInstaller
pip install pyinstaller>=6.0

# Build standalone executable
pyinstaller --onefile --windowed --name "Painel Juridico v2" main.py

# Verify executable
ls dist\  # Should show "Painel Juridico v2.exe"

# Create installer (optional, professional)
# Download NSIS: https://nsis.sourceforge.io/Download
# Create installer.nsi (template in ADMIN_GUIDE.md)
makensis installer.nsi

# Output: Painel_Juridico_v2_Setup.exe
```

#### Step 2: Distribute to Target Machines

**Option A: Direct Installation (User-initiated)**
```powershell
# On target machine
# 1. Double-click Painel_Juridico_v2_Setup.exe
# 2. Follow wizard
# 3. Application installs to C:\Program Files\Painel_Juridico
# 4. Shortcut created on Desktop
```

**Option B: Silent/Automated Installation**
```powershell
# In batch script or Group Policy
Painel_Juridico_v2_Setup.exe /S /D=C:\Program Files\Painel_Juridico

# Wait for completion
timeout /t 30

# Configure API keys (optional)
echo OPENAI_API_KEY=sk-your-key > "C:\Program Files\Painel_Juridico\.env"

# Launch application
start "" "C:\Program Files\Painel_Juridico\Painel Juridico v2.exe"
```

**Option C: Group Policy Deployment (Enterprise)**
```powershell
# 1. Copy Painel_Juridico_v2_Setup.exe to network share
# \\domain\software\painel-juridico\

# 2. Create Group Policy (gpedit.msc):
# Computer Config → Software Installation → New → Package
# Select: \\domain\software\painel-juridico\Painel_Juridico_v2_Setup.exe

# 3. Deploy to OUs (automatic on group member logon)

# 4. Monitor deployment via Group Policy Results Viewer
```

#### Step 3: Post-Installation Configuration

```powershell
# Verify installation
python "C:\Program Files\Painel_Juridico\verify_setup.py"

# Configure application settings
# Edit: C:\Program Files\Painel_Juridico\.env

# Set file permissions
icacls "C:\Program Files\Painel_Juridico\data" /grant:r "%USERNAME%:M" /T

# Create backup directory
mkdir "C:\Program Files\Painel_Juridico\data\backups"
```

---

### Method 2: Portable Deployment (Remote/Field)

**Best for**: Remote offices, USB distribution, zero-installation requirement

#### Step 1: Create Portable Package

```powershell
# On development machine
cd C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2

# Build executable
pyinstaller --onefile --windowed --name "Painel Juridico v2" main.py

# Create portable directory
mkdir painel_juridico_portable
mkdir painel_juridico_portable\data
mkdir painel_juridico_portable\data\backups
mkdir painel_juridico_portable\exports_output

# Copy executable
cp dist\"Painel Juridico v2.exe" painel_juridico_portable\

# Copy requirements.txt (for reference)
cp requirements.txt painel_juridico_portable\

# Copy documentation
cp QUICK_START.md painel_juridico_portable\
cp README.md painel_juridico_portable\

# Create launcher batch file
@"
@echo off
REM Launch Painel Juridico v2
cd /d "%~dp0"
start "" "Painel Juridico v2.exe"
"@ | Out-File -Encoding ASCII painel_juridico_portable\launch.bat

# Create .env template
@"
# Optional API Keys - Edit this file and rename to .env
OPENAI_API_KEY=sk-your-key-here
LEGAL_AI_API_URL=https://api.legalai.com
"@ | Out-File -Encoding UTF8 painel_juridico_portable\.env.template

# Create ZIP archive
Compress-Archive -Path painel_juridico_portable -DestinationPath painel_juridico_portable.zip

# Verify
ls painel_juridico_portable.zip
```

#### Step 2: Distribute Portable Version

```powershell
# Option 1: Network share
Copy-Item painel_juridico_portable.zip "\\server\shared\apps\"

# Option 2: USB drive
Copy-Item painel_juridico_portable.zip "E:\"

# Option 3: Cloud storage
# Upload to OneDrive, Dropbox, Google Drive for easy sharing

# Option 4: Email (if <100 MB)
# Attach painel_juridico_portable.zip to email
```

#### Step 3: User Setup (Remote Machine)

```
1. Extract ZIP file
   - Right-click painel_juridico_portable.zip
   - Select "Extract All..."
   - Choose destination (Desktop, C:\Apps\, or USB root)

2. Configure API keys (optional)
   - Open .env.template with Notepad
   - Add your OpenAI API key
   - Save as .env (remove .template)

3. Run application
   - Double-click launch.bat OR
   - Double-click Painel Juridico v2.exe

4. Database initializes automatically
   - First launch takes ~3 seconds
   - Database created in data\ folder
   - 51 legal references loaded
```

---

### Method 3: Developer/Server Setup (Advanced)

**Best for**: Customization, integration, multiple machines with shared database

#### Step 1: System Dependencies

```powershell
# Windows Server or Linux VM

# Windows PowerShell
# Install Python 3.9+
https://www.python.org/downloads/

# Or Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip git

# Install Git
sudo apt install git
```

#### Step 2: Clone Repository

```powershell
# On deployment machine
git clone https://github.com/your-org/painel_juridico_v2.git
cd painel_juridico_v2

# Or download ZIP
# wget https://github.com/your-org/painel_juridico_v2/archive/main.zip
# unzip main.zip
```

#### Step 3: Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS
python3.9 -m venv venv
source venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

# Additional production packages
pip install gunicorn  # If running as service
pip install psycopg2-binary  # If using PostgreSQL
pip install python-dotenv  # For .env file support
```

#### Step 5: Configure Environment

```bash
# Create .env file
cat > .env << EOF
# Database Configuration
DATABASE_PATH=./data/painel_juridico.db
# DATABASE_URL=postgresql://user:password@localhost/painel_juridico  # For PostgreSQL

# API Keys
OPENAI_API_KEY=sk-your-key-here
LEGAL_AI_API_URL=https://api.legalai.com
LEGAL_AI_API_KEY=your-key

# Application Settings
APP_ENV=production
LOG_LEVEL=INFO
DEBUG=False
ENABLE_AI_FEATURES=True
BACKUP_RETENTION_DAYS=30

# Server Settings (if applicable)
HOST=0.0.0.0
PORT=8000
WORKERS=4
EOF

# Set permissions (Linux)
chmod 600 .env
```

#### Step 6: Run Application

```bash
# Direct execution
python main.py

# Or as a service (Linux systemd)
sudo tee /etc/systemd/system/painel-juridico.service > /dev/null << EOF
[Unit]
Description=Painel Jurídico v2
After=network.target

[Service]
Type=simple
User=painel
WorkingDirectory=/home/painel/painel_juridico_v2
ExecStart=/home/painel/painel_juridico_v2/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable painel-juridico
sudo systemctl start painel-juridico
sudo systemctl status painel-juridico
```

---

## Configuration Management

### Environment Variables (.env)

**Location**: Application directory (same as executable or main.py)

**Template**:
```env
# =================================================================
# PAINEL JURÍDICO v2 - PRODUCTION CONFIGURATION
# =================================================================

# DATABASE CONFIGURATION
# =====================
DATABASE_PATH=./data/painel_juridico.db
# For PostgreSQL: postgresql://user:password@localhost/painel_juridico

# API KEYS & EXTERNAL SERVICES
# =============================
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4.1
LEGAL_AI_API_URL=https://api.legalai.com
LEGAL_AI_API_KEY=your-key-here

# APPLICATION SETTINGS
# ====================
APP_ENV=production
LOG_LEVEL=INFO
DEBUG=False
ENABLE_AI_FEATURES=True

# BACKUP & DATA RETENTION
# =======================
BACKUP_RETENTION_DAYS=30
AUTO_BACKUP_ENABLED=True
BACKUP_TIME=23:00

# PERFORMANCE TUNING
# ==================
DATABASE_TIMEOUT=10.0
MAX_QUERY_TIMEOUT=30.0
CONNECTION_POOL_SIZE=5

# SECURITY
# ========
ALLOWED_ORIGINS=localhost,127.0.0.1
SESSION_TIMEOUT=3600
REQUIRE_PASSWORD=False

# MONITORING
# ==========
ENABLE_METRICS=True
ENABLE_AUDIT_LOG=True
SENTRY_DSN=  # Optional: error tracking service
```

### Configuration by Environment

**Development**:
```env
APP_ENV=development
LOG_LEVEL=DEBUG
DEBUG=True
OPENAI_API_KEY=test-key
```

**Staging**:
```env
APP_ENV=staging
LOG_LEVEL=INFO
DEBUG=False
OPENAI_API_KEY=staging-key
```

**Production**:
```env
APP_ENV=production
LOG_LEVEL=WARNING
DEBUG=False
OPENAI_API_KEY=prod-key
BACKUP_RETENTION_DAYS=90
```

### Configuration Management (Advanced)

**Using Configuration Server** (for enterprise):
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    DATABASE_PATH = os.getenv('DATABASE_PATH', './data/painel_juridico.db')
    OPENAI_KEY = os.getenv('OPENAI_API_KEY')
    APP_ENV = os.getenv('APP_ENV', 'development')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    BACKUP_RETENTION_DAYS = 90

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    BACKUP_RETENTION_DAYS = 7

# Select based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'staging': Config  # Use default/staging config
}

APP_CONFIG = config.get(os.getenv('APP_ENV', 'development'))
```

---

## Database Setup

### SQLite (Single-User/Small Teams)

**Advantages**:
- No setup required
- Zero administration
- Portable (single file)
- Works offline

**Setup**:
```bash
# Database auto-creates on first run
python main.py

# Verify database created
ls -la data/painel_juridico.db
```

**Backup**:
```bash
# Simple file copy
cp data/painel_juridico.db data/backups/painel_juridico_$(date +%Y%m%d).db

# Using Python
python -c "from core.database import backup_database; backup_database('backup.json')"
```

### PostgreSQL (Multi-User/Enterprise)

**Advantages**:
- Supports concurrent users
- Centralized backup
- Better performance for large datasets
- Remote access

#### Installation

**Windows**:
```powershell
# Download PostgreSQL 15+ from https://www.postgresql.org/download/windows/

# Or use Chocolatey
choco install postgresql15

# Start service
Start-Service PostgreSQL
```

**Linux (Ubuntu)**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib python3-psycopg2

sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Configuration

```bash
# Create database and user
sudo -u postgres psql

postgres=# CREATE DATABASE painel_juridico;
postgres=# CREATE USER painel_user WITH ENCRYPTED PASSWORD 'secure-password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE painel_juridico TO painel_user;
postgres=# \q

# Update .env
echo "DATABASE_URL=postgresql://painel_user:secure-password@localhost/painel_juridico" >> .env
```

#### Initialize Database

```python
# initialize_postgres.py
import psycopg2
from core.database import initialize_database

connection = psycopg2.connect(
    host="localhost",
    database="painel_juridico",
    user="painel_user",
    password="secure-password"
)

# Initialize tables
initialize_database(connection)

connection.close()
print("PostgreSQL database initialized")
```

```bash
python initialize_postgres.py
```

#### Performance Optimization

```sql
-- Connect as painel_user
\c painel_juridico painel_user

-- Create indexes
CREATE INDEX idx_processo_numero ON lawsuits(numero_processo);
CREATE INDEX idx_processo_status ON lawsuits(status);
CREATE INDEX idx_cliente_cpf ON clientes(cpf);
CREATE INDEX idx_processo_data ON lawsuits(data_cadastro);

-- Analyze table statistics
ANALYZE;

-- Check query performance
EXPLAIN ANALYZE SELECT * FROM lawsuits WHERE status = 'Ativo';
```

---

## Security Hardening

### File Permissions

**Windows**:
```powershell
# Restrict .env file access
icacls "C:\Program Files\Painel_Juridico\.env" /inheritance:r /grant:r "%USERNAME%:F"

# Database file
icacls "C:\Program Files\Painel_Juridico\data" /grant:r "%USERNAME%:M" /T
```

**Linux**:
```bash
# Application directory
sudo chown -R painel:painel /opt/painel_juridico_v2
sudo chmod 750 /opt/painel_juridico_v2

# Configuration file
sudo chmod 600 /opt/painel_juridico_v2/.env

# Database
sudo chmod 700 /opt/painel_juridico_v2/data
sudo chmod 600 /opt/painel_juridico_v2/data/*.db
```

### API Key Management

**Do NOT**:
- ❌ Store keys in source code
- ❌ Commit .env to version control
- ❌ Use same keys for dev/prod
- ❌ Share keys in emails/messages

**DO**:
- ✅ Use separate keys per environment
- ✅ Store in .env (excluded from git)
- ✅ Use environment variables
- ✅ Rotate keys quarterly
- ✅ Monitor API usage
- ✅ Use least-privilege API scopes

**Key Rotation**:
```bash
# Generate new OpenAI API key
# 1. Visit https://platform.openai.com/api-keys
# 2. Click "Create new secret key"
# 3. Copy new key
# 4. Update .env with new key
# 5. Restart application
# 6. Delete old key from OpenAI dashboard

# Verify key works
python -c "import openai; openai.api_key='sk-...'; print('✅ Key valid')"
```

### Network Security

**Firewall Configuration**:
```bash
# Allow only necessary ports
sudo ufw allow 443/tcp  # HTTPS for API
sudo ufw allow 5432/tcp # PostgreSQL (if needed)
sudo ufw allow 22/tcp   # SSH for admin

# Deny unnecessary ports
sudo ufw deny 3389/tcp  # Block RDP
sudo ufw deny 139/tcp   # Block NetBIOS
```

**SSL/TLS (for remote database access)**:
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Update PostgreSQL for SSL
sudo nano /etc/postgresql/15/main/postgresql.conf
# Uncomment: ssl = on
# ssl_cert_file = '/etc/ssl/certs/cert.pem'
# ssl_key_file = '/etc/ssl/private/key.pem'

sudo systemctl restart postgresql
```

---

## Monitoring & Logging

### Logging Configuration

**Application Logs**:
```python
# logging_config.py
import logging
import os
from datetime import datetime

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

def setup_logging():
    # File handler
    fh = logging.FileHandler(
        f"{log_dir}/painel_juridico_{datetime.now():%Y%m%d}.log"
    )
    fh.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = setup_logging()

# Usage in application
logger.info("Application started")
logger.error("Critical error occurred", exc_info=True)
```

### Health Monitoring

**Health Check Script**:
```python
# health_monitor.py
import os
import sqlite3
import sys
from datetime import datetime

def health_check():
    print(f"\n{'='*60}")
    print(f"Painel Jurídico v2 - Health Report")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Database
    db_path = "data/painel_juridico.db"
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / 1024 / 1024
        print(f"✅ Database: {size_mb:.2f} MB", end="")
        
        if size_mb > 500:
            print(" ⚠️  Large")
        else:
            print()
        
        # Integrity check
        try:
            db = sqlite3.connect(db_path)
            result = db.execute("PRAGMA integrity_check").fetchone()[0]
            if result == 'ok':
                print("✅ Integrity: OK")
            else:
                print(f"❌ Integrity: {result}")
                return 1
            db.close()
        except Exception as e:
            print(f"❌ Database error: {e}")
            return 1
    else:
        print("❌ Database not found")
        return 1
    
    # Backups
    backup_dir = "data/backups"
    if os.path.exists(backup_dir):
        backups = os.listdir(backup_dir)
        print(f"✅ Backups: {len(backups)} files")
    else:
        print("⚠️  No backup directory")
    
    # Disk space
    import shutil
    try:
        total, used, free = shutil.disk_usage(".")
        print(f"✅ Disk: {free / 1024 / 1024 / 1024:.1f} GB free")
    except:
        pass
    
    print(f"\n{'='*60}")
    print("✅ Health check passed")
    return 0

if __name__ == "__main__":
    sys.exit(health_check())
```

**Run Health Check**:
```bash
# Manual
python health_monitor.py

# Scheduled (Linux cron)
0 8 * * * cd /opt/painel_juridico && python health_monitor.py >> logs/health.log 2>&1

# Scheduled (Windows Task Scheduler)
# Create task: "Painel Health Check"
# Run: python health_monitor.py
# Frequency: Daily at 08:00
```

### Metrics to Monitor

**Database**:
- Size (alert if >500MB)
- Record counts
- Query performance
- Integrity status

**Application**:
- Startup time
- Response times
- Error rate
- API calls/costs

**System**:
- CPU usage
- Memory usage
- Disk I/O
- Network connectivity

---

## Backup & Disaster Recovery

### Backup Strategy

**Frequency**: Daily (automated)  
**Retention**: 30 days (configurable)  
**Location**: `data/backups/` (local) + network NAS (offsite)  
**RTO**: < 15 minutes  
**RPO**: < 24 hours

### Automated Backups

```python
# backup_scheduler.py
import schedule
import time
from core.database import backup_database
from datetime import datetime

def daily_backup():
    """Create daily backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"data/backups/painel_juridico_{timestamp}.json"
    
    try:
        backup_database(backup_file)
        print(f"✅ Backup created: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def cleanup_old_backups(days=30):
    """Delete backups older than N days"""
    import os
    from datetime import datetime, timedelta
    
    cutoff = datetime.now() - timedelta(days=days)
    backup_dir = "data/backups"
    
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        if mtime < cutoff:
            os.remove(filepath)
            print(f"🗑️  Deleted old backup: {filename}")

# Schedule jobs
schedule.every().day.at("23:00").do(daily_backup)
schedule.every().day.at("23:30").do(cleanup_old_backups)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

**Run as Service**:
```bash
# Windows Task Scheduler
# Task name: "Painel Daily Backup"
# Script: python backup_scheduler.py
# Frequency: Daily at 23:00
# Run with highest privileges

# Linux systemd service
sudo tee /etc/systemd/system/painel-backup.service > /dev/null << EOF
[Unit]
Description=Painel Jurídico Backup Service
After=network.target

[Service]
Type=simple
User=painel
WorkingDirectory=/opt/painel_juridico
ExecStart=/opt/painel_juridico/venv/bin/python backup_scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable painel-backup
sudo systemctl start painel-backup
```

### Manual Backup

```bash
# Export to JSON
python -c "from core.database import backup_database; backup_database('backup_manual.json')"

# Verify backup
ls -lh data/backups/

# Copy to offsite storage
cp data/backups/painel_juridico_*.json /mnt/nas/backups/
```

### Disaster Recovery

**Scenario 1: Database Corrupted**

```bash
# 1. Stop application
sudo systemctl stop painel-juridico

# 2. Check integrity
sqlite3 data/painel_juridico.db "PRAGMA integrity_check;"

# 3. Backup corrupted database
cp data/painel_juridico.db data/painel_juridico.db.corrupt

# 4. Restore from backup
python -c "from core.database import restore_database; restore_database('data/backups/painel_juridico_20260519.json')"

# 5. Verify restored database
python verify_setup.py

# 6. Start application
sudo systemctl start painel-juridico

# 7. Verify data
# Check Dashboard statistics match expectations
```

**Scenario 2: Data Loss (Recent Deletion)**

```bash
# 1. Check available backups
ls -lt data/backups/ | head -10

# 2. Merge backup with current database (preserves recent data)
python -c "from core.database import restore_database; restore_database('data/backups/painel_juridico_YYYY-MM-DD.json', clear_existing=False)"

# 3. Verify merge
python verify_setup.py
```

**Scenario 3: Server Failure**

```bash
# 1. On new server, install application
# 2. Restore latest backup
python -c "from core.database import restore_database; restore_database('/mnt/backup/painel_juridico_latest.json')"

# 3. Verify all data restored
python health_monitor.py

# 4. Start application
```

---

## Performance Tuning

### Database Optimization

**SQLite**:
```python
# Optimize SQLite performance
import sqlite3

db = sqlite3.connect('data/painel_juridico.db')

# Enable WAL mode (faster concurrent access)
db.execute('PRAGMA journal_mode=WAL;')

# Increase cache size
db.execute('PRAGMA cache_size = 10000;')

# Optimize query plans
db.execute('PRAGMA optimize;')

# Analyze statistics
db.execute('ANALYZE;')

# Run VACUUM (monthly)
db.execute('VACUUM;')

db.close()
```

**PostgreSQL**:
```sql
-- Connect as admin
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '4GB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;

-- Apply changes
SELECT pg_reload_conf();
```

### Application-Level Optimization

**Caching**:
```python
from functools import lru_cache
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

# Usage
cache = CacheManager(ttl_seconds=1800)

def get_dashboard_metrics():
    cached = cache.get('dashboard_metrics')
    if cached:
        return cached
    
    # Expensive query
    metrics = calculate_dashboard_metrics()
    cache.set('dashboard_metrics', metrics)
    return metrics
```

**Pagination**:
```python
# Instead of loading all records
def get_processes(limit=100, offset=0):
    db = sqlite3.connect('data/painel_juridico.db')
    cursor = db.cursor()
    
    # Limit results
    query = "SELECT * FROM lawsuits LIMIT ? OFFSET ?"
    cursor.execute(query, (limit, offset))
    
    results = cursor.fetchall()
    db.close()
    return results

# Usage
page = 1
page_size = 100
offset = (page - 1) * page_size
processes = get_processes(limit=page_size, offset=offset)
```

### Load Testing

```bash
# Test application with multiple concurrent users
pip install locust

# Create locustfile.py with test scenarios
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class PainelUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def load_dashboard(self):
        self.client.get("/dashboard")
    
    @task
    def search_cases(self):
        self.client.get("/search?q=test")
    
    @task
    def generate_document(self):
        self.client.post("/generate-pdf", json={"case_id": 1})
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10
```

---

## Troubleshooting

### Cannot Start Application

**Symptom**: Application fails to launch

**Solution**:
```powershell
# 1. Check Python version (developer setup)
python --version  # Should be 3.9+

# 2. Verify dependencies
pip list

# 3. Check for corrupted database
del data/painel_juridico.db  # Recreates on next launch

# 4. Clear Python cache
rm -r __pycache__
rm -r .pytest_cache

# 5. Test database module
python -c "from core.database import initialize_database; print('✅ Database OK')"

# 6. Check file permissions
icacls data  # Ensure user has write permission
```

### Slow Performance

**Symptom**: Application/queries running slowly

**Solution**:
```bash
# 1. Check database size
ls -lh data/painel_juridico.db

# 2. Optimize database
python -c "import sqlite3; sqlite3.connect('data/painel_juridico.db').execute('VACUUM')"

# 3. Add indexes
python -c "import sqlite3; db = sqlite3.connect('data/painel_juridico.db'); db.execute('CREATE INDEX IF NOT EXISTS idx_processo_status ON lawsuits(status)'); db.commit()"

# 4. Check system resources
# Windows: Task Manager → Performance
# Linux: top / htop / free -h

# 5. Reduce dataset (archive old cases)
# See ADMIN_GUIDE.md
```

### API Key Not Working

**Symptom**: AI features not functioning, error messages about API

**Solution**:
```bash
# 1. Verify API key in .env
cat .env | grep OPENAI_API_KEY

# 2. Check key format (must start with "sk-")
echo $OPENAI_API_KEY

# 3. Verify API key is valid
# Visit https://platform.openai.com/api-keys

# 4. Check API quota/billing
# Visit https://platform.openai.com/account/billing/overview

# 5. Test API connection
python -c "
import openai
openai.api_key = 'sk-...'
response = openai.ChatCompletion.create(
    model='gpt-4',
    messages=[{'role': 'user', 'content': 'test'}]
)
print('✅ API working')
"

# 6. Regenerate key if unsure
# Delete old key from OpenAI
# Create new key and update .env
# Restart application
```

### Database Locked

**Symptom**: "Database is locked" error

**Solution**:
```powershell
# 1. Close all application instances
taskkill /IM "Painel Juridico v2.exe" /F

# 2. Wait 5 seconds
timeout /t 5

# 3. Restart application
start "" "Painel Juridico v2.exe"

# 4. If persists, restart computer
Restart-Computer
```

### Backup Failures

**Symptom**: Backups not creating or restore failing

**Solution**:
```bash
# 1. Verify backup directory exists
ls -la data/backups/

# 2. Check permissions
chmod 777 data/backups

# 3. Verify disk space
df -h | grep data  # >100MB free required

# 4. Test backup manually
python -c "from core.database import backup_database; backup_database('test_backup.json')"

# 5. Verify backup file created
ls -lh test_backup.json

# 6. Test restore
python -c "from core.database import restore_database; restore_database('test_backup.json', clear_existing=False)"
```

---

## Checklists

### Pre-Deployment

- [ ] All system requirements verified
- [ ] Installation media prepared (exe, portable, or source)
- [ ] Configuration file (.env) created with valid API keys
- [ ] Backup strategy defined and tested
- [ ] Monitoring system configured
- [ ] Support team trained
- [ ] User documentation reviewed
- [ ] Rollback plan documented

### Deployment Day

- [ ] Backup existing data (if applicable)
- [ ] Install application using chosen method
- [ ] Run verification script: `python verify_setup.py`
- [ ] Test core functionality (add client, case, generate PDF)
- [ ] Verify backup system working
- [ ] Configure monitoring alerts
- [ ] Notify users of deployment
- [ ] Begin user training

### Post-Deployment

- [ ] Monitor application logs for errors
- [ ] Check daily backup completion
- [ ] Gather user feedback
- [ ] Document any issues encountered
- [ ] Schedule performance optimization review
- [ ] Plan Phase 3 features
- [ ] Update runbooks with actual procedures

---

## Support & Documentation

| Issue | Document | Solution |
|-------|----------|----------|
| Installation help | DEPLOYMENT_INSTRUCTIONS.md | 3 deployment methods |
| User training | QUICK_START.md | 5-minute guide |
| Operations | ADMIN_GUIDE.md | Maintenance procedures |
| Architecture | DEPLOYMENT_PLAN.md | Technical design |
| Verification | PRODUCTION_READINESS_REPORT.md | Test results |

---

## Version Information

- **Application**: Painel Jurídico v2
- **Version**: 2.0.0
- **Release Date**: 2026-05-19
- **Status**: Production Ready
- **Maintenance**: Contact: [Your Organization]

---

**Successfully deploying Painel Jurídico v2 requires careful planning, proper configuration, and ongoing monitoring. Follow this guide to ensure a smooth production environment.**
