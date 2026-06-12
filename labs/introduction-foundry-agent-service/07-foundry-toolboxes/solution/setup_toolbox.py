"""Create the acl-remedy-toolbox and update acl-remedy-advisor to v4.

Use this script when the Foundry portal does not yet expose the Toolboxes UI
in your region, or when the portal Agent Builder cannot add the toolbox
connection to the agent (for example, custom-header support is missing).

The script:
  1. Creates the acl-remedy-toolbox toolbox version with Web Search,
     the Retail Remedy Operations MCP server, and Tool Search enabled.
  2. Prints the toolbox consumer endpoint URL.
  3. Creates a new v4 of the acl-remedy-advisor agent that uses the
     toolbox as an MCP connection and keeps Code Interpreter direct.

Prerequisites:
  - MCP server running and publicly accessible via a dev tunnel or port
    forwarding (see Module 06 README, Part 2).
  - MCP_SERVER_URL set in your .env file to the public tunnel URL plus /mcp.
    Example: MCP_SERVER_URL=https://abc123-8080.devtunnels.ms/mcp

Usage:
    python labs/introduction-foundry-agent-service/07-foundry-toolboxes/solution/setup_toolbox.py
"""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeInterpreterTool,
    MCPTool,
    PromptAgentDefinition,
    ToolboxSearchPreviewTool,
    WebSearchTool,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

TOOLBOX_NAME = 'acl-remedy-toolbox'
TOOLBOX_DESCRIPTION = (
    'Retail Remedy operations tools and web search for ACCC and ACL guidance'
)
WEB_SEARCH_DESCRIPTION = (
    'Search the web for ACCC rulings, Australian Consumer Law guidance, '
    'and current retail policy information.'
)
MCP_DESCRIPTION = (
    'Retail Remedy Operations tools for looking up purchases, product profiles, '
    'store policies, replacement options, and creating remedy cases.'
)

INSTRUCTIONS = (
    'You are an Australian Consumer Law (ACL) Remedy Advisor for retail staff.\n'
    'When a customer reports a problem with a product, help staff determine the\n'
    'correct remedy under the ACL consumer guarantees.\n'
    '\n'
    'Distinguish between a **major failure** (the customer may choose a refund,\n'
    'replacement, or repair) and a **minor failure** (the business may choose to\n'
    'repair the product within a reasonable time, or offer a replacement or\n'
    'refund).\n'
    '\n'
    'When assessing a situation consider:\n'
    '- The type of product and its expected lifespan\n'
    '- The price paid\n'
    '- How long the customer has had the product\n'
    '- What a reasonable consumer would expect\n'
    '\n'
    'Always state clearly that you provide general guidance, not legal advice,\n'
    'and that "no refund" signs are unlawful under the ACL.\n'
    '\n'
    'Be concise and practical — retail staff need fast, clear answers in a\n'
    'busy store environment.\n'
    '\n'
    'When asked to calculate refund amounts, depreciation, pro-rata warranty\n'
    'values, or compare prices, use code interpreter to perform the calculation\n'
    'precisely and show your working.\n'
    '\n'
    'You have access to a toolbox that provides retail operations tools and web search.\n'
    'When you need a tool that is not already in your tool list, call tool_search with a\n'
    'natural-language description of the capability you need before responding that you\n'
    'cannot help.\n'
    '\n'
    'Use the retail operations tools when a question includes a receipt ID, customer ID,\n'
    'or product ID, or when staff ask about store policy, warranty details, or replacement\n'
    'availability. Use web search to look up ACCC rulings, Australian Consumer Law guidance,\n'
    'or current retail policy information. Use code interpreter to perform calculations such\n'
    'as pro-rata refund amounts.\n'
    '\n'
    'Do not invent purchase, warranty, policy, or stock details — always call tool_search\n'
    'first if the tool you need is not already visible, then use the discovered tool.'
)


def run() -> None:
    load_dotenv()

    endpoint = os.environ['FOUNDRY_PROJECT_ENDPOINT']
    agent_name = os.environ.get('AGENT_NAME', 'acl-remedy-advisor')
    mcp_server_url = os.environ.get('MCP_SERVER_URL', '').strip()

    if not mcp_server_url:
        raise ValueError(
            'MCP_SERVER_URL is not set. Start the MCP server (server.py), expose it via a dev '
            'tunnel or port forward, then set MCP_SERVER_URL to the public URL plus /mcp in your '
            '.env file. Example: MCP_SERVER_URL=https://abc123-8080.devtunnels.ms/mcp'
        )

    client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Step 1: Create the toolbox version with Web Search, MCP, and Tool Search.
    print(f'Creating toolbox: {TOOLBOX_NAME} ...')
    toolbox_version = client.beta.toolboxes.create_version(
        name=TOOLBOX_NAME,
        description=TOOLBOX_DESCRIPTION,
        tools=[
            WebSearchTool(description=WEB_SEARCH_DESCRIPTION),
            MCPTool(
                server_label='retail_remedy_ops',
                server_url=mcp_server_url,
                require_approval='never',
                description=MCP_DESCRIPTION,
            ),
            ToolboxSearchPreviewTool(),
        ],
    )
    print(f'Toolbox created: {toolbox_version.name} (version: {toolbox_version.version})')

    # Step 2: Derive the consumer endpoint URL.
    toolbox_endpoint = (
        f'{endpoint.rstrip("/")}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1'
    )
    print(f'Toolbox consumer endpoint: {toolbox_endpoint}')
    print()

    # Step 3: Create a new agent version that uses the toolbox via MCP.
    print(f'Updating agent: {agent_name} ...')
    agent = client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model='chat',
            instructions=INSTRUCTIONS,
            tools=[
                CodeInterpreterTool(),
                MCPTool(
                    server_label='acl_remedy_toolbox',
                    server_url=toolbox_endpoint,
                    require_approval='never',
                ),
            ],
        ),
    )

    print(f'Agent updated: {agent.name} (id: {agent.id}, version: {agent.version})')
    print()
    print('Next steps:')
    print('  - Open the agent playground in the Foundry portal and send a test prompt.')
    print('  - Confirm tool_search appears in the run trace before the retail tools are called.')
    print(f'  - Toolbox endpoint: {toolbox_endpoint}')


if __name__ == '__main__':
    run()
