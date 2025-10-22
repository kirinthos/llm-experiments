"""
MCP Client for Universal AI Chat
Connects to FastMCP server to access structured tools via Model Context Protocol
"""

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """Represents an MCP tool with structured schema"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    category: str = "General"

class MCPClient:
    """Client for communicating with FastMCP server"""
    
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process: Optional[subprocess.Popen] = None
        self.tools: Dict[str, MCPTool] = {}
        self._initialized = False
    
    async def connect(self) -> bool:
        """Connect to the MCP server"""
        try:
            # Start the MCP server process
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Initialize MCP protocol
            await self._initialize_protocol()
            await self._list_tools()
            
            self._initialized = True
            logger.info(f"Connected to MCP server with {len(self.tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            if self.process:
                self.process.terminate()
                self.process = None
            return False
    
    async def _initialize_protocol(self):
        """Initialize MCP protocol handshake"""
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "universal-ai-chat",
                    "version": "1.0.0"
                }
            }
        }
        
        await self._send_request(init_request)
        response = await self._read_response()
        
        if response.get("error"):
            raise Exception(f"MCP initialization failed: {response['error']}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        await self._send_request(initialized_notification)
    
    async def _list_tools(self):
        """List available tools from the MCP server"""
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        await self._send_request(list_tools_request)
        response = await self._read_response()
        
        if response.get("error"):
            raise Exception(f"Failed to list tools: {response['error']}")
        
        # Parse tools from response
        tools_data = response.get("result", {}).get("tools", [])
        
        for tool_data in tools_data:
            tool = MCPTool(
                name=tool_data["name"],
                description=tool_data["description"],
                input_schema=tool_data["inputSchema"],
                category=self._categorize_tool(tool_data["name"])
            )
            self.tools[tool.name] = tool
    
    def _categorize_tool(self, tool_name: str) -> str:
        """Categorize tool based on its name"""
        if any(word in tool_name for word in ['browser', 'navigate', 'screenshot', 'click', 'fill']):
            return "Web Automation"
        elif any(word in tool_name for word in ['calculator', 'random', 'temperature']):
            return "Math & Logic"
        elif any(word in tool_name for word in ['obsidian']):
            return "Obsidian"
        elif any(word in tool_name for word in ['file', 'directory', 'search_files']):
            return "Filesystem"
        elif any(word in tool_name for word in ['execute_command']):
            return "System"
        elif any(word in tool_name for word in ['time', 'word_count']):
            return "Utilities"
        else:
            return "General"
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool via MCP protocol"""
        if not self._initialized:
            raise Exception("MCP client not initialized")
        
        if tool_name not in self.tools:
            raise Exception(f"Tool '{tool_name}' not found")
        
        # Prepare tool call request
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await self._send_request(tool_call_request)
        response = await self._read_response()
        
        if response.get("error"):
            raise Exception(f"Tool call failed: {response['error']}")
        
        return response.get("result", {})
    
    async def _send_request(self, request: Dict[str, Any]):
        """Send JSON-RPC request to MCP server"""
        if not self.process or not self.process.stdin:
            raise Exception("MCP server process not available")
        
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        logger.debug(f"Sent MCP request: {request}")
    
    async def _read_response(self) -> Dict[str, Any]:
        """Read JSON-RPC response from MCP server"""
        if not self.process or not self.process.stdout:
            raise Exception("MCP server process not available")
        
        # Read line from stdout
        line = self.process.stdout.readline()
        if not line:
            raise Exception("No response from MCP server")
        
        try:
            response = json.loads(line.strip())
            logger.debug(f"Received MCP response: {response}")
            return response
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools in API format"""
        tools = []
        
        for tool_name, tool in self.tools.items():
            tools.append({
                "name": tool_name,
                "description": tool.description,
                "category": tool.category,
                "schema": tool.input_schema
            })
        
        return tools
    
    def disconnect(self):
        """Disconnect from MCP server"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
        
        self._initialized = False
        logger.info("Disconnected from MCP server")

class MCPToolAdapter:
    """Adapter to integrate MCP tools with existing agent framework"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
    
    def get_tool_functions(self) -> Dict[str, callable]:
        """Get tool functions compatible with existing agent framework"""
        functions = {}
        
        for tool_name in self.mcp_client.tools:
            # Create a wrapper function for each tool
            def make_tool_function(name: str):
                async def tool_function(**kwargs) -> Any:
                    try:
                        result = await self.mcp_client.call_tool(name, kwargs)
                        return result
                    except Exception as e:
                        return {"error": str(e), "success": False}
                
                # Set function metadata
                tool_function.__name__ = name
                tool_function.__doc__ = self.mcp_client.tools[name].description
                
                return tool_function
            
            functions[tool_name] = make_tool_function(tool_name)
        
        return functions
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get tool schemas compatible with OpenAI function calling format"""
        schemas = {}
        
        for tool_name, tool in self.mcp_client.tools.items():
            # Convert MCP schema to OpenAI format
            openai_schema = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool.description,
                    "parameters": tool.input_schema
                }
            }
            
            schemas[tool_name] = openai_schema
        
        return schemas

# Convenience function to create and connect MCP client
async def create_mcp_client(server_path: str = "../mcp-server/server.py") -> MCPClient:
    """Create and connect to MCP server"""
    import os
    import sys
    
    # Get the absolute path to the server
    server_full_path = os.path.abspath(server_path)
    
    # Command to run the MCP server
    server_command = [sys.executable, server_full_path]
    
    client = MCPClient(server_command)
    
    if await client.connect():
        return client
    else:
        raise Exception("Failed to connect to MCP server")

# Example usage
async def main():
    """Example usage of MCP client"""
    try:
        # Create and connect to MCP server
        client = await create_mcp_client()
        
        # List available tools
        print("Available tools:")
        for tool_name, tool in client.tools.items():
            print(f"  - {tool_name}: {tool.description}")
        
        # Test a simple tool call
        if "calculator" in client.tools:
            result = await client.call_tool("calculator", {"expression": "2 + 3 * 4"})
            print(f"Calculator result: {result}")
        
        # Test another tool
        if "get_current_time" in client.tools:
            result = await client.call_tool("get_current_time", {})
            print(f"Current time: {result}")
        
        # Disconnect
        client.disconnect()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())