# ATELIER — one-click start (Flask only, no Node)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Write-Ru([string]$msg, [string]$color = "White") {
    Write-Host $msg -ForegroundColor $color
}

function Find-Python {
    foreach ($cmd in @("py -3", "python", "python3")) {
        try {
            $parts = $cmd -split " "
            $exe = $parts[0]
            $verArgs = @($parts | Select-Object -Skip 1) + @("--version")
            $out = & $exe @verArgs 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0 -or $out -match "Python 3") { return $cmd }
        } catch { }
    }
    return $null
}

function Test-PortInUse([int]$Port) {
    try {
        return $null -ne (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    } catch { return $false }
}

Write-Ru ""
Write-Ru "========================================" "Cyan"
Write-Ru "  ATELIER — запуск (только Flask)" "Cyan"
Write-Ru "========================================" "Cyan"
Write-Ru ""

if (-not (Test-Path "$Root\.env")) {
    if (Test-Path "$Root\.env.example") {
        Copy-Item "$Root\.env.example" "$Root\.env"
        Write-Ru "[ok] Создан .env из .env.example" "Green"
    }
}

$env:DATABASE_URL = "sqlite:///fashion_store.db"
$env:REDIS_URL = ""
$env:FLASK_APP = "run.py"
$env:FLASK_ENV = "development"
$env:SECRET_KEY = if ($env:SECRET_KEY) { $env:SECRET_KEY } else { "dev-secret-change-me" }
$env:JWT_SECRET_KEY = if ($env:JWT_SECRET_KEY) { $env:JWT_SECRET_KEY } else { "dev-jwt-change-me" }
$env:FRONTEND_URL = "http://127.0.0.1:5000"
$env:BACKEND_URL = "http://127.0.0.1:5000"
$env:YOOKASSA_RETURN_URL = "http://127.0.0.1:5000/checkout/success"

$py = Find-Python
if (-not $py) {
    Write-Ru "[ошибка] Python 3 не найден." "Red"
    Write-Ru "Установите: https://www.python.org/downloads/ (Add to PATH)" "Yellow"
    Write-Ru "или: winget install Python.Python.3.12" "Yellow"
    Read-Host "Enter чтобы закрыть"
    exit 1
}
Write-Ru "[ok] Python: $py" "Green"

$Backend = Join-Path $Root "fashion-store\backend"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"
$VenvPip = Join-Path $Backend ".venv\Scripts\pip.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Ru "[..] Создаю .venv..." "Yellow"
    $parts = $py -split " "
    if ($parts.Count -gt 1) { & $parts[0] $parts[1] -m venv "$Backend\.venv" }
    else { & $parts[0] -m venv "$Backend\.venv" }
    if (-not (Test-Path $VenvPython)) {
        Write-Ru "[ошибка] Не удалось создать .venv" "Red"
        Read-Host "Enter чтобы закрыть"
        exit 1
    }
}

Write-Ru "[..] pip install..." "Yellow"
& $VenvPython -m pip install --upgrade pip --quiet
& $VenvPip install -r "$Backend\requirements.txt" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Ru "[ошибка] pip install не удался" "Red"
    Read-Host "Enter чтобы закрыть"
    exit 1
}
Write-Ru "[ok] Зависимости готовы" "Green"

$DbPath = Join-Path $Backend "instance\fashion_store.db"
if (-not (Test-Path $DbPath)) {
    Write-Ru "[..] Seed базы..." "Yellow"
    Push-Location $Backend
    & $VenvPython seed.py
    Pop-Location
    if (-not (Test-Path $DbPath)) {
        Write-Ru "[ошибка] seed не создал БД" "Red"
        Read-Host "Enter чтобы закрыть"
        exit 1
    }
    Write-Ru "[ok] База готова" "Green"
} else {
    Write-Ru "[ok] База уже есть" "Green"
}

if (Test-PortInUse 5000) {
    Write-Ru "[!] Порт 5000 занят — запустите stop.bat или закройте старый процесс" "Yellow"
}

$backendCmd = @"
cd /d "$Backend"
set DATABASE_URL=sqlite:///fashion_store.db
set REDIS_URL=
set FLASK_APP=run.py
set FLASK_ENV=development
set SECRET_KEY=dev-secret-change-me
set JWT_SECRET_KEY=dev-jwt-change-me
set FRONTEND_URL=http://127.0.0.1:5000
set BACKEND_URL=http://127.0.0.1:5000
set YOOKASSA_RETURN_URL=http://127.0.0.1:5000/checkout/success
title ATELIER Flask :5000
echo.
echo  Магазин: http://127.0.0.1:5000
echo  API:     http://127.0.0.1:5000/api/health
echo  Не закрывайте это окно.
echo.
".venv\Scripts\python.exe" run.py
pause
"@
$backendBat = Join-Path $env:TEMP "atelier-flask-start.bat"
Set-Content -Path $backendBat -Value $backendCmd -Encoding ASCII
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "`"$backendBat`""

Write-Ru ""
Write-Ru "[ok] Flask запущен" "Green"
Write-Ru "  Магазин: http://127.0.0.1:5000" "Cyan"
Write-Ru "  Демо:    demo@atelier.dev / Demo123!" "White"
Write-Ru "  Админ:   admin@atelier.dev / Admin123!" "White"
Write-Ru "  Стоп:    stop.bat" "DarkGray"
Write-Ru ""
Start-Sleep -Seconds 2
try { Start-Process "http://127.0.0.1:5000" } catch { }
Read-Host "Enter чтобы закрыть это окно (сервер продолжит работать)"
