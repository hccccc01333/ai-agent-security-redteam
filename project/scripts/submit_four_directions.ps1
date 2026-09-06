# Push+submit four direction variants sequentially on afterrain42/jed-attack-v1.
$ErrorActionPreference = "Stop"
$Project = Split-Path $PSScriptRoot -Parent
$Variants = @(
    @{ File = "d1_harmony.py";            Msg = "D1 harmony: prefer inj_* when eligible" },
    @{ File = "d2_cd_exfil.py";            Msg = "D2 CD+EXFIL: Assia pack + verified CD combos" },
    @{ File = "d3_ultra_search.py";        Msg = "D3 ultra search-budget single-template fill" },
    @{ File = "d4_dense_multipost.py";     Msg = "D4 dense multipost: keep n_exfil>=2 when possible" }
)

$env:KAGGLE_API_TOKEN = ([Environment]::GetEnvironmentVariable("KAGGLE_API_TOKEN", "Machine")).Trim()
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$stage = Join-Path $env:USERPROFILE "kaggle_kernels\jed-attack-v1"
New-Item -ItemType Directory -Force -Path $stage | Out-Null

function Get-LatestKernelVersion {
    # kaggle kernels push prints "Kernel version N successfully pushed"
    # We track by counting after each push via status page is hard; parse push output.
    return $script:LastPushedVersion
}

$results = @()
$verHint = 3  # last known was v3

foreach ($v in $Variants) {
    $attackPath = Join-Path $Project "variants\$($v.File)"
    Write-Host "`n======== $($v.File) ========"
    Copy-Item -Force $attackPath (Join-Path $Project "attack.py")

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

    $pushOut = kaggle kernels push -p $stage 2>&1 | Out-String
    Write-Host $pushOut
    if ($pushOut -match 'Kernel version (\d+) successfully pushed') {
        $ver = [int]$Matches[1]
    } else {
        $verHint++
        $ver = $verHint
        Write-Host "WARN: could not parse version, assuming $ver"
    }
    $script:LastPushedVersion = $ver
    $verHint = $ver

    for ($i = 1; $i -le 40; $i++) {
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
    $results += [pscustomobject]@{ File = $v.File; Version = $ver; Message = $msg }
    Start-Sleep -Seconds 3
}

Write-Host "`n==== DONE ===="
$results | Format-Table -AutoSize
kaggle competitions submissions -c ai-agent-security-multi-step-tool-attacks 2>&1 | Select-Object -First 10
