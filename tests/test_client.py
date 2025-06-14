import pytest
import subprocess
import time
from src.coding_agent.client import CodingAgent
import pytest_asyncio

# mark async tests with asyncio
@pytest.mark.asyncio
async def test_coding_agent_execute_task(coding_agent, server):
    """Test the coding agent's ability to execute a task."""
    result = await coding_agent.execute_task("Create a simple Python script that prints 'Hello, World!'")
    assert "Hello, World!" in result

@pytest_asyncio.fixture
async def server():
    """Start the MCP server for testing."""
    # Start server in a separate process
    server_process = subprocess.Popen(
        ['python', '-m', 'src.coding_agent.server'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give server time to start
    time.sleep(2)
    
    yield
    
    # Cleanup
    server_process.terminate()
    server_process.wait()

@pytest.fixture
def coding_agent():
    """Create a coding agent."""
    return CodingAgent()

def test_coding_agent_init(coding_agent):
    """Test the coding agent's initialization."""
    assert coding_agent is not None