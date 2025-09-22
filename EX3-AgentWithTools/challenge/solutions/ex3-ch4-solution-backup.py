# Import necessary libraries

from concurrent.futures import thread
import os, time
import jsonref
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    ToolApproval,
    FunctionTool,
    OpenApiTool, 
    OpenApiAnonymousAuthDetails
)
from dotenv import load_dotenv

load_dotenv()

azure_foundry_project_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
azure_foundry_deployment = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME")

########### FIRST AGENT TOOL DEFINITION - FUNCTION TOOL ###########
# Create the function to be used by the FunctionTool
def analyze_code_metrics(repo_data):
    """
    Analyzes basic repository metrics from GitHub API response
    
    Args:
        repo_data (dict): Repository information from GitHub API
        
    Returns:
        dict: Analysis results with complexity metrics
    """
    
    if not repo_data:
        return {"error": "No repository data provided"}
    
    # Extract key metrics from GitHub API response
    language = repo_data.get("language", "Unknown")
    size_kb = repo_data.get("size", 0)
    stars = repo_data.get("stargazers_count", 0)
    forks = repo_data.get("forks_count", 0)
    issues = repo_data.get("open_issues_count", 0)
    
    # Calculate derived metrics
    if size_kb < 1000:
        project_size = "Small"
    elif size_kb < 10000:
        project_size = "Medium"
    else:
        project_size = "Large"
        
    if stars < 100:
        popularity = "Low"
    elif stars < 1000:
        popularity = "Medium"
    else:
        popularity = "High"
        
    activity_level = "Active" if issues > 10 else "Moderate" if issues > 0 else "Low"
    
    return {
        "main_language": language,
        "project_size": project_size,
        "popularity_level": popularity,
        "activity_level": activity_level,
        "repository_size_kb": size_kb,
        "stars": stars,
        "forks": forks,
        "open_issues": issues,
        "complexity_summary": f"{project_size} {language} project with {popularity.lower()} popularity"
    }

# Creating objects user_function and function_tool
# Define user functions
user_functions = {analyze_code_metrics}

# Initialize the FunctionTool with user-defined functions
functions = FunctionTool(functions=user_functions)

########### SECOND AGENT TOOL DEFINITION - OPENAPI TOOL ###########
# Load the OpenAPI specification for GitHub repositories API
openapi_file_path = os.path.join(os.path.dirname(__file__), "../gitHubOpenApidef.json")
with open(openapi_file_path, "r") as f:
    openapi_inventory = jsonref.loads(f.read())

print(f"✅ Loaded OpenAPI spec from: {openapi_file_path}")
print(f"🌐 Target API: {openapi_inventory['servers'][0]['url']}")

# Initialize the main OpenAPI tool definition for GitHub repositories
openapi_tool = OpenApiTool(
    name="RepositoryFinder",
    spec=openapi_inventory,
    description="Access real GitHub repository data including issues, pull requests, and branches. Use this to retrieve repository information, check issue status, find pull requests by author, and generate repository insights.",
    auth=OpenApiAnonymousAuthDetails()
)

########### THIRD AGENT TOOL DEFINITION - MCP TOOL ###########
# Get MCP server configuration from environment variables or Fixed values
mcp_server_url = "https://learn.microsoft.com/api/mcp"
mcp_server_label = "MicrosoftLean"

# Initialize agent MCP tool
mcp_tool = McpTool(
    server_label=mcp_server_label,
    server_url=mcp_server_url,
    allowed_tools=[],  # Optional: specify allowed tools
)

############ COMMON CLIENT CREATION ###########
project_client = AIProjectClient(
    endpoint=azure_foundry_project_endpoint,
    credential=DefaultAzureCredential(),
)

