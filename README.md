# Test Plan & Test Case Generator MCP

A comprehensive testing solution powered by MCP (Model Context Protocol) that generates detailed test plans and Excel-formatted test cases for API testing.

## 🚀 Overview

This project provides two powerful MCP servers that work together to create a complete testing pipeline:

1. **Test Plan Generator** - Creates comprehensive test plans from OpenAPI specifications and other input files
2. **Test Case Generator** - Generates detailed, executable test cases in Excel format directly from OpenAPI specifications

## 📋 Features

### Test Plan Generator
- ✅ Generates enterprise-grade test plans from OpenAPI specifications
- ✅ Supports multiple input formats (JSON, YAML, text files)
- ✅ Risk-based testing approach with comprehensive coverage analysis
- ✅ Includes security, performance, and functional testing strategies
- ✅ Follows industry best practices and modern testing methodologies

### Test Case Generator
- ✅ Creates structured test cases directly from OpenAPI specifications
- ✅ Generates Excel-formatted test cases with multiple organized sheets
- ✅ Includes detailed test steps, expected results, and test data
- ✅ Covers functional, security, performance, and error handling testing
- ✅ Provides test execution tracking capabilities
- ✅ Ready for import into test management tools and automation frameworks

## 🏗️ Architecture

```
Input Files → Test Plan Generator → Test Plan → Test Case Generator → Executable Test Cases
     ↓                ↓                 ↓              ↓                    ↓
OpenAPI.json    Comprehensive     test_plan.md    Structured         test_cases.json
URLs.txt        Analysis &                        Test Cases         Ready for Automation
Other Files     Strategy
```

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mcp-generate-test-plane
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or using uv
   uv sync
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```

## 🚀 Quick Start

### Option 1: Complete Pipeline (Recommended)
Run both servers in sequence with the orchestrator:

```bash
python run_complete_testing_pipeline.py
```

This will:
1. Generate a comprehensive test plan from your input files
2. Create detailed test cases from the test plan
3. Validate the test cases
4. Show summary statistics and next steps

### Option 2: Individual Servers

#### Generate Test Plan Only
```bash
uv run python client/client.py
```

#### Generate Test Cases (Excel format)
  ```bash
  python client/test_case_client.py
  ```

#### Generate Test Cases with Configuration Management
  ```bash
  python client/config_test_case_client.py
  ```

## 📁 Project Structure

```
mcp-generate-test-plane/
├── server/
│   ├── test_plan_generator.py      # Test plan generation MCP server
│   ├── test_case_generator.py      # Test case generation MCP server
│   ├── preprocess.py               # Input file preprocessing
│   ├── validation.py               # Test plan validation
│   └── url_fetcher.py             # URL content fetching
  ├── client/
  │   ├── client.py                   # Test plan generator client
  │   ├── test_case_client.py         # Test case generator client (Excel format)
  │   └── config_test_case_client.py  # Configuration-based test case client
