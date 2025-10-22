#!/usr/bin/env python3
"""
Test script to verify the universal agent interface works correctly
"""

from universal_agent import UniversalAgent, create_openai_agent
from ai_interface import ProviderFactory, MessageRole
from openai_provider import OpenAIProvider  # This will register the provider
try:
    from gemini_provider import GeminiProvider  # Register Gemini provider
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
from tools import calculator, convert_temperature, TOOL_SCHEMAS


def test_local_interface():
    """Test the interface components without needing API calls"""
    
    print("🧪 Testing Universal AI Interface")
    print("=" * 50)
    
    # Test 1: Provider Factory
    print("1️⃣  Testing Provider Factory")
    providers = ProviderFactory.list_providers()
    print(f"   Available providers: {providers}")
    assert "openai" in providers, "OpenAI provider should be registered"
    print("   ✅ Provider factory works")
    print()
    
    # Test 2: Agent Creation
    print("2️⃣  Testing Agent Creation")
    try:
        agent = create_openai_agent("gpt-4", "You are a test assistant.")
        print(f"   Created agent with model: {agent.model_name}")
        print("   ✅ Agent creation works")
    except Exception as e:
        print(f"   ❌ Agent creation failed: {e}")
        return
    print()
    
    # Test 3: Tool Addition
    print("3️⃣  Testing Tool Addition")
    try:
        agent.add_tool("calculator", calculator, "Do math", TOOL_SCHEMAS["calculator"])
        agent.add_tool("convert_temperature", convert_temperature, "Convert temps", TOOL_SCHEMAS["convert_temperature"])
        
        tools = agent.list_tools()
        print(f"   Added tools: {tools}")
        assert "calculator" in tools, "Calculator should be added"
        assert "convert_temperature" in tools, "Temperature converter should be added"
        print("   ✅ Tool addition works")
    except Exception as e:
        print(f"   ❌ Tool addition failed: {e}")
        return
    print()
    
    # Test 4: Provider Info
    print("4️⃣  Testing Provider Info")
    try:
        info = agent.get_provider_info()
        print(f"   Provider info: {info}")
        assert info["model_name"] == "gpt-4", "Model name should match"
        assert info["num_tools"] == 2, "Should have 2 tools"
        print("   ✅ Provider info works")
    except Exception as e:
        print(f"   ❌ Provider info failed: {e}")
        return
    print()
    
    # Test 5: Direct Tool Execution (without API)
    print("5️⃣  Testing Direct Tool Execution")
    try:
        # Test calculator directly through the provider
        from ai_interface import ToolCall
        tool_call = ToolCall(id="test", name="calculator", arguments={"operation": "add", "x": 15, "y": 25})
        result = agent.provider.execute_tool(tool_call)
        print(f"   Calculator result (15 + 25): {result}")
        assert "40" in result, "Calculator should return 40"
        
        # Test temperature conversion
        temp_call = ToolCall(id="test2", name="convert_temperature", arguments={"temperature": 100, "from_unit": "F", "to_unit": "C"})
        temp_result = agent.provider.execute_tool(temp_call)
        print(f"   Temperature conversion (100F to C): {temp_result}")
        assert "37.7" in temp_result, "Should convert 100F to ~37.7C"
        
        print("   ✅ Direct tool execution works")
    except Exception as e:
        print(f"   ❌ Direct tool execution failed: {e}")
        return
    print()
    
    print("🎉 All interface tests passed!")
    print("\n💡 The universal interface is working correctly!")
    print("💡 To test with real API calls, set your OPENAI_API_KEY and run:")
    print("   python demo_universal.py")


def demonstrate_interface_usage():
    """Show practical usage examples"""
    
    print("\n" + "=" * 60)
    print("📚 Interface Usage Examples")
    print("=" * 60)
    
    print("""
🔧 Basic Usage:
```python
from universal_agent import create_openai_agent

# Create agent
agent = create_openai_agent("gpt-4", "You are helpful.")

# Add tools
agent.add_tool("calculator", calculator, "Do math", schema)

# Chat
response = agent.chat("What's 15 + 25?")
```

🔄 Provider Switching:
```python
# Start with OpenAI
agent = UniversalAgent("openai", "gpt-4", "You are helpful.")

# Switch to Gemini (when implemented)
agent.switch_provider("gemini", "gemini-pro")

# Same interface, different model!
response = agent.chat("Hello!")
```

🛠️ Advanced Usage:
```python
# Create with custom provider instance
from openai_provider import OpenAIProvider
provider = OpenAIProvider("gpt-4")
agent = UniversalAgent(provider)

# Full control over messages
from ai_interface import MessageRole
messages = [
    agent.provider.create_message(MessageRole.USER, "Hello"),
    agent.provider.create_message(MessageRole.ASSISTANT, "Hi there!"),
    agent.provider.create_message(MessageRole.USER, "How are you?")
]
response = agent.chat_advanced(messages)
```

🎯 Benefits:
- ✅ Provider-agnostic code
- ✅ Easy model switching
- ✅ Consistent tool interface
- ✅ Future-proof architecture
- ✅ Simple migration path
""")


if __name__ == "__main__":
    test_local_interface()
    demonstrate_interface_usage()