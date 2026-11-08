$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python -m src.seed
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
