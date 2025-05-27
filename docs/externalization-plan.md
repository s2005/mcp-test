# MCP Test Server Content Externalization Plan

**Date**: May 27, 2025  
**Objective**: Remove remaining hardcoded content and move to external JSON configuration files

## Executive Summary

This plan outlines the strategy to identify and extract all remaining hardcoded content from the MCP Test Server source code and move it to external JSON configuration files. The goal is to create a clean, maintainable system where all content is externalized without duplicate code or complex fallback mechanisms.

## Current State Analysis

### ✅ Already Externalized (Completed)

- **Prompts**: Fully migrated to `src/data/content.json` with JSON schema validation
- **Tips Data**: Already supports external JSON loading via `TIPS_JSON_PATH`

### 🔍 Hardcoded Content Identified

#### 1. Greeting Messages (`src/tools/greeting_tools.py`)

**Hardcoded Content**:

```python
greetings = [
    f"Hello {name}! Welcome to the MCP test server!",
    f"Hi there, {name}! Great to see you using MCP!",
    f"Greetings {name}! Hope you're having a fantastic day!",
    f"Hey {name}! Ready to explore Model Context Protocol?"
]
```

#### 2. Default Tips Data (`src/utils.py`)

**Hardcoded Content**:

```python
default_tips = {
    "mcp-test": [
        "Configure this server by adding it to your MCP client configuration file",
        "Set the TIPS_JSON_PATH environment variable to load custom tips from a JSON file",
        "Use 'uv run src/server.py' to start the server in development mode",
        "Test the server tools using get_current_time, generate_greeting, and get_tips functions",
        "The server provides tips categorized by technology - add more categories as needed",
        "Extend functionality by adding new @mcp.tool() decorated functions to the server"
    ]
}
```

#### 3. Special Processing Logic (`src/prompts/prompt_loader.py`)

**Hardcoded Content**:

```python
# Complex special processing methods that add dynamic content
def _process_mcp_development_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
    component_guidance = {
        "tool": "functions that can be called by the LLM to perform actions",
        "resource": "static or dynamic content that can be accessed by the LLM", 
        "prompt": "template messages that help structure LLM interactions",
        "server": "complete MCP server with multiple tools, resources, and prompts"
    }
    args["component_guidance"] = component_guidance.get(component_type, "MCP components")
    return args

def _process_debugging_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
    debugging_steps = {
        "runtime": "stack trace analysis, variable inspection, and runtime state examination",
        "syntax": "code parsing, syntax validation, and formatting issues",
        "logic": "algorithm review, test case analysis, and expected vs actual behavior",
        "performance": "profiling, bottleneck identification, and optimization opportunities"
    }
    args["debugging_steps"] = debugging_steps.get(error_type, "general debugging methodology")
    return args
```

**Issue**: Complex special processing adds unnecessary complexity and hardcoded logic.

#### 4. Multiple Prompt Files

**Current Structure**:

- `src/prompts/development_prompts.py`
- `src/prompts/learning_prompts.py`
- `src/prompts/planning_prompts.py`

**Issue**: Multiple files for different prompt categories when categories should be defined in JSON.

## Proposed Solution Architecture

### 1. Simplified JSON Configuration Structure

Single comprehensive `content.json` with simplified structure:

```json
{
    "tips": {
        "mcp": ["..."],
        "python": ["..."],
        "docker": ["..."]
    },
    "messages": {
        "greetings": [
            "Hello {name}! Welcome to the MCP test server!",
            "Hi there, {name}! Great to see you using MCP!",
            "Greetings {name}! Hope you're having a fantastic day!",
            "Hey {name}! Ready to explore Model Context Protocol?"
        ]
    },
    "prompts": {
        "development": {
            "code_review_prompt": { /* existing structure */ },
            "mcp_development_prompt": { 
                /* simplified template without special processing */ 
            }
        },
        "learning": {
            "learning_plan_prompt": { /* existing structure */ },
            "debugging_assistant_prompt": { 
                /* simplified template without special processing */ 
            }
        },
        "planning": {
            "project_planning_prompt": { /* existing structure */ }
        }
    }
}
```

### 2. Simplified Component Architecture

#### A. Content Manager (`src/content/content_manager.py`)

