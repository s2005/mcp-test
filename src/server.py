from mcp.server.fastmcp import FastMCP
import datetime
import random
from typing import Dict, List, Optional, Any

# Create an MCP server
mcp = FastMCP("LinkedIn Demo")

# Category-specific tips - single source of truth
TIPS_BY_CATEGORY = {
    "mcp": [
        "Start with simple tools and gradually add complexity",
        "Use the MCP Inspector to test your servers during development",
        "Read the official MCP documentation at modelcontextprotocol.io",
        "Join the MCP community discussions on GitHub",
        "Practice with both Python and TypeScript implementations",
        "Test your MCP servers with Claude Desktop for real-world usage",
        "Use proper error handling in your tool functions",
        "Document your tools clearly with descriptive docstrings",
        "Consider security when exposing system resources",
        "Start with local development before deploying to production"
    ],
    "python": [
        "Use virtual environments to isolate project dependencies",
        "Follow PEP 8 style guidelines for consistent code formatting",
        "Write comprehensive docstrings for all functions and classes",
        "Use type hints to improve code readability and catch errors",
        "Implement proper exception handling with try-except blocks",
        "Use list comprehensions for concise and readable code",
        "Learn and use Python's built-in modules like itertools and collections",
        "Write unit tests using pytest or unittest framework",
        "Use logging instead of print statements for debugging",
        "Follow the DRY (Don't Repeat Yourself) principle"
    ],
    "docker": [
        "Use multi-stage builds to reduce final image size",
        "Always specify exact versions in your Dockerfile",
        "Use .dockerignore to exclude unnecessary files",
        "Run containers as non-root users for security",
        "Use health checks to monitor container status",
        "Leverage Docker layer caching for faster builds",
        "Keep your base images updated and secure",
        "Use docker-compose for multi-container applications",
        "Store secrets securely using Docker secrets or environment variables",
        "Monitor container resource usage and set appropriate limits"
    ]
}

@mcp.tool()
def get_current_time() -> str:
    """
    Get the current date and time.
    
    Returns:
        Current date and time as a formatted string
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def generate_greeting(name: str = "User") -> str:
    """
    Generate a personalized greeting message.
    
    Args:
        name: The name of the person to greet (default: "User")
    
    Returns:
        A personalized greeting message
    """
    greetings = [
        f"Hello {name}! Welcome to the LinkedIn Demo MCP server!",
        f"Hi there, {name}! Great to see you using MCP!",
        f"Greetings {name}! Hope you're having a fantastic day!",
        f"Hey {name}! Ready to explore Model Context Protocol?"
    ]
    return random.choice(greetings)

@mcp.tool()
def calculate_days_until_date(target_date: str) -> Dict[str, Any]:
    """
    Calculate the number of days between today and a target date.
    
    Args:
        target_date: Target date in YYYY-MM-DD format
    
    Returns:
        Dictionary with calculation results and information
    """
    try:
        target = datetime.datetime.strptime(target_date, "%Y-%m-%d")
        today = datetime.datetime.now()
        difference = target - today
        days = difference.days
        
        if days > 0:
            message = f"{days} days until {target_date}"
        elif days < 0:
            message = f"{target_date} was {abs(days)} days ago"
        else:
            message = f"{target_date} is today!"
        
        return {
            "target_date": target_date,
            "current_date": today.strftime("%Y-%m-%d"),
            "days_difference": days,
            "message": message,
            "is_future": days > 0,
            "is_past": days < 0,
            "is_today": days == 0
        }
    except ValueError:
        return {
            "error": "Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-12-25)"
        }

@mcp.resource("tips://mcp")
def get_learning_tips_resource() -> str:
    """
    Get a list of learning tips for MCP development.
    
    Returns:
        Learning tips formatted as a string
    """
    # Use MCP tips from TIPS_BY_CATEGORY as default
    tips = TIPS_BY_CATEGORY["mcp"]
    
    # Format as a readable string resource
    formatted_tips = "MCP Development Learning Tips:\n\n"
    for i, tip in enumerate(tips, 1):
        formatted_tips += f"{i}. {tip}\n"
    
    return formatted_tips

@mcp.tool()
def get_learning_tips(category: Optional[str] = None) -> List[str]:
    """
    Get a list of learning tips for development.
    
    Args:
        category: Optional category to filter tips (mcp, python, docker). 
                 If not provided, returns MCP tips.
    
    Returns:
        List of helpful tips for learning
    """
    if category is None:
        # Default behavior - return MCP tips from TIPS_BY_CATEGORY
        return TIPS_BY_CATEGORY["mcp"].copy()
    
    # Convert category to lowercase for case-insensitive matching
    category_lower = category.lower()
    
    # Check if category exists
    if category_lower not in TIPS_BY_CATEGORY:
        available_categories = list(TIPS_BY_CATEGORY.keys())
        return [f"Error: Category '{category}' not found. Available categories: {', '.join(available_categories)}"]
    
    # Return tips for the specified category
    return TIPS_BY_CATEGORY[category_lower].copy()

# Dynamic resource by category
@mcp.resource("tips://category/{category}")
def get_tips_by_category(category: str) -> str:
    """
    Get learning tips for a specific category.
    
    Args:
        category: The category of tips to retrieve (mcp, python, docker)
    
    Returns:
        Formatted learning tips for the specified category
    """
    # Convert category to lowercase for case-insensitive matching
    category_lower = category.lower()
    
    # Check if category exists
    if category_lower not in TIPS_BY_CATEGORY:
        available_categories = ", ".join(TIPS_BY_CATEGORY.keys())
        return f"Category '{category}' not found.\n\nAvailable categories: {available_categories}"
    
    # Get tips for the specified category
    tips = TIPS_BY_CATEGORY[category_lower]
    
    # Format as a readable string resource
    formatted_tips = f"{category.upper()} Learning Tips:\n\n"
    for i, tip in enumerate(tips, 1):
        formatted_tips += f"{i}. {tip}\n"
    
    # Add footer with available categories
    formatted_tips += f"\nOther available categories: {', '.join([cat for cat in TIPS_BY_CATEGORY.keys() if cat != category_lower])}"
    
    return formatted_tips

# Prompt implementations using FastMCP
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
def learning_plan_prompt(topic: str, skill_level: str = "beginner", timeframe: str = "1 month") -> List[Dict[str, str]]:
    """
    Generate a personalized learning plan prompt template.
    
    Args:
        topic: The subject or technology to learn
        skill_level: Current skill level (beginner, intermediate, advanced)
        timeframe: Available time for learning (e.g., "1 month", "3 months", "6 months")
    
    Returns:
        List of message dictionaries for the learning plan prompt
    """
    return [
        {
            "role": "user", 
            "content": f"""Create a comprehensive {timeframe} learning plan for {topic} suitable for a {skill_level} level learner.

