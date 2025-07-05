#!/usr/bin/env python3
"""
MCP Client for AI-Enhanced Test Generation
"""
import asyncio
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

# MCP imports
try:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client
except ImportError:
    print("❌ MCP not installed. Run: pip install mcp")
    exit(1)


class TestGeneratorClient:
    """MCP client for test generation"""
    
    def __init__(self):
        self.session = None
        self.read_stream = None
        self.write_stream = None
        self.client_context = None
    
    async def connect(self) -> None:
        """Connect to MCP server"""
        import sys
        import os
        
        server_path = os.path.join(os.path.dirname(__file__), "server.py")
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_path],
            env=None
        )
        
        # Create the stdio client context
        self.client_context = stdio_client(server_params)
        self.read_stream, self.write_stream = await self.client_context.__aenter__()
        
        # Create session
        self.session = ClientSession(self.read_stream, self.write_stream)
        
        # Initialize the session with timeout
        try:
            await asyncio.wait_for(self.session.initialize(), timeout=15.0)
            print("✅ Session initialized successfully")
        except asyncio.TimeoutError:
            print("❌ Session initialization timed out")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        if not self.session:
            await self.connect()
        
        response = await self.session.list_tools()
        return [tool.dict() for tool in response.tools]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the server"""
        if not self.session:
            await self.connect()
        
        response = await self.session.call_tool(name, arguments)
        
        # Extract text content from response
        if response.content:
            return response.content[0].text
        return "No response"
    
    async def read_test_cases(self, csv_path: str, component: str = None) -> str:
        """Read test cases from CSV"""
        arguments = {"csv_path": csv_path}
        if component:
            arguments["component"] = component
        
        return await self.call_tool("read_test_cases", arguments)
    
    async def generate_test_file(self, csv_path: str, component: str, 
                               output_path: str, use_ai: bool = False) -> str:
        """Generate test file"""
        arguments = {
            "csv_path": csv_path,
            "component": component,
            "output_path": output_path,
            "use_ai": use_ai
        }
        
        return await self.call_tool("generate_test_file", arguments)
    
    async def generate_config_files(self, output_dir: str) -> str:
        """Generate configuration files"""
        arguments = {"output_dir": output_dir}
        return await self.call_tool("generate_config_files", arguments)
    
    async def close(self) -> None:
        """Close the session gracefully"""
        try:
            if self.session:
                # Don't explicitly close session, let context manager handle it
                self.session = None
            
            if self.client_context:
                await self.client_context.__aexit__(None, None, None)
                self.client_context = None
                
        except Exception as e:
            # Ignore cleanup errors
            pass
        
        self.read_stream = None
        self.write_stream = None


async def interactive_mode():
    """Interactive mode for the client"""
    client = TestGeneratorClient()
    
    try:
        print("🚀 MCP AI Test Generator Client")
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
                    True  # Use AI
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


async def command_line_mode(args):
    """Command line mode"""
    client = TestGeneratorClient()
    
    try:
        print("🚀 MCP AI Test Generator Client")
        print("=" * 50)
        
        # Connect to server
        print("📡 Connecting to MCP server...")
        await client.connect()
        print("✅ Connected to server")
        
        if args.command == "read":
            print(f"\n📊 Reading test cases from {args.csv_path}...")
            result = await client.read_test_cases(args.csv_path, args.component)
            print(result)
        
        elif args.command == "generate":
            print(f"\n🏗️  Generating test file for {args.component}...")
            result = await client.generate_test_file(
                args.csv_path, 
                args.component, 
                args.output_path, 
                args.use_ai
            )
            print(result)
        
        elif args.command == "config":
            print(f"\n📁 Generating config files in {args.output_dir}...")
            result = await client.generate_config_files(args.output_dir)
            print(result)
        
        elif args.command == "demo":
            print("\n🎯 Demo: Generating config tests...")
            
            # Read test cases
            print("📊 Reading test cases...")
            result = await client.read_test_cases("../output/test_cases.csv", "config")
            print(result)
            
            # Generate test file with AI
            print("\n🤖 Generating AI-enhanced test file...")
            result = await client.generate_test_file(
                "../output/test_cases.csv", 
                "config", 
                "generated_tests/test_config.py",
                True
            )
            print(result)
            
            # Generate config files
            print("\n📁 Generating config files...")
            result = await client.generate_config_files("generated_tests")
            print(result)
            
            print("\n✅ Demo completed!")
        
        else:
            print(f"❌ Unknown command: {args.command}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MCP AI Test Generator Client")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Read test cases from CSV')
    read_parser.add_argument('--csv-path', default='../output/test_cases.csv', help='CSV file path')
    read_parser.add_argument('--component', help='Filter by component')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate test file')
    generate_parser.add_argument('--csv-path', default='../output/test_cases.csv', help='CSV file path')
    generate_parser.add_argument('--component', required=True, help='Component name')
    generate_parser.add_argument('--output-path', help='Output file path')
    generate_parser.add_argument('--use-ai', action='store_true', help='Use AI enhancement')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Generate config files')
    config_parser.add_argument('--output-dir', default='generated_tests', help='Output directory')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demo')
    
    args = parser.parse_args()
    
    # Set default output path for generate command
    if args.command == 'generate' and not args.output_path:
        args.output_path = f"generated_tests/test_{args.component}.py"
    
    if args.command == 'interactive' or not args.command:
        asyncio.run(interactive_mode())
    else:
        asyncio.run(command_line_mode(args))


if __name__ == "__main__":
    main() 