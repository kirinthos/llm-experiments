# Universal AI Chat API Testing Guide

## 🚀 Quick Start

### 1. Start the API Server

```bash
cd chat-api
source ../venv/bin/activate
python api_server.py
```

### 2. Start the Frontend

```bash
cd chat-app
npm run dev
```

## 📋 API Endpoints Testing with curl

### Health Check

```bash
curl -X GET http://localhost:5000/health | jq
```

### Get Available Models

```bash
curl -X GET http://localhost:5000/models | jq
```

### Get Available Tools

```bash
curl -X GET http://localhost:5000/tools | jq
```

### Get Tools by Category

```bash
curl -X GET http://localhost:5000/tools/categories | jq
```

### Get Recent Logs (for debugging)

```bash
# Get last 20 log entries
curl -X GET "http://localhost:5000/logs?lines=20" | jq

# Get last 5 log entries (default is 50)
curl -X GET "http://localhost:5000/logs?lines=5" | jq '.logs[]'
```

### Simple Chat

```bash
curl -X POST http://localhost:5000/chat/simple \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you calculate 25 + 17 for me?",
    "model": "gpt-4o-mini",
    "provider": "openai"
  }' | jq
```

### Full Chat with Message History

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is 15 * 23?"}
    ],
    "model": "gpt-4o-mini",
    "provider": "openai",
    "tools_enabled": true
  }' | jq
```

### Execute Tool Directly

```bash
# Calculator
curl -X POST http://localhost:5000/tools/calculator/execute \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "operation": "multiply",
      "x": 15,
      "y": 23
    }
  }' | jq

# Temperature Conversion
curl -X POST http://localhost:5000/tools/convert_temperature/execute \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "temperature": 100,
      "from_unit": "F",
      "to_unit": "C"
    }
  }' | jq

# Random Number
curl -X POST http://localhost:5000/tools/generate_random_number/execute \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "min_val": 1,
      "max_val": 100
    }
  }' | jq
```

## 🌐 Web Automation Tools (Playwright)

### Start Browser and Navigate

```bash
# Start browser
curl -X POST http://localhost:5000/tools/start_browser/execute \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}' | jq

# Navigate to URL
curl -X POST http://localhost:5000/tools/navigate_to_url/execute \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "url": "https://example.com"
    }
  }' | jq

# Take screenshot
curl -X POST http://localhost:5000/tools/take_screenshot/execute \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}' | jq

# Get page text
curl -X POST http://localhost:5000/tools/get_page_text/execute \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}' | jq

# Close browser
curl -X POST http://localhost:5000/tools/close_browser/execute \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}' | jq
```

## 🎯 Frontend Testing

### Features to Test:

1. **Model Selection**: Try switching between different AI models
2. **Tools Dropdown**: Click the "🔧 Tools" button to see available tools
3. **Chat Integration**: Send messages and see real AI responses
4. **Connection Status**: Should show "🟢 Connected to API" if backend is
   running
5. **Tool Usage**: Ask the AI to perform calculations or other tool operations

### Sample Questions:

- "Calculate 25 \* 17"
- "What's the current time?"
- "Convert 100°F to Celsius"
- "Generate a random number between 1 and 50"
- "Analyze this text: 'Hello world, this is a test message'"
- "Start a browser and navigate to https://example.com"

## 🔧 Tool Categories

The API organizes tools into these categories:

- **Math & Logic**: Calculator
- **Utilities**: Current time, random numbers
- **Text Processing**: Word count analysis
- **Converters**: Temperature conversion
- **Web Automation**: Browser control, page interaction

## 📊 Expected Responses

### Successful Tool Execution:

```json
{
  "success": true,
  "result": 345,
  "tool": "calculator"
}
```

### AI Chat Response:

```json
{
  "response": {
    "content": "I calculated 25 * 17 for you, and the result is 425.",
    "role": "assistant",
    "timestamp": "2024-08-08T20:45:30.123Z"
  },
  "model": "gpt-4o-mini",
  "provider": "openai",
  "tools_used": true
}
```

## 🚨 Troubleshooting

- **API not responding**: Check if Flask server is running on port 5000
- **Frontend shows test mode**: API backend is not accessible, using fallback
- **Tool errors**: Check if all dependencies are installed (playwright, etc.)
- **Model errors**: Verify API keys are set in `.env` file

## 📋 Debugging with Logs

The API server now includes comprehensive logging:

**Log File**: `chat-api/api_server.log` **View Logs via API**:
`GET /logs?lines=N`

**What's Logged**:

- ✅ All incoming requests with parameters
- ✅ Provider switching attempts
- ✅ Chat generation process
- ✅ Error details with full stack traces
- ✅ Model loading and tool registration
- ✅ Response status codes and timing

**Example Log Analysis**:

```bash
# Check recent errors
curl -s "http://localhost:5000/logs?lines=100" | jq '.logs[] | select(contains("ERROR"))'

# Monitor real-time logs
tail -f chat-api/api_server.log

# Check specific request
curl -s "http://localhost:5000/logs" | jq '.logs[] | select(contains("[20250808_172625_"))'
```
