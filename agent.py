
import json
import asyncio
from openai import OpenAI

import config
from local_tools import get_weather, get_current_datetime
from tool_registry import registry
from tool_resolver import execute_tool
from mcp_manager import mcp_manager


client = OpenAI(api_key=config.OPENAI_API_KEY)


def register_local_tools():
    registry.register_local(
        name="get_weather",
        description="Get the current weather for a given location.",
        input_schema={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or place name."
                }
            },
            "required": ["location"]
        },
        fn=get_weather
    )

    registry.register_local(
        name="get_current_datetime",
        description="Get the current date and time.",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        },
        fn=get_current_datetime
    )


def normalize_tool_result(result):
    """
    Convert MCP/local tool results into plain text
    that can safely be sent back to the LLM.
    """

    if result is None:
        return ""

    # MCP content list
    if isinstance(result, list):
        parts = []

        for item in result:
            if hasattr(item, "text"):
                parts.append(str(item.text))
            else:
                parts.append(str(item))

        return "\n".join(parts)

    # Single MCP TextContent-like object
    if hasattr(result, "text"):
        return str(result.text)

    # Dict/list/other structured result
    if isinstance(result, (dict, list)):
        return json.dumps(result, default=str)

    return str(result)


async def run_agent(user_message: str) -> dict:

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant with access to tools. "
                "Use tools when needed. "
                "If a tool result gives you information needed for another tool, "
                "continue calling tools until you have enough information "
                "to answer the user's question."
            )
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    tools_used = []

    # ---------------------------------------------------------
    # TOOL-CALLING LOOP
    # ---------------------------------------------------------

    while True:

        print("\n[LLM] Sending context to model...")

        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            tools=registry.get_openai_schemas(),
            tool_choice="auto"
        )

        reply = response.choices[0].message

        # -----------------------------------------------------
        # NO TOOL CALL
        # -----------------------------------------------------

        if not reply.tool_calls:

            final_answer = reply.content or ""

            return {
                "answer": final_answer,
                "tools_used": tools_used
            }

        # -----------------------------------------------------
        # ASSISTANT TOOL CALL MESSAGE
        # -----------------------------------------------------

        assistant_message = {
            "role": "assistant",
            "content": reply.content,
            "tool_calls": []
        }

        for tool_call in reply.tool_calls:

            assistant_message["tool_calls"].append({
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            })

        messages.append(assistant_message)

        # -----------------------------------------------------
        # EXECUTE ALL TOOL CALLS
        # -----------------------------------------------------

        for tool_call in reply.tool_calls:

            tool_name = tool_call.function.name

            try:
                tool_args = json.loads(
                    tool_call.function.arguments
                )
            except json.JSONDecodeError as exc:

                tool_result = (
                    f"Error: invalid tool arguments: {exc}"
                )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

                continue

            print("\n========================================")
            print("[AGENT] Tool call")
            print(f"[AGENT] Name: {tool_name}")
            print(f"[AGENT] Arguments: {tool_args}")
            print("========================================")

            tool_def = registry.resolve(tool_name)

            try:

                result = await execute_tool(
                    tool_name,
                    tool_args,
                    registry,
                    mcp_manager
                )

                # Convert MCP result to plain text
                tool_result = normalize_tool_result(result)

            except Exception as exc:

                tool_result = (
                    f"Tool execution failed: {exc}"
                )

            print("[AGENT] Tool result:")
            print(tool_result)

            # -------------------------------------------------
            # LOG TOOL USAGE
            # -------------------------------------------------

            tools_used.append({
                "tool_name": tool_name,
                "source": (
                    tool_def.source
                    if tool_def
                    else "unknown"
                ),
                "server_id": (
                    tool_def.server_id
                    if tool_def
                    else None
                ),
                "arguments": tool_args,
                "result": tool_result
            })

            # -------------------------------------------------
            # PUT TOOL RESULT INTO LLM CONTEXT
            # -------------------------------------------------

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

            print("\n[AGENT] Tool result added to LLM context.")

        # -----------------------------------------------------
        # LOOP CONTINUES
        # -----------------------------------------------------
        #
        # The next iteration sends:
        #
        # user
        # assistant tool call
        # tool result
        #
        # back to the LLM.
        #
        # If the LLM wants another tool, it executes it.
        #
        # If the LLM doesn't want another tool, it returns
        # the final answer.
        # -----------------------------------------------------


if __name__ == "__main__":

    register_local_tools()

    while True:

        user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            break

        result = asyncio.run(
            run_agent(user_input)
        )

        print(f"\nAgent: {result['answer']}")

        if result["tools_used"]:
            print(
                "(tools used: "
                f"{[t['tool_name'] for t in result['tools_used']]})"
            )