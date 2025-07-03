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
        
        prompt = f"""You are a Principal QA Architect and Test Strategist with 15+ years of experience across multiple domains (fintech, healthcare, e-commerce, data platforms, enterprise systems, etc.). Your expertise is in creating CONTEXT-AWARE test plans that adapt to the specific business domain and requirements found in the provided input documents.

## INSTRUCTIONS FOR INTELLIGENT ANALYSIS:

### STEP 1: ANALYZE THE PROVIDED INPUT DOCUMENTS
Before creating the test plan, carefully analyze ALL provided input documents to understand:

1. **APPLICATION PURPOSE & DOMAIN**:
   - What type of system/application is this? (e-commerce, data platform, fintech, healthcare, etc.)
   - What business problem does it solve?
   - Who are the target users and stakeholders?

2. **CORE BUSINESS FEATURES & WORKFLOWS**:
   - What are the main business capabilities?
   - What are the key user workflows and journeys?
   - What business rules and logic need validation?

3. **TECHNICAL ARCHITECTURE**:
   - What technologies and frameworks are involved?
   - What are the key API endpoints and their purposes?
   - What external systems or services does it integrate with?

4. **DOMAIN-SPECIFIC REQUIREMENTS**:
   - What regulatory compliance needs exist (GDPR, HIPAA, SOX, etc.)?
   - What performance characteristics are critical?
   - What security requirements are specific to this domain?

5. **BUSINESS RISKS & CRITICAL PATHS**:
   - What failures would have the highest business impact?
   - What workflows are most business-critical?
   - What integration points are riskiest?

### STEP 2: CREATE DOMAIN-ADAPTIVE TEST STRATEGY
Based on your analysis, create a test strategy that is specifically tailored to the identified domain and business context:

## COMPREHENSIVE TEST PLAN STRUCTURE:

### EXECUTIVE SUMMARY
- **Application Overview**: Describe the application based on your analysis of the input documents
- **Business Context**: Explain the business domain, value proposition, and user benefits
- **Key Business Functions**: List the core business capabilities identified from the documents
- **Testing Objectives**: Define quality goals specific to this application's business context
- **Critical Risk Areas**: Identify the highest-risk areas based on business impact

### BUSINESS-DRIVEN TEST STRATEGY

#### FUNCTIONAL TESTING STRATEGY
Based on the identified business domain, focus on:
- **Core Business Workflows**: End-to-end testing of primary user journeys
- **Business Rule Validation**: Testing of domain-specific business logic
- **Data Flow & Processing**: Testing of data handling workflows specific to this domain
- **Integration Scenarios**: Testing of critical system integrations
- **User Role & Permission Testing**: Testing of role-based access appropriate to the domain

#### DOMAIN-SPECIFIC NON-FUNCTIONAL TESTING
Adapt testing approach based on the identified domain:
- **Performance Requirements**: Based on real usage patterns for this domain
- **Security Testing**: Focus on security concerns specific to this business domain
- **Scalability Testing**: Based on expected growth patterns and business scaling needs
- **Reliability & Availability**: Based on business continuity requirements
- **Compliance Testing**: Address regulatory requirements specific to the domain

#### API-TO-BUSINESS MAPPING
For each API endpoint identified in the specifications:
- **Business Function**: What business capability does this endpoint serve?
- **User Context**: In what business scenarios would this endpoint be used?
- **Business Impact**: What business processes depend on this endpoint?
- **Integration Role**: How does this endpoint fit into larger business workflows?

### DETAILED TEST CASE SPECIFICATIONS

For each major business function identified:

#### Test Case Structure:
- **Test Case ID**: Clear hierarchical numbering (TC-[DOMAIN]-[FUNCTION]-[TYPE]-###)
- **Business Function**: What specific business capability is being tested
- **Business Scenario**: Real-world business context for this test
- **Test Objective**: What business risk or requirement is being validated
- **User Role**: Which user type or system would perform this action
- **API Endpoints**: Which technical endpoints are involved
- **Test Type**: Functional/Integration/Performance/Security/Compliance
- **Business Priority**: Critical/High/Medium/Low with business justification
- **Preconditions**: Required business state and data setup
- **Test Steps**: Business-focused test execution steps
- **Expected Results**: Business-oriented success criteria
- **Business Impact of Failure**: What happens to the business if this fails

### END-TO-END BUSINESS WORKFLOW TESTING
- **Primary User Journeys**: Complete business process validation
- **Cross-System Workflows**: Multi-system business processes
- **Exception Handling**: How the system handles business exceptions
- **Edge Case Scenarios**: Unusual but valid business situations

### PERFORMANCE & SCALABILITY STRATEGY
Based on the business context:
- **Expected Load Patterns**: Realistic usage based on business model
- **Business Performance KPIs**: Metrics that matter to business stakeholders
- **Scalability Requirements**: Growth projections based on business plans
- **Performance Impact on Business**: How performance affects business outcomes

### SECURITY & COMPLIANCE STRATEGY
Tailored to the identified domain:
- **Domain-Specific Security Risks**: Security concerns particular to this business
- **Regulatory Compliance**: Specific compliance requirements (GDPR, HIPAA, PCI, etc.)
- **Data Protection**: Appropriate to the type of data handled
- **Access Control**: Role-based security appropriate to the business model

### RISK ASSESSMENT & MITIGATION
- **Business Risk Matrix**: Risks prioritized by business impact
- **Technical Risk Assessment**: Technology-specific risks
- **Integration Risk Analysis**: Third-party and external system risks
- **Mitigation Strategies**: Business-continuity focused approaches

### QUALITY METRICS & SUCCESS CRITERIA
- **Business KPIs**: Metrics that directly impact business success
- **User Experience Metrics**: Relevant to the target user base
- **Technical Performance Metrics**: Aligned with business requirements
- **Quality Gates**: Release criteria based on business risk tolerance

## INPUT DOCUMENTS TO ANALYZE:
{file_content}

## OUTPUT REQUIREMENTS:
Create a comprehensive test plan that demonstrates:
1. **Deep understanding** of the specific business domain and application context
2. **Intelligent mapping** between business requirements and technical implementation
3. **Domain-appropriate** testing strategies and priorities
4. **Context-aware** test cases that reflect real business scenarios
5. **Business-risk-driven** prioritization rather than generic technical concerns
6. **Actionable recommendations** that can be immediately implemented

The test plan should clearly show that you've thoroughly analyzed and understood the provided input documents, and have created a testing approach specifically tailored to this application's business domain and requirements."""
        
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
