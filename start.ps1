# ATELIER — one-click start (Windows)
# Usage: double-click start.bat  OR  powershell -ExecutionPolicy Bypass -File .\start.ps1
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
            $args = @($parts | Select-Object -Skip 1) + @("--version")
            $out = & $exe @args 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0 -or $out -match "Python 3") {
                return $cmd
            }
        } catch { }
    }
    return $null
}

function Find-Npm {
    $candidates = @(
        "$env:ProgramFiles\nodejs\npm.cmd",
        "${env:ProgramFiles(x86)}\nodejs\npm.cmd",
        "$env:LOCALAPPDATA\Programs\nodejs\npm.cmd",
        "$env:APPDATA\npm\npm.cmd"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    $cmd = Get-Command npm -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

function Test-PortInUse([int]$Port) {
    try {
        $c = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        return $null -ne $c
    } catch {
        return $false
    }
}

Write-Ru ""
Write-Ru "========================================" "Cyan"
Write-Ru "  ATELIER — запуск курсовой" "Cyan"
Write-Ru "========================================" "Cyan"
Write-Ru ""

# --- .env ---
if (-not (Test-Path "$Root\.env")) {
    if (Test-Path "$Root\.env.example") {
        Copy-Item "$Root\.env.example" "$Root\.env"
        Write-Ru "[ok] Создан .env из .env.example" "Green"
    }
}

# Force coursework defaults in this session (SQLite, no Redis)
$env:DATABASE_URL = "sqlite:///fashion_store.db"
$env:REDIS_URL = ""
$env:FLASK_APP = "run.py"
$env:FLASK_ENV = "development"
$env:SECRET_KEY = if ($env:SECRET_KEY) { $env:SECRET_KEY } else { "dev-secret-change-me" }
$env:JWT_SECRET_KEY = if ($env:JWT_SECRET_KEY) { $env:JWT_SECRET_KEY } else { "dev-jwt-change-me" }
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:5000/api"
$env:NEXT_PUBLIC_STORE_NAME = "ATELIER"

# --- Python ---
$py = Find-Python
if (-not $py) {
    Write-Ru "[ошибка] Python 3 не найден." "Red"
    Write-Ru "Установите с https://www.python.org/downloads/ (галочка Add to PATH)" "Yellow"
    Write-Ru "или: winget install Python.Python.3.12" "Yellow"
    Read-Host "Нажмите Enter чтобы закрыть"
    exit 1
}
Write-Ru "[ok] Python: $py" "Green"

$Backend = Join-Path $Root "fashion-store\backend"
$Frontend = Join-Path $Root "fashion-store\frontend"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"
$VenvPip = Join-Path $Backend ".venv\Scripts\pip.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Ru "[..] Создаю виртуальное окружение (.venv)..." "Yellow"
    $parts = $py -split " "
    if ($parts.Count -gt 1) {
        & $parts[0] $parts[1] -m venv "$Backend\.venv"
    } else {
        & $parts[0] -m venv "$Backend\.venv"
    }
    if (-not (Test-Path $VenvPython)) {
        Write-Ru "[ошибка] Не удалось создать .venv" "Red"
        Read-Host "Нажмите Enter чтобы закрыть"
        exit 1
    }
}

Write-Ru "[..] Устанавливаю зависимости backend..." "Yellow"
& $VenvPython -m pip install --upgrade pip --quiet
& $VenvPip install -r "$Backend\requirements.txt" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Ru "[ошибка] pip install не удался. Проверьте интернет / antivirus." "Red"
    Read-Host "Нажмите Enter чтобы закрыть"
    exit 1
}
Write-Ru "[ok] Backend зависимости готовы" "Green"

# Seed if DB missing
$DbPath = Join-Path $Backend "instance\fashion_store.db"
if (-not (Test-Path $DbPath)) {
    Write-Ru "[..] База отсутствует — заполняю демо-каталог (seed)..." "Yellow"
    Push-Location $Backend
    & $VenvPython seed.py
    Pop-Location
    if (-not (Test-Path $DbPath)) {
        Write-Ru "[ошибка] seed не создал базу. Смотрите вывод выше." "Red"
        Read-Host "Нажмите Enter чтобы закрыть"
        exit 1
    }
    Write-Ru "[ok] База и демо-данные готовы" "Green"
} else {
    Write-Ru "[ok] База уже есть (seed пропущен)" "Green"
}

