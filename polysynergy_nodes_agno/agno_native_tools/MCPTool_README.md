# MCP Tool - Model Context Protocol Integration

The MCP Tool enables Agno agents to connect to Model Context Protocol (MCP) servers, providing access to external tools, data sources, and systems through a standardized interface.

## What is MCP?

Model Context Protocol (MCP) is an open standard that provides a unified way for AI applications to connect with external systems. Think of MCP as a "USB-C port for AI applications" - it standardizes how AI models interact with different data sources and tools.

## Features

- **Multiple Connection Modes**: Connect via command, URL, or server parameters
- **Auto-Connect**: Automatically establish connections when the tool is initialized
- **Timeout Configuration**: Configurable connection timeouts
- **Server Identification**: Optional server naming for better organization

## Configuration Options

### Connection Modes

1. **Command Mode** (Default)
   - Launch an MCP server using a command
   - Example: `uvx mcp-server-git`, `npx @modelcontextprotocol/server-postgres`

2. **URL Mode**
   - Connect to an already running MCP server
   - Example: `http://localhost:3000`

3. **Server Parameters Mode**
   - Advanced configuration for complex server setups
   - Provides fine-grained control over server initialization

### Parameters

- **Connection Mode**: How to connect to the MCP server
- **Server Command**: Command to launch MCP server (command mode)
- **Server URL**: URL of running MCP server (URL mode)
- **Server Name**: Optional identifier for the MCP server
- **Connection Timeout**: Timeout in seconds (default: 30)
- **Auto Connect**: Automatically connect on initialization (default: true)

## Common MCP Servers

### Development & Code
- **Git Server**: `uvx mcp-server-git`
- **GitHub**: `npx @modelcontextprotocol/server-github`
- **Filesystem**: `uvx mcp-server-filesystem`

### Data & Analytics
- **PostgreSQL**: `npx @modelcontextprotocol/server-postgres`
- **SQLite**: `uvx mcp-server-sqlite`
- **Power BI**: Custom server implementations available

### Infrastructure
- **Kubernetes**: Community MCP servers available
- **Docker**: `uvx mcp-server-docker`
- **AWS**: Various AWS service MCP servers

## Usage Examples

### Basic Git Integration
```
Connection Mode: Command
Server Command: uvx mcp-server-git
Server Name: Git Repository Access
```

### Database Access
```
Connection Mode: Command  
Server Command: npx @modelcontextprotocol/server-postgres --connection-string postgresql://user:pass@host/db
Server Name: Production Database
```

### Kubernetes Cluster
```
Connection Mode: Command
Server Command: uvx mcp-server-kubernetes --kubeconfig ~/.kube/config
Server Name: K8s Cluster
```

### Running MCP Server
```
Connection Mode: URL
Server URL: http://localhost:3000
Server Name: Custom MCP Service
```

## Integration with Agents

Once configured, the MCP Tool provides agents with access to:
- **Tools**: Actions the agent can perform through the MCP server
- **Resources**: Data and context the MCP server provides
- **Prompts**: Pre-defined interactions available through the server

Agents can then use these capabilities naturally in their workflows, with the MCP protocol handling the standardized communication.

## Benefits

- **Ecosystem Access**: Connect to the growing MCP ecosystem
- **Standardization**: Consistent interface across different external systems
- **Scalability**: Easy to add new capabilities without custom integrations
- **Reliability**: Built on proven protocols with error handling
- **Flexibility**: Support for various connection patterns and configurations

## Best Practices

1. **Use descriptive server names** for better organization in multi-agent systems
2. **Set appropriate timeouts** based on expected server response times
3. **Test connections** in development before deploying to production
4. **Monitor MCP server health** for production deployments
5. **Use command mode** for development, URL mode for production services