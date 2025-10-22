"""
REST API Server for Universal AI Chat
Provides endpoints for chat interactions and tool management
"""

import os
import json
import logging
import traceback
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from universal_agent import UniversalAgent
from ai_interface import ProviderFactory, Message, MessageRole
from tool_registry import get_all_tools, get_tools_by_category, execute_tool

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize the universal agent
def create_agent():
    """Create and configure the universal agent"""
    try:
        logger.info("Initializing Universal Agent...")
        
        # Import providers to register them
        import openai_provider
        import gemini_provider
        logger.info("Providers imported successfully")
        
        # Create agent with default OpenAI provider
        agent = UniversalAgent(
            provider='openai',
            model_name='gpt-4o-mini',
            system_prompt="You are a helpful AI assistant with access to various tools. Use them when appropriate to help users."
        )
        logger.info("Agent created with OpenAI provider")
        
        # Register all tools
        from tool_registry import TOOL_FUNCTIONS, ALL_TOOL_SCHEMAS, TOOL_DESCRIPTIONS
        tool_count = 0
        for tool_name, tool_func in TOOL_FUNCTIONS.items():
            try:
                description = TOOL_DESCRIPTIONS.get(tool_name, {}).get('description', 'No description available')
                schema = ALL_TOOL_SCHEMAS.get(tool_name, {})
                agent.add_tool(tool_name, tool_func, description, schema)
                tool_count += 1
            except Exception as tool_error:
                logger.error(f"Failed to register tool {tool_name}: {tool_error}")
        
        logger.info(f"Successfully registered {tool_count} tools")
        return agent
        
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

# Global agent instance
agent = create_agent()

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
            'version': '1.0.0',
            'agent_available': agent is not None
        }
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
            
        models = []
        
        # Get OpenAI models
        try:
            logger.info("Fetching OpenAI models...")
            openai_provider = ProviderFactory.create_provider('openai', 'gpt-4o-mini')
            openai_models = openai_provider.get_available_models()
            openai_model_list = [{
                'id': model,
                'name': model.replace('-', ' ').title(),
                'provider': 'openai',
                'description': f'OpenAI {model} model'
            } for model in openai_models]
            models.extend(openai_model_list)
            logger.info(f"Found {len(openai_models)} OpenAI models")
        except Exception as e:
            logger.error(f"Error getting OpenAI models: {e}")
            logger.error(f"OpenAI models traceback: {traceback.format_exc()}")
        
        # Get Gemini models
        try:
            if os.getenv('GEMINI_API_KEY'):
                logger.info("Fetching Gemini models...")
                gemini_provider = ProviderFactory.create_provider('gemini', 'gemini-2.5-flash')
                gemini_models = gemini_provider.get_available_models()
                gemini_model_list = [{
                    'id': model,
                    'name': model.replace('-', ' ').title(),
                    'provider': 'gemini',
                    'description': f'Google {model} model'
                } for model in gemini_models]
                models.extend(gemini_model_list)
                logger.info(f"Found {len(gemini_models)} Gemini models")
            else:
                logger.warning("GEMINI_API_KEY not found, skipping Gemini models")
        except Exception as e:
            logger.error(f"Error getting Gemini models: {e}")
            logger.error(f"Gemini models traceback: {traceback.format_exc()}")
        
        logger.info(f"Returning {len(models)} total models")
        return jsonify({
            'models': models,
            'total': len(models)
        })
    except Exception as e:
        logger.error(f"Models endpoint failed: {e}")
        logger.error(f"Models endpoint traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/tools', methods=['GET'])
def get_available_tools():
    """Get all available tools with descriptions"""
    try:
        category = request.args.get('category')
        
        if category:
            tools_by_category = get_tools_by_category()
            tools = tools_by_category.get(category, [])
        else:
            tools = get_all_tools()
        
        return jsonify({
            'tools': tools,
            'total': len(tools),
            'categories': list(get_tools_by_category().keys())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tools/categories', methods=['GET'])
def get_tool_categories():
    """Get tools organized by categories"""
    try:
        categories = get_tools_by_category()
        return jsonify({
            'categories': categories,
            'total_categories': len(categories),
            'total_tools': sum(len(tools) for tools in categories.values())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tools/<tool_name>/execute', methods=['POST'])
def execute_single_tool(tool_name):
    """Execute a single tool directly"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        kwargs = data.get('arguments', {})
        result = execute_tool(tool_name, **kwargs)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tool': tool_name
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint for AI interactions"""
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Chat endpoint requested")
    
    try:
        if not agent:
            logger.error(f"[{request_id}] Agent not available")
            return jsonify({'error': 'Agent not available'}), 500
            
        data = request.get_json()
        if not data:
            logger.error(f"[{request_id}] No request body provided")
            return jsonify({'error': 'Request body required'}), 400
        
        logger.info(f"[{request_id}] Request data keys: {list(data.keys())}")
        
        # Extract request parameters
        messages_data = data.get('messages', [])
        model = data.get('model', 'gpt-4o-mini')
        provider = data.get('provider', 'openai')
        max_tokens = data.get('max_tokens', 1000)
        temperature = data.get('temperature', 0.7)
        tools_enabled = data.get('tools_enabled', True)
        
        logger.info(f"[{request_id}] Parameters - Model: {model}, Provider: {provider}, Messages: {len(messages_data)}, Tools: {tools_enabled}")
        
        if not messages_data:
            logger.error(f"[{request_id}] No messages provided")
            return jsonify({'error': 'Messages required'}), 400
        
        # Convert messages to internal format
        messages = []
        for i, msg_data in enumerate(messages_data):
            try:
                message = Message(
                    role=MessageRole(msg_data.get('role', 'user')),
                    content=msg_data.get('content', ''),
                    tool_call_id=msg_data.get('tool_call_id'),
                    name=msg_data.get('name')
                )
                messages.append(message)
                logger.debug(f"[{request_id}] Message {i}: {msg_data.get('role')} - {len(msg_data.get('content', ''))} chars")
            except Exception as msg_error:
                logger.error(f"[{request_id}] Error processing message {i}: {msg_error}")
                return jsonify({'error': f'Invalid message format at index {i}'}), 400
        
        # Set up agent with specified model and provider
        try:
            logger.info(f"[{request_id}] Switching to provider {provider} with model {model}")
            agent.switch_provider(provider, model)
        except Exception as switch_error:
            logger.error(f"[{request_id}] Provider switch failed: {switch_error}")
            logger.error(f"[{request_id}] Switch traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Failed to switch to {provider}/{model}: {str(switch_error)}'}), 500
        
        # Get AI response
        try:
            if tools_enabled and len(messages) == 1 and messages[0].role == MessageRole.USER:
                logger.info(f"[{request_id}] Using single message chat with tools")
                response_content = agent.chat(
                    messages[0].content,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                response = {
                    'response': {
                        'content': response_content,
                        'role': 'assistant',
                        'timestamp': datetime.now().isoformat()
                    },
                    'model': model,
                    'provider': provider,
                    'tools_used': True  # chat may use tools
                }
                logger.info(f"[{request_id}] Single message response length: {len(response_content)}")
                return jsonify(response)
            else:
                logger.info(f"[{request_id}] Using multi-message chat")
                response_content = agent.chat_advanced(
                    messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                response = {
                    'response': {
                        'content': response_content,
                        'role': 'assistant',
                        'timestamp': datetime.now().isoformat()
                    },
                    'model': model,
                    'provider': provider,
                    'tools_used': True  # chat_advanced may use tools
                }
                logger.info(f"[{request_id}] Multi-message response length: {len(response_content)}")
                return jsonify(response)
                
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

@app.route('/chat/simple', methods=['POST'])
def chat_simple():
    """Simplified chat endpoint for single message interactions"""
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Simple chat endpoint requested")
    
    try:
        if not agent:
            logger.error(f"[{request_id}] Agent not available")
            return jsonify({'error': 'Agent not available'}), 500
            
        data = request.get_json()
        if not data:
            logger.error(f"[{request_id}] No request body provided")
            return jsonify({'error': 'Request body required'}), 400
        
        message = data.get('message', '')
        model = data.get('model', 'gpt-4o-mini')
        provider = data.get('provider', 'openai')
        
        logger.info(f"[{request_id}] Simple chat - Model: {model}, Provider: {provider}, Message length: {len(message)}")
        
        if not message:
            logger.error(f"[{request_id}] No message provided")
            return jsonify({'error': 'Message required'}), 400
        
        # Set up agent
        try:
            logger.info(f"[{request_id}] Switching to provider {provider} with model {model}")
            agent.switch_provider(provider, model)
        except Exception as switch_error:
            logger.error(f"[{request_id}] Provider switch failed: {switch_error}")
            logger.error(f"[{request_id}] Switch traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Failed to switch to {provider}/{model}: {str(switch_error)}'}), 500
        
        # Get response
        try:
            logger.info(f"[{request_id}] Generating response...")
            response_content = agent.chat(message)
            logger.info(f"[{request_id}] Response generated, length: {len(response_content)}")
            
            return jsonify({
                'response': response_content,
                'model': model,
                'provider': provider,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as chat_error:
            logger.error(f"[{request_id}] Chat generation failed: {chat_error}")
            logger.error(f"[{request_id}] Chat traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Chat generation failed: {str(chat_error)}'}), 500
        
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error in simple chat endpoint: {e}")
        logger.error(f"[{request_id}] Full traceback: {traceback.format_exc()}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent log entries for debugging"""
    try:
        lines = int(request.args.get('lines', 50))  # Default to last 50 lines
        
        if not os.path.exists('api_server.log'):
            return jsonify({'logs': [], 'message': 'No log file found'})
        
        with open('api_server.log', 'r') as f:
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
            'GET /tools/categories',
            'GET /logs?lines=N',
            'POST /tools/<tool_name>/execute',
            'POST /chat',
            'POST /chat/simple'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Universal AI Chat API Server...")
    logger.info(f"📊 Available tools: {len(get_all_tools())}")
    logger.info(f"🤖 Agent status: {'Ready' if agent else 'Error'}")
    logger.info("📋 Log file: api_server.log")
    
    print("🚀 Starting Universal AI Chat API Server...")
    print(f"📊 Available tools: {len(get_all_tools())}")
    print(f"🤖 Agent status: {'Ready' if agent else 'Error'}")
    print("📋 Logs will be written to api_server.log")
    
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )