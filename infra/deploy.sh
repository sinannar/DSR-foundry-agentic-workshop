#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ENV_NAME="${1:-hol}"
LOCATION="${2:-australiaeast}"
RESOURCE_GROUP="${3:-rg-foundry-hol}"
ATTENDEE_COUNT="${4:-20}"

pushd "$REPO_ROOT" >/dev/null

azd env new "$ENV_NAME" --no-prompt 2>/dev/null || azd env select "$ENV_NAME"
azd env set AZURE_LOCATION "$LOCATION"
azd env set TF_VAR_location "$LOCATION"
azd env set TF_VAR_env_name "$ENV_NAME"
azd env set TF_VAR_resource_group_name "$RESOURCE_GROUP"
azd env set TF_VAR_attendee_count "$ATTENDEE_COUNT"

azd provision --no-prompt

popd >/dev/null

echo "azd provision complete for environment '$ENV_NAME'"
