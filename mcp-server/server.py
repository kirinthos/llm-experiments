#!/usr/bin/env python3
"""
FastMCP Server for Universal AI Chat Tools
Provides structured tool access via Model Context Protocol
"""

import asyncio
import json
import logging
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from fastmcp import FastMCP

# Import Obsidian tools
from obsidian_tools import (
    ObsidianVaultInput, ObsidianVaultOutput,
    CreateNoteInput, CreateNoteOutput,
    ReadNoteInput, ReadNoteOutput,
    SearchNotesInput, SearchNotesOutput,
    AdvancedSearchInput, AdvancedSearchOutput,
    ListNotesInput, ListNotesOutput,
    discover_obsidian_vault,
    create_obsidian_note,
    read_obsidian_note,
    search_obsidian_notes,
    advanced_search_obsidian_notes,
    list_obsidian_notes
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Universal AI Chat Tools")

# Pydantic models for structured inputs/outputs
class CalculatorInput(BaseModel):
    expression: str = Field(..., description="Mathematical expression to evaluate (e.g., '2 + 3 * 4')")

class CalculatorOutput(BaseModel):
    result: float = Field(..., description="The calculated result")
    expression: str = Field(..., description="The original expression")

class RandomNumberInput(BaseModel):
    min_value: int = Field(1, description="Minimum value (inclusive)")
    max_value: int = Field(100, description="Maximum value (inclusive)")

class RandomNumberOutput(BaseModel):
    number: int = Field(..., description="The generated random number")
    range: str = Field(..., description="The range used")

class TemperatureInput(BaseModel):
    value: float = Field(..., description="Temperature value to convert")
    from_unit: str = Field(..., description="Source unit: 'celsius', 'fahrenheit', or 'kelvin'")
    to_unit: str = Field(..., description="Target unit: 'celsius', 'fahrenheit', or 'kelvin'")

class TemperatureOutput(BaseModel):
    original_value: float = Field(..., description="Original temperature value")
    original_unit: str = Field(..., description="Original unit")
    converted_value: float = Field(..., description="Converted temperature value")
    converted_unit: str = Field(..., description="Target unit")
    formula_used: str = Field(..., description="Conversion formula description")

class WordCountInput(BaseModel):
    text: str = Field(..., description="Text to analyze")

class WordCountOutput(BaseModel):
    word_count: int = Field(..., description="Number of words")
    character_count: int = Field(..., description="Number of characters (including spaces)")
    character_count_no_spaces: int = Field(..., description="Number of characters (excluding spaces)")
    line_count: int = Field(..., description="Number of lines")

class TimeOutput(BaseModel):
    current_time: str = Field(..., description="Current UTC time in ISO format")
    timezone: str = Field(..., description="Timezone (always UTC)")
    formatted_time: str = Field(..., description="Human-readable formatted time")

# Web automation models
class NavigateInput(BaseModel):
    url: str = Field(..., description="URL to navigate to")

class NavigateOutput(BaseModel):
    success: bool = Field(..., description="Whether navigation was successful")
    url: str = Field(..., description="Final URL after navigation")
    title: str = Field(..., description="Page title")

class ScreenshotInput(BaseModel):
    filename: Optional[str] = Field(None, description="Optional filename for screenshot")

class ScreenshotOutput(BaseModel):
    success: bool = Field(..., description="Whether screenshot was taken successfully")
    filename: str = Field(..., description="Path to the screenshot file")
    size: str = Field(..., description="Image dimensions")

class ClickInput(BaseModel):
    selector: str = Field(..., description="CSS selector for element to click")

class ClickOutput(BaseModel):
    success: bool = Field(..., description="Whether click was successful")
    selector: str = Field(..., description="Selector that was clicked")

class FillInput(BaseModel):
    selector: str = Field(..., description="CSS selector for input element")
    text: str = Field(..., description="Text to fill into the input")

class FillOutput(BaseModel):
    success: bool = Field(..., description="Whether fill was successful")
    selector: str = Field(..., description="Selector that was filled")
    text: str = Field(..., description="Text that was entered")

# Filesystem interaction models
class ReadFileInput(BaseModel):
    file_path: str = Field(..., description="Path to the file to read")
    encoding: str = Field("utf-8", description="File encoding (default: utf-8)")

class ReadFileOutput(BaseModel):
    success: bool = Field(..., description="Whether file was read successfully")
    content: str = Field(..., description="File content")
    file_path: str = Field(..., description="Path to the file")
    file_size: int = Field(..., description="File size in bytes")
    last_modified: str = Field(..., description="Last modification time")

class WriteFileInput(BaseModel):
    file_path: str = Field(..., description="Path to the file to write")
    content: str = Field(..., description="Content to write to the file")
    encoding: str = Field("utf-8", description="File encoding (default: utf-8)")
    create_dirs: bool = Field(True, description="Create parent directories if they don't exist")

class WriteFileOutput(BaseModel):
    success: bool = Field(..., description="Whether file was written successfully")
    file_path: str = Field(..., description="Path to the file")
    bytes_written: int = Field(..., description="Number of bytes written")
    created_dirs: List[str] = Field(default_factory=list, description="Directories created")

class ListDirectoryInput(BaseModel):
    directory_path: str = Field(..., description="Path to the directory to list")
    include_hidden: bool = Field(False, description="Include hidden files and directories")
    recursive: bool = Field(False, description="List subdirectories recursively")

class ListDirectoryOutput(BaseModel):
    success: bool = Field(..., description="Whether directory was listed successfully")
    directory_path: str = Field(..., description="Path to the directory")
    files: List[Dict[str, Any]] = Field(..., description="List of files with metadata")
    total_files: int = Field(..., description="Total number of files")
    total_directories: int = Field(..., description="Total number of directories")

class ExecuteCommandInput(BaseModel):
    command: str = Field(..., description="Command to execute")
    working_directory: Optional[str] = Field(None, description="Working directory for the command")
    timeout: int = Field(30, description="Command timeout in seconds")

class ExecuteCommandOutput(BaseModel):
    success: bool = Field(..., description="Whether command executed successfully")
    command: str = Field(..., description="Command that was executed")
    return_code: int = Field(..., description="Command return code")
    stdout: str = Field(..., description="Standard output")
    stderr: str = Field(..., description="Standard error")
    execution_time: float = Field(..., description="Execution time in seconds")

class SearchFilesInput(BaseModel):
    directory_path: str = Field(..., description="Directory to search in")
    pattern: str = Field(..., description="Search pattern (supports glob patterns)")
    content_search: Optional[str] = Field(None, description="Search for text within files")
    recursive: bool = Field(True, description="Search recursively in subdirectories")

class SearchFilesOutput(BaseModel):
    success: bool = Field(..., description="Whether search completed successfully")
    directory_path: str = Field(..., description="Directory that was searched")
    pattern: str = Field(..., description="Search pattern used")
    matches: List[Dict[str, Any]] = Field(..., description="List of matching files")
    total_matches: int = Field(..., description="Total number of matches")

# Tool implementations
@mcp.tool()
async def calculator(input: CalculatorInput) -> CalculatorOutput:
    """Perform mathematical calculations with basic operations"""
    try:
        # Safe evaluation of mathematical expressions
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in input.expression):
            raise ValueError("Expression contains invalid characters")
        
        # Use eval safely for basic math (in production, use a proper math parser)
        result = eval(input.expression)
        
        return CalculatorOutput(
            result=float(result),
            expression=input.expression
        )
    except Exception as e:
        raise ValueError(f"Calculation error: {str(e)}")

