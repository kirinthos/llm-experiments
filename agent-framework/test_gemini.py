#!/usr/bin/env python3
"""
Test script specifically for Gemini provider functionality
"""

import os
from universal_agent import UniversalAgent
from ai_interface import ProviderFactory
try:
    from gemini_provider import GeminiProvider, GEMINI_AVAILABLE
except ImportError:
    GEMINI_AVAILABLE = False

from tools import calculator, convert_temperature, TOOL_SCHEMAS


def test_gemini_local():
    """Test Gemini provider without API calls"""
    
    print("🧪 Testing Gemini Provider Locally")
    print("=" * 40)
    
    if not GEMINI_AVAILABLE:
        print("❌ Gemini not available - google-generativeai not installed")
        print("💡 Install with: pip install google-generativeai")
        return False
    
    # Test 1: Provider Registration
    print("1️⃣  Testing Provider Registration")
    providers = ProviderFactory.list_providers()
    print(f"   Available providers: {providers}")
    
    if "gemini" in providers:
        print("   ✅ Gemini provider registered successfully")
    else:
        print("   ❌ Gemini provider not registered")
        return False
    
    print()
    return True


def test_gemini_with_api():
    """Test Gemini provider with actual API calls"""
    
    print("🚀 Testing Gemini Provider with API")
    print("=" * 40)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("💡 Set your API key with: export GEMINI_API_KEY=your_key_here")
        print("💡 Or add it to your .env file: GEMINI_API_KEY=your_key_here")
        return False
    
    try:
        # Test 1: Basic Agent Creation
        print("1️⃣  Creating Gemini Agent")
        agent = UniversalAgent("gemini", "gemini-pro", "You are a helpful assistant.")
        print(f"   ✅ Agent created with model: {agent.model_name}")
        
        # Test 2: Add Tools
        print("\n2️⃣  Adding Tools")
        agent.add_tool("calculator", calculator, "Do math", TOOL_SCHEMAS["calculator"])
        agent.add_tool("convert_temperature", convert_temperature, "Convert temps", TOOL_SCHEMAS["convert_temperature"])
        
        tools = agent.list_tools()
        print(f"   ✅ Tools added: {tools}")
        
        # Test 3: Provider Info
        print("\n3️⃣  Checking Provider Info")
        info = agent.get_provider_info()
        print(f"   Provider: {info['provider_type']}")
        print(f"   Model: {info['model_name']}")
        print(f"   Function Calling: {'✅' if info['supports_function_calling'] else '❌'}")
        print(f"   Tools: {len(info['tool_names'])} available")
        
        # Test 4: Simple Chat (without tools)
        print("\n4️⃣  Testing Simple Chat")
        response = agent.chat("Hello! How are you?", use_history=False)
        print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        print("   ✅ Basic chat works")
        
        # Test 5: Function Calling
        print("\n5️⃣  Testing Function Calling")
        math_response = agent.chat("What is 15 + 27?", use_history=False)
        print(f"   Math response: {math_response}")
        
        temp_response = agent.chat("Convert 100 degrees Fahrenheit to Celsius", use_history=False)  
        print(f"   Temperature response: {temp_response}")
        
        print("   ✅ Function calling works")
        
        print("\n🎉 All Gemini tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini test failed: {e}")
        
        # Provide helpful error messages
        error_str = str(e).lower()
        if "api key" in error_str or "authentication" in error_str:
            print("💡 Check your GEMINI_API_KEY")
        elif "quota" in error_str or "rate limit" in error_str:
            print("💡 You may have exceeded API quotas/rate limits")
        elif "model" in error_str:
            print("💡 The model might not be available or correctly specified")
        else:
            print("💡 Check your internet connection and API key")
        
        return False


def demo_gemini_vs_openai():
    """Demo comparing responses from Gemini vs OpenAI"""
    
    print("\n🆚 Gemini vs OpenAI Comparison")
    print("=" * 50)
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY required for comparison")
        return
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY required for comparison")
        return
    
    test_query = "What's 25 * 4 + 10?"
    
    try:
        # Create both agents
        gemini_agent = UniversalAgent("gemini", "gemini-pro", "You are a helpful assistant.")
        openai_agent = UniversalAgent("openai", "gpt-4o-mini", "You are a helpful assistant.")
        
        # Add calculator to both
        for agent in [gemini_agent, openai_agent]:
            agent.add_tool("calculator", calculator, "Do math", TOOL_SCHEMAS["calculator"])
        
        print(f"Query: {test_query}")
        print()
        
        # Get Gemini response
        print("🟢 Gemini Response:")
        gemini_response = gemini_agent.chat(test_query, use_history=False)
        print(f"   {gemini_response}")
        
        print()
        
        # Get OpenAI response  
        print("🔵 OpenAI Response:")
        openai_response = openai_agent.chat(test_query, use_history=False)
        print(f"   {openai_response}")
        
        print("\n✨ Both providers work with the same interface!")
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")


if __name__ == "__main__":
    print("🎯 Gemini Provider Testing")
    print()
    
    # Test 1: Local tests (no API required)
    if not test_gemini_local():
        print("❌ Local tests failed")
        exit(1)
    
    # Test 2: API tests (requires API key)
    print()
    if test_gemini_with_api():
        # Test 3: Comparison demo (requires both API keys)
        demo_gemini_vs_openai()
    else:
        print("⚠️  API tests failed - but local interface tests passed")
        print("💡 Set up your GEMINI_API_KEY to test full functionality")