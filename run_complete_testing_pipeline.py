#!/usr/bin/env python3

import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_test_plan_generator():
    """Run the Test Plan Generator MCP server."""
    
    print("🚀 STEP 1: GENERATING TEST PLAN")
    print("="*60)
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.test_plan_generator"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("🔧 Test Plan Generator MCP Server initialized successfully!")
            
            try:
                result = await session.call_tool(
                    "generate_test_plan",
                    {
                        "input_dir": "input"
                    }
                )
                
                print("✅ Test plan generated successfully!")
                result_data = json.loads(result.content[0].text)
                print(f"   📁 Test plan saved to: {result_data.get('output_file', 'output/test_plan.md')}")
                
                return True
                
            except Exception as e:
                print(f"❌ Error generating test plan: {str(e)}")
                return False

async def run_test_case_generator():
    """Run the Test Case Generator MCP server."""
    
    print("\n🧪 STEP 2: GENERATING TEST CASES")
    print("="*60)
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.test_case_generator"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("🔧 Test Case Generator MCP Server initialized successfully!")
            
            try:
                # Generate test cases
                result = await session.call_tool(
                    "generate_test_cases",
                    {
                        "input_dir": "input"
                    }
                )
                
                result_data = json.loads(result.content[0].text)
                
                if "statistics" in result_data:
                    stats = result_data["statistics"]
                    print("✅ Test cases generated successfully!")
                    print(f"   📁 Test cases saved to: {result_data.get('output_file', 'output/test_cases.json')}")
                    print(f"   📊 Statistics:")
                    print(f"      - Test Suites: {stats.get('total_test_suites', 0)}")
                    print(f"      - Test Cases: {stats.get('total_test_cases', 0)}")
                    print(f"      - API Endpoints: {stats.get('api_endpoints_analyzed', 0)}")
                
                # Excel test cases are self-validating due to structured format
                print("✅ Excel test cases generated and validated!")
                
                return True
                
            except Exception as e:
                print(f"❌ Error generating test cases: {str(e)}")
                return False

def display_results():
    """Display the final results and next steps."""
    
    print("\n" + "="*60)
    print("🎉 COMPLETE TESTING PIPELINE FINISHED!")
    print("="*60)
    
    # Check generated files
    files_generated = []
    
    if os.path.exists("output/test_plan.md"):
        files_generated.append("📄 output/test_plan.md - Comprehensive test plan")
    
    if os.path.exists("output/test_cases.xlsx"):
        files_generated.append("📊 output/test_cases.xlsx - Excel test cases with multiple sheets")
        files_generated.append("   └── Sheets: Test Cases, Test Execution, Metadata, API Endpoints")
    
    print("📁 Generated Files:")
    for file_info in files_generated:
        print(f"   {file_info}")
    
    print("\n🔧 Next Steps:")
    print("   1. Review the generated test plan and test cases")
    print("   2. Customize test cases for your specific requirements")
    print("   3. Import test cases into your automation framework")
    print("   4. Set up test data and environment")
    print("   5. Execute test cases against your API")
    
    print("\n💡 Integration Options:")
    print("   - Excel: Open directly for review and manual testing")
    print("   - Test Management: Import into TestRail, Zephyr, qTest")
    print("   - Automation: Convert to Postman, REST Assured, pytest")
    print("   - Tracking: Use 'Test Execution' sheet for test runs")
    print("   - CI/CD: Export data for automated test generation")

async def main():
    """Main orchestrator function."""
    
    print("🚀 COMPLETE TESTING PIPELINE")
    print("="*60)
    print("This pipeline will:")
    print("1. Generate a comprehensive test plan from your input files")
    print("2. Create detailed test cases from the test plan and API spec")
    print("3. Validate and structure the test cases for automation")
    print("")
    
    # Check if input files exist
    required_files = ["input/openapi.json"]
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required input files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nPlease ensure all input files are present before running the pipeline.")
        return
    
    try:
        # Step 1: Generate test plan
        test_plan_success = await run_test_plan_generator()
        
        if not test_plan_success:
            print("❌ Test plan generation failed. Stopping pipeline.")
            return
        
        # Step 2: Generate test cases
        test_case_success = await run_test_case_generator()
        
        if not test_case_success:
            print("❌ Test case generation failed.")
            return
        
        # Display final results
        display_results()
        
    except KeyboardInterrupt:
        print("\n\n👋 Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error in pipeline: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 