import json
from typing import List

from langchain_core.messages import ToolCall
from openai.types.chat import ChatCompletionMessageToolCall
from kirinchat.schemas.mcp import MCPSSEConfig, MCPWebsocketConfig, MCPStreamableHttpConfig


def convert_langchain_tool_calls(tool_calls: List[ChatCompletionMessageToolCall]):
    if not tool_calls:
        return []

    langchain_tool_calls: List[ToolCall] = []
    for tool_call in tool_calls:
        langchain_tool_calls.append(
            ToolCall(id=tool_call.id, args=json.loads(tool_call.function.arguments), name=tool_call.function.name))

    return langchain_tool_calls

def convert_mcp_config(servers_info: dict | list):

    def convert_single_mcp(server_info):
        if isinstance(server_info, dict):
            if server_info.get("type") == "sse":
                return MCPSSEConfig(
                    url=server_info.get("url"),
                    headers=server_info.get("headers"),
                    server_name=server_info.get("server_name")
                )
            elif server_info.get("type") == "websocket":
                return MCPWebsocketConfig(
                    url=server_info.get("url"),
                    server_name=server_info.get("server_name")
                )
            elif server_info.get("type") == "streamable_http":
                return MCPStreamableHttpConfig(
                    url=server_info.get("url"),
                    headers=server_info.get("headers"),
                    server_name=server_info.get("server_name")
                )
            else:
                # Stdio
                pass

    if isinstance(servers_info, dict):
        return convert_single_mcp(servers_info)
    else:
        return [convert_single_mcp(server_info) for server_info in servers_info]


def mcp_tool_to_args_schema(name, description, args_schema) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": args_schema
        }
    }

