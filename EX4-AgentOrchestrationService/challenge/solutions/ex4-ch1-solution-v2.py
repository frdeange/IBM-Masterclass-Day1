# 0. Import necessary libraries and set up environment variables
# ---------------------------------------------------------------------
# This solution demonstrates Agent Orchestration using Azure AI Foundry.
# Version 2: Using ONLY AgentsClient (following EX4-S1 sample pattern exactly)
# 
# Key difference from v1:
#   - Uses only AgentsClient (no AIProjectClient mixing)
#   - Follows the exact pattern from ex4-s1-FoundryAgentsOrch.py
#   - Simpler tool definitions matching the working sample
# ---------------------------------------------------------------------
import os
import jsonref
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    ConnectedAgentTool, 
    MessageRole, 
    ListSortOrder, 
    FunctionTool,
    OpenApiTool,
    OpenApiAnonymousAuthDetails,
    ResponseFormatJsonSchema,
    ResponseFormatJsonSchemaType,
    McpTool,
    RequiredMcpToolCall,
    SubmitToolApprovalAction,
    ToolApproval
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from a .env file
load_dotenv()

# 1. Environment Variables Setup
# ---------------------------------------------------------------------
# Azure AI Foundry Agent Orchestration requires:
# - AI_FOUNDRY_ENDPOINT: Your Azure AI Foundry project endpoint
# - AI_FOUNDRY_DEPLOYMENT_NAME: The model deployment you want to use
# ---------------------------------------------------------------------
azure_foundry_project_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
azure_foundry_deployment = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME")

# 1.5. Define Pydantic Models for Structured Output (from EX3-CH4)
# ---------------------------------------------------------------------
# These models ensure the GitHub Explorer Agent returns structured data
# that can be processed by the Code Analyst Agent in the orchestration
# ---------------------------------------------------------------------
class GitHubRepo(BaseModel):
    """
    Individual repository information compatible with code analysis.
    Uses same field names as GitHub API for seamless integration.
    """
    name: str                   # Repository name  
    language: str               # Main programming language
    size: int                   # Repository size in KB
    stargazers_count: int       # Number of stars
    forks_count: int            # Number of forks
    open_issues_count: int      # Number of open issues
    html_url: str               # Repository URL

class GitHubReposResponse(BaseModel):
    """
    Complete response structure containing multiple repositories.
    Enables the orchestration to process multiple repositories for analysis.
    """
    repositories: list[GitHubRepo]  # Array of repository objects
    total_found: int                # Total number of repositories found
    query_used: str                 # The search query that was used

# 2. Authentication and Client Setup
# ---------------------------------------------------------------------
# AgentsClient is specialized for managing multiple agents and their interactions.
# Using ONLY AgentsClient (no AIProjectClient) for consistency with EX4-S1 sample.
# ---------------------------------------------------------------------
agents_client = AgentsClient(
     endpoint=azure_foundry_project_endpoint,
     credential=DefaultAzureCredential()
)

# 2.5. Configure GitHub OpenAPI Tool (from EX3-CH4)
# ---------------------------------------------------------------------
# Load the GitHub OpenAPI specification to enable real GitHub repository search
# ---------------------------------------------------------------------
openapi_file_path = os.path.join(os.path.dirname(__file__), "../gitHubOpenApidef.json")
with open(openapi_file_path, "r") as f:
    github_openapi_spec = jsonref.loads(f.read())

print(f"✅ Loaded GitHub OpenAPI spec from: {openapi_file_path}")

# Create OpenAPI tool for GitHub repository search
github_openapi_tool = OpenApiTool(
    name="RepositoryFinder",
    spec=github_openapi_spec,
    description="Access real GitHub repository data including repository information, statistics, and metadata. Use this to search for repositories and retrieve detailed information.",
    auth=OpenApiAnonymousAuthDetails()
)

