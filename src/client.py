#!/usr/bin/env python3
"""
Simple MCP client without asyncio
"""

import json
import subprocess
import time
from typing import Any, Dict, List, Optional


class SimpleMCPClient:
    """Simple synchronous MCP client for stdio transport"""

    def __init__(self) -> None:
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.initialized = False

    def start_server(self, command: str, args: Optional[List[str]] = None) -> bool:
        """Start MCP server as subprocess"""
        if args is None:
            args = []

        try:
            self.process = subprocess.Popen(
                [command] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
            )

            # Give server time to start
            time.sleep(0.1)

            # Check if process is still running
            if self.process.poll() is not None:
                return False

            return True

        except Exception as e:
            print(f"Error starting server: {e}")
            return False

    def _get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id

    def _send_request(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send JSON-RPC request to server"""
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("Server not running")

        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
        }

        if params:
            request["params"] = params

        # Send request
        request_json = json.dumps(request) + "\n"
        if self.process.stdin is None:
            raise RuntimeError("Server stdin is not available")
        self.process.stdin.write(request_json)
        self.process.stdin.flush()

        # Read response
        if self.process.stdout is None:
            raise RuntimeError("Server stdout is not available")
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")

        response = json.loads(response_line.strip())

        # Return full response (including errors)
        if "error" in response:
            return {"error": response["error"]}

        result = response.get("result", {})
        # Ensure we return a Dict[str, Any]
        if isinstance(result, dict):
            return result
        return {}

    def initialize(self) -> bool:
        """Initialize connection with MCP server"""
        try:
            params = {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "simple-mcp-client",
                    "version": "1.0.0",
                },
            }

            response = self._send_request("initialize", params)

            if "error" not in response:
                # Send initialized notification
                notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                }
                notification_json = json.dumps(notification) + "\n"
                if self.process is None or self.process.stdin is None:
                    raise RuntimeError("Server stdin is not available")
                self.process.stdin.write(notification_json)
                self.process.stdin.flush()

                self.initialized = True
                return True

            return False

        except Exception as e:
            print(f"Error initializing: {e}")
            return False

    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        if not self.initialized:
            raise RuntimeError("Client not initialized")

        try:
            response = self._send_request("tools/list")
            if "error" in response:
                print(f"Error listing tools: {response['error']}")
                return []

            if "tools" in response:
                tools = response["tools"]
                # Ensure we return a List[Dict[str, Any]]
                if isinstance(tools, list) and all(
                    isinstance(tool, dict) for tool in tools
                ):
                    return tools
            return []

        except Exception as e:
            print(f"Error listing tools: {e}")
            return []

    def list_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources"""
        if not self.initialized:
            raise RuntimeError("Client not initialized")

        try:
            response = self._send_request("resources/list")
            if "error" in response:
                print(f"Error listing resources: {response['error']}")
                return []

            if "resources" in response:
                resources = response["resources"]
                # Ensure we return a List[Dict[str, Any]]
                if isinstance(resources, list) and all(
                    isinstance(resource, dict) for resource in resources
                ):
                    return resources
            return []

        except Exception as e:
            print(f"Error listing resources: {e}")
            return []

    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource by URI"""
        if not self.initialized:
            raise RuntimeError("Client not initialized")

        params = {"uri": uri}

        try:
            response = self._send_request("resources/read", params)
            return response

        except Exception as e:
            print(f"Error reading resource {uri}: {e}")
            return {"error": str(e)}

    def list_prompts(self) -> List[Dict[str, Any]]:
        """Get list of available prompts"""
        if not self.initialized:
            raise RuntimeError("Client not initialized")

        try:
            response = self._send_request("prompts/list")
            if "error" in response:
                print(f"Error listing prompts: {response['error']}")
                return []

            if "prompts" in response:
                prompts = response["prompts"]
                # Ensure we return a List[Dict[str, Any]]
                if isinstance(prompts, list) and all(
                    isinstance(prompt, dict) for prompt in prompts
                ):
                    return prompts
            return []

        except Exception as e:
            print(f"Error listing prompts: {e}")
            return []

    def get_prompt(
        self, name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get a prompt template with optional arguments"""
        if not self.initialized:
            raise RuntimeError("Client not initialized")

        params: Dict[str, Any] = {"name": name}
        if arguments:
            params["arguments"] = arguments

        try:
            response = self._send_request("prompts/get", params)
            return response

        except Exception as e:
            print(f"Error getting prompt {name}: {e}")
            return {"error": str(e)}

    def call_tool(
        self, name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call a tool"""
        if not self.initialized:
            raise RuntimeError("Client not initialized")

        params: Dict[str, Any] = {"name": name}
        if arguments:
            params["arguments"] = arguments

        try:
            response = self._send_request("tools/call", params)
            return response

        except Exception as e:
            print(f"Error calling tool {name}: {e}")
            return {"error": str(e)}

    def close(self) -> None:
        """Close connection and terminate server"""
        if self.process:
            try:
                if self.process.stdin:
                    self.process.stdin.close()
                if self.process.stdout:
                    self.process.stdout.close()
                if self.process.stderr:
                    self.process.stderr.close()
                self.process.terminate()
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception:
                pass
            finally:
                self.process = None
                self.initialized = False


def main() -> None:
    """Demo function showing how to use the client"""
    print("=== Simple MCP Client Demo ===")

    # Create client
    client = SimpleMCPClient()

    try:
        # Start server
        print("1. Starting MCP server...")
        if not client.start_server("python", ["src/server.py"]):
            print("❌ Failed to start server")
            return
        print("✅ Server started")

        # Initialize connection
        print("2. Initializing connection...")
        if not client.initialize():
            print("❌ Failed to initialize")
            return
        print("✅ Connection initialized")

        # List available tools
        print("3. Listing available tools...")
        tools = client.list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            name = tool.get("name", "Unknown")
            desc = tool.get("description", "No description")
            print(f"   - {name}: {desc}")

        # List available resources
        print("4. Listing available resources...")
        resources = client.list_resources()
        print(f"✅ Found {len(resources)} resources:")
        for resource in resources:
            uri = resource.get("uri", "Unknown")
            name = resource.get("name", "No name")
            print(f"   - {uri}: {name}")

        # List available prompts
        print("5. Listing available prompts...")
        prompts = client.list_prompts()
        print(f"✅ Found {len(prompts)} prompts:")
        for prompt in prompts:
            name = prompt.get("name", "Unknown")
            desc = prompt.get("description", "No description")
            print(f"   - {name}: {desc}")

        # Call some tools
        if tools:
            print("6. Testing tools...")

            # Test get_current_time
            print("   - Testing get_current_time...")
            result = client.call_tool("get_current_time")
            if "error" in result:
                print(f"     ❌ Error: {result['error']}")
            else:
                print(f"     ✅ Current time: {result}")

            # Test generate_greeting
            print("   - Testing generate_greeting...")
            result = client.call_tool("generate_greeting", {"name": "Test User"})
            if "error" in result:
                print(f"     ❌ Error: {result['error']}")
            else:
                print(f"     ✅ Greeting: {result}")

        # Test prompts
        if prompts:
            print("7. Testing prompts...")

            # Test code_review_prompt
            print("   - Testing code_review_prompt...")
            result = client.get_prompt(
                "code_review_prompt", {"language": "python", "code_type": "function"}
            )
            if "error" in result:
                print(f"     ❌ Error: {result['error']}")
            else:
                print(
                    f"     ✅ Code review prompt: {len(result.get('messages', []))} messages"
                )

            # Test learning_plan_prompt
            print("   - Testing learning_plan_prompt...")
            result = client.get_prompt(
                "learning_plan_prompt", {"topic": "FastAPI", "skill_level": "beginner"}
            )
            if "error" in result:
                print(f"     ❌ Error: {result['error']}")
            else:
                print(
                    f"     ✅ Learning plan prompt: {len(result.get('messages', []))} messages"
                )

        print("\n🎉 Demo completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        print("8. Closing client...")
        client.close()
        print("✅ Client closed")


if __name__ == "__main__":
    main()
