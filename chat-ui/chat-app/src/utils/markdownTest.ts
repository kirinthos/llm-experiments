// Test markdown content for demonstrating the new rendering capabilities

export const markdownTestContent = `# Comprehensive Markdown Test

This demonstrates our new **markdown rendering capabilities** with *italic text*, \`inline code\`, and more!

## Features Implemented

### 1. Text Formatting
- **Bold text** using double asterisks
- *Italic text* using single asterisks  
- \`Inline code\` with backticks
- ~~Strikethrough~~ text (if supported)

### 2. Code Blocks with Syntax Highlighting

\`\`\`javascript
// JavaScript example with syntax highlighting
function calculateSum(a, b) {
    const result = a + b;
    console.log(\`The sum of \${a} and \${b} is \${result}\`);
    return result;
}

// Usage
const total = calculateSum(15, 27);
\`\`\`

\`\`\`python
# Python example
def greet_user(name: str) -> str:
    """Return a personalized greeting."""
    return f"Hello, {name}! Welcome to our markdown chat!"

# Usage
message = greet_user("Developer")
print(message)
\`\`\`

### 3. Tables

| Feature | Status | Description |
|---------|--------|-------------|
| **Bold Text** | ✅ Complete | Double asterisk formatting |
| *Italic Text* | ✅ Complete | Single asterisk formatting |
| \`Code Blocks\` | ✅ Complete | Syntax highlighting with copy button |
| Tables | ✅ Complete | Responsive table rendering |
| Citations | ✅ Complete | Clickable reference pills |

### 4. Lists

#### Ordered List:
1. First item with **bold text**
2. Second item with *italic text*
3. Third item with \`inline code\`

#### Unordered List:
- Bullet point one
- Bullet point two with [external link](https://github.com)
- Bullet point three

### 5. Citations and References

Modern AI systems provide accurate information with proper sourcing [1]. This enhances trust and allows users to verify claims [2]. Our implementation follows industry standards [3].

### 6. Blockquotes

> This is a blockquote demonstrating how longer quotes and important information can be highlighted in the chat interface. It supports **markdown formatting** within quotes.

### 7. Links

Visit our [GitHub repository](https://github.com) or check out the [documentation](https://example.com) for more information.

---

## References

[1] https://openai.com/research
[2] https://perplexity.ai  
[3] https://github.com/microsoft/copilot

*This test content demonstrates all major markdown features implemented in our chat UI.*`;