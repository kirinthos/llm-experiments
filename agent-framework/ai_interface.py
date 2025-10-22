"""
Abstract interface for AI models with support for various providers
(OpenAI, Gemini, Claude, etc.)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum


class MessageRole(Enum):
    """Standard message roles across all AI providers"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """Standardized message format"""
    role: MessageRole
    content: str
    tool_call_id: Optional[str] = None
    name: Optional[str] = None  # For tool messages
    tool_calls: Optional[List['ToolCall']] = None  # For assistant messages with tool calls


@dataclass
class ToolCall:
    """Represents a tool call made by the AI"""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class AIResponse:
    """Standardized response format from AI models"""
    content: Optional[str]
    tool_calls: List[ToolCall] = None
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []


@dataclass
class ToolDefinition:
    """Standardized tool definition format"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]  # JSON schema for parameters
    

class AIProvider(ABC):
    """
    Abstract base class for AI model providers.
    
    This interface standardizes interaction with different AI models
    (OpenAI, Gemini, Claude, etc.) providing a unified API.
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.system_prompt: Optional[str] = None
        self.tools: Dict[str, ToolDefinition] = {}
        
    @abstractmethod
    def chat(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """
        Send messages to the AI and get a response.
        
        Args:
            messages: List of messages in the conversation
            temperature: Controls randomness (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters
            
        Returns:
            AIResponse with content and/or tool calls
        """
        pass
    
    @abstractmethod
    def supports_function_calling(self) -> bool:
        """Check if this provider supports function calling"""
        pass
    
    @abstractmethod
    def supports_system_prompt(self) -> bool:
        """Check if this provider supports system prompts"""
        pass
    
    def set_system_prompt(self, prompt: str):
        """Set the system prompt for the AI"""
        self.system_prompt = prompt
    
    def add_tool(self, tool: ToolDefinition):
        """Add a tool that the AI can use"""
        self.tools[tool.name] = tool
    
    def remove_tool(self, tool_name: str):
        """Remove a tool"""
        if tool_name in self.tools:
            del self.tools[tool_name]
    
    def clear_tools(self):
        """Remove all tools"""
        self.tools.clear()
    
    def get_tools(self) -> List[ToolDefinition]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def execute_tool(self, tool_call: ToolCall) -> str:
        """
        Execute a tool call and return the result.
        
        Args:
            tool_call: The tool call to execute
            
        Returns:
            String result of the tool execution
        """
        if tool_call.name not in self.tools:
            return f"Error: Tool '{tool_call.name}' not found"
        
        tool = self.tools[tool_call.name]
        
        try:
            result = tool.function(**tool_call.arguments)
            return str(result)
        except Exception as e:
            return f"Error executing tool '{tool_call.name}': {str(e)}"
    
    def create_message(self, role: MessageRole, content: str, **kwargs) -> Message:
        """Helper to create a standardized message"""
        return Message(role=role, content=content, **kwargs)
    
    def chat_simple(
        self, 
        message: str, 
        conversation_history: Optional[List[Message]] = None,
        **kwargs
    ) -> str:
        """
        Simplified chat interface for single messages.
        
        Args:
            message: User message
            conversation_history: Previous messages
            **kwargs: Additional parameters for chat()
            
        Returns:
            AI response content as string
        """
        messages = []
        
        # Add system prompt if supported and set
        if self.supports_system_prompt() and self.system_prompt:
            messages.append(self.create_message(MessageRole.SYSTEM, self.system_prompt))
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current message
        messages.append(self.create_message(MessageRole.USER, message))
        
        # Get response
        response = self.chat(messages, **kwargs)
        
        # Handle tool calls if present
        if response.tool_calls:
            # Add the assistant's response with tool calls
            messages.append(Message(
                role=MessageRole.ASSISTANT,
                content=response.content or "",
                tool_calls=response.tool_calls
            ))
            
            # Execute tools and add results
            for tool_call in response.tool_calls:
                tool_result = self.execute_tool(tool_call)
                messages.append(Message(
                    role=MessageRole.TOOL,
                    content=tool_result,
                    tool_call_id=tool_call.id,
                    name=tool_call.name
                ))
            
            # Get final response after tool execution
            final_response = self.chat(messages, **kwargs)
            content = final_response.content
            if content is None:
                return "No response generated"
            elif not isinstance(content, str):
                return str(content)
            return content
        
        # Ensure we return a string
        content = response.content
        if content is None:
            return "No response generated"
        elif not isinstance(content, str):
            return str(content)
        return content


class ProviderFactory:
    """Factory for creating AI providers"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a new provider"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(
        cls, 
        provider_name: str, 
        model_name: str, 
        api_key: Optional[str] = None,
        **kwargs
    ) -> AIProvider:
        """Create a provider instance"""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(model_name=model_name, api_key=api_key, **kwargs)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """List all registered providers"""
        return list(cls._providers.keys())


# Utility functions for common operations

def create_tool_from_function(
    func: Callable,
    name: str,
    description: str,
    parameters: Dict[str, Any]
) -> ToolDefinition:
    """Helper to create a ToolDefinition from a function"""
    return ToolDefinition(
        name=name,
        description=description,
        function=func,
        parameters=parameters
    )

def messages_to_dict(messages: List[Message]) -> List[Dict[str, Any]]:
    """Convert Message objects to dictionary format"""
    result = []
    for msg in messages:
        msg_dict = {
            "role": msg.role.value,
            "content": msg.content,
        }
        if msg.tool_call_id:
            msg_dict["tool_call_id"] = msg.tool_call_id
        if msg.name:
            msg_dict["name"] = msg.name
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "name": tc.name,
                    "arguments": tc.arguments
                } for tc in msg.tool_calls
            ]
        result.append(msg_dict)
    return result

def messages_from_dict(messages: List[Dict[str, Any]]) -> List[Message]:
    """Convert dictionary format to Message objects"""
    result = []
    for msg in messages:
        role = MessageRole(msg["role"])
        result.append(Message(
            role=role,
            content=msg["content"],
            tool_call_id=msg.get("tool_call_id"),
            name=msg.get("name")
        ))
    return result