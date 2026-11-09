function Resolve-PythonRuntime {
    $projectRuntime = Join-Path (Get-Location).Path '.venv\Scripts\python.exe'
    if (Test-Path $projectRuntime) {
        & $projectRuntime --version *> $null
        if ($LASTEXITCODE -eq 0) {
            return @{ Executable = $projectRuntime; Prefix = @() }
        }
    }

    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand -and $pythonCommand.Source -notmatch '\\Microsoft\\WindowsApps\\') {
        & $pythonCommand.Source --version *> $null
        if ($LASTEXITCODE -eq 0) {
            return @{ Executable = $pythonCommand.Source; Prefix = @() }
        }
    }

    $pythonRoot = Join-Path $env:USERPROFILE 'AppData\Local\Programs\Python'
    $installedRuntimes = @(
        (Join-Path $pythonRoot 'Python312\python.exe')
    ) + @(
        Get-ChildItem $pythonRoot -Directory -Filter 'Python3*' -ErrorAction SilentlyContinue |
            ForEach-Object { Join-Path $_.FullName 'python.exe' } |
            Where-Object { $_ -ne (Join-Path $pythonRoot 'Python312\python.exe') } |
            Sort-Object -Descending
    ) | Where-Object { Test-Path $_ }
    foreach ($runtime in $installedRuntimes) {
        & $runtime --version *> $null
        if ($LASTEXITCODE -eq 0) {
            return @{ Executable = $runtime; Prefix = @() }
        }
    }

    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        & $launcher.Source -3 --version *> $null
        if ($LASTEXITCODE -eq 0) {
            return @{ Executable = $launcher.Source; Prefix = @('-3') }
        }
    }

    throw @'
No se encontró una instalación de Python 3.11 o superior.
El lanzador `py` está presente, pero no tiene ningún runtime instalado.
Instala Python 3.11+ y vuelve a ejecutar este script.
'@
}
