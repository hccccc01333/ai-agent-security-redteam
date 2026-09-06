# Push + submit ONE variant on afterrain42/jed-attack-v1.
# Discipline: one version, one shot; ERROR -> stop; never batch.
param(
    [Parameter(Mandatory = $true)][string]$Variant,
    [string]$Msg = ""
)

$ErrorActionPreference = "Stop"
$Project = Split-Path $PSScriptRoot -Parent
$attackPath = Join-Path $Project "variants\$Variant"
if (-not (Test-Path -LiteralPath $attackPath)) {
    throw "variant not found: $attackPath"
}

$token = [Environment]::GetEnvironmentVariable("KAGGLE_API_TOKEN", "Machine")
if (-not $token) {
    throw "Missing KAGGLE_API_TOKEN (Machine scope)"
}
$env:KAGGLE_API_TOKEN = $token.Trim()
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "`n======== $Variant ========"
Copy-Item -Force $attackPath (Join-Path $Project "attack.py")

python -c "import ast; ast.parse(open(r'$attackPath', encoding='utf-8').read()); print('ast OK')"
if ($LASTEXITCODE -ne 0) { throw "ast parse failed for $Variant" }

python (Join-Path $PSScriptRoot "validate_submission.py") --variant $attackPath
if ($LASTEXITCODE -ne 0) { throw "submission validation failed for $Variant" }

python (Join-Path $PSScriptRoot "build_submit_notebook.py") $attackPath
if ($LASTEXITCODE -ne 0) { throw "build failed for $Variant" }

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

$stage = Join-Path $Project "kernel_stage\jed-attack-v1"
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item -Force (Join-Path $Project "notebooks\kernel_submit\submit.ipynb") (Join-Path $stage "submit.ipynb")
Copy-Item -Force $metaPath (Join-Path $stage "kernel-metadata.json")

$ver = $null
for ($attempt = 1; $attempt -le 5; $attempt++) {
    $pushOut = kaggle kernels push -p $stage 2>&1 | Out-String
    Write-Host $pushOut
    if ($pushOut -match 'Kernel version (\d+) successfully pushed') {
        $ver = [int]$Matches[1]
        break
    }
    if ($pushOut -match 'CPU session limit|429|503|timeout') {
        Write-Host "push retry $attempt in 30s..."
        Start-Sleep -Seconds 30
        continue
    }
    throw "push failed: $pushOut"
}
if (-not $ver) { throw "push failed after retries" }

$s = ""
for ($i = 1; $i -le 50; $i++) {
    $s = (kaggle kernels status -k afterrain42/jed-attack-v1 2>&1 | Out-String).Trim()
    Write-Host "[$i] $s"
    if ($s -match "COMPLETE") { break }
    if ($s -match "ERROR|CANCEL") { throw "kernel failed: $s" }
    Start-Sleep -Seconds 12
}
if ($s -notmatch "COMPLETE") { throw "timeout waiting for kernel v$ver" }

$msg = if ($Msg) { $Msg } else { "one-shot $Variant" }
$submitOut = python -c @"
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
"@ 2>&1 | Out-String
Write-Host $submitOut
if ($LASTEXITCODE -ne 0) { throw "submit failed for $Variant v$ver" }
if ($submitOut -match 'limit|quota|too many|exceeded') {
    Write-Host "SUBMISSION_LIMIT: 今日额度可能已用尽，停止后续动作"
    throw "submission limit hit for $Variant"
}
$ref = ""
if ($submitOut -match 'ref.{0,4}?(\d{5,})') { $ref = $Matches[1] }
if ($ref) {
    Write-Host "Early failure watch on ref=$ref (max 3 min)..."
    for ($i = 1; $i -le 6; $i++) {
        Start-Sleep -Seconds 30
        $list = kaggle competitions submissions -c ai-agent-security-multi-step-tool-attacks 2>&1 | Out-String
        $line = ($list -split "`n" | Where-Object { $_ -match [regex]::Escape($ref) } | Select-Object -First 1)
        if ($line -match 'SubmissionStatus\.ERROR') {
            Write-Host "EARLY ERROR on ref=${ref}: $line"
            break
        }
        if ($line -match 'SubmissionStatus\.COMPLETE') {
            Write-Host "EARLY COMPLETE on ref=$ref"
            break
        }
        Write-Host "[watch $i] ref=$ref still pending"
    }
}

Write-Host "`n==== SUBMITTED $Variant v$ver ===="
kaggle competitions submissions -c ai-agent-security-multi-step-tool-attacks 2>&1 | Select-Object -First 5
