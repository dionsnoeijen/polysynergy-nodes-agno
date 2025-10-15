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

**Session Properties**: `session_id` and `session_name` are now available directly on the main AgnoAgent and AgnoTeam nodes as input fields, allowing direct configuration without requiring separate session settings nodes. These properties can be connected from prompt nodes or set directly on the agent/team.

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

### Agno Database Architecture (v2)

The project uses Agno v2's unified `BaseDb` interface for all persistence needs:

#### Database Nodes (`agno_db/`)
Provide complete persistence for sessions, memory, metrics, and knowledge:
- **SqliteDatabase**: SQLite-backed database for local development
- **PostgreSQLDatabase**: PostgreSQL-backed database for production (ideal for large sessions)
- **DynamoDBDatabase**: DynamoDB-backed database for serverless deployments
- All use `agno.db.base.BaseDb` interface
- Provide `provide_db_settings()` for agent configuration
- Support tenant-prefixed table names for multi-tenancy

**Key Features**:
- Unified interface across all database types
- Configurable table names for sessions, memory, metrics, evals, and knowledge
- History settings: `add_history_to_context`, `num_history_runs`, `read_chat_history`
- Memory settings: `enable_user_memories`

#### Type Pattern for Frontend Recognition
**IMPORTANT**: Always use base interface types in NodeVariableSettings:
```python
# Correct - uses base interface type
db_instance: BaseDb | None = NodeVariableSettings(...)
vector_db_instance: VectorDb | None = NodeVariableSettings(...)
knowledge_base_instance: AgentKnowledge | None = NodeVariableSettings(...)

# Wrong - frontend won't recognize dependency
db_instance: SqliteDb | None = NodeVariableSettings(...)
vector_db_instance: LanceDb | None = NodeVariableSettings(...)
knowledge_base_instance: PDFUrlKnowledgeBase | None = NodeVariableSettings(...)
```

The frontend requires base interface types (`BaseDb`, `VectorDb`, `AgentKnowledge`) to:
- Display proper connection types in the UI
- Enable dependency resolution between nodes
- Show full module paths for type matching

### Knowledge Management Architecture

The project implements a flexible knowledge management system following Agno's architecture:

#### Vector Database Nodes (`agno_vectordb/`)
Provide vector storage services that can be connected to any knowledge base:
- **LanceDBVectorDB**: High-performance vector database built on Apache Arrow
- Future: QdrantVectorDB, ChromaVectorDB, etc.

#### Knowledge Base Nodes (`agno_knowledge/`)
Transform various data sources into knowledge bases using connected vector databases:
- **PDFUrlKnowledge**: Load PDF documents from URLs with metadata filtering
- Future: PDFFileKnowledge, TextKnowledge, WebKnowledge, etc.

#### Flow Pattern
```
LanceDBVectorDB → PDFUrlKnowledge → AgentSettingsKnowledge → Agent
     ↓                    ↓                    ↓              ↓
 VectorDb instance  →  AgentKnowledge  →    knowledge    →  Agent()
```

This architecture provides:
- **Pluggable Vector Storage**: Any vector DB can be used with any knowledge source
- **Flexible Knowledge Sources**: PDF, text, web, etc. work with any vector DB
- **Agno Compatibility**: Follows exact pattern from Agno documentation

### Service Node Development Patterns

#### Critical Service Node Rules
**IMPORTANT**: When developing service nodes, follow these patterns:

1. **Return Type Matching**: Always use base interface types for output variables:
   ```python
   # Correct - frontend can detect compatibility
   vector_db_instance: VectorDb | None = NodeVariableSettings(...)
   
   # Wrong - frontend won't recognize connections
   vector_db_instance: LanceDb | None = NodeVariableSettings(...)
   ```

2. **Avoid Redundant Execute Methods**: Service nodes should NOT implement `execute()` unless specifically needed:
   ```python
   # Correct - only implement provide_instance()
   async def provide_instance(self) -> VectorDb:
       # Create and return instance
       return self.vector_db_instance
   
   # Wrong - leads to double instantiation
   async def execute(self):
       await self.provide_instance()  # Redundant call
   ```

3. **Single Instantiation**: The framework calls `provide_instance()` automatically when needed. Adding `execute()` that calls `provide_instance()` causes the instance to be created twice.

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