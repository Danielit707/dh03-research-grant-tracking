$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python -m pytest -q
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
