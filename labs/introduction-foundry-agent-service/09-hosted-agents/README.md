# 09. Build and run a hosted agent

**Estimated time:** 35 minutes

> [!IMPORTANT]
> This module builds on [Module 08 — Use Agent Framework for Python](../08-agent-framework-python/README.md). You now take the same `acl-remedy-advisor` tools you have used throughout the workshop, package them into a **code-first agent**, and deploy it as a **hosted agent** that runs fully managed inside your Foundry project.

<!-- markdownlint-disable-next-line MD028 -->
> [!NOTE]
> Hosted agents are a **preview** feature of Microsoft Foundry Agent Service. The Python SDK calls in this module pass `allow_preview=True` and use `project.beta.agents` for the preview session and endpoint operations.

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Understand what a hosted agent is and how it differs from the Prompt Agents you built in Modules 04-07.
- Package a code-first Agent Framework agent that serves the **Responses** protocol.
- Deploy the agent two ways: from a **container image** (Part 1) and from **source code** (Part 2).
- Grant the hosted agent's own Microsoft Entra identity the role it needs to call models.
- Invoke the deployed hosted agent from Python and hold a multi-turn conversation.

## Concepts

### What a hosted agent is

A **Prompt Agent** (Modules 04-07) is configured *declaratively* on the Foundry
service — you give it a model, instructions, and tools, and Foundry runs it. A
**hosted agent** is different: *you* write the agent as a container that Foundry
hosts and scales for you. The agent's logic, tools, and dependencies all live in
your code, while Foundry provides a managed endpoint, autoscaling, observability,
and a dedicated identity.

Use a hosted agent when you need full control of the agent's orchestration — custom
tools, your own libraries, or logic that does not fit the declarative Prompt Agent
model — but still want a fully managed, serverless endpoint.

### The Responses protocol and ResponsesHostServer

A hosted agent communicates over the OpenAI-compatible **Responses** protocol on
port **8088**. You do not implement that protocol by hand. The Agent Framework's
`ResponsesHostServer` wraps your `Agent` and serves the protocol for you:

```python
from agent_framework_foundry_hosting import ResponsesHostServer

ResponsesHostServer(agent).run()
```

The agent bundle for this module lives in [`src/agent/`](src/agent/):

| File | Purpose |
|------|---------|
| `main.py` | Builds the `acl-remedy-advisor-hosted` agent and serves it with `ResponsesHostServer`. |
| `retail_tools.py` | The six retail remedy tools (the same set you used in Module 06). |
| `retail-operations.json` | Sample purchases, products, policies, and inventory. |
| `requirements.txt`, `Dockerfile`, `agent.yaml`, `.dockerignore` | Packaging for the hosted agent. |

### Two ways to deploy

- **Part 1 — from a container image.** You build the image with Docker, push it to
  the shared workshop **Azure Container Registry (ACR)**, and point Foundry at the
  image. This shows exactly what is happening under the hood.
- **Part 2 — from source code (preview).** You hand Foundry a zip of `src/agent/` and
  it builds the image *remotely* — no local Docker required. This is the recommended
  path for this workshop.

### The agent's own identity

Every hosted agent gets its **own Microsoft Entra agent identity** when you deploy
it. That identity — not yours — calls the model at runtime, so it needs the
**Foundry User** role on the Foundry account. The identity only exists *after* the
agent version is created, so the role cannot be pre-assigned in infrastructure. The
deploy scripts assign it for you with `ensure_agent_identity_rbac`. Your workshop
project was provisioned with a constrained Role Based Access Control Administrator
role that lets you assign *only* that one role to service principals, so this stays
within least privilege.

### Avoiding collisions in a shared workshop

All attendees share one Azure Container Registry. Part 1 tags the image with your
**project name** (`acl-remedy-advisor-hosted:<project>`), and every hosted agent is
scoped to your own project, so attendees never overwrite each other.

## Steps

> [!NOTE]
> The scripts in this module run Python. Confirm your `.venv` virtual environment is active before running them — look for the `(.venv)` prefix in your terminal prompt. If it is not active, run `.venv\Scripts\Activate.ps1` (Windows PowerShell) or `source .venv/bin/activate` (macOS / Linux) from the repository root.

### Prepare

- [ ] Activate the `.venv` virtual environment from the repository root and confirm the shared dependencies are installed:

   ```bash
   python -m pip install -r shared/requirements.txt
   ```

