# Universal AI Chat - LLM Experiments

A comprehensive multi-provider AI chat application with both backend API and
frontend web interface.

## 🏗️ Project Structure

```
llm-experiments/
├── chat-api/           # Python backend with AI providers
│   ├── agent.py        # Legacy OpenAI agent
│   ├── ai_interface.py # Abstract AI provider interface
│   ├── openai_provider.py # OpenAI implementation
│   ├── gemini_provider.py # Google Gemini implementation
│   ├── universal_agent.py # Multi-provider agent
│   ├── playwright_tools.py # Web automation tools
│   ├── tools.py        # Basic utility tools
│   ├── chat.py         # CLI chat interface
│   ├── requirements.txt # Python dependencies
│   └── venv/           # Python virtual environment
│
└── chat-app/           # TypeScript frontend web application
    ├── src/
    │   ├── types.ts        # TypeScript interfaces
    │   ├── providers/      # AI provider implementations
    │   │   └── testProvider.ts # Test harness for development
    │   ├── utils/
    │   │   └── storage.ts  # localStorage conversation management
    │   ├── chat/
    │   │   ├── ChatApp.ts  # Main application logic
    │   │   └── ChatUI.ts   # User interface component
    │   ├── main.ts         # Application entry point
    │   └── style.css       # Modern CSS styling
    ├── index.html          # HTML template
    ├── package.json        # Node.js dependencies
    └── vite.config.ts      # Vite configuration
```

## 🚀 Quick Start

### Backend (Python API)

```bash
cd chat-api
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
python chat.py  # CLI interface
```

### Frontend (Web Application)

```bash
cd chat-app
npm install
npm run dev  # Starts development server
```

## ✨ Features

### Backend (chat-api)

- 🤖 **Universal AI Interface**: Abstract provider system
- 🔌 **Multiple Providers**: OpenAI, Google Gemini support
- 🛠️ **Function Calling**: Calculator, time, temperature, text analysis
- 🌐 **Web Automation**: Playwright integration for browser control
- 💬 **CLI Chat**: Terminal-based chat interface

### Frontend (chat-app)

- 💬 **Modern Chat UI**: Beautiful bubble interface
- 🎛️ **Model Selector**: Switch between AI providers easily
- 💾 **Auto-save**: Conversations stored in localStorage
- 📱 **Responsive**: Works on desktop and mobile
- 🧪 **Test Harness**: Mock AI responses for development
- ⚡ **Fast**: Built with Vite + TypeScript

## 🎯 Key Components

### Abstract AI Interface

The backend provides a universal interface (`AIProvider`) that standardizes:

- Message handling across providers
- Function calling capabilities
- Model switching
- Error handling

### Test-Driven Frontend

The frontend includes a test provider that simulates AI responses, allowing
development without API keys:

- Realistic response delays
- Provider-specific response styles
- Error simulation capabilities

### Conversation Management

- Automatic saving to localStorage
- Message history persistence
- Model switching with context preservation

## 🔮 Future Enhancements

- [ ] Connect frontend to backend API
- [ ] Add Claude/Anthropic provider
- [ ] Real-time streaming responses
- [ ] Multi-conversation support
- [ ] Export conversation history
- [ ] Plugin system for custom tools
- [ ] Voice input/output
- [ ] Collaborative chat rooms

## 🛠️ Development

### Adding New AI Providers

**Backend:**

1. Implement `AIProvider` interface in `chat-api/`
2. Register with `ProviderFactory`
3. Add to model lists in `chat.py`

**Frontend:**

1. Add models to `testProvider.ts`
2. Update provider icons in `ChatUI.ts`
3. Add provider-specific styling

### Architecture Benefits

- **Separation of Concerns**: Backend handles AI logic, frontend handles UX
- **Provider Agnostic**: Easy to add new AI providers
- **Development Friendly**: Test harness enables offline development
- **Scalable**: Clean interfaces support future expansion

## 📝 License

See LICENSE file for details.
