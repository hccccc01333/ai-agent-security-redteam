param(
    [Parameter(Mandatory = $true)][string]$Variant,
    [string]$Msg = ""
)

$ErrorActionPreference = "Stop"
$Project = Split-Path $PSScriptRoot -Parent
$attackPath = Join-Path $Project "variants\$Variant"
if (-not (Test-Path -LiteralPath $attackPath)) { throw "variant not found: $attackPath" }

$token = [Environment]::GetEnvironmentVariable("KAGGLE_API_TOKEN", "Machine")
if (-not $token) { throw "Missing KAGGLE_API_TOKEN (Machine scope)" }
$env:KAGGLE_API_TOKEN = $token.Trim()
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Copy-Item -Force $attackPath (Join-Path $Project "attack.py")
python (Join-Path $PSScriptRoot "build_submit_notebook.py") $attackPath
if ($LASTEXITCODE -ne 0) { throw "build failed" }

$stage = Join-Path $env:USERPROFILE "kaggle_kernels\jed-attack-v1"
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item -Force (Join-Path $Project "notebooks\kernel_submit\submit.ipynb") (Join-Path $stage "submit.ipynb")
Copy-Item -Force (Join-Path $Project "notebooks\kernel_submit\kernel-metadata.json") (Join-Path $stage "kernel-metadata.json")

$ver = $null
for ($attempt = 1; $attempt -le 5; $attempt++) {
    $pushOut = kaggle kernels push -p $stage 2>&1 | Out-String
    if ($pushOut -match 'Kernel version (\d+) successfully pushed') {
        $ver = [int]$Matches[1]; break
    }
    if ($pushOut -match '429|503|timeout|CPU session limit') {
        Write-Host "push retry $attempt"; Start-Sleep -Seconds 20; continue
    }
    throw "push failed: $pushOut"
}
if (-not $ver) { throw "push failed after retries" }

for ($i = 1; $i -le 30; $i++) {
    $s = (kaggle kernels status -k afterrain42/jed-attack-v1 2>&1 | Out-String).Trim()
    if ($s -match "COMPLETE") { break }
    if ($s -match "ERROR|CANCEL") { throw "kernel failed: $s" }
    Start-Sleep -Seconds 10
}
if ($s -notmatch "COMPLETE") { throw "kernel wait timeout" }

$msg = if ($Msg) { $Msg } else { "fast one-shot $Variant" }
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
$ref = ""
if ($submitOut -match 'ref.{0,4}?(\d{5,})') { $ref = $Matches[1] }
Write-Host "SUBMITTED $Variant v$ver ref=$ref"
