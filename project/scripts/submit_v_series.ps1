# Push+submit five V-series variants on afterrain42/jed-attack-v1.
$ErrorActionPreference = "Stop"
$Project = Split-Path $PSScriptRoot -Parent
$Variants = @(
    @{ File = "v1_lat_split_fill.py";   Msg = "V1 Q5 forge + v12 latency split fill 8-classify inj_close/VERBOSE" },
    @{ File = "v2_replay_sizing.py";     Msg = "V2 Q5 + v12 replay sizing warmup deduct REPLAY0.996" },
    @{ File = "v3_single_fill.py";       Msg = "V3 v12 single fill no probe slow=inj_close fast=VERBOSE" },
    @{ File = "v4_adaptive_margin.py";   Msg = "V4 Q5 + adaptive margin floor4 coef2.5 REPLAY0.996" },
    @{ File = "v5_v12_host.py";          Msg = "V5 Q5 + v12 host _label aa/ab suffix REPLAY0.996" }
)

$env:KAGGLE_API_TOKEN = ([Environment]::GetEnvironmentVariable("KAGGLE_API_TOKEN", "Machine")).Trim()
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$stage = Join-Path $env:USERPROFILE "kaggle_kernels\jed-attack-v1"
New-Item -ItemType Directory -Force -Path $stage | Out-Null

$results = @()
$verHint = 65

foreach ($v in $Variants) {
    $attackPath = Join-Path $Project "variants\$($v.File)"
    Write-Host "`n======== $($v.File) ========"
    Copy-Item -Force $attackPath (Join-Path $Project "attack.py")

    python -c "import ast; ast.parse(open(r'$attackPath', encoding='utf-8').read()); print('ast OK')"
    if ($LASTEXITCODE -ne 0) { throw "ast parse failed for $($v.File)" }

    python (Join-Path $PSScriptRoot "build_submit_notebook.py") $attackPath
    if ($LASTEXITCODE -ne 0) { throw "build failed for $($v.File)" }

    $metaPath = Join-Path $Project "notebooks\kernel_submit\kernel-metadata.json"
    python -c @"
import json
from pathlib import Path
p = Path(r'$metaPath')
meta = json.loads(p.read_text(encoding='utf-8-sig'))
meta['competition_sources'] = ['ai-agent-security-multi-step-tool-attacks']
meta['enable_gpu'] = False
meta['enable_internet'] = False
meta['code_file'] = 'submit.ipynb'
meta['id'] = 'afterrain42/jed-attack-v1'
meta['title'] = 'JED Attack v1'
p.write_bytes((json.dumps(meta, indent=2) + chr(10)).encode('utf-8'))
"@

    Copy-Item -Force (Join-Path $Project "notebooks\kernel_submit\submit.ipynb") (Join-Path $stage "submit.ipynb")
    Copy-Item -Force $metaPath (Join-Path $stage "kernel-metadata.json")

    $pushOk = $false
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        $pushOut = kaggle kernels push -p $stage 2>&1 | Out-String
        Write-Host $pushOut
        if ($pushOut -match 'Kernel version (\d+) successfully pushed') {
            $ver = [int]$Matches[1]
            $pushOk = $true
            break
        }
        if ($pushOut -match 'CPU session limit|429|503|timeout') {
            Write-Host "push retry $attempt in 30s..."
            Start-Sleep -Seconds 30
            continue
        }
        throw "push failed: $pushOut"
    }
    if (-not $pushOk) { throw "push failed after retries for $($v.File)" }
    $verHint = $ver

    for ($i = 1; $i -le 50; $i++) {
        $s = (kaggle kernels status -k afterrain42/jed-attack-v1 2>&1 | Out-String).Trim()
        Write-Host "[$i] $s"
        if ($s -match "COMPLETE") { break }
        if ($s -match "ERROR|CANCEL") { throw "kernel failed: $s" }
        Start-Sleep -Seconds 12
    }
    if ($s -notmatch "COMPLETE") { throw "timeout waiting for kernel v$ver" }

    $msg = $v.Msg
    python -c @"
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi(); api.authenticate()
resp = api.competition_submit_code(
    file_name='submission.csv',
    message='''$msg''',
    competition='ai-agent-security-multi-step-tool-attacks',
    kernel='afterrain42/jed-attack-v1',
    kernel_version=$ver,
)
print('submit', resp)
"@
    if ($LASTEXITCODE -ne 0) { throw "submit failed for $($v.File) v$ver" }
    $results += [pscustomobject]@{ File = $v.File; Version = $ver; Message = $msg }
    Start-Sleep -Seconds 3
}

Write-Host "`n==== DONE ===="
$results | Format-Table -AutoSize
kaggle competitions submissions -c ai-agent-security-multi-step-tool-attacks 2>&1 | Select-Object -First 15
