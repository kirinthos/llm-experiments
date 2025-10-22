"""
OpenAI implementation of the AI interface
"""

import os
from typing import List, Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

from ai_interface import (
    AIProvider, AIResponse, Message, MessageRole, ToolCall, ToolDefinition,
    messages_to_dict
)

load_dotenv()


class OpenAIProvider(AIProvider):
    """OpenAI implementation of the AI interface"""
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        # OpenAI models that support function calling
        self.function_calling_models = {
            "gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4-0125-preview",
            "gpt-4-1106-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-1106", 
            "gpt-3.5-turbo-0125", "gpt-4o", "gpt-4o-mini"
        }
        
    def supports_function_calling(self) -> bool:
        """Check if this OpenAI model supports function calling"""
        return any(model in self.model_name for model in self.function_calling_models)
    
    def supports_system_prompt(self) -> bool:
        """OpenAI models support system prompts"""
        return True
    
    def _convert_tools_to_openai_format(self) -> List[Dict[str, Any]]:
        """Convert our tool definitions to OpenAI's format"""
        tools = []
        for tool in self.tools.values():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return tools
    
    def _convert_openai_response(self, response) -> AIResponse:
        """Convert OpenAI response to our standard format"""
        message = response.choices[0].message
        
        # Extract tool calls if present
        tool_calls = []
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                import json
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                tool_calls.append(ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=arguments
                ))
        
        # Extract usage information
        usage = None
        if hasattr(response, 'usage') and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        return AIResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=response.choices[0].finish_reason,
            usage=usage
        )
    
    def chat(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Send messages to OpenAI and get a response"""
        
        # Convert our message format to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_msg = {
                "role": msg.role.value,
                "content": msg.content
            }
            
            # Add additional fields for tool messages
            if msg.tool_call_id:
                openai_msg["tool_call_id"] = msg.tool_call_id
            if msg.name:
                openai_msg["name"] = msg.name
            
            # Add tool_calls for assistant messages
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                openai_tool_calls = []
                for tool_call in msg.tool_calls:
                    import json
                    openai_tool_calls.append({
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(tool_call.arguments)
                        }
                    })
                openai_msg["tool_calls"] = openai_tool_calls
                
            openai_messages.append(openai_msg)
        
        # Prepare API call parameters
        api_params = {
            "model": self.model_name,
            "messages": openai_messages,
            "temperature": temperature
        }
        
        if max_tokens:
            api_params["max_tokens"] = max_tokens
        
        # Add tools if available and model supports function calling
        if self.tools and self.supports_function_calling():
            api_params["tools"] = self._convert_tools_to_openai_format()
            api_params["tool_choice"] = "auto"
        
        # Add any additional OpenAI-specific parameters
        api_params.update(kwargs)
        
        # Make the API call
        response = self.client.chat.completions.create(**api_params)
        
        return self._convert_openai_response(response)
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if 'gpt' in model.id]
        except Exception:
            # Return common models if API call fails
            return [
                "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini",
                "gpt-3.5-turbo", "gpt-3.5-turbo-1106"
            ]


# Register the OpenAI provider with the factory
from ai_interface import ProviderFactory
ProviderFactory.register_provider("openai", OpenAIProvider)


# Convenience functions for creating OpenAI providers

def create_openai_provider(
    model: str = "gpt-4", 
    api_key: Optional[str] = None
) -> OpenAIProvider:
    """Create an OpenAI provider instance"""
    return OpenAIProvider(model_name=model, api_key=api_key)

def create_gpt4_provider(api_key: Optional[str] = None) -> OpenAIProvider:
    """Create a GPT-4 provider"""
    return OpenAIProvider(model_name="gpt-4", api_key=api_key)

def create_gpt35_provider(api_key: Optional[str] = None) -> OpenAIProvider:
    """Create a GPT-3.5 Turbo provider"""
    return OpenAIProvider(model_name="gpt-3.5-turbo", api_key=api_key)

def create_gpt4o_provider(api_key: Optional[str] = None) -> OpenAIProvider:
    """Create a GPT-4o provider"""
    return OpenAIProvider(model_name="gpt-4o", api_key=api_key)


# Example usage and testing functions

def test_openai_provider():
    """Test the OpenAI provider"""
    from tools import calculator, TOOL_SCHEMAS
    from ai_interface import create_tool_from_function, MessageRole
    
    # Create provider
    provider = create_openai_provider("gpt-4")
    provider.set_system_prompt("You are a helpful math assistant.")
    
    # Add calculator tool
    calc_tool = create_tool_from_function(
        func=calculator,
        name="calculator",
        description="Perform mathematical operations",
        parameters=TOOL_SCHEMAS["calculator"]
    )
    provider.add_tool(calc_tool)
    
    # Test simple chat
    response = provider.chat_simple("What is 15 + 27?")
    print(f"Response: {response}")
    
    # Test with conversation history
    messages = [
        provider.create_message(MessageRole.USER, "What is 10 + 5?"),
        provider.create_message(MessageRole.ASSISTANT, "10 + 5 equals 15."),
        provider.create_message(MessageRole.USER, "Now multiply that by 3")
    ]
    
    response = provider.chat(messages)
    print(f"Response with history: {response.content}")


if __name__ == "__main__":
    test_openai_provider()