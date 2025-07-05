# MCP Test Automation Framework

An advanced **Model Context Protocol (MCP)** based test automation framework that reads test cases from CSV and dynamically generates component-based pytest frameworks for API testing.

## 🚀 Enhanced Features

### ✅ **Component-Based Organization**
- **One test file per component**: Generate `test_config_component.py`, `test_namespaces_component.py`, etc.
- **Better maintainability**: Tests grouped by functionality rather than arbitrary splits
- **Smart categorization**: Automatic component detection from API paths

### ✅ **Intelligent Test Generation with AI Enhancement**
- **Hybrid Intelligence**: Combines rule-based reliability with AI-powered innovation
- **Multiple AI Providers**: Groq, OpenAI, and Anthropic integration
- **Intelligence Levels**: Rule-based, Balanced (hybrid), and AI-first approaches
- **Smart Test Types**: Innovative, edge cases, advanced security, and intelligent performance testing
- **Category-aware implementations**: Different test logic for Functional, Security, Performance, Error Handling
- **Rich pytest markers**: Component, category, priority, and test-type markers
- **Mock response handling**: Works without live API endpoints
- **Comprehensive coverage**: Happy path, negative, boundary, and edge case testing

### ✅ **Advanced MCP Integration**
- **Enhanced MCP Server**: `mcp_pytest_server.py` with built-in utilities
- **Sophisticated Client**: `mcp_pytest_client.py` with interactive workflows
- **Component-specific operations**: Analyze, generate, and run tests per component
- **Real-time analysis**: Comprehensive CSV analysis with component breakdowns

## 📊 Current Test Coverage

- **Total Test Cases**: 828
- **Components**: 5 (config, namespaces, policies, tables, tasks)
- **Categories**: 9 (Functional, Security, Performance, Error Handling, etc.)
- **Automation Coverage**: 100%
- **Generated Files**: One comprehensive test file per component

## 🧠 AI Intelligence Levels

The system supports multiple intelligence levels for test generation:

### 1. **Rule-based** (`--intelligence-level rule_based`)
- ✅ **Reliable**: Consistent, predictable test patterns
- ✅ **Fast**: No API calls, instant generation
- ✅ **No dependencies**: Works offline
- 🎯 **Use case**: Production systems, CI/CD pipelines

### 2. **Balanced** (`--intelligence-level balanced`) 
- ✅ **Hybrid approach**: Combines AI creativity with rule-based reliability
- 🤖 **AI-enhanced**: Uses LLM for creative test scenarios
- 🛡️ **Fallback protection**: Falls back to rules if AI fails
- 🎯 **Use case**: Best of both worlds (Recommended)

### 3. **AI-first** (`--intelligence-level ai_first`)
- 🤖 **AI-powered**: Maximizes creative, intelligent test generation
- 🚀 **Innovative**: Generates unique test scenarios beyond templates
- 🛡️ **Fallback protection**: Falls back to rules if AI fails
- 🎯 **Use case**: Research, advanced testing, maximum creativity

## 🤖 AI Providers

### **Groq** (`--ai-provider groq`)
- ⚡ **Fast**: Ultra-fast inference with specialized hardware
- 🎯 **Model**: Llama3-8B-8192 (default)
- 💰 **Cost**: Very affordable
- 🔑 **Setup**: `export GROQ_API_KEY="your-key"`

### **OpenAI** (`--ai-provider openai`)
- 🧠 **Advanced**: GPT-4 for sophisticated test generation
- 🎯 **Model**: GPT-4 (default)
- 🔑 **Setup**: `export OPENAI_API_KEY="your-key"`

### **Anthropic** (`--ai-provider anthropic`)
- 🎯 **Balanced**: Claude-3 Sonnet for reliable creativity
- 🎯 **Model**: claude-3-sonnet-20240229 (default)
- 🔑 **Setup**: `export ANTHROPIC_API_KEY="your-key"`

## 🎨 Smart Test Types

The AI intelligently determines test types based on context:

- **🔒 Security Advanced**: For auth, permissions, access control
- **⚡ Performance Intelligent**: For load, stress, scalability tests
- **🎯 Edge Cases**: For boundary conditions, unusual scenarios
- **🚀 Innovative**: For creative, comprehensive testing

## 🎯 Quick Start

### Option 1: Enhanced MCP System with AI Intelligence (Recommended)

