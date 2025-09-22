# EX3-S4: Structured Output with Pydantic Models
# =====================================================
# This sample demonstrates how to create agents that return structured JSON output
# using Pydantic models and ResponseFormatJsonSchema. This is particularly useful 
# when you need consistent, parseable responses from your agents.
#
# Key concepts covered:
# - Pydantic BaseModel for data validation and schema generation
# - ResponseFormatJsonSchema for enforcing output structure
# - OpenAPI tool integration with structured responses
# - Working with complex data structures and arrays

import os
import jsonref
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder, 
    OpenApiTool, 
    OpenApiAnonymousAuthDetails, 
    ResponseFormatJsonSchema, 
    ResponseFormatJsonSchemaType
)
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from a .env file
load_dotenv()

# Environment Variables Setup
# ---------------------------------------------------------------------
azure_foundry_project_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
azure_foundry_key = os.getenv("AI_FOUNDRY_API_KEY")
azure_foundry_deployment = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME")

# Define Pydantic Models for Structured Output
# ---------------------------------------------------------------------
# Pydantic models serve two purposes:
# 1. They define the exact structure of the data we expect from the agent
# 2. They automatically generate JSON schemas that Azure AI can use to enforce response format

class GitHubRepo(BaseModel):
    """
    Individual repository information.
    Each field is validated automatically by Pydantic.
    """
    repo_name: str          # Repository name
    description: str        # Repository description
    stars: int             # Number of stars
    forks: int             # Number of forks
    issues: int            # Number of open issues
    url: str               # Repository URL

class GitHubReposResponse(BaseModel):
    """
    Complete response structure containing multiple repositories.
    This model enforces that the agent returns a consistent structure
    with an array of repositories and metadata.
    """
    repositories: list[GitHubRepo]  # Array of repository objects
    total_found: int                # Total number of repositories found
    query_used: str                 # The search query that was used

# Authentication Setup using DefaultAzureCredential
# ---------------------------------------------------------------------
# Using context manager for proper resource management
with AIProjectClient(
    endpoint=azure_foundry_project_endpoint,
    credential=DefaultAzureCredential()
) as project:

    # OpenAPI Tool Setup for GitHub Integration
    # ---------------------------------------------------------------------
    # Load the GitHub OpenAPI specification from a local JSON file
    # This allows our agent to search GitHub repositories using the GitHub API
    with open(os.path.join(os.path.dirname(__file__), "openApiDef/gitHubOpenApidef.json"), "r") as f:
        github_openapi_spec = jsonref.loads(f.read())

    # Create authentication object for the OpenAPI tool
    # Using anonymous auth for GitHub public API (no token required for basic searches)
    auth = OpenApiAnonymousAuthDetails()

    # Initialize the OpenAPI tool definition for GitHub
    github_tool = OpenApiTool(
        name="github_search", 
        spec=github_openapi_spec, 
        description="Search and retrieve GitHub repository information", 
        auth=auth
    )

    # Agent Creation with Structured Output Configuration
    # ---------------------------------------------------------------------
    agent = project.agents.create_agent(
        model=azure_foundry_deployment,
        name="github_structured_output_agent",
        
        # Detailed instructions for the agent
        # These instructions are crucial for getting the desired structured output
        instructions="""
        You are a GitHub repository specialist that provides structured data about repositories.

        When searching for repositories:
        1. Use the GitHub search API to find MULTIPLE repositories (at least 3-5) related to the user's query
        2. For each repository found, extract the following information:
           - Repository name (repo_name)
           - Description
           - Number of stars
           - Number of forks
           - Number of open issues
           - Repository URL
        """,
        
        # Attach the GitHub search tool to the agent
        tools=github_tool.definitions,
        
        # Configure structured output using ResponseFormatJsonSchema
        # This is the key component that enforces the Pydantic model structure
        response_format=ResponseFormatJsonSchemaType(
            json_schema=ResponseFormatJsonSchema(
                name="GitHubReposResponse",  # Name of the schema
                schema=GitHubReposResponse.model_json_schema()  # Auto-generated from Pydantic model
            )
        )
    )

    # Thread and Message Creation
    # ---------------------------------------------------------------------
    # Create a conversation thread
    thread = project.agents.threads.create()

    # Create the user message with the search query
    message = project.agents.messages.create(
        thread_id=thread.id, 
        role="user", 
        content="Find repositories related to AI Agent frameworks and services"
    )

    # Run Creation and Processing
    # ---------------------------------------------------------------------
    # This will execute the agent with the structured output requirements
    print("🔍 Searching for AI Agent repositories with structured output...")
    run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    # Error Handling
    # ---------------------------------------------------------------------
    if run.status == "failed":
        print(f"❌ Run failed: {run.last_error}")
    else:
        print("✅ Search completed successfully!")

    # Retrieving and Displaying Structured Results
    # ---------------------------------------------------------------------
    messages = project.agents.messages.list(
        thread_id=thread.id, 
        order=ListSortOrder.ASCENDING
    )

    # Process the agent's response
    for message in messages:
        if message.run_id == run.id and message.text_messages:
            response_content = message.text_messages[-1].text.value
            print(f"\n📊 Structured Output from Agent:")
            print("=" * 50)
            print(f"{response_content}")
            
            # Optional: Parse the JSON response to validate it matches our Pydantic model
            try:
                import json
                parsed_response = json.loads(response_content)
                validated_response = GitHubReposResponse(**parsed_response)
                print(f"\n✅ Response validation successful!")
                print(f"📈 Found {validated_response.total_found} repositories")
                print(f"🔍 Query used: {validated_response.query_used}")
                print(f"📦 First repository: {validated_response.repositories[0].repo_name}")
            except Exception as e:
                print(f"⚠️  Response validation failed: {e}")

# Key Takeaways for Structured Output:
# ====================================
# 1. Define clear Pydantic models that represent your desired output structure
# 2. Use ResponseFormatJsonSchema to enforce the structure at the agent level
# 3. Provide detailed instructions to guide the agent on how to populate the structure
# 4. Always validate the response to ensure it matches your expected format
# 5. Consider the complexity of your schema - simpler structures are more reliable