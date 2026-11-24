# Stop ATELIER Flask (port 5000)
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "Останавливаю ATELIER (порт 5000)..." -ForegroundColor Cyan

function Stop-Port([int]$Port) {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        $procId = $c.OwningProcess
        if ($procId -and $procId -ne 0) {
            $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
            Write-Host ("  порт {0}: PID {1} ({2})" -f $Port, $procId, $proc.ProcessName)
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
}

Stop-Port 5000
Start-Sleep -Seconds 1
Stop-Port 5000
Write-Host "Готово." -ForegroundColor Green
Write-Host ""
