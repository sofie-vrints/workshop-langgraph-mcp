# MCP Workshop - LangGraph Chatbot Development

This workspace is set up for the **MCP (Model Context Protocol) with LangGraph** workshop.

## Project Overview
- **Workshop Repository**: https://github.com/DiegoLigtenberg/workshop-langgraph-mcp
- **Purpose**: Learn to build AI chatbots using MCP and LangGraph
- **Language**: Python
- **Package Manager**: Poetry

## Prerequisites
- [x] Python 3.x installed
- [x] Poetry installed
- [x] Container environment (Docker Desktop, Podman, or Rancher)

## Quick Start Commands
```bash
# Clone the repository
git clone https://github.com/DiegoLigtenberg/workshop-langgraph-mcp.git
cd workshop-langgraph-mcp

# Configure Poetry to create venv in project
poetry config virtualenvs.in-project true

# Update lock file and install dependencies
poetry lock
poetry install
```

## VS Code Setup
1. Press `Cmd+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose the `.venv` one from your project

## Project Examples
- `01_langgraph_agent_no_mcp.py` - Basic LangGraph agent with local tools (no MCP)
- `02_mcp_stdio_local.py` - LangGraph agent with local MCP servers via stdio transport
- `03_mcp_stdio_external_package.py` - LangGraph agent with external MCP packages via stdio
- `04_mcp_http_external_package.py` - LangGraph agent with remote HTTP MCP servers

## MCP Architecture
MCP enables AI applications to securely connect to external tools and data sources:
- **MCP Servers**: Provide specific tools and capabilities
- **MCP Client**: Bridge between AI applications and MCP servers
- **MCP Host**: The AI application that uses MCP tools

## Resources
- [MCP Servers Directory](https://mcpservers.org/)
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
