import os, time
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool
import json
import datetime
import random
import string
from typing import Any, Callable, Set, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

azure_foundry_project_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
azure_foundry_deployment = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME")

# Global task storage for the session
task_storage = []
task_counter = 1

# Enhanced weather function with multiple cities and detailed information
def fetch_weather(location: str, include_forecast: bool = False) -> str:
    """
    Fetches detailed weather information for the specified location.
    
    :param location: The location to fetch weather for
    :param include_forecast: Whether to include a 3-day forecast
    :return: Weather information as a JSON string
    """
    # Enhanced weather database with detailed information
    weather_database = {
        "New York": {"temp": "18°C", "condition": "Cloudy", "humidity": "65%", "wind": "12 km/h NW"},
        "London": {"temp": "12°C", "condition": "Rainy", "humidity": "80%", "wind": "8 km/h SW"},
        "Tokyo": {"temp": "22°C", "condition": "Sunny", "humidity": "55%", "wind": "6 km/h E"},
        "Sydney": {"temp": "25°C", "condition": "Partly Cloudy", "humidity": "60%", "wind": "15 km/h SE"},
        "Barcelona": {"temp": "25°C", "condition": "Sunny", "humidity": "45%", "wind": "10 km/h E"},
        "Madrid": {"temp": "22°C", "condition": "Cloudy", "humidity": "50%", "wind": "7 km/h N"},
        "Frankfurt": {"temp": "16°C", "condition": "Rainy", "humidity": "75%", "wind": "9 km/h W"},
        "Paris": {"temp": "19°C", "condition": "Overcast", "humidity": "70%", "wind": "11 km/h NW"},
        "Berlin": {"temp": "17°C", "condition": "Partly Cloudy", "humidity": "60%", "wind": "8 km/h NE"}
    }
    
    # Simple 3-day forecast data
    forecast_data = {
        "New York": ["19°C Sunny", "21°C Partly Cloudy", "16°C Rainy"],
        "London": ["14°C Overcast", "11°C Rainy", "15°C Cloudy"],
        "Tokyo": ["24°C Sunny", "23°C Partly Cloudy", "25°C Sunny"],
        "Sydney": ["27°C Sunny", "24°C Cloudy", "26°C Partly Cloudy"],
        "Barcelona": ["27°C Sunny", "26°C Sunny", "24°C Partly Cloudy"]
    }
    
    current_weather = weather_database.get(location, {
        "temp": "N/A", "condition": "Data not available", 
        "humidity": "N/A", "wind": "N/A"
    })
    
    result = {
        "location": location,
        "current": current_weather
    }
    
    if include_forecast and location in forecast_data:
        result["forecast"] = {
            "tomorrow": forecast_data[location][0],
            "day_2": forecast_data[location][1],
            "day_3": forecast_data[location][2]
        }
    
    return json.dumps(result)

# Time function with timezone support
def get_current_time(timezone: str = "UTC") -> str:
    """
    Gets the current time in the specified timezone.
    
    :param timezone: Timezone (UTC, EST, EDT, PST, PDT, CET, etc.) or America/New_York format
    :return: Current time as a JSON string
    """
    # Enhanced timezone mappings with both standard and daylight saving time
    # Also handle common timezone names
    timezones = {
        "UTC": 0, "GMT": 0,
        # US Eastern Time
        "EST": -5, "EDT": -4, "AMERICA/NEW_YORK": -4, "NEW_YORK": -4, "EASTERN": -4,
        # US Pacific Time  
        "PST": -8, "PDT": -7, "AMERICA/LOS_ANGELES": -7, "PACIFIC": -7,
        # US Central Time
        "CST": -6, "CDT": -5, "AMERICA/CHICAGO": -5, "CENTRAL": -5,
        # US Mountain Time
        "MST": -7, "MDT": -6, "AMERICA/DENVER": -6, "MOUNTAIN": -6,
        # European Time
        "CET": 1, "CEST": 2, "EUROPE/MADRID": 2, "EUROPE/PARIS": 2,
        # Asian Time
        "JST": 9, "ASIA/TOKYO": 9, "TOKYO": 9,
        # Australian Time
        "AEST": 10, "AEDT": 11, "AUSTRALIA/SYDNEY": 10, "SYDNEY": 10
    }
    
    # Get current UTC time
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    
    # Normalize timezone input
    tz_key = timezone.upper().replace("/", "/")
    
    # Apply timezone offset
    offset = timezones.get(tz_key, 0)
    if offset == 0 and tz_key != "UTC" and tz_key != "GMT":
        # If timezone not found, try common variations
        for tz_name, tz_offset in timezones.items():
            if tz_key in tz_name or tz_name in tz_key:
                offset = tz_offset
                break
    
    local_time = utc_now + datetime.timedelta(hours=offset)
    
    # Determine the actual timezone name being used
    actual_tz = timezone
    if tz_key == "AMERICA/NEW_YORK" or tz_key == "NEW_YORK":
        actual_tz = "EDT (Eastern Daylight Time)"
    elif tz_key == "EST":
        actual_tz = "EST (Eastern Standard Time)"
    
    result = {
        "timezone": actual_tz,
        "timezone_offset": f"UTC{offset:+d}",
        "current_time": local_time.strftime("%Y-%m-%d %H:%M:%S"),
        "day_of_week": local_time.strftime("%A"),
        "formatted_time": local_time.strftime("%I:%M %p"),
        "date": local_time.strftime("%B %d, %Y"),
        "note": "September uses Daylight Saving Time (EDT = UTC-4)" if "YORK" in tz_key.upper() else ""
    }
    
    return json.dumps(result)

