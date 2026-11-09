$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. .\python-runtime.ps1
try { $python = Resolve-PythonRuntime }
catch { Write-Host $_.Exception.Message -ForegroundColor Red; exit 1 }
$pythonPrefix = $python.Prefix

& $python.Executable @pythonPrefix -m pytest -q
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
