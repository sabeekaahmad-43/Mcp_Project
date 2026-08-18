import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client


class MCPServerConnection:
    def __init__(self, server_id: str, name: str, url: str, headers: dict | None = None):
        self.server_id = server_id
        self.name = name
        self.url = url
        self.headers = headers or {}
        self.status = "disconnected"
        self.tools = []

        self._http_client = None
        self._client = None
        self._client_ctx = None

    async def connect(self):
        self._http_client = httpx2.AsyncClient(
            headers=self.headers,
            follow_redirects=True,
            timeout=httpx2.Timeout(30.0, read=300.0),
        )
        await self._http_client.__aenter__()

        transport = streamable_http_client(self.url, http_client=self._http_client)
        self._client = Client(transport)
        await self._client.__aenter__()

        self.status = "connected"

    async def list_tools(self):
        result = await self._client.list_tools()
        self.tools = result.tools
        return self.tools

    async def call_tool(self, name: str, arguments: dict):
        return await self._client.call_tool(name, arguments)

    async def disconnect(self):
        if self._client is not None:
            await self._client.__aexit__(None, None, None)
        if self._http_client is not None:
            await self._http_client.__aexit__(None, None, None)
        self.status = "disconnected"


class MCPClientManager:
    def __init__(self):
        self._connections: dict[str, MCPServerConnection] = {}

    async def register(self, server_id: str, name: str, url: str, headers: dict | None = None) -> MCPServerConnection:
        conn = MCPServerConnection(server_id, name, url, headers)
        await conn.connect()
        await conn.list_tools()
        self._connections[server_id] = conn
        return conn

    def get(self, server_id: str) -> MCPServerConnection | None:
        return self._connections.get(server_id)

    def all(self) -> dict[str, MCPServerConnection]:
        return self._connections

    async def remove(self, server_id: str):
        conn = self._connections.get(server_id)
        if conn is not None:
            await conn.disconnect()
            del self._connections[server_id]

    async def refresh(self, server_id: str):
        conn = self._connections.get(server_id)
        if conn is None:
            return None
        return await conn.list_tools()


mcp_manager = MCPClientManager()