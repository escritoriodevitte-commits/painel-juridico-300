# Painel Jurídico v2 - Administrator & Operations Guide

This guide is for system administrators, IT staff, and managers responsible for deployment, maintenance, and operations.

## System Requirements

### Minimum Specifications
- **OS**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **RAM**: 2 GB minimum (4 GB recommended)
- **Storage**: 500 MB for application + database
- **Network**: Internet connection (optional, for AI features)
- **Python**: 3.9+ (for development version only)

### Recommended Specifications
- **OS**: Windows 10/11 (latest updates)
- **RAM**: 8 GB+
- **Storage**: 2 GB free space (SSD recommended)
- **Network**: Stable broadband (for Legal AI sync)

## Deployment Methods

### Method 1: Windows Installer (Recommended for Enterprise)

**Advantages**: 
- Professional installation experience
- Automatic updates
- Registry entries
- Uninstall capability

**Installation**:
```cmd
Painel_Juridico_v2_Setup.exe /S /D=C:\Program Files\Painel_Juridico
```

**Deployment to Multiple Machines** (via Group Policy):
1. Place `Painel_Juridico_v2_Setup.exe` on network share
2. Configure Group Policy to deploy on login
3. Users receive automatic installation on next logon
4. No user interaction required

### Method 2: Portable Version (for Remote/Field Offices)

**Advantages**:
- Zero installation required
- USB-portable (works on any computer)
- No admin rights needed
- Self-contained

**Deployment**:
1. Download `painel_juridico_portable.zip`
2. Extract to network share or USB drive
3. Users run `Painel Juridico v2.exe` directly
4. Database auto-initializes on first run

### Method 3: Silent Installation (Automated Deployment)

**Batch Script** (`install_pj.bat`):
```batch
@echo off
REM Uninstall previous version
wmic product where name="Painel Juridico v2" call uninstall /nointeractive

REM Install new version silently
Painel_Juridico_v2_Setup.exe /S /D=C:\Program Files\Painel_Juridico

REM Create config file
echo OPENAI_API_KEY=sk-your-key > "C:\Program Files\Painel_Juridico\.env"

REM Launch application
start "" "C:\Program Files\Painel_Juridico\Painel Juridico v2.exe"

echo Installation complete
pause
```

## Database Management

### Daily Operations

**Backup Schedule**:
- Automatic: Daily at application startup
- Manual: Users can trigger anytime via Dashboard → Menu → Backup
- Location: `data/backups/painel_juridico_YYYY-MM-DD.json`

**Monitoring**:
```batch
REM Check database size (alert if >500MB)
for /R "data\" %%f in (*.db) do @echo %%~zf %%~nf

REM Check backup directory size
for /d %%d in (data\backups) do @echo %%~zd
```

**Health Check** (Monthly):
```python
import sqlite3
import os

db_path = "data/painel_juridico.db"

# Check integrity
db = sqlite3.connect(db_path)
integrity = db.execute("PRAGMA integrity_check").fetchone()
print(f"Database integrity: {integrity}")

# Check size
db_size_mb = os.path.getsize(db_path) / 1024 / 1024
print(f"Database size: {db_size_mb:.2f} MB")

# Check table counts
tables = ["clientes", "judges", "lawsuits", "settlements", "legal_references", "negotiation_params", "generated_pieces"]
for table in tables:
    count = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} records")

db.close()
```

### Maintenance Tasks

**Optimize Database** (Quarterly):
```bash
python -c "import sqlite3; sqlite3.connect('data/painel_juridico.db').execute('VACUUM')"
```

**Add Indexes** (for large datasets >10,000 records):
```python
import sqlite3

db = sqlite3.connect('data/painel_juridico.db')
cursor = db.cursor()

indexes = [
    "CREATE INDEX IF NOT EXISTS idx_processo_numero ON lawsuits(numero_processo)",
    "CREATE INDEX IF NOT EXISTS idx_processo_status ON lawsuits(status)",
    "CREATE INDEX IF NOT EXISTS idx_cliente_cpf ON clientes(cpf)",
    "CREATE INDEX IF NOT EXISTS idx_processo_data ON lawsuits(data_cadastro)"
]

for idx in indexes:
    cursor.execute(idx)
    print(f"Created: {idx}")

db.commit()
db.close()
```

