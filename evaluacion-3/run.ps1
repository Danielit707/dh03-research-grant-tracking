$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. .\python-runtime.ps1
try { $python = Resolve-PythonRuntime }
catch { Write-Host $_.Exception.Message -ForegroundColor Red; exit 1 }
$pythonPrefix = $python.Prefix

& $python.Executable @pythonPrefix -m src.seed
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
& $python.Executable @pythonPrefix -c "import inspect, src.domain; assert 'requested_amount' not in inspect.getsource(src.domain.validate_submission); print('Submission validator loaded from:', src.domain.__file__); print('requested_amount is optional')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "The selected Python runtime is loading an outdated proposal validator." -ForegroundColor Red
    exit $LASTEXITCODE
}
& $python.Executable @pythonPrefix -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
