param([string]$Python = '')
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonArguments = @()
if (-not $Python) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        $Python = $launcher.Source
        $pythonArguments = @('-3.12')
    } else {
        $Python = (Get-Command python -ErrorAction Stop).Source
    }
}
$runtime = & $Python @pythonArguments -c "import sys,struct,platform; print(f'{sys.version_info.major}.{sys.version_info.minor}|{struct.calcsize('P')*8}|{platform.system()}')"
if ($LASTEXITCODE -ne 0 -or $runtime -ne '3.12|64|Windows') {
    throw 'Use Python 3.12, Windows 64-bit. Example: .\setup.ps1 -Python C:\Python312\python.exe'
}
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
Push-Location -LiteralPath $projectRoot
try {
    & $Python @pythonArguments -m venv --copies (Join-Path $projectRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
    & $venvPython -m pip install --no-index --find-links (Join-Path $projectRoot 'wheelhouse') -r (Join-Path $projectRoot 'requirements.lock')
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    Write-Output 'Ready. Start the web interface with .\run_ui.ps1'
} finally {
    Pop-Location
}
