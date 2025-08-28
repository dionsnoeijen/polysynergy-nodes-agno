import pytest
from polysynergy_nodes_agno.agno_native_tools.tool_mcp import MCPTool


async def test_mcp_tool_creation():
    """Test that MCPTool can be instantiated."""
    tool = MCPTool()
    assert tool is not None
    assert tool.connection_mode == "command"
    assert tool.timeout == 30
    assert tool.auto_connect == True


async def test_mcp_tool_command_mode():
    """Test MCPTool with command mode configuration."""
    tool = MCPTool()
    tool.connection_mode = "command"
    tool.command = "uvx mcp-server-git"
    tool.server_name = "Git MCP Server"
    
    instance = await tool.provide_instance()
    assert instance is not None


async def test_mcp_tool_url_mode():
    """Test MCPTool with URL mode configuration."""
    tool = MCPTool()
    tool.connection_mode = "url"
    tool.url = "http://localhost:3000"
    tool.server_name = "Local MCP Server"
    
    instance = await tool.provide_instance()
    assert instance is not None


async def test_mcp_tool_default_fallback():
    """Test MCPTool fallback when no configuration is provided."""
    tool = MCPTool()
    tool.connection_mode = "server_params"  # No server_params provided
    
    instance = await tool.provide_instance()
    assert instance is not None  # Should create default instance