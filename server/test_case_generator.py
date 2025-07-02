import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

mcp = FastMCP("TestCaseGenerator")

def load_test_config(config_path: str = "config/test_config.json") -> Dict[str, Any]:
    """Load test configuration from JSON file."""
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        # Return default config if file doesn't exist
        return {
            "enabled_test_types": {
                "functional": {"enabled": True, "tests": ["FUNC-HAPPY", "FUNC-NEGATIVE", "FUNC-VALIDATION", "FUNC-WORKFLOW", "FUNC-BOUNDARY"]},
                "security": {"enabled": True, "tests": ["SEC-AUTH", "SEC-AUTHZ", "SEC-CONTENT", "SEC-ENCRYPTION"]},
                "error_handling": {"enabled": True, "tests": ["ERR-NOTFOUND", "ERR-INVALID"]}
            },
            "current_profile": "default"
        }
    except Exception as e:
        raise Exception(f"Error loading test config: {str(e)}")

def load_test_plan_intelligence(test_plan_path: str = "output/test_plan.md") -> Dict[str, Any]:
    """Load and extract intelligence from the test plan to inform test case generation."""
    try:
        with open(test_plan_path, "r", encoding="utf-8") as file:
            test_plan_content = file.read()
        
        # Extract key information from test plan
        intelligence = {
            "application_context": "",
            "business_workflows": [],
            "integration_points": [],
            "critical_scenarios": [],
            "performance_requirements": [],
            "security_requirements": []
        }
        
        # Parse application context
        if "Executive Summary" in test_plan_content:
            lines = test_plan_content.split('\n')
            in_summary = False
            for line in lines:
                if "Executive Summary" in line or "Strategic Overview" in line:
                    in_summary = True
                    continue
                if in_summary and line.strip().startswith('**') and "Executive" not in line:
                    break
                if in_summary and line.strip():
                    intelligence["application_context"] += line.strip() + " "
        
        # Extract workflow patterns from test plan
        workflow_indicators = [
            "workflow", "process", "sequence", "integration", "end-to-end",
            "business logic", "transaction", "pipeline", "orchestration"
        ]
        
        lines = test_plan_content.lower().split('\n')
        for line in lines:
            for indicator in workflow_indicators:
                if indicator in line and len(line.strip()) > 20:
                    intelligence["business_workflows"].append(line.strip())
                    break
        
        # Extract performance requirements
        perf_lines = [line for line in lines if any(kw in line for kw in ["performance", "response time", "throughput", "latency", "load"])]
        intelligence["performance_requirements"] = perf_lines[:5]  # Top 5 performance insights
        
        # Extract security requirements  
        sec_lines = [line for line in lines if any(kw in line for kw in ["security", "authentication", "authorization", "encryption", "owasp"])]
        intelligence["security_requirements"] = sec_lines[:5]  # Top 5 security insights
        
        return intelligence
        
    except FileNotFoundError:
        # Return empty intelligence if test plan not found
        return {
            "application_context": "API testing without specific business context",
            "business_workflows": [],
            "integration_points": [],
            "critical_scenarios": [],
            "performance_requirements": [],
            "security_requirements": []
        }
    except Exception as e:
        raise Exception(f"Error loading test plan intelligence: {str(e)}")

