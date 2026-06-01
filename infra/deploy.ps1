param(
  [string]$ResourceGroup = "rg-foundry-hol",
  [string]$Location = "australiaeast",
  [string]$ParameterFile = "./main.parameters.json"
)

$ErrorActionPreference = "Stop"

az group create --name $ResourceGroup --location $Location | Out-Null
az deployment group create `
  --resource-group $ResourceGroup `
  --template-file ./main.bicep `
  --parameters $ParameterFile

Write-Host "Deployment complete for $ResourceGroup"
