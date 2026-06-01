# Azure AI Foundry Agentic Workshop (HOL)

This repository scaffolds a **3–4 hour, L200–L300 instructor-led workshop** for building agentic solutions on **Azure AI Foundry**.

## Audience
- Software engineers and technical data scientists
- Comfortable with Azure basics
- Mostly new to Azure AI Foundry

## Prerequisites
- Azure subscription with quota to deploy lab resources
- VS Code Insiders
- Foundry Toolkit for VS Code
- Python 3.11+
- Azure CLI (`az`) and Bicep CLI support
- An AI coding agent (GitHub Copilot or Claude Code)

## Agenda (3–4 hours)

| Module | Topic | Duration (min) |
|---|---|---:|
| 00 | Setup and access validation | 20 |
| 01 | Hosted agents (framework-orchestrated ReAct + tools) | 30 |
| 02 | Prompt-based agents (prompt-orchestrated ReAct + tools) | 30 |
| 03 | Multi-agent-as-tools patterns | 30 |
| 04 | Microsoft Agent Framework (Python) | 25 |
| 05 | Foundry IQ retrieval across enterprise sources | 30 |
| 06 | Foundry Toolkit for VS Code tasks | 20 |
| 07 | Foundry Toolboxes (optional) | 15 |
| 08 | Agent ID and publishing | 20 |

## Attendee setup flow
1. Deploy shared environment from `infra/`.
2. Assign each attendee their parameterized Foundry project.
3. Complete `labs/00-setup` to verify auth, tools, and project access.
4. Progress through labs in numerical order.

## Cost note
Plan for approximately **AUD 50/day** for a sandbox environment, depending on region, SKU, and usage.

## Reset between runs
Use `infra/teardown.sh` or `infra/teardown.ps1` to remove workshop resources between instructor deliveries, then redeploy with updated attendee count.

## Repository layout
- `.github/` Copilot guidance and issue/PR templates
- `infra/` idempotent infrastructure templates and deploy wrappers
- `labs/` numbered module content with `src/` starters and `solution/` placeholders
- `shared/` reusable Python utilities, common dependencies, sample data
- `docs/` instructor and facilitator assets
- `scripts/` helper scripts for lab operations
