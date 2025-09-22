# 0. Import necessary libraries and set up environment variables
# ---------------------------------------------------------------------
# This solution demonstrates Agent Orchestration using Azure AI Foundry.
# It combines the three specialized agents from EX3-CH4 into an orchestrated system
# where a Master Development Agent coordinates all specialists automatically.
# 
# Key orchestration concepts demonstrated:
#   - Reusing existing specialized agents from previous exercises
#   - ConnectedAgentTool for agent-to-agent communication
#   - Single query activating multiple agents in sequence
#   - Unified workflow with comprehensive output
# ---------------------------------------------------------------------
import os, time
import jsonref
import json
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ConnectedAgentTool, MessageRole, ListSortOrder
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    McpTool,
    RequiredMcpToolCall,
    SubmitToolApprovalAction,
    ToolApproval,
    FunctionTool,
    OpenApiTool, 
    OpenApiAnonymousAuthDetails
)
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# 1. Environment Variables Setup
# ---------------------------------------------------------------------
# Azure AI Foundry Agent Orchestration requires:
# - AI_FOUNDRY_ENDPOINT: Your Azure AI Foundry project endpoint
# - AI_FOUNDRY_DEPLOYMENT_NAME: The model deployment you want to use
#
# This solution reuses the three specialized agents from EX3-CH4:
#   - Code Analyst Agent (with FunctionTool)
#   - GitHub Explorer Agent (with OpenApiTool)
#   - Documentation Expert Agent (with McpTool)
# ---------------------------------------------------------------------
azure_foundry_project_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
azure_foundry_deployment = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME")

# 2. Authentication and Client Setup
# ---------------------------------------------------------------------
# AgentsClient is specialized for managing multiple agents and their interactions.
# This client enables ConnectedAgentTool functionality for orchestration.
# ---------------------------------------------------------------------
agents_client = AgentsClient(
     endpoint=azure_foundry_project_endpoint,
     credential=DefaultAzureCredential()
)

# 3. Recreate Specialized Agents from EX3-CH4
# ---------------------------------------------------------------------
# We reuse the exact same three specialized agents from Exercise 3 Challenge 4:
#   1. Code Analyst Agent: Analyzes repository metrics and complexity
#   2. GitHub Explorer Agent: Searches GitHub repositories using OpenAPI
#   3. Documentation Expert Agent: Finds Microsoft Learn documentation using MCP
#
# These agents maintain their original functionality but will now work together
# through orchestration instead of independently.
# ---------------------------------------------------------------------

########### FIRST AGENT - CODE ANALYST WITH FUNCTION TOOL ###########
# Reuse the analyze_code_metrics function from EX3-CH4
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

# Initialize the FunctionTool with the analyze_code_metrics function
user_functions = {analyze_code_metrics}
functions_tool = FunctionTool(functions=user_functions)

# Create Code Analyst Agent (same as EX3-CH4)
code_analyst = agents_client.create_agent(
    model=azure_foundry_deployment,
    name="Code Analyst Agent",
    instructions="You are a code analysis specialist. Your job is to analyze GitHub repositories and provide insights about their complexity, size, and characteristics. When given repository data from GitHub API, use the analyze_code_metrics function to provide detailed analysis including project size assessment, programming language identification, popularity and activity metrics, and development recommendations.",
    tools=functions_tool.definitions,
)
print(f"✅ Created Code Analyst Agent, ID: {code_analyst.id}")

########### SECOND AGENT - GITHUB EXPLORER WITH OPENAPI TOOL ###########
# Load the OpenAPI specification for GitHub repositories API (same as EX3-CH4)
openapi_file_path = os.path.join(os.path.dirname(__file__), "../gitHubOpenApidef.json")
with open(openapi_file_path, "r") as f:
    openapi_inventory = jsonref.loads(f.read())

print(f"✅ Loaded OpenAPI spec from: {openapi_file_path}")
print(f"🌐 Target API: {openapi_inventory['servers'][0]['url']}")

# Initialize the OpenAPI tool for GitHub repositories (same as EX3-CH4)
openapi_tool = OpenApiTool(
    name="RepositoryFinder",
    spec=openapi_inventory,
    description="Access real GitHub repository data including issues, pull requests, and branches. Use this to retrieve repository information, check issue status, find pull requests by author, and generate repository insights.",
    auth=OpenApiAnonymousAuthDetails()
)

# Create GitHub Explorer Agent (same as EX3-CH4)
github_explorer = agents_client.create_agent(
    model=azure_foundry_deployment,
    name="GitHub Repository Agent",
    instructions="You are a GitHub repository agent that uses the RepositoryFinder tool to access real GitHub repository data including issues, pull requests, and branches. Search for repositories based on user queries and provide detailed information about found repositories.",
    tools=openapi_tool.definitions,
)
print(f"✅ Created GitHub Explorer Agent, ID: {github_explorer.id}")

########### THIRD AGENT - DOCUMENTATION EXPERT WITH MCP TOOL ###########
# Initialize MCP tool for Microsoft Learn (same as EX3-CH4)
mcp_server_url = "https://learn.microsoft.com/api/mcp"
mcp_server_label = "MicrosoftLean"

mcp_tool = McpTool(
    server_label=mcp_server_label,
    server_url=mcp_server_url,
    allowed_tools=[],
)

