import asyncio
import os
from pathlib import Path
from fastmcp import Client, FastMCP

async def check_input_files():
    """Check if input directory exists and has files"""
    input_dir = Path("input")
    
    if not input_dir.exists():
        print("❌ Input directory does not exist!")
        print("💡 Please create an 'input' directory and add your requirement files")
        return False
    
    # Get all files in input directory
    files = list(input_dir.glob("*"))
    readable_files = [f for f in files if f.is_file() and f.suffix.lower() in ['.txt', '.md', '.doc', '.docx', '.pdf', '.json']]
    
    if not readable_files:
        print("❌ No readable files found in input directory!")
        print("💡 Please add your requirement files (.txt, .md, .doc, .docx, .pdf, .json) to the 'input' directory")
        print("📁 Example files to add:")
        print("   - requirements.txt")
        print("   - user_stories.md") 
        print("   - specifications.docx")
        print("   - acceptance_criteria.txt")
        print("   - api_specs.json")
        print("   - test_scenarios.json")
        print("   - urls.txt (optional - URLs to fetch content from)")
        return False
    
    print(f"✅ Found {len(readable_files)} file(s) in input directory:")
    for file in readable_files:
        print(f"   📄 {file.name}")
    
    return True

async def test_with_direct_server():
    """Test using direct server import (in-memory connection)"""
    try:
        print("🔄 Attempting direct server connection...")
        
        # Import the server directly for in-memory testing
        import sys
        sys.path.append('.')
        
        from server.test_plan_generator import mcp
        
        client = Client(mcp)
        
        async with client:
            print("✅ Connected to server successfully!")
            
            # Test the tool
            input_dir = "input"
            response = await client.call_tool("generate_test_plan", {"input_dir": input_dir})
            
            print("\n" + "="*50)
            print("🎉 TEST PLAN GENERATED:")
            print("="*50)
            print(response[0].text if isinstance(response, list) else response.text)
            print("="*50)
            
            return True
            
    except Exception as e:
        print(f"❌ Direct server connection failed: {e}")
        return False

async def test_with_script_path():
    """Test using script path connection"""
    try:
        print("🔄 Attempting script path connection...")
        
        client = Client("server/test_plan_generator.py")
        
        async with client:
            print("✅ Connected to server via script path!")
            
            input_dir = "input"
            response = await client.call_tool("generate_test_plan", {"input_dir": input_dir})
            
            print("\n" + "="*50)
            print("🎉 TEST PLAN GENERATED:")
            print("="*50)
            print(response[0].text if isinstance(response, list) else response.text)
            print("="*50)
            
            return True
            
    except Exception as e:
        print(f"❌ Script path connection failed: {e}")
        return False

async def main():
    """Main function that tries different connection methods"""
    print("🚀 Starting MCP Test Plan Generator Client")
    print("="*50)
    
    # Check environment
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Warning: GROQ_API_KEY not found in environment")
        print("   Make sure to set your GROQ API key in .env file or environment variables")
        return
    
    # Check if input files exist
    if not await check_input_files():
        return
    
    # Try different connection methods
    success = False
    
    # Method 1: Direct server import (recommended for testing)
    if not success:
        success = await test_with_direct_server()
    
    # Method 2: Script path (if direct import fails)
    if not success:
        success = await test_with_script_path()
    
    if not success:
        print("\n❌ All connection methods failed!")
        print("💡 Troubleshooting tips:")
        print("   1. Make sure all dependencies are installed: uv sync")
        print("   2. Check that GROQ_API_KEY is set in your environment")
        print("   3. Verify server files exist and are correct")
        print("   4. Try running the server separately first")
    else:
        print("\n✅ Test plan generation completed successfully!")
        print("📁 Check the 'output' directory for the saved test plan file.")

if __name__ == "__main__":
    asyncio.run(main())