### Backup Management

**Create Full Backup**:
```python
from core.database import backup_database
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"painel_juridico_backup_{timestamp}.json"
backup_database(backup_file)
print(f"Backup created: {backup_file}")
```

**Restore from Backup**:
```python
from core.database import restore_database

# With clear_existing=True: replaces entire database
restore_database('painel_juridico_backup_20260519_120000.json', clear_existing=True)
print("Database restored successfully")

# With clear_existing=False: merges with existing data
restore_database('painel_juridico_backup_20260519_120000.json', clear_existing=False)
print("Backup merged with existing database")
```

**Disaster Recovery Procedure**:
1. Stop all instances of application
2. Backup current corrupted database: `copy data\painel_juridico.db data\painel_juridico.db.corrupt`
3. Delete current database: `del data\painel_juridico.db`
4. Restore from backup: Run restore script above
5. Start application (database recreates with restored data)
6. Verify data: Check Dashboard statistics match expectations
7. Test critical functionality: Add/edit case, generate PDF, search

**RTO (Recovery Time Objective)**: < 15 minutes
**RPO (Recovery Point Objective)**: < 24 hours (daily backups)

## Configuration Management

### Environment Configuration (.env)

**Location**: Application directory (same as .exe or main.py)

**Template** (`.env`):
```env
# OpenAI Integration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4.1

# Legal AI Integration (optional)
LEGAL_AI_API_URL=https://api.legalai.com
LEGAL_AI_API_KEY=your-key-here

# Database
DATABASE_PATH=./data/painel_juridico.db

# Application Settings
APP_ENV=production
LOG_LEVEL=INFO
DEBUG=False

# Feature Flags
ENABLE_AI_FEATURES=True
ENABLE_BACKUP_AUTOSTART=True
BACKUP_RETENTION_DAYS=30
```

**Security Best Practices**:
1. Never commit `.env` to version control
2. Use file permissions: Make `.env` readable by application user only
3. Rotate API keys quarterly
4. Use separate API keys for development/production
5. Monitor API usage and costs

**Deployment Configuration**:
```batch
REM Create .env during deployment
(
  echo OPENAI_API_KEY=%OPENAI_KEY%
  echo LEGAL_AI_API_URL=%LEGAL_AI_URL%
  echo DATABASE_PATH=./data/painel_juridico.db
  echo APP_ENV=production
  echo LOG_LEVEL=INFO
) > "C:\Program Files\Painel_Juridico\.env"

REM Set file permissions (Windows)
icacls "C:\Program Files\Painel_Juridico\.env" /inheritance:r /grant:r "%USERNAME%:F"
```

## Updates & Patching

### Version Management

**Current Version**: 2.0.0

**Version Numbering Scheme** (Semantic Versioning):
- Major (2.x.x): Breaking changes, new major features
- Minor (x.1.x): New features, backward compatible
- Patch (x.x.1): Bug fixes, no new features

### Minor Updates (Patches)

**Example**: v2.0.0 → v2.0.1 (bug fix)

1. Update version in source: `__version__ = "2.0.1"`
2. Run all tests: `python test_final.py` (expect 100% pass)
3. Rebuild executable:
   ```bash
   pyinstaller --onefile --windowed --name "Painel Juridico v2" main.py
   ```
4. Test on clean machine
5. Create release notes
6. Deploy new version

**Release Notes Template**:
```
Version 2.0.1
Released: 2026-06-01

Fixes:
- Fixed database initialization timeout on first launch
- Fixed search results not updating when filtering by date range
- Fixed memory leak in chart generation module
- Fixed CSV export encoding on Windows

Improvements:
- Reduced startup time by 30% with database caching
- Improved search performance for datasets >10,000 records
- Better error messages for validation failures

No database migration required
```

### Major Updates (New Features)

**Example**: v2.0.x → v2.1.0 (new functionality)

1. Extended testing period (1-2 weeks)
2. Beta testing with subset of users
3. Database migration planning (if schema changes)
4. Full regression testing
5. Staged rollout (pilot → small group → full deployment)

**Rollback Plan**:
- Keep previous version available for 30 days
- If issues detected: Restore from backup, revert to previous version
- Communicate with users about rollback

### Automatic Update Feature (Optional)