# 2.6. Configure MCP Tool for Microsoft Learn Documentation (from EX3-CH4)
# ---------------------------------------------------------------------
# MCP (Model Context Protocol) tool for accessing Microsoft Learn documentation
# ---------------------------------------------------------------------
mcp_server_url = "https://learn.microsoft.com/api/mcp"
mcp_server_label = "MicrosoftLean"

# Initialize MCP tool for Microsoft documentation access
microsoft_docs_mcp_tool = McpTool(
    server_label=mcp_server_label,
    server_url=mcp_server_url,
    allowed_tools=[],  # Optional: specify allowed tools
)

print(f"✅ Configured MCP Tool for Microsoft Learn documentation")

# 3. Create Specialized Agents for Development Analysis
# ---------------------------------------------------------------------
# Following the EX4-S1 pattern exactly, we create simple specialized agents
# without complex tool definitions initially. We'll add tools after basic agents work.
# 
# Starting with simple agents to test orchestration pattern first:
#   1. Code Analyst Agent: Analyzes repository complexity (simplified)
#   2. GitHub Explorer Agent: Finds GitHub repositories (simplified)  
#   3. Documentation Expert Agent: Finds Microsoft documentation (simplified)
# ---------------------------------------------------------------------

# Create a simple code analyst agent (no custom functions initially)
code_analyst = agents_client.create_agent(
     model=azure_foundry_deployment,
     name="code_analyst",
     instructions="""
You are a code analysis specialist. 

Analyze GitHub repository information and provide insights about:
- Programming language and technology stack
- Project size and complexity assessment
- Development activity and community engagement
- Quality indicators and recommendations

Provide clear, structured analysis in a professional format.
"""
)

# Create GitHub explorer agent with Structured Output (enhanced from EX3-CH4)
github_explorer = agents_client.create_agent(
     model=azure_foundry_deployment,
     name="github_explorer", 
     instructions="""
You are a GitHub repository specialist that provides structured data about repositories.

When searching for repositories:
1. Find MULTIPLE repositories that match the user's query
2. Include the total count of repositories found
3. Include the original search query used""",
     tools=github_openapi_tool.definitions,
     response_format=ResponseFormatJsonSchemaType(
         json_schema=ResponseFormatJsonSchema(
             name="GitHubReposResponse",
             schema=GitHubReposResponse.model_json_schema()
         )
     )
)

# Create documentation expert agent with MCP Tool (enhanced from EX3-CH4)
documentation_expert = agents_client.create_agent(
     model=azure_foundry_deployment,
     name="documentation_expert",
     instructions="""
You are a technical documentation specialist focused on Microsoft technologies.

Use the available MCP tools to provide comprehensive guidance on:
- Microsoft Azure services and features
- Development frameworks and tools
- Best practices and architectural patterns
- Learning resources and official documentation
- Code examples and implementation guidance

Always use the MCP tools to access the most current and official Microsoft documentation.
Focus on providing accurate, up-to-date information from official Microsoft resources.
""",
     tools=microsoft_docs_mcp_tool.definitions
)

print(f"✅ Created Code Analyst Agent, ID: {code_analyst.id}")
print(f"✅ Created GitHub Explorer Agent, ID: {github_explorer.id}")
print(f"✅ Created Documentation Expert Agent, ID: {documentation_expert.id}")

# 4. Create ConnectedAgentTool Instances 
# ---------------------------------------------------------------------
# ConnectedAgentTool is a key concept in Agent Orchestration that allows:
#   - One agent to invoke another agent as a tool
#   - Seamless communication between specialized agents
#   - Automatic result passing and context sharing
#   - Building complex workflows from simple agent interactions
#
# Following the exact pattern from EX4-S1 sample
# ---------------------------------------------------------------------

# Create connected agent tools for the development agents
code_analyst_tool = ConnectedAgentTool(
     id=code_analyst.id, 
     name=code_analyst.name, 
     description="Analyzes code metrics and complexity of repositories"
)
    
