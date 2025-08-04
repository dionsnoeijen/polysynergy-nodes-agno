<div align="center">

<img src="https://www.polysynergy.com/ps-color-logo-with-text.svg" alt="PolySynergy" width="300" style="margin-right: 40px;" />

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://agno-public.s3.us-east-1.amazonaws.com/assets/logo-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://agno-public.s3.us-east-1.amazonaws.com/assets/logo-light.svg">
  <img alt="Agno" src="https://agno-public.s3.us-east-1.amazonaws.com/assets/logo-light.svg" width="200">
</picture>

</div>

# PolySynergy Agno Nodes

> 🚀 **Get Started**: This is part of the [PolySynergy Orchestrator](https://github.com/dionsnoeijen/polysynergy-orchestrator) - a visual workflow automation platform. Start there to set up the complete system and begin building AI agent workflows.

> ⚠️ **Development Status**: This project is currently in active development and not yet ready for production use. APIs and functionality may change significantly.

A comprehensive node library for the PolySynergy orchestrator that integrates with the [Agno AI agent framework](https://github.com/agno-agi/agno). This library provides visual, drag-and-drop nodes for building sophisticated AI agent workflows and multi-agent systems within the PolySynergy ecosystem.

## 🎯 Purpose

PolySynergy Agno Nodes bridges the gap between the powerful Agno AI agent framework and visual workflow orchestration. It enables users to:

- **Build AI Agent Workflows Visually**: Create complex agent interactions using a node-based visual interface
- **Orchestrate Multi-Agent Systems**: Design teams of AI agents that can collaborate, coordinate, or route tasks
- **Integrate Research Tools**: Access academic papers, web search, financial data, and social media through pre-built tool nodes
- **Configure Agent Behavior**: Fine-tune agent settings, memory, reasoning, and response patterns through intuitive UI controls
- **Stream Real-time Interactions**: Monitor agent conversations and tool usage in real-time

## 🏗️ Architecture

### Core Components

- **AgnoAgent**: Individual AI agents with configurable personalities, tools, and behaviors
- **AgnoTeam**: Multi-agent teams with different collaboration modes (route, coordinate, collaborate)
- **PromptNode**: Simple text prompt management for agent interactions
- **Research Tools**: Pre-integrated tools for ArXiv, web search, financial data, and social platforms
- **Settings System**: Modular configuration for context, memory, knowledge, streaming, and more

### Integration Points

This library extends the PolySynergy node runner framework and integrates with:
- **Agno Framework** (MPL-2.0): Core AI agent functionality
- **OpenAI Models**: GPT-4 and other language models
- **Research APIs**: ArXiv, DuckDuckGo, Google Search, Yahoo Finance, Twitter/X
- **PolySynergy Orchestrator**: Visual workflow design and execution

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- Poetry for dependency management
- PolySynergy Orchestrator (for visual workflow design)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd polysynergy-nodes-agno

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Basic Usage

The nodes are designed to be used within the PolySynergy visual workflow builder. However, you can also use them programmatically:

```python
from polysynergy_nodes_agno.agent.agno_agent import AgnoAgent
from polysynergy_nodes_agno.agent.model_openai import ModelOpenAi

# This is a simplified example - actual usage involves the PolySynergy framework
```

## 📦 Available Nodes

### Agent Nodes
- **Agno Agent**: Create individual AI agents with custom personalities and tools
- **Agno Team**: Build collaborative agent teams with different coordination modes
- **Prompt**: Manage and route text prompts to agents and teams

### Model Nodes
- **OpenAI Model**: Configure GPT-4 and other OpenAI models

### Tool Nodes
- **ArXiv Tool**: Search and read academic papers
- **DuckDuckGo Tool**: Web search capabilities
- **Exa Tool**: AI-powered search
- **Google Search Tool**: Google search integration
- **Hacker News Tool**: Access Hacker News content
- **X/Twitter Tool**: Social media integration
- **YFinance Tool**: Financial data and market information

### Settings Nodes
Comprehensive configuration nodes for:
- Context management
- Conversation history
- Knowledge bases
- Memory systems
- Reasoning patterns
- Response formatting
- Streaming options
- Workflow orchestration

## 🔧 Development

### Project Structure

```
polysynergy_nodes_agno/
├── agent/                  # Core agent and team nodes
│   ├── agno_agent.py      # Individual agent implementation
│   ├── agno_team.py       # Multi-agent team implementation
│   ├── prompt_node.py     # Prompt management
│   ├── model_openai.py    # OpenAI model integration
│   ├── tool_*.py          # Various research and utility tools
│   ├── *_settings_*.py    # Configuration nodes
│   └── utils/             # Helper utilities
├── icons/                 # Node icons for the UI
└── tmp/                   # Temporary file storage
```

### Building

```bash
# Build the package
poetry build

# Run tests (when available)
poetry run pytest

# Format code (when configured)
poetry run black .
```

## 📋 Roadmap

- [ ] Complete core agent and team functionality
- [ ] Add comprehensive test coverage
- [ ] Implement additional AI model providers
- [ ] Expand tool ecosystem
- [ ] Add example workflows and tutorials
- [ ] Performance optimization and monitoring
- [ ] Documentation website

## 📄 License

This project is licensed under the Business Source License 1.1 (BSL 1.1).

- **Licensor**: PolySynergy BV
- **Additional Use Grant**: You may use the Licensed Work for any purpose except offering the Licensed Work as a commercial service to third parties
- **Change Date**: January 1, 2028
- **Change License**: Apache License, Version 2.0

For alternative licensing arrangements, please contact: dion@polysynergy.com

### Third-Party Licenses

This project uses the Agno framework, which is licensed under the Mozilla Public License 2.0 (MPL-2.0). See the [Agno repository](https://github.com/agno-agi/agno) for details.

## 🤝 Contributing

We welcome contributions! However, please note that this project is in early development and the contribution guidelines are still being established.

For now, please:
1. Open an issue to discuss proposed changes
2. Follow the existing code style and patterns
3. Ensure any new code includes appropriate type hints
4. Test your changes thoroughly

## 📞 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Email**: dion@polysynergy.com
- **Documentation**: See `CLAUDE.md` for development guidance

## 🙏 Acknowledgments

- [Agno Framework](https://github.com/agno-agi/agno) - The underlying AI agent framework
- OpenAI - Language model API
- The open-source community for various tool integrations
