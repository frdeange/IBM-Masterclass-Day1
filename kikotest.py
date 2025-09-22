# 0. Import necessary libraries and set up environment variables
# ---------------------------------------------------------------------
import os
import jsonref
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder, OpenApiTool, OpenApiAnonymousAuthDetails, ResponseFormatJsonSchema, ResponseFormatJsonSchemaType
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from a .env file
load_dotenv()

# 1. Environment Variables Setup
# ---------------------------------------------------------------------
azure_foundry_project_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
azure_foundry_key = os.getenv("AI_FOUNDRY_API_KEY")
azure_foundry_deployment = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME")

# 2. Authentication Setup using DefaultAzureCredential
# ---------------------------------------------------------------------
# 3. AI Project Client Setup with context manager
# ---------------------------------------------------------------------

with AIProjectClient(
    endpoint=azure_foundry_project_endpoint,
    credential=DefaultAzureCredential()
) as project:

    # 4. Create the OpenAPI Tool loading the specification from a local file
    # ---------------------------------------------------------------------
    # Load the OpenAPI specification for the inventory service from a local JSON file
    with open(os.path.join(os.path.dirname(__file__), "./gitHubOpenApidef.json"), "r") as f:
        openapi_inventory = jsonref.loads(f.read())

    # Create Auth object for the OpenApiTool (note: using anonymous auth here; connection or managed identity requires additional setup)
    auth = OpenApiAnonymousAuthDetails()

    # Initialize the main OpenAPI tool definition for inventory
    openapi_tool = OpenApiTool(
        name="get_inventory", 
        spec=openapi_inventory, 
        description="Retrieve inventory information for a location", 
        auth=auth
    )

    class GitHubRepo(BaseModel):
        repo_name: str
        description: str
        stars: int
        forks: int
        issues: int
        url: str

    class GitHubReposResponse(BaseModel):
        repositories: list[GitHubRepo]
        total_found: int
        query_used: str

    # 5. Agent Creation
    # ---------------------------------------------------------------------
    agent = project.agents.create_agent(
        model=azure_foundry_deployment,
        name="github_explorer_agent_TEST",
        instructions="""
        You are a GitHub repository specialist.

        When searching for repositories:
        1. Find MULTIPLE repositories (at least 3-5) related to the user's query
        2. For each repository, extract: name, description, stars, forks, open issues, and URL
        3. Return a structured JSON response with ALL found repositories in the 'repositories' array
        4. Include the total count and search query used
        5. Use the GitHub search API to find popular and relevant repositories

        IMPORTANT: Always return the response in the exact JSON format specified, with multiple repositories in the repositories array.""",
        
        tools=openapi_tool.definitions,
        response_format=ResponseFormatJsonSchemaType(
            json_schema=ResponseFormatJsonSchema(
                name="GitHubReposResponse",
                schema=GitHubReposResponse.model_json_schema()
            )
        )
    )

    # 6. Thread Creation
    # ---------------------------------------------------------------------
    thread = project.agents.threads.create()

    # 7. Message Creation
    # ---------------------------------------------------------------------
    message = project.agents.messages.create(
        thread_id=thread.id, 
        role="user", 
        content="Give me repos related to AI Agent Service"
    )

    # 8. Run Creation and Processing
    # ---------------------------------------------------------------------
    run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    # 9. Error Handling
    # ---------------------------------------------------------------------
    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    # 10. Retrieving and Displaying Messages
    # ---------------------------------------------------------------------
    messages = project.agents.messages.list(
        thread_id=thread.id, 
        order=ListSortOrder.ASCENDING
    )

    for message in messages:
        if message.run_id == run.id and message.text_messages:
            print(f"{message.role}: {message.text_messages[-1].text.value}")