def analyze_api_relationships(endpoints: List[Dict], openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze API endpoints to identify potential workflows and relationships."""
    
    # Group endpoints by tags/modules
    endpoints_by_tag = {}
    for endpoint in endpoints:
        tags = endpoint.get('tags', ['General'])
        for tag in tags:
            if tag not in endpoints_by_tag:
                endpoints_by_tag[tag] = []
            endpoints_by_tag[tag].append(endpoint)
    
    # Identify CRUD workflows
    crud_workflows = []
    for tag, tag_endpoints in endpoints_by_tag.items():
        methods = [ep['method'] for ep in tag_endpoints]
        paths = [ep['path'] for ep in tag_endpoints]
        
        # Look for CRUD patterns
        has_create = 'POST' in methods
        has_read = 'GET' in methods  
        has_update = 'PUT' in methods or 'PATCH' in methods
        has_delete = 'DELETE' in methods
        
        if sum([has_create, has_read, has_update, has_delete]) >= 2:
            crud_workflows.append({
                "tag": tag,
                "operations": methods,
                "paths": paths,
                "workflow_type": "CRUD"
            })
    
    # Identify potential sequences (endpoints that might be called together)
    sequences = []
    for i, ep1 in enumerate(endpoints):
        for j, ep2 in enumerate(endpoints[i+1:], i+1):
            # Check if endpoints might be related
            path1_parts = ep1['path'].split('/')
            path2_parts = ep2['path'].split('/')
            
            # Same resource family but different operations
            if len(path1_parts) > 1 and len(path2_parts) > 1:
                if path1_parts[1] == path2_parts[1] and ep1['method'] != ep2['method']:
                    sequences.append({
                        "endpoint1": ep1,
                        "endpoint2": ep2,
                        "relationship": "resource_family",
                        "sequence_type": f"{ep1['method']}_then_{ep2['method']}"
                    })
    
    return {
        "endpoints_by_tag": endpoints_by_tag,
        "crud_workflows": crud_workflows,
        "potential_sequences": sequences[:10]  # Limit to top 10 sequences
    }

def generate_workflow_test_cases(endpoint: Dict, test_plan_intelligence: Dict, api_relationships: Dict, all_endpoints: List[Dict]) -> List[Dict]:
    """Generate intelligent workflow test cases based on test plan analysis and API relationships."""
    
    workflow_tests = []
    endpoint_path = endpoint['path']
    endpoint_method = endpoint['method']
    endpoint_tag = endpoint.get('tags', ['API'])[0] if endpoint.get('tags') else 'API'
    
    # Get application context for more intelligent test descriptions
    app_context = test_plan_intelligence.get("application_context", "API system")
    business_workflows = test_plan_intelligence.get("business_workflows", [])
    
    # 1. End-to-End Workflow Test
    workflow_tests.append({
        "suffix": "WORKFLOW-E2E",
        "title": f"Test {endpoint_method} {endpoint_path} - End-to-End Business Workflow",
        "description": f"Verify {endpoint_method} {endpoint_path} works correctly within complete business workflows based on test plan analysis",
        "category": "Workflow Integration",
        "priority": "High",
        "test_level": "System",
        "risk_level": "High",
        "test_steps": f"1. Identify complete business workflow involving {endpoint_path}\n2. Set up prerequisite data and system state\n3. Execute workflow sequence including {endpoint_method} {endpoint_path}\n4. Verify end-to-end workflow completion\n5. Validate business rules and data consistency\n6. Check audit trails and logging\n7. Verify rollback scenarios if workflow fails",
        "expected_results": f"Complete workflow executes successfully; Business rules enforced; Data consistency maintained; Proper error handling in workflow failures; Context: {app_context[:100]}...",
        "test_data": "Complete workflow scenario data, prerequisite resources, business rule test cases",
        "tags": "api, workflow, e2e, business-process, integration, system-test"
    })
    
    # 2. API Sequence Testing
    related_endpoints = []
    for seq in api_relationships.get("potential_sequences", []):
        if (seq["endpoint1"]["path"] == endpoint_path and seq["endpoint1"]["method"] == endpoint_method) or \
           (seq["endpoint2"]["path"] == endpoint_path and seq["endpoint2"]["method"] == endpoint_method):
            related_endpoints.append(seq)
    
    sequence_description = f"Test {endpoint_method} {endpoint_path} in sequence with related APIs"
    if related_endpoints:
        related_info = related_endpoints[0]
        other_ep = related_info["endpoint2"] if related_info["endpoint1"]["path"] == endpoint_path else related_info["endpoint1"]
        sequence_description = f"Test {endpoint_method} {endpoint_path} in sequence with {other_ep['method']} {other_ep['path']}"
    
    workflow_tests.append({
        "suffix": "WORKFLOW-SEQUENCE",
        "title": f"Test {endpoint_method} {endpoint_path} - API Sequence Integration",
        "description": sequence_description,
        "category": "Workflow Integration",
        "priority": "Medium",
        "test_level": "Integration",
        "risk_level": "Medium",
        "test_steps": f"1. Identify API sequence involving {endpoint_path}\n2. Test prerequisite API calls\n3. Execute {endpoint_method} {endpoint_path} in sequence\n4. Verify data flow between APIs\n5. Test sequence with invalid intermediate states\n6. Validate error propagation in sequence\n7. Test sequence rollback scenarios",
        "expected_results": "API sequence executes correctly; Data flows properly between calls; Error handling works in sequence; State consistency maintained",
        "test_data": "Sequence test data, intermediate state data, dependency chain test cases",
        "tags": "api, workflow, sequence, integration, data-flow"
    })
    
    # 3. CRUD Workflow Testing (if endpoint is part of CRUD operations)
    endpoint_crud_info = None
    for crud in api_relationships.get("crud_workflows", []):
        if endpoint_tag == crud["tag"] or any(endpoint_path in path for path in crud["paths"]):
            endpoint_crud_info = crud
            break
    
    crud_operations = ""
    if endpoint_crud_info:
        crud_operations = f"Part of {endpoint_crud_info['tag']} CRUD workflow: {', '.join(endpoint_crud_info['operations'])}"
    
    workflow_tests.append({
        "suffix": "WORKFLOW-CRUD",
        "title": f"Test {endpoint_method} {endpoint_path} - CRUD Workflow Integration",
        "description": f"Verify {endpoint_method} {endpoint_path} works correctly within CRUD operations workflow",
        "category": "Workflow Integration",
        "priority": "Medium",
        "test_level": "Integration",
        "risk_level": "Medium",
        "test_steps": f"1. Test CREATE operation and data setup\n2. Verify READ operations can access created data\n3. Test {endpoint_method} {endpoint_path} with existing data\n4. Execute UPDATE operations and verify changes\n5. Test DELETE operations and cleanup\n6. Verify referential integrity throughout CRUD cycle\n7. Test concurrent CRUD operations",
        "expected_results": f"CRUD workflow operates correctly; Data integrity maintained; Proper resource lifecycle management; {crud_operations}",
        "test_data": "CRUD workflow test data, resource lifecycle scenarios, concurrent operation test cases",
        "tags": "api, workflow, crud, lifecycle, data-integrity"
    })
    
    # 4. Cross-Module Integration
    cross_module_endpoints = []
    current_module = endpoint_tag
    for ep in all_endpoints:
        ep_tags = ep.get('tags', ['General'])
        if ep_tags and ep_tags[0] != current_module and ep['path'] != endpoint_path:
            cross_module_endpoints.append(ep)
    
    integration_context = f"Integration with other modules in {app_context[:50]}..." if app_context else "Cross-module integration testing"
    
    workflow_tests.append({
        "suffix": "WORKFLOW-INTEGRATION",
        "title": f"Test {endpoint_method} {endpoint_path} - Cross-Module Integration",
        "description": f"Verify {endpoint_method} {endpoint_path} integrates correctly with other system modules",
        "category": "Workflow Integration", 
        "priority": "Medium",
        "test_level": "System",
        "risk_level": "Medium",
        "test_steps": f"1. Identify cross-module dependencies for {endpoint_path}\n2. Test integration with external modules\n3. Verify data exchange between modules\n4. Test module isolation and error boundaries\n5. Validate cross-module authentication/authorization\n6. Test module failover scenarios\n7. Verify cross-module transaction consistency",
        "expected_results": f"Cross-module integration works correctly; Module boundaries respected; Data consistency across modules; {integration_context}",
        "test_data": "Cross-module integration data, external dependency mocks, module boundary test scenarios",
        "tags": "api, workflow, integration, cross-module, system-integration"
    })
    
    return workflow_tests

def get_enabled_test_suffixes(config: Dict[str, Any]) -> List[str]:
    """Get list of enabled test suffixes based on configuration."""
    enabled_suffixes = []
    
    # Check if using a profile
    current_profile = config.get("current_profile")
    if current_profile and current_profile in config.get("predefined_profiles", {}):
        profile = config["predefined_profiles"][current_profile]
        enabled_types = profile["enabled_types"]
        
        # Get test suffixes for enabled types in profile
        for test_type in enabled_types:
            type_config = config["enabled_test_types"].get(test_type, {})
            if type_config.get("tests"):
                enabled_suffixes.extend(type_config["tests"])
    else:
        # Use individual enabled_test_types
        for test_type, type_config in config.get("enabled_test_types", {}).items():
            if type_config.get("enabled", False):
                enabled_suffixes.extend(type_config.get("tests", []))
    
    return enabled_suffixes

def read_openapi_spec(openapi_path: str) -> Dict[str, Any]:
    """Read and parse the OpenAPI specification."""
    try:
        with open(openapi_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"OpenAPI specification not found at: {openapi_path}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in OpenAPI specification: {str(e)}")
    except Exception as e:
        raise Exception(f"Error reading OpenAPI specification: {str(e)}")

def generate_comprehensive_test_cases(endpoints: List[Dict], openapi_spec: Dict[str, Any], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Generate comprehensive test cases for all API endpoints based on configuration."""
    
    # Load config if not provided
    if config is None:
        config = load_test_config()
    
    # Get enabled test suffixes from config
    enabled_suffixes = get_enabled_test_suffixes(config)
    
    # Load test plan intelligence if workflow tests are enabled
    test_plan_intelligence = {}
    api_relationships = {}
    if any("WORKFLOW" in suffix for suffix in enabled_suffixes):
        test_plan_intelligence = load_test_plan_intelligence()
        api_relationships = analyze_api_relationships(endpoints, openapi_spec)
    
    test_cases_list = []
    test_case_id = 1
    
    for endpoint in endpoints:
        endpoint_tag = endpoint['tags'][0] if endpoint['tags'] else 'API'
        
        # Define all possible test case types
        all_test_case_types = [
            {
                "suffix": "FUNC-HAPPY",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Happy Path",
                "description": f"Verify successful {endpoint['method']} request to {endpoint['path']} with valid data",
                "category": "Functional",
                "priority": "High",
                "test_level": "Integration",
                "risk_level": "Medium",
                "test_steps": f"1. Prepare valid request data for {endpoint['path']}\n2. Set up proper authentication headers\n3. Send {endpoint['method']} request to {endpoint['path']}\n4. Verify response status code (200-299)\n5. Validate response body structure matches API specification\n6. Check response headers are correct\n7. Verify response time is within acceptable limits",
                "expected_results": f"Status code: 200-299; Valid response body structure; Correct content-type header; Response time < 2 seconds; All required fields present in response",
                "test_data": "Valid input parameters as per OpenAPI specification",
                "tags": "api, functional, smoke, regression, happy-path"
            },
            {
                "suffix": "FUNC-NEGATIVE",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Negative Scenarios",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} handles negative scenarios properly",
                "category": "Functional",
                "priority": "Medium",
                "test_level": "Integration",
                "risk_level": "Medium",
                "test_steps": f"1. Test with missing required parameters\n2. Send {endpoint['method']} request with wrong data types\n3. Test with negative numbers where positive expected\n4. Try invalid enum values if applicable\n5. Test with extremely long strings\n6. Verify proper error responses for each scenario\n7. Ensure system stability maintained",
                "expected_results": "Appropriate error codes (400, 422) returned; Clear error messages explaining failures; System remains stable; No data corruption occurs",
                "test_data": "Missing parameters, wrong data types, invalid enum values, oversized strings, negative numbers",
                "tags": "api, functional, negative, validation, error-scenarios"
            },
            {
                "suffix": "FUNC-VALIDATION",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Input Validation",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} validates input data correctly",
                "category": "Functional",
                "priority": "Medium",
                "test_level": "Integration", 
                "risk_level": "Medium",
                "test_steps": f"1. Test field length validations (min/max)\n2. Validate data format requirements (email, phone, URL)\n3. Test special character handling in text fields\n4. Validate numeric range constraints\n5. Test date/time format validations\n6. Verify required field validations\n7. Test conditional field validations",
                "expected_results": "Input validation rules properly enforced; Clear validation error messages; Consistent validation behavior across all fields",
                "test_data": "Field length violations, format violations, special characters, out-of-range numbers, invalid dates",
                "tags": "api, functional, validation, input-validation, data-integrity"
            },
            {
                "suffix": "FUNC-WORKFLOW",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Business Workflow",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} follows correct business logic and workflow",
                "category": "Functional",
                "priority": "High",
                "test_level": "System",
                "risk_level": "High",
                "test_steps": f"1. Test business rule enforcement\n2. Verify workflow state transitions\n3. Test dependent resource relationships\n4. Validate business logic calculations\n5. Test workflow permissions and approvals\n6. Verify audit trail creation\n7. Test rollback scenarios if applicable",
                "expected_results": "Business rules correctly enforced; Proper workflow state management; Dependent resources updated correctly; Audit trails created",
                "test_data": "Business workflow scenarios, state transition data, dependent resource relationships",
                "tags": "api, functional, workflow, business-logic, state-management"
            },
            {
                "suffix": "FUNC-BOUNDARY",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Functional Boundary Conditions",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} handles functional boundary conditions",
                "category": "Functional",
                "priority": "Medium",
                "test_level": "Integration",
                "risk_level": "Medium",
                "test_steps": f"1. Test with minimum allowed values\n2. Test with maximum allowed values\n3. Test with values just inside boundaries\n4. Test with values just outside boundaries\n5. Test with zero values where applicable\n6. Test with null/empty values for optional fields\n7. Verify consistent boundary behavior",
                "expected_results": "Boundary values handled correctly; Clear responses for out-of-bounds values; Consistent behavior at all boundaries",
                "test_data": "Minimum values, maximum values, boundary edge cases, zero values, null values",
                "tags": "api, functional, boundary-testing, edge-cases, limits"
            },
            {
                "suffix": "SEC-AUTH",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Authentication Required",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} requires proper authentication",
                "category": "Security",
                "priority": "Critical",
                "test_level": "Integration",
                "risk_level": "High",
                "test_steps": f"1. Prepare valid request data for {endpoint['path']}\n2. Send {endpoint['method']} request WITHOUT authentication headers\n3. Verify response status code is 401\n4. Validate error message indicates authentication required\n5. Ensure no sensitive data is returned\n6. Verify proper WWW-Authenticate header is returned",
                "expected_results": "Status code: 401 Unauthorized; Error message indicates authentication required; No sensitive data in response; Proper security headers present",
                "test_data": "Valid request data but no authentication token",
                "tags": "api, security, authentication, negative, unauthorized"
            },
            {
                "suffix": "SEC-AUTHZ",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Authorization Check",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} checks user permissions",
                "category": "Security",
                "priority": "Critical",
                "test_level": "Integration",
                "risk_level": "High",
                "test_steps": f"1. Prepare valid request data for {endpoint['path']}\n2. Use authentication token with insufficient permissions\n3. Send {endpoint['method']} request to {endpoint['path']}\n4. Verify response status code is 403\n5. Validate error message indicates insufficient permissions\n6. Ensure no unauthorized data access occurs",
                "expected_results": "Status code: 403 Forbidden; Error message indicates insufficient permissions; No unauthorized data returned",
                "test_data": "Valid request data with low-privilege authentication token",
                "tags": "api, security, authorization, negative, forbidden"
            },
            {
                "suffix": "ERR-NOTFOUND",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Resource Not Found",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} handles non-existent resources",
                "category": "Error Handling",
                "priority": "Medium",
                "test_level": "Integration",
                "risk_level": "Low",
                "test_steps": f"1. Prepare request for non-existent resource in {endpoint['path']}\n2. Set up proper authentication headers\n3. Send {endpoint['method']} request to non-existent resource\n4. Verify response status code is 404\n5. Validate error message is user-friendly\n6. Ensure no system errors occur",
                "expected_results": "Status code: 404 Not Found; User-friendly error message; No system errors or stack traces exposed",
                "test_data": "Request parameters pointing to non-existent resources",
                "tags": "api, error-handling, negative, not-found"
            },
            {
                "suffix": "ERR-INVALID",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Invalid Input Data",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} handles invalid input correctly",
                "category": "Error Handling",
                "priority": "Medium",
                "test_level": "Integration",
                "risk_level": "Medium",
                "test_steps": f"1. Prepare INVALID request data for {endpoint['path']}\n2. Set up proper authentication headers\n3. Send {endpoint['method']} request with invalid data\n4. Verify response status code is 400\n5. Validate error message provides helpful information\n6. Ensure system remains stable\n7. Check that partial data is not processed",
                "expected_results": "Status code: 400 Bad Request; Clear error message indicating validation failures; System remains stable; No partial processing of invalid data",
                "test_data": "Invalid input parameters (wrong data types, missing required fields, malformed data)",
                "tags": "api, error-handling, negative, validation, bad-request"
            },
            {
                "suffix": "EDGE-BOUNDARY",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Boundary Values",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} handles boundary conditions correctly",
                "category": "Edge Cases",
                "priority": "Medium",
                "test_level": "Integration",
                "risk_level": "Medium",
                "test_steps": f"1. Prepare boundary value test data (min/max lengths, numbers)\n2. Set up proper authentication headers\n3. Send {endpoint['method']} request with boundary values\n4. Verify response behavior at limits\n5. Test empty strings, null values, zero values\n6. Validate proper error handling for out-of-range values",
                "expected_results": "Proper handling of boundary conditions; Clear validation messages for out-of-range values; No system crashes or unexpected behavior",
                "test_data": "Minimum/maximum values, empty strings, null values, edge case inputs",
                "tags": "api, edge-cases, boundary, validation"
            },
            {
                "suffix": "SEC-CONTENT",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Content Type Validation",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} validates content types correctly",
                "category": "Security",
                "priority": "Medium",
                "test_level": "Integration",
                "risk_level": "Medium",
                "test_steps": f"1. Prepare valid request data\n2. Set up proper authentication headers\n3. Send {endpoint['method']} request with wrong Content-Type header\n4. Try XML data with JSON Content-Type\n5. Send request without Content-Type header\n6. Verify proper rejection of unsupported content types",
                "expected_results": "Status code: 415 Unsupported Media Type for wrong content types; Clear error messages; No processing of malformed content",
                "test_data": "Valid data with incorrect Content-Type headers (text/xml, text/plain, etc.)",
                "tags": "api, security, content-type, validation, negative"
            },
            {
                "suffix": "PERF-LOAD",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Load Testing",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} performs well under expected load",
                "category": "Performance",
                "priority": "Medium",
                "test_level": "System",
                "risk_level": "Medium",
                "test_steps": f"1. Prepare valid request data for {endpoint['path']}\n2. Set up load testing tool (e.g., JMeter, Artillery)\n3. Configure 10 concurrent users for 5 minutes\n4. Send continuous {endpoint['method']} requests to {endpoint['path']}\n5. Monitor response times and error rates\n6. Verify system remains stable under normal load",
                "expected_results": "Average response time < 2 seconds; 95th percentile < 5 seconds; Error rate < 1%; System remains stable; No memory leaks or resource exhaustion",
                "test_data": "Valid test data set for normal load simulation",
                "tags": "api, performance, load-testing, non-functional"
            },
            {
                "suffix": "PERF-STRESS",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Stress Testing",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} behavior beyond normal capacity",
                "category": "Performance",
                "priority": "Medium",
                "test_level": "System",
                "risk_level": "High",
                "test_steps": f"1. Prepare valid request data for {endpoint['path']}\n2. Set up stress testing configuration\n3. Gradually increase load from 50 to 200 concurrent users\n4. Continue until response times degrade significantly\n5. Monitor system behavior at breaking point\n6. Verify graceful degradation and recovery",
                "expected_results": "System degrades gracefully; No data corruption; Error messages are appropriate; System recovers after load reduction",
                "test_data": "High volume test data for stress conditions",
                "tags": "api, performance, stress-testing, non-functional, breaking-point"
            },
            {
                "suffix": "PERF-SPIKE",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Spike Testing",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} handles sudden traffic spikes",
                "category": "Performance",
                "priority": "Medium",
                "test_level": "System",
                "risk_level": "Medium",
                "test_steps": f"1. Start with normal load baseline (5 users)\n2. Suddenly spike to 100 concurrent users\n3. Monitor system response to sudden load increase\n4. Return to normal load\n5. Repeat spike pattern multiple times\n6. Verify system stability during spikes",
                "expected_results": "System handles traffic spikes without crashes; Response times recover quickly; No permanent performance degradation",
                "test_data": "Burst traffic simulation data",
                "tags": "api, performance, spike-testing, non-functional, traffic-burst"
            },
            {
                "suffix": "RELI-TIMEOUT",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Timeout Handling",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} handles timeouts gracefully",
                "category": "Reliability",
                "priority": "Medium",
                "test_level": "Integration",
                "risk_level": "Medium",
                "test_steps": f"1. Configure client with short timeout (1 second)\n2. Send {endpoint['method']} request to {endpoint['path']}\n3. If response takes longer, verify timeout behavior\n4. Test with various timeout values\n5. Verify no hanging connections\n6. Check proper error messages",
                "expected_results": "Proper timeout exception thrown; Clear error messages; No resource leaks; Connection properly closed",
                "test_data": "Normal request data with timeout constraints",
                "tags": "api, reliability, timeout, non-functional, resilience"
            },
            {
                "suffix": "RELI-RETRY",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Retry Mechanism",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} retry behavior on failures",
                "category": "Reliability",
                "priority": "Medium",
                "test_level": "Integration",
                "risk_level": "Medium",
                "test_steps": f"1. Simulate network failures or 5xx errors\n2. Configure retry mechanism with exponential backoff\n3. Send {endpoint['method']} request to {endpoint['path']}\n4. Verify retry attempts are made\n5. Check backoff timing is appropriate\n6. Ensure eventual success or proper failure",
                "expected_results": "Appropriate retry attempts made; Exponential backoff implemented; Circuit breaker pattern if applicable; Final success or clear failure",
                "test_data": "Request data for retry scenario testing",
                "tags": "api, reliability, retry, non-functional, resilience, circuit-breaker"
            },
            {
                "suffix": "SCALE-CONCURRENT",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Concurrent Users",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} handles multiple concurrent users",
                "category": "Scalability",
                "priority": "Medium",
                "test_level": "System",
                "risk_level": "Medium",
                "test_steps": f"1. Set up test with 50-500 concurrent users\n2. Each user sends {endpoint['method']} requests continuously\n3. Monitor response times across all users\n4. Check for race conditions or data inconsistency\n5. Verify resource utilization scales appropriately\n6. Test connection pooling effectiveness",
                "expected_results": "Linear or acceptable response time scaling; No race conditions; Data consistency maintained; Resource usage scales predictably",
                "test_data": "Concurrent user simulation data with unique identifiers",
                "tags": "api, scalability, concurrent-users, non-functional, race-conditions"
            },
            {
                "suffix": "COMPAT-VERSIONS",
                "title": f"Test {endpoint['method']} {endpoint['path']} - API Version Compatibility",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} works across API versions",
                "category": "Compatibility",
                "priority": "Low",
                "test_level": "Integration",
                "risk_level": "Low",
                "test_steps": f"1. Test with different API version headers\n2. Send {endpoint['method']} request with v1, v2 headers\n3. Verify backward compatibility\n4. Check deprecated endpoint warnings\n5. Validate response format consistency\n6. Test version negotiation",
                "expected_results": "Backward compatibility maintained; Proper version handling; Clear deprecation warnings; Consistent response formats",
                "test_data": "Version-specific request data and headers",
                "tags": "api, compatibility, versioning, non-functional, backward-compatibility"
            },
            {
                "suffix": "SEC-ENCRYPTION",
                "title": f"Test {endpoint['method']} {endpoint['path']} - Data Encryption",
                "description": f"Verify {endpoint['method']} request to {endpoint['path']} uses proper encryption",
                "category": "Security",
                "priority": "High",
                "test_level": "Integration",
                "risk_level": "High",
                "test_steps": f"1. Verify HTTPS is enforced (no HTTP allowed)\n2. Check TLS version is 1.2 or higher\n3. Validate SSL certificate\n4. Test cipher suite strength\n5. Verify sensitive data is encrypted in transit\n6. Check for proper security headers",
                "expected_results": "Only HTTPS connections allowed; Strong TLS version used; Valid SSL certificate; Strong cipher suites; Security headers present (HSTS, etc.)",
                "test_data": "Requests over HTTP vs HTTPS with sensitive data",
                "tags": "api, security, encryption, tls, https, non-functional"
            }
                 ]
        
        # Add intelligent workflow test cases if enabled
        if any("WORKFLOW" in suffix for suffix in enabled_suffixes):
            workflow_test_cases = generate_workflow_test_cases(
                endpoint, test_plan_intelligence, api_relationships, endpoints
            )
            all_test_case_types.extend(workflow_test_cases)
        
        # Filter test case types based on configuration
        test_case_types = [tc for tc in all_test_case_types if tc["suffix"] in enabled_suffixes]
        
        for test_type in test_case_types:
            test_case = {
                "test_case_id": f"TC-{endpoint_tag}-{test_type['suffix']}-{test_case_id:03d}",
                "test_suite": f"{endpoint_tag} {test_type['category']} Tests",
                "title": test_type["title"],
                "description": test_type["description"],
                "category": test_type["category"],
                "priority": test_type["priority"],
                "test_level": test_type["test_level"],
                "risk_level": test_type["risk_level"],
                "automation_candidate": "Yes",
                "api_method": endpoint['method'],
                "api_path": endpoint['path'],
                "operation_id": endpoint.get('operationId', ''),
                "api_summary": endpoint.get('summary', ''),
                "preconditions": "API server is running and accessible",
                "test_steps": test_type["test_steps"],
                "expected_results": test_type["expected_results"],
                "test_data": test_type["test_data"],
                "post_conditions": "System state remains consistent",
                "dependencies": "Authentication service, Database connection, API service",
                "tags": test_type["tags"],
                "estimated_duration": "5 minutes",
                "author": "Test Case Generator",
                "creation_date": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "status": "Draft",
                "execution_notes": "",
                "bug_references": ""
            }
            test_cases_list.append(test_case)
            test_case_id += 1
    
    return test_cases_list

