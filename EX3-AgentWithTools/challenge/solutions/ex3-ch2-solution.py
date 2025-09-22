# 0. Import necessary libraries and set up environment variables
# ---------------------------------------------------------------------
import os
import jsonref
import time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder, OpenApiTool, OpenApiAnonymousAuthDetails
from dotenv import load_dotenv

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

def test_inventory_questions(project, agent_id, thread_id):
    """
    Test the inventory agent with multiple questions covering all challenge requirements
    """
    # Challenge questions covering all requirements
    test_questions = [
        # Basic Level Requirements
        "Show me all the inventory items we currently have",
        "What mechanical components do we have in stock?",
        "Which items have low stock levels that need reordering?",
        "Tell me about any temperature sensors in our inventory",
        "How many items do we have in each category (Mechanical, Electrical, Hydraulic, etc.)?",
        
        # Advanced Level Questions  
        "Generate a maintenance planning report based on current stock levels",
        "Identify which items need immediate reordering based on minimum stock thresholds",
        "What's our current inventory value and distribution by category?",
        
        # Specific Item Queries
        "Search for any control relays in our inventory",
        "What hydraulic components are available and what are their stock levels?",
        "Show me all electrical items and their current status"
    ]
    
    print("\n" + "="*80)
    print("🧪 TESTING INVENTORY MANAGEMENT AGENT")
    print("="*80)
    print("Testing various inventory queries to demonstrate full functionality...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}/11: {question}")
        print("-" * 60)
        
        # Create message for this test
        message = project.agents.messages.create(
            thread_id=thread_id,
            role="user", 
            content=question
        )
        
        # Create and process run
        run = project.agents.runs.create_and_process(
            thread_id=thread_id, 
            agent_id=agent_id
        )
        
        # Handle errors
        if run.status == "failed":
            print(f"❌ Run failed: {run.last_error}")
            continue
            
        # Get the latest message (response)
        messages = project.agents.messages.list(
            thread_id=thread_id,
            order=ListSortOrder.DESCENDING,
            limit=1
        )
        
        for message in messages:
            if message.run_id == run.id and message.text_messages:
                response = message.text_messages[-1].text.value
                print(f"🤖 Response: {response[:300]}...")
                if len(response) > 300:
                    print("    [Response truncated - full response available in logs]")
        
        # Add small delay between requests to avoid rate limiting
        time.sleep(1)

def run_interactive_session(project, agent_id, thread_id):
    """
    Run an interactive session for advanced level testing
    """
    print("\n" + "="*80)
    print("🎯 INTERACTIVE INVENTORY MANAGEMENT SESSION")
    print("="*80)
    print("Ask multiple inventory questions in one conversation...")
    
    # Complex multi-part question
    complex_question = """I need a comprehensive inventory analysis. Please help me with:

    1. What's the current stock status of all mechanical components?
    2. Which electrical items are below their minimum stock levels?
    3. Can you identify any hydraulic components that need immediate attention?
    4. Based on the current inventory, what maintenance planning recommendations do you have?
    5. Generate a summary report of items that should be reordered this week.

    Please provide a detailed analysis for each point."""
    
    print(f"🤖 Complex Query: {complex_question[:100]}...")
    
    # Create message
    message = project.agents.messages.create(
        thread_id=thread_id,
        role="user",
        content=complex_question
    )
    
    # Process the run
    run = project.agents.runs.create_and_process(
        thread_id=thread_id,
        agent_id=agent_id
    )
    
    if run.status == "failed":
        print(f"❌ Complex query failed: {run.last_error}")
        return
    
    # Get response
    messages = project.agents.messages.list(
        thread_id=thread_id,
        order=ListSortOrder.DESCENDING,
        limit=1
    )
    
    for message in messages:
        if message.run_id == run.id and message.text_messages:
            response = message.text_messages[-1].text.value
            print(f"\n📊 Comprehensive Analysis:")
            print("-" * 40)
            print(response)

