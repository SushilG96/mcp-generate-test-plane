import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from fastmcp import FastMCP, Context
from server.preprocess import read_and_preprocess_files
from server.validation import validate_test_plan

# Load environment variables
load_dotenv()

mcp = FastMCP("TestPlanGenerator")

# Initialize GROQ client
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY environment variable is required")

groq_client = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192"  # Using Llama 3 70B with 8K context window
)

@mcp.tool("generate_test_plan")
async def generate_test_plan(input_dir: str, ctx: Context) -> dict:
    """
    Generates a test plan using files from a directory.
    
    Args:
        input_dir (str): Directory path containing input files
        ctx (Context): MCP context for logging
        
    Returns:
        dict: Result containing test plan or error message
    """
    try:
        # Step 1: Read and preprocess input files
        await ctx.info("Reading and preprocessing input files...")
        file_content = read_and_preprocess_files(input_dir)
        
        if not file_content:
            return {"error": "No readable files found in the specified directory"}

        # Step 2: Generate test plan using GROQ LLM
        await ctx.info("Generating test plan with GROQ LLM...")
        
        # Truncate content if too long to avoid token limits
        max_content_length = 15000  # Leave room for prompt + response
        if len(file_content) > max_content_length:
            file_content = file_content[:max_content_length] + "\n\n[Content truncated due to length...]"
            await ctx.info(f"Input content truncated to {max_content_length} characters")
        
        prompt = f"""You are a senior QA engineer and test architect. Create a comprehensive, professional test plan based on the provided requirements and user stories.

## REQUIREMENTS FOR THE TEST PLAN:

### Structure the test plan with these sections:
1. **Executive Summary** - Brief overview and testing approach
2. **Test Objectives** - What we're testing and why
3. **Scope and Coverage** - What's included/excluded, test levels
4. **Test Strategy** - Testing approach, types, priorities
5. **Test Environment** - Required setup, data, configurations
6. **Test Cases** - Detailed, actionable test scenarios
7. **Risk Assessment** - Potential risks and mitigation
8. **Entry/Exit Criteria** - When to start/stop testing
9. **Deliverables** - Expected outputs and reports

### For Test Cases, include:
- **Test Case ID** (TC-001, TC-002, etc.)
- **Test Case Name** (descriptive title)
- **Priority** (High/Medium/Low)
- **Test Type** (Functional/Security/Performance/UI)
- **Preconditions** (setup required)
- **Test Steps** (numbered, detailed steps)
- **Expected Results** (what should happen)
- **Test Data** (specific inputs to use)
- **Dependencies** (other tests/systems needed)

### Test Coverage Areas to Address:
- **Functional Testing**: Core feature validation
- **Security Testing**: Authentication, authorization, data protection
- **Usability Testing**: User experience, accessibility
- **Performance Testing**: Load, response times, scalability
- **Compatibility Testing**: Browser, device, OS support
- **Error Handling**: Invalid inputs, edge cases, failures
- **Integration Testing**: API endpoints, database interactions
- **Regression Testing**: Ensure existing functionality works

### Make it Professional and Actionable:
- Use clear, specific language
- Include realistic test data examples
- Add test automation recommendations where applicable
- Consider different user roles and permissions
- Include both positive and negative test scenarios
- Add boundary value testing
- Include accessibility and compliance considerations

## INPUT DOCUMENTS:
{file_content}

Generate a detailed, production-ready test plan that a QA team can immediately execute."""
        
        response = groq_client.invoke(prompt)
        test_plan = response.content

        # Step 3: Validate the generated test plan
        await ctx.info("Validating the test plan...")
        validation_result = validate_test_plan(test_plan)

        if not validation_result["is_valid"]:
            return {"error": validation_result["message"]}

        # Step 4: Save and return test plan
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "test_plan.md")
        
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(test_plan)

        await ctx.info(f"Test plan saved to {output_file}")
        return {
            "test_plan": test_plan, 
            "output_file": output_file,
            "validation": validation_result
        }
        
    except Exception as e:
        await ctx.error(f"Error generating test plan: {str(e)}")
        return {"error": f"Failed to generate test plan: {str(e)}"}


if __name__ == "__main__":
    mcp.run()