@mcp.tool("generate_test_cases")
async def generate_test_cases(input_dir: str, ctx: Context) -> dict:
    """
    Generates comprehensive test cases in Excel format from OpenAPI specification.
    
    Args:
        input_dir (str): Input directory containing OpenAPI specification
        ctx (Context): MCP context for logging
        
    Returns:
        dict: Result containing generated test cases statistics or error message
    """
    try:
        await ctx.info("Starting Excel test case generation from OpenAPI specification...")
        
        # Step 1: Load test configuration
        config = load_test_config()
        current_profile = config.get("current_profile", "default")
        await ctx.info(f"Loaded test configuration with profile: {current_profile}")
        
        # Step 2: Read OpenAPI specification from input directory
        openapi_path = os.path.join(input_dir, "openapi.json")
        if not os.path.exists(openapi_path):
            return {"error": f"OpenAPI specification not found at: {openapi_path}"}
        
        openapi_spec = read_openapi_spec(openapi_path)
        await ctx.info("OpenAPI specification loaded successfully")
        
        # Step 3: Extract API endpoints
        endpoints = []
        paths = openapi_spec.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoints.append({
                        "path": path,
                        "method": method.upper(),
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "operationId": details.get("operationId", ""),
                        "parameters": details.get("parameters", []),
                        "responses": details.get("responses", {}),
                        "tags": details.get("tags", [])
                    })
        
        await ctx.info(f"Found {len(endpoints)} API endpoints to generate test cases for")
        
        # Step 4: Generate test cases based on configuration
        test_cases_list = generate_comprehensive_test_cases(endpoints, openapi_spec, config)
        enabled_suffixes = get_enabled_test_suffixes(config)
        
        # Log workflow intelligence usage
        workflow_enabled = any("WORKFLOW" in suffix for suffix in enabled_suffixes)
        if workflow_enabled:
            await ctx.info(f"✨ Workflow intelligence enabled - analyzing test plan and API relationships")
            await ctx.info(f"📋 Test plan analysis: Found business context and workflow patterns")
            await ctx.info(f"🔗 API relationship analysis: Identifying CRUD workflows and sequences")
        
        await ctx.info(f"Generated {len(test_cases_list)} test cases using config profile '{current_profile}' with test types: {', '.join(enabled_suffixes)}")
        
        # Step 5: Create Excel file with multiple sheets
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "test_cases.xlsx")
        
        # Create DataFrames
        df_test_cases = pd.DataFrame(test_cases_list)
        
        # Create metadata DataFrame
        metadata_data = {
            'Property': [
                'Generated Date',
                'Total Test Cases',
                'Total API Endpoints',
                'Test Categories',
                'Priority Distribution',
                'Automation Candidates',
                'Generator Version',
                'Input Source',
                'API Title',
                'API Version'
            ],
            'Value': [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                len(test_cases_list),
                len(endpoints),
                ', '.join(df_test_cases['category'].unique()),
                f"Critical: {len(df_test_cases[df_test_cases['priority'] == 'Critical'])}, High: {len(df_test_cases[df_test_cases['priority'] == 'High'])}, Medium: {len(df_test_cases[df_test_cases['priority'] == 'Medium'])}",
                f"{len(df_test_cases[df_test_cases['automation_candidate'] == 'Yes'])} out of {len(test_cases_list)}",
                "2.0 (Excel Direct Generation)",
                f"OpenAPI Specification from {input_dir}",
                openapi_spec.get('info', {}).get('title', 'Unknown API'),
                openapi_spec.get('info', {}).get('version', 'Unknown')
            ]
        }
        df_metadata = pd.DataFrame(metadata_data)
        
        # Create API endpoints summary DataFrame
        endpoints_summary = []
        for endpoint in endpoints:
            test_cases_for_endpoint = [tc for tc in test_cases_list if tc['api_path'] == endpoint['path'] and tc['api_method'] == endpoint['method']]
            endpoints_summary.append({
                'Method': endpoint['method'],
                'Path': endpoint['path'],
                'Operation ID': endpoint.get('operationId', ''),
                'Summary': endpoint.get('summary', ''),
                'Description': endpoint.get('description', ''),
                'Tags': ', '.join(endpoint.get('tags', [])),
                'Parameters Count': len(endpoint.get('parameters', [])),
                'Response Codes': ', '.join(endpoint.get('responses', {}).keys()),
                'Test Cases Generated': len(test_cases_for_endpoint)
            })
        df_endpoints = pd.DataFrame(endpoints_summary)
        
        # Create test execution tracking sheet
        execution_tracking = []
        for tc in test_cases_list:
            execution_tracking.append({
                'Test Case ID': tc['test_case_id'],
                'Title': tc['title'],
                'Priority': tc['priority'],
                'Category': tc['category'],
                'Status': 'Not Executed',
                'Execution Date': '',
                'Executed By': '',
                'Result': '',
                'Actual vs Expected': '',
                'Bugs Found': '',
                'Notes': ''
            })
        df_execution = pd.DataFrame(execution_tracking)
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Test Cases Sheet (detailed)
            df_test_cases.to_excel(writer, sheet_name='Test Cases', index=False)
            
            # Test Execution Tracking Sheet
            df_execution.to_excel(writer, sheet_name='Test Execution', index=False)
            
            # Metadata Sheet
            df_metadata.to_excel(writer, sheet_name='Metadata', index=False)
            
            # API Endpoints Sheet
            df_endpoints.to_excel(writer, sheet_name='API Endpoints', index=False)
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        await ctx.info(f"Excel test cases saved to {output_file}")
        
        # Calculate statistics
        statistics = {
            "total_test_suites": len(df_test_cases['test_suite'].unique()),
            "total_test_cases": len(test_cases_list),
            "api_endpoints_analyzed": len(endpoints),
            "output_format": "excel",
            "categories": df_test_cases['category'].value_counts().to_dict(),
            "priorities": df_test_cases['priority'].value_counts().to_dict(),
            "automation_candidates": len(df_test_cases[df_test_cases['automation_candidate'] == 'Yes']),
            "sheets_created": ["Test Cases", "Test Execution", "Metadata", "API Endpoints"]
        }
        
        return {
            "success": True,
            "output_file": output_file,
            "statistics": statistics,
            "message": f"Successfully generated {len(test_cases_list)} test cases for {len(endpoints)} API endpoints in Excel format"
        }
        
    except Exception as e:
        await ctx.error(f"Error generating Excel test cases: {str(e)}")
        return {"error": f"Failed to generate Excel test cases: {str(e)}"}

