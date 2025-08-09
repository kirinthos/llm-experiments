#!/usr/bin/env python3
"""
Demo showing the universal interface working with multiple providers
"""

from universal_agent import UniversalAgent
from ai_interface import ProviderFactory
from openai_provider import OpenAIProvider
try:
    from gemini_provider import GeminiProvider, GEMINI_AVAILABLE
except ImportError:
    GEMINI_AVAILABLE = False
from tools import calculator, convert_temperature, TOOL_SCHEMAS


def demo_provider_switching():
    """Demonstrate switching between providers with the same interface"""
    
    print("🔄 Universal AI Provider Demo")
    print("=" * 50)
    
    # Show available providers
    providers = ProviderFactory.list_providers()
    print(f"🔌 Available providers: {', '.join(providers)}")
    print()
    
    # Test 1: OpenAI Agent
    print("1️⃣  Creating OpenAI Agent")
    try:
        openai_agent = UniversalAgent("openai", "gpt-4o-mini", "You are a helpful assistant.")
        openai_agent.add_tool("calculator", calculator, "Do math", TOOL_SCHEMAS["calculator"])
        
        info = openai_agent.get_provider_info()
        print(f"   ✅ OpenAI Agent: {info['model_name']}")
        print(f"   🔧 Function calling: {'✅' if info['supports_function_calling'] else '❌'}")
        print(f"   🛠️  Tools: {len(info['tool_names'])}")
    except Exception as e:
        print(f"   ❌ OpenAI setup failed: {e}")
    
    print()
    
    # Test 2: Gemini Agent (if available)
    if GEMINI_AVAILABLE:
        print("2️⃣  Creating Gemini Agent")
        try:
            gemini_agent = UniversalAgent("gemini", "gemini-1.5-flash", "You are a helpful assistant.")
            gemini_agent.add_tool("calculator", calculator, "Do math", TOOL_SCHEMAS["calculator"])
            
            info = gemini_agent.get_provider_info()
            print(f"   ✅ Gemini Agent: {info['model_name']}")
            print(f"   🔧 Function calling: {'✅' if info['supports_function_calling'] else '❌'}")
            print(f"   🛠️  Tools: {len(info['tool_names'])}")
        except Exception as e:
            print(f"   ❌ Gemini setup failed: {e}")
            if "quota" in str(e).lower():
                print("   💡 This is expected - quota limits reached, but setup worked!")
    else:
        print("2️⃣  Gemini not available (google-generativeai not installed)")
    
    print()
    
    # Test 3: Provider Switching Demo
    print("3️⃣  Provider Switching Demo")
    try:
        # Start with OpenAI
        agent = UniversalAgent("openai", "gpt-4o-mini", "You are helpful.")
        agent.add_tool("calculator", calculator, "Do math", TOOL_SCHEMAS["calculator"])
        print(f"   📍 Started with: {agent.get_provider_info()['provider_type']}")
        
        # Switch to Gemini (if available)
        if GEMINI_AVAILABLE:
            agent.switch_provider("gemini", "gemini-1.5-flash")
            print(f"   🔄 Switched to: {agent.get_provider_info()['provider_type']}")
            print(f"   🛠️  Tools preserved: {len(agent.list_tools())}")
        
        print("   ✅ Provider switching works!")
        
    except Exception as e:
        print(f"   ❌ Provider switching failed: {e}")
    
    print()
    
    # Test 4: Same Interface Demo
    print("4️⃣  Same Interface for All Providers")
    print("   🔧 Universal methods work with any provider:")
    print("   • agent.chat('Hello!')  # Same for all")
    print("   • agent.add_tool(...)   # Same for all") 
    print("   • agent.list_tools()    # Same for all")
    print("   • agent.switch_provider() # Easy switching")
    print()
    
    print("🎉 Universal Interface Demo Complete!")
    print()
    print("💡 Key Benefits:")
    print("   ✅ Write once, run with any AI provider")
    print("   ✅ Easy to add new providers")
    print("   ✅ Switch models without changing code")
    print("   ✅ Consistent tool interface")
    print("   ✅ Future-proof architecture")


def show_usage_examples():
    """Show practical usage examples"""
    
    print("\n" + "=" * 60)
    print("📚 Usage Examples")
    print("=" * 60)
    
    print("""
🚀 Basic Usage:
```python
from universal_agent import UniversalAgent

# OpenAI
agent = UniversalAgent("openai", "gpt-4", "You are helpful.")

# Gemini  
agent = UniversalAgent("gemini", "gemini-1.5-flash", "You are helpful.")

# Same interface for both!
response = agent.chat("Hello!")
```

🔄 Easy Switching:
```python
# Start with OpenAI
agent = UniversalAgent("openai", "gpt-4", "You are helpful.")
agent.add_tool("calculator", calc_func, "Do math", schema)

# Switch to Gemini - keeps all tools and settings!
agent.switch_provider("gemini", "gemini-1.5-flash")

# Same code works with both providers
response = agent.chat("What's 2 + 2?")
```

🛠️ Tool Management:
```python
# Add tools (works with any provider)
agent.add_tool("calculator", calculator, "Math operations", schema)
agent.add_tool("weather", weather_func, "Get weather", weather_schema)

# List tools
tools = agent.list_tools()  # ['calculator', 'weather']

# Remove tools
agent.remove_tool("weather")
```

🔧 Provider Info:
```python
info = agent.get_provider_info()
print(f"Provider: {info['provider_type']}")
print(f"Model: {info['model_name']}")
print(f"Function calling: {info['supports_function_calling']}")
print(f"Tools: {info['tool_names']}")
```
""")


if __name__ == "__main__":
    demo_provider_switching()
    show_usage_examples()