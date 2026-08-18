
# import asyncio
# from flask import Blueprint, request, jsonify
# from agent import run_agent

# chat_bp = Blueprint("chat", __name__)


# @chat_bp.route("/chat", methods=["POST"])
# def chat():
#     data = request.get_json()
#     message = data.get("message")

#     if not message:
#         return jsonify({"error": "'message' is required"}), 400

#     try:
#         result = asyncio.run(run_agent(message))
#     except Exception as e:
#         return jsonify({"error": f"Agent failed: {e}"}), 500

#     return jsonify({
#         "response": result["answer"],
#         "tools_used": result["tools_used"]
#     })
from flask import Blueprint, request, jsonify
from agent import run_agent
from async_loop import run_async

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "'message' is required"}), 400

    try:
        result = run_async(run_agent(message))
    except Exception as e:
        return jsonify({"error": f"Agent failed: {e}"}), 500

    return jsonify({
        "response": result["answer"],
        "tools_used": result["tools_used"]
    })