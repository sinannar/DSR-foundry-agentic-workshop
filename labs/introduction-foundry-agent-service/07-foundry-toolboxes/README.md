# 07. Foundry Toolboxes (optional, preview)

![Diagram showing the Foundry Toolbox architecture — Build and Consume pillars expose a curated set of tools through a single MCP-compatible endpoint consumed by any agent framework.](../../../docs/assets/diagrams/foundry-toolbox.png)

**Estimated time:** 20 minutes

> [!IMPORTANT]
> **Preview notice**: Foundry Toolboxes and Tool Search are currently in **public preview**. Steps and portal UI may change as the feature evolves. See [Supplemental Terms of Use for Microsoft Azure Previews](https://azure.microsoft.com/support/legal/preview-supplemental-terms/).

<!-- markdownlint-disable-next-line MD028 -->
> [!IMPORTANT]
> This module builds on [Module 06 — Integrate MCP tools](../06-mcp-tools/README.md). Complete Module 06 before starting here. The `acl-remedy-advisor` agent must exist at v3, the MCP server must be running, and port 8080 must be publicly exposed via a dev tunnel.

<!-- markdownlint-disable-next-line MD028 -->
> [!NOTE]
> If you could not complete Module 06, start the MCP server and expose port 8080 as described in Module 06 before continuing, then run:
>
> ```bash
> python labs/introduction-foundry-agent-service/06-mcp-tools/solution/create_agent_with_mcp.py
> ```

<!-- markdownlint-disable-next-line MD028 -->
> [!TIP]
> Tick the checkbox next to each step as you complete it to track your progress through this module.

## Objectives

- Bundle the MCP server and Web Search into a single **Foundry Toolbox** managed through the portal.
- Enable **Tool Search** so the agent discovers tools by intent rather than receiving the full tool list.
- Swap the direct tool connections on `acl-remedy-advisor` for the toolbox, saving the agent configuration from wiring each tool individually.
- Confirm the updated agent produces the same quality answers using Tool Search in the run trace.

## Concepts

### What is a Foundry Toolbox?

A **Foundry Toolbox** is a centrally managed collection of tools exposed through a single MCP-compatible endpoint. Instead of each agent wiring its own connections, you define the tools once in a toolbox and any agent connects to a single URL.

Key benefits:

| Benefit | Detail |
|---|---|
| **Centralised management** | Rotate credentials, swap servers, or add new tools without redeploying agents |
| **Versioning** | Create a new toolbox version, test it, then promote it to default when ready |
| **Guardrails** | Apply a named RAI content policy to all tool inputs and outputs at the toolbox layer |
| **Discoverability** | Any agent or MCP client in the organisation can reuse the same toolbox endpoint |

### What is Tool Search?

When a toolbox contains many tools, passing all definitions to the model on every turn wastes tokens and dilutes focus. **Tool Search** solves this by replacing the full tool list with two meta-tools:

| Meta-tool | What the model does |
|---|---|
| `tool_search` | Calls with a natural-language description of what it needs; Foundry returns the matching tool definitions |
| `call_tool` | Invokes any tool returned by `tool_search` |

The model never browses a full tool list — it describes intent, discovers the right tools, and calls them. The agent instructions need to tell the model to call `tool_search` when a needed tool is not already visible.

> [!NOTE]
> Tool descriptions drive match quality. A vague or missing description causes poor discovery. Every tool added to the toolbox should have a clear description.

## Steps

### Part 1 — Verify the MCP server is still running

The toolbox will wrap the same `retail_remedy_ops` MCP server set up in Module 06. It must be running and publicly accessible before you create the toolbox.

#### 1. Confirm the server is running

- [ ] Check the MCP server terminal. It should still show:

  ```text
  Starting Retail Remedy Operations MCP server on http://0.0.0.0:8080/mcp
  ```

  If not, restart it from a terminal:

  ```bash
  python labs/introduction-foundry-agent-service/06-mcp-tools/src/server.py
  ```

#### 2. Confirm port 8080 is publicly exposed

- [ ] In VS Code, click the **PORTS** tab in the bottom panel.
- [ ] Confirm port `8080` is listed and **Visibility** shows **Public**.
- [ ] Hover over the forwarded address and copy the tunnel URL.
- [ ] Append `/mcp` to the copied URL if it is not already present. For example:

  ```text
  https://abc123-8080.devtunnels.ms/mcp
  ```

- [ ] Save this URL — you will paste it into the toolbox configuration in the next part.

---

### Part 2 — Create the toolbox in the Foundry portal

> [!NOTE]
> The Toolboxes portal UI is in preview. The exact navigation path at [ai.azure.com](https://ai.azure.com) may differ from the steps below as the portal evolves. If **Toolboxes** is not visible in your portal navigation, use the [code fallback](#code-fallback--create-the-toolbox-with-python) at the end of this part.

#### 3. Navigate to Toolboxes

- [ ] In a browser, navigate to [Microsoft Foundry](https://ai.azure.com) and sign in.
- [ ] In the left navigation, click **Build**.
- [ ] Look for a **Toolboxes** entry under **Build** (it may also appear under **Build → Agents → Tools** or **Build → Tools**).
- [ ] Click **Toolboxes** to open the toolbox management view.

#### 4. Create a new toolbox

- [ ] Click **+ Create** or **+ New toolbox**.
- [ ] Enter the following details:

  | Field | Value |
  |---|---|
  | Name | `acl-remedy-toolbox` |
  | Description | `Retail Remedy operations tools and web search for ACCC and ACL guidance` |

#### 5. Add the Web Search tool

- [ ] In the tool configuration area, click **+ Add tool**.
- [ ] Select **Web Search** from the tool picker.
- [ ] In the tool **Description** field, enter:

  ```text
  Search the web for ACCC rulings, Australian Consumer Law guidance, and current retail policy information.
  ```

  > This description is used by Tool Search to route queries. Make it specific to what users will ask about.

#### 6. Add the MCP tool

- [ ] Click **+ Add tool** again.
- [ ] Select **MCP** (or **Model Context Protocol** / **Custom MCP**) from the tool picker.
- [ ] Fill in the connection details:

  | Field | Value |
  |---|---|
  | Label / Server name | `retail_remedy_ops` |
  | Server URL | Your tunnel URL ending in `/mcp` |
  | Authentication | None / Anonymous |
  | Description | `Retail Remedy Operations tools for looking up purchases, product profiles, store policies, replacement options, and creating remedy cases.` |

- [ ] Confirm the six MCP tools are discovered from the running server: `lookup_purchase`, `get_product_profile`, `search_store_policy`, `find_replacement_options`, `draft_remedy_summary`, `create_remedy_case`.

#### 7. Enable Tool Search

- [ ] Look for a **Tool search** toggle or checkbox in the toolbox configuration.
- [ ] Enable it.

  > Enabling Tool Search adds the `toolbox_search_preview` configuration to the toolbox version. This hides the individual tools from the initial `tools/list` response and exposes them through `tool_search` instead, keeping the agent's active tool context small.

#### 8. Publish the toolbox

- [ ] Click **Publish** (or **Save** / **Create**).
- [ ] Confirm a toolbox named `acl-remedy-toolbox` at version `v1` is created and set as the default.

#### 9. Copy the toolbox MCP endpoint

- [ ] After publishing, locate the **Consumer endpoint** URL for `acl-remedy-toolbox`. It has the form:

  ```text
  https://<account>.services.ai.azure.com/api/projects/<project>/toolboxes/acl-remedy-toolbox/mcp?api-version=v1
  ```

- [ ] Copy this URL and keep it handy — you will paste it into the agent configuration in Part 3.

#### Code fallback — Create the toolbox with Python

> [!TIP]
> If the portal does not expose Toolboxes in your region yet, run the fallback script to create the toolbox through the Python SDK. The MCP server must be running and `MCP_SERVER_URL` must be set in your `.env` file.
>
> ```bash
> python labs/introduction-foundry-agent-service/07-foundry-toolboxes/solution/setup_toolbox.py
> ```
>
> The script creates the `acl-remedy-toolbox` toolbox, enables Tool Search, prints the consumer endpoint URL, and updates `acl-remedy-advisor` to v4 automatically. You can skip Parts 3 and 4 and go straight to Part 5.

---

### Part 3 — Update the agent to use the toolbox

Replace the direct **Web Search** and **MCP** connections on `acl-remedy-advisor` with the new toolbox endpoint. **Code Interpreter** stays as a direct tool — it is always needed for calculations and gains nothing from Tool Search routing.

#### 10. Open the agent in the Foundry portal

- [ ] In the Foundry portal, click **Build** → **Agents**.
- [ ] Click `acl-remedy-advisor` to open it.
- [ ] Confirm the active version is **v3**.

#### 11. Remove the direct Web Search tool

- [ ] In the **TOOL** section of the agent editor, locate the **Web search** entry.
- [ ] Click the remove / delete icon next to it and confirm.

#### 12. Remove the direct MCP tool

- [ ] In the **TOOL** section, locate the `retail_remedy_ops` MCP entry.
- [ ] Click the remove / delete icon next to it and confirm.

  > The agent now has only **Code Interpreter** as a directly attached tool.

#### 13. Add the toolbox as a tool

- [ ] Click **+ Add tool** in the **TOOL** section.
- [ ] In the tool picker, look for a **Toolbox** option. If it is available, select it and choose `acl-remedy-toolbox` from the list.
- [ ] If only an **MCP** option is available, select that and fill in:

  | Field | Value |
  |---|---|
  | Label / Name | `acl_remedy_toolbox` |
  | Server URL | The consumer endpoint you copied in Step 9 |
  | Authentication | Azure AD / Entra (scope `https://ai.azure.com/.default`) |

  > [!IMPORTANT]
  > When using the generic MCP option, you may need to add the custom header `Foundry-Features: Toolboxes=V1Preview`. The toolbox endpoint rejects requests that omit this header. If the portal Agent Builder does not have a header field, use the code fallback script from Step 9 instead (it handles this automatically).

- [ ] Save the tool connection.

#### 14. Update the agent instructions

Tool Search works best when the model is guided to use it. Update the instructions to replace the direct MCP tool-boundary paragraph added in Module 06.

- [ ] Scroll to the **Instructions** field in the agent editor.
- [ ] Find and replace the paragraph that begins *"Use the retail operations MCP tools when a question includes a receipt ID…"* with the following:

  ```text
  You have access to a toolbox that provides retail operations tools and web search.
  When you need a tool that is not already in your tool list, call tool_search with a
  natural-language description of the capability you need before responding that you
  cannot help.

  Use the retail operations tools when a question includes a receipt ID, customer ID,
  or product ID, or when staff ask about store policy, warranty details, or replacement
  availability. Use web search to look up ACCC rulings, Australian Consumer Law guidance,
  or current retail policy information. Use code interpreter to perform calculations such
  as pro-rata refund amounts.

  Do not invent purchase, warranty, policy, or stock details — always call tool_search
  first if the tool you need is not already visible, then use the discovered tool.
  ```

#### 15. Save as v4

- [ ] Click **Save to Foundry** in the agent editor.
- [ ] Confirm the version increments to **v4**.

  > Version history: v1 — Web search only; v2 — + Code Interpreter; v3 — + direct MCP; v4 — Code Interpreter (direct) + toolbox with Tool Search.

---

### Part 4 — Test the updated agent

#### 16. Send the battery-failure test prompt

- [ ] Open the playground for `acl-remedy-advisor v4` in the Foundry portal.
- [ ] Paste the following prompt and send it:

  ```text
  Receipt R-1007 is for a laptop bought by customer C-1042. The battery now only
  holds 20% charge after 14 months of normal use. Check our records and store policy,
  then advise the retail staff member what remedy to offer under Australian Consumer Law.
  Include any replacement options and calculate a reasonable pro-rata refund.
  ```

- [ ] Watch the run trace. Confirm `tool_search` is called with a relevant query before the underlying tools are invoked.

#### 17. Inspect the run trace

- [ ] Open the **Run** trace in the playground or the Runs panel.
- [ ] Confirm a `tool_search` call appears early in the trace with a natural-language query such as `"retail purchase lookup"` or `"store policy for warranty"`.
- [ ] Confirm the retail operations MCP tools (`lookup_purchase`, `get_product_profile`, `search_store_policy`) are called after being discovered.
- [ ] Confirm **Code Interpreter** is called directly for the pro-rata refund calculation (it does not go through `tool_search`).
- [ ] Confirm the final response includes a remedy recommendation citing store policy and ACL.

---

## Validation

- The `acl-remedy-toolbox` toolbox exists in your Foundry project containing Web Search, the `retail_remedy_ops` MCP server, and Tool Search enabled.
- The `acl-remedy-advisor` agent is at **v4** with **Code Interpreter** as the only direct tool and the toolbox connected as an MCP endpoint.
- The battery-failure test prompt triggers a `tool_search` call visible in the run trace before the underlying retail tools are invoked.
- The run trace shows Code Interpreter called directly for the pro-rata calculation.
- The final response includes a clear remedy recommendation with policy citations.

## Troubleshooting

- **Toolboxes not visible in the portal:** This preview feature may not appear in all regions or portal versions. Use the Python SDK fallback script (`solution/setup_toolbox.py`) to create the toolbox and update the agent.
- **`tool_search` is never called:** The model may not know it can search for tools. Add the sentence *"call `tool_search` with a description of what you need before responding that you cannot help"* to the agent instructions and re-save.
- **`tool_search` returns no results:** Tool descriptions drive discovery. Ensure the Web Search and MCP tools have clear, specific descriptions in the toolbox definition. Publish a new toolbox version with improved descriptions.
- **`Foundry-Features` header error:** Confirm the header `Foundry-Features: Toolboxes=V1Preview` is included on the MCP connection to the toolbox endpoint. Without this header the endpoint returns an error.
- **MCP tools not discovered during toolbox creation:** Confirm the MCP server is running and the tunnel URL is still publicly accessible. Restart the server and re-expose port 8080 if needed, then re-create the toolbox with the updated URL.
- **Agent still calls old direct tools:** Confirm v4 is the active version. If the portal saved without the toolbox connection, use `solution/setup_toolbox.py` to create v4 via the SDK.
- **This is an optional module.** If the toolbox feature is not available in your environment, skip this module — later modules do not depend on it.
