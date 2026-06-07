# Attendee Guide

This guide walks through preparing your machine and validating access before you run the
labs. For the condensed flow, see the [Attendee Quickstart](./quickstart-attendee.md).

## What your organizer provides

Your organizer provisions the shared Foundry environment and assigns you a project. Before
you start, you should have:

- Your `FOUNDRY_PROJECT_NAME` (for example, `attendee-01`).
- The shared values: `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`,
  `FOUNDRY_RESOURCE_NAME`, and `AZURE_SEARCH_SERVICE_NAME`.

With the default `foundry-user` role you can build agents and use the models your organizer
pre-deployed. You do not deploy models yourself.

## Install prerequisites

1. Install [VS Code Insiders](https://code.visualstudio.com/insiders/).
1. Install the Foundry Toolkit for VS Code from the Extensions view.
1. Install the [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
1. Install Python 3.11 or later.
1. Install the workshop Python dependencies.

   ```bash
   python -m pip install -r shared/requirements.txt
   ```

> [!NOTE]
> Screenshot placeholder — *the Foundry Toolkit extension in the VS Code Insiders Extensions
> view.* Alt text: "VS Code Insiders Extensions view with the Foundry Toolkit extension
> selected."

## Configure your environment file

1. Copy `shared/.env.example` to `.env` in the repository root.
1. Populate the values your organizer gave you:
   - `AZURE_SUBSCRIPTION_ID`
   - `AZURE_RESOURCE_GROUP`
   - `FOUNDRY_RESOURCE_NAME`
   - `FOUNDRY_PROJECT_NAME`
   - `AZURE_SEARCH_SERVICE_NAME`
1. Leave the attendee RBAC and `AZURE_SEARCH_ADMIN_KEY` values blank; those are for
   organizers.

## Sign in

```bash
az login
az account set --subscription <your-subscription-id>
```

The labs authenticate with `DefaultAzureCredential`, so signing in with the Azure CLI is
enough — no keys required.

## Validate setup

```bash
python scripts/health-check.py
```

Resolve any reported issues before starting. If the check reports a missing value, confirm
it against the assignment your organizer shared.

> [!NOTE]
> Screenshot placeholder — *a successful `health-check.py` run.* Alt text: "Terminal showing
> the health check passing for the configured Foundry project."

## Open your project

1. Sign in to the [Foundry portal](https://ai.azure.com).
1. Select the project named in your `FOUNDRY_PROJECT_NAME`.

## Run the labs

1. Begin with [Introduction to Foundry Agent Service](./labs/introduction-foundry-agent-service.md).
1. Continue through labs 01-08 in order. Each lab is independently runnable, so you can
   resume at any point.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `health-check.py` reports authentication failure | Not signed in or wrong subscription. | Re-run `az login` and `az account set --subscription <id>`. |
| Project not visible in the portal | Role not yet assigned, or wrong project name. | Confirm your `FOUNDRY_PROJECT_NAME` with your organizer or proctor. |
| Cannot deploy a model | Expected with the `foundry-user` role. | Use the models your organizer pre-deployed. |
| Cannot publish an agent (lab 08) | Publishing needs the Foundry Project Manager role. | Ask your organizer to raise your role for lab 08. |
