# Solution — Module 07: Foundry Toolboxes

This folder contains the reference implementation for Module 07.

## setup_toolbox.py

Code fallback script for attendees whose Foundry portal does not yet expose
the Toolboxes preview UI, or whose portal Agent Builder cannot add an MCP
connection with custom headers.

The script:

1. Creates the `acl-remedy-toolbox` toolbox with **Web Search**, the
   `retail_remedy_ops` MCP server, and **Tool Search** (`toolbox_search_preview`)
   enabled.
1. Prints the toolbox consumer endpoint URL.
1. Creates `acl-remedy-advisor` **v4** with **Code Interpreter** as the only
   direct tool and the toolbox connected as an MCP endpoint.

Before running:

- Start the MCP server (`server.py`) and expose port 8080 as a public tunnel
  (see Module 06 README, Part 2).
- Set `MCP_SERVER_URL` in `shared/.env` to the public tunnel URL including
  the `/mcp` suffix.

```bash
python labs/introduction-foundry-agent-service/07-foundry-toolboxes/solution/setup_toolbox.py
```

After running, open the agent playground in the Foundry portal and send the
battery-failure test prompt from the README to confirm `tool_search` appears
in the run trace before the retail operations tools are called.
