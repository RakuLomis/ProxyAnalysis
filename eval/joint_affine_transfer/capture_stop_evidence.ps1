$ErrorActionPreference = 'Stop'
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if ($repoRoot -ne 'F:\Program\VSCode\MyGit\ProxyAnalysis') { throw 'Workspace scope mismatch' }
$target = Join-Path $repoRoot 'outputs/joint-affine-transfer-20261007/run-01/recovery'
New-Item -ItemType Directory -Path $target -Force | Out-Null
$events = @()
foreach ($logName in @('Application','System')) {
    $found = Get-WinEvent -FilterHashtable @{LogName=$logName; StartTime=[datetime]'2026-10-07T23:49:50'; EndTime=[datetime]'2026-10-07T23:50:30'}
    foreach ($event in $found) {
        if ($event.ProviderName -notmatch 'CodexSandboxService|WindowsUpdateClient|Service Control Manager|nvlddmkm') { continue }
        $xml = [xml]$event.ToXml()
        $events += [pscustomobject]@{
            LocalTime=$event.TimeCreated.ToString('o'); UtcTime=$xml.Event.System.TimeCreated.SystemTime
            Log=$logName; Provider=$event.ProviderName; Id=$event.Id; RecordId=$event.RecordId
            Data=@($xml.Event.EventData.Data | ForEach-Object { $_.InnerText })
            Xml=$event.ToXml()
        }
    }
}
[pscustomobject]@{
    CapturedLocalTime=(Get-Date).ToString('o'); Events=@($events | Sort-Object LocalTime)
    Attribution='Codex update and sandbox-service restart coincide with abrupt exit; concurrent NVIDIA driver error remains a possible contributor; no per-process termination proof.'
    LastBootUpTime=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToString('o')
} | ConvertTo-Json -Depth 8 | Out-File -LiteralPath (Join-Path $target 'stop-events-20261007.json') -Encoding utf8
Get-Item -LiteralPath (Join-Path $target 'stop-events-20261007.json') | Select-Object FullName,Length