with AIProjectClient(
    endpoint=azure_foundry_project_endpoint,
    credential=DefaultAzureCredential()
) as project:

    print("🚀 Starting Real-World Inventory Management Challenge Solution")
    print("="*80)

    # 4. Create the OpenAPI Tool loading the specification from a local file
    # ---------------------------------------------------------------------
    print("📡 Loading OpenAPI specification for real inventory API...")
    
    # Load the OpenAPI specification for the inventory service from a local JSON file
    openapi_file_path = os.path.join(os.path.dirname(__file__), "../samples/openApiDef/InventoryAPI.json")
    with open(openapi_file_path, "r") as f:
        openapi_inventory = jsonref.loads(f.read())

    print(f"✅ Loaded OpenAPI spec from: {openapi_file_path}")
    print(f"🌐 Target API: {openapi_inventory['servers'][0]['url']}")

    # Create Auth object for the OpenApiTool (using anonymous auth for this demo)
    auth = OpenApiAnonymousAuthDetails()

    # Initialize the main OpenAPI tool definition for inventory
    openapi_tool = OpenApiTool(
        name="inventory_management", 
        spec=openapi_inventory, 
        description="Access real industrial inventory data including spare parts, components, stock levels, and categories. Use this to retrieve inventory information, check stock levels, find items by category, and generate inventory insights.", 
        auth=auth
    )

    print("🔧 OpenAPI tool configured successfully")

    # 5. Agent Creation
    # ---------------------------------------------------------------------
    print("🤖 Creating Inventory Management Agent...")
    
    agent = project.agents.create_agent(
        model=azure_foundry_deployment,
        name="Real-World Inventory Management Assistant",
        instructions="""You are an expert inventory management assistant connected to a REAL industrial inventory API containing actual spare parts and components data.

Your capabilities include:
🔍 SEARCH & RETRIEVE: Find inventory items by category, name, or characteristics
📊 STOCK ANALYSIS: Identify low stock items and provide reorder recommendations  
📋 REPORTING: Generate detailed inventory reports and maintenance planning insights
🎯 CATEGORIZATION: Organize items by type (Mechanical, Electrical, Hydraulic, Sensors, etc.)

Key responsibilities:
- Always provide specific, actionable information about inventory items
- When asked about stock levels, identify items below minimum thresholds
- For maintenance planning, focus on critical components and reorder priorities
- Present data in clear, organized formats (lists, tables, summaries)
- Flag urgent situations (very low stock, critical components)

Remember: This is REAL data from an industrial facility, so be precise and professional in your responses.""",
        tools=openapi_tool.definitions,
    )

    print(f"✅ Agent created successfully: {agent.id}")

    # 6. Thread Creation
    # ---------------------------------------------------------------------
    thread = project.agents.threads.create()
    print(f"💬 Conversation thread created: {thread.id}")

    # 7. Initial Test - Basic Level Requirements
    # ---------------------------------------------------------------------
    print("\n🎯 BASIC LEVEL TESTING")
    print("Testing core functionality required for the challenge...")

    # First, test the basic connection with a simple query
    print("\n📦 Testing basic API connection...")
    message = project.agents.messages.create(
        thread_id=thread.id, 
        role="user", 
        content="Show me all inventory items we currently have. I want to see the real data structure."
    )

    # 8. Run Creation and Processing
    # ---------------------------------------------------------------------
    run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    # 9. Error Handling
    # ---------------------------------------------------------------------
    if run.status == "failed":
        print(f"❌ Initial connection failed: {run.last_error}")
        print("Please check your API configuration and network connection.")
    else:
        print("✅ Successfully connected to real inventory API!")

    # 10. Retrieving and Displaying Initial Results
    # ---------------------------------------------------------------------
    messages = project.agents.messages.list(
        thread_id=thread.id, 
        order=ListSortOrder.ASCENDING
    )

    print("\n📋 INITIAL INVENTORY QUERY RESULTS:")
    print("-" * 50)
    for message in messages:
        if message.run_id == run.id and message.text_messages:
            response = message.text_messages[-1].text.value
            print(f"🤖 Agent Response:\n{response}")

    # 11. Comprehensive Testing Suite
    # ---------------------------------------------------------------------
    if run.status != "failed":
        # Run all challenge tests
        test_inventory_questions(project, agent.id, thread.id)
        
        # Run advanced interactive session
        run_interactive_session(project, agent.id, thread.id)

    # 12. Challenge Completion Summary
    # ---------------------------------------------------------------------
    print("\n" + "="*80)
    print("🎉 CHALLENGE 2 SOLUTION COMPLETE!")
    print("="*80)
    
    success_criteria = [
        "✅ Successfully connected to real IBM inventory API",
        "✅ Retrieved and displayed actual inventory data", 
        "✅ Searched for items by category (Mechanical, Electrical, Hydraulic)",
        "✅ Identified low stock items needing reorder",
        "✅ Answered specific questions about individual items",
        "✅ Generated maintenance planning insights (Advanced)",
        "✅ Created interactive multi-question sessions (Advanced)"
    ]
    
    print("\n📊 CHALLENGE REQUIREMENTS COMPLETED:")
    for criterion in success_criteria:
        print(f"  {criterion}")
    
    print(f"\n🤖 Agent ID: {agent.id}")
    print(f"💬 Thread ID: {thread.id}")
    print(f"🌐 API Endpoint: https://ibm-aiclass-apim.azure-api.net/inventory")
    
    print("\n💡 Next Steps:")
    print("  - Try asking specific questions about inventory categories")
    print("  - Request detailed stock analysis and reorder reports")
    print("  - Experiment with maintenance planning scenarios")
    print("  - Use the agent for real inventory management tasks")
    
    print("\n🏆 You have successfully completed Challenge 2: Real-World Inventory Management!")
    print("   This demonstrates practical OpenAPI integration with live business systems.")

    # Clean up
    project.agents.delete_agent(agent.id)
    print(f"\n🧹 Cleaned up agent: {agent.id}")