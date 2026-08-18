# import asyncio
# import uuid
# from flask import Blueprint, request, jsonify
# from tool_registry import registry
# from mcp_manager import mcp_manager

# mcp_bp = Blueprint("mcp", __name__)


# @mcp_bp.route("/servers", methods=["POST"])
# def register_server():
#     data = request.get_json()
#     name = data.get("name")
#     url = data.get("url")
#     headers = data.get("headers")  # optional, for auth tokens later

#     if not name or not url:
#         return jsonify({"error": "'name' and 'url' are required"}), 400

#     server_id = str(uuid.uuid4())[:8]

#     try:
#         conn = asyncio.run(mcp_manager.register(server_id, name, url, headers))
#     except Exception as e:
#         return jsonify({"error": f"Failed to connect to MCP server: {e}"}), 502

#     discovered = registry.register_mcp_tools(server_id, conn.tools)

#     return jsonify({
#         "server_id": server_id,
#         "name": name,
#         "url": url,
#         "status": conn.status,
#         "tools_discovered": discovered
#     }), 201


# @mcp_bp.route("/servers", methods=["GET"])
# def list_servers():
#     servers = []
#     for server_id, conn in mcp_manager.all().items():
#         servers.append({
#             "server_id": server_id,
#             "name": conn.name,
#             "url": conn.url,
#             "status": conn.status,
#             "tool_count": len(conn.tools)
#         })
#     return jsonify(servers)


# @mcp_bp.route("/servers/<server_id>", methods=["DELETE"])
# def delete_server(server_id):
#     conn = mcp_manager.get(server_id)
#     if conn is None:
#         return jsonify({"error": "server not found"}), 404

#     asyncio.run(mcp_manager.remove(server_id))
#     registry.remove_by_server(server_id)

#     return jsonify({"deleted": server_id})


# @mcp_bp.route("/servers/<server_id>/tools", methods=["GET"])
# def get_server_tools(server_id):
#     conn = mcp_manager.get(server_id)
#     if conn is None:
#         return jsonify({"error": "server not found"}), 404

#     return jsonify([{"name": t.name, "description": t.description} for t in conn.tools])


# @mcp_bp.route("/servers/<server_id>/refresh", methods=["POST"])
# def refresh_server(server_id):
#     conn = mcp_manager.get(server_id)
#     if conn is None:
#         return jsonify({"error": "server not found"}), 404

#     tools = asyncio.run(mcp_manager.refresh(server_id))
#     registry.remove_by_server(server_id)
#     discovered = registry.register_mcp_tools(server_id, tools)

#     return jsonify({"server_id": server_id, "tools_discovered": discovered})
import uuid
from flask import Blueprint, request, jsonify
from tool_registry import registry
from mcp_manager import mcp_manager
from async_loop import run_async

mcp_bp = Blueprint("mcp", __name__)


@mcp_bp.route("/servers", methods=["POST"])
def register_server():
    data = request.get_json()
    name = data.get("name")
    url = data.get("url")
    headers = data.get("headers")

    if not name or not url:
        return jsonify({"error": "'name' and 'url' are required"}), 400

    server_id = str(uuid.uuid4())[:8]

    try:
        conn = run_async(mcp_manager.register(server_id, name, url, headers))
    except Exception as e:
        return jsonify({"error": f"Failed to connect to MCP server: {e}"}), 502

    discovered = registry.register_mcp_tools(server_id, conn.tools)

    return jsonify({
        "server_id": server_id,
        "name": name,
        "url": url,
        "status": conn.status,
        "tools_discovered": discovered
    }), 201


@mcp_bp.route("/servers", methods=["GET"])
def list_servers():
    servers = []
    for server_id, conn in mcp_manager.all().items():
        servers.append({
            "server_id": server_id,
            "name": conn.name,
            "url": conn.url,
            "status": conn.status,
            "tool_count": len(conn.tools)
        })
    return jsonify(servers)


@mcp_bp.route("/servers/<server_id>", methods=["DELETE"])
def delete_server(server_id):
    conn = mcp_manager.get(server_id)
    if conn is None:
        return jsonify({"error": "server not found"}), 404

    run_async(mcp_manager.remove(server_id))
    registry.remove_by_server(server_id)

    return jsonify({"deleted": server_id})


@mcp_bp.route("/servers/<server_id>/tools", methods=["GET"])
def get_server_tools(server_id):
    conn = mcp_manager.get(server_id)
    if conn is None:
        return jsonify({"error": "server not found"}), 404

    return jsonify([{"name": t.name, "description": t.description} for t in conn.tools])


@mcp_bp.route("/servers/<server_id>/refresh", methods=["POST"])
def refresh_server(server_id):
    conn = mcp_manager.get(server_id)
    if conn is None:
        return jsonify({"error": "server not found"}), 404

    tools = run_async(mcp_manager.refresh(server_id))
    registry.remove_by_server(server_id)
    discovered = registry.register_mcp_tools(server_id, tools)

    return jsonify({"server_id": server_id, "tools_discovered": discovered})