├── config/
│   └── test_config.json           # Test case generation configuration
├── input/
│   ├── openapi.json               # OpenAPI specification
│   └── urls.txt                   # Additional URLs to analyze
├── output/
│   ├── test_plan.md               # Generated test plan
│   └── test_cases.xlsx            # Generated test cases (Excel format)
├── docs/                          # Documentation and diagrams
├── run_complete_testing_pipeline.py  # Complete pipeline orchestrator
└── requirements.txt
```

## 📋 Input Files

Place your input files in the `input/` directory:

- **openapi.json** - OpenAPI 3.0 specification of your API
- **urls.txt** - Additional URLs to analyze (optional)
- **Any other documentation files** (PDF, TXT, MD)

## 📊 Output Files

The generators create structured output files:

### Test Plan (`output/test_plan.md`)
- Executive summary and strategic overview
- Comprehensive test strategy and methodology
- Risk assessment and mitigation strategies
- Test coverage analysis
- Performance and security testing plans
- Automation framework recommendations

### Test Cases (`output/test_cases.xlsx`) - Excel Format

The Excel format provides a structured, tabular view with multiple sheets:

#### Sheet 1: Test Cases
| Column | Description |
|--------|-------------|
| test_case_id | Unique identifier (e.g., TC-API-FUNC-001) |
| test_suite | Test suite grouping |
| title | Descriptive test case title |
| description | What the test validates |
| category | Functional, Security, Performance, Error Handling |
| priority | Critical, High, Medium, Low |
| api_method | GET, POST, PUT, DELETE, etc. |
| api_path | API endpoint path |
| test_steps | Detailed execution steps |
| expected_results | Expected outcomes |
| test_data | Required test data |
| automation_candidate | Yes/No for automation feasibility |

#### Sheet 2: Test Execution
- Test execution tracking
- Status, results, and notes
- Bug references and execution history

#### Sheet 3: Metadata
- Generation statistics
- API information
- Coverage metrics

#### Sheet 4: API Endpoints
- Complete API endpoint summary
- Parameters and response codes
- Test case counts per endpoint

## 🔧 MCP Server Tools

### Test Plan Generator Tools
- `generate_test_plan(input_dir)` - Generate comprehensive test plan from input directory

### Test Case Generator Tools
- `generate_test_cases(input_dir)` - Generate comprehensive Excel test cases directly from OpenAPI specification
- `show_test_config()` - Display current test configuration and available profiles
- `switch_test_profile(profile_name)` - Switch to a different test profile

## 🎯 Configuration-Based Test Generation

The test case generator now supports **configuration-based test generation** through the `config/test_config.json` file. This allows you to easily customize what types of test cases are generated without modifying code.

### 📋 Configuration File Structure

The `config/test_config.json` file contains:

```json
{
  "enabled_test_types": {
    "functional": {
      "enabled": true,
      "description": "Basic functional testing with valid inputs",
      "priority": "Essential",
      "tests": ["FUNC-HAPPY"]
    },
    "security": {
      "enabled": true,
      "description": "Security testing including authentication, authorization, and encryption",
      "priority": "Critical",
      "tests": ["SEC-AUTH", "SEC-AUTHZ", "SEC-CONTENT", "SEC-ENCRYPTION"]
    },
    "error_handling": {
      "enabled": true,
      "description": "Error response and invalid input handling", 
      "priority": "High",
      "tests": ["ERR-NOTFOUND", "ERR-INVALID"]
    }
    // ... more test types
  },
  "predefined_profiles": {
    "quick": {
      "description": "Quick smoke tests for CI/CD",
      "enabled_types": ["functional", "security"]
    },
    "comprehensive": {
      "description": "Full test coverage",
      "enabled_types": ["functional", "security", "error_handling", "edge_cases", "performance", "reliability", "scalability", "compatibility"]
    }
    // ... more profiles
  },
  "current_profile": "quick"
}
```

### 🔧 Available Test Types

| Test Type | Description | Tests per Endpoint | Priority |
|-----------|-------------|-------------------|----------|
| **functional** | Comprehensive functional testing (positive, negative, validation, workflow, boundary) | 5 | Essential |
| **security** | Authentication, authorization, encryption | 4 | Critical |
| **error_handling** | Error responses and invalid input handling | 2 | High |
| **edge_cases** | Boundary values and edge case scenarios | 1 | Medium |
| **performance** | Load, stress, and spike testing | 3 | Medium |
| **reliability** | Timeout handling and retry mechanisms | 2 | Medium |
| **scalability** | Concurrent users and scaling behavior | 1 | Low |
| **compatibility** | API version compatibility testing | 1 | Low |
| **workflow_integration** | Intelligent workflow testing based on test plan analysis and API relationships | 4 | High |

#### 🎯 Enhanced Functional Testing Coverage

The **functional** test type now provides comprehensive coverage with 5 distinct test scenarios:

| Functional Test | Focus Area | What It Tests |
|----------------|------------|---------------|
| **FUNC-HAPPY** | Positive Cases | Happy path with valid data, successful workflows |
| **FUNC-NEGATIVE** | Negative Cases | Missing parameters, wrong data types, invalid scenarios |
| **FUNC-VALIDATION** | Input Validation | Field length, format validation, special characters |
| **FUNC-WORKFLOW** | Business Logic | Workflow state transitions, business rules, audit trails |
| **FUNC-BOUNDARY** | Boundary Conditions | Min/max values, edge cases, null handling |

This ensures **complete functional coverage** including both positive and negative test scenarios, making functional testing much more robust than the previous single happy-path test.

### 📚 Predefined Profiles

| Profile | Description | Test Types | Use Case |
|---------|-------------|------------|----------|
| **quick** | Quick smoke tests for CI/CD (9 tests/endpoint) | functional, security | Fast pipeline validation |
| **development** | Basic development testing (7 tests/endpoint) | functional, error_handling | Dev environment testing |
| **security_audit** | Security-focused testing (12 tests/endpoint) | functional, security, error_handling, edge_cases | Security assessments |
| **performance_testing** | Performance and reliability focus (11 tests/endpoint) | functional, performance, reliability, scalability | Load testing scenarios |
| **comprehensive** | Complete test coverage (19 tests/endpoint) | All 8 categories | Full testing cycles |

### 🎮 Using Configuration Profiles

#### Method 1: Interactive Configuration Client
```bash
python client/config_test_case_client.py
```

This client provides an interactive interface to:
- View current configuration
- Switch between profiles
- Generate test cases with selected profile

#### Method 2: Direct Configuration Management

**Show current configuration:**
```python
# Using MCP tools directly
result = await session.call_tool("show_test_config", {})
```

**Switch profiles:**
```python
# Switch to performance testing profile
result = await session.call_tool("switch_test_profile", {"profile_name": "performance_testing"})
```

#### Method 3: Manual Configuration Editing

Edit `config/test_config.json` directly:

```json
{
  // To enable/disable individual test types
  "enabled_test_types": {
    "functional": {"enabled": true},
    "security": {"enabled": false},  // Disable security tests
    "performance": {"enabled": true}
  },
  
  // Or use predefined profiles
  "current_profile": "security_audit"
}
```

### 💡 Configuration Examples

**Quick CI/CD Testing (9 tests per endpoint):**
```bash
python client/config_test_case_client.py
# Select "quick" profile  
# Generates: 5 functional + 4 security tests
```

**Full Security Audit (12 tests per endpoint):**
```json
"current_profile": "security_audit"
```

**Performance Testing Focus (11 tests per endpoint):**
```json
"current_profile": "performance_testing"
```

**Custom Configuration:**
```json
{
  "current_profile": null,  // Use individual settings
  "enabled_test_types": {
    "functional": {"enabled": true},
    "error_handling": {"enabled": true},
    "performance": {"enabled": true}
    // Only these 3 types will be generated
  }
}
```

### 🔄 Dynamic Profile Switching

Switch profiles programmatically or interactively:

```python
# Switch to comprehensive testing
await session.call_tool("switch_test_profile", {"profile_name": "comprehensive"})