github_explorer_tool = ConnectedAgentTool(
     id=github_explorer.id, 
     name=github_explorer.name, 
     description="Finds and evaluates GitHub repositories related to technologies"
)
    
documentation_expert_tool = ConnectedAgentTool(
     id=documentation_expert.id, 
     name=documentation_expert.name, 
     description="Provides Microsoft documentation and best practices guidance"
)

print(f"✅ Created ConnectedAgentTool wrappers for all specialist agents")

# 5. Create the Master Orchestration Agent
# ---------------------------------------------------------------------
# The master agent acts as the orchestrator, coordinating all specialized agents.
# This agent demonstrates the orchestration pattern:
#   - Receives the complex task (development project analysis)
#   - Determines which specialized agents to call
#   - Coordinates the sequence of agent interactions
#   - Combines results into a comprehensive response
#
# Following the exact pattern from EX4-S1 sample with .definitions[0]
# ---------------------------------------------------------------------

# Create a master agent for development project analysis using connected agents
master_agent = agents_client.create_agent(
     model=azure_foundry_deployment,
     name="master-development-agent",
     instructions="""
You are a master development project analyzer. Use the connected specialist agents to provide comprehensive project analysis.

When analyzing a development project or technology:
1. Use the github_explorer to find relevant repositories and projects
2. Use the code_analyst to analyze the complexity and characteristics of found projects
3. Use the documentation_expert to find official documentation and learning resources

Combine the insights from all specialists into a structured, comprehensive analysis that helps users understand:
- Available projects and their characteristics
- Technical complexity and development considerations  
- Official resources and learning paths

Present your analysis in a clear, organized format.
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
# This section demonstrates how to use the orchestrated agents:
#   1. Create a conversation thread for the interaction
#   2. Get user input for the development analysis
#   3. Send the query to the master agent
#   4. The master agent automatically coordinates with specialized agents
#   5. Display the comprehensive analysis results
#
# Following the exact pattern from EX4-S1 sample
# ---------------------------------------------------------------------

print("\n" + "="*80)
print("🚀 DEVELOPMENT PROJECT ANALYZER - AGENT ORCHESTRATION v2")
print("="*80)
print("Using ONLY AgentsClient pattern (following EX4-S1 sample exactly)")
print("📊 Code Analyst • 🔍 GitHub Explorer • 📚 Documentation Expert")
print("="*80)

# Use the agents to analyze a development project
print("Creating agent thread.")
thread = agents_client.threads.create()  

# Create the analysis prompt
prompt = input("\nWhat development project or technology do you want to analyze?: ")
    
# Send a prompt to the agent
message = agents_client.messages.create(
     thread_id=thread.id,
     role=MessageRole.USER,
     content=prompt,
)   
    
# Run the thread using the master agent
# create_and_process() is a convenience method that:
#   - Creates a run with the specified agent
#   - Automatically processes any tool calls (including ConnectedAgentTool calls)
#   - Handles the orchestration workflow without manual intervention
#   - Returns when the entire orchestration is complete
print("\nProcessing agent thread. Please wait.")
run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=master_agent.id)
        
if run.status == "failed":
     print(f"Run failed: {run.last_error}")

# Fetch and display messages
# The results will show the coordinated output from all agents involved in the analysis
print("\n" + "="*80)
print("📋 ORCHESTRATED ANALYSIS RESULTS")
print("="*80)

messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
for message in messages:
     if message.text_messages:
         last_msg = message.text_messages[-1]
         if message.role == MessageRole.USER:
             print(f"👤 USER QUERY:")
             print(f"   {last_msg.text.value}")
             print()
         elif message.role == "assistant":  # Use string instead of enum
             print(f"🤖 ORCHESTRATED RESPONSE:")
             print(f"   (Coordinated results from all specialist agents)")
             print()
             print(last_msg.text.value)
             print()

print("="*80)
print("✨ Agent Orchestration Complete!")
print("="*80)