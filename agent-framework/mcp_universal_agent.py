"""
Enhanced Universal Agent with MCP (Model Context Protocol) Support
Integrates structured tool communication via FastMCP server
"""

import asyncio
import logging
import traceback
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Import existing components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai-providers'))

from ai_interface import AIProvider, ProviderFactory, Message, MessageRole, AIResponse

# Import providers to register them
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai-providers'))
import openai_provider
import gemini_provider
from mcp_client import MCPClient, MCPToolAdapter, create_mcp_client

logger = logging.getLogger(__name__)

class ThinkingStepType(Enum):
    """Types of thinking steps"""
    USER_INPUT = "user_input"
    TOOL_PLANNING = "tool_planning"
    TOOL_EXECUTION = "tool_execution"
    TOOL_RESULT = "tool_result"
    REASONING = "reasoning"
    FINAL_RESPONSE = "final_response"

@dataclass
class ThinkingStep:
    """A step in the AI's thinking process"""
    type: ThinkingStepType
    title: str
    content: str
    timestamp: str
    duration_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ToolResult:
    """Structured result from tool execution"""
    success: bool
    content: Any
    tool_name: str
    structured_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class MCPUniversalAgent:
    """Enhanced Universal Agent with MCP protocol support"""
    
    def __init__(self, provider: str = 'openai', model_name: str = 'gpt-4o-mini', 
                 system_prompt: str = None, mcp_server_path: str = "../mcp-server/server.py"):
        """
        Initialize the Enhanced Universal Agent with MCP support
        
        Args:
            provider: AI provider name ('openai', 'gemini', 'claude')
            model_name: Model to use
            system_prompt: System prompt for the agent
            mcp_server_path: Path to the MCP server script
        """
        self.provider_name = provider
        self.model_name = model_name
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.mcp_server_path = mcp_server_path
        
        # Initialize AI provider
        self.provider: Optional[AIProvider] = None
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_adapter: Optional[MCPToolAdapter] = None
        
        # Conversation history
        self.conversation_history: List[Message] = []
        
        # Tool execution results for context
        self.recent_tool_results: List[ToolResult] = []
        
        # Thinking process tracking
        self.thinking_steps: List[ThinkingStep] = []
        
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize both AI provider and MCP client"""
        try:
            # Initialize AI provider
            self.provider = ProviderFactory.create_provider(
                self.provider_name, 
                self.model_name
            )
            
            # Initialize MCP client
            self.mcp_client = await create_mcp_client(self.mcp_server_path)
            self.mcp_adapter = MCPToolAdapter(self.mcp_client)
            
            self._initialized = True
            
            logger.info(f"Enhanced Universal Agent initialized with {len(self.mcp_client.tools)} MCP tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Universal Agent: {e}")
            return False
    
    def _add_thinking_step(self, step_type: ThinkingStepType, title: str, content: str, 
                          duration_ms: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None):
        """Add a step to the thinking process"""
        step = ThinkingStep(
            type=step_type,
            title=title,
            content=content,
            timestamp=datetime.now().isoformat(),
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
        self.thinking_steps.append(step)
        logger.info(f"Thinking step: {title}")

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt with MCP tool awareness"""
        return """You are an advanced AI assistant with access to structured tools via the Model Context Protocol (MCP).

You have access to powerful, structured tools for:
- Mathematical calculations with detailed results
- Web automation (browser control, screenshots, navigation)
- Text analysis and utilities
- Time and date operations
- Temperature conversions with formulas

When using tools:
1. Always use structured inputs as specified in the tool schemas
2. Interpret structured outputs to provide comprehensive responses
3. Chain multiple tools when needed to accomplish complex tasks
4. Provide clear explanations of what each tool does and its results

Be helpful, accurate, and make full use of the available tools to provide the best possible assistance."""
    
    async def chat(self, user_input: str, temperature: float = 0.7, 
                  max_tokens: int = 1000, use_tools: bool = True) -> str:
        """
        Enhanced chat method with MCP tool integration
        
        Args:
            user_input: User's message
            temperature: Response randomness (0.0-1.0)
            max_tokens: Maximum tokens in response
            use_tools: Whether to use MCP tools
            
        Returns:
            AI response as string
        """
        # Clear previous thinking steps for new conversation
        self.thinking_steps.clear()
        
        # Track user input
        self._add_thinking_step(
            ThinkingStepType.USER_INPUT,
            "Processing user request",
            user_input,
            metadata={"use_tools": use_tools, "temperature": temperature, "max_tokens": max_tokens}
        )
        
        if not self._initialized:
            await self.initialize()
        
        # Add user message to history
        user_message = Message(
            role=MessageRole.USER,
            content=user_input
        )
        self.conversation_history.append(user_message)
        
        try:
            # Prepare messages for AI provider
            messages = self._prepare_messages_for_provider()
            
            # Get available tools if enabled
            tools = []
            if use_tools and self.mcp_adapter:
                tool_schemas = self.mcp_adapter.get_tool_schemas()
                tools = list(tool_schemas.values())
                
                # Track tool planning
                self._add_thinking_step(
                    ThinkingStepType.TOOL_PLANNING,
                    f"Planning with {len(tools)} available tools",
                    f"Available tools: {', '.join([tool.get('function', {}).get('name', 'unknown') for tool in tools])}",
                    metadata={"tool_count": len(tools)}
                )
            
            # Track reasoning step
            start_time = datetime.now()
            self._add_thinking_step(
                ThinkingStepType.REASONING,
                "Generating initial response",
                f"Calling {self.provider_name} with model {self.model_name}"
            )
            
            # Call AI provider
            response = await self._call_provider_with_tools(messages, tools, temperature, max_tokens)
            
            # Process response and handle tool calls
            final_response = await self._process_response(response, use_tools)
            
            # Track final response
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds() * 1000)
            self._add_thinking_step(
                ThinkingStepType.FINAL_RESPONSE,
                "Response completed",
                f"Generated {len(final_response)} characters",
                duration_ms=duration,
                metadata={"response_length": len(final_response)}
            )
            
            # Add assistant response to history
            assistant_message = Message(
                role=MessageRole.ASSISTANT,
                content=final_response
            )
            self.conversation_history.append(assistant_message)
            
            return final_response
            
        except Exception as e:
            error_msg = f"Error in chat processing: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _prepare_messages_for_provider(self) -> List[Message]:
        """Prepare messages including system prompt and tool context"""
        messages = []
        
        # Add system message with tool context
        enhanced_system_prompt = self.system_prompt
        
        if self.recent_tool_results:
            tool_context = "\n\nRecent tool execution results for context:"
            for result in self.recent_tool_results[-3:]:  # Last 3 results
                if result.success:
                    tool_context += f"\n- {result.tool_name}: {result.content}"
        
        system_message = Message(
            role=MessageRole.SYSTEM,
            content=enhanced_system_prompt
        )
        messages.append(system_message)
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        return messages
    
    async def _call_provider_with_tools(self, messages: List[Message], tools: List[Dict], 
                                       temperature: float, max_tokens: int) -> AIResponse:
        """Call AI provider with tool support"""
        logger.info(f"Calling provider with {len(tools)} tools available")
        
        # Add tools to provider if available
        if tools and hasattr(self.provider, 'clear_tools') and hasattr(self.provider, 'add_tool'):
            # Clear existing tools and add new ones
            self.provider.clear_tools()
            
            for tool_schema in tools:
                tool_name = tool_schema.get('function', {}).get('name', 'unknown')
                logger.info(f"Adding tool: {tool_name}")
                
                # Convert MCP tool schema to provider format and create MCP wrapper function
                if 'function' in tool_schema:
                    from ai_interface import ToolDefinition
                    
                    # Create a wrapper function that calls MCP
                    def make_mcp_tool_function(name: str):
                        async def mcp_tool_function(**kwargs):
                            logger.info(f"Executing MCP tool: {name} with args: {kwargs}")
                            try:
                                result = await self.mcp_client.call_tool(name, kwargs)
                                logger.info(f"MCP tool {name} result: {result}")
                                return result
                            except Exception as e:
                                logger.error(f"MCP tool {name} error: {e}")
                                return {"error": str(e), "success": False}
                        return mcp_tool_function
                    
                    tool_def = ToolDefinition(
                        name=tool_schema['function']['name'],
                        description=tool_schema['function']['description'],
                        parameters=tool_schema['function']['parameters'],
                        function=make_mcp_tool_function(tool_name)
                    )
                    self.provider.add_tool(tool_def)
        
        # Call provider with tools
        response = self.provider.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info(f"Provider response: content_length={len(response.content or '')}, tool_calls={len(response.tool_calls) if response.tool_calls else 0}")
        return response
    
    async def _process_response(self, response: AIResponse, use_tools: bool) -> str:
        """Process AI response and handle tool calls with proper OpenAI flow"""
        
        # If no tool calls, return content directly
        if not (hasattr(response, 'tool_calls') and response.tool_calls and use_tools):
            return response.content or ""
        
        # Handle tool calls with proper OpenAI conversation flow
        logger.info(f"Processing {len(response.tool_calls)} tool calls")
        
        # Add the assistant's response with tool calls to conversation
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=response.content or "",
            tool_calls=response.tool_calls
        )
        self.conversation_history.append(assistant_message)
        
        # Execute each tool call and add results to conversation
        for tool_call in response.tool_calls:
            try:
                # Track tool execution
                self._add_thinking_step(
                    ThinkingStepType.TOOL_EXECUTION,
                    f"Executing {tool_call.name}",
                    f"Arguments: {tool_call.arguments}",
                    metadata={"tool_name": tool_call.name, "arguments": tool_call.arguments}
                )
                
                tool_start_time = datetime.now()
                logger.info(f"Executing tool: {tool_call.name} with args: {tool_call.arguments}")
                tool_result = await self._execute_tool_call(tool_call)
                self.recent_tool_results.append(tool_result)
                
                # Track tool result
                tool_end_time = datetime.now()
                tool_duration = int((tool_end_time - tool_start_time).total_seconds() * 1000)
                result_preview = tool_result.content[:200] + "..." if len(str(tool_result.content)) > 200 else str(tool_result.content)
                
                self._add_thinking_step(
                    ThinkingStepType.TOOL_RESULT,
                    f"Tool {tool_call.name} {'succeeded' if tool_result.success else 'failed'}",
                    result_preview,
                    duration_ms=tool_duration,
                    metadata={
                        "tool_name": tool_call.name,
                        "success": tool_result.success,
                        "result_length": len(str(tool_result.content))
                    }
                )
                
                # Log tool result
                logger.info(f"Tool {tool_call.name} result: success={tool_result.success}, content_length={len(tool_result.content) if tool_result.content else 0}")
                
                # Add tool result message to conversation
                tool_content = tool_result.content if tool_result.success else f"Error: {tool_result.error_message}"
                tool_message = Message(
                    role=MessageRole.TOOL,
                    content=tool_content,
                    tool_call_id=tool_call.id,
                    name=tool_call.name
                )
                self.conversation_history.append(tool_message)
                logger.info(f"Added tool message to conversation: {tool_content[:100]}...")
                
            except Exception as e:
                logger.error(f"Error executing tool call: {e}")
                logger.error(f"Tool call traceback: {traceback.format_exc()}")
                # Add error message to conversation
                error_content = f"Tool execution error: {str(e)}"
                error_message = Message(
                    role=MessageRole.TOOL,
                    content=error_content,
                    tool_call_id=tool_call.id,
                    name=tool_call.name
                )
                self.conversation_history.append(error_message)
                logger.info(f"Added error message to conversation: {error_content}")
        
        # Get final response from model after tool execution
        logger.info("Getting final response from model after tool execution")
        messages = self._prepare_messages_for_provider()
        
        # Get available tools for the follow-up call
        tools = []
        if use_tools and self.mcp_adapter:
            tool_schemas = self.mcp_adapter.get_tool_schemas()
            tools = list(tool_schemas.values())
        
        # Make follow-up call to get final response (without tools to prevent infinite loop)
        logger.info(f"Making follow-up call with {len(messages)} messages (no tools to prevent recursion)")
        final_response = await self._call_provider_with_tools(messages, [], 0.7, 1000)
        
        logger.info(f"Final response: content_length={len(final_response.content or '')}, tool_calls={len(final_response.tool_calls) if final_response.tool_calls else 0}")
        
        return final_response.content or ""
    
    async def chat_with_thinking(self, user_input: str, temperature: float = 0.7, 
                                max_tokens: int = 1000, use_tools: bool = True) -> tuple[str, List[Dict[str, Any]]]:
        """
        Enhanced chat method that returns both response and thinking steps
        
        Returns:
            Tuple of (response_content, thinking_steps_dict)
        """
        response = await self.chat(user_input, temperature, max_tokens, use_tools)
        
        # Convert thinking steps to dictionary format for JSON serialization
        thinking_steps_dict = []
        for step in self.thinking_steps:
            thinking_steps_dict.append({
                "type": step.type.value,
                "title": step.title,
                "content": step.content,
                "timestamp": step.timestamp,
                "duration_ms": step.duration_ms,
                "metadata": step.metadata
            })
        
        return response, thinking_steps_dict
    
    async def _execute_tool_call(self, tool_call) -> ToolResult:
        """Execute a tool call via MCP"""
        # Handle both ToolCall objects and dictionaries
        if hasattr(tool_call, 'name'):
            tool_name = tool_call.name
            arguments = tool_call.arguments
        else:
            tool_name = tool_call.get('name')
            arguments = tool_call.get('arguments', {})
        
        try:
            # MCP tools expect arguments wrapped in an 'input' object
            mcp_arguments = {"input": arguments}
            logger.info(f"Calling MCP tool {tool_name} with wrapped args: {mcp_arguments}")
            
            # Execute via MCP client
            mcp_result = await self.mcp_client.call_tool(tool_name, mcp_arguments)
            
            # Parse MCP result
            if mcp_result.get('isError', False):
                return ToolResult(
                    success=False,
                    content=mcp_result.get('content', [{}])[0].get('text', 'Unknown error'),
                    tool_name=tool_name,
                    error_message=mcp_result.get('content', [{}])[0].get('text', 'Tool execution failed')
                )
            else:
                # Extract content
                content = mcp_result.get('content', [{}])[0].get('text', '')
                structured_data = mcp_result.get('structuredContent', {})
                
                return ToolResult(
                    success=True,
                    content=content,
                    tool_name=tool_name,
                    structured_data=structured_data
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                content=str(e),
                tool_name=tool_name,
                error_message=str(e)
            )
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools"""
        if not self._initialized:
            await self.initialize()
        
        if self.mcp_client:
            return self.mcp_client.get_available_tools()
        else:
            return []
    
    def switch_provider(self, provider: str, model_name: str = None):
        """Switch AI provider"""
        self.provider_name = provider
        if model_name:
            self.model_name = model_name
        
        # Reinitialize provider
        self.provider = ProviderFactory.create_provider(
            self.provider_name, 
            self.model_name
        )
        
        logger.info(f"Switched to provider: {provider}/{self.model_name}")
    
    def clear_conversation(self):
        """Clear conversation history and recent tool results"""
        self.conversation_history.clear()
        self.recent_tool_results.clear()
        logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        return {
            "message_count": len(self.conversation_history),
            "tool_results": len(self.recent_tool_results),
            "provider": f"{self.provider_name}/{self.model_name}",
            "mcp_tools_available": len(self.mcp_client.tools) if self.mcp_client else 0
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.mcp_client:
            self.mcp_client.disconnect()
        
        logger.info("Enhanced Universal Agent cleaned up")

# Example usage and testing
async def main():
    """Example usage of Enhanced Universal Agent with MCP"""
    agent = MCPUniversalAgent(
        provider='openai',
        model_name='gpt-4o-mini'
    )
    
    # Initialize
    if not await agent.initialize():
        print("Failed to initialize agent")
        return
    
    print("Enhanced Universal Agent with MCP initialized successfully!")
    print(f"Available tools: {len(await agent.get_available_tools())}")
    
    # Test some interactions
    test_queries = [
        "Calculate 15 * 23 + 7",
        "What's the current time?",
        "Convert 72 degrees Fahrenheit to Celsius",
        "Count the words in this text: 'Hello world, this is a test message with several words.'"
    ]
    
    for query in test_queries:
        print(f"\n🤔 User: {query}")
        response = await agent.chat(query)
        print(f"🤖 Assistant: {response}")
    
    # Cleanup
    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())