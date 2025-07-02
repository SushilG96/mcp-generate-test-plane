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
        
        prompt = f"""You are a Principal QA Architect and Test Strategist with 15+ years of experience in enterprise-level testing. Create a comprehensive, production-ready test plan that demonstrates advanced testing methodologies and industry best practices.

## ADVANCED TEST PLAN REQUIREMENTS:

### 1. EXECUTIVE SUMMARY & STRATEGIC OVERVIEW
- **Project Context**: Business objectives, stakeholder impact, and strategic alignment
- **Testing Philosophy**: Risk-based, shift-left, continuous testing approach
- **Quality Goals**: Specific quality attributes and success metrics
- **Resource Allocation**: Team structure, skills matrix, and capacity planning
- **Timeline & Milestones**: Detailed testing phases with dependencies

### 2. TEST STRATEGY & METHODOLOGY
- **Testing Pyramid**: Unit (70%), Integration (20%), E2E (10%) distribution
- **Risk-Based Testing**: Risk assessment matrix with impact/probability analysis
- **Test Levels**: Component, Integration, System, Acceptance testing details
- **Testing Types**: 
  - **Functional**: Feature, regression, smoke, sanity testing
  - **Non-Functional**: Performance, security, usability, reliability
  - **Specialized**: API, database, mobile, cross-browser testing
- **Automation Strategy**: Tool selection, framework design, CI/CD integration
- **Shift-Left Practices**: Early testing, static analysis, code reviews

### 3. COMPREHENSIVE TEST COVERAGE ANALYSIS
- **Requirements Traceability Matrix**: Link tests to requirements/user stories
- **Test Coverage Metrics**: Code coverage, functional coverage, risk coverage
- **Boundary Value Analysis**: Edge cases, limits, and error conditions
- **Equivalence Partitioning**: Input domains and representative test cases
- **State Transition Testing**: Workflow and state-based scenarios
- **Decision Table Testing**: Complex business rule validation

### 4. ADVANCED TEST CASE SPECIFICATIONS
For each test case, provide:
- **Test Case ID**: Hierarchical numbering (TC-MODULE-TYPE-###)
- **Test Suite**: Logical grouping and test suite organization
- **Priority**: Critical/High/Medium/Low with business justification
- **Test Type**: Functional/Security/Performance/Integration/E2E
- **Test Level**: Unit/Integration/System/Acceptance
- **Risk Level**: High/Medium/Low risk scenarios
- **Automation Candidate**: Yes/No with automation feasibility
- **Preconditions**: System state, test data, environment setup
- **Test Steps**: Detailed numbered steps with expected intermediate results
- **Expected Results**: Specific, measurable, verifiable outcomes
- **Test Data**: Realistic data sets with privacy considerations
- **Post-conditions**: System state after test execution
- **Dependencies**: Other tests, external systems, or configurations

### 5. PERFORMANCE & SCALABILITY TESTING
- **Load Testing**: Normal expected load scenarios
- **Stress Testing**: Beyond normal capacity limits
- **Spike Testing**: Sudden load increases
- **Volume Testing**: Large amounts of data processing
- **Performance KPIs**: Response time, throughput, resource utilization
- **Scalability Metrics**: Horizontal and vertical scaling tests
- **Performance Baselines**: Benchmark establishment and monitoring

### 6. COMPREHENSIVE SECURITY TESTING
- **OWASP Top 10**: Vulnerability assessment and mitigation
- **Authentication & Authorization**: Role-based access control testing
- **Data Protection**: Encryption, PII handling, GDPR compliance
- **Input Validation**: Injection attacks, XSS, CSRF prevention
- **Session Management**: Token handling, timeout, session fixation
- **API Security**: Rate limiting, authentication, input sanitization
- **Security Scanning**: SAST, DAST, dependency vulnerability checks

### 7. ACCESSIBILITY & COMPLIANCE TESTING
- **WCAG 2.1 AA Compliance**: Screen readers, keyboard navigation
- **Section 508**: Government accessibility standards
- **ADA Compliance**: Americans with Disabilities Act requirements
- **Cross-Platform Accessibility**: Mobile, desktop, assistive technologies
- **Regulatory Compliance**: Industry-specific standards (HIPAA, SOX, PCI-DSS)

### 8. TEST ENVIRONMENT & INFRASTRUCTURE
- **Environment Strategy**: Dev, Test, Staging, Production-like environments
- **Test Data Management**: Data generation, masking, refresh strategies
- **Configuration Management**: Environment consistency and version control
- **Monitoring & Observability**: Logging, metrics, alerting setup
- **Disaster Recovery**: Backup and recovery testing procedures
- **Cloud Testing**: Multi-cloud, hybrid cloud considerations

### 9. AUTOMATION FRAMEWORK & CI/CD INTEGRATION
- **Test Automation Architecture**: Layered approach, design patterns
- **Framework Selection**: Tool evaluation and selection criteria
- **CI/CD Pipeline Integration**: Automated testing in deployment pipeline
- **Test Reporting**: Real-time dashboards, trend analysis, failure analysis
- **Parallel Execution**: Grid setup, containerization, cloud scaling
- **Maintenance Strategy**: Test stability, flaky test management

### 10. QUALITY METRICS & KPIs
- **Test Metrics**: Pass/fail rates, defect density, test coverage
- **Quality Gates**: Entry/exit criteria with measurable thresholds
- **Defect Metrics**: Detection rate, severity distribution, fix time
- **Performance Metrics**: Response time trends, throughput analysis
- **Process Metrics**: Test execution efficiency, automation ROI
- **Predictive Analytics**: Quality forecasting, risk indicators

### 11. RISK MANAGEMENT & MITIGATION
- **Risk Assessment Matrix**: Technical, business, and operational risks
- **Mitigation Strategies**: Contingency plans for high-risk scenarios
- **Dependency Management**: External dependencies and fallback plans
- **Resource Risks**: Team availability, skill gap analysis
- **Timeline Risks**: Critical path analysis, buffer planning

### 12. COMMUNICATION & REPORTING
- **Stakeholder Matrix**: Communication frequency and content per audience
- **Test Reporting Strategy**: Daily, weekly, and milestone reports
- **Defect Triage Process**: Severity classification, escalation procedures
- **Go/No-Go Criteria**: Release readiness assessment framework
- **Post-Implementation Review**: Lessons learned, process improvements

## ADVANCED TESTING TECHNIQUES TO INCLUDE:
- **Exploratory Testing**: Charter-based, session-based testing
- **Pairwise Testing**: Combinatorial test design
- **Model-Based Testing**: State machines, UML-based testing
- **Property-Based Testing**: Generative testing approaches
- **Chaos Engineering**: Resilience and fault tolerance testing
- **A/B Testing**: Feature flag testing and gradual rollouts
- **Synthetic Monitoring**: Production-like testing in staging

## MODERN TESTING PRACTICES:
- **Behavior-Driven Development (BDD)**: Gherkin scenarios
- **Test-Driven Development (TDD)**: Red-Green-Refactor cycle
- **Continuous Testing**: Feedback loops and quality gates
- **Shift-Right Testing**: Production monitoring and canary releases
- **Risk-Based Testing**: Focus on high-impact, high-probability scenarios
- **Crowd Testing**: Leveraging diverse user perspectives

## INPUT DOCUMENTS:
{file_content}

Generate an enterprise-grade, comprehensive test plan that serves as a blueprint for world-class quality assurance. The plan should be immediately executable by a distributed QA team and demonstrate mastery of modern testing practices."""
        
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
