<#
.SYNOPSIS
  Auto Portfolio Updater — runs update.py and logs results.
  Designed to be triggered by Windows Task Scheduler daily.

.LOGS
  Logs are written to: portfolio/logs/auto-update-YYYY-MM-DD.log
  Only the last 30 days of logs are kept.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir\.."
$LogDir = "$ScriptDir\logs"
$LogFile = "$LogDir\auto-update-$(Get-Date -Format 'yyyy-MM-dd').log"

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp  $Message" | Out-File -FilePath $LogFile -Append -Encoding utf8
    Write-Host "$Timestamp  $Message"
}

Write-Log "=== Auto Portfolio Updater started ==="
Write-Log "Project root: $ProjectRoot"
Write-Log "Python: $(python --version 2>&1)"

# Run the update script
try {
    $Output = @(& python "$ScriptDir\update.py" 2>&1)
    $ExitCode = $LASTEXITCODE

    # Write output to log
    foreach ($Line in @($Output)) {
        Write-Log $Line
    }

    if ($ExitCode -eq 0) {
        Write-Log "[OK] Portfolio updated successfully."
    } else {
        Write-Log "[WARN] update.py exited with code $ExitCode"
    }
}
catch {
    Write-Log "[ERROR] Failed to run update.py: $_"
    $ExitCode = 1
}

# Clean up logs older than 30 days
$OldLogs = Get-ChildItem "$LogDir\*.log" | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-30)
}
foreach ($OldLog in $OldLogs) {
    Remove-Item $OldLog.FullName -Force
    Write-Log "[CLEANUP] Removed old log: $($OldLog.Name)"
}

Write-Log "=== Auto Portfolio Updater finished (exit: $ExitCode) ==="
exit $ExitCode