# Password generator function
def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """
    Generates a secure random password.
    
    :param length: Length of the password (4-20 characters)
    :param include_symbols: Whether to include special symbols (!@#$%^&*)
    :return: Generated password as a JSON string
    """
    # Validate input
    if length < 4:
        length = 4
    elif length > 20:
        length = 20
    
    # Character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    numbers = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Build character pool
    char_pool = uppercase + lowercase + numbers
    if include_symbols:
        char_pool += symbols
    
    # Ensure password has at least one character from each required set
    password_chars = []
    password_chars.append(random.choice(uppercase))  # At least one uppercase
    password_chars.append(random.choice(lowercase))  # At least one lowercase
    password_chars.append(random.choice(numbers))    # At least one number
    
    if include_symbols:
        password_chars.append(random.choice(symbols))  # At least one symbol
    
    # Fill the rest randomly
    remaining_length = length - len(password_chars)
    for _ in range(remaining_length):
        password_chars.append(random.choice(char_pool))
    
    # Shuffle the password to avoid predictable patterns
    random.shuffle(password_chars)
    password = ''.join(password_chars)
    
    result = {
        "password": password,
        "length": length,
        "includes_symbols": include_symbols,
        "strength": "Strong" if length >= 12 and include_symbols else "Medium",
        "tips": "Store this password securely and don't share it!"
    }
    
    return json.dumps(result)

