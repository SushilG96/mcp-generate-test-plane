#!/usr/bin/env python3
"""
MCP AI Test Generator Demo
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the client
from client import TestGeneratorClient


async def demo():
    """Run the demo"""
    client = TestGeneratorClient()
    
    try:
        print("🚀 MCP AI-Enhanced Test Generator Demo")
        print("=" * 50)
        
        # Connect to server
        print("📡 Connecting to MCP server...")
        await client.connect()
        print("✅ Connected to server")
        
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
        print("  3. Try: python client.py interactive")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n🔧 Troubleshooting:")
        print("  1. Make sure MCP is installed: pip install mcp")
        print("  2. Check if CSV file exists: ../output/test_cases.csv")
        print("  3. Try: python client.py demo")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(demo()) 