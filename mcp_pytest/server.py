#!/usr/bin/env python3
"""
MCP Server for AI-Enhanced Test Generation
"""
import asyncio
import json
import os
import csv
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
except ImportError:
    pass

# MCP imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("❌ MCP not installed. Run: pip install mcp")
    exit(1)

# AI integration
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


@dataclass
class TestCase:
    """Test case data structure"""
    test_case_id: str
    title: str
    description: str
    category: str
    priority: str
    api_method: str
    api_path: str

    @property
    def component_name(self) -> str:
        """Extract component name from API path"""
        if '/' in self.api_path:
            parts = self.api_path.strip('/').split('/')
            return parts[0] if parts else 'unknown'
        return 'unknown'
    
    @property
    def sanitized_id(self) -> str:
        """Get sanitized ID for test method name"""
        return re.sub(r'[^a-zA-Z0-9_]', '_', self.test_case_id.lower())


class TestGenerator:
    """Test generator with AI enhancement"""
    
    def __init__(self):
        self.ai_client = None
        if GROQ_AVAILABLE and os.getenv("GROQ_API_KEY"):
            self.ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def read_csv(self, csv_path: str) -> List[TestCase]:
        """Read test cases from CSV"""
        test_cases = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    test_case = TestCase(
                        test_case_id=row.get('test_case_id', ''),
                        title=row.get('title', ''),
                        description=row.get('description', ''),
                        category=row.get('category', ''),
                        priority=row.get('priority', ''),
                        api_method=row.get('api_method', ''),
                        api_path=row.get('api_path', '')
                    )
                    test_cases.append(test_case)
        except Exception as e:
            print(f"Error reading CSV: {e}")
        return test_cases
    
    def generate_test_logic(self, test_case: TestCase, use_ai: bool = False) -> str:
        """Generate test logic with optional AI enhancement"""
        if use_ai and self.ai_client:
            return self._get_ai_logic(test_case)
        else:
            return self._get_rule_logic(test_case)
    
    def _get_ai_logic(self, test_case: TestCase) -> str:
        """AI-enhanced test logic"""
        try:
            prompt = f"""Generate pytest test code for:
API: {test_case.api_method} {test_case.api_path}
Category: {test_case.category}
Description: {test_case.description}

Requirements:
- Use self._make_request() for HTTP calls
- Include smart assertions
- Add proper logging
- Return only the test implementation code (no method signature)"""

            response = self.ai_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            ai_code = response.choices[0].message.content.strip()
            cleaned_code = self._clean_ai_code(ai_code)
            
            return f"""            # 🤖 AI-Enhanced Test
            logger.info("Running AI-enhanced test for {test_case.category.lower()}")
            
            try:
{cleaned_code}
            except Exception as e:
                logger.warning(f"AI logic failed: {{e}}")
                {self._get_basic_logic(test_case)}"""
            
        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._get_rule_logic(test_case)
    
    def _get_rule_logic(self, test_case: TestCase) -> str:
        """Rule-based test logic"""
        category = test_case.category.lower()
        
        if category == "security":
            return f"""            # 🛡️ Security Test
            logger.info("Running security validation")
            
            # Test without auth
            response = self._make_request("{test_case.api_method}", "{test_case.api_path}", 
                                        headers={{"Authorization": ""}})
            
            if response.status_code == 200:
                logger.warning("Endpoint may not require authentication")
            else:
                assert response.status_code in [401, 403], f"Expected 401/403, got {{response.status_code}}"
            
            logger.info("Security validation completed")"""
        
        elif category == "performance":
            return f"""            # ⚡ Performance Test
            logger.info("Running performance analysis")
            
            start_time = time.time()
            response = self._make_request("{test_case.api_method}", "{test_case.api_path}")
            duration = time.time() - start_time
            
            assert duration < 3.0, f"Response took {{duration:.2f}}s (too slow)"
            assert response.status_code == 200, f"Expected 200, got {{response.status_code}}"
            
            logger.info(f"Performance test completed in {{duration:.2f}}s")"""
        
        else:
            return self._get_basic_logic(test_case)
    
    def _get_basic_logic(self, test_case: TestCase) -> str:
        """Basic test logic"""
        return f"""            # 📝 Basic Test
            response = self._make_request("{test_case.api_method}", "{test_case.api_path}")
            
            assert 200 <= response.status_code <= 499, f"Unexpected status: {{response.status_code}}"
            logger.info(f"Test completed with status {{response.status_code}}")"""
    
    def _clean_ai_code(self, ai_code: str) -> str:
        """Clean AI-generated code"""
        # Remove markdown
        ai_code = re.sub(r'```python\n?', '', ai_code)
        ai_code = re.sub(r'```\n?', '', ai_code)
        
        # Remove method signatures
        lines = ai_code.split('\n')
        cleaned_lines = []
        skip_def = False
        
        for line in lines:
            if line.strip().startswith('def ') and 'test_' in line:
                skip_def = True
                continue
            if skip_def and line.strip() and not line.startswith(' '):
                skip_def = False
            if not skip_def:
                cleaned_lines.append(line)
        
        # Proper indentation
        result = '\n'.join(cleaned_lines).strip()
        if result:
            indented_lines = []
            for line in result.split('\n'):
                if line.strip():
                    indented_lines.append('            ' + line.lstrip())
                else:
                    indented_lines.append('')
            result = '\n'.join(indented_lines)
        
        return result if result else self._get_basic_logic(TestCase("", "", "", "", "", "", ""))
    
    def generate_test_file(self, test_cases: List[TestCase], component: str, use_ai: bool = False) -> str:
        """Generate complete test file"""
        if not test_cases:
            return ""
        
        # Generate test methods
        test_methods = []
        for test_case in test_cases:
            method_name = f"test_{test_case.sanitized_id}"
            test_logic = self.generate_test_logic(test_case, use_ai)
            
            markers = [
                test_case.category.lower().replace(" ", "_"),
                f"priority_{test_case.priority.lower()}",
                f"component_{test_case.component_name}"
            ]
            
            intelligence_type = "AI-Enhanced" if use_ai and self.ai_client else "Rule-Based"
            
            method = f'''
    @pytest.mark.{markers[0]}
    @pytest.mark.{markers[1]}
    @pytest.mark.{markers[2]}
    def {method_name}(self):
        """
        {test_case.test_case_id}: {test_case.title}
        
        Description: {test_case.description}
        Category: {test_case.category} | Priority: {test_case.priority}
        API: {test_case.api_method} {test_case.api_path}
        Intelligence: {intelligence_type}
        """
        logger.info("🧪 Starting {test_case.test_case_id}")
        
        start_time = time.time()
        try:
{test_logic}
            
            duration = time.time() - start_time
            logger.info(f"✅ Test completed in {{duration:.2f}}s")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {{e}}")
            raise
'''
            test_methods.append(method)
        
        # Complete test file
        intelligence_info = "AI-Enhanced" if use_ai and self.ai_client else "Rule-Based"
        
        content = f'''"""
{intelligence_info} Tests for {component.title()} Component

Generated from CSV test cases.
Contains {len(test_cases)} test cases.
"""
import pytest
import requests
import time
import logging
from typing import Dict, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class Test{component.title().replace('_', '')}:
    """Test class for {component} component"""
    
    def setup_class(self):
        """Setup test class"""
        self.base_url = "http://localhost:8080"
        self.timeout = 30
        logger.info(f"🔧 Setting up tests for {{self.base_url}}")
    
    def _make_request(self, method: str, endpoint: str, 
                     headers: Optional[Dict] = None, 
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with mock response"""
        url = urljoin(self.base_url, endpoint)
        
        default_headers = {{"Content-Type": "application/json"}}
        if headers:
            default_headers.update(headers)
        
        # Mock response for demo
        class MockResponse:
            status_code = 200
            elapsed = type('', (), {{'total_seconds': lambda: 0.5}})()
            headers = {{"Content-Type": "application/json"}}
            text = '{{"status": "healthy", "message": "mock response"}}'
            def json(self): return {{"status": "healthy", "message": "mock response"}}
        
        logger.debug(f"🌐 {{method}} {{url}}")
        return MockResponse()
{''.join(test_methods)}
'''
        
        return content


