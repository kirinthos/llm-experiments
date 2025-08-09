"""
Collection of tools/functions that can be used by the OpenAI agent.
"""

import math
import random
from datetime import datetime
from typing import Union


def calculator(operation: str, x: float, y: float = None) -> float:
    """
    Perform basic mathematical operations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide, power, sqrt)
        x: First number
        y: Second number (not required for sqrt)
        
    Returns:
        The result of the mathematical operation
    """
    operations = {
        "add": lambda a, b: a + b,
        "subtract": lambda a, b: a - b,
        "multiply": lambda a, b: a * b,
        "divide": lambda a, b: a / b if b != 0 else float('inf'),
        "power": lambda a, b: a ** b,
        "sqrt": lambda a, b: math.sqrt(a)  # b is ignored for sqrt
    }
    
    if operation not in operations:
        raise ValueError(f"Unknown operation: {operation}")
    
    if operation == "sqrt":
        if x < 0:
            raise ValueError("Cannot take square root of negative number")
        return math.sqrt(x)
    
    if y is None:
        raise ValueError(f"Operation '{operation}' requires two numbers")
    
    return operations[operation](x, y)


def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current time.
    
    Args:
        timezone: Timezone (currently only supports UTC)
        
    Returns:
        Current time as a formatted string
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S UTC")


def generate_random_number(min_val: int = 1, max_val: int = 100) -> int:
    """
    Generate a random number within a specified range.
    
    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
        
    Returns:
        A random integer between min_val and max_val
    """
    return random.randint(min_val, max_val)


def word_count(text: str) -> dict:
    """
    Count words, characters, and lines in a text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary with word count, character count, and line count
    """
    words = len(text.split())
    characters = len(text)
    characters_no_spaces = len(text.replace(" ", ""))
    lines = len(text.split("\n"))
    
    return {
        "words": words,
        "characters": characters,
        "characters_no_spaces": characters_no_spaces,
        "lines": lines
    }


def convert_temperature(temperature: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between Celsius, Fahrenheit, and Kelvin.
    
    Args:
        temperature: Temperature value to convert
        from_unit: Source unit (C, F, or K)
        to_unit: Target unit (C, F, or K)
        
    Returns:
        Converted temperature
    """
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()
    
    # Convert to Celsius first
    if from_unit == "F":
        celsius = (temperature - 32) * 5/9
    elif from_unit == "K":
        celsius = temperature - 273.15
    elif from_unit == "C":
        celsius = temperature
    else:
        raise ValueError(f"Unknown temperature unit: {from_unit}")
    
    # Convert from Celsius to target
    if to_unit == "C":
        return celsius
    elif to_unit == "F":
        return celsius * 9/5 + 32
    elif to_unit == "K":
        return celsius + 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {to_unit}")


# Function schemas for OpenAI function calling
TOOL_SCHEMAS = {
    "calculator": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt"],
                "description": "The mathematical operation to perform"
            },
            "x": {
                "type": "number",
                "description": "The first number"
            },
            "y": {
                "type": "number",
                "description": "The second number (not required for sqrt operation)"
            }
        },
        "required": ["operation", "x"]
    },
    
    "get_current_time": {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "Timezone (currently only UTC supported)",
                "default": "UTC"
            }
        },
        "required": []
    },
    
    "generate_random_number": {
        "type": "object",
        "properties": {
            "min_val": {
                "type": "integer",
                "description": "Minimum value (inclusive)",
                "default": 1
            },
            "max_val": {
                "type": "integer",
                "description": "Maximum value (inclusive)",
                "default": 100
            }
        },
        "required": []
    },
    
    "word_count": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to analyze"
            }
        },
        "required": ["text"]
    },
    
    "convert_temperature": {
        "type": "object",
        "properties": {
            "temperature": {
                "type": "number",
                "description": "Temperature value to convert"
            },
            "from_unit": {
                "type": "string",
                "enum": ["C", "F", "K"],
                "description": "Source temperature unit (C=Celsius, F=Fahrenheit, K=Kelvin)"
            },
            "to_unit": {
                "type": "string",
                "enum": ["C", "F", "K"],
                "description": "Target temperature unit (C=Celsius, F=Fahrenheit, K=Kelvin)"
            }
        },
        "required": ["temperature", "from_unit", "to_unit"]
    }
}