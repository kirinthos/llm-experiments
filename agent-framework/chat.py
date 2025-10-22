#!/usr/bin/env python3
"""
Simple chat interface using the Universal AI Agent
"""

import os
import sys
from typing import Optional
from universal_agent import UniversalAgent, create_openai_agent
from ai_interface import ProviderFactory
from openai_provider import OpenAIProvider  # Register the provider
try:
    from gemini_provider import GeminiProvider  # Register Gemini provider
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
from tools import (
    calculator, get_current_time, generate_random_number, 
    word_count, convert_temperature, TOOL_SCHEMAS
)
from playwright_tools import (
    start_browser, navigate_to_url, take_screenshot, get_page_content,
    get_page_text, click_element, fill_input, wait_for_element,
    get_element_text, close_browser, PLAYWRIGHT_TOOL_SCHEMAS
)


def display_banner():
    """Display the chat application banner"""
    print("╔════════════════════════════════════════╗")
    print("║        🤖 Universal AI Chat           ║")  
    print("║   Multi-Provider Agent Interface       ║")
    print("╚════════════════════════════════════════╝")


def get_available_models():
    """Get available models organized by provider"""
    models = {
        "openai": [
            "gpt-4", 
            "gpt-4-turbo", 
            "gpt-4o", 
            "gpt-4o-mini",
            "gpt-3.5-turbo"
        ]
    }
    
    # Add Gemini models if available
    if GEMINI_AVAILABLE:
        models["gemini"] = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-2.0-flash",
            "gemini-2.5-flash"
        ]
    
    # Future providers can be added here:
    # "claude": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    
    return models


def select_model():
    """Let user select which model to use"""
    models = get_available_models()
    providers = ProviderFactory.list_providers()
    
    print("\n🔧 Available AI Models:")
    print("-" * 40)
    
    model_options = []
    option_num = 1
    
    for provider_name in providers:
        if provider_name in models:
            print(f"\n📡 {provider_name.upper()} Models:")
            for model in models[provider_name]:
                print(f"  {option_num}. {model}")
                model_options.append((provider_name, model))
                option_num += 1
    
    print(f"\n  {option_num}. Custom model (specify provider and model name)")
    print("-" * 40)
    
    while True:
        try:
            choice = input(f"\nSelect model (1-{option_num}): ").strip()
            
            if choice == str(option_num):
                # Custom model
                provider_name = input("Enter provider name (e.g., 'openai'): ").strip()
                model_name = input("Enter model name (e.g., 'gpt-4'): ").strip()
                return provider_name, model_name
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(model_options):
                return model_options[choice_idx]
            else:
                print("❌ Invalid selection. Please try again.")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)


def setup_agent(provider_name: str, model_name: str) -> UniversalAgent:
    """Set up the universal agent with selected model and tools"""
    
    print(f"\n🚀 Setting up {provider_name} agent with model: {model_name}")
    
    # Check for API key
    api_key = None
    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
            print("💡 Set your API key with: export OPENAI_API_KEY=your_key_here")
            print("💡 Or create a .env file with: OPENAI_API_KEY=your_key_here")
    elif provider_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  Warning: GEMINI_API_KEY not found in environment variables")
            print("💡 Set your API key with: export GEMINI_API_KEY=your_key_here")
            print("💡 Or create a .env file with: GEMINI_API_KEY=your_key_here")
    
    # Create the agent
    try:
        agent = UniversalAgent(
            provider_name, 
            model_name, 
            system_prompt="""You are a helpful AI assistant with access to various tools. 
            Use them when appropriate to help the user. You have access to:
            - Calculator for mathematical operations
            - Current time retrieval  
            - Random number generation
            - Text analysis (word count)
            - Temperature conversion
            - Web automation with Playwright (navigate, screenshot, interact with pages)
            
            For web automation, always start by using start_browser, then navigate_to_url, and use other tools as needed.
            Always be helpful, concise, and use tools when they would be useful for answering questions.""",
            api_key=api_key
        )
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        sys.exit(1)
    
    # Add tools
    print("🔧 Adding tools...")
    tools_to_add = [
        # Basic tools
        ("calculator", calculator, "Perform basic mathematical operations", TOOL_SCHEMAS["calculator"]),
        ("get_current_time", get_current_time, "Get the current date and time", TOOL_SCHEMAS["get_current_time"]),
        ("generate_random_number", generate_random_number, "Generate a random number within a specified range", TOOL_SCHEMAS["generate_random_number"]),
        ("word_count", word_count, "Count words, characters, and lines in a text", TOOL_SCHEMAS["word_count"]),
        ("convert_temperature", convert_temperature, "Convert temperature between Celsius, Fahrenheit, and Kelvin", TOOL_SCHEMAS["convert_temperature"]),
        
        # Playwright web automation tools
        ("start_browser", start_browser, "Start a browser instance for web automation", PLAYWRIGHT_TOOL_SCHEMAS["start_browser"]),
        ("navigate_to_url", navigate_to_url, "Navigate to a specific URL", PLAYWRIGHT_TOOL_SCHEMAS["navigate_to_url"]),
        ("take_screenshot", take_screenshot, "Take a screenshot of the current page", PLAYWRIGHT_TOOL_SCHEMAS["take_screenshot"]),
        ("get_page_content", get_page_content, "Get the HTML content of the current page", PLAYWRIGHT_TOOL_SCHEMAS["get_page_content"]),
        ("get_page_text", get_page_text, "Get visible text from the current page", PLAYWRIGHT_TOOL_SCHEMAS["get_page_text"]),
        ("click_element", click_element, "Click an element by CSS selector", PLAYWRIGHT_TOOL_SCHEMAS["click_element"]),
        ("fill_input", fill_input, "Fill an input field with text", PLAYWRIGHT_TOOL_SCHEMAS["fill_input"]),
        ("wait_for_element", wait_for_element, "Wait for an element to appear", PLAYWRIGHT_TOOL_SCHEMAS["wait_for_element"]),
        ("get_element_text", get_element_text, "Get text content of an element", PLAYWRIGHT_TOOL_SCHEMAS["get_element_text"]),
        ("close_browser", close_browser, "Close the browser and cleanup", PLAYWRIGHT_TOOL_SCHEMAS["close_browser"])
    ]
    
    for name, func, description, schema in tools_to_add:
        try:
            agent.add_tool(name, func, description, schema)
        except Exception as e:
            print(f"⚠️  Warning: Could not add tool '{name}': {e}")
    
    # Show agent info
    info = agent.get_provider_info()
    print(f"✅ Agent ready!")
    print(f"   Provider: {info['provider_type']}")
    print(f"   Model: {info['model_name']}")
    print(f"   Function Calling: {'✅' if info['supports_function_calling'] else '❌'}")
    print(f"   Available Tools: {', '.join(info['tool_names'])}")
    
    return agent


def display_help():
    """Display available commands"""
    print("\n💡 Available Commands:")
    print("  /help     - Show this help message")
    print("  /clear    - Clear conversation history")
    print("  /info     - Show agent information")
    print("  /tools    - List available tools")
    print("  /quit     - Exit the chat")
    print("\n💭 Example questions:")
    print("  • What's 25 * 4 + 10?")
    print("  • Convert 100°F to Celsius")
    print("  • What time is it?")
    print("  • Generate a random number between 1 and 100")
    print("  • How many words are in 'Hello world'?")
    print("  • Navigate to https://example.com and take a screenshot")
    print("  • Open a website and get the page title")
    print("  • Capture content from a URL")


def chat_loop(agent: UniversalAgent):
    """Main chat loop"""
    
    print("\n" + "="*50)
    print("🎉 Chat started! Type /help for commands")
    print("="*50)
    
    display_help()
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command = user_input[1:].lower()
                
                if command in ['quit', 'exit', 'q']:
                    print("👋 Thanks for chatting! Goodbye!")
                    break
                    
                elif command == 'help':
                    display_help()
                    continue
                    
                elif command == 'clear':
                    agent.clear_conversation()
                    print("🧹 Conversation history cleared!")
                    continue
                    
                elif command == 'info':
                    info = agent.get_provider_info()
                    print(f"\n🤖 Agent Information:")
                    print(f"   Provider: {info['provider_type']}")
                    print(f"   Model: {info['model_name']}")
                    print(f"   Function Calling: {'✅' if info['supports_function_calling'] else '❌'}")
                    print(f"   Tools: {len(info['tool_names'])} available")
                    continue
                    
                elif command == 'tools':
                    tools = agent.list_tools()
                    print(f"\n🔧 Available Tools ({len(tools)}):")
                    for tool in tools:
                        print(f"   • {tool}")
                    continue
                    
                else:
                    print(f"❌ Unknown command: /{command}")
                    print("💡 Type /help for available commands")
                    continue
            
            # Regular chat message
            print("🤔 Thinking...")
            
            try:
                response = agent.chat(user_input)
                print(f"🤖 Assistant: {response}")
                
            except Exception as e:
                error_msg = str(e).lower()
                if "api key" in error_msg or "authentication" in error_msg:
                    print("❌ API Authentication Error!")
                    print("💡 Please set your API key:")
                    if "openai" in agent.model_name.lower():
                        print("   export OPENAI_API_KEY=your_key_here")
                elif "rate limit" in error_msg:
                    print("⏰ Rate limit exceeded. Please wait a moment and try again.")
                elif "model" in error_msg:
                    print(f"❌ Model error: {e}")
                    print("💡 The selected model might not be available.")
                else:
                    print(f"❌ Error: {e}")
                    print("💡 Please try rephrasing your question or check your connection.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break


def main():
    """Main application entry point"""
    
    display_banner()
    
    # Check if we have any providers
    providers = ProviderFactory.list_providers()
    if not providers:
        print("❌ No AI providers available!")
        print("💡 Make sure you have implemented at least one provider.")
        sys.exit(1)
    
    print(f"\n🔌 Available providers: {', '.join(providers)}")
    
    # Select model
    provider_name, model_name = select_model()
    
    # Setup agent
    agent = setup_agent(provider_name, model_name)
    
    # Start chat loop
    chat_loop(agent)


if __name__ == "__main__":
    main()