```bash
# Navigate to the MCP system directory
cd mcp_pytest/

# Set up AI API keys (optional, for intelligent generation)
export GROQ_API_KEY="your-groq-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# AI-Enhanced test generation
python client.py generate --use-ai --ai-provider groq --intelligence-level balanced
python client.py generate --use-ai --ai-provider openai --intelligence-level ai_first
python client.py generate --component config --use-ai --intelligence-level balanced

# Traditional rule-based generation (no AI required)
python client.py generate --component config --intelligence-level rule_based

# Interactive mode with AI options
python client.py interactive
```

### Option 2: Simple Direct Generation

```bash
# Navigate to the MCP system directory
cd mcp_pytest/

# Direct test generation without MCP complexity
python simple_generator.py analyze
python simple_generator.py generate
python simple_generator.py run
```

### Option 3: Complete Pipeline

  ```bash
# Navigate to the MCP system directory and run the full pipeline
cd mcp_pytest/
python client.py full-pipeline
  ```

## 📁 Project Structure

```
mcp-generate-test-plane/
├── mcp_pytest/                   # 🚀 Enhanced MCP Test Automation System
│   ├── server.py                 # Enhanced MCP server with component logic
│   ├── client.py                 # Advanced MCP client with workflows  
│   ├── simple_generator.py       # Standalone generator (no MCP dependencies)
│   ├── pipeline.py               # Pipeline automation script
│   ├── requirements.txt          # MCP system dependencies
│   ├── README.md                 # MCP system documentation
│   └── SYSTEM_SUMMARY.md         # Technical architecture details
├── 
├── input/
│   ├── openapi.json              # OpenAPI specification
│   ├── urls.txt                  # API endpoints
│   └── clo.txt                   # Command line options
├── output/
│   ├── test_cases.csv            # Generated test cases (828 cases)
│   ├── test_plan.md              # Test plan documentation
│   └── test_cases.xlsx           # Excel format test cases
├── 
├── generated_tests/              # Output from simple generator
│   ├── test_*_component.py       # Component-specific test files
│   ├── conftest.py               # Pytest configuration
│   ├── pytest.ini               # Pytest settings
│   └── requirements.txt          # Dependencies
├── 
├── component_tests/              # Output from enhanced MCP system
│   ├── test_config_component.py     # Config tests (46 cases)
│   ├── test_namespaces_component.py # Namespaces tests (161 cases)
│   ├── test_policies_component.py   # Policies tests (345 cases)
│   ├── test_tables_component.py     # Tables tests (161 cases)
│   ├── test_tasks_component.py      # Tasks tests (115 cases)
│   └── *.py, *.ini, requirements.txt
├── 
├── server/                       # Original server components
├── client/                       # Original client components
├── config/                       # Configuration files
└── docs/                         # Documentation
```

## 🔧 Available MCP Tools

### Analysis Tools
- **`analyze_test_cases`**: Comprehensive CSV analysis with component insights
- **`list_components`**: Show all available components and their details

### Generation Tools  
- **`generate_component_tests`**: Create component-based pytest framework
- **`run_component_tests`**: Execute tests with component-specific filtering

## 🎨 Component-Based Test Organization

### Traditional Approach (Old)
```
test_suite_part1.py    # 20 random tests
test_suite_part2.py    # 20 random tests  
test_suite_part3.py    # 20 random tests
```

### Enhanced Approach (New) ✅
```
test_config_component.py      # All config-related tests
test_namespaces_component.py  # All namespace-related tests
test_policies_component.py    # All policy-related tests
test_tables_component.py      # All table-related tests
test_tasks_component.py       # All task-related tests
```

## 📋 Test Categories & Implementation

| Category | Implementation | Example Tests |
|----------|---------------|---------------|
| **Functional** | Happy path validation, response structure | GET /config/health → 200 OK |
| **Security** | Authentication, authorization, data exposure | Unauthorized access → 401/403 |
| **Performance** | Response time, concurrent requests | Response < 2s, 5 concurrent calls |
| **Error Handling** | Input validation, malicious input | SQL injection → 400 Bad Request |
| **Reliability** | Retry logic, error recovery | Network failures, timeouts |
| **Scalability** | Load testing, resource limits | High volume requests |
| **Compatibility** | Version compatibility, browser support | API versioning |
| **Edge Cases** | Boundary conditions, unusual inputs | Large payloads, special characters |
| **Workflow** | Multi-step processes, integration | CRUD operations, data flow |

## 🎯 Pytest Markers Usage