@mcp.tool("show_test_config")
async def show_test_config(ctx: Context) -> dict:
    """
    Shows the current test configuration and available profiles.
    
    Returns:
        dict: Current configuration settings and available options
    """
    try:
        await ctx.info("Loading test configuration...")
        
        config = load_test_config()
        enabled_suffixes = get_enabled_test_suffixes(config)
        
        # Count test cases that will be generated
        total_tests_per_endpoint = len(enabled_suffixes)
        
        current_profile = config.get("current_profile", "individual")
        
        result = {
            "success": True,
            "current_profile": current_profile,
            "enabled_test_types": [],
            "enabled_test_suffixes": enabled_suffixes,
            "tests_per_endpoint": total_tests_per_endpoint,
            "available_profiles": {},
            "configuration_file": "config/test_config.json"
        }
        
        # Get enabled test types
        if current_profile in config.get("predefined_profiles", {}):
            profile = config["predefined_profiles"][current_profile]
            result["profile_description"] = profile["description"]
            result["enabled_test_types"] = profile["enabled_types"]
        else:
            # Individual settings
            for test_type, type_config in config.get("enabled_test_types", {}).items():
                if type_config.get("enabled", False):
                    result["enabled_test_types"].append({
                        "type": test_type,
                        "description": type_config.get("description", ""),
                        "priority": type_config.get("priority", ""),
                        "tests": type_config.get("tests", [])
                    })
        
        # Get available profiles
        for profile_name, profile_data in config.get("predefined_profiles", {}).items():
            profile_test_count = 0
            for test_type in profile_data["enabled_types"]:
                type_config = config["enabled_test_types"].get(test_type, {})
                profile_test_count += len(type_config.get("tests", []))
            
            result["available_profiles"][profile_name] = {
                "description": profile_data["description"],
                "enabled_types": profile_data["enabled_types"],
                "tests_per_endpoint": profile_test_count
            }
        
        return result
        
    except Exception as e:
        await ctx.error(f"Error showing test config: {str(e)}")
        return {"error": f"Failed to show test config: {str(e)}"}

