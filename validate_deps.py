#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para validar dependências do projeto"""

import sys

print("=" * 60)
print("VALIDAÇÃO DE DEPENDÊNCIAS - PAINEL JURÍDICO v2")
print("=" * 60)

deps = {
    'customtkinter': 'UI Framework',
    'requests': 'HTTP Client',
    'sqlite3': 'Database',
}

print(f"\n✓ Python: {sys.version.split()[0]}")

print("\n=== DEPENDÊNCIAS PRINCIPAIS ===\n")

for package, desc in deps.items():
    try:
        if package == 'sqlite3':
            import sqlite3
            print(f"✓ {package:15} {desc:20} (versão {sqlite3.sqlite_version})")
        else:
            mod = __import__(package)
            version = getattr(mod, '__version__', 'desconhecida')
            print(f"✓ {package:15} {desc:20} ({version})")
    except ImportError as e:
        print(f"✗ {package:15} {desc:20} ❌ NÃO INSTALADO")

# Testar módulos locais
print("\n=== MÓDULOS DO PROJETO ===\n")

local_modules = [
    ('core.database', 'Database'),
    ('modules.api_bridge', 'API Bridge'),
    ('modules.calculadora.calc', 'Calculadora'),
    ('modules.analytics.engine', 'Analytics'),
    ('modules.ia.gerador', 'Gerador de Peças'),
    ('modules.exports.pdf', 'PDF Export'),
]

for module, desc in local_modules:
    try:
        __import__(module)
        print(f"✓ {module:30} {desc:20} ✓")
    except Exception as e:
        print(f"✗ {module:30} {desc:20} ❌ {str(e)[:30]}")

print("\n" + "=" * 60)
print("RESUMO: Validação Completa")
print("=" * 60)
