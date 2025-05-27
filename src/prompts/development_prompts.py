from typing import List, Dict

def register_development_prompts(mcp):
    """Register development-related prompts with the MCP server."""
    
    @mcp.prompt()
    def code_review_prompt(language: str = "python", code_type: str = "function") -> List[Dict[str, str]]:
        """
        Generate a prompt template for code review assistance.
        
        Args:
            language: Programming language for the code review (default: python)
            code_type: Type of code to review (function, class, module, etc.)
        
        Returns:
            List of message dictionaries for the prompt template
        """
        return [
            {
                "role": "user",
                "content": f"""Please review this {language} {code_type} and provide detailed feedback on:

1. Code quality and best practices
2. Performance considerations
3. Security implications
4. Readability and maintainability
5. Potential bugs or edge cases
6. Suggestions for improvement

Focus on {language}-specific conventions and provide actionable recommendations.

Code to review:
[PASTE YOUR {language.upper()} {code_type.upper()} HERE]"""
            }
        ]

    @mcp.prompt()
    def mcp_development_prompt(component_type: str = "tool", complexity: str = "intermediate") -> List[Dict[str, str]]:
        """
        Generate a prompt template for MCP (Model Context Protocol) development assistance.
        
        Args:
            component_type: Type of MCP component to develop (tool, resource, prompt, server)
            complexity: Complexity level (beginner, intermediate, advanced)
        
        Returns:
            List of message dictionaries for the MCP development prompt
        """
        component_guidance = {
            "tool": "functions that can be called by the LLM to perform actions",
            "resource": "static or dynamic content that can be accessed by the LLM", 
            "prompt": "template messages that help structure LLM interactions",
            "server": "complete MCP server with multiple tools, resources, and prompts"
        }
        
        guidance = component_guidance.get(component_type, "MCP components")
        
        return [
            {
                "role": "user",
                "content": f"""Help me develop an MCP (Model Context Protocol) {component_type} at {complexity} level.

**What I want to build:**
[DESCRIBE YOUR MCP {component_type.upper()} REQUIREMENTS]

**Use Case:**
[EXPLAIN HOW THIS WILL BE USED WITH LLMs]

**Technical Requirements:**
[LIST ANY SPECIFIC TECHNICAL NEEDS OR CONSTRAINTS]

Please provide guidance on building {guidance} including:

1. **Implementation Approach**
   - FastMCP decorator usage (@mcp.{component_type}())
   - Function signature and parameters
   - Return type and format specifications
   - Error handling best practices

2. **MCP Protocol Compliance**
   - Required fields and data structures
   - Message formatting standards
   - Type hints and validation
   - Documentation requirements

3. **Code Example**
   - Complete working implementation
   - Proper docstring documentation
   - Input validation and error handling
   - Integration with existing MCP server

4. **Testing Strategy**
   - Unit test examples
   - MCP Inspector testing workflow
   - Client-side integration testing
   - Error scenario testing

5. **Best Practices**
   - Security considerations
   - Performance optimization
   - Debugging and troubleshooting
   - Production deployment tips

Focus on {complexity}-level patterns and include practical examples suitable for someone building MCP {component_type}s."""
            }
        ]
