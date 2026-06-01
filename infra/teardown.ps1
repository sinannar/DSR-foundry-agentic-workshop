param(
  [string]$ResourceGroup = "rg-foundry-hol"
)

$ErrorActionPreference = "Stop"
az group delete --name $ResourceGroup --yes --no-wait
Write-Host "Teardown started for $ResourceGroup"
