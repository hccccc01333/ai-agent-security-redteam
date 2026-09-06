# Runs one python command from registry/py_cmd.txt in the interactive user
# environment (Task Scheduler context), redirecting output to
# registry/bridge_out.txt (+ BRIDGE_EXIT=<code>) and stderr to bridge_err.txt.
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$cmdFile = Join-Path $root 'registry\py_cmd.txt'
$outFile = Join-Path $root 'registry\bridge_out.txt'
$errFile = Join-Path $root 'registry\bridge_err.txt'

if (-not (Test-Path -LiteralPath $cmdFile)) {
    Set-Content -LiteralPath $outFile -Value "BRIDGE_NO_CMD" -Encoding UTF8
    exit 9
}
$pyArgs = (Get-Content -LiteralPath $cmdFile -Raw -Encoding UTF8).Trim()

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = 'python'
$psi.Arguments = $pyArgs
$psi.WorkingDirectory = $root
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.Environment['KAGGLE_API_TOKEN'] = [Environment]::GetEnvironmentVariable('KAGGLE_API_TOKEN', 'Machine')
$p = [System.Diagnostics.Process]::Start($psi)
$stdout = $p.StandardOutput.ReadToEnd()
$stderr = $p.StandardError.ReadToEnd()
$p.WaitForExit()
Set-Content -LiteralPath $outFile -Value $stdout -Encoding UTF8
Set-Content -LiteralPath $errFile -Value $stderr -Encoding UTF8
Add-Content -LiteralPath $outFile -Value "BRIDGE_EXIT=$($p.ExitCode)" -Encoding UTF8
exit $p.ExitCode
