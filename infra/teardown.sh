#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_NAME="${1:-hol}"

pushd "$REPO_ROOT" >/dev/null
azd env select "$ENV_NAME"
azd down --force --purge --no-prompt
popd >/dev/null

echo "azd down complete for environment '$ENV_NAME'"