Please include:

1. **Learning Objectives**: Clear, measurable goals
2. **Prerequisites**: What should be known before starting
3. **Weekly Breakdown**: Detailed week-by-week plan
4. **Resources**: Books, courses, tutorials, and practice projects
5. **Hands-on Projects**: Practical exercises to reinforce learning
6. **Milestones**: Checkpoints to track progress
7. **Assessment**: How to evaluate understanding
8. **Next Steps**: What to learn after completing this plan

Make the plan practical and actionable with specific recommendations for someone at the {skill_level} level."""
        }
    ]

@mcp.prompt()
def debugging_assistant_prompt(language: str = "python", error_type: str = "runtime") -> List[Dict[str, str]]:
    """
    Generate a prompt template for debugging assistance.
    
    Args:
        language: Programming language of the code with issues
        error_type: Type of error (runtime, syntax, logic, performance)
    
    Returns:
        List of message dictionaries for the debugging prompt
    """
    debugging_steps = {
        "runtime": "stack trace analysis, variable inspection, and runtime state examination",
        "syntax": "code parsing, syntax validation, and formatting issues",
        "logic": "algorithm review, test case analysis, and expected vs actual behavior",
        "performance": "profiling, bottleneck identification, and optimization opportunities"
    }
    
    steps = debugging_steps.get(error_type, "general debugging methodology")
    
    return [
        {
            "role": "user",
            "content": f"""Help me debug this {language} code that has a {error_type} error.

Please provide a systematic debugging approach focusing on {steps}.

**Error Information:**
[DESCRIBE THE ERROR OR UNEXPECTED BEHAVIOR]

**Code:**
[PASTE THE PROBLEMATIC {language.upper()} CODE HERE]

**Expected Behavior:**
[DESCRIBE WHAT SHOULD HAPPEN]

**Actual Behavior:**
[DESCRIBE WHAT ACTUALLY HAPPENS]

**Environment Details:**
- Language: {language}
- Error Type: {error_type}
- [ADD ANY RELEVANT ENVIRONMENT INFO]

Please provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Specific fix recommendations
4. Prevention strategies for similar issues
5. Testing suggestions to verify the fix"""
        }
    ]

@mcp.prompt()
def project_planning_prompt(project_type: str, team_size: str = "1-3", timeline: str = "1-3 months") -> List[Dict[str, str]]:
    """
    Generate a project planning and architecture prompt template.
    
    Args:
        project_type: Type of project (web app, API, mobile app, data pipeline, etc.)
        team_size: Size of the development team
        timeline: Expected project timeline
    
    Returns:
        List of message dictionaries for the project planning prompt
    """
    return [
        {
            "role": "user",
            "content": f"""Help me plan and architect a {project_type} project for a team of {team_size} people with a {timeline} timeline.

**Project Requirements:**
[DESCRIBE YOUR PROJECT REQUIREMENTS AND GOALS]

**Technical Constraints:**
[LIST ANY TECHNICAL CONSTRAINTS, PREFERRED TECHNOLOGIES, ETC.]

**Target Audience:**
[DESCRIBE WHO WILL USE THIS PROJECT]

Please provide a comprehensive project plan including:

1. **Architecture Design**
   - System architecture overview
   - Technology stack recommendations
   - Database design considerations
   - API design (if applicable)

2. **Development Plan**
   - Project phases and milestones
   - Task breakdown and estimation
   - Team role assignments
   - Development workflow and branching strategy

3. **Technical Specifications**
   - Infrastructure requirements
   - Security considerations
   - Performance requirements
   - Scalability planning

4. **Project Management**
   - Timeline with realistic deadlines
   - Risk assessment and mitigation
   - Testing strategy
   - Deployment plan

5. **Best Practices**
   - Code quality standards
   - Documentation requirements
   - Monitoring and maintenance plan

Tailor the recommendations for a {team_size} person team working over {timeline}."""
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

if __name__ == "__main__":
    # mcp.run(protocol="stdio", port=8000, debug=True)
    mcp.run()
