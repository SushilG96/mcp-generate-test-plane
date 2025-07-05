#!/usr/bin/env python3
"""
Simple Test Generator Client (Direct API)
"""
import asyncio
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Import the server components directly
from server import TestGenerator


class SimpleTestGeneratorClient:
    """Simple client that uses direct function calls"""
    
    def __init__(self):
        self.generator = TestGenerator()
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        return [
            {
                "name": "read_test_cases",
                "description": "Read test cases from CSV file"
            },
            {
                "name": "generate_test_file", 
                "description": "Generate pytest test file from test cases"
            },
            {
                "name": "generate_config_files",
                "description": "Generate pytest configuration files"
            }
        ]
    
    async def read_test_cases(self, csv_path: str, component: str = None) -> str:
        """Read test cases from CSV"""
        test_cases = self.generator.read_csv(csv_path)
        
        if component:
            test_cases = [tc for tc in test_cases if tc.component_name.lower() == component.lower()]
        
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
            "test_cases": [
                {
                    "test_case_id": tc.test_case_id,
                    "title": tc.title,
                    "category": tc.category,
                    "priority": tc.priority,
                    "api_method": tc.api_method,
                    "api_path": tc.api_path
                } for tc in test_cases[:5]
            ]
        }
        
        return f"✅ Loaded {len(test_cases)} test cases from CSV\n\n" + \
               f"📊 Components found: {', '.join(components.keys())}\n\n" + \
               f"📋 Sample test cases:\n{json.dumps(result, indent=2)}"
    
    async def generate_test_file(self, csv_path: str, component: str, 
                               output_path: str, use_ai: bool = False) -> str:
        """Generate test file"""
        # Read test cases
        all_test_cases = self.generator.read_csv(csv_path)
        test_cases = [tc for tc in all_test_cases if tc.component_name.lower() == component.lower()]
        
        if not test_cases:
            return f"❌ No test cases found for component: {component}"
        
        # Generate test file
        test_content = self.generator.generate_test_file(test_cases, component, use_ai)
        
        # Write to file
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        ai_status = "✅ AI-Enhanced" if use_ai and self.generator.ai_client else "📝 Rule-Based"
        
        return f"🎉 Generated test file successfully!\n\n" + \
               f"📂 Output: {output_path}\n" + \
               f"🧪 Tests: {len(test_cases)} for {component}\n" + \
               f"🤖 Intelligence: {ai_status}\n\n" + \
               f"🚀 Ready to run:\n" + \
               f"  cd {output_dir}\n" + \
               f"  pytest {Path(output_path).name} -v"
    
    async def generate_config_files(self, output_dir: str) -> str:
        """Generate configuration files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate pytest.ini
        pytest_ini = output_path / "pytest.ini"
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
        requirements = output_path / "requirements.txt"
        with open(requirements, 'w') as f:
            f.write('''pytest>=7.0.0
requests>=2.28.0
pytest-html>=3.1.0
''')
        
        return f"✅ Generated configuration files in {output_dir}\n\n" + \
               f"📄 Files created:\n" + \
               f"  - pytest.ini\n" + \
               f"  - requirements.txt"
    
    async def close(self) -> None:
        """Close the client (no-op for direct client)"""
        pass


async def demo():
    """Run the demo"""
    client = SimpleTestGeneratorClient()
    
    try:
        print("🚀 Simple Test Generator Demo")
        print("=" * 50)
        
        # List available tools
        print("\n🔧 Available tools:")
        tools = await client.list_tools()
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool['name']}: {tool['description']}")
        
        # Demo 1: Read test cases
        print("\n" + "=" * 50)
        print("📊 DEMO 1: Reading test cases from CSV")
        print("=" * 50)
        
        try:
            result = await client.read_test_cases("../output/test_cases.csv", "config")
            print(result)
        except Exception as e:
            print(f"❌ Failed to read test cases: {e}")
        
        # Demo 2: Generate test file
        print("\n" + "=" * 50)
        print("🏗️  DEMO 2: Generating test file")
        print("=" * 50)
        
        try:
            result = await client.generate_test_file(
                "../output/test_cases.csv", 
                "config", 
                "generated_tests/test_config.py",
                False  # Start with rule-based for reliability
            )
            print(result)
        except Exception as e:
            print(f"❌ Failed to generate test file: {e}")
        
        # Demo 3: Generate config files
        print("\n" + "=" * 50)
        print("📁 DEMO 3: Generating config files")
        print("=" * 50)
        
        try:
            result = await client.generate_config_files("generated_tests")
            print(result)
        except Exception as e:
            print(f"❌ Failed to generate config files: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("=" * 50)
        
        print("\n🚀 Next steps:")
        print("  1. Check the generated files in generated_tests/")
        print("  2. Run: cd generated_tests && pytest test_config.py -v")
        print("  3. Test a specific category: pytest -m security")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


async def interactive_mode():
    """Interactive mode for the client"""
    client = SimpleTestGeneratorClient()
    
    try:
        print("🚀 Simple Test Generator Client")
        print("=" * 50)
        
        # List available tools
        print("\n🔧 Available tools:")
        tools = await client.list_tools()
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool['name']}: {tool['description']}")
        
        while True:
            print("\n" + "=" * 50)
            print("Commands:")
            print("  1. Read test cases from CSV")
            print("  2. Generate test file")
            print("  3. Generate config files")
            print("  4. Quick demo")
            print("  5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                csv_path = input("Enter CSV file path (default: ../output/test_cases.csv): ").strip()
                if not csv_path:
                    csv_path = "../output/test_cases.csv"
                
                component = input("Filter by component (optional): ").strip()
                if not component:
                    component = None
                
                print("\n📊 Reading test cases...")
                result = await client.read_test_cases(csv_path, component)
                print(result)
            
            elif choice == "2":
                csv_path = input("Enter CSV file path (default: ../output/test_cases.csv): ").strip()
                if not csv_path:
                    csv_path = "../output/test_cases.csv"
                
                component = input("Enter component name (e.g., config): ").strip()
                if not component:
                    print("❌ Component name is required")
                    continue
                
                output_path = input(f"Enter output path (default: generated_tests/test_{component}.py): ").strip()
                if not output_path:
                    output_path = f"generated_tests/test_{component}.py"
                
                use_ai = input("Use AI enhancement? (y/n, default: n): ").strip().lower() == 'y'
                
                print(f"\n🏗️  Generating test file for {component}...")
                result = await client.generate_test_file(csv_path, component, output_path, use_ai)
                print(result)
            
            elif choice == "3":
                output_dir = input("Enter output directory (default: generated_tests): ").strip()
                if not output_dir:
                    output_dir = "generated_tests"
                
                print(f"\n📁 Generating config files in {output_dir}...")
                result = await client.generate_config_files(output_dir)
                print(result)
            
            elif choice == "4":
                print("\n🎯 Quick Demo: Generating config tests...")
                
                # Read test cases
                print("📊 Reading test cases...")
                result = await client.read_test_cases("../output/test_cases.csv", "config")
                print(result)
                
                # Generate test file
                print("\n🏗️  Generating test file...")
                result = await client.generate_test_file(
                    "../output/test_cases.csv", 
                    "config", 
                    "generated_tests/test_config.py",
                    False
                )
                print(result)
                
                # Generate config files
                print("\n📁 Generating config files...")
                result = await client.generate_config_files("generated_tests")
                print(result)
                
                print("\n✅ Demo completed!")
            
            elif choice == "5":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Simple Test Generator Client")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demo')
    
    args = parser.parse_args()
    
    if args.command == 'demo':
        asyncio.run(demo())
    elif args.command == 'interactive' or not args.command:
        asyncio.run(interactive_mode())
    else:
        print(f"❌ Unknown command: {args.command}")


if __name__ == "__main__":
    main() 