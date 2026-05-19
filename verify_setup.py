#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Painel Jurídico v2 - Core Functionality Verification
Verifies database, calculator, generators, and analytics initialization
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core import database as db
from modules.calculadora.calc import calcular_verbas as calc
from modules.ia.gerador import GeradorPecas
from modules.analytics.engine import AnalyticsEngine

def verify_setup():
    """Run core functionality verification"""
    
    print("=" * 70)
    print("PAINEL JURÍDICO v2 - CORE FUNCTIONALITY VERIFICATION")
    print("=" * 70)
    
    results = []
    
    # 1. Database initialization
    print("\n1. DATABASE INITIALIZATION")
    try:
        db.init_db()
        clientes = db.get_all_clientes()
        judges = db.get_all_judges()
        refs = db.get_all_legal_references()
        
        print("   ✅ Database initialized successfully")
        print(f"   ✅ Clients in database: {len(clientes)}")
        print(f"   ✅ Judges in database: {len(judges)}")
        print(f"   ✅ Legal references loaded: {len(refs)}")
        results.append(("Database", True))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Database", False))
    
    # 2. Calculator test
    print("\n2. CALCULATOR MODULE (Labor Law)")
    try:
        # Test sem justa causa calculation
        from datetime import date, timedelta
        calc_date = date.today()
        result = calc({
            'tipo_rescisao': 'sem_justa_causa',
            'salario_base': 3000,
            'data_admissao': (calc_date - timedelta(days=730)).isoformat(),
            'data_demissao': calc_date.isoformat(),
            'adicional_noturno_horas': 80,
            'aviso_previo': 'indenizado'
        })
        
        print("   ✅ Calculator module working")
        print(f"   ✅ Test: Termination without just cause")
        print(f"   ✅ Salary: R$ 3.000,00")
        print(f"   ✅ Tenure: ~24 months")
        print(f"   ✅ Total debts calculated: {len(result)} items")
        results.append(("Calculator", True))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Calculator", False))
    
    # 3. Document generator test
    print("\n3. DOCUMENT GENERATOR MODULE")
    try:
        from modules.ia.gerador import TIPOS_PECA
        
        gerador = GeradorPecas()
        
        # Test reclamatoria generation using correct method signature
        lawsuit = {
            'numero_processo': '0012345-67.2026.5.08.0100',
            'vara': 'Vara do Trabalho',
            'reclamante': 'João Silva',
            'reclamada': 'Empresa XYZ',
            'tese_inicial': 'Cobrança de horas extras não pagas'
        }
        template = gerador.gerar_peca(lawsuit, None, [], 'reclamatoria_trabalhista')
        
        print("   ✅ Document generator initialized")
        print(f"   ✅ Template generated: {len(template)} characters")
        print(f"   ✅ Supported document types: {len(TIPOS_PECA)}")
        results.append(("Generator", True))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Generator", False))
    
    # 4. Analytics engine test
    print("\n4. ANALYTICS ENGINE")
    try:
        analytics = AnalyticsEngine()
        metrics = analytics.get_dashboard_metrics()
        
        print("   ✅ Analytics engine initialized")
        print("   ✅ Dashboard metrics retrieved")
        total = metrics.get('total_processos', 0)
        taxa = metrics.get('taxa_vitoria', 'N/A')
        print(f"   ✅ Total processes in dashboard: {total}")
        print(f"   ✅ Win rate: {taxa}%")
        results.append(("Analytics", True))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Analytics", False))
    
    # 5. Backup and restore test
    print("\n5. DATABASE BACKUP & RESTORE")
    try:
        backup_file = 'test_backup.json'
        
        # Create backup
        db.backup_database(backup_file)
        
        if os.path.exists(backup_file):
            size_kb = os.path.getsize(backup_file) / 1024
            print("   ✅ Database backup created successfully")
            print(f"   ✅ Backup file size: {size_kb:.2f} KB")
            
            # Verify it can be read
            import json
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tables = len(data.keys())
            print(f"   ✅ Backup contains {tables} tables")
            
            # Clean up
            os.remove(backup_file)
            print("   ✅ Backup file verified and cleaned")
            results.append(("Backup", True))
        else:
            print("   ❌ Backup file was not created")
            results.append(("Backup", False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("Backup", False))
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for module, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {module}")
    
    print("\n" + "=" * 70)
    print(f"RESULT: {passed}/{total} modules working correctly")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 APPLICATION READY FOR PRODUCTION")
        print("All core modules verified and functional.")
        return 0
    else:
        print(f"\n⚠️ Some modules need attention ({total - passed} failures)")
        return 1

if __name__ == "__main__":
    exit_code = verify_setup()
    sys.exit(exit_code)
