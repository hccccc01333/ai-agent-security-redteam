# Push submit notebook to Kaggle (GPU, no internet).
# Requires: KAGGLE_API_TOKEN in User/Process env, or ~/.kaggle/access_token

$ErrorActionPreference = "Stop"
$ScriptsDir = $PSScriptRoot
$ProjectDir = Split-Path $ScriptsDir -Parent
$KernelDir = Join-Path $ProjectDir "notebooks\kernel_submit"
$Competition = "ai-agent-security-multi-step-tool-attacks"

function Resolve-KaggleToken {
    foreach ($scope in @("Process", "User", "Machine")) {
        $v = [Environment]::GetEnvironmentVariable("KAGGLE_API_TOKEN", $scope)
        if ($v) { return $v.Trim() }
    }
    $legacyKey = [Environment]::GetEnvironmentVariable("KAGGLE_KEY", "User")
    $legacyUser = [Environment]::GetEnvironmentVariable("KAGGLE_USERNAME", "User")
    if ($legacyKey -and $legacyUser) {
        return @{ Username = $legacyUser; Key = $legacyKey }
    }
    $access = Join-Path $env:USERPROFILE ".kaggle\access_token"
    if (Test-Path $access) {
        $t = (Get-Content $access -Raw).Trim()
        if ($t) { return $t }
    }
    return $null
}

$tokenOrCreds = Resolve-KaggleToken
if (-not $tokenOrCreds) {
    Write-Error "Missing KAGGLE_API_TOKEN. Set User env then reopen the terminal, or write ~/.kaggle/access_token"
}

$kaggleDir = Join-Path $env:USERPROFILE ".kaggle"
New-Item -ItemType Directory -Force -Path $kaggleDir | Out-Null

if ($tokenOrCreds -is [hashtable]) {
    $env:KAGGLE_USERNAME = $tokenOrCreds.Username
    $env:KAGGLE_KEY = $tokenOrCreds.Key
    @{ username = $tokenOrCreds.Username; key = $tokenOrCreds.Key } |
        ConvertTo-Json -Compress |
        Set-Content -Path (Join-Path $kaggleDir "kaggle.json") -Encoding ascii
    Write-Host "Using legacy KAGGLE_USERNAME/KAGGLE_KEY"
} else {
    $env:KAGGLE_API_TOKEN = $tokenOrCreds
    Set-Content -Path (Join-Path $kaggleDir "access_token") -Value $tokenOrCreds -NoNewline -Encoding ascii
    Write-Host "Using KAGGLE_API_TOKEN (-> ~/.kaggle/access_token)"
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

python (Join-Path $ScriptsDir "build_submit_notebook.py")
if ($LASTEXITCODE -ne 0) { throw "build_submit_notebook.py failed" }

$metaPath = Join-Path $KernelDir "kernel-metadata.json"
# PowerShell utf8 encoding writes BOM; Kaggle rejects BOM metadata.
python -c @"
import json
from pathlib import Path
p = Path(r'$metaPath')
meta = json.loads(p.read_text(encoding='utf-8-sig'))
meta['competition_sources'] = ['$Competition']
meta['enable_gpu'] = False
meta['enable_internet'] = False
meta['code_file'] = 'submit.ipynb'
kid = meta.get('id') or ''
if (not kid) or ('placeholder' in kid) or kid.startswith('localuser/'):
    meta['id'] = 'afterrain42/jed-attack-v1'
p.write_bytes((json.dumps(meta, indent=2) + '\n').encode('utf-8'))
print('meta', meta['id'], 'gpu', meta['enable_gpu'])
"@

# Kaggle CLI on Windows can choke on non-ASCII paths; push from ASCII staging dir.
$stage = Join-Path $env:USERPROFILE "kaggle_kernels\jed-attack-v1"
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item -Force (Join-Path $KernelDir "submit.ipynb") (Join-Path $stage "submit.ipynb")
Copy-Item -Force $metaPath (Join-Path $stage "kernel-metadata.json")

Write-Host "Pushing kernel from $stage ..."
kaggle kernels push -p $stage
Write-Host "Done: https://www.kaggle.com/code/afterrain42/jed-attack-v1"
Write-Host "Open notebook -> Submit to Competition (GPU / internet off)."
