# Painel Jurídico v2 - Quick Start Guide

Welcome to Painel Estratégico Jurídico v2! This guide will help you get started in 5 minutes.

## Installation

### Option 1: Windows Installer (Easiest)
1. Download `Painel_Juridico_v2_Setup.exe`
2. Double-click to run the installer
3. Follow the on-screen instructions
4. Click "Finish" when complete
5. Shortcut appears on desktop and Start Menu

### Option 2: Portable Version (No Installation)
1. Download `painel_juridico_portable.zip`
2. Extract to any folder (Documents, Desktop, USB drive)
3. Double-click `Painel Juridico v2.exe`
4. Application starts immediately

### Option 3: Developer (Python)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## First Launch

When you start the application:
1. Database initializes automatically (~3 seconds)
2. 51 legal references load into Library
3. Main dashboard appears with empty statistics
4. You're ready to start using the system

**Note**: First launch takes ~5 seconds as database is created. Subsequent launches are instant.

## The 5 Main Sections

### 📊 GESTÃO (Management)
- **Dashboard** - Overview of all metrics (total cases, wins, economy, clients)
- **Clientes** - Add/edit client information (name, CPF, phone, email)
- **Processos** - Add/edit legal cases (case number, amounts, judges, dates)
- **Magistrados** - Manage judges (names, experience, tendencies)
- **Acordos** - Record settlements and agreements reached
- **Biblioteca** - Search 51 pre-loaded legal references by theme
- **Calculadora** - Calculate labor law settlements (8 termination types)

### 🧠 INTELIGÊNCIA (Intelligence)
- **Previsão** - Predicted win probability for each case
- **Motor Teses** - Ranked legal theories by strength
- **Radar Risco** - Risk classification (low/medium/high/critical)
- **Competitiva** - Win rate rankings and KPIs
- **Gerar Peças** - Create legal documents (reclamation, reply, appeals, etc.) with AI assistance

### ⚙️ CONFIGURAÇÕES (Settings)
- **API OpenAI** - Enable AI-powered document generation (optional)
- **Integração Legal AI** - Sync cases with external legal AI platform

## Common Tasks

### Add a New Client
1. Click **Clientes** in sidebar
2. Click **Novo Cliente** button
3. Fill in: Name, CPF, Phone, Email, Address
4. Click **Salvar** (Save)
5. Client appears in table below

### Add a New Case
1. Click **Processos** in sidebar
2. Click **Novo Processo** button
3. Fill in: Case number, Claim value, Client, Judge, Vara (court)
4. Choose dates (filing, expected judgment)
5. Specify action type (horas extras, justa causa, rescisão indireta, etc.)
6. Click **Salvar** (Save)
7. Case appears in dashboard statistics

### Calculate Labor Settlement
1. Click **Calculadora** in sidebar
2. Select termination type (e.g., "Sem Justa Causa")
3. Enter salary, tenure, vacation dates
4. Check boxes for applicable bonuses (extra hours, night shift, etc.)
5. Click **Calcular** (Calculate)
6. Results show all debts owed to employee by law
7. Click **Exportar PDF** to save calculation report

### Generate Legal Document (with AI)
1. Click **Gerar Peças** in sidebar
2. Select document type (Reclamation, Reply, etc.)
3. Enter document content and client info
4. **Option A**: Click **Gerar com IA** to use AI (requires OpenAI key)
5. **Option B**: Click **Usar Template** to use local template
6. Review generated document
7. Click **Exportar PDF** to save

### Search Cases
1. Use **Global Search** (magnifying glass icon) at top
2. Type case number, client name, or judge name
3. Results appear instantly with filtering options
4. Click result to see full details

### Backup Your Data
1. Click **Dashboard**
2. Click **Menu** (three dots)
3. Click **Backup Database**
4. Choose save location
5. File is saved as JSON (can be restored later)

## Tips & Tricks

✅ **Dashboard Cards**: Click any stat card to filter by that category  
✅ **Export Options**: All screens support PDF, CSV, and TXT export  
✅ **Search**: Use partial names/numbers (doesn't need exact match)  
✅ **API Key**: Get from openai.com if you want AI document generation  
✅ **Database**: Auto-backed up daily, manual backup available anytime  
✅ **Legal References**: Keyword search across 51 references by theme  

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+S | Save current form |
| Ctrl+E | Export visible table |
| Ctrl+N | New record (context-dependent) |
| Ctrl+F | Open search |
| F1 | Help |
| Escape | Close dialog |

## Common Issues & Solutions

**Q: Application won't start**  
A: Delete `painel_juridico.db` file, restart app (database recreates automatically)

**Q: "Database locked" error**  
A: Close all instances of application, restart computer if issue persists

**Q: AI features not working**  
A: Ensure OpenAI API key is entered in **API OpenAI** settings. Free trial required.

**Q: Too slow with many cases (>5000)**  
A: Archive old cases to separate backup file, or contact support for optimization

**Q: Lost database**  
A: Restore from backup JSON file: Dashboard → Menu → Restore Database

## Documentation

- **Full Features**: See README.md (all 13 screens documented)
- **Deployment**: See DEPLOYMENT_PLAN.md (setup, backup, maintenance)
- **Phase 2 Details**: See PHASE2_COMPLETION.md (technical implementation)

## Support

### For Issues:
1. Check this Quick Start Guide
2. Check Help menu in application
3. Review FAQ section
4. Contact support with screenshot and error message

### Data You Need for Support:
- Application version (Help → About)
- Database size (Dashboard → Statistics)
- Error message (exact text)
- Steps to reproduce issue

---

**Version**: 2.0.0  
**Last Updated**: 2026-05-19  
**License**: Proprietary  
**Contact**: support@painel-juridico.com
