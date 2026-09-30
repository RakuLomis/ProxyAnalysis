param(
    [string]$Python = 'D:/Tools/Anaconda/envs/Pytorch312/python.exe',
    [string]$Tectonic = "$env:TEMP/proxy-paper-tools/tectonic/tectonic.exe",
    [string]$Drawio = "$env:TEMP/proxy-paper-tools/drawio/draw.io.exe"
)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$paperRoot = Join-Path $repoRoot 'docs/paper/proxy-boundary-correspondence'
Push-Location $repoRoot
try {
    foreach ($script in @('build_all.py','plot_transformations.py','make_diagrams.py','feature_appendix.py','finish_evidence.py')) {
        & $Python (Join-Path $PSScriptRoot $script)
        if ($LASTEXITCODE -ne 0) { throw "Failed: $script" }
    }
    if (!(Test-Path -LiteralPath $Tectonic)) { throw 'Specify a Tectonic executable; no installation is performed.' }
    if (!(Test-Path -LiteralPath $Drawio)) { throw 'Specify a draw.io executable; no installation is performed.' }
    foreach ($name in @('observation-boundary','calibration-framework')) {
        $source = Join-Path $paperRoot "figures/source/$name.drawio"
        $target = Join-Path $paperRoot "figures/generated/$name.pdf"
        $argsList = @('--export','--format','pdf','--crop','--output',"`"$target`"","`"$source`"")
        $job = Start-Process -FilePath $Drawio -ArgumentList $argsList -WindowStyle Hidden -Wait -PassThru
        if ($job.ExitCode -ne 0 -or !(Test-Path -LiteralPath $target)) { throw "Diagram export failed: $name" }
    }
    New-Item -ItemType Directory -Force (Join-Path $paperRoot 'build') | Out-Null
    foreach ($name in @('main','supplement')) {
        & $Tectonic (Join-Path $paperRoot "$name.tex") --outdir (Join-Path $paperRoot 'build') --keep-logs --keep-intermediates
        if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $name" }
    }
    & $Python (Join-Path $PSScriptRoot 'finish_evidence.py')
} finally { Pop-Location }
