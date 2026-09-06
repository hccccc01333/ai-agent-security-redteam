# JED W1 score monitor (called every 2h by Windows Task Scheduler)
# Each run: sync Kaggle submissions -> write status file registry/w1_monitor_status.txt
# Status values: [time] SCORED W1=<score> / PENDING / ERROR <reason>
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$statusFile = Join-Path $root 'registry\w1_monitor_status.txt'
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'

try {
    Push-Location $root
    $out = python scripts/sync_submissions.py 2>&1 | Out-String
    Pop-Location

    $score = $null
    $reg = Join-Path $root 'registry\experiments.jsonl'
    $line = Get-Content -LiteralPath $reg -Encoding UTF8 |
        Where-Object { $_ -match '"experiment_id": "w1_probe5_fire65"' } | Select-Object -First 1
    if ($line) {
        $obj = $line | ConvertFrom-Json
        $score = $obj.metrics.public_score
    }
    if ($score -ne $null -and "$score" -ne '') {
        Set-Content -LiteralPath $statusFile -Value "[$stamp] SCORED W1=$score" -Encoding UTF8
        exit 0
    }
    Set-Content -LiteralPath $statusFile -Value "[$stamp] PENDING" -Encoding UTF8
    exit 1
} catch {
    Set-Content -LiteralPath $statusFile -Value "[$stamp] ERROR $_" -Encoding UTF8
    exit 2
}
