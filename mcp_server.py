from mcp.server import MCPServer
from local_tools import get_weather, get_current_datetime
import config

mcp = MCPServer("local-tools-server")


@mcp.tool()
def get_weather_tool(location: str) -> dict:
    """Get current weather for a given location."""
    return get_weather(location)


@mcp.tool()
def get_current_datetime_tool() -> str:
    """Get the current date and time."""
    return get_current_datetime()


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=config.MCP_SERVER_HOST,
        port=config.MCP_SERVER_PORT
    )