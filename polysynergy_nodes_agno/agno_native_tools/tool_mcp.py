from typing import Literal

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

    transport: str = NodeVariableSettings(
        label="URL Transport",
        default="streamable-http",
        dock=dock_select_values({
            "streamable-http": "Streamable HTTP",
            "sse": "Server-Sent Events (SSE)"
        }),
        info="Transport protocol for URL connections (streamable-http is recommended, SSE is deprecated)",
    )

    env: dict | None = NodeVariableSettings(
        label="Environment Variables",
        dock=True,
        info="Environment variables for the MCP server process (command mode only). Example: {'API_KEY': 'value', 'DATABASE_URL': 'postgres://...'}",
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
        info="Timeout in seconds for MCP server connections and responses",
    )

    include_tools: list[str] | None = NodeVariableSettings(
        label="Include Tools",
        dock=True,
        info="Optional list of tool names to include. If None, includes all available tools. Example: ['get_file', 'search_files']",
    )

    exclude_tools: list[str] | None = NodeVariableSettings(
        label="Exclude Tools",
        dock=True,
        info="Optional list of tool names to exclude. If None, excludes none. Example: ['dangerous_tool']",
    )

    auto_connect: bool = NodeVariableSettings(
        label="Auto Connect",
        default=True,
        dock=True,
        info="Automatically connect to MCP server when tool is initialized",
    )

    # Set by tool calling mechanism
    output: str | None = None

    async def provide_instance(self) -> Toolkit:
        """
        Create and configure an MCPTools instance based on connection settings.

        Returns:
            Toolkit: Configured MCPTools instance ready for use by agents
        """
        # Build kwargs for MCPTools - name parameter should go through kwargs to avoid conflicts
        mcp_kwargs = {}
        if self.server_name:
            mcp_kwargs['name'] = self.server_name

        # Configure MCP tools based on connection mode
        if self.connection_mode == "command" and self.command:
            mcp_tools = MCPTools(
                command=self.command,
                env=self.env,
                timeout_seconds=self.timeout,
                include_tools=self.include_tools,
                exclude_tools=self.exclude_tools,
                **mcp_kwargs
            )
        elif self.connection_mode == "url" and self.url:
            # URL mode requires transport specification
            transport: Literal["stdio", "sse", "streamable-http"] = (
                "streamable-http" if self.transport == "streamable-http" else "sse"
            )
            mcp_tools = MCPTools(
                url=self.url,
                transport=transport,
                timeout_seconds=self.timeout,
                include_tools=self.include_tools,
                exclude_tools=self.exclude_tools,
                **mcp_kwargs
            )
        else:
            # Default to command mode with a basic server if no configuration
            raise ValueError(
                "MCP Tool requires either a command or URL to be configured. "
                f"Current mode: {self.connection_mode}, command: {self.command}, url: {self.url}"
            )

        # Auto-connect if enabled
        if self.auto_connect:
            await mcp_tools.connect()

        return mcp_tools