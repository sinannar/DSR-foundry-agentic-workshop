"""Basic workshop environment health check."""

import os
import sys

REQUIRED_ENV_VARS = [
    'AZURE_SUBSCRIPTION_ID',
    'AZURE_RESOURCE_GROUP',
    'FOUNDRY_RESOURCE_NAME',
    'FOUNDRY_PROJECT_NAME',
]


def main() -> int:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        print('Missing required environment variables:')
        for name in missing:
            print(f'- {name}')
        return 1

    print('Environment variables look good. Next: validate az login and Foundry access.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
