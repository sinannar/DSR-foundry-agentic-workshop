#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="${1:-rg-foundry-hol}"
az group delete --name "$RESOURCE_GROUP" --yes --no-wait

echo "Teardown started for $RESOURCE_GROUP"
