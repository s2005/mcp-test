from typing import List, Dict

def register_learning_prompts(mcp):
    """Register learning-related prompts with the MCP server."""
    
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
