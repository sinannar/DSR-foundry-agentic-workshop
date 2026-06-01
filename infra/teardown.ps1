param(
  [string]$EnvironmentName = "hol"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $repoRoot

azd env select $EnvironmentName | Out-Null
azd down --force --purge --no-prompt

Pop-Location
Write-Host "azd down complete for environment '$EnvironmentName'"
