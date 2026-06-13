# Solution — Module 09: Hosted agents

This folder contains the reference implementation for deploying the
`acl-remedy-advisor-hosted` agent to Microsoft Foundry hosted agents. Run scripts from the
repository root after activating the workshop virtual environment and populating
`shared/.env` from `shared/.env.example`.

## hosted_agent_support.py

Shared helpers used by every script in this folder: `wait_for_agent_version_active` polls a
new version until it is active, `get_latest_active_agent_version` selects the newest active
version, and `ensure_agent_identity_rbac` grants the agent's per-deploy Microsoft Entra
identity the **Foundry User** role at the Foundry account scope so the agent can call
models at runtime.

## deploy_hosted_agent_code.py

**Part 2 (primary).** Zips the agent bundle in `src/agent/` and deploys it from source
code. Foundry builds the container image remotely, so no local Docker is required.

```bash
python labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_code.py
```

## deploy_hosted_agent_container.py

**Part 1 (optional).** Builds the image with Docker, pushes it to the shared workshop Azure
Container Registry under a project-specific tag (`acl-remedy-advisor-hosted:<project>`), then
deploys the agent from that image. Requires Docker and the Azure CLI.

```bash
python labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_container.py
```

## invoke_hosted_agent.py

Creates a session against the latest active version, routes the agent endpoint to it, and
runs a short multi-turn conversation over the Responses API.

```bash
python labs/introduction-foundry-agent-service/09-hosted-agents/solution/invoke_hosted_agent.py
```

## Notes

- Attendees can assign the Foundry User role because `infra/main.bicep` grants each attendee
  a constrained Role Based Access Control Administrator role that allows assigning only that
  role to service principals.
- Hosted agents are a preview feature, so the scripts pass `allow_preview=True` and use
  `project.beta.agents` for session and endpoint operations.
