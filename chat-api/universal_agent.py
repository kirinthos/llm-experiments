"""
Universal AI Agent that can work with any AI provider
(OpenAI, Gemini, Claude, etc.) through the unified interface
"""

from typing import List, Optional, Dict, Any, Union
from ai_interface import (
    AIProvider, Message, MessageRole, ToolDefinition, 
    create_tool_from_function, ProviderFactory
)


class UniversalAgent:
    """
    A universal AI agent that can work with any AI provider.
    
    This agent provides a simple interface while being provider-agnostic.
    You can easily switch between OpenAI, Gemini, Claude, or other providers.
    """
    
    def __init__(
        self,
        provider: Union[AIProvider, str],
        model_name: str = None,
        system_prompt: str = "You are a helpful AI assistant.",
        api_key: Optional[str] = None,
        **provider_kwargs
    ):
        """
        Initialize the Universal Agent.
        
        Args:
            provider: Either an AIProvider instance or provider name (e.g., "openai")
            model_name: Name of the model to use (e.g., "gpt-4", "gemini-pro")
            system_prompt: System prompt for the agent
            api_key: API key for the provider
            **provider_kwargs: Additional provider-specific arguments
        """
        if isinstance(provider, str):
            # Create provider from factory
            if model_name is None:
                raise ValueError("model_name is required when using provider name")
            self.provider = ProviderFactory.create_provider(
                provider, model_name, api_key, **provider_kwargs
            )
        else:
            # Use provided provider instance
            self.provider = provider
        
        # Set system prompt
        self.provider.set_system_prompt(system_prompt)
        self.conversation_history: List[Message] = []
        
    @property
    def model_name(self) -> str:
        """Get the current model name"""
        return self.provider.model_name
    
    @property
    def supports_function_calling(self) -> bool:
        """Check if current provider supports function calling"""
        return self.provider.supports_function_calling()
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt"""
        self.provider.set_system_prompt(prompt)
    
    def add_tool(self, name: str, func: callable, description: str, parameters: Dict[str, Any]):
        """
        Add a tool that the agent can use.
        
        Args:
            name: Name of the tool
            func: The function to execute
            description: Description of what the tool does
            parameters: JSON schema describing the parameters
        """
        tool = create_tool_from_function(func, name, description, parameters)
        self.provider.add_tool(tool)
    
    def add_tool_from_definition(self, tool: ToolDefinition):
        """Add a tool using a ToolDefinition object"""
        self.provider.add_tool(tool)
    
    def remove_tool(self, name: str):
        """Remove a tool"""
        self.provider.remove_tool(name)
    
    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return [tool.name for tool in self.provider.get_tools()]
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Message]:
        """Get the current conversation history"""
        return self.conversation_history.copy()
    
    def chat(
        self, 
        message: str, 
        use_history: bool = True,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: The user message
            use_history: Whether to include conversation history
            temperature: Controls randomness in responses
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The agent's response as a string
        """
        history = self.conversation_history if use_history else []
        
        response = self.provider.chat_simple(
            message, 
            conversation_history=history,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Update conversation history
        if use_history:
            self.conversation_history.append(
                self.provider.create_message(MessageRole.USER, message)
            )
            self.conversation_history.append(
                self.provider.create_message(MessageRole.ASSISTANT, response)
            )
            
            # Keep history manageable (last 20 messages)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
        
        return response
    
    def chat_advanced(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Advanced chat interface with full message control.
        
        Args:
            messages: List of Message objects
            temperature: Controls randomness
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
            
        Returns:
            Response content as string
        """
        response = self.provider.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Handle tool calls if present
        if response.tool_calls:
            # This is handled internally by chat_simple, so we'll use that instead
            # Convert messages to simple format and use chat_simple
            if messages:
                last_message = messages[-1]
                if last_message.role == MessageRole.USER:
                    history = messages[:-1] if len(messages) > 1 else []
                    return self.provider.chat_simple(
                        last_message.content,
                        conversation_history=history,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
        
        return response.content or "No response generated"
    
    def switch_provider(
        self,
        provider: Union[AIProvider, str],
        model_name: str = None,
        api_key: Optional[str] = None,
        **provider_kwargs
    ):
        """
        Switch to a different AI provider while keeping tools and settings.
        
        Args:
            provider: New provider (instance or name)
            model_name: Model name for new provider
            api_key: API key for new provider
            **provider_kwargs: Additional provider arguments
        """
        # Save current state
        current_tools = self.provider.get_tools()
        current_system_prompt = self.provider.system_prompt
        
        # Create new provider
        if isinstance(provider, str):
            if model_name is None:
                raise ValueError("model_name is required when switching to provider by name")
            self.provider = ProviderFactory.create_provider(
                provider, model_name, api_key, **provider_kwargs
            )
        else:
            self.provider = provider
        
        # Restore state
        if current_system_prompt:
            self.provider.set_system_prompt(current_system_prompt)
        
        for tool in current_tools:
            self.provider.add_tool(tool)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        return {
            "provider_type": type(self.provider).__name__,
            "model_name": self.provider.model_name,
            "supports_function_calling": self.provider.supports_function_calling(),
            "supports_system_prompt": self.provider.supports_system_prompt(),
            "num_tools": len(self.provider.tools),
            "tool_names": [tool.name for tool in self.provider.get_tools()]
        }


# Convenience functions for creating agents with specific providers

def create_openai_agent(
    model: str = "gpt-4",
    system_prompt: str = "You are a helpful AI assistant.",
    api_key: Optional[str] = None
) -> UniversalAgent:
    """Create an agent using OpenAI"""
    return UniversalAgent("openai", model, system_prompt, api_key)

def create_agent_with_tools(
    provider: str,
    model: str,
    tools: List[Dict[str, Any]],
    system_prompt: str = "You are a helpful AI assistant with access to various tools.",
    api_key: Optional[str] = None
) -> UniversalAgent:
    """
    Create an agent with predefined tools.
    
    Args:
        provider: Provider name (e.g., "openai")
        model: Model name
        tools: List of tool dictionaries with keys: name, func, description, parameters
        system_prompt: System prompt
        api_key: API key
        
    Returns:
        Configured UniversalAgent
    """
    agent = UniversalAgent(provider, model, system_prompt, api_key)
    
    for tool_config in tools:
        agent.add_tool(
            tool_config["name"],
            tool_config["func"],
            tool_config["description"],
            tool_config["parameters"]
        )
    
    return agent


# Demo and testing functions

def demo_universal_agent():
    """Demonstrate the universal agent with different providers"""
    from tools import calculator, get_current_time, TOOL_SCHEMAS
    
    print("🤖 Universal AI Agent Demo")
    print("=" * 50)
    
    # Create OpenAI agent
    agent = create_openai_agent("gpt-4", "You are a helpful math and time assistant.")
    
    # Add tools
    agent.add_tool("calculator", calculator, "Perform mathematical operations", TOOL_SCHEMAS["calculator"])
    agent.add_tool("get_current_time", get_current_time, "Get current time", TOOL_SCHEMAS["get_current_time"])
    
    print(f"Agent Info: {agent.get_provider_info()}")
    print()
    
    # Test the agent
    test_queries = [
        "What's 25 * 4?",
        "What time is it?",
        "Calculate the square root of 144"
    ]
    
    for query in test_queries:
        print(f"👤 User: {query}")
        try:
            response = agent.chat(query)
            print(f"🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print()


if __name__ == "__main__":
    demo_universal_agent()