from agno.agent import Agent
from agno.team import Team
from agno.tools import Toolkit
from agno.tools.mcp import MCPTools
from polysynergy_node_runner.setup_context.dock_property import dock_select_values
from polysynergy_node_runner.setup_context.node_decorator import node
from polysynergy_node_runner.setup_context.node_variable_settings import NodeVariableSettings
from polysynergy_node_runner.setup_context.service_node import ServiceNode


@node(
    name="MCP Tool",
    category="agno_native_tools",
    icon='agno.svg',
    has_enabled_switch=False,
)
class MCPTool(ServiceNode):
    """
    Model Context Protocol (MCP) Tool for Agno agents.
    Enables agents to connect to MCP servers and use their tools and resources.
    
    MCP provides a standardized way for AI applications to connect with external
    data sources and tools. This node allows Agno agents to leverage the entire
    MCP ecosystem including Kubernetes, Power BI, databases, and custom servers.
    
    Connection modes:
    - Command: Launch an MCP server using a command (e.g., "uvx mcp-server-git")
    - URL: Connect to a running MCP server at a specific URL
    - Server Parameters: Advanced configuration for complex server setups
    """

    agent_or_team: Agent | Team | None = NodeVariableSettings(
        has_in=True,
        info="Specify whether this tool is for an agent or a team.",
    )

    connection_mode: str = NodeVariableSettings(
        label="Connection Mode",
        default="command",
        dock=dock_select_values({
            "command": "Command",
            "url": "URL",
            "server_params": "Server Parameters"
        }),
        info="How to connect to the MCP server: via command, URL, or server parameters.",
    )

    command: str | None = NodeVariableSettings(
        label="Server Command",
        dock=True,
        info="Command to launch MCP server (e.g., 'uvx mcp-server-git', 'npx @modelcontextprotocol/server-postgres')",
    )

    url: str | None = NodeVariableSettings(
        label="Server URL",
        dock=True,
        info="URL of running MCP server (e.g., 'http://localhost:3000')",
    )

    server_name: str | None = NodeVariableSettings(
        label="Server Name",
        dock=True,
        info="Optional name for the MCP server (used for identification)",
    )

    timeout: int = NodeVariableSettings(
        label="Connection Timeout",
        default=30,
        dock=True,
        info="Timeout in seconds for connecting to the MCP server",
    )

    auto_connect: bool = NodeVariableSettings(
        label="Auto Connect",
        default=True,
        dock=True,
        info="Automatically connect to MCP server when tool is initialized",
    )

    def provide_instance(self) -> Toolkit:
        # Configure MCP tools based on connection mode
        if self.connection_mode == "command" and self.command:
            mcp_tools = MCPTools(
                command=self.command,
                name=self.server_name or "MCP Server"
            )
        elif self.connection_mode == "url" and self.url:
            mcp_tools = MCPTools(
                url=self.url,
                name=self.server_name or "MCP Server"
            )
        else:
            # Default to command mode with a basic server if no configuration
            mcp_tools = MCPTools(
                command="echo 'No MCP server configured'",
                name=self.server_name or "MCP Server"
            )

        return mcp_tools