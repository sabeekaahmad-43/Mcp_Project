async def execute_tool(tool_name, arguments, registry, mcp_manager):
    tool_def = registry.resolve(tool_name)

    if tool_def is None:
        return f"Error: unknown tool '{tool_name}'"

    try:
        if tool_def.source == "local":
            return tool_def.fn(**arguments)

        elif tool_def.source == "mcp":
            conn = mcp_manager.get(tool_def.server_id)
            if conn is None:
                return f"Error: MCP server '{tool_def.server_id}' not connected"

            result = await conn.call_tool(tool_def.raw_name, arguments)
            return result.content

    except Exception as e:
        return f"Tool execution failed: {e}"