# 0. Import necessary libraries and set up environment variables
# ---------------------------------------------------------------------
# This example demonstrates Agent Orchestration using Azure AI Foundry.
# Agent Orchestration allows multiple specialized agents to work together to solve complex problems.
# Unlike single agents, orchestration provides:
#   - Multiple agents with specialized roles and capabilities
#   - Automatic coordination between agents
#   - ConnectedAgentTool for agent-to-agent communication
#   - Centralized triage and task distribution
#   - Scalable architecture for complex workflows
# ---------------------------------------------------------------------
import os
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ConnectedAgentTool, MessageRole, ListSortOrder, ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# 1. Environment Variables Setup
# ---------------------------------------------------------------------
# Azure AI Foundry Agent Orchestration requires:
# - AI_FOUNDRY_ENDPOINT: Your Azure AI Foundry project endpoint
# - AI_FOUNDRY_DEPLOYMENT_NAME: The model deployment you want to use
#
# Agent Orchestration enables:
#   - Multiple specialized agents working in concert
#   - Automatic task distribution and coordination
#   - Scalable agent-based architectures
#   - Complex workflow management with minimal code
# ---------------------------------------------------------------------
azure_foundry_project_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
azure_foundry_deployment = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME")

# 2. Authentication and Client Setup
# ---------------------------------------------------------------------
# AgentsClient is specialized for managing multiple agents and their interactions.
# Unlike AIProjectClient (used for single agents), AgentsClient provides:
#   - Multi-agent coordination capabilities
#   - ConnectedAgentTool for inter-agent communication
#   - Simplified orchestration workflows
#   - Built-in agent lifecycle management
# ---------------------------------------------------------------------
agents_client = AgentsClient(
     endpoint=azure_foundry_project_endpoint,
     credential=DefaultAzureCredential()
)

# 3. Create Specialized Agents for Different Functions
# ---------------------------------------------------------------------
# In Agent Orchestration, we create multiple specialized agents, each with a specific role.
# This approach follows the "separation of concerns" principle:
#   - Each agent has a single, well-defined responsibility
#   - Agents can be optimized for their specific task
#   - The system is more maintainable and scalable
#   - Individual agents can be updated without affecting others
# 
# We'll create three specialized agents for support ticket triage:
#   1. Priority Agent: Assesses urgency levels
#   2. Team Agent: Determines appropriate team assignment
#   3. Effort Agent: Estimates work complexity
# ---------------------------------------------------------------------

# Create an agent to prioritize support tickets
priority_agent = agents_client.create_agent(
     model=azure_foundry_deployment,
     name="priority_agent",
     instructions="""
Assess how urgent a ticket is based on its description.

Respond with one of the following levels:
- High: User-facing or blocking issues
- Medium: Time-sensitive but not breaking anything
- Low: Cosmetic or non-urgent tasks

Only output the urgency level and a very brief explanation.
"""
)

# Create an agent to assign tickets to the appropriate team
team_agent = agents_client.create_agent(
     model=azure_foundry_deployment,
     name="team_agent",
     instructions="""
Decide which team should own each ticket.

Choose from the following teams:
- Frontend
- Backend
- Infrastructure
- Marketing

Base your answer on the content of the ticket. Respond with the team name and a very brief explanation.
"""
)

# Create an agent to estimate effort for a support ticket
effort_agent = agents_client.create_agent(
     model=azure_foundry_deployment,
     name="effort_agent",
     instructions="""
Estimate how much work each ticket will require.

Use the following scale:
- Small: Can be completed in a day
- Medium: 2-3 days of work
- Large: Multi-day or cross-team effort

Base your estimate on the complexity implied by the ticket. Respond with the effort level and a brief justification.
"""
)

# 4. Create ConnectedAgentTool Instances 
# ---------------------------------------------------------------------
# ConnectedAgentTool is a key concept in Agent Orchestration that allows:
#   - One agent to invoke another agent as a tool
#   - Seamless communication between specialized agents
#   - Automatic result passing and context sharing
#   - Building complex workflows from simple agent interactions
#
# Each ConnectedAgentTool wraps an existing agent and makes it available
# as a tool that other agents can call, similar to function calling but
# with the full power of an AI agent behind each "function".
# ---------------------------------------------------------------------

# Create connected agent tools for the support agents
priority_agent_tool = ConnectedAgentTool(
     id=priority_agent.id, 
     name=priority_agent.name, 
     description="Assess the priority of a ticket"
)
    
team_agent_tool = ConnectedAgentTool(
     id=team_agent.id, 
     name=team_agent.name, 
     description="Determines which team should take the ticket"
)
    
effort_agent_tool = ConnectedAgentTool(
     id=effort_agent.id, 
     name=effort_agent.name, 
     description="Determines the effort required to complete the ticket"
)

# 5. Create the Master Orchestration Agent
# ---------------------------------------------------------------------
# The triage agent acts as the orchestrator, coordinating all specialized agents.
# This agent demonstrates the orchestration pattern:
#   - Receives the complex task (ticket triage)
#   - Determines which specialized agents to call
#   - Coordinates the sequence of agent interactions
#   - Combines results into a comprehensive response
#
# Note how we use .definitions[0] to extract the tool definition from each
# ConnectedAgentTool - this makes the specialized agents available as tools
# that the triage agent can call during its processing.
# ---------------------------------------------------------------------

# Create an agent to triage support ticket processing by using connected agents
triage_agent = agents_client.create_agent(
     model=azure_foundry_deployment,
     name="triage-agent",
     instructions="""
Triage the given ticket. Use the connected tools to determine the ticket's priority, 
which team it should be assigned to, and how much effort it may take.
""",
     tools=[
         priority_agent_tool.definitions[0],
         team_agent_tool.definitions[0],
         effort_agent_tool.definitions[0]
     ]
)

# 6. Execute the Agent Orchestration Workflow
# ---------------------------------------------------------------------
# This section demonstrates how to use the orchestrated agents:
#   1. Create a conversation thread for the interaction
#   2. Get user input for the support ticket
#   3. Send the ticket to the triage agent
#   4. The triage agent automatically coordinates with specialized agents
#   5. Display the comprehensive triage results
#
# The power of orchestration is that the complex coordination happens automatically.
# The triage agent will call the appropriate specialized agents as needed,
# and we get a complete analysis without manually managing the workflow.
# ---------------------------------------------------------------------

# Use the agents to triage a support issue
print("Creating agent thread.")
thread = agents_client.threads.create()  

# Create the ticket prompt
prompt = input("\nWhat's the support problem you need to resolve?: ")
    
# Send a prompt to the agent
message = agents_client.messages.create(
     thread_id=thread.id,
     role=MessageRole.USER,
     content=prompt,
)   
    
# Run the thread using the primary agent
# create_and_process() is a convenience method that:
#   - Creates a run with the specified agent
#   - Automatically processes any tool calls (including ConnectedAgentTool calls)
#   - Handles the orchestration workflow without manual intervention
#   - Returns when the entire orchestration is complete
print("\nProcessing agent thread. Please wait.")
run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=triage_agent.id)
        
if run.status == "failed":
     print(f"Run failed: {run.last_error}")

# Fetch and display messages
# The results will show the coordinated output from all agents involved in the triage
messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
for message in messages:
     if message.text_messages:
         last_msg = message.text_messages[-1]
         print(f"{message.role}:\n{last_msg.text.value}\n")