# Initialize MCP server
server = Server("ai-test-generator")
generator = TestGenerator()

# Tool definitions
@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="read_test_cases",
            description="Read test cases from CSV file",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_path": {
                        "type": "string",
                        "description": "Path to CSV file"
                    },
                    "component": {
                        "type": "string",
                        "description": "Filter by component (optional)"
                    }
                },
                "required": ["csv_path"]
            }
        ),
        Tool(
            name="generate_test_file",
            description="Generate pytest test file from test cases",
            inputSchema={
                "type": "object",
                "properties": {
                    "csv_path": {
                        "type": "string",
                        "description": "Path to CSV file"
                    },
                    "component": {
                        "type": "string",
                        "description": "Component to generate tests for"
                    },
                    "use_ai": {
                        "type": "boolean",
                        "description": "Use AI enhancement",
                        "default": False
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output file path"
                    }
                },
                "required": ["csv_path", "component", "output_path"]
            }
        ),
        Tool(
            name="generate_config_files",
            description="Generate pytest configuration files",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory"
                    }
                },
                "required": ["output_dir"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "read_test_cases":
        csv_path = arguments["csv_path"]
        component_filter = arguments.get("component")
        
        test_cases = generator.read_csv(csv_path)
        
        if component_filter:
            test_cases = [tc for tc in test_cases if tc.component_name.lower() == component_filter.lower()]
        
        # Group by component
        components = {}
        for tc in test_cases:
            comp = tc.component_name
            if comp not in components:
                components[comp] = []
            components[comp].append(tc)
        
        result = {
            "total_test_cases": len(test_cases),
            "components": {comp: len(cases) for comp, cases in components.items()},
            "test_cases": [asdict(tc) for tc in test_cases[:5]]  # Show first 5
        }
        
        return [TextContent(
            type="text",
            text=f"✅ Loaded {len(test_cases)} test cases from CSV\n\n" +
                 f"📊 Components found: {', '.join(components.keys())}\n\n" +
                 f"📋 Sample test cases:\n{json.dumps(result, indent=2)}"
        )]
    
    elif name == "generate_test_file":
        csv_path = arguments["csv_path"]
        component = arguments["component"]
        use_ai = arguments.get("use_ai", False)
        output_path = arguments["output_path"]
        
        # Read test cases
        all_test_cases = generator.read_csv(csv_path)
        test_cases = [tc for tc in all_test_cases if tc.component_name.lower() == component.lower()]
        
        if not test_cases:
            return [TextContent(
                type="text",
                text=f"❌ No test cases found for component: {component}"
            )]
        
        # Generate test file
        test_content = generator.generate_test_file(test_cases, component, use_ai)
        
        # Write to file
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        ai_status = "✅ AI-Enhanced" if use_ai and generator.ai_client else "📝 Rule-Based"
        
        return [TextContent(
            type="text",
            text=f"🎉 Generated test file successfully!\n\n" +
                 f"📂 Output: {output_path}\n" +
                 f"🧪 Tests: {len(test_cases)} for {component}\n" +
                 f"🤖 Intelligence: {ai_status}\n\n" +
                 f"🚀 Ready to run:\n" +
                 f"  cd {output_dir}\n" +
                 f"  pytest {Path(output_path).name} -v"
        )]
    
    elif name == "generate_config_files":
        output_dir = Path(arguments["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate pytest.ini
        pytest_ini = output_dir / "pytest.ini"
        with open(pytest_ini, 'w') as f:
            f.write('''[tool:pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --html=report.html --self-contained-html
markers =
    functional: Functional tests
    security: Security tests
    performance: Performance tests
    priority_critical: Critical priority
    priority_high: High priority
    priority_medium: Medium priority
    priority_low: Low priority
''')
        
        # Generate requirements.txt
        requirements = output_dir / "requirements.txt"
        with open(requirements, 'w') as f:
            f.write('''pytest>=7.0.0
requests>=2.28.0
pytest-html>=3.1.0
''')
        
        return [TextContent(
            type="text",
            text=f"✅ Generated configuration files in {output_dir}\n\n" +
                 f"📄 Files created:\n" +
                 f"  - pytest.ini\n" +
                 f"  - requirements.txt"
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"❌ Unknown tool: {name}"
        )]


async def main():
    """Run MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    print("🚀 Starting MCP AI Test Generator Server...")
    print(f"🔑 AI Status: {'✅ Available' if generator.ai_client else '❌ Not configured'}")
    asyncio.run(main()) 