# Generate test cases with new profile
result = await session.call_tool("generate_test_cases", {"input_dir": "input"})
```

The configuration system provides flexibility to generate exactly the test types you need for different scenarios, from quick smoke tests to comprehensive testing suites.

## 🚀 Integration with Testing Frameworks

The generated test cases can be integrated with popular testing frameworks:

### Excel Integration
```bash
# Open Excel file directly
open output/test_cases.xlsx

# Use Excel for test case management
# - Review and edit test cases in Excel
# - Track test execution in the "Test Execution" sheet
# - Export specific sheets as CSV for tool integration
```

### Postman
```bash
# Import test_cases.json as a Postman collection
# Or convert Excel data to Postman format
# Use the structured test data from Excel sheets
```

### REST Assured (Java)
```java
// Convert Excel test cases to REST Assured test classes
// Read Excel data using Apache POI or similar
// Generate @Test methods from Excel rows
```

### pytest (Python)
```python
# Generate pytest test functions from Excel data
# Use pandas to read Excel test cases
# Create parameterized tests from Excel data
```

### Test Management Tools
```bash
# Import Excel test cases into:
# - TestRail, Zephyr, qTest
# - Azure DevOps Test Plans
# - Jira with Xray plugin
```

## 🔍 Test Case Structure

Each generated test case includes:

- **Identification**: Unique ID, title, description
- **Classification**: Category, priority, test level, risk level
- **API Details**: Method, path, operation ID
- **Execution**: Detailed test steps with expected results
- **Data**: Valid inputs, invalid inputs, edge cases
- **Context**: Preconditions, post-conditions, dependencies
- **Automation**: Automation feasibility and tags

## 🛡️ Security Testing

The generators include comprehensive security testing:

- **OWASP Top 10** vulnerability testing
- **Authentication & Authorization** testing
- **Input validation** and injection attack testing
- **Session management** testing
- **API security** best practices

## ⚡ Performance Testing

Generated test cases include:

- **Load testing** scenarios
- **Stress testing** beyond normal limits
- **Spike testing** for sudden traffic increases
- **Response time** validation
- **Throughput** testing

## 🔧 Customization

### Custom Prompts
Modify the prompts in the server files to customize the generated content:
- `server/test_plan_generator.py` - Line ~50
- `server/test_case_generator.py` - Line ~90

### Custom Validation
Add custom validation rules in `server/validation.py`

### Custom Preprocessing
Extend file processing capabilities in `server/preprocess.py`

## 🚀 Advanced Usage

### Custom Input Processing
```python
# Add support for new file formats
def process_custom_format(file_path):
    # Your custom processing logic
    return processed_content
```

### Environment-Specific Test Cases
```bash
# Generate test cases for specific environments
python client/test_case_client.py --environment staging
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Generate Test Plan
  run: python run_complete_testing_pipeline.py
  
- name: Upload Test Cases
  uses: actions/upload-artifact@v3
  with:
    name: test-cases
    path: output/test_cases.json
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please:
1. Check the [documentation](docs/)
2. Review existing [issues](../../issues)
3. Create a new issue with detailed information

## 🔮 Roadmap

- [ ] Support for GraphQL API specifications
- [ ] Integration with more testing frameworks
- [ ] Real-time test execution monitoring
- [ ] AI-powered test case optimization
- [ ] Multi-language test case generation
- [ ] Visual test case designer

---

**Happy Testing! 🧪✨**
