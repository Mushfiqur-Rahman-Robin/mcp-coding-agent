import os
import subprocess
import tempfile
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CodingAgent", port=8092)


@mcp.tool(name='execute_python_code')
async def execute_python_code(code: str) -> str:
    """Execute Python code and return the output."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        result = subprocess.run(
            ['uv', 'run', 'python', temp_file], 
            capture_output=True, 
            text=True, 
            timeout=30,
            check=False
        )
        
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return f"✅ Success:\n{result.stdout}"
        else:
            return f"❌ Error:\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "❌ Timeout: Code execution exceeded 30 seconds"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@mcp.tool(name='add_package')
async def add_package(package_name: str) -> str:
    """Add a Python package using uv."""
    try:
        result = subprocess.run(
            ['uv', 'add', package_name],
            capture_output=True,
            text=True,
            timeout=120,
            check=False
        )
        
        if result.returncode == 0:
            return f"✅ Package added: {package_name}\n{result.stdout}"
        else:
            return f"❌ Addition failed: {result.stderr}"
    except FileNotFoundError:
        return "❌ Error: uv not found. Please install uv first."
    except Exception as e:
        return f"❌ Error: {str(e)}"
    
@mcp.tool(name='remove_package')
async def remove_package(package_name: str) -> str:
    """Remove a Python package using uv."""
    try:
        result = subprocess.run(
            ['uv', 'remove', package_name],
            capture_output=True,
            text=True,
            timeout=120,
            check=False
        )
        
        if result.returncode == 0:
            return f"✅ Package removed: {package_name}\n{result.stdout}"
        else:
            return f"❌ Removal failed: {result.stderr}"
    except FileNotFoundError:
        return "❌ Error: uv not found. Please install uv first."
    except Exception as e:
        return f"❌ Error: {str(e)}"


@mcp.tool(name='create_file')
async def create_file(filename: str, content: str) -> str:
    """Create a new file with the given content."""
    try:
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return f"✅ File created: {filename}"
    except Exception as e:
        return f"❌ Error creating file: {str(e)}"


@mcp.tool(name='read_file')
async def read_file(filename: str) -> str:
    """Read the content of a file."""
    try:
        path = Path(filename)
        if not path.exists():
            return f"❌ File not found: {filename}"
        content = path.read_text()
        return f"📄 Content of {filename}:\n{content}"
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


@mcp.tool(name='list_files')
async def list_files(directory: str = ".") -> str:
    """List files in a directory."""
    try:
        path = Path(directory)
        if not path.exists():
            return f"❌ Directory not found: {directory}"
        
        files = []
        for item in path.iterdir():
            if item.is_file():
                files.append(f"📄 {item.name}")
            elif item.is_dir():
                files.append(f"📁 {item.name}/")
        
        return f"📂 Contents of {directory}:\n" + "\n".join(files)
    except Exception as e:
        return f"❌ Error listing files: {str(e)}"


if __name__ == "__main__":
    print("🚀 Starting MCP Coding Agent Server...")
    mcp.run(transport="streamable-http")