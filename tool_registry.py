class ToolDefinition:
    def __init__(self, name, description, input_schema, source, fn=None, server_id=None, raw_name=None):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.source = source          # "local" | "mcp"
        self.fn = fn                  # only for local
        self.server_id = server_id    # only for mcp
        self.raw_name = raw_name      # original tool name on the MCP server


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register_local(self, name, description, input_schema, fn):
        self._tools[name] = ToolDefinition(
            name=name, description=description, input_schema=input_schema,
            source="local", fn=fn
        )

    def register_mcp_tools(self, server_id, mcp_tools):
        added = []
        for tool in mcp_tools:
            namespaced_name = f"{server_id}__{tool.name}"
            self._tools[namespaced_name] = ToolDefinition(
                name=namespaced_name,
                description=tool.description or "",
                input_schema=tool.input_schema,
                source="mcp",
                server_id=server_id,
                raw_name=tool.name
            )
            added.append(namespaced_name)
        return added

    def remove_by_server(self, server_id):
        to_remove = [name for name, t in self._tools.items() if t.server_id == server_id]
        for name in to_remove:
            del self._tools[name]

    def resolve(self, name) -> ToolDefinition | None:
        return self._tools.get(name)

    def all_tools(self):
        return list(self._tools.values())

    def get_openai_schemas(self):
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema or {"type": "object", "properties": {}, "required": []}
                }
            })
        return schemas


registry = ToolRegistry()