#!/usr/bin/env python3
"""
Test Case Generator Client with Configuration Management

This client demonstrates how to use the configuration-based test case generator
that reads from config/test_config.json to determine what test types to generate.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_config_test_case_client():
    """Run test case client with configuration management."""
    
    # Server configuration
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.test_case_generator"],
        env=None
    )
    
    print("🔧 Test Case Generator - Configuration-Based Client")
    print("=" * 60)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            try:
                # Step 1: Show current configuration
                print("\n📋 Step 1: Checking current test configuration...")
                config_result = await session.call_tool("show_test_config", {})
                
                if config_result.content[0].text:
                    import json
                    config_data = json.loads(config_result.content[0].text)
                    
                    if "error" in config_data:
                        print(f"❌ Error: {config_data['error']}")
                        return
                    
                    print(f"✅ Current Profile: {config_data['current_profile']}")
                    print(f"📊 Tests per endpoint: {config_data['tests_per_endpoint']}")
                    print(f"🔧 Configuration file: {config_data['configuration_file']}")
                    
                    if "profile_description" in config_data:
                        print(f"📝 Description: {config_data['profile_description']}")
                    
                    print(f"🧪 Enabled test types: {', '.join(config_data['enabled_test_types'])}")
                    print(f"🎯 Test suffixes: {', '.join(config_data['enabled_test_suffixes'])}")
                    
                    print("\n📚 Available Profiles:")
                    for profile_name, profile_info in config_data['available_profiles'].items():
                        status = "👈 CURRENT" if profile_name == config_data['current_profile'] else ""
                        print(f"  • {profile_name}: {profile_info['description']} ({profile_info['tests_per_endpoint']} tests/endpoint) {status}")

                # Step 2: Ask user if they want to switch profiles
                print("\n" + "=" * 60)
                print("🔄 Step 2: Profile Management")
                
                switch_profile = input("\nDo you want to switch to a different profile? (y/N): ").lower().strip()
                
                if switch_profile == 'y':
                    print("\nAvailable profiles:")
                    for profile_name, profile_info in config_data['available_profiles'].items():
                        print(f"  • {profile_name}: {profile_info['description']}")
                    
                    new_profile = input("\nEnter profile name to switch to: ").strip()
                    
                    if new_profile:
                        print(f"\n🔄 Switching to profile: {new_profile}")
                        switch_result = await session.call_tool("switch_test_profile", {"profile_name": new_profile})
                        
                        if switch_result.content[0].text:
                            switch_data = json.loads(switch_result.content[0].text)
                            
                            if "error" in switch_data:
                                print(f"❌ Error: {switch_data['error']}")
                            else:
                                print(f"✅ {switch_data['message']}")
                                print(f"📊 New settings: {switch_data['tests_per_endpoint']} tests per endpoint")
                                print(f"🧪 Test types: {', '.join(switch_data['enabled_types'])}")

                # Step 3: Generate test cases with current configuration
                print("\n" + "=" * 60)
                print("🚀 Step 3: Generating Test Cases")
                
                proceed = input("\nGenerate test cases with current configuration? (Y/n): ").lower().strip()
                
                if proceed != 'n':
                    print("\n🔄 Generating test cases based on configuration...")
                    
                    result = await session.call_tool("generate_test_cases", {"input_dir": "input"})
                    
                    if result.content[0].text:
                        result_data = json.loads(result.content[0].text)
                        
                        if "error" in result_data:
                            print(f"❌ Error: {result_data['error']}")
                        else:
                            print(f"✅ Success! Test cases generated:")
                            print(f"📊 Excel file: {result_data['output_file']}")
                            if 'csv_file' in result_data:
                                print(f"📄 CSV file: {result_data['csv_file']} (for viewing in Cursor)")
                            print(f"💬 Message: {result_data.get('message', '')}")
                            
                            # Show statistics if available
                            if "statistics" in result_data:
                                stats = result_data["statistics"]
                                print(f"📊 Statistics:")
                                print(f"   • Total test cases: {stats.get('total_test_cases', 0)}")
                                print(f"   • API endpoints: {stats.get('api_endpoints_analyzed', 0)}")
                                print(f"   • Test suites: {stats.get('total_test_suites', 0)}")
                                print(f"   • Automation candidates: {stats.get('automation_candidates', 0)}")
                                
                                # Calculate average tests per endpoint
                                if stats.get('api_endpoints_analyzed', 0) > 0:
                                    avg_tests = stats.get('total_test_cases', 0) / stats.get('api_endpoints_analyzed', 1)
                                    print(f"   • Average tests per endpoint: {avg_tests:.1f}")
                                
                                # Show test categories
                                if "categories" in stats:
                                    categories_str = ', '.join([f"{k}: {v}" for k, v in stats['categories'].items()])
                                    print(f"   • Test categories: {categories_str}")
                                
                                # Show test priorities  
                                if "priorities" in stats:
                                    priorities_str = ', '.join([f"{k}: {v}" for k, v in stats['priorities'].items()])
                                    print(f"   • Test priorities: {priorities_str}")
                            
                            print(f"\n🎉 Generation Complete!")
                            print(f"📋 Open {result_data['output_file']} to view your test cases")
                
                print("\n" + "=" * 60)
                print("💡 Configuration Tips:")
                print("   • Edit config/test_config.json to customize test types")
                print("   • Set 'enabled': true/false for individual test types")
                print("   • Change 'current_profile' to switch between predefined profiles")
                print("   • Create custom profiles in 'predefined_profiles' section")
                print("   • Use show_test_config tool to check current settings")
                
            except Exception as e:
                print(f"❌ Error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_config_test_case_client()) 