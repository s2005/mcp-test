from typing import List, Dict

def register_planning_prompts(mcp):
    """Register planning-related prompts with the MCP server."""
    
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