# Create Documentation Expert Agent (same as EX3-CH4)
documentation_expert = agents_client.create_agent(
    model=azure_foundry_deployment,
    name="Microsoft Learn Agent",
    instructions="You are a documentation expert that specializes in finding relevant Microsoft Learn resources. Use the available MCP tools to search for official documentation, tutorials, and best practices related to user queries.",
    tools=mcp_tool.definitions,
)
print(f"✅ Created Documentation Expert Agent, ID: {documentation_expert.id}")

# 4. Create ConnectedAgentTool Instances for Orchestration
# ---------------------------------------------------------------------
# ConnectedAgentTool is the key to orchestration - it wraps each specialized agent
# and makes it available as a tool that the master agent can call.
# This enables seamless agent-to-agent communication and coordination.
# ---------------------------------------------------------------------

# Create connected agent tools for orchestration
code_analyst_tool = ConnectedAgentTool(
    id=code_analyst.id,
    name="code_analyst", 
    description="Analyzes code metrics and complexity of repositories. Provides detailed analysis of project size, programming language, popularity, and development recommendations."
)

github_explorer_tool = ConnectedAgentTool(
    id=github_explorer.id,
    name="github_explorer",
    description="Searches and retrieves information from GitHub repositories. Finds relevant repositories based on technology, language, or topic queries."
)

documentation_expert_tool = ConnectedAgentTool(
    id=documentation_expert.id,
    name="documentation_expert", 
    description="Searches for official Microsoft Learn documentation, tutorials, and best practices related to technologies and development topics."
)

print(f"✅ Created ConnectedAgentTool wrappers for all specialist agents")

# 5. Create the Master Development Agent (Orchestrator)
# ---------------------------------------------------------------------
# The Master Development Agent coordinates all three specialist agents automatically.
# It receives user queries and intelligently decides which specialists to call,
# in what order, and how to combine their results into a comprehensive analysis.
# ---------------------------------------------------------------------

master_agent = agents_client.create_agent(
    model=azure_foundry_deployment,
    name="Master Development Agent",
    instructions="""
You are an expert development project analysis coordinator. Your role is to orchestrate multiple specialist agents to provide comprehensive development project insights.

When you receive a query about a project, technology, or development topic:

1. **Use the github_explorer** to find relevant repositories, projects, and real-world examples
2. **Use the code_analyst** to analyze the complexity, size, and characteristics of found repositories  
3. **Use the documentation_expert** to find official Microsoft documentation, tutorials, and best practices

Always provide a well-structured analysis that includes:
- **Repository Recommendations**: List of relevant repositories with basic information
- **Technical Analysis**: Code complexity, project characteristics, and technical insights
- **Learning Resources**: Official documentation, tutorials, and recommended learning paths
- **Summary**: Key findings and recommendations for the user

Structure your response clearly with sections and make it actionable for developers.
""",
    tools=[
        code_analyst_tool.definitions[0],
        github_explorer_tool.definitions[0], 
        documentation_expert_tool.definitions[0]
    ]
)
print(f"✅ Created Master Development Agent (Orchestrator), ID: {master_agent.id}")

# 6. Execute the Agent Orchestration Workflow
# ---------------------------------------------------------------------
# This section demonstrates the orchestration in action:
#   1. Create a conversation thread
#   2. Get user input about development projects or technologies
#   3. Send the query to the master agent
#   4. The master agent automatically coordinates with all specialists
#   5. Display the comprehensive orchestrated results
# ---------------------------------------------------------------------

print("\n" + "="*80)
print("🚀 DEVELOPMENT PROJECT ANALYZER - AGENT ORCHESTRATION")
print("="*80)
print("This system orchestrates three specialist agents:")
print("📊 Code Analyst • 🔍 GitHub Explorer • 📚 Documentation Expert")
print("="*80)

# Create thread for the orchestrated conversation
thread = agents_client.threads.create()
print(f"✅ Created conversation thread, ID: {thread.id}")

# Get user input for development project analysis
user_query = input("\n🤔 What project or technology do you want to analyze?: ")

# Create message in the thread
message = agents_client.messages.create(
    thread_id=thread.id,
    role=MessageRole.USER,
    content=user_query,
)
print(f"✅ Created user message, ID: {message.id}")

# Execute the orchestrated workflow
# create_and_process() automatically handles:
#   - Agent coordination and sequencing
#   - Tool call approvals and processing
#   - Multi-agent communication
#   - Result aggregation and synthesis
print("\n🔄 Processing orchestrated analysis... (this may take a moment)")
print("   The master agent is coordinating with all specialist agents...")

run = agents_client.runs.create_and_process(
    thread_id=thread.id, 
    agent_id=master_agent.id
)

# Handle the orchestration results
if run.status == "failed":
    print(f"❌ Orchestration failed: {run.last_error}")
else:
    print(f"✅ Orchestration completed successfully!")
    
    # Fetch and display the orchestrated results
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    
    print("\n" + "="*80)
    print("📋 ORCHESTRATED DEVELOPMENT PROJECT ANALYSIS")
    print("="*80)
    
    for message in messages:
        if message.text_messages:
            last_msg = message.text_messages[-1]
            if message.role == MessageRole.USER:
                print(f"👤 USER QUERY:")
                print(f"   {last_msg.text.value}")
                print()
            elif message.role == MessageRole.ASSISTANT:
                print(f"🤖 MASTER AGENT ORCHESTRATED RESPONSE:")
                print(f"   (Coordinated results from Code Analyst + GitHub Explorer + Documentation Expert)")
                print()
                print(last_msg.text.value)
                print()
    
    print("="*80)
    print("✨ Orchestration Complete! All specialist agents worked together seamlessly.")
    print("="*80)