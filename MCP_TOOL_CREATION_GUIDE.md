# 🛠️ MCP Tool Creation Guide

## 📋 **Complete Guide to Creating New Tools for Universal AI Chat**

This guide will walk you through creating powerful, structured tools for your
MCP-enabled AI chat system. Perfect for building custom integrations like
Obsidian vault management!

## 🏗️ **MCP Tool Architecture**

### **Components Overview**:

```
MCP Tool = Pydantic Models + Tool Function + Registration
```

1. **Input Model**: Defines and validates tool parameters
2. **Output Model**: Structures the response data
3. **Tool Function**: Implements the actual functionality
4. **Registration**: Adds tool to FastMCP server

## 🎯 **Step-by-Step Tool Creation**

### **Step 1: Define Pydantic Models**

Create structured input/output models for type safety:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Input model - defines what the tool accepts
class MyToolInput(BaseModel):
    required_param: str = Field(..., description="Required parameter description")
    optional_param: Optional[str] = Field(None, description="Optional parameter")
    number_param: int = Field(default=10, description="Number with default value")
    boolean_param: bool = Field(True, description="Boolean parameter")

# Output model - defines what the tool returns
class MyToolOutput(BaseModel):
    success: bool = Field(..., description="Whether operation was successful")
    result: str = Field(..., description="Main result of the operation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    items_processed: int = Field(0, description="Number of items processed")
```

### **Step 2: Implement Tool Function**

Create the tool function with proper error handling:

```python
@mcp.tool()
async def my_custom_tool(input: MyToolInput) -> MyToolOutput:
    """
    Brief description of what this tool does

    This tool performs X operation and returns Y results.
    Use it when you need to accomplish Z tasks.
    """
    try:
        # Your tool logic here
        result = perform_operation(
            input.required_param,
            input.optional_param,
            input.number_param
        )

        # Return structured success response
        return MyToolOutput(
            success=True,
            result=result,
            metadata={"operation_time": "0.5s", "version": "1.0"},
            items_processed=len(result) if isinstance(result, list) else 1
        )

    except Exception as e:
        # Return structured error response
        return MyToolOutput(
            success=False,
            result=f"Error: {str(e)}",
            metadata={"error_type": type(e).__name__},
            items_processed=0
        )
```

### **Step 3: Add to MCP Server**

Add your models and function to `/mcp-server/server.py`:

```python
# Add imports at the top
from my_custom_module import perform_operation

# Add models after existing ones
class MyToolInput(BaseModel):
    # ... your input model

class MyToolOutput(BaseModel):
    # ... your output model

# Add tool function after existing tools
@mcp.tool()
async def my_custom_tool(input: MyToolInput) -> MyToolOutput:
    # ... your tool function
```

## 🗂️ **Real-World Examples**

### **Example 1: File Operations Tool**

```python
class FileOperationInput(BaseModel):
    operation: str = Field(..., description="Operation: 'read', 'write', 'delete', 'copy'")
    source_path: str = Field(..., description="Source file path")
    target_path: Optional[str] = Field(None, description="Target path for copy operations")
    content: Optional[str] = Field(None, description="Content for write operations")

class FileOperationOutput(BaseModel):
    success: bool = Field(..., description="Operation success status")
    operation: str = Field(..., description="Operation that was performed")
    file_path: str = Field(..., description="File path that was operated on")
    content: Optional[str] = Field(None, description="File content for read operations")
    bytes_affected: int = Field(0, description="Number of bytes read/written")

@mcp.tool()
async def file_operation(input: FileOperationInput) -> FileOperationOutput:
    """Perform file operations: read, write, delete, or copy files"""
    try:
        file_path = Path(input.source_path).expanduser().resolve()

        if input.operation == "read":
            content = file_path.read_text()
            return FileOperationOutput(
                success=True,
                operation="read",
                file_path=str(file_path),
                content=content,
                bytes_affected=len(content.encode())
            )

        elif input.operation == "write":
            file_path.write_text(input.content or "")
            return FileOperationOutput(
                success=True,
                operation="write",
                file_path=str(file_path),
                bytes_affected=len((input.content or "").encode())
            )

        # ... other operations

    except Exception as e:
        return FileOperationOutput(
            success=False,
            operation=input.operation,
            file_path=input.source_path,
            bytes_affected=0
        )
```

### **Example 2: API Integration Tool**

```python
class APICallInput(BaseModel):
    url: str = Field(..., description="API endpoint URL")
    method: str = Field("GET", description="HTTP method")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    data: Optional[Dict[str, Any]] = Field(None, description="Request body data")
    timeout: int = Field(30, description="Request timeout in seconds")

class APICallOutput(BaseModel):
    success: bool = Field(..., description="Request success status")
    status_code: int = Field(..., description="HTTP status code")
    response_data: Dict[str, Any] = Field(..., description="Response data")
    headers: Dict[str, str] = Field(..., description="Response headers")
    execution_time: float = Field(..., description="Request execution time")

@mcp.tool()
async def api_call(input: APICallInput) -> APICallOutput:
    """Make HTTP API calls with full request/response handling"""
    import httpx
    import time

    try:
        start_time = time.time()

        async with httpx.AsyncClient(timeout=input.timeout) as client:
            response = await client.request(
                method=input.method,
                url=input.url,
                headers=input.headers,
                json=input.data
            )

        execution_time = time.time() - start_time

        return APICallOutput(
            success=response.is_success,
            status_code=response.status_code,
            response_data=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"text": response.text},
            headers=dict(response.headers),
            execution_time=execution_time
        )

    except Exception as e:
        return APICallOutput(
            success=False,
            status_code=0,
            response_data={"error": str(e)},
            headers={},
            execution_time=0.0
        )
