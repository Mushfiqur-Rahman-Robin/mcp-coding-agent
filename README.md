# MCP Coding Agent

A powerful, decoupled coding assistant built with the Model Context Protocol (MCP) and `uv`. This project demonstrates how to separate an AI agent's reasoning capabilities (the client) from its practical tools (the server), allowing for flexible, scalable, and maintainable agentic systems.

## Core Concept

The primary goal of this project is to showcase the power of the **Model Context Protocol (MCP)**. Instead of building a monolithic agent where the tools are tightly coupled with the agent's code, we use MCP to create two distinct services:

1.  **The MCP Server:** A standalone service that hosts a suite of "tools" (e.g., file I/O, code execution, package management). It knows nothing about the agent that will use it.
2.  **The LangGraph Client:** An intelligent agent (powered by GPT-4o-mini) that connects to the MCP server, discovers the available tools, and uses them to accomplish tasks given by a user.

This architecture reduces complexity from \( M times N \) (M agents needing N tools) to \( M + N \) (M agents and N tools connect to a common protocol), making it easy to add new tools or agents without modifying the other components.

## Features

The agent is equipped with the following tools, served via the MCP server:

*   **File Management**: Create, read, and list files in the project directory.
*   **Code Execution**: Safely execute Python code within a `uv` environment.
*   **Package Management**: Add new Python packages to the project using `uv`.
*   **Project Inspection**: Initialize `uv` projects and view dependency information.

## Tech Stack

*   **Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
*   **Agent Framework**: [LangGraph](https://github.com/langchain-ai/langgraph)
*   **LLM**: OpenAI `gpt-4o-mini`
*   **Tool Server**: `mcp.server.fastmcp` (built on FastAPI/Uvicorn)
*   **Package & Environment Manager**: [uv](https://docs.astral.sh/uv/)
*   **Python Version**: 3.12+

## Project Structure

The project uses a standard `src` layout for clean, installable packaging.

```
mcp-coding-tool/
├── .venv/                   # Virtual environment managed by uv
├── pyproject.toml           # Project configuration and dependencies
├── .env                     # For storing API keys (you will create this)
└── src/
    └── coding_agent/
        ├── __init__.py      # Makes this a Python package
        ├── server.py        # The MCP tool server
        └── client.py        # The LangGraph agent client
```

## Setup and Installation

Follow these steps to get the agent running on your local machine.

### 1. Prerequisites

Ensure you have [uv](https://docs.astral.sh/uv/install/) installed.
```bash
# On macOS, Linux, or Windows (WSL)
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the Repository

```bash
git clone <your-repo-url>
cd mcp-coding-tool
```

### 3. Create Environment and Install Dependencies

`uv` will create a virtual environment and install all packages defined in `pyproject.toml`.

```bash
# Create the virtual environment in ./.venv
uv venv

# Install all dependencies
uv sync
```

### 4. Set Up Your API Key

Create a `.env` file in the root of the project directory to store your OpenAI API key.

```bash
# Create the file
touch .env

# Add your key to the file
echo 'OPENAI_API_KEY="sk-..."' > .env
```

## Running the Agent

The system requires two separate terminal sessions: one for the server and one for the client.

### Terminal 1: Start the MCP Server

This command starts the tool server, which will listen for requests from the agent.

```bash
uv run src/coding_agent/server.py
```

You should see output indicating the Uvicorn server is running on `http://127.0.0.1:8092`.

### Terminal 2: Start the Agent Client

This command starts the interactive agent client. It will connect to the server, discover its tools, and wait for your instructions.

```bash
uv run src/coding_agent/client.py
```

You can now chat with the agent and ask it to perform coding-related tasks.

## How It Works

1.  The **MCP Server** starts up, exposing functions like `create_file` and `execute_python_code` as tools available over the network.
2.  The **LangGraph Client** starts. Its `execute_task` function establishes a temporary, live session with the MCP server.
3.  Within this session, the client calls `load_mcp_tools(session)` to get a list of functional tool objects that are bound to the live session.
4.  The user provides a prompt (e.g., "create a file called hello.txt").
5.  The LangGraph agent, using a **ReAct (Reasoning and Acting)** loop, determines that it needs to use the `create_file` tool.
6.  The agent calls the tool. This sends a JSON-RPC request over HTTP to the MCP server.
7.  The server executes the `create_file` function and returns the result (e.g., "✅ File created: hello.txt").
8.  The agent receives this result, understands the task is complete, and formulates a final response to the user.


## Example Usage

```
🤖 Coding Agent Initialized!
Available commands:
  - Type your coding task
  - Type 'quit' to exit
--------------------------------------------------

💭 Enter your coding task: create a file called tmp.txt with the content "# My Project"
🔄 Processing your request...
✅ Loaded 6 tools for this task.
--- AGENT WORKFLOW STARTED ---
--- AGENT WORKFLOW FINISHED ---

🤖 Agent's Final Response:
I have successfully created the file `tmp.txt` with the content "# My Project".
```