param(
  [string]$EnvironmentName = "hol",
  [string]$Location = "australiaeast",
  [string]$ResourceGroup = "rg-foundry-hol",
  [int]$AttendeeCount = 20
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $repoRoot

try {
  azd env new $EnvironmentName --no-prompt | Out-Null
} catch {
  azd env select $EnvironmentName | Out-Null
}

azd env set AZURE_LOCATION $Location | Out-Null
azd env set TF_VAR_location $Location | Out-Null
azd env set TF_VAR_env_name $EnvironmentName | Out-Null
azd env set TF_VAR_resource_group_name $ResourceGroup | Out-Null
azd env set TF_VAR_attendee_count $AttendeeCount | Out-Null

azd provision --no-prompt

Pop-Location
Write-Host "azd provision complete for environment '$EnvironmentName'"
