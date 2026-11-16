# Explicit opt-in Copilot SDLC launcher for Windows PowerShell.
# No plugin, global skill copy, Python package installation or project modifications.
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,
    [string]$Goal,
    [switch]$CheckOnly,
    [switch]$Isolated
)

$ErrorActionPreference = "Stop"
$frameworkRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$project = (Resolve-Path -LiteralPath $ProjectRoot).Path
if (-not (Test-Path -LiteralPath $project -PathType Container)) {
    throw "ProjectRoot is not a directory: $project"
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ is required."
}
if (-not $CheckOnly -and -not (Get-Command copilot -ErrorAction SilentlyContinue)) {
    throw "GitHub Copilot CLI was not found in PATH."
}

$oldLocation = Get-Location
$oldPythonPath = $env:PYTHONPATH
$oldCopilotHome = $env:COPILOT_HOME
try {
    $separator = [IO.Path]::PathSeparator
    $env:PYTHONPATH = if ([string]::IsNullOrEmpty($oldPythonPath)) {
        $frameworkRoot
    } else {
        "$frameworkRoot$separator$oldPythonPath"
    }
    if ($Isolated) {
        $env:COPILOT_HOME = Join-Path $HOME ".copilot-sdlc"
        New-Item -ItemType Directory -Force -Path $env:COPILOT_HOME | Out-Null
        Write-Host "Using isolated Copilot home: $env:COPILOT_HOME (separate login/settings may be required)."
    }
    Set-Location -LiteralPath $project
    & python -m sdlc.entrypoint doctor --project-root $project
    if ($LASTEXITCODE -ne 0) {
        throw "SDLC preflight failed. Resolve shadow_conflicts and retry."
    }
    if ($PSBoundParameters.ContainsKey("Goal")) {
        # Read-only context preparation; does not write a Task Contract.
        & python -m sdlc.entrypoint prepare --project-root $project --goal $Goal
        if ($LASTEXITCODE -ne 0) {
            throw "SDLC task-context preparation failed."
        }
    }
    if (-not $CheckOnly) {
        $cliArguments = @("--agent=orchestrator", "--add-dir=$frameworkRoot")
        if ($PSBoundParameters.ContainsKey("Goal")) {
            $cliArguments += @("--prompt", $Goal)
        }
        & copilot @cliArguments
        if ($LASTEXITCODE -ne 0) {
            throw "Copilot CLI exited with code $LASTEXITCODE."
        }
    }
}
finally {
    Set-Location $oldLocation
    $env:PYTHONPATH = $oldPythonPath
    $env:COPILOT_HOME = $oldCopilotHome
}