# Ports
if (Test-PortInUse 5000) {
    Write-Ru "[!] Порт 5000 занят. Закройте старый сервер или запустите stop.bat" "Yellow"
}
if (Test-PortInUse 3000) {
    Write-Ru "[!] Порт 3000 занят. Закройте старый Next или запустите stop.bat" "Yellow"
}

# Start Flask in new window
$backendCmd = @"
cd /d "$Backend"
set DATABASE_URL=sqlite:///fashion_store.db
set REDIS_URL=
set FLASK_APP=run.py
set FLASK_ENV=development
set SECRET_KEY=dev-secret-change-me
set JWT_SECRET_KEY=dev-jwt-change-me
title ATELIER Backend :5000
echo.
echo  Backend: http://127.0.0.1:5000/api/health
echo  Не закрывайте это окно.
echo.
".venv\Scripts\python.exe" run.py
pause
"@
$backendBat = Join-Path $env:TEMP "atelier-backend-start.bat"
Set-Content -Path $backendBat -Value $backendCmd -Encoding ASCII
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "`"$backendBat`""
Write-Ru "[ok] Flask запускается в отдельном окне → http://127.0.0.1:5000" "Green"

# Frontend / npm
$npm = Find-Npm
if (-not $npm) {
    Write-Ru ""
    Write-Ru "[ошибка] Node.js / npm не найден — витрина (Next.js) не запустится." "Red"
    Write-Ru "Backend уже стартует. Установите Node 20 LTS:" "Yellow"
    Write-Ru "  https://nodejs.org/  (галочка Add to PATH)" "Yellow"
    Write-Ru "  или: winget install OpenJS.NodeJS.LTS" "Yellow"
    Write-Ru "После установки снова нажмите start.bat" "Yellow"
    Write-Ru ""
    Write-Ru "Демо API без UI: http://127.0.0.1:5000/api/health" "Cyan"
    Write-Ru "Логины: demo@atelier.dev / Demo123!  |  admin@atelier.dev / Admin123!" "Cyan"
    Read-Host "Нажмите Enter чтобы закрыть"
    exit 0
}

Write-Ru "[ok] npm: $npm" "Green"
if (-not (Test-Path "$Frontend\node_modules")) {
    Write-Ru "[..] Устанавливаю зависимости frontend (первый раз может занять пару минут)..." "Yellow"
    Push-Location $Frontend
    & $npm install
    $npmOk = ($LASTEXITCODE -eq 0)
    Pop-Location
    if (-not $npmOk) {
        Write-Ru "[ошибка] npm install не удался." "Red"
        Read-Host "Нажмите Enter чтобы закрыть"
        exit 1
    }
    Write-Ru "[ok] Frontend зависимости готовы" "Green"
} else {
    Write-Ru "[ok] node_modules уже есть" "Green"
}

$frontendCmd = @"
cd /d "$Frontend"
set NEXT_PUBLIC_API_URL=http://127.0.0.1:5000/api
set NEXT_PUBLIC_STORE_NAME=ATELIER
title ATELIER Frontend :3000
echo.
echo  Магазин: http://127.0.0.1:3000
echo  Не закрывайте это окно.
echo.
call "$npm" run dev
pause
"@
$frontendBat = Join-Path $env:TEMP "atelier-frontend-start.bat"
Set-Content -Path $frontendBat -Value $frontendCmd -Encoding ASCII
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "`"$frontendBat`""
Write-Ru "[ok] Next.js запускается в отдельном окне → http://127.0.0.1:3000" "Green"

Write-Ru ""
Write-Ru "Готово. Откройте в браузере:" "Cyan"
Write-Ru "  Магазин:  http://127.0.0.1:3000" "White"
Write-Ru "  API:      http://127.0.0.1:5000/api/health" "White"
Write-Ru ""
Write-Ru "Демо:  demo@atelier.dev / Demo123!" "White"
Write-Ru "Админ: admin@atelier.dev / Admin123!" "White"
Write-Ru "Промокод: WELCOME10" "White"
Write-Ru ""
Write-Ru "Остановка: stop.bat" "DarkGray"
Write-Ru ""
Start-Sleep -Seconds 2
try { Start-Process "http://127.0.0.1:3000" } catch { }
Read-Host "Нажмите Enter чтобы закрыть это окно (серверы продолжат работать)"
