"""Sample MCP server in Python using FastMCP."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sample-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """Return a greeting message for the given name."""
    return f"Hello, {name}!"


@mcp.resource("config://app")
def get_config() -> str:
    """Return static application configuration."""
    return "App version: 1.0.0\nEnvironment: development"


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Return a personalized greeting resource."""
    return f"Welcome to MCP, {name}!"


if __name__ == "__main__":
    mcp.run()
