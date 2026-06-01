#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="${1:-rg-foundry-hol}"
LOCATION="${2:-australiaeast}"
PARAM_FILE="${3:-./main.parameters.json}"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
az deployment group create   --resource-group "$RESOURCE_GROUP"   --template-file ./main.bicep   --parameters "$PARAM_FILE"

echo "Deployment complete for $RESOURCE_GROUP"
