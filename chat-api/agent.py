"""
OpenAI Agent with Function Calling Capabilities
"""

import json
import os
from typing import Any, Dict, List, Optional, Callable
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIAgent:
    """
    A simple OpenAI agent that supports system prompts and function calling.
    """
    
    def __init__(
        self,
        model: str = "gpt-4",
        system_prompt: str = "You are a helpful AI assistant.",
        api_key: Optional[str] = None
    ):
        """
        Initialize the OpenAI agent.
        
        Args:
            model: The OpenAI model to use
            system_prompt: The system prompt for the agent
            api_key: OpenAI API key (if not provided, will use OPENAI_API_KEY env var)
        """
        self.model = model
        self.system_prompt = system_prompt
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.functions = {}  # Registry of available functions
        
    def register_function(self, name: str, func: Callable, description: str, parameters: Dict):
        """
        Register a function that can be called by the agent.
        
        Args:
            name: The name of the function
            func: The actual function to call
            description: Description of what the function does
            parameters: JSON schema describing the function parameters
        """
        self.functions[name] = {
            "function": func,
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
            }
        }
    
    def _execute_function(self, function_name: str, arguments: str) -> str:
        """
        Execute a registered function with the provided arguments.
        
        Args:
            function_name: Name of the function to execute
            arguments: JSON string of arguments
            
        Returns:
            String result of the function execution
        """
        if function_name not in self.functions:
            return f"Error: Function '{function_name}' not found"
        
        try:
            args = json.loads(arguments)
            result = self.functions[function_name]["function"](**args)
            return str(result)
        except Exception as e:
            return f"Error executing function '{function_name}': {str(e)}"
    
    def chat(self, message: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: The user message
            conversation_history: Previous conversation messages
            
        Returns:
            The agent's response
        """
        # Prepare messages
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": message})
        
        # Prepare function schemas for the API call
        tools = [func_info["schema"] for func_info in self.functions.values()] if self.functions else None
        
        # Make the API call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None
        )
        
        assistant_message = response.choices[0].message
        
        # Check if the model wants to call a function
        if assistant_message.tool_calls:
            # Add the assistant's message to the conversation
            messages.append(assistant_message)
            
            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                
                # Execute the function
                function_result = self._execute_function(function_name, function_args)
                
                # Add the function result to the conversation
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_result
                })
            
            # Get the final response from the model
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None
            )
            
            return final_response.choices[0].message.content
        else:
            return assistant_message.content


def main():
    """
    Main function to demonstrate the agent.
    """
    # Create the agent
    agent = OpenAIAgent(
        model="gpt-4",
        system_prompt="You are a helpful AI assistant with access to various tools. Use them when appropriate to help the user."
    )
    
    print("🤖 OpenAI Agent initialized!")
    print("💡 Type 'quit' to exit")
    print("-" * 50)
    
    conversation_history = []
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            response = agent.chat(user_input, conversation_history)
            print(f"🤖 Agent: {response}")
            
            # Update conversation history
            conversation_history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response}
            ])
            
            # Keep conversation history manageable
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
                
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()