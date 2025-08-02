# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package called `polysynergy_nodes_agno` - a node library for the PolySynergy orchestrator that integrates with the Agno AI agent framework. The project provides nodes for creating AI agents and teams within the PolySynergy workflow system.

## Development Commands

```bash
# Install dependencies
poetry install

# Build package
poetry build

# Activate virtual environment
poetry shell
```

## Architecture

### Core Components

- **AgnoAgent** (`polysynergy_nodes_agno/agent/agno_agent.py`): Main node for creating individual AI agents with configurable settings, tools, and models
- **AgnoTeam** (`polysynergy_nodes_agno/agent/agno_team.py`): Node for creating teams of agents that can collaborate in different modes (route, coordinate, collaborate)
- **ChatPlayAgent** (`polysynergy_nodes_agno/agent/chat_play_agent.py`): Simple UI node for chat interactions

### Settings System

The project uses a modular settings architecture where both agents and teams can be configured with various settings modules:

- **Agent Settings**: Context, History, Knowledge, Memory, Messaging, Reasoning, Response, Session, Storage, Streaming, Team, Tools, Workflow
- **Team Settings**: Context, History, Knowledge, Reasoning, Session, Storage, Streaming, Structured Output, System Message, Team History, Team Tools, Tools

### Tool Integration

Multiple search and research tools are available:
- **ArxivTools** (`tool_arxiv.py`): Search and read academic papers
- **DuckDuckGoTool** (`tool_duck_duck_go.py`): Web search
- **ExaTool** (`tool_exa.py`): AI-powered search
- **GoogleSearchTool** (`tool_google_search.py`): Google search
- **HackerNewsTool** (`tool_hacker_news.py`): Hacker News integration  
- **XTool** (`tool_x.py`): X/Twitter integration
- **YFinanceTool** (`tool_yfinance.py`): Financial data

### Node Runner Integration

The project extends `polysynergy_node_runner` framework:
- Nodes use `@node` decorator with metadata (name, category, icon)
- Inherit from `ServiceNode` for service-providing nodes
- Use `NodeVariableSettings` for configurable properties
- Support both dock UI and programmatic configuration
- Implement async execution patterns

### Key Utilities

Located in `utils/` directory:
- `extract_props_from_settings.py`: Extracts configuration from settings instances
- `find_connected_*` modules: Locate connected models, tools, settings, and team members
- `send_chat_stream_event.py`: Handle streaming events for the UI

## Development Notes

- Uses Poetry for dependency management
- Built on Python 3.12+
- Integrates with Agno framework for AI agent functionality
- Supports both individual agents and collaborative teams
- Implements streaming responses for real-time interaction
- Tools support both async and sync execution patterns