- [ ] Sign in with the Azure CLI so `DefaultAzureCredential` can authenticate, and load your environment values:

   ```bash
   az login
   azd env get-values
   ```

   > [!NOTE]
   > Confirm your `.env` file sets `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `FOUNDRY_RESOURCE_NAME`, `AZURE_CONTAINER_REGISTRY_NAME`, and `AZURE_CONTAINER_REGISTRY_ENDPOINT`. `HOSTED_AGENT_NAME` defaults to `acl-remedy-advisor-hosted` and `AGENT_MODEL` defaults to `chat`.

- [ ] Review the agent bundle in `src/agent/` — open `main.py` and `retail_tools.py` to see the six tools the hosted agent exposes.

### Part 1 — deploy from a container image (optional)

> [!NOTE]
> This part needs **Docker** and the **Azure CLI**. If Docker is not available in your environment, skip straight to **Part 2** — it deploys the same agent without Docker.

- [ ] Deploy the agent from a container image. The script builds for `linux/amd64`, logs in to the shared registry, pushes the image under your project-specific tag, creates the hosted agent version, waits for it to become active, and assigns the agent identity the Foundry User role:

   ```bash
   python labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_container.py
   ```

- [ ] Watch the status messages until you see `Hosted agent acl-remedy-advisor-hosted is active.`

### Part 2 — deploy from source code (preview, recommended)

- [ ] Open [`src/starter.py`](src/starter.py) and complete the three TODOs to build the `CreateAgentVersionFromCodeContent`, create the version from code, and wait for it to become active. The completed reference is in [`solution/deploy_hosted_agent_code.py`](solution/deploy_hosted_agent_code.py).

- [ ] Run your completed starter to deploy the agent from source code. Foundry zips `src/agent/`, builds the image remotely, and runs it as a hosted agent:

   ```bash
   python labs/introduction-foundry-agent-service/09-hosted-agents/src/starter.py
   ```

   > [!TIP]
   > If you get stuck, run the reference implementation instead:
   >
   > ```bash
   > python labs/introduction-foundry-agent-service/09-hosted-agents/solution/deploy_hosted_agent_code.py
   > ```

- [ ] Wait until the script reports `Hosted agent acl-remedy-advisor-hosted is active.`

### Invoke the hosted agent

- [ ] Chat with the deployed hosted agent. The script selects the latest active version, opens a session, and runs a two-turn conversation over the Responses API:

   ```bash
   python labs/introduction-foundry-agent-service/09-hosted-agents/solution/invoke_hosted_agent.py
   ```

- [ ] Confirm the second turn (the follow-up about the original box and charger) builds on the answer from the first turn.

- [ ] In the Foundry portal, open **Agents** and confirm `acl-remedy-advisor-hosted` appears with an active version.

## Validation

- The deploy script prints `Hosted agent acl-remedy-advisor-hosted is active.`
- `invoke_hosted_agent.py` prints a grounded remedy answer for the first prompt and a context-aware answer for the follow-up.
- `acl-remedy-advisor-hosted` appears in the **Agents** list in the Foundry portal with an active version.
- The hosted agent calls its retail tools (for example, looking up receipt `R-1007`) rather than answering generically.

## Congratulations 🎉

You shipped a code-first agent. You packaged the retail remedy tools into a hosted
agent, deployed it both from a container image and from source code, granted its own
Microsoft Entra identity the role it needs to call models, and held a multi-turn
conversation with the managed endpoint. This is the pattern for production workloads
that need custom orchestration with a fully managed, serverless runtime.

> [!TIP]
> **Next up → [Module 10: Foundry Toolboxes](../10-foundry-toolboxes/README.md)**
> Bundle your tools into a reusable Toolbox and consume it from any agent framework. No need to scroll — jump straight in!

## Troubleshooting

- **Authentication fails** — the scripts use `DefaultAzureCredential`, which relies on your Azure CLI session. Run `az login` in the terminal to re-authenticate, then retry.
- **The agent identity cannot call the model (403 at runtime)** — the Foundry User role can take a minute to propagate after deployment. Wait and retry the invoke. The deploy script already retries the assignment while the new identity propagates to Microsoft Entra ID.
- **`PrincipalNotFound` or a role-assignment error during deploy** — confirm your project was provisioned with the constrained Role Based Access Control Administrator role (Part 1 and Part 2 require it). Ask your facilitator if the role is missing.
- **`docker: command not found` (Part 1)** — Docker is not available in your environment. Use Part 2 (source-code deploy) instead.
- **The version never becomes active** — open the agent in the Foundry portal and check the version's build logs. A failed remote build usually means a dependency in `src/agent/requirements.txt` could not be installed.
- **`acl-remedy-advisor-hosted` is not found when invoking** — confirm a deploy completed successfully and that `HOSTED_AGENT_NAME` matches in your `.env`.
