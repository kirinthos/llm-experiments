"""
Google Gemini implementation using the new unified API
"""

import os
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
    GEMINI_AVAILABLE = False


class GeminiProvider(AIProvider):
    """Google Gemini implementation using the new unified API"""
    
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
    
    def chat(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Send messages to Gemini using the new unified API"""
        
        try:
            # Extract the user message - for now, just use the last user message
            user_message = ""
            for msg in reversed(messages):
                if msg.role == MessageRole.USER:
                    user_message = msg.content
                    break
            
            if not user_message:
                return AIResponse(
                    content="No user message found",
                    tool_calls=[],
                    finish_reason="error",
                    usage=None
                )
            
            # Use the new unified API
            config = {"temperature": temperature}
            if max_tokens:
                config["max_output_tokens"] = max_tokens
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_message,
                config=config
            )
            
            # Extract text from response
            response_text = ""
            if hasattr(response, 'text') and response.text:
                response_text = response.text
            else:
                response_text = str(response)
            
            return AIResponse(
                content=response_text,
                tool_calls=[],  # Tool calling will be implemented separately
                finish_reason="stop",
                usage=None
            )
            
        except Exception as e:
            # Enhanced error handling
            error_msg = str(e)
            
            if "API_KEY" in error_msg.upper() or "401" in error_msg:
                raise ValueError("Invalid or missing Gemini API key. Please check your GEMINI_API_KEY.")
            elif "QUOTA" in error_msg.upper() or "429" in error_msg:
                raise ValueError("Gemini API quota exceeded. Please check your usage limits.")
            elif "404" in error_msg or "not found" in error_msg.lower():
                raise ValueError(f"Gemini model '{self.model_name}' not found or not accessible.")
            else:
                raise ValueError(f"Gemini API error: {error_msg}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available Gemini models"""
        try:
            # Use the client to list models
            models_response = self.client.models.list()
            model_names = []
            
            for model in models_response:
                if hasattr(model, 'name'):
                    # Extract model name from full path
                    model_name = model.name.split('/')[-1] if '/' in model.name else model.name
                    if model_name.startswith('gemini') or model_name.startswith('learnlm') or model_name.startswith('gemma'):
                        model_names.append(model_name)
            
            return sorted(model_names) if model_names else [
                "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro"
            ]
            
        except Exception as e:
            print(f"Error getting Gemini models: {e}")
            # Return default models if API call fails
            return [
                "gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro",
                "gemini-2.0-flash", "gemini-1.5-flash-latest", "gemini-1.5-pro-latest"
            ]


# Register the provider with the factory
if GEMINI_AVAILABLE:
    from ai_interface import ProviderFactory
    ProviderFactory.register_provider('gemini', GeminiProvider)


# Convenience functions for creating Gemini providers
def create_gemini_provider(model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None) -> GeminiProvider:
    """Create a Gemini provider with the specified model"""
    return GeminiProvider(model_name=model_name, api_key=api_key)

def create_gemini_flash_provider(api_key: Optional[str] = None) -> GeminiProvider:
    """Create a Gemini Flash provider (fastest)"""
    return GeminiProvider(model_name="gemini-2.5-flash", api_key=api_key)

def create_gemini_pro_provider(api_key: Optional[str] = None) -> GeminiProvider:
    """Create a Gemini Pro provider (most capable)"""
    return GeminiProvider(model_name="gemini-2.5-pro", api_key=api_key)


if __name__ == "__main__":
    # Test the provider
    try:
        provider = create_gemini_flash_provider()
        
        # Test basic functionality
        from ai_interface import MessageRole, Message
        
        messages = [
            Message(role=MessageRole.USER, content="Hello! How are you?")
        ]
        
        response = provider.chat(messages)
        print(f"Response: {response.content}")
        
        # Test model listing
        models = provider.get_available_models()
        print(f"Available models: {len(models)}")
        for model in models[:5]:
            print(f"  - {model}")
            
    except Exception as e:
        print(f"Test failed: {e}")