@mcp.tool("switch_test_profile")
async def switch_test_profile(profile_name: str, ctx: Context) -> dict:
    """
    Switches to a different test profile.
    
    Args:
        profile_name (str): Name of the profile to switch to
        
    Returns:
        dict: Result of the profile switch operation
    """
    try:
        await ctx.info(f"Switching to test profile: {profile_name}")
        
        config_path = "config/test_config.json"
        config = load_test_config(config_path)
        
        # Check if profile exists
        if profile_name not in config.get("predefined_profiles", {}):
            available_profiles = list(config.get("predefined_profiles", {}).keys())
            return {
                "error": f"Profile '{profile_name}' not found. Available profiles: {', '.join(available_profiles)}"
            }
        
        # Update config
        config["current_profile"] = profile_name
        
        # Save config
        os.makedirs("config", exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2, ensure_ascii=False)
        
        # Get new settings
        enabled_suffixes = get_enabled_test_suffixes(config)
        profile_data = config["predefined_profiles"][profile_name]
        
        return {
            "success": True,
            "switched_to": profile_name,
            "description": profile_data["description"],
            "enabled_types": profile_data["enabled_types"],
            "enabled_test_suffixes": enabled_suffixes,
            "tests_per_endpoint": len(enabled_suffixes),
            "message": f"Successfully switched to profile '{profile_name}'. Next test generation will use these settings."
        }
        
    except Exception as e:
        await ctx.error(f"Error switching test profile: {str(e)}")
        return {"error": f"Failed to switch test profile: {str(e)}"}

if __name__ == "__main__":
    mcp.run() 