# Task management function (Advanced level)
def manage_tasks(action: str, task: str = "", task_id: int = 0) -> str:
    """
    Manages a simple task list.
    
    :param action: Action to perform (add, list, complete, delete)
    :param task: Task description (for add action)
    :param task_id: Task ID (for complete/delete actions)
    :return: Task management result as JSON
    """
    global task_storage, task_counter
    
    if action.lower() == "add":
        if not task:
            return json.dumps({"error": "Task description is required for add action"})
        
        new_task = {
            "id": task_counter,
            "description": task,
            "status": "pending",
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        task_storage.append(new_task)
        task_counter += 1
        
        return json.dumps({
            "action": "added",
            "task": new_task,
            "total_tasks": len(task_storage)
        })
    
    elif action.lower() == "list":
        return json.dumps({
            "action": "list",
            "tasks": task_storage,
            "total_tasks": len(task_storage),
            "pending_tasks": len([t for t in task_storage if t["status"] == "pending"])
        })
    
    elif action.lower() == "complete":
        for task_item in task_storage:
            if task_item["id"] == task_id:
                task_item["status"] = "completed"
                task_item["completed"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                return json.dumps({
                    "action": "completed",
                    "task": task_item
                })
        return json.dumps({"error": f"Task with ID {task_id} not found"})
    
    elif action.lower() == "delete":
        for i, task_item in enumerate(task_storage):
            if task_item["id"] == task_id:
                deleted_task = task_storage.pop(i)
                return json.dumps({
                    "action": "deleted",
                    "task": deleted_task,
                    "total_tasks": len(task_storage)
                })
        return json.dumps({"error": f"Task with ID {task_id} not found"})
    
    else:
        return json.dumps({
            "error": "Invalid action. Use: add, list, complete, or delete"
        })

# Random content function (Advanced level)
def get_random_content(content_type: str) -> str:
    """
    Generates random content like jokes, facts, or numbers.
    
    :param content_type: Type of content (joke, fact, number)
    :return: Random content as JSON
    """
    if content_type.lower() == "joke":
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!"
        ]
        return json.dumps({
            "type": "joke",
            "content": random.choice(jokes),
            "category": "general"
        })
    
    elif content_type.lower() == "fact":
        facts = [
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.",
            "A group of flamingos is called a 'flamboyance'.",
            "The human brain contains approximately 86 billion neurons.",
            "Bananas are berries, but strawberries aren't.",
            "The shortest war in history lasted only 38-45 minutes between Britain and Zanzibar in 1896."
        ]
        return json.dumps({
            "type": "fact",
            "content": random.choice(facts),
            "category": "interesting"
        })
    
    elif content_type.lower() == "number":
        lucky_number = random.randint(1, 100)
        return json.dumps({
            "type": "number",
            "content": f"Your lucky number is: {lucky_number}",
            "number": lucky_number,
            "range": "1-100"
        })
    
    else:
        return json.dumps({
            "error": "Invalid content type. Use: joke, fact, or number"
        })

# Define user functions - including all basic and advanced functions
user_functions = {fetch_weather, get_current_time, generate_password, manage_tasks, get_random_content}

# Initialize the AIProjectClient
project_client = AIProjectClient(
    endpoint=azure_foundry_project_endpoint,
    credential=DefaultAzureCredential(),
)

# Initialize the FunctionTool with user-defined functions
functions = FunctionTool(functions=user_functions)

with project_client:
    # Create an agent with custom functions
    agent = project_client.agents.create_agent(
        model=azure_foundry_deployment,
        name="Multi-Function Personal Assistant",
        instructions="""You are a helpful personal assistant with multiple capabilities. You can:
        
        🌤️ Provide detailed weather information for cities worldwide
        ⏰ Tell the current time in different timezones  
        🔐 Generate secure passwords with customizable options
        📝 Manage tasks (add, list, complete, delete)
        🎲 Generate random jokes, facts, and lucky numbers
        
        Always be friendly and helpful. When users ask for multiple things, handle them all efficiently.
        Provide clear, well-formatted responses and explain what you're doing.""",
        tools=functions.definitions,
    )
    print(f"Created Multi-Function Personal Assistant Agent, ID: {agent.id}")

    # Create a thread for communication
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Test with a complex multi-function request
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="""Hello! I need help with several things:
        1. What's the weather like in Tokyo with forecast?
        2. What time is it in New York right now?
        3. Generate a secure password with 4 characters including symbols
        4. Add a task 'Prepare for tomorrow's meeting'
        5. Tell me a random fact
        
        Thanks for your help!""",
    )
    print(f"Created message, ID: {message['id']}")

    # Create and process a run for the agent to handle the message
    run = project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)
    print(f"Created run, ID: {run.id}")

    # Poll the run status until it is completed or requires action
    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Calling function: {function_name} with args: {function_args}")
                
                # Handle each function call
                if function_name == "fetch_weather":
                    output = fetch_weather(**function_args)
                elif function_name == "get_current_time":
                    output = get_current_time(**function_args)
                elif function_name == "generate_password":
                    output = generate_password(**function_args)
                elif function_name == "manage_tasks":
                    output = manage_tasks(**function_args)
                elif function_name == "get_random_content":
                    output = get_random_content(**function_args)
                else:
                    output = json.dumps({"error": f"Unknown function: {function_name}"})
                
                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
            
            # Submit all tool outputs
            project_client.agents.runs.submit_tool_outputs(
                thread_id=thread.id, 
                run_id=run.id, 
                tool_outputs=tool_outputs
            )

    print(f"Run completed with status: {run.status}")

    # Fetch and log all messages from the thread
    messages = project_client.agents.messages.list(thread_id=thread.id)
    print("\n" + "="*80)
    print("CONVERSATION SUMMARY")
    print("="*80)
    
    messages_list = list(messages)  # Convert to list first
    for message in reversed(messages_list):  # Reverse to show chronological order
        role = message.role.upper()
        content = ""
        
        if hasattr(message, 'content') and message.content:
            if isinstance(message.content, list):
                for content_item in message.content:
                    if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                        content += content_item.text.value
            else:
                content = str(message.content)
        
        print(f"\n{role}:")
        print("-" * 40)
        print(content)

    # Demonstrate additional functionality
    print("\n" + "="*80)
    print("TESTING INDIVIDUAL FUNCTIONS")
    print("="*80)
    
    # Test individual functions to show they work
    print("\n🌤️ Weather Test:")
    print(fetch_weather("Barcelona", True))
    
    print("\n⏰ Time Test:")
    print(get_current_time("CET"))
    
    print("\n🔐 Password Test:")
    print(generate_password(20, False))
    
    print("\n📝 Task Test:")
    print(manage_tasks("add", "Buy groceries"))
    print(manage_tasks("list"))
    
    print("\n🎲 Random Content Test:")
    print(get_random_content("joke"))

    # Delete the agent after use
    project_client.agents.delete_agent(agent.id)
    print(f"\n✅ Deleted agent: {agent.id}")
    print("🎉 Multi-Function Personal Assistant Demo Complete!")