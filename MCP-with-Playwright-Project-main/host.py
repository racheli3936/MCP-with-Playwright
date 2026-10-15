import asyncio
import json
import os
from contextlib import AsyncExitStack
from typing import Any

import httpx
from openai import OpenAI
from client import MCPClient
from dotenv import load_dotenv

load_dotenv()


class ChatHost:
    def __init__(self):
        self.mcp_clients: list[MCPClient] = [
            MCPClient("./weather_USA.py"),
            MCPClient("./weather_Israel.py")
        ]
        self.tool_clients: dict[str, tuple[MCPClient, str]] = {}
        self.clients_connected = False
        self.exit_stack = AsyncExitStack()
        self.openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        transport = httpx.HTTPTransport(verify=False)
        self.openai = OpenAI(http_client=httpx.Client(transport=transport))

    async def connect_mcp_clients(self):
        """Connect all configured MCP clients once."""
        if self.clients_connected:
            return

        for client in self.mcp_clients:
            if client.session is None:
                await client.connect_to_server()

        if not self.mcp_clients:
            raise RuntimeError("No MCP clients are connected")

        self.clients_connected = True

    async def get_available_tools(self) -> list[dict[str, Any]]:
        """Collect tools from all MCP clients and map them back to their owner."""
        await self.connect_mcp_clients()
        self.tool_clients = {}
        available_tools: list[dict[str, Any]] = []

        for client in self.mcp_clients:
            if client.session is None:
                print(f"Warning: MCP client {client.client_name} is not connected, skipping")
                continue

            try:
                response = await client.session.list_tools()
                for tool in response.tools:
                    exposed_name = f"{client.client_name}__{tool.name}"
                    if exposed_name in self.tool_clients:
                        raise RuntimeError(f"Duplicate tool name detected: {exposed_name}")

                    self.tool_clients[exposed_name] = (client, tool.name)
                    available_tools.append(
                        {
                            "name": exposed_name,
                            "description": f"[{client.client_name}] {tool.description}",
                            "input_schema": tool.inputSchema,
                        }
                    )
            except Exception as e:
                print(f"Warning: Failed to get tools from {client.client_name}: {str(e)}")
                continue

        if not available_tools:
            raise RuntimeError("No tools available from any MCP client")

        return available_tools

    @staticmethod
    def _openai_object_to_dict(value: Any) -> Any:
        if isinstance(value, dict):
            return value
        if hasattr(value, "to_dict"):
            return value.to_dict()
        try:
            return dict(value)
        except Exception:
            return value

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available tools."""
        messages = [{"role": "user", "content": query}]
        available_tools = await self.get_available_tools()
        functions = []

        for tool in available_tools:
            functions.append(
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"] or {"type": "object", "properties": {}},
                }
            )

        final_text = []

        while True:
            response = await asyncio.to_thread(
                self.openai.chat.completions.create,
                model=self.openai_model,
                messages=messages,
                functions=functions,
                function_call="auto",
                max_tokens=1000,
            )

            choice = response.choices[0]
            message = self._openai_object_to_dict(choice.message)
            assistant_text = message.get("content")
            if assistant_text:
                final_text.append(assistant_text)

            function_call = message.get("function_call") or message.get("tool")
            if not function_call:
                break

            tool_name = function_call["name"]
            tool_args = function_call.get("arguments", "{}")
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            if tool_name not in self.tool_clients:
                raise RuntimeError(f"Unknown tool requested by model: {tool_name}")

            client, original_tool_name = self.tool_clients[tool_name]
            if client.session is None:
                raise RuntimeError(f"MCP client {client.client_name} is not connected")

            result = await client.session.call_tool(original_tool_name, tool_args)
            messages.append(
                {
                    "role": "function",
                    "name": tool_name,
                    "content": result.content,
                }
            )

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop."""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nchat_loop Error: {str(e)}")

    async def cleanup(self):
        """Clean up resources."""
        for client in reversed(self.mcp_clients):
            await client.cleanup()
        await self.exit_stack.aclose()


async def main():
    host = ChatHost()
    try:
        await host.chat_loop()
    finally:
        await host.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
