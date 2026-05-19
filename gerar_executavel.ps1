# ============================================================
# PAINEL JURÍDICO v2 - GERAR EXECUTÁVEL
# ============================================================
# Este script cria um arquivo .exe pronto para usar
# Sem precisar instalar nada!
# ============================================================

Write-Host "============================================================" -ForegroundColor Green
Write-Host "PAINEL JURÍDICO v2 - GERAR EXECUTÁVEL" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

# Navegar para o projeto
$projectPath = "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"
cd $projectPath

# Verificar se pyinstaller está instalado
Write-Host "`n1. Verificando PyInstaller..." -ForegroundColor Cyan
try {
    $output = pip show pyinstaller 2>&1
    if ($output -match "Location") {
        Write-Host "✅ PyInstaller já está instalado" -ForegroundColor Green
    } else {
        throw "PyInstaller não encontrado"
    }
} catch {
    Write-Host "⚠️  Instalando PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Criar diretório para saída
Write-Host "`n2. Preparando diretório..." -ForegroundColor Cyan
if (!(Test-Path "dist")) {
    New-Item -ItemType Directory -Name "dist" | Out-Null
    Write-Host "✅ Diretório criado" -ForegroundColor Green
}

# Gerar executável
Write-Host "`n3. Gerando executável (isto pode levar 2-3 minutos)..." -ForegroundColor Cyan
Write-Host "   Por favor, aguarde..." -ForegroundColor Yellow

pyinstaller --onefile `
    --windowed `
    --name "PainelJuridico" `
    --icon=None `
    --add-data "data:data" `
    --add-data "modules:modules" `
    --add-data "core:core" `
    --hidden-import=customtkinter `
    --hidden-import=tkinter `
    --hidden-import=sqlite3 `
    --distpath="dist" `
    --buildpath="build" `
    --specpath="." `
    main.py

# Verificar se executável foi criado
Write-Host "`n4. Verificando resultado..." -ForegroundColor Cyan
$exePath = "dist\PainelJuridico.exe"

if (Test-Path $exePath) {
    Write-Host "✅ Executável criado com sucesso!" -ForegroundColor Green
    Write-Host "   Localização: $exePath" -ForegroundColor Green
    
    # Mostrar tamanho
    $size = (Get-Item $exePath).Length / 1MB
    Write-Host "   Tamanho: $([Math]::Round($size, 1)) MB" -ForegroundColor Green
    
    Write-Host "`n============================================================" -ForegroundColor Green
    Write-Host "✅ EXECUTÁVEL PRONTO PARA USAR!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    
    Write-Host "`nPara executar:" -ForegroundColor Cyan
    Write-Host "  1. Abra a pasta: dist" -ForegroundColor Gray
    Write-Host "  2. Clique duplo em: PainelJuridico.exe" -ForegroundColor Gray
    Write-Host "  3. Pronto! Aplicação abre automaticamente" -ForegroundColor Gray
    
    Write-Host "`nVocê pode:" -ForegroundColor Cyan
    Write-Host "  ✅ Logar na aplicação" -ForegroundColor Gray
    Write-Host "  ✅ Ver os dados" -ForegroundColor Gray
    Write-Host "  ✅ Usar todas as funções" -ForegroundColor Gray
    Write-Host "  ✅ Fazer testes" -ForegroundColor Gray
    
    Write-Host "`nDepois, para instalar de verdade:" -ForegroundColor Cyan
    Write-Host "  📖 Leia: DEPLOYMENT_INSTRUCTIONS.md" -ForegroundColor Gray
    Write-Host "  📖 Leia: QUICK_START.md" -ForegroundColor Gray
    
} else {
    Write-Host "❌ Erro ao gerar executável" -ForegroundColor Red
    Write-Host "Verifique os erros acima" -ForegroundColor Red
    exit 1
}

Write-Host "`n" -ForegroundColor Green