**Implementation** (future version):
```python
import requests
from packaging import version

RELEASES_URL = "https://api.github.com/repos/painel-juridico/releases/latest"

def check_for_updates():
    response = requests.get(RELEASES_URL)
    if response.status_code == 200:
        latest = response.json()['tag_name'].replace('v', '')
        current = "2.0.1"
        
        if version.parse(latest) > version.parse(current):
            return True, latest
    return False, None
```

## Monitoring & Alerting

### Key Metrics to Monitor

**Application Health**:
- Daily users (average)
- Features used (charts, exports, calculations)
- API calls (searches, syncs)
- Error rate (exceptions per day)

**Database Health**:
- File size (alert if >500MB)
- Record counts by table
- Query performance (slow queries)
- Backup completion status

**System Health**:
- Disk space available
- Memory usage
- Process CPU usage
- Network latency (for sync features)

### Monitoring Script

```python
import os
import sqlite3
from datetime import datetime

def generate_health_report():
    print(f"\n=== Painel Jurídico v2 - Health Report ===")
    print(f"Generated: {datetime.now().isoformat()}")
    
    # Database metrics
    db_path = "data/painel_juridico.db"
    if os.path.exists(db_path):
        db_size_mb = os.path.getsize(db_path) / 1024 / 1024
        print(f"\n📊 Database Size: {db_size_mb:.2f} MB", end="")
        
        if db_size_mb > 500:
            print(" ⚠️ WARNING: >500MB")
        else:
            print(" ✅")
        
        # Integrity check
        db = sqlite3.connect(db_path)
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        print(f"🔍 Integrity: {integrity if integrity == 'ok' else f'ERROR: {integrity}'}")
        
        # Record counts
        print("\n📋 Record Counts:")
        tables = ["clientes", "judges", "lawsuits", "settlements", "legal_references", "negotiation_params", "generated_pieces"]
        for table in tables:
            count = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"   {table}: {count}")
        
        db.close()
    else:
        print("❌ Database not found")
    
    # Backup metrics
    backup_dir = "data/backups"
    if os.path.exists(backup_dir):
        backups = os.listdir(backup_dir)
        print(f"\n💾 Latest Backups ({len(backups)} total):")
        for backup in sorted(backups, reverse=True)[:5]:
            backup_size_kb = os.path.getsize(os.path.join(backup_dir, backup)) / 1024
            print(f"   {backup} ({backup_size_kb:.0f} KB)")
    
    # Disk space
    total, used, free = 0, 0, 0
    import shutil
    try:
        total, used, free = shutil.disk_usage(".")
        print(f"\n💿 Disk Space: {free / 1024 / 1024 / 1024:.1f} GB free ({free * 100 / total:.1f}%)")
    except:
        pass

if __name__ == "__main__":
    generate_health_report()
```

**Run Daily**:
```cmd
REM Create scheduled task
schtasks /create /tn "PainelJuridico_Health" /tr "python health_report.py" /sc daily /st 08:00
```

## User Support & Training

### Training Materials

1. **Quick Start Guide** (`QUICK_START.md`)
   - Installation options
   - First launch checklist
   - Common tasks (add client, case, calculate, generate doc)
   - Keyboard shortcuts
   - Troubleshooting

2. **Full Feature Documentation** (`README.md`)
   - All 13 screens documented
   - Feature descriptions
   - Example workflows

3. **Video Tutorials** (optional, to create):
   - Dashboard overview (2 min)
   - Adding cases & clients (3 min)
   - Calculator walkthrough (4 min)
   - AI document generation (3 min)
   - Backup & restore (2 min)

### Support Process

**Tier 1: User Self-Help**
1. Check Quick Start Guide
2. Check Help menu in application
3. Read FAQ
4. Check knowledge base

**Tier 2: Administrator Support**
1. Verify application version and database size
2. Check application logs (Help → View Logs)
3. Run health report script
4. Check for known issues in release notes

**Tier 3: Development Team**
- Escalate with logs, error messages, steps to reproduce
- Expected response time: 24 hours

## Compliance & Legal

### LGPD Compliance (Lei Geral de Proteção de Dados)

**Required Features**:
1. ✅ Data access: Users can export their data (JSON/CSV)
2. ⏳ Data deletion: Implement feature to delete case + related data
3. ✅ Privacy policy: Add to Help menu
4. ⏳ Audit log: Track who modified what data (for enterprise)

