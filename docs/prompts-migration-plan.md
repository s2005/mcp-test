# Prompts Migration Plan: From Source Code to JSON Configuration

**Date**: May 27, 2025  
**Project**: MCP Test Server  
**Goal**: Migrate all prompts from hardcoded Python functions to JSON-based configuration system

## Executive Summary

This plan outlines the migration of all MCP prompts from source code to JSON files, enabling:

- **Data-driven configuration**: Prompts become editable configuration rather than code
- **User customization**: Non-programmers can modify prompts without code changes
- **Extensibility**: Easy addition of new content types and prompt categories
- **Validation**: JSON schema ensures data integrity and provides better error messages
- **Backward compatibility**: Existing tips functionality preserved during transition

## Current State Analysis

### Existing Prompt Structure

- **5 prompt functions** across 3 Python files:
  - `development_prompts.py`: `code_review_prompt`, `mcp_development_prompt`
  - `learning_prompts.py`: `learning_plan_prompt`, `debugging_assistant_prompt`
  - `planning_prompts.py`: `project_planning_prompt`

### Current JSON Structure

- **File**: `tests/data/tips_categories.json`
- **Content**: Only tips data (mcp, python, docker categories)
- **Limitation**: No support for other content types

### Current Registration System

- **Static registration**: Hardcoded function calls in `src/server.py`
- **FastMCP decorators**: `@mcp.prompt()` decorators on functions
- **Parameter handling**: Function arguments with defaults

## Migration Plan

### Phase 1: JSON Schema Design and Creation

**Goal**: Design robust data structure with validation

#### 1.1 Create JSON Schema

**File**: `src/data/content_schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MCP Content Configuration",
  "description": "Schema for MCP server content including tips and prompts",
  "type": "object",
  "properties": {
    "tips": {
      "type": "object",
      "description": "Learning tips organized by category",
      "patternProperties": {
        "^[a-zA-Z_][a-zA-Z0-9_]*$": {
          "type": "array",
          "items": {
            "type": "string",
            "minLength": 1
          }
        }
      }
    },
    "prompts": {
      "type": "object",
      "description": "Prompt templates organized by category",
      "patternProperties": {
        "^[a-zA-Z_][a-zA-Z0-9_]*$": {
          "type": "object",
          "patternProperties": {
            "^[a-zA-Z_][a-zA-Z0-9_]*$": {
              "$ref": "#/definitions/prompt"
            }
          }
        }
      }
    }
  },
  "definitions": {
    "prompt": {
      "type": "object",
      "required": ["name", "description", "template"],
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$",
          "description": "Unique identifier for the prompt"
        },
        "description": {
          "type": "string",
          "minLength": 1,
          "description": "Human-readable description of the prompt's purpose"
        },
        "arguments": {
          "type": "array",
          "description": "List of parameters the prompt accepts",
          "items": {
            "$ref": "#/definitions/argument"
          }
        },
        "template": {
          "type": "string",
          "minLength": 1,
          "description": "Template string with {parameter} placeholders"
        },
        "role": {
          "type": "string",
          "enum": ["user", "assistant", "system"],
          "default": "user",
          "description": "Message role for the prompt"
        }
      }
    },
    "argument": {
      "type": "object",
      "required": ["name", "description"],
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$",
          "description": "Parameter name"
        },
        "description": {
          "type": "string",
          "minLength": 1,
          "description": "Parameter description"
        },
        "required": {
          "type": "boolean",
          "default": false,
          "description": "Whether this parameter is required"
        },
        "default": {
          "type": ["string", "number", "boolean", "null"],
          "description": "Default value if parameter not provided"
        },
        "type": {
          "type": "string",
          "enum": ["string", "number", "boolean"],
          "default": "string",
          "description": "Expected parameter type"
        }
      }
    }
  }
}
```

#### 1.2 Design New JSON Structure

**Target Structure**:

```json
{
  "tips": {
    "mcp": ["tip1", "tip2", ...],
    "python": ["tip1", "tip2", ...],
    "docker": ["tip1", "tip2", ...]
  },
  "prompts": {
    "development": {
      "code_review_prompt": {
        "name": "code_review_prompt",
        "description": "Generate structured code review requests",
        "arguments": [
          {
            "name": "language",
            "description": "Programming language for review",
            "required": false,
            "default": "python",
            "type": "string"
          },
          {
            "name": "code_type",
            "description": "Type of code to review",
            "required": false,
            "default": "function",
            "type": "string"
          }
        ],
        "template": "Please review this {language} {code_type} and provide detailed feedback on:\n\n1. Code quality and best practices\n2. Performance considerations\n3. Security implications\n4. Readability and maintainability\n5. Potential bugs or edge cases\n6. Suggestions for improvement\n\nFocus on {language}-specific conventions and provide actionable recommendations.\n\nCode to review:\n[PASTE YOUR {language.upper()} {code_type.upper()} HERE]",
        "role": "user"
      }
    },
    "learning": {
      "learning_plan_prompt": {...},
      "debugging_assistant_prompt": {...}
    },
    "planning": {
      "project_planning_prompt": {...}
    }
  }
}
```

### Phase 2: Infrastructure Development

**Goal**: Build loading and validation infrastructure

#### 2.1 Update Utilities (`src/utils.py`)

- Rename `load_tips_from_json()` to `load_content_from_json()`
- Add JSON schema validation
- Support backward compatibility
- Add dependency: `jsonschema`

#### 2.2 Create Prompt Loading System

**New Files**:

- `src/prompts/prompt_loader.py` - JSON-based prompt loader
- `src/prompts/prompt_registry.py` - Dynamic prompt registration
- `src/prompts/validator.py` - Schema validation utilities

#### 2.3 Add Validation Dependencies

**Update**: `pyproject.toml`

```toml
dependencies = [
    # ...existing dependencies...
    "jsonschema>=4.17.0",
]
```

### Phase 3: Create JSON Data Files

**Goal**: Convert existing prompts to JSON format

#### 3.1 Create Main Content File

**File**: `src/data/content.json`

- Migrate all 5 existing prompts
- Include existing tips data
- Validate against schema

#### 3.2 Create Example/Test Files

**Files**:

- `tests/data/content_example.json` - Complete example
- `tests/data/prompts_only.json` - Prompts-only example
- Update `tests/data/tips_categories.json` for backward compatibility

### Phase 4: Dynamic Registration System

**Goal**: Replace static registration with dynamic system

#### 4.1 Create Prompt Loader (`src/prompts/prompt_loader.py`)

```python
class JSONPromptLoader:
    def __init__(self, content_data: dict, validator: ContentValidator):
        self.content_data = content_data
        self.validator = validator
    
    def load_prompts(self) -> Dict[str, PromptDefinition]:
        """Load all prompts from JSON data"""
        
    def create_prompt_function(self, prompt_def: dict):
        """Create MCP prompt function from JSON definition"""
        
    def validate_prompt_arguments(self, prompt_def: dict, args: dict):
        """Validate arguments against prompt definition"""
```

#### 4.2 Create Registration System (`src/prompts/prompt_registry.py`)

```python
class PromptRegistry:
    def register_prompts_from_json(self, mcp, content_data: dict):
        """Register all prompts from JSON with MCP server"""
        
    def register_prompt_category(self, mcp, category: str, prompts: dict):
        """Register prompts from a specific category"""
```

#### 4.3 Update Server Registration (`src/server.py`)

- Replace individual prompt registration calls
- Add JSON-based registration
- Maintain backward compatibility option

### Phase 5: Testing and Validation

**Goal**: Ensure all functionality works with JSON-based system

#### 5.1 Update Existing Tests

**Modify**: `tests/test_prompts.py`

- Test JSON-loaded prompts
- Validate prompt argument handling
- Test schema validation errors

#### 5.2 Create New Test Files

**New Files**:

- `tests/test_prompt_loader.py` - Test JSON loading system
- `tests/test_content_validation.py` - Test schema validation

#### 5.3 Integration Testing

- Test with MCP Inspector
- Validate Claude Desktop integration
- Performance testing with large prompt files

### Phase 6: Documentation

**Goal**: Update documentation

#### 6.1 Update Documentation

**Files to update**:

- `README.md` - New JSON configuration section
- Add `docs/prompt-configuration.md` - Detailed configuration guide

### Phase 7: Cleanup

**Goal**: Ensure smooth transition and future maintenance

#### 7.2 Optional Cleanup

- Remove deprecated prompt files
- Simplify server.py registration
- Remove unused imports

## Implementation Benefits

### Immediate Benefits

✅ **User Customization**: Non-technical users can modify prompts  
✅ **Data Integrity**: Schema validation prevents configuration errors  
✅ **Better Error Messages**: Clear feedback on JSON structure issues  
✅ **IDE Support**: Auto-completion and validation in editors  
✅ **Version Control**: Easy to track prompt changes in git  

### Long-term Benefits

✅ **Extensibility**: Easy to add new content types (resources, etc.)  
✅ **Maintainability**: Prompts can be maintained separately from code  
✅ **Sharing**: Prompt configurations can be shared between projects  
✅ **Internationalization**: Future support for multiple languages  
✅ **A/B Testing**: Easy to test different prompt variations  

## Risk Mitigation

### Technical Risks

- **Schema Validation Overhead**: Minimal performance impact, validate once on load
- **JSON Parsing Errors**: Comprehensive error handling and validation
- **Backward Compatibility**: No need to maintain old approach, new approach should be supported only

### User Experience Risks

- **Configuration Complexity**: Provide clear examples and documentation
- **Learning Curve**: Comprehensive documentation and examples

## Success Criteria

### Functional Requirements

- [ ] All existing prompts work identically with JSON system
- [ ] Schema validation prevents invalid configurations
- [ ] Backward compatibility no need to be maintained
- [ ] All existing tests pass

### Quality Requirements

- [ ] Unit tests cover all new functionality
- [ ] Clear error messages for invalid JSON
- [ ] Complete documentation with examples
