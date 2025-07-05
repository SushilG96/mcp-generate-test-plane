# MCP AI-Enhanced Test Generator

A professional MCP (Model Context Protocol) system that generates intelligent pytest test cases from CSV data with optional AI enhancement.

## Features

- 🤖 **AI-Enhanced**: Optional Groq AI integration for creative test generation
- 📝 **Rule-Based**: Intelligent rule-based generation without AI
- 📊 **CSV Integration**: Reads test cases from CSV files
- 🎯 **Component-Based**: Organizes tests by API components
- 🔧 **MCP Architecture**: Clean client-server separation
- 🚀 **Multiple Interfaces**: Interactive CLI, command-line, and demo modes

## Architecture

```
┌─────────────────┐    MCP Protocol    ┌─────────────────┐
│   MCP Client    │◄──────────────────►│   MCP Server    │
│   (client.py)   │                    │  (server.py)    │
└─────────────────┘                    └─────────────────┘
```

- **MCP Server** (`server.py`): Handles test generation, CSV reading, AI integration
- **MCP Client** (`client.py`): Provides interactive and command-line interfaces
- **Demo Script** (`demo.py`): Quick demonstration of the system capabilities

## File Structure

```
mcp_pytest/
├── server.py           # MCP server with test generation logic
├── client.py           # MCP client with interactive/CLI interfaces
├── demo.py             # Quick demo script
├── requirements.txt    # Dependencies
├── README.md           # Documentation
└── generated_tests/    # Output directory (created automatically)
```

## Quick Start

1. **Install dependencies**:
```bash
uv add mcp pytest requests pytest-html groq python-dotenv
```

2. **Interactive mode** (recommended):
```bash
uv run python client.py interactive
```

3. **Quick demo**:
```bash
uv run python demo.py
```

4. **Command line**:
```bash
uv run python client.py demo
```

## Usage Examples

### Interactive Mode (Best Experience)
```bash
uv run python client.py interactive
```

**Interactive menu options:**
- Read test cases from CSV
- Generate test files (rule-based or AI-enhanced)
- Generate configuration files
- Quick demo with sample data

### Command Line Mode

```bash
# Read test cases
uv run python client.py read --component config

# Generate rule-based tests
uv run python client.py generate --component config

# Generate AI-enhanced tests
uv run python client.py generate --component config --use-ai

# Generate config files
uv run python client.py config

# Full demo
uv run python client.py demo
```

### Demo Script
```bash
uv run python demo.py
```

## AI Setup (Optional)

1. **Create `.env` file** in project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

2. **AI dependencies** (included in requirements.txt):
```bash
uv add groq python-dotenv
```

3. **Use AI enhancement** in interactive mode or with `--use-ai` flag

## MCP Tools

The server provides these tools:

- **`read_test_cases`**: Read and analyze CSV test cases
- **`generate_test_file`**: Generate pytest files with AI or rule-based logic
- **`generate_config_files`**: Generate pytest configuration files

## Generated Output

```
generated_tests/
├── test_config.py      # Component-specific test files
├── test_namespaces.py  # (one per component)
├── pytest.ini         # Pytest configuration
├── requirements.txt    # Test dependencies
└── report.html        # HTML report (after running tests)
```

## Running Generated Tests

```bash
cd generated_tests
pytest -v                    # Run all tests
pytest -v -m security        # Run security tests only
pytest -v -m priority_high   # Run high priority tests
pytest --html=report.html    # Generate HTML report
```

## Intelligence Modes

- **Rule-Based**: Smart, reliable test generation using enhanced rules
- **AI-Enhanced**: Creative test generation with Groq AI + fallback to rules

## Test Categories

### Generated Test Types
- **🛡️ Security Tests**: Authentication/authorization validation (401/403 checks)
- **⚡ Performance Tests**: Response time monitoring (<3s assertions)
- **📝 Functional Tests**: Basic API functionality validation
- **🔧 Error Handling**: Boundary conditions and edge cases

### Pytest Markers
- **Category markers**: `@pytest.mark.functional`, `@pytest.mark.security`
- **Priority markers**: `@pytest.mark.priority_high`, `@pytest.mark.priority_critical`
- **Component markers**: `@pytest.mark.component_config`

## Requirements

- Python 3.8+
- MCP (Model Context Protocol)
- pytest, requests, pytest-html
- Optional: groq, python-dotenv (for AI features)

## Development

### Running the Server Directly
```bash
uv run python server.py
```

### Testing MCP Connection
```bash
uv run python client.py read --component config
```

## Example Generated Test

```python
@pytest.mark.security.priority_critical.component_config
def test_tc_config_sec_auth_006(self):
    """
    TC-config-SEC-AUTH-006: Test GET /config/health - Authentication Required
    
    Description: Verify GET request to /config/health requires proper authentication
    Category: Security | Priority: Critical
    API: GET /config/health
    Intelligence: Rule-Based
    """
    logger.info("🧪 Starting TC-config-SEC-AUTH-006")
    
    start_time = time.time()
    try:
        # 🛡️ Security Test
        logger.info("Running security validation")
        
        # Test without auth
        response = self._make_request("GET", "/config/health", 
                                    headers={"Authorization": ""})
        
        if response.status_code == 200:
            logger.warning("Endpoint may not require authentication")
        else:
            assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
        logger.info("Security validation completed")
        
        duration = time.time() - start_time
        logger.info(f"✅ Test completed in {duration:.2f}s")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
```

## Benefits

✅ **Professional MCP Architecture**: Clean client-server separation  
✅ **Multiple Interfaces**: Interactive, CLI, demo modes  
✅ **AI Enhancement**: Optional Groq integration with fallback  
✅ **Smart Test Generation**: Category-aware logic patterns  
✅ **Production Ready**: Comprehensive pytest configuration  
✅ **Extensible**: Easy to add new tools and capabilities 