**Implementation Checklist**:
- [ ] Privacy policy document (Help menu)
- [ ] Data export feature (Dashboard → Menu → Export Data)
- [ ] Delete case feature with cascade delete
- [ ] Optional: Audit logging middleware

### Document Retention

**Brazilian Labor Law Requirements**:
- Archive cases for 7 years minimum
- Maintain audit trail for legal discovery
- Export capability for court requests

**Implementation**:
```python
# Archive old cases (>3 years) to separate database
def archive_old_cases():
    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=3*365)).isoformat()
    
    # Export cases before cutoff
    db = sqlite3.connect('painel_juridico.db')
    archived = db.execute(
        "SELECT * FROM lawsuits WHERE data_cadastro < ?",
        (cutoff_date,)
    ).fetchall()
    
    # Save to archive database
    archive_db = sqlite3.connect(f"archives/painel_juridico_{datetime.now().year}.db")
    archive_db.executemany("INSERT INTO lawsuits VALUES (?)", archived)
    archive_db.commit()
    
    # Delete from main database (with backup first!)
    db.execute("DELETE FROM lawsuits WHERE data_cadastro < ?", (cutoff_date,))
    db.commit()
```

## Troubleshooting for Administrators

### Issue: Slow Application on Multiple Users

**Cause**: SQLite not optimized for concurrent access
**Solution**: 
1. Add database indexes (see above)
2. Implement query caching
3. Consider database migration to PostgreSQL for multi-user setup

### Issue: High API Costs (OpenAI)

**Causes**: Excessive document generation, inefficient API calls
**Solutions**:
1. Set API rate limiting: `MAX_API_CALLS_PER_DAY=100`
2. Use local templates instead of AI (when possible)
3. Monitor API usage: `Usage → Dashboard → API Costs`
4. Consider cheaper model: `gpt-3.5-turbo` instead of `gpt-4`

### Issue: Database Corruption After Crash

**Recovery**:
1. Check integrity: `PRAGMA integrity_check`
2. Attempt repair: `PRAGMA integrity_check` → look for errors
3. If damaged: Restore from backup
4. If no backup: Recreate empty database and notify users of data loss

### Issue: Disk Space Full

**Causes**: Large backups, exports, old logs
**Solutions**:
1. Clean old exports: `exports_output/` older than 30 days
2. Remove old backups: Keep only last 7 days
3. Compress old archives to separate storage
4. Set auto-cleanup policy in configuration

## Performance Tuning

### For Large Datasets (>10,000 processes)

**Database Optimization**:
```python
# Add indexes (see above)
# Vacuum monthly
# Analyze query plans: EXPLAIN QUERY PLAN SELECT ...

# Increase query timeout
db.timeout = 10.0  # 10 seconds
```

**UI Optimization**:
```python
# Implement pagination (100 records per page)
# Add caching for dashboard metrics
# Lazy-load details on click
# Debounce search input (wait 300ms)
```

**Batch Operations**:
```python
# Instead of individual inserts
for i in range(1000):
    insert_case(data[i])  # Slow

# Use batch insert
db.executemany("INSERT INTO lawsuits VALUES (?, ?, ...)", cases)  # Fast
```

## Checklist for Administrators

### Initial Setup
- [ ] Install application (single machine or network deployment)
- [ ] Create `.env` configuration file with API keys
- [ ] Run test suite: `python test_final.py`
- [ ] Verify database creation and seeding
- [ ] Test backup/restore functionality
- [ ] Configure backup schedule (daily)
- [ ] Set up monitoring/alerts

### Ongoing Maintenance
- [ ] Daily: Monitor database size and backup status
- [ ] Weekly: Check for user-reported issues
- [ ] Monthly: Run health report, optimize database
- [ ] Quarterly: Full backup to secure storage, test restore
- [ ] Quarterly: Review API costs and usage
- [ ] Annually: Security audit, performance review

### Updates & Patches
- [ ] Review release notes before updating
- [ ] Test updates on non-production machine first
- [ ] Back up database before major updates
- [ ] Have rollback plan ready
- [ ] Communicate changes to users

---

**Version**: 2.0.0  
**Last Updated**: 2026-05-19  
**Next Review**: 2026-08-19
