#!/usr/bin/env python3
"""
Enhanced REST API Server with MCP Support
Provides structured tool access via Model Context Protocol integration
"""

import os
import sys
import json
import logging
import traceback
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for config loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import get_config, get_config_loader

from mcp_universal_agent import MCPUniversalAgent

# Import providers to register them
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai-providers'))
import openai_provider
import gemini_provider

# Load environment variables and configuration
load_dotenv()

# Load TOML configuration
try:
    config = get_config()
    config_loader = get_config_loader()
    logger = logging.getLogger(__name__)
    logger.info(f"✅ Configuration loaded - API: {config.server.api_url}, Frontend: {config.server.frontend_url}")
except Exception as e:
    print(f"❌ Failed to load configuration: {e}")
    exit(1)

app = Flask(__name__)
CORS(app, origins=config.api.cors_origins, methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])  # Enable CORS with configured origins

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global agent instance
agent: MCPUniversalAgent = None

async def create_agent():
    """Create and initialize the MCP-enhanced universal agent"""
    global agent
    
    try:
        logger.info("Initializing MCP Universal Agent...")
        
        # Create agent with default OpenAI provider
        agent = MCPUniversalAgent(
            provider='openai',
            model_name='gpt-4o-mini',
            system_prompt="""You are an advanced AI assistant with access to structured tools via MCP.

Available capabilities include:
- Mathematical calculations with detailed step-by-step results
- Web automation (browser control, navigation, screenshots)
- Text analysis and word counting
- Time and date operations
- Temperature conversions with formulas
- Random number generation

When using tools, always:
1. Use the structured inputs correctly
2. Interpret the structured outputs to provide comprehensive responses
3. Show your work and explain the results
4. Chain multiple tools when needed for complex tasks

Be helpful, accurate, and make full use of the available structured tools."""
        )
        
        # Initialize the agent
        success = await agent.initialize()
        
        if success:
            tools = await agent.get_available_tools()
            logger.info(f"Successfully initialized agent with {len(tools)} MCP tools")
            return True
        else:
            logger.error("Failed to initialize MCP agent")
            return False
        
    except Exception as e:
        logger.error(f"Error creating MCP agent: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

# Initialize agent at startup
async def init_agent():
    """Initialize the agent asynchronously"""
    await create_agent()

# Request logging middleware
@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.path}")
    if request.is_json and request.get_json():
        # Log request data but mask sensitive info
        data = request.get_json()
        safe_data = {k: (v if k not in ['api_key', 'password'] else '***') for k, v in data.items()}
        logger.info(f"Request data: {safe_data}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    try:
        response = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0-mcp',
            'agent_available': agent is not None,
            'mcp_enabled': True
        }
        
        if agent:
            summary = agent.get_conversation_summary()
            response['agent_info'] = summary
        
        logger.info(f"Health check response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'error': 'Health check failed', 'details': str(e)}), 500

@app.route('/models', methods=['GET'])
def get_models():
    """Get available AI models"""
    logger.info("Models endpoint requested")
    try:
        if not agent:
            logger.error("Agent not available for models endpoint")
            return jsonify({'error': 'Agent not available'}), 500
        
        # Get models from TOML configuration
        models = config_loader.get_all_models()
        
        logger.info(f"Returning {len(models)} models")
        return jsonify({
            'models': models,
            'total': len(models)
        })
        
    except Exception as e:
        logger.error(f"Models endpoint failed: {e}")
        logger.error(f"Models endpoint traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/tools', methods=['GET'])
async def get_available_tools():
    """Get all available MCP tools with descriptions"""
    logger.info("Tools endpoint requested")
    try:
        if not agent:
            logger.error("Agent not available for tools endpoint")
            return jsonify({'error': 'Agent not available'}), 500
        
        tools = await agent.get_available_tools()
        
        # Group tools by category
        categories = {}
        for tool in tools:
            category = tool.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(tool)
        
        logger.info(f"Returning {len(tools)} MCP tools in {len(categories)} categories")
        return jsonify({
            'tools': tools,
            'categories': categories,
            'total': len(tools)
        })
        
    except Exception as e:
        logger.error(f"Tools endpoint failed: {e}")
        logger.error(f"Tools endpoint traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST', 'OPTIONS'])
async def chat_full():
    """Enhanced chat endpoint with full conversation history and MCP tool support"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        return '', 200
    
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Full chat endpoint requested")
    
    try:
        if not agent:
            logger.error(f"[{request_id}] Agent not available")
            return jsonify({'error': 'Agent not available'}), 500
        
        data = request.get_json()
        if not data:
            logger.error(f"[{request_id}] No request body provided")
            return jsonify({'error': 'Request body required'}), 400
        
        messages = data.get('messages', [])
        model = data.get('model', config.models.default_model)
        provider = data.get('provider', config.models.default_provider)
        tools_enabled = data.get('tools_enabled', config.mcp.enabled)
        
        logger.info(f"[{request_id}] Full chat - Model: {model}, Provider: {provider}, Messages: {len(messages)}, Tools: {tools_enabled}")
        
        if not messages:
            logger.error(f"[{request_id}] No messages provided")
            return jsonify({'error': 'Messages required'}), 400
        
        # Switch provider if needed
        if agent.provider_name != provider or agent.model_name != model:
            try:
                logger.info(f"[{request_id}] Switching to provider {provider} with model {model}")
                agent.switch_provider(provider, model)
            except Exception as switch_error:
                logger.error(f"[{request_id}] Provider switch failed: {switch_error}")
                return jsonify({'error': f'Failed to switch to {provider}/{model}: {str(switch_error)}'}), 500
        
        # Build conversation context from message history
        conversation_context = []
        for msg in messages:
            conversation_context.append(f"{msg.get('role', 'user')}: {msg.get('content', '')}")
        
        # Use the latest message as the main input
        latest_message = messages[-1].get('content', '') if messages else ''
        
        # Get response from MCP-enhanced agent with conversation context
        try:
            logger.info(f"[{request_id}] Generating response with conversation history...")
            response_content, thinking_steps = await agent.chat_with_thinking(
                latest_message,
                temperature=0.7,
                max_tokens=1000,
                use_tools=tools_enabled
            )
            logger.info(f"[{request_id}] Response generated, length: {len(response_content)}, thinking steps: {len(thinking_steps)}")
            
            return jsonify({
                'response': {
                    'content': response_content
                },
                'thinking_steps': thinking_steps,
                'model': model,
                'provider': provider,
                'timestamp': datetime.now().isoformat(),
                'mcp_enabled': config.mcp.enabled,
                'tools_used': tools_enabled
            })
            
        except Exception as chat_error:
            logger.error(f"[{request_id}] Chat generation failed: {chat_error}")
            logger.error(f"[{request_id}] Chat traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Chat generation failed: {str(chat_error)}'}), 500
        
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error in chat endpoint: {e}")
        logger.error(f"[{request_id}] Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/chat/simple', methods=['POST', 'OPTIONS'])
async def chat_simple():
    """Enhanced chat endpoint with MCP tool support"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        return '', 200
    
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Enhanced chat endpoint requested")
    
    try:
        if not agent:
            logger.error(f"[{request_id}] Agent not available")
            return jsonify({'error': 'Agent not available'}), 500
        
        data = request.get_json()
        if not data:
            logger.error(f"[{request_id}] No request body provided")
            return jsonify({'error': 'Request body required'}), 400
        
        message = data.get('message', '')
        model = data.get('model', config.models.default_model)
        provider = data.get('provider', config.models.default_provider)
        temperature = data.get('temperature', config.models.temperature_default)
        max_tokens = data.get('max_tokens', config.models.max_tokens_default)
        use_tools = data.get('use_tools', config.mcp.enabled)
        
        logger.info(f"[{request_id}] Enhanced chat - Model: {model}, Provider: {provider}, Message length: {len(message)}, Tools: {use_tools}")
        
        if not message:
            logger.error(f"[{request_id}] No message provided")
            return jsonify({'error': 'Message required'}), 400
        
        # Switch provider if needed
        if agent.provider_name != provider or agent.model_name != model:
            try:
                logger.info(f"[{request_id}] Switching to provider {provider} with model {model}")
                agent.switch_provider(provider, model)
            except Exception as switch_error:
                logger.error(f"[{request_id}] Provider switch failed: {switch_error}")
                return jsonify({'error': f'Failed to switch to {provider}/{model}: {str(switch_error)}'}), 500
        
        # Get response from MCP-enhanced agent with thinking steps
        try:
            logger.info(f"[{request_id}] Generating enhanced response with MCP tools...")
            response_content, thinking_steps = await agent.chat_with_thinking(
                message,
                temperature=temperature,
                max_tokens=max_tokens,
                use_tools=use_tools
            )
            logger.info(f"[{request_id}] Enhanced response generated, length: {len(response_content)}, thinking steps: {len(thinking_steps)}")
            
            return jsonify({
                'response': response_content,
                'thinking_steps': thinking_steps,
                'model': model,
                'provider': provider,
                'timestamp': datetime.now().isoformat(),
                'mcp_enabled': True,
                'tools_used': use_tools
            })
            
        except Exception as chat_error:
            logger.error(f"[{request_id}] Enhanced chat generation failed: {chat_error}")
            logger.error(f"[{request_id}] Chat traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Enhanced chat generation failed: {str(chat_error)}'}), 500
        
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error in enhanced chat endpoint: {e}")
        logger.error(f"[{request_id}] Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/agent/summary', methods=['GET'])
def get_agent_summary():
    """Get current agent conversation summary"""
    try:
        if not agent:
            return jsonify({'error': 'Agent not available'}), 500
        
        summary = agent.get_conversation_summary()
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Agent summary failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/agent/clear', methods=['POST'])
def clear_agent():
    """Clear agent conversation history"""
    try:
        if not agent:
            return jsonify({'error': 'Agent not available'}), 500
        
        agent.clear_conversation()
        return jsonify({'success': True, 'message': 'Conversation cleared'})
        
    except Exception as e:
        logger.error(f"Agent clear failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/config', methods=['GET'])
async def get_config_endpoint():
    """Get current server configuration for frontend"""
    try:
        tools_count = 0
        if agent and config.mcp.enabled:
            try:
                tools = await agent.get_available_tools()
                tools_count = len(tools)
            except:
                tools_count = 0
        
        return jsonify({
            'server': {
                'apiHost': config.server.api_host,
                'apiPort': config.server.api_port,
                'apiUrl': config.server.api_url,
                'frontendHost': config.server.frontend_host,
                'frontendPort': config.server.frontend_port,
                'frontendUrl': config.server.frontend_url,
                'healthCheckTimeout': config.server.health_check_timeout,
                'healthCheckInterval': config.server.health_check_interval
            },
            'ui': {
                'theme': config.ui.theme,
                'autoRefreshStatus': config.ui.auto_refresh_status,
                'showDebugInfo': config.ui.show_debug_info
            },
            'mcp': {
                'enabled': config.mcp.enabled,
                'toolsAvailable': tools_count
            }
        })
        
    except Exception as e:
        logger.error(f"Config endpoint failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent log entries for debugging"""
    try:
        lines = int(request.args.get('lines', 50))
        
        if not os.path.exists('mcp_api_server.log'):
            return jsonify({'logs': [], 'message': 'No log file found'})
        
        with open('mcp_api_server.log', 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return jsonify({
            'logs': [line.strip() for line in recent_lines],
            'total_lines': len(all_lines),
            'showing': len(recent_lines)
        })
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error for {request.method} {request.path}")
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /health',
            'GET /models', 
            'GET /tools',
            'GET /config',
            'GET /logs?lines=N',
            'GET /agent/summary',
            'POST /agent/clear',
            'POST /chat',
            'POST /chat/simple'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Enhanced Universal AI Chat API Server with MCP...")
    
    # Initialize agent
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(init_agent())
        
        if agent:
            logger.info("✅ MCP Agent initialized successfully")
            print("🚀 Starting Enhanced Universal AI Chat API Server with MCP...")
            print("🔧 MCP (Model Context Protocol) enabled")
            print("📋 Logs will be written to mcp_api_server.log")
            
            # Development server with configured port
            app.run(
                host=config.server.api_host,
                port=config.server.api_port,
                debug=config.development.debug_mode
            )
        else:
            logger.error("❌ Failed to initialize MCP agent")
            print("❌ Failed to initialize MCP agent - check logs")
            
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Failed to start server: {e}")
    finally:
        loop.close()