########### AGENTS CREATION AND MESSAGE SENDING ###########
with project_client:
    agents_client = project_client.agents

    # Create Agent 1 - Function Tool Agent
    agentTool = agents_client.create_agent(
        model=azure_foundry_deployment,
        name="Code Analyst Agent",
        instructions="You are a code analysis specialist. Your job is to analyze GitHub repositories and provide insights about their complexity, size, and characteristics. When given repository data from GitHub API, use the analyze_code_metrics function to provide detailed analysis including project size assessment, programming language identification, popularity and activity metrics, and development recommendations.",
        tools=functions.definitions,
    )
    print(f"Created Agent 1, ID: {agentTool.id}")

    # Create Agent 2 - OpenAPI Tool Agent
    agentOpenAPI = agents_client.create_agent(
        model=azure_foundry_deployment,
        name="GitHub Repository Agent",
        instructions="You are a GitHub repository agent that uses the RepositoryFinder tool to access real GitHub repository data including issues, pull requests, and branches.",
        tools=openapi_tool.definitions,
    )
    print(f"Created Agent 2, ID: {agentOpenAPI.id}")

    # Create Agent 3 - MCP Tool Agent
    agentMCP = agents_client.create_agent(
        model=azure_foundry_deployment,
        name="Microsoft Learn Agent",
        instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
        tools=mcp_tool.definitions,
    )
    print(f"Created Agent 3, ID: {agentMCP.id}")

    # Create thread for communication
    thread1 = agents_client.threads.create()
    print(f"Created thread for Agent 1, ID: {thread1.id}")

    thread2 = agents_client.threads.create()
    print(f"Created thread for Agent 2, ID: {thread2.id}")

    thread3 = agents_client.threads.create()
    print(f"Created thread for Agent 3, ID: {thread3.id}")

    # Create message to thread for Agent 1
    message1 = agents_client.messages.create(
        thread_id=thread1.id,
        role="user",
        content="""Analyze this repository data: {
            "name": "chainlit-azure-openai", 
            "language": "Python",
            "size": 2500,
            "stargazers_count": 150,
            "forks_count": 25,
            "open_issues_count": 8
        }""",
    )
    print(f"Created message for Agent 1, ID: {message1.id}")

    # Create message to thread for Agent 2
    message2 = agents_client.messages.create(
        thread_id=thread2.id,
        role="user",
        content="Find repositories related to 'machine learning' on GitHub"
    )
    print(f"Created message for Agent 2, ID: {message2.id}")
    
    # Create message to thread for Agent 3
    message3 = agents_client.messages.create(
        thread_id=thread3.id,
        role="user",
        content="Please help me find Microsoft Learn documentation on Azure Functions and provide code examples.",
    )
    print(f"Created message for Agent 3, ID: {message3.id}")
    
    # Create and process agent run in thread with Function Tool
    run1 = agents_client.runs.create(thread_id=thread1.id, agent_id=agentTool.id)
    
    print(f"Created run for Agent 1, ID: {run1.id}")
    
    while run1.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run1 = agents_client.runs.get(thread_id=thread1.id, run_id=run1.id)
        
        # Handle function call approval for Agent 1
        if run1.status == "requires_action":
            print("Agent 1 requires action - processing function call")
            
            # Get the required action details
            required_action = run1.required_action
            tool_calls = required_action.submit_tool_outputs.tool_calls
            
            tool_outputs = []
            for tool_call in tool_calls:
                if tool_call.function.name == "analyze_code_metrics":
                    # Parse the function arguments
                    import json
                    args = json.loads(tool_call.function.arguments)
                    
                    # Get repo_data and ensure it's a dictionary
                    repo_data = args.get("repo_data", {})
                    
                    # If repo_data is a string, try to parse it as JSON
                    if isinstance(repo_data, str):
                        try:
                            repo_data = json.loads(repo_data)
                        except json.JSONDecodeError:
                            # If it's not valid JSON, create a default structure
                            repo_data = {"error": "Invalid repo data format"}
                    
                    # Call our function with the parsed arguments
                    result = analyze_code_metrics(repo_data)
                    
                    # Add the result to tool outputs
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result)
                    })
            
            # Submit the tool outputs
            if tool_outputs:
                run1 = agents_client.runs.submit_tool_outputs(
                    thread_id=thread1.id, 
                    run_id=run1.id, 
                    tool_outputs=tool_outputs
                )
        
        print(f"Current run status for Agent 1: {run1.status}")
    print(f"Final run status for Agent 1: {run1.status}")
    
    if run1.status == "completed":
        # Get the messages from the thread to see the response
        messages = agents_client.messages.list(thread_id=thread1.id)
        for message in messages:
            if message.role == "assistant":
                print(f"Agent 1 Response: {message.content}")
                break
    else:
        print("Run for Agent 1 did not complete successfully.")
        
    # Create and process agent run in thread with OpenAPI Tool
    run2 = agents_client.runs.create(thread_id=thread2.id, agent_id=agentOpenAPI.id)
    print(f"Created run for Agent 2, ID: {run2.id}")
    while run2.status in ["queued", "in_progress"]:
        time.sleep(1)
        run2 = agents_client.runs.get(thread_id=thread2.id, run_id=run2.id)
        print(f"Current run status for Agent 2: {run2.status}")
    print(f"Final run status for Agent 2: {run2.status}")
    
    if run2.status == "completed":
        # Get the messages from the thread to see the response
        messages = agents_client.messages.list(thread_id=thread2.id)
        for message in messages:
            if message.role == "assistant":
                print(f"Agent 2 Response: {message.content}")
                break
    else:
        print("Run for Agent 2 did not complete successfully.")
    
    # Create and process agent run in thread with MCP tools
    run3 = agents_client.runs.create(thread_id=thread3.id, agent_id=agentMCP.id)
    print(f"Created run for Agent 3, ID: {run3.id}")
    
    while run3.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run3 = agents_client.runs.get(thread_id=thread3.id, run_id=run3.id)

        if run3.status == "requires_action" and isinstance(run3.required_action, SubmitToolApprovalAction):
            tool_calls = run3.required_action.submit_tool_approval.tool_calls
            if not tool_calls:
                print("No tool calls provided - cancelling run")
                agents_client.runs.cancel(thread_id=thread3.id, run_id=run3.id)
                break

            tool_approvals = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredMcpToolCall):
                    try:
                        print(f"Approving tool call: {tool_call}")
                        tool_approvals.append(
                            ToolApproval(
                                tool_call_id=tool_call.id,
                                approve=True,
                                headers=mcp_tool.headers,
                            )
                        )
                    except Exception as e:
                        print(f"Error approving tool_call {tool_call.id}: {e}")

            print(f"tool_approvals: {tool_approvals}")
            if tool_approvals:
                agents_client.runs.submit_tool_outputs(
                    thread_id=thread3.id, run_id=run3.id, tool_approvals=tool_approvals
                )

        print(f"Current run status for Agent 3: {run3.status}")
    print(f"Final run status for Agent 3: {run3.status}")
    
    if run3.status == "completed":
        # Get the messages from the thread to see the response
        messages = agents_client.messages.list(thread_id=thread3.id)
        for message in messages:
            if message.role == "assistant":
                print(f"Agent 3 Response: {message.content}")
                break
    else:
        print("Run for Agent 3 did not complete successfully.")

print("✅ All agents have completed their runs!")

