param([switch]$Launch)
$ErrorActionPreference = 'Stop'
$taskName = 'ProxyAnalysis-JA-20261007-run01-recovery-20261008'
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runPath = Join-Path $repoRoot 'outputs/joint-affine-transfer-20261007/run-01'
$pythonPath = 'D:\Tools\Anaconda\envs\Pytorch312\pythonw.exe'
$scriptPath = Join-Path $PSScriptRoot 'recover.py'
if (-not $Launch) {
    [pscustomobject]@{TaskName=$taskName; Run=$runPath; Python=$pythonPath; Script=$scriptPath}
    exit 0
}
if ($repoRoot -ne 'F:\Program\VSCode\MyGit\ProxyAnalysis') { throw 'Workspace scope mismatch' }
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Pytorch312 pythonw missing' }
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) { throw 'Task exists; do not duplicate or overwrite' }
$existing = @(Get-CimInstance Win32_Process | Where-Object {
    $_.Name -match '^python(w)?\.exe$' -and $_.CommandLine -match 'joint_affine_transfer[\\/](runner|train|recover)\.py'
})
if ($existing.Count -gt 0) { throw 'JA process already active' }
$userName = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument ('"{0}" --run "{1}"' -f $scriptPath,$runPath) -WorkingDirectory $repoRoot
$principal = New-ScheduledTaskPrincipal -UserId $userName -LogonType Interactive -RunLevel Limited
# No trigger: launch exactly once on demand. No reboot/logon schedule, credentials or restart policy.
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 7) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$task = New-ScheduledTask -Action $action -Principal $principal -Settings $settings -Description 'One approved JA recovery run; unchanged sealed experiment, current user, no automatic retry.'
Register-ScheduledTask -TaskName $taskName -InputObject $task | Out-Null
Start-ScheduledTask -TaskName $taskName
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName,State
