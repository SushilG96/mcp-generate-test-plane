#!/usr/bin/env python3

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_test_case_generator():
    """Run the Test Case Generator MCP server to generate Excel test cases."""
    
    # Configure server parameters for the test case generator
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.test_case_generator"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            print("🔧 Test Case Generator MCP Server initialized successfully!")
            print("📊 Available tools:")
            
            # List available tools
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n" + "="*60)
            print("📊 GENERATING EXCEL TEST CASES FROM OPENAPI")
            print("="*60)
            
            # Generate Excel test cases directly from OpenAPI specification
            try:
                result = await session.call_tool(
                    "generate_test_cases",
                    {
                        "input_dir": "input"
                    }
                )
                
                print("\n✅ Excel Test Case Generation Results:")
                result_data = json.loads(result.content[0].text)
                
                if result_data.get("success"):
                    print(f"   📁 Output file: {result_data.get('output_file', 'output/test_cases.xlsx')}")
                    print(f"   📋 Message: {result_data.get('message', '')}")
                    
                    # Display statistics
                    if "statistics" in result_data:
                        stats = result_data["statistics"]
                        print(f"   📊 Statistics:")
                        print(f"      - Test Suites: {stats.get('total_test_suites', 0)}")
                        print(f"      - Test Cases: {stats.get('total_test_cases', 0)}")
                        print(f"      - API Endpoints: {stats.get('api_endpoints_analyzed', 0)}")
                        print(f"      - Output Format: {stats.get('output_format', 'excel')}")
                        print(f"      - Automation Candidates: {stats.get('automation_candidates', 0)}")
                        
                        if "categories" in stats:
                            print(f"      - Categories: {', '.join(stats['categories'].keys())}")
                        
                        if "priorities" in stats:
                            print(f"      - Priorities: {', '.join(f'{k}: {v}' for k, v in stats['priorities'].items())}")
                        
                        if "sheets_created" in stats:
                            print(f"      - Excel Sheets: {', '.join(stats['sheets_created'])}")
                    
                    print("\n" + "="*60)
                    print("🎉 EXCEL TEST CASE GENERATION COMPLETE!")
                    print("="*60)
                    print("📁 Generated Excel file contains:")
                    print("   📋 Test Cases - Complete test case details")
                    print("   ✅ Test Execution - Tracking sheet for test runs")
                    print("   📊 Metadata - Generation details and statistics")
                    print("   🔗 API Endpoints - API endpoint summary")
                    
                    print("\n🔧 Next steps:")
                    print("   1. Open the Excel file in Microsoft Excel or Google Sheets")
                    print("   2. Review and customize test cases as needed")
                    print("   3. Use the 'Test Execution' sheet to track test results")
                    print("   4. Import test cases into your automation framework")
                    print("   5. Execute tests against your API endpoints")
                    
                    print("\n💡 Excel Features:")
                    print("   - Auto-sized columns for readability")
                    print("   - Multiple sheets for different purposes")
                    print("   - Structured data ready for automation tools")
                    print("   - Test execution tracking capabilities")
                    print("   - Comprehensive metadata and statistics")
                    
                else:
                    print(f"   ❌ Error: {result_data.get('error', 'Unknown error occurred')}")
                    return False
                
            except Exception as e:
                print(f"❌ Error during Excel test case generation: {str(e)}")
                return False
            
            return True

async def main():
    """Main function to run the test case generator client."""
    print("📊 Test Case Generator Client")
    print("="*60)
    print("This client connects to the Test Case Generator MCP server")
    print("to generate detailed test cases directly from OpenAPI specification")
    print("and output them in Excel format for easy review and execution.\n")
    
    try:
        success = await run_test_case_generator()
        if success:
            print("\n✅ Excel test case generation completed successfully!")
            print("📊 Check the output/test_cases.xlsx file for your test cases.")
        else:
            print("\n❌ Excel test case generation failed!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Excel test case generation interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 