```python
class ContentManager:
    """Centralized content management for all externalized content."""
    
    def __init__(self, content_data: dict):
        self.content_data = content_data
    
    def get_greetings(self) -> List[str]:
        return self.content_data.get("messages", {}).get("greetings", [])
    
    def get_tips(self, category: str = None) -> List[str]:
        tips = self.content_data.get("tips", {})
        if category:
            return tips.get(category, [])
        return tips.get("mcp", [])
```

#### B. Single Prompt Module (`src/prompts/prompts.py`)

Replace all category-specific prompt files with one consolidated module:

```python
def register_all_prompts(mcp, content_data):
    """Register all prompts from JSON configuration."""
    prompt_registry = PromptRegistry()
    prompt_registry.register_prompts_from_json(mcp, content_data)
```

#### C. Simplified Prompt Loader (`src/prompts/prompt_loader.py`)

Remove complex special processing:

```python
def create_prompt_function(self, prompt_name: str, prompt_def: Dict[str, Any]) -> Callable:
    """Create MCP prompt function from JSON definition - simplified processing."""
    
    def prompt_function(**kwargs) -> List[Dict[str, str]]:
        # Get argument definitions
        arg_definitions = prompt_def.get("arguments", [])
        
        # Validate and process arguments
        processed_args = self.validator.validate_arguments(arg_definitions, kwargs)
        
        # Simple template formatting without special processing
        template = prompt_def["template"]
        try:
            formatted_content = template.format(**processed_args)
        except KeyError as e:
            formatted_content = template
            print(f"Warning: Missing placeholder in template: {e}")
        
        # Return message with appropriate role
        role = prompt_def.get("role", "user")
        return [{"role": role, "content": formatted_content}]
    
    # Set function metadata
    prompt_function.__name__ = prompt_name
    prompt_function.__doc__ = prompt_def.get("description", f"Generated prompt: {prompt_name}")
    
    return prompt_function
```

#### D. Updated Tool Modules

**Modified `src/tools/greeting_tools.py`**:

```python
def register_greeting_tools(mcp, content_manager):
    
    @mcp.tool()
    def generate_greeting(name: str = "User") -> str:
        greetings = content_manager.get_greetings()
        formatted_greetings = [greeting.format(name=name) for greeting in greetings]
        return random.choice(formatted_greetings)
```

#### E. Simplified Utils (`src/utils.py`)

```python
def load_content_from_json(json_file_path: Optional[str] = None) -> dict:
    """Load complete content configuration from JSON file."""
    from prompts.prompt_loader import load_content_from_json as loader_func
    return loader_func(json_file_path)

def load_tips_from_json(json_file_path: Optional[str] = None) -> Dict[str, List[str]]:
    """Load tips from content configuration."""
    content = load_content_from_json(json_file_path)
    return content.get("tips", {})
```

### 3. Consolidated File Structure

**Remove**:

- `src/prompts/development_prompts.py`
- `src/prompts/learning_prompts.py`
- `src/prompts/planning_prompts.py`

**Add**:

- `src/content/content_manager.py`
- `src/prompts/prompts.py` (single consolidated file)

**Keep/Modify**:

- `src/prompts/prompt_loader.py` (simplified - remove special processing)
- `src/prompts/prompt_registry.py` (simplified)
- `src/prompts/validator.py` (simplified schema)
- `src/data/content.json` (enhanced)
- `src/data/content_schema.json` (updated)

## Implementation Commits (Agile Sprints)

### Commit 1: Enhanced JSON Schema Foundation

**Scope**: ~120 lines of code  
**Value**: Foundation for content externalization with validation  
**Testable**: Schema validation works for new content structure  

**Files Modified**:

```text
src/data/content_schema.json        (+60 lines)
tests/test_schema_validation.py     (+60 lines - new file)
```

**Test Criteria**:

- Schema validates existing content.json
- Schema validates new messages section
- Schema rejects invalid structures
- All existing tests continue to pass

---

### Commit 2: ContentManager Core Implementation

**Scope**: ~150 lines of code  
**Value**: Centralized content access API ready for use  
**Testable**: ContentManager can load and access all content types  

**Changes**:

- Create `src/content/content_manager.py` with simplified API
- Implement methods for greetings and tips access only
- Create comprehensive unit tests with dynamic JSON generation

**Files Created**:

```text
src/content/__init__.py              (+5 lines)
src/content/content_manager.py       (+80 lines)
tests/test_content_manager.py        (+65 lines)
```