```

## 🎨 **Best Practices**

### **✅ Do's**:

1. **Always Use Pydantic Models**: Ensures type safety and validation
2. **Comprehensive Descriptions**: Help the AI understand when to use your tool
3. **Structured Error Handling**: Return consistent error responses
4. **Include Metadata**: Provide context like execution time, version, etc.
5. **Use Path Objects**: For file operations, use `pathlib.Path`
6. **Validate Inputs**: Check file existence, URL validity, etc.
7. **Async Functions**: Use `async def` for all tool functions

### **❌ Don'ts**:

1. **Don't Return Raw Exceptions**: Always catch and structure errors
2. **Don't Use Hardcoded Paths**: Use expanduser() and resolve()
3. **Don't Skip Validation**: Trust but verify all inputs
4. **Don't Forget Timeouts**: Always set reasonable timeouts
5. **Don't Return Inconsistent Types**: Use the same output model structure

## 🧪 **Testing Your Tools**

### **Test Tool Individually**:

```python
# Test in the MCP client
async def test_my_tool():
    client = await create_mcp_client()

    result = await client.call_tool("my_custom_tool", {
        "required_param": "test_value",
        "optional_param": "optional_test",
        "number_param": 42
    })

    print(f"Tool result: {result}")
    client.disconnect()

# Run test
asyncio.run(test_my_tool())
```

### **Test via API**:

```bash
curl -X POST http://localhost:5001/chat/simple \
  -H "Content-Type: application/json" \
  -d '{"message": "Use my_custom_tool with required_param as test", "use_tools": true}'
```

## 📁 **File Organization**

### **For Complex Tools**:

```
mcp-server/
├── server.py                 # Main server file
├── tools/
│   ├── __init__.py
│   ├── filesystem_tools.py   # File system operations
│   ├── obsidian_tools.py     # Obsidian integration
│   ├── api_tools.py          # API integrations
│   └── custom_tools.py       # Your custom tools
└── models/
    ├── __init__.py
    ├── filesystem_models.py  # Pydantic models for filesystem
    ├── obsidian_models.py    # Pydantic models for Obsidian
    └── api_models.py         # Pydantic models for APIs
```

### **Import in server.py**:

```python
from tools.obsidian_tools import *
from tools.custom_tools import *
from models.obsidian_models import *
```

## 🚀 **Deployment & Updates**

### **Adding Tools (Hot Reload)**:

1. **Add your tool** to `mcp-server/server.py`
2. **Restart MCP API server**:
   `pkill -f mcp_api_server.py && python mcp_api_server.py`
3. **Test immediately**: Tools are available instantly

### **Tool Versioning**:

```python
class ToolOutput(BaseModel):
    success: bool = Field(..., description="Success status")
    version: str = Field("1.0.0", description="Tool version")
    # ... other fields
```

## 🔮 **Advanced Patterns**

### **Tool Chaining**:

```python
@mcp.tool()
async def complex_workflow(input: WorkflowInput) -> WorkflowOutput:
    """Chain multiple operations together"""

    # Step 1: Read file
    file_result = await call_internal_tool("read_file", {"file_path": input.source})

    # Step 2: Process content
    processed = process_content(file_result.content)

    # Step 3: Write result
    write_result = await call_internal_tool("write_file", {
        "file_path": input.target,
        "content": processed
    })

    return WorkflowOutput(
        success=True,
        steps_completed=3,
        final_result=write_result
    )
```

### **Configuration Management**:

```python
class ToolConfig(BaseModel):
    max_file_size: int = 10_000_000  # 10MB
    allowed_extensions: List[str] = [".txt", ".md", ".json"]
    timeout_seconds: int = 30

# Load from environment or config file
config = ToolConfig()

@mcp.tool()
async def configured_tool(input: ToolInput) -> ToolOutput:
    if input.file_size > config.max_file_size:
        raise ValueError(f"File too large: {input.file_size} > {config.max_file_size}")
    # ... rest of tool
```

## 🎯 **Ready for Obsidian Integration!**

With this foundation, you're ready to create powerful Obsidian vault tools:

- **Note Management**: Create, read, update, delete notes
- **Tag Operations**: Add, remove, search by tags
- **Link Analysis**: Find broken links, create link maps
- **Template System**: Apply templates to new notes
- **Search & Filter**: Complex queries across your vault
- **Metadata Extraction**: Parse frontmatter and properties

**Next Steps**:

1. Create `obsidian_tools.py` with note management functions
2. Define Obsidian-specific Pydantic models
3. Add vault discovery and configuration
4. Test with your actual Obsidian vault
5. Integrate with the AI for intelligent note operations

**Your MCP tool creation system is ready! 🚀**
