# MCP Coding Agent

A powerful, decoupled coding assistant built with the Model Context Protocol (MCP) and `uv`. This project demonstrates how to separate an AI agent's reasoning capabilities (the client) from its practical tools (the server), allowing for flexible, scalable, and maintainable agentic systems.

## Core Concept

The primary goal of this project is to showcase the power of the **Model Context Protocol (MCP)**. Instead of building a monolithic agent where the tools are tightly coupled with the agent's code, we use MCP to create two distinct services:

1.  **The MCP Server:** A standalone service that hosts a suite of "tools" (e.g., file I/O, code execution, package management). It knows nothing about the agent that will use it.
2.  **The Client:** An intelligent agent that connects to the MCP server, discovers the available tools, and uses them to accomplish tasks given by a user.

This architecture reduces complexity from \( M * N \) (M agents needing N tools) to \( M + N \) (M agents and N tools connect to a common protocol), making it easy to add new tools or agents without modifying the other components.

## Features

The agent is equipped with the following tools, served via the MCP server:

*   **File Management**: Create, read, and list files in the project directory.
*   **Code Execution**: Safely execute Python code within a `uv` environment.
*   **Package Management**: Add and remove Python packages using `uv`.
*   **Project Inspection**: Initialize `uv` projects and view dependency information.

## Usage Modes

This project supports two different usage modes:

1. **Standalone Mode**: Run with the included LangGraph client
2. **Cursor IDE Integration**: Use as an MCP server within Cursor IDE

## Tech Stack

*   **Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
*   **Agent Framework**: [LangGraph](https://github.com/langchain-ai/langgraph) (standalone mode)
*   **LLM**: OpenAI `gpt-4o-mini` (standalone mode) / Claude (Cursor mode)
*   **Tool Server**: `mcp.server.fastmcp` (built on FastAPI/Uvicorn)
*   **Package & Environment Manager**: [uv](https://docs.astral.sh/uv/)
*   **Python Version**: 3.12+

## Project Structure

The project uses a standard `src` layout for clean, installable packaging.

```
mcp-coding-tool/
├── .venv/                        # Virtual environment managed by uv
├── pyproject.toml                # Project configuration and dependencies
├── .env                          # For storing API keys (standalone mode)
└── src/
    └── coding_agent/
        ├── __init__.py           # Makes this a Python package
        ├── server.py             # MCP server for standalone mode
        ├── server_for_cursor.py  # MCP server for Cursor IDE
        └── client.py             # The LangGraph agent client
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

### 4. Set Up Your API Key (for standalone mode)

Create a `.env` file in the root of the project directory to store your OpenAI API key.

```bash
# Create the file
touch .env

# Add your key to the file
echo 'OPENAI_API_KEY="sk-..."' > .env
```

## Usage

### Option 1: Standalone Mode with LangGraph Client

This mode runs the agent with its own LangGraph client interface.

#### Terminal 1: Start the MCP Server

```bash
uv run src/coding_agent/server.py
```

You should see output indicating the Uvicorn server is running on `http://127.0.0.1:8092`.

#### Terminal 2: Start the Agent Client

```bash
uv run src/coding_agent/client.py
```

You can now chat with the agent and ask it to perform coding-related tasks.

### Option 2: Cursor IDE Integration

This mode integrates the MCP server directly with Cursor IDE, allowing you to use the tools within Cursor's AI assistant.

#### 1. Configure MCP in Cursor

Create or update your `mcp.json` file in your Cursor settings directory with the following configuration:

```json
{
  "mcpServers": {
    "CodingAgent": {
      "command": "path/to/your/directory/.venv/bin/python",
      "args": [
        "path/to/your/directory/src/coding_agent/server_for_cursor.py"
      ],
      "transport": "http",
      "url": "http://localhost:8092"
    }
  }
}
```

**Note:** Update the paths to match your actual project location.

#### 2. Start Using in Cursor

1. Open Cursor IDE
2. The MCP server will automatically start when Cursor launches
3. You can now use the coding tools directly in Cursor's chat interface

#### 3. Available Commands in Cursor

Once configured, you can ask Cursor to:
- `execute_python_code`: Run Python code snippets
- `create_file`: Create new files with content
- `read_file`: Read existing files
- `list_files`: List directory contents
- `add_package`: Add Python packages using uv
- `remove_package`: Remove Python packages using uv

**Example Cursor prompts:**
- "Create a new Python file called `main.py` with a hello world function"
- "Execute this Python code and show me the output: `print('Hello, World!')`"
- "Add the requests package to this project"
- "List all files in the current directory"

## How It Works

### Standalone Mode
1.  The **MCP Server** starts up, exposing functions like `create_file` and `execute_python_code` as tools available over the network.
2.  The **LangGraph Client** starts and establishes a session with the MCP server.
3.  The user provides a prompt, and the agent uses a **ReAct (Reasoning and Acting)** loop to determine which tools to use.
4.  The agent calls the appropriate tools via JSON-RPC requests to the MCP server.

### Cursor IDE Mode
1.  Cursor IDE launches the **MCP Server** as a subprocess using stdio transport.
2.  The server registers its tools with Cursor's MCP client.
3.  When you chat with Cursor, it can automatically discover and use these tools.
4.  Cursor sends tool requests via the MCP protocol to execute actions like file operations or code execution.

## Example Usage

### Standalone Mode
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

### Cursor IDE Mode
Simply chat with Cursor and ask it to perform coding tasks:

```
User: Create a Python script that calculates fibonacci numbers

Cursor: I'll create a Python script for calculating Fibonacci numbers for you.

[Uses create_file tool to create fibonacci.py]
[Uses execute_python_code tool to test the script]

I've created a fibonacci.py file with a function to calculate Fibonacci numbers...
```

## Troubleshooting

### Cursor IDE Integration Issues

1. **Server not connecting**: Ensure the paths in `mcp.json` are correct and point to your actual project location.

2. **Transport errors**: Make sure you're using `"transport": "stdio"` in your `mcp.json` configuration.

3. **Permission errors**: Ensure the Python executable and script files have proper permissions.

4. **uv not found**: Make sure `uv` is installed and available in your system PATH.

### Testing the MCP Server

You can test the Cursor server independently:

```bash
# Test the server manually
uv run src/coding_agent/server_for_cursor.py
```