@mcp.tool()
async def generate_random_number(input: RandomNumberInput) -> RandomNumberOutput:
    """Generate a random number within a specified range"""
    import random
    
    if input.min_value > input.max_value:
        raise ValueError("Minimum value cannot be greater than maximum value")
    
    number = random.randint(input.min_value, input.max_value)
    
    return RandomNumberOutput(
        number=number,
        range=f"{input.min_value}-{input.max_value}"
    )

@mcp.tool()
async def convert_temperature(input: TemperatureInput) -> TemperatureOutput:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin"""
    
    # Normalize units
    from_unit = input.from_unit.lower()
    to_unit = input.to_unit.lower()
    
    valid_units = ['celsius', 'fahrenheit', 'kelvin']
    if from_unit not in valid_units or to_unit not in valid_units:
        raise ValueError(f"Units must be one of: {', '.join(valid_units)}")
    
    # Convert to Celsius first
    if from_unit == 'fahrenheit':
        celsius = (input.value - 32) * 5/9
        formula_from = f"({input.value}°F - 32) × 5/9"
    elif from_unit == 'kelvin':
        celsius = input.value - 273.15
        formula_from = f"{input.value}K - 273.15"
    else:
        celsius = input.value
        formula_from = f"{input.value}°C"
    
    # Convert from Celsius to target unit
    if to_unit == 'fahrenheit':
        result = celsius * 9/5 + 32
        formula_to = f"({celsius:.2f}°C × 9/5) + 32"
    elif to_unit == 'kelvin':
        result = celsius + 273.15
        formula_to = f"{celsius:.2f}°C + 273.15"
    else:
        result = celsius
        formula_to = f"{celsius:.2f}°C"
    
    formula_used = f"{formula_from} = {formula_to}" if from_unit != to_unit else "No conversion needed"
    
    return TemperatureOutput(
        original_value=input.value,
        original_unit=input.from_unit,
        converted_value=round(result, 2),
        converted_unit=input.to_unit,
        formula_used=formula_used
    )

@mcp.tool()
async def word_count(input: WordCountInput) -> WordCountOutput:
    """Analyze text and return word count, character count, and line count"""
    
    text = input.text
    
    # Count words (split by whitespace)
    words = len(text.split())
    
    # Count characters
    chars_with_spaces = len(text)
    chars_without_spaces = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
    
    # Count lines
    lines = len(text.split('\n'))
    
    return WordCountOutput(
        word_count=words,
        character_count=chars_with_spaces,
        character_count_no_spaces=chars_without_spaces,
        line_count=lines
    )

@mcp.tool()
async def get_current_time() -> TimeOutput:
    """Get the current date and time in UTC"""
    
    now = datetime.utcnow()
    
    return TimeOutput(
        current_time=now.isoformat() + 'Z',
        timezone='UTC',
        formatted_time=now.strftime('%Y-%m-%d %H:%M:%S UTC')
    )

# Web search tool
class WebSearchInput(BaseModel):
    query: str = Field(..., description="Search query to look up on the web")
    max_results: int = Field(5, description="Maximum number of search results to return")

class WebSearchOutput(BaseModel):
    success: bool = Field(..., description="Whether the search was successful")
    results: List[Dict[str, str]] = Field(default_factory=list, description="Search results with title, url, and snippet")
    query: str = Field(..., description="The original search query")

@mcp.tool()
async def web_search(input: WebSearchInput) -> WebSearchOutput:
    """Search the web for information using DuckDuckGo"""
    try:
        # Import duckduckgo_search if available
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return WebSearchOutput(
                success=False,
                results=[],
                query=input.query
            )
        
        # Perform search
        results = []
        with DDGS() as ddgs:
            search_results = ddgs.text(input.query, max_results=input.max_results)
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
        
        return WebSearchOutput(
            success=True,
            results=results,
            query=input.query
        )
    except Exception as e:
        return WebSearchOutput(
            success=False,
            results=[{"error": str(e)}],
            query=input.query
        )

# Web automation tools (using Playwright)
browser_instance = None

@mcp.tool()
async def start_browser() -> Dict[str, Any]:
    """Start a browser instance for web automation"""
    global browser_instance
    
    try:
        from playwright.async_api import async_playwright
        
        if browser_instance is None:
            playwright = await async_playwright().start()
            browser_instance = await playwright.chromium.launch(headless=True)
        
        return {
            "success": True,
            "message": "Browser started successfully",
            "headless": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def navigate_to_url(input: NavigateInput) -> NavigateOutput:
    """Navigate to a specific URL"""
    global browser_instance
    
    try:
        if browser_instance is None:
            await start_browser()
        
        page = await browser_instance.new_page()
        await page.goto(input.url)
        title = await page.title()
        
        return NavigateOutput(
            success=True,
            url=page.url,
            title=title
        )
    except Exception as e:
        return NavigateOutput(
            success=False,
            url=input.url,
            title=f"Error: {str(e)}"
        )

@mcp.tool()
async def take_screenshot(input: ScreenshotInput) -> ScreenshotOutput:
    """Take a screenshot of the current page"""
    global browser_instance
    
    try:
        if browser_instance is None:
            raise ValueError("Browser not started. Call start_browser first.")
        
        pages = browser_instance.pages
        if not pages:
            raise ValueError("No active pages. Navigate to a URL first.")
        
        page = pages[-1]  # Use the most recent page
        
        filename = input.filename or f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        await page.screenshot(path=filename)
        
        # Get viewport size
        viewport = await page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
        size = f"{viewport['width']}x{viewport['height']}"
        
        return ScreenshotOutput(
            success=True,
            filename=filename,
            size=size
        )
    except Exception as e:
        return ScreenshotOutput(
            success=False,
            filename=input.filename or "error.png",
            size=f"Error: {str(e)}"
        )

@mcp.tool()
async def click_element(input: ClickInput) -> ClickOutput:
    """Click on an element specified by CSS selector"""
    global browser_instance
    
    try:
        if browser_instance is None:
            raise ValueError("Browser not started. Call start_browser first.")
        
        pages = browser_instance.pages
        if not pages:
            raise ValueError("No active pages. Navigate to a URL first.")
        
        page = pages[-1]
        await page.click(input.selector)
        
        return ClickOutput(
            success=True,
            selector=input.selector
        )
    except Exception as e:
        return ClickOutput(
            success=False,
            selector=input.selector
        )

@mcp.tool()
async def fill_input(input: FillInput) -> FillOutput:
    """Fill text into an input element"""
    global browser_instance
    
    try:
        if browser_instance is None:
            raise ValueError("Browser not started. Call start_browser first.")
        
        pages = browser_instance.pages
        if not pages:
            raise ValueError("No active pages. Navigate to a URL first.")
        
        page = pages[-1]
        await page.fill(input.selector, input.text)
        
        return FillOutput(
            success=True,
            selector=input.selector,
            text=input.text
        )
    except Exception as e:
        return FillOutput(
            success=False,
            selector=input.selector,
            text=input.text
        )

# Filesystem tools
@mcp.tool()
async def read_file(input: ReadFileInput) -> ReadFileOutput:
    """Read content from a file with metadata"""
    try:
        file_path = Path(input.file_path).expanduser().resolve()
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Get file stats
        stat = file_path.stat()
        file_size = stat.st_size
        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # Read file content
        with open(file_path, 'r', encoding=input.encoding) as f:
            content = f.read()
        
        return ReadFileOutput(
            success=True,
            content=content,
            file_path=str(file_path),
            file_size=file_size,
            last_modified=last_modified
        )
        
    except Exception as e:
        return ReadFileOutput(
            success=False,
            content=f"Error reading file: {str(e)}",
            file_path=input.file_path,
            file_size=0,
            last_modified=""
        )

@mcp.tool()
async def write_file(input: WriteFileInput) -> WriteFileOutput:
    """Write content to a file, creating directories if needed"""
    try:
        file_path = Path(input.file_path).expanduser().resolve()
        created_dirs = []
        
        # Create parent directories if needed
        if input.create_dirs and not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(file_path.parent))
        
        # Write file content
        with open(file_path, 'w', encoding=input.encoding) as f:
            f.write(input.content)
        
        bytes_written = len(input.content.encode(input.encoding))
        
        return WriteFileOutput(
            success=True,
            file_path=str(file_path),
            bytes_written=bytes_written,
            created_dirs=created_dirs
        )
        
    except Exception as e:
        return WriteFileOutput(
            success=False,
            file_path=input.file_path,
            bytes_written=0,
            created_dirs=[]
        )

@mcp.tool()
async def list_directory(input: ListDirectoryInput) -> ListDirectoryOutput:
    """List directory contents with metadata"""
    try:
        dir_path = Path(input.directory_path).expanduser().resolve()
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")
        
        files = []
        total_files = 0
        total_directories = 0
        
        def scan_directory(path: Path, depth: int = 0):
            nonlocal total_files, total_directories
            
            try:
                for item in path.iterdir():
                    # Skip hidden files unless requested
                    if not input.include_hidden and item.name.startswith('.'):
                        continue
                    
                    try:
                        stat = item.stat()
                        
                        file_info = {
                            "name": item.name,
                            "path": str(item),
                            "type": "directory" if item.is_dir() else "file",
                            "size": stat.st_size if item.is_file() else 0,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "permissions": oct(stat.st_mode)[-3:],
                            "depth": depth
                        }
                        
                        files.append(file_info)
                        
                        if item.is_dir():
                            total_directories += 1
                            if input.recursive:
                                scan_directory(item, depth + 1)
                        else:
                            total_files += 1
                            
                    except (PermissionError, OSError) as e:
                        # Skip files we can't access
                        files.append({
                            "name": item.name,
                            "path": str(item),
                            "type": "unknown",
                            "error": str(e),
                            "depth": depth
                        })
                        
            except PermissionError as e:
                raise PermissionError(f"Permission denied accessing directory: {path}")
        
        scan_directory(dir_path)
        
        return ListDirectoryOutput(
            success=True,
            directory_path=str(dir_path),
            files=files,
            total_files=total_files,
            total_directories=total_directories
        )
        
    except Exception as e:
        return ListDirectoryOutput(
            success=False,
            directory_path=input.directory_path,
            files=[],
            total_files=0,
            total_directories=0
        )

@mcp.tool()
async def execute_command(input: ExecuteCommandInput) -> ExecuteCommandOutput:
    """Execute a shell command with timeout and working directory support"""
    import time
    
    try:
        start_time = time.time()
        
        # Set working directory
        cwd = None
        if input.working_directory:
            cwd = Path(input.working_directory).expanduser().resolve()
            if not cwd.exists() or not cwd.is_dir():
                raise ValueError(f"Working directory does not exist: {cwd}")
        
        # Execute command
        result = subprocess.run(
            input.command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=input.timeout
        )
        
        execution_time = time.time() - start_time
        
        return ExecuteCommandOutput(
            success=result.returncode == 0,
            command=input.command,
            return_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time=execution_time
        )
        
    except subprocess.TimeoutExpired:
        return ExecuteCommandOutput(
            success=False,
            command=input.command,
            return_code=-1,
            stdout="",
            stderr=f"Command timed out after {input.timeout} seconds",
            execution_time=input.timeout
        )
    except Exception as e:
        return ExecuteCommandOutput(
            success=False,
            command=input.command,
            return_code=-1,
            stdout="",
            stderr=str(e),
            execution_time=0.0
        )

@mcp.tool()
async def search_files(input: SearchFilesInput) -> SearchFilesOutput:
    """Search for files by name pattern and optionally by content"""
    import glob
    import re
    
    try:
        dir_path = Path(input.directory_path).expanduser().resolve()
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        matches = []
        
        # Build search pattern
        if input.recursive:
            search_pattern = str(dir_path / "**" / input.pattern)
        else:
            search_pattern = str(dir_path / input.pattern)
        
        # Find files by pattern
        for file_path in glob.glob(search_pattern, recursive=input.recursive):
            file_path = Path(file_path)
            
            if not file_path.is_file():
                continue
            
            try:
                stat = file_path.stat()
                
                match_info = {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "content_matches": []
                }
                
                # Search content if requested
                if input.content_search:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Find all matches in content
                        pattern = re.compile(input.content_search, re.IGNORECASE)
                        for i, line in enumerate(content.split('\n'), 1):
                            if pattern.search(line):
                                match_info["content_matches"].append({
                                    "line_number": i,
                                    "line_content": line.strip(),
                                    "match_positions": [m.span() for m in pattern.finditer(line)]
                                })
                    
                    except (UnicodeDecodeError, PermissionError):
                        # Skip files we can't read
                        match_info["content_matches"] = ["Error: Could not read file content"]
                
                matches.append(match_info)
                
            except (PermissionError, OSError):
                # Skip files we can't access
                continue
        
        return SearchFilesOutput(
            success=True,
            directory_path=str(dir_path),
            pattern=input.pattern,
            matches=matches,
            total_matches=len(matches)
        )
        
    except Exception as e:
        return SearchFilesOutput(
            success=False,
            directory_path=input.directory_path,
            pattern=input.pattern,
            matches=[],
            total_matches=0
        )

# Obsidian integration tools
@mcp.tool()
async def obsidian_discover_vault(input: ObsidianVaultInput) -> ObsidianVaultOutput:
    """Discover and analyze an Obsidian vault structure"""
    return await discover_obsidian_vault(input)

@mcp.tool()
async def obsidian_create_note(input: CreateNoteInput) -> CreateNoteOutput:
    """Create a new note in an Obsidian vault"""
    return await create_obsidian_note(input)

@mcp.tool()
async def obsidian_read_note(input: ReadNoteInput) -> ReadNoteOutput:
    """Read and parse an Obsidian note with frontmatter and links"""
    return await read_obsidian_note(input)

@mcp.tool()
async def obsidian_search_notes(input: SearchNotesInput) -> SearchNotesOutput:
    """Search for notes in an Obsidian vault by content, title, or tags"""
    return await search_obsidian_notes(input)

@mcp.tool()
async def obsidian_list_notes(input: ListNotesInput) -> ListNotesOutput:
    """List all notes in an Obsidian vault with metadata"""
    return await list_obsidian_notes(input)

@mcp.tool()
async def obsidian_advanced_search(input: AdvancedSearchInput) -> AdvancedSearchOutput:
    """Advanced search with ripgrep: regex, context, patterns, statistics"""
    return await advanced_search_obsidian_notes(input)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()