**Test Criteria**:

- ContentManager loads content from dictionary
- All getter methods return expected data
- Dynamic JSON testing works (create temp JSON, test, cleanup)
- Handles missing sections gracefully

---

### Commit 3: Enhanced Content Data

**Scope**: ~80 lines of code  
**Value**: All hardcoded content externalized to JSON  
**Testable**: Content loads and validates against schema  

**Changes**:

- Add `messages` section with greeting templates to `content.json`
- Validate enhanced content against updated schema

**Files Modified**:

```text
src/data/content.json               (+40 lines)
tests/test_enhanced_content.py      (+40 lines - new file)
```

**Test Criteria**:

- Enhanced content.json validates against schema
- ContentManager can access all new content sections
- No regression in existing prompt/tips functionality

---

### Commit 4: Greeting Tools Externalization

**Scope**: ~100 lines of code  
**Value**: First tool converted to use external content  
**Testable**: Greeting tool uses JSON content instead of hardcoded messages  

**Changes**:

- Refactor `src/tools/greeting_tools.py` to use ContentManager
- Update server initialization to pass ContentManager to tools
- Create integration test for externalized greetings

**Files Modified**:

```text
src/tools/greeting_tools.py         (~30 lines modified)
src/server.py                       (+20 lines)
tests/test_greeting_integration.py  (+50 lines - new file)
```

**Test Criteria**:

- Greeting tool generates messages from JSON content
- Server starts successfully with ContentManager
- Integration test verifies end-to-end functionality
- MCP Inspector shows greeting tool working

---

### Commit 5: Utils Content Externalization

**Scope**: ~120 lines of code  
**Value**: Default tips and utilities use external content  
**Testable**: Utils load content from JSON, no hardcoded defaults  

**Changes**:

- Remove hardcoded default_tips from `src/utils.py`
- Update utils to use ContentManager for content access
- Ensure backward compatibility for existing TIPS_JSON_PATH usage

**Files Modified**:

```text
src/utils.py                        (~50 lines modified)
tests/test_utils_externalization.py (+70 lines - new file)
```

**Test Criteria**:

- Utils load tips from ContentManager
- No hardcoded content remains in utils
- Existing JSON file loading still works
- All tip-related functionality preserved

---

### Commit 6: Prompt Loader Simplification  

**Scope**: ~100 lines of code  
**Value**: Simplified prompt processing without complex logic  
**Testable**: Prompts generate correctly using simple template substitution  

**Changes**:

- Remove `_process_mcp_development_args()` and `_process_debugging_args()` from `prompt_loader.py`
- Simplify `create_prompt_function()` to use basic template formatting only
- Update prompt templates to include static content where needed

**Files Modified**:

```text
src/prompts/prompt_loader.py        (~60 lines removed/simplified)
tests/test_prompt_simplification.py (+40 lines - new file)
```

**Test Criteria**:

- Prompt loader uses simple template substitution
- All existing prompt functionality preserved
- No complex processing logic remains
- Dynamic testing with various prompts works

---

### Commit 7: Consolidated Prompt Architecture

**Scope**: ~200 lines of code  
**Value**: Single prompt file with category-based organization  
**Testable**: All prompts work from consolidated structure  

**Changes**:

- Create single `src/prompts/prompts.py` file
- Remove category-specific prompt files
- Update imports and registrations

**Files Created/Removed**:

```text
src/prompts/prompts.py              (+100 lines - new file)
src/prompts/development_prompts.py  (delete)
src/prompts/learning_prompts.py     (delete)  
src/prompts/planning_prompts.py     (delete)
tests/test_consolidated_prompts.py  (+100 lines - new file)
```

**Test Criteria**:

- All prompts register successfully from single file
- No functionality lost during consolidation
- MCP Inspector shows all prompt categories
- Dynamic testing with various prompt categories works

---

### Commit 8: Integration Testing & Validation

**Scope**: ~180 lines of code  
**Value**: Complete system validation with dynamic testing  
**Testable**: Full end-to-end functionality verified  

**Changes**:

- Create comprehensive integration test suite
- Test complete server functionality with custom JSON configurations
- Validate all externalized content works together

**Files Created**:

```text
tests/test_integration_complete.py  (+120 lines - new file)
tests/test_dynamic_configurations.py (+60 lines - new file)
```

**Test Criteria**:

- Server starts with completely custom content.json
- All tools, resources, and prompts use externalized content
- Dynamic JSON testing covers edge cases
- Performance meets requirements (fast startup)
- MCP Inspector validates complete functionality

---

### Commit 9: Final Cleanup & Optimization

**Scope**: ~80 lines of code  
**Value**: Clean, optimized codebase ready for production  
**Testable**: All tests pass, no unused code remains  

**Changes**:

- Remove any remaining hardcoded content
- Clean up unused imports and variables
- Final validation sweep

**Files Modified**:

```text
Multiple files                      (~80 lines cleaned up)
tests/test_final_validation.py     (+40 lines - new file)
```

**Test Criteria**:

- No hardcoded content detected in codebase
- No code with legacy or backward compatibility functionality
- All tests pass with 100% success rate
- Performance benchmarks met
- Code quality metrics satisfied

### Commit 10: Documentation & Examples

**Scope**: ~150 lines of code  
**Value**: Complete documentation for content customization  
**Testable**: Documentation examples work correctly  

**Changes**:

- Create ContentManager API documentation
- Add configuration examples
- Update README with new architecture
- Create example custom content files

**Files Created**:

```text
docs/content-manager-api.md         (+80 lines)
examples/custom-content-example.json (+40 lines)
README.md                           (~30 lines updated)
```

**Test Criteria**:

- Documentation examples validate against schema
- API documentation is complete and accurate
- Example configurations work with server
- README accurately reflects new architecture

---

## Testing Strategy

### Dynamic JSON Testing Approach

```python
# Example test pattern
def test_custom_categories():
    # Create temporary JSON with custom categories
    temp_content = {
        "tips": {"custom": ["tip1", "tip2"]},
        "messages": {"greetings": ["Hello {name}!"]},
        "prompts": {"custom_category": {"test_prompt": {...}}}
    }
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(temp_content, f)
        temp_file = f.name
    
    try:
        # Test functionality
        content_manager = ContentManager(temp_content)
        assert content_manager.get_tips("custom") == ["tip1", "tip2"]
    finally:
        # Clean up
        os.unlink(temp_file)
```

### Test Categories

1. **Content Loading**: Various JSON structures
2. **Schema Validation**: Valid and invalid configurations  
3. **ContentManager**: All public methods
4. **Integration**: Complete server functionality
5. **Error Handling**: Missing content, invalid JSON

## Benefits

### Code Quality

- **Simplification**: Single source of truth for all content
- **Maintainability**: No hardcoded values in source code
- **Consistency**: Unified content management approach
- **Reduced Complexity**: No special processing logic

### User Experience

- **Customization**: Complete control over all server content
- **Flexibility**: Easy to add new categories and content types
- **Validation**: JSON schema prevents configuration errors
- **Simplicity**: Straightforward template substitution

### Development

- **Less Code**: Consolidated prompt handling and simplified processing
- **Better Organization**: Clear separation of content and logic
- **Easier Testing**: Dynamic test configurations
- **Maintainable Templates**: Simple template format without complex logic

## File Changes Summary

### Files to Remove

```text
src/prompts/development_prompts.py
src/prompts/learning_prompts.py  
src/prompts/planning_prompts.py
```

### Files to Create

```text
src/content/content_manager.py
src/prompts/prompts.py
```

### Files to Modify

```text
src/data/content.json              # Add messages section
src/data/content_schema.json       # Update schema for messages section
src/prompts/prompt_loader.py       # Remove special processing, simplify
src/prompts/prompt_registry.py     # Simplified registration
src/tools/greeting_tools.py        # Use ContentManager
src/utils.py                       # Use externalized content
src/server.py                      # Initialize ContentManager
```

### Test Files

```text
tests/test_content_manager.py      # New comprehensive tests
tests/test_dynamic_content.py      # Dynamic JSON testing
tests/test_prompt_migration.py     # Update existing tests
```

## Success Criteria

### Functional Requirements

✅ All hardcoded content externalized to JSON  
✅ Single consolidated prompt file  
✅ JSON schema validation for all content  
✅ Dynamic testing with temporary JSON files  
✅ Simplified template processing  
✅ Complete test coverage  

### Quality Requirements

✅ No duplicate code or complex processing logic  
✅ Simplified file structure  
✅ Clear content management API  
✅ Comprehensive validation  
