"""
Tool Registry - Centralized management of all available tools with human-readable descriptions
"""

from tools import (
    calculator, get_current_time, generate_random_number, 
    word_count, convert_temperature, TOOL_SCHEMAS
)
from playwright_tools import (
    start_browser, navigate_to_url, take_screenshot, get_page_content,
    get_page_text, click_element, fill_input, wait_for_element,
    get_element_text, close_browser, PLAYWRIGHT_TOOL_SCHEMAS
)

# Combine all tool functions
TOOL_FUNCTIONS = {
    # Basic utility tools
    'calculator': calculator,
    'get_current_time': get_current_time,
    'generate_random_number': generate_random_number,
    'word_count': word_count,
    'convert_temperature': convert_temperature,
    
    # Web automation tools
    'start_browser': start_browser,
    'navigate_to_url': navigate_to_url,
    'take_screenshot': take_screenshot,
    'get_page_content': get_page_content,
    'get_page_text': get_page_text,
    'click_element': click_element,
    'fill_input': fill_input,
    'wait_for_element': wait_for_element,
    'get_element_text': get_element_text,
    'close_browser': close_browser
}

# Combine all tool schemas
ALL_TOOL_SCHEMAS = {**TOOL_SCHEMAS, **PLAYWRIGHT_TOOL_SCHEMAS}

# Human-readable tool descriptions for the API
TOOL_DESCRIPTIONS = {
    'calculator': {
        'name': 'Calculator',
        'description': 'Perform basic mathematical operations like addition, subtraction, multiplication, division, powers, and square roots',
        'category': 'Math & Logic',
        'icon': '🧮'
    },
    'get_current_time': {
        'name': 'Current Time',
        'description': 'Get the current date and time in UTC timezone',
        'category': 'Utilities',
        'icon': '🕒'
    },
    'generate_random_number': {
        'name': 'Random Number Generator',
        'description': 'Generate random numbers within a specified range for testing or randomization',
        'category': 'Utilities',
        'icon': '🎲'
    },
    'word_count': {
        'name': 'Text Analysis',
        'description': 'Analyze text to count words, characters, and lines - useful for content analysis',
        'category': 'Text Processing',
        'icon': '📊'
    },
    'convert_temperature': {
        'name': 'Temperature Converter',
        'description': 'Convert temperatures between Celsius, Fahrenheit, and Kelvin scales',
        'category': 'Converters',
        'icon': '🌡️'
    },
    'start_browser': {
        'name': 'Start Web Browser',
        'description': 'Launch a new browser instance for web automation tasks',
        'category': 'Web Automation',
        'icon': '🌐'
    },
    'navigate_to_url': {
        'name': 'Navigate to Website',
        'description': 'Navigate the browser to a specific URL or website',
        'category': 'Web Automation',
        'icon': '🔗'
    },
    'take_screenshot': {
        'name': 'Take Screenshot',
        'description': 'Capture a screenshot of the current web page for visual analysis',
        'category': 'Web Automation',
        'icon': '📷'
    },
    'get_page_content': {
        'name': 'Get Page HTML',
        'description': 'Extract the full HTML content of the current web page',
        'category': 'Web Automation',
        'icon': '📄'
    },
    'get_page_text': {
        'name': 'Extract Page Text',
        'description': 'Extract all visible text content from the current web page',
        'category': 'Web Automation',
        'icon': '📝'
    },
    'click_element': {
        'name': 'Click Web Element',
        'description': 'Click on buttons, links, or other interactive elements on a web page',
        'category': 'Web Automation',
        'icon': '👆'
    },
    'fill_input': {
        'name': 'Fill Form Input',
        'description': 'Enter text into form fields, search boxes, or other input elements',
        'category': 'Web Automation',
        'icon': '✏️'
    },
    'wait_for_element': {
        'name': 'Wait for Element',
        'description': 'Wait for a specific element to appear on the page before proceeding',
        'category': 'Web Automation',
        'icon': '⏳'
    },
    'get_element_text': {
        'name': 'Get Element Text',
        'description': 'Extract text content from a specific element on the web page',
        'category': 'Web Automation',
        'icon': '🔍'
    },
    'close_browser': {
        'name': 'Close Browser',
        'description': 'Close the browser instance and clean up resources',
        'category': 'Web Automation',
        'icon': '❌'
    }
}

def get_all_tools():
    """Get all available tools with their descriptions and schemas"""
    tools = []
    for tool_name in TOOL_FUNCTIONS.keys():
        tool_info = TOOL_DESCRIPTIONS.get(tool_name, {})
        tools.append({
            'id': tool_name,
            'name': tool_info.get('name', tool_name.replace('_', ' ').title()),
            'description': tool_info.get('description', 'No description available'),
            'category': tool_info.get('category', 'Uncategorized'),
            'icon': tool_info.get('icon', '🔧'),
            'schema': ALL_TOOL_SCHEMAS.get(tool_name, {})
        })
    return tools

def get_tools_by_category():
    """Get tools organized by category"""
    categories = {}
    for tool in get_all_tools():
        category = tool['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(tool)
    return categories

def execute_tool(tool_name: str, **kwargs):
    """Execute a tool by name with provided arguments"""
    if tool_name not in TOOL_FUNCTIONS:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    tool_function = TOOL_FUNCTIONS[tool_name]
    try:
        result = tool_function(**kwargs)
        return {
            'success': True,
            'result': result,
            'tool': tool_name
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'tool': tool_name
        }