```bash
# Run by component
pytest -m "component_config"
pytest -m "component_namespaces"

# Run by category  
pytest -m "functional"
pytest -m "security and priority_high"

# Run by priority
pytest -m "priority_critical"
pytest -m "priority_high or priority_critical"

# Combine markers
pytest -m "component_config and functional and priority_high"
```

## 🚀 Advanced Features

### Interactive Workflow
```python
# Start interactive mode
python mcp_pytest_client.py interactive

# Choose from:
# 1. Test all components
# 2. Test specific component  
# 3. Test by category
# 4. Custom analysis
```

### Component-Specific Analysis
```bash
# Analyze specific component
python mcp_pytest_client.py analyze --component config

# Generate for specific component
python mcp_pytest_client.py generate --component namespaces

# Run specific component tests
python mcp_pytest_client.py run --component policies --parallel
```

### Rich Reporting
- **HTML Reports**: `--html=report.html --self-contained-html`
- **Component Breakdown**: Test distribution by component
- **Category Analysis**: Test coverage by type
- **Priority Insights**: Critical vs. low priority test ratios

## 📦 Dependencies

```bash
# Core MCP dependencies
pip install mcp requests urllib3

# Testing dependencies  
pip install pytest pytest-html pytest-xdist

# Or install from requirements
pip install -r mcp_requirements.txt
```

## 🔍 Component Details

### Config Component (46 tests)
- Health checks, configuration management
- Endpoints: `/config/health`, `/config/reconfigure`
- Categories: Functional, Security, Performance, Reliability

### Namespaces Component (161 tests)  
- Namespace operations, policy management
- Endpoints: `/namespaces/{id}/policies`, `/namespaces/{id}/tables`
- Full CRUD operations with validation

### Policies Component (345 tests)
- Policy resource management, permissions
- Endpoints: `/policies/resource`, `/policies/permissions`
- Complex authorization and security testing

### Tables Component (161 tests)
- Table operations, data management  
- Endpoints: `/tables/{id}/paused`, `/tables/{id}/data`
- Performance and scalability focus

### Tasks Component (115 tests)
- Task processing, ingestion logs
- Endpoints: `/tasks/ingestlog`, `/tasks/status`
- Workflow and error handling emphasis

## 🤖 Why No LLMs for Test Generation?

### **Rule-Based vs LLM-Based Approach**

**Current Approach: Rule-Based Templates** ✅
```python
# Fast, reliable, consistent
if test_case.category == "Security":
    return generate_security_test_template(test_case)
elif test_case.category == "Performance":  
    return generate_performance_test_template(test_case)
```

**Alternative: LLM-Based Generation** 🤖
```python
# Creative, context-aware, but unpredictable
prompt = f"Generate pytest for {api_endpoint} testing {category}..."
test_code = await llm.generate(prompt)
```

### **Why Rule-Based for This System?**

| Factor | Rule-Based ✅ | LLM-Based ❓ |
|--------|---------------|--------------|
| **Consistency** | Same pattern every time | Varies per generation |
| **Speed** | Instant (no API calls) | Slower (API latency) |
| **Cost** | Free | $$ per API call |
| **Reliability** | 100% working tests | May need debugging |
| **Scale** | 828 tests in seconds | Expensive at scale |
| **Debugging** | Easy to trace templates | Hard to debug AI logic |

### **When to Use Each Approach**

**Rule-Based (Current) - Best for:**
- High-volume test generation (828+ tests)
- Production reliability requirements
- Consistent test patterns
- Cost-sensitive projects
- Predictable API testing

**LLM-Based - Best for:**
- Complex, unique test scenarios
- Creative edge case generation
- Natural language test descriptions
- One-off custom tests
- Exploratory testing

## 🎉 Benefits

✅ **Better Organization**: One test file per component
✅ **Maintainability**: Logical grouping by functionality  
✅ **Scalability**: Easy to add new components
✅ **Flexibility**: Component-specific test execution
✅ **Intelligence**: Category-aware test implementations
✅ **Reporting**: Rich insights and analytics
✅ **Integration**: Seamless MCP workflow
✅ **Cost Effective**: No LLM API costs for generation
✅ **Reliable**: Deterministic, predictable test code

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new components or enhance existing ones
4. Test with the MCP system
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Enhanced Test Automation Framework** - Powered by Model Context Protocol (MCP)
*Intelligent • Component-Based • Scalable • Maintainable*
