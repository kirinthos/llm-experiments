"""
Demo script showing the OpenAI agent with function calling capabilities.
"""

from agent import OpenAIAgent
from tools import (
    calculator, get_current_time, generate_random_number, 
    word_count, convert_temperature, TOOL_SCHEMAS
)


def create_demo_agent():
    """
    Create and configure the demo agent with all available tools.
    """
    agent = OpenAIAgent(
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
    
    # Register all the tools
    agent.register_function(
        "calculator",
        calculator,
        "Perform basic mathematical operations like addition, subtraction, multiplication, division, power, and square root",
        TOOL_SCHEMAS["calculator"]
    )
    
    agent.register_function(
        "get_current_time",
        get_current_time,
        "Get the current date and time",
        TOOL_SCHEMAS["get_current_time"]
    )
    
    agent.register_function(
        "generate_random_number",
        generate_random_number,
        "Generate a random number within a specified range",
        TOOL_SCHEMAS["generate_random_number"]
    )
    
    agent.register_function(
        "word_count",
        word_count,
        "Count words, characters, and lines in a text",
        TOOL_SCHEMAS["word_count"]
    )
    
    agent.register_function(
        "convert_temperature",
        convert_temperature,
        "Convert temperature between Celsius, Fahrenheit, and Kelvin",
        TOOL_SCHEMAS["convert_temperature"]
    )
    
    return agent


def run_test_cases():
    """
    Run some test cases to demonstrate the agent's capabilities.
    """
    agent = create_demo_agent()
    
    test_cases = [
        "What's 25 * 4?",
        "What time is it?",
        "Generate a random number between 1 and 10",
        "How many words are in this sentence: 'The quick brown fox jumps over the lazy dog'?",
        "Convert 32 degrees Fahrenheit to Celsius",
        "What's the square root of 144?",
        "Can you help me with some calculations? I need to add 15 and 27, then multiply the result by 3."
    ]
    
    print("🚀 Running Test Cases")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case}")
        print("-" * 40)
        
        try:
            response = agent.chat(test_case)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test cases completed!")


def interactive_mode():
    """
    Run the agent in interactive mode.
    """
    agent = create_demo_agent()
    
    print("🤖 OpenAI Agent with Function Calling Demo")
    print("🔧 Available tools: calculator, time, random numbers, text analysis, temperature conversion")
    print("💡 Type 'quit' to exit")
    print("💡 Try questions like: 'What's 15 + 23?', 'What time is it?', 'Convert 100F to Celsius'")
    print("-" * 70)
    
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
            print("💡 Make sure you have set your OPENAI_API_KEY environment variable.")


if __name__ == "__main__":
    import sys
    
    print("🎯 OpenAI Function Calling Agent Demo")
    print("Choose an option:")
    print("1. Run test cases (automatic demonstration)")
    print("2. Interactive mode (chat with the agent)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        run_test_cases()
    elif choice == "2":
        interactive_mode()
    else:
        print("Invalid choice. Running test cases by default.")
        run_test_cases()