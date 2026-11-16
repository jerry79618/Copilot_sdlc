# Backward-compatible alias. New entry: scripts/start-poteto.ps1.
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,
    [string]$Goal,
    [switch]$CheckOnly,
    [switch]$Isolated,
    [switch]$UseLegacyOrchestrator
)

& (Join-Path $PSScriptRoot "start-poteto.ps1") @PSBoundParameters
