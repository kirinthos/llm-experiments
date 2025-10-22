"""
Google Gemini implementation of the AI interface
"""

import os
import json
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from ai_interface import (
    AIProvider, AIResponse, Message, MessageRole, ToolCall, ToolDefinition
)

# Load environment variables
load_dotenv()

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        # Fallback to old API
        import google.generativeai as genai_old
        GEMINI_AVAILABLE = True
        USING_OLD_API = True
    except ImportError:
        GEMINI_AVAILABLE = False
        USING_OLD_API = False


class GeminiProvider(AIProvider):
    """Google Gemini implementation of the AI interface"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-genai library not installed. Run: pip install google-genai")
        
        super().__init__(model_name, api_key)
        
        # Configure Gemini
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Set it in your .env file or pass as parameter.")
        
        # Use new unified SDK
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        
        # Gemini models that support function calling
        self.function_calling_models = {
            "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", 
            "gemini-2.5-flash", "gemini-1.5-pro-latest", "gemini-1.5-flash-latest"
        }
        
    def supports_function_calling(self) -> bool:
        """Check if this Gemini model supports function calling"""
        return any(model in self.model_name for model in self.function_calling_models)
    
    def supports_system_prompt(self) -> bool:
        """Gemini supports system instructions"""
        return True
    
    def _convert_tools_to_gemini_format(self) -> List[Dict[str, Any]]:
        """Convert our tool definitions to Gemini's format"""
        tools = []
        
        for tool in self.tools.values():
            # Convert our JSON schema to Gemini's function declaration format
            gemini_func = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters.get("properties", {}),
                    "required": tool.parameters.get("required", [])
                }
            }
            tools.append(gemini_func)
        
        return tools
    
    def _convert_messages_to_gemini_format(self, messages: List[Message]) -> tuple:
        """Convert our messages to Gemini's format"""
        system_instruction = None
        conversation_history = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            elif msg.role == MessageRole.USER:
                conversation_history.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif msg.role == MessageRole.ASSISTANT:
                # Handle assistant messages with potential tool calls
                parts = []
                if msg.content:
                    parts.append({"text": msg.content})
                
                # Add function calls if present
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        parts.append({
                            "function_call": {
                                "name": tool_call.name,
                                "args": tool_call.arguments
                            }
                        })
                
                conversation_history.append({
                    "role": "model",
                    "parts": parts
                })
            elif msg.role == MessageRole.TOOL:
                # Function response in Gemini format
                conversation_history.append({
                    "role": "function",
                    "parts": [{
                        "function_response": {
                            "name": msg.name,
                            "response": {"result": msg.content}
                        }
                    }]
                })
        
        return system_instruction, conversation_history
    
    def _convert_gemini_response(self, response) -> AIResponse:
        """Convert Gemini response to our standard format"""
        content = ""
        tool_calls = []
        
        try:
            # Try to get text content directly first
            if hasattr(response, 'text') and response.text:
                content = response.text
            
            # Check for function calls in candidates
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            func_call = part.function_call
                            if hasattr(func_call, 'name') and func_call.name:  # Only add if name exists
                                tool_calls.append(ToolCall(
                                    id=f"gemini_{len(tool_calls)}",  # Generate unique ID
                                    name=func_call.name,
                                    arguments=dict(func_call.args) if func_call.args else {}
                                ))
                        elif hasattr(part, 'text') and part.text:
                            content = part.text
            
            # Extract usage information if available
            usage = None
            if hasattr(response, 'usage_metadata'):
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0)
                }
        
        except Exception as e:
            # If we can't parse the response properly, return basic info
            content = str(response) if response else "No response"
            print(f"Debug - Gemini response parsing error: {e}")
            print(f"Debug - Response type: {type(response)}")
        
        # Ensure content is a string
        if not isinstance(content, str):
            content = str(content) if content else "No response generated"
        
        return AIResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason="stop",  # Gemini doesn't provide finish_reason in the same way
            usage=usage
        )
    
    def chat(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Send messages to Gemini and get a response"""
        
        # Convert messages to Gemini format
        system_instruction, conversation_history = self._convert_messages_to_gemini_format(messages)
        
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        # Add any additional Gemini-specific parameters
        for key, value in kwargs.items():
            if hasattr(generation_config, key):
                setattr(generation_config, key, value)
        
        # Prepare the model with system instruction if available
        if system_instruction and system_instruction != self.model._system_instruction:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model
        
        # Add tools if available and model supports function calling
        tools = None
        if self.tools and self.supports_function_calling():
            gemini_tools = self._convert_tools_to_gemini_format()
            if gemini_tools:
                tools = [genai.protos.Tool(function_declarations=gemini_tools)]
        
        try:
            # Start a chat session
            if conversation_history:
                # Get the last message to send
                last_message = conversation_history[-1] if conversation_history else None
                if last_message and last_message["role"] == "user":
                    # Use chat session for multi-turn conversations
                    chat = model.start_chat(history=conversation_history[:-1])  # Exclude the last message
                    message_text = last_message["parts"][0]["text"]
                    response = chat.send_message(
                        message_text,
                        generation_config=generation_config,
                        tools=tools
                    )
                else:
                    # If last message isn't from user, try to find a user message
                    user_messages = [msg for msg in conversation_history if msg["role"] == "user"]
                    if user_messages:
                        message_text = user_messages[-1]["parts"][0]["text"]
                        response = model.generate_content(
                            message_text,
                            generation_config=generation_config,
                            tools=tools
                        )
                    else:
                        raise ValueError("No user message found in conversation history")
            else:
                # No conversation history - this shouldn't happen normally
                raise ValueError("No conversation history provided")
        
        except Exception as e:
            # Handle Gemini-specific errors
            error_str = str(e).upper()
            if "API_KEY" in error_str or "AUTHENTICATION" in error_str:
                raise ValueError(f"Gemini API key error: {e}")
            elif "QUOTA" in error_str or "RATE_LIMIT" in error_str or "429" in str(e):
                raise ValueError(f"Gemini quota/rate limit exceeded: {e}")
            elif "404" in str(e) or "NOT_FOUND" in error_str:
                raise ValueError(f"Gemini model not found: {e}")
            else:
                raise ValueError(f"Gemini API error: {e}")
        
        return self._convert_gemini_response(response)
    
    def get_available_models(self) -> List[str]:
        """Get list of available Gemini models"""
        try:
            models = genai.list_models()
            return [model.name.replace('models/', '') for model in models 
                   if 'generateContent' in model.supported_generation_methods]
        except Exception:
            # Return common models if API call fails
            return [
                "gemini-1.5-flash", 
                "gemini-1.5-pro", 
                "gemini-2.0-flash",
                "gemini-2.5-flash"
            ]


# Only register the provider if Gemini is available
if GEMINI_AVAILABLE:
    from ai_interface import ProviderFactory
    ProviderFactory.register_provider("gemini", GeminiProvider)


# Convenience functions for creating Gemini providers

def create_gemini_provider(
    model: str = "gemini-1.5-flash", 
    api_key: Optional[str] = None
) -> GeminiProvider:
    """Create a Gemini provider instance"""
    return GeminiProvider(model_name=model, api_key=api_key)

def create_gemini_flash_provider(api_key: Optional[str] = None) -> GeminiProvider:
    """Create a Gemini 1.5 Flash provider"""
    return GeminiProvider(model_name="gemini-1.5-flash", api_key=api_key)

def create_gemini_15_pro_provider(api_key: Optional[str] = None) -> GeminiProvider:
    """Create a Gemini 1.5 Pro provider"""
    return GeminiProvider(model_name="gemini-1.5-pro", api_key=api_key)


# Example usage and testing functions

def test_gemini_provider():
    """Test the Gemini provider"""
    if not GEMINI_AVAILABLE:
        print("❌ Gemini not available. Install with: pip install google-generativeai")
        return
    
    from tools import calculator, TOOL_SCHEMAS
    from ai_interface import create_tool_from_function, MessageRole
    
    try:
        # Create provider
        provider = create_gemini_provider("gemini-pro")
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
        print(f"Gemini Response: {response}")
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        print("💡 Make sure your GEMINI_API_KEY is set correctly")


if __name__ == "__main__":
    test_gemini_provider()