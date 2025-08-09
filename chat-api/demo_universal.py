"""
Demo of the Universal Agent with the new AI provider interface
"""

from universal_agent import UniversalAgent, create_openai_agent, create_agent_with_tools
from ai_interface import ProviderFactory
from tools import (
    calculator, get_current_time, generate_random_number, 
    word_count, convert_temperature, TOOL_SCHEMAS
)


def create_demo_universal_agent():
    """Create a universal agent with all demo tools"""
    
    # Create the agent using the new interface
    agent = create_openai_agent(
        model="gpt-4",
        system_prompt="""You are a helpful AI assistant with access to various tools. 
        Use them when appropriate to help the user. You have access to:
        - Calculator for mathematical operations
        - Current time retrieval
        - Random number generation
        - Text analysis (word count)
        - Temperature conversion
        
        Always be helpful and use the tools when they would be useful for answering questions."""
    )
    
    # Add all the tools using the new interface
    agent.add_tool("calculator", calculator, "Perform basic mathematical operations", TOOL_SCHEMAS["calculator"])
    agent.add_tool("get_current_time", get_current_time, "Get the current date and time", TOOL_SCHEMAS["get_current_time"])
    agent.add_tool("generate_random_number", generate_random_number, "Generate a random number within a specified range", TOOL_SCHEMAS["generate_random_number"])
    agent.add_tool("word_count", word_count, "Count words, characters, and lines in a text", TOOL_SCHEMAS["word_count"])
    agent.add_tool("convert_temperature", convert_temperature, "Convert temperature between Celsius, Fahrenheit, and Kelvin", TOOL_SCHEMAS["convert_temperature"])
    
    return agent


def run_specific_tests():
    """Run the specific tests requested: temperature conversion, random numbers + addition, and more"""
    
    agent = create_demo_universal_agent()
    
    tests = [
        # Temperature conversion test (as requested)
        {
            "query": "Convert 100 degrees Fahrenheit to Celsius",
            "description": "🌡️  Temperature Conversion Test"
        },
        
        # Random number generation and addition test (as requested)
        {
            "query": "Generate two random numbers between 1 and 50, then add them together",
            "description": "🎲 Random Numbers + Addition Test"
        },
        
        # Additional interesting test
        {
            "query": "What's the square root of 144, then multiply that result by 5?",
            "description": "🧮 Complex Math Test (sqrt + multiply)"
        },
        
        # Text analysis test
        {
            "query": "How many words are in this quote: 'The only way to do great work is to love what you do' and what's the current time?",
            "description": "📝 Multi-tool Test (text analysis + time)"
        }
    ]
    
    print("🚀 Universal Agent Function Calling Demo")
    print("=" * 60)
    
    # Show agent info
    info = agent.get_provider_info()
    print(f"🤖 Agent Provider: {info['provider_type']}")
    print(f"🧠 Model: {info['model_name']}")
    print(f"🔧 Function Calling: {'✅' if info['supports_function_calling'] else '❌'}")
    print(f"📋 Tools: {', '.join(info['tool_names'])}")
    print()
    
    for i, test in enumerate(tests, 1):
        print(f"{test['description']}")
        print(f"👤 Query: {test['query']}")
        print("-" * 40)
        
        try:
            response = agent.chat(test['query'], use_history=False)  # Fresh context for each test
            print(f"🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            if "API key" in str(e).lower():
                print("💡 Tip: Set your OPENAI_API_KEY environment variable")
        
        print()
    
    print("=" * 60)
    print("✅ Universal Agent demo completed!")


def interactive_mode():
    """Run the universal agent in interactive mode"""
    
    agent = create_demo_universal_agent()
    
    print("🤖 Universal AI Agent - Interactive Mode")
    info = agent.get_provider_info()
    print(f"Provider: {info['provider_type']} | Model: {info['model_name']}")
    print(f"Available tools: {', '.join(info['tool_names'])}")
    print("💡 Type 'quit' to exit, 'clear' to clear conversation history")
    print("💡 Try: 'What's 25*4?', 'Convert 100F to C', 'What time is it?'")
    print("-" * 70)
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if user_input.lower() == 'clear':
            agent.clear_conversation()
            print("🧹 Conversation history cleared!")
            continue
        
        if not user_input:
            continue
        
        try:
            response = agent.chat(user_input)
            print(f"🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            if "API key" in str(e).lower():
                print("💡 Set your OPENAI_API_KEY environment variable")


def test_provider_switching():
    """Demo switching between different providers (when available)"""
    
    print("🔄 Provider Switching Demo")
    print("=" * 40)
    
    # Create agent with OpenAI
    agent = create_openai_agent("gpt-4", "You are a helpful assistant.")
    agent.add_tool("calculator", calculator, "Do math", TOOL_SCHEMAS["calculator"])
    
    print(f"Initial provider: {agent.get_provider_info()}")
    
    # Test a simple calculation
    print("\n👤 User: What's 10 + 15?")
    try:
        response = agent.chat("What's 10 + 15?")
        print(f"🤖 Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n💡 This demonstrates how easy it would be to switch providers!")
    print("💡 Just implement new provider classes (GeminiProvider, ClaudeProvider, etc.)")
    print("💡 and use agent.switch_provider('gemini', 'gemini-pro') to switch!")


def showcase_interface_benefits():
    """Show the benefits of the new interface"""
    
    print("✨ Universal AI Interface Benefits")
    print("=" * 50)
    
    # Show available providers
    providers = ProviderFactory.list_providers()
    print(f"🔌 Available providers: {providers}")
    
    # Show how easy it is to create agents
    print("\n🚀 Easy agent creation:")
    print("```python")
    print("# OpenAI agent")
    print("agent = UniversalAgent('openai', 'gpt-4', 'You are helpful.')")
    print()
    print("# Gemini agent (when implemented)")
    print("# agent = UniversalAgent('gemini', 'gemini-pro', 'You are helpful.')")
    print()
    print("# Claude agent (when implemented)") 
    print("# agent = UniversalAgent('claude', 'claude-3', 'You are helpful.')")
    print("```")
    
    print("\n🔧 Unified tool interface:")
    print("- Same add_tool() method for all providers")
    print("- Same chat() method for all providers") 
    print("- Same system prompt handling")
    print("- Automatic function calling translation")
    
    print("\n🔄 Easy provider switching:")
    print("- Keep all tools and settings")
    print("- Switch models mid-conversation")
    print("- Compare responses from different providers")
    
    print("\n📈 Future extensibility:")
    print("- Add new providers by implementing AIProvider interface")
    print("- Support new model features automatically")
    print("- Consistent behavior across all models")


if __name__ == "__main__":
    import sys
    
    print("🎯 Universal AI Agent Demo")
    print("Choose an option:")
    print("1. Run specific tests (temperature, random numbers, etc.)")
    print("2. Interactive mode")
    print("3. Provider switching demo")
    print("4. Interface benefits showcase")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    if choice == "1":
        run_specific_tests()
    elif choice == "2":
        interactive_mode()
    elif choice == "3":
        test_provider_switching()
    elif choice == "4":
        showcase_interface_benefits()
    else:
        print("Invalid choice. Running specific tests by default.")
        run_specific_tests()