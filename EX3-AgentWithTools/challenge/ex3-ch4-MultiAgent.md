# 🚀 Challenge 4: Multi-Agent Development Assistant

<div align="center">

![Challenge 4](https://img.shields.io/badge/Challenge-4-blue?style=for-the-badge)
![Difficulty](https://img.shields.io/badge/Difficulty-Intermediate-yellow?style=for-the-badge)
![Time](https://img.shields.io/badge/Time-35%20minutes-orange?style=for-the-badge)

**Build 3 specialized AI agents that work together as a development team!**

</div>

---

## 🎯 **Objective**

Create three specialized agents that complement each other, preparing for agent orchestration in the next exercise. Each agent will master one integration type: Custom Functions, OpenAPI, and MCP. Together, they form a complete development assistance system!

Remember, we're gonna build agents "standalone" first, and then in the next exercise, we'll orchestrate them to work together seamlessly. At this point, you don't need to implement the orchestration logic yet.

## ✨ **What You'll Learn**

<table>
<tr>
<td>

### 🔄 **Core Skills**
- Multi-agent system design
- Specialized agent responsibilities  
- Custom functions, OpenAPI, and MCP integration
- Preparing for agent orchestration

</td>
<td>

### 🧠 **AI Concepts**  
- Agent specialization patterns
- Complementary agent capabilities
- Foundation for orchestration systems
- Real-world multi-agent workflows

</td>
</tr>
</table>

---

## 📝 **Challenge Description**

This challenge use the agents created in the previous exercises. Build three independent specialized agents based on the existing samples (`ex3-s1-FunctionCalling.py`, `ex3-s2-AgentWithOpenAPI.py`, and `ex3-s3-AgentWithMCP.py`):

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 15px 0; color: white;">

### 🎯 **Your Mission: The Development Dream Team**

**👨‍💻 Agent 1: Code Analyst** (Custom Function)
- Analyzes repository complexity and metrics based on GitHub API data (see hints below)
- Uses custom `analyze_code_metrics()` function
- Provides insights on project size, language, popularity, and activity
- Limits analysis to 3 repositories by default

**🐙 Agent 2: GitHub Explorer** (OpenAPI Integration)  
- Searches GitHub repositories by keywords
- Uses GitHub REST API for repository discovery
- You can find in this repo the OpenAPI definition to connect to GitHub (gitHHubOpenAPidef.json) or use the raw GitHub definition https://raw.githubusercontent.com/github/rest-api-description/refs/heads/main/descriptions/api.github.com/api.github.com.json

**📚 Agent 3: Documentation Expert** (MCP Integration)
- Provides Microsoft Learn documentation and guidance
- Uses Microsoft Learn MCP server

**🌟 Together they enable workflows like:**
*"Find Chainlit projects using Azure OpenAI → Analyze their complexity → Get relevant documentation"*

</div>

---

## 📋 **Technical Requirements**

### 🥇 **Basic Level (30-35 minutes)** ✅ MAIN GOAL

<div style="background: #022209ff; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin: 10px 0;">

**Perfect for learning multi-agent design patterns!**

- [ ] ✅ **Build Code Analyst Agent** with `analyze_code_metrics()` custom function
- [ ] ✅ **Build GitHub Explorer Agent** connected to GitHub REST API  and retrieve repository data ONLY 3 REPOS BY DEFAULT
- [ ] ✅ **Build Documentation Expert Agent** connected to Microsoft Learn MCP
- [ ] ✅ **Test each agent independently** with their specialized tasks

</div>

---

## 💡 **Getting Started Hints**

### 🤖 **Imported Libraries and modules**
Remember to import necessary libraries and modules at the beginning of your script. In the different examples we use only the required imports for each agent, but in this multi-agent setup, you'll need to combine them all.


### 🤖 **Agent 1: Code Analyst (Custom Function)**

<details>
<summary>🔍 <strong>Click to see analyze_code_metrics function</strong></summary>

```python
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
```

</details>

<details>
<summary>🤖 <strong>Click to see Code Analyst agent setup</strong></summary>

```python
# Function calling tool definition
tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_code_metrics",
            "description": "Analyzes repository complexity and metrics from GitHub repository data",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_data": {
                        "type": "object",
                        "description": "Repository data from GitHub API containing size, language, stars, etc."
                    }
                },
                "required": ["repo_data"]
            }
        }
    }
]

agent = agents_client.create_agent(
    model=azure_foundry_deployment,
    name="Code Analyst Agent",
    instructions="""You are a code analysis specialist. Your job is to analyze GitHub repositories and provide insights about their complexity, size, and characteristics.

When given repository data from GitHub API, use the analyze_code_metrics function to provide detailed analysis including:
- Project size and complexity assessment
- Programming language identification  
- Popularity and activity metrics
- Development recommendations

Provide clear, actionable insights to help developers understand repository characteristics.""",
    tools=tools
)
```

</details>

### 🐙 **Agent 2: GitHub Explorer (OpenAPI)**

<details>
<summary>🤖 <strong>Click to see GitHub Explorer agent setup</strong></summary>

```python
agent = agents_client.create_agent(
    model=azure_foundry_deployment,
    name="GitHub Explorer Agent", 
    instructions="""You are a GitHub repository discovery specialist. Your job is to help developers find relevant repositories based on their requirements.

Use the GitHub search API to:
- (describe conditions required by the exercise here)""",
    tools=openapi_tool.definitions
)
```

</details>

### 📚 **Agent 3: Documentation Expert (MCP)**

<details>
<summary>🔍 <strong>Click to see MCP configuration</strong></summary>

```python
# Microsoft Learn MCP configuration
mcp_server_url = "https://learn.microsoft.com/api/mcp"
mcp_server_label = "microsoft_learn"

mcp_tool = McpTool(
    server_label=mcp_server_label,
    server_url=mcp_server_url,
    allowed_tools=[]  # Allow all available tools
)
```

</details>

<details>
<summary>🤖 <strong>Click to see Documentation Expert agent setup</strong></summary>

```python
agent = agents_client.create_agent(
    model=azure_foundry_deployment,
    name="Documentation Expert Agent",
    instructions="""You are a Microsoft Learn documentation specialist. Your job is to provide accurate, up-to-date technical guidance from official Microsoft documentation.

Use Microsoft Learn MCP tools to:
- Search for relevant documentation and tutorials
- Provide step-by-step guidance for Microsoft technologies
- Explain concepts with official examples and best practices
- Help with Azure services, .NET, Python, AI/ML, and other Microsoft technologies

Always base your responses on official Microsoft Learn content and provide clear, actionable guidance.""",
    tools=mcp_tool.definitions
)
```

</details>

---

## 🧪 **Testing Your Multi-Agent System**

### 📝 **Individual Agent Tests**

**Test Code Analyst Agent:**
```python
# Test with repository data
test_repo_data = {
    "name": "chainlit-azure-openai", 
    "language": "Python",
    "size": 2500,
    "stargazers_count": 150,
    "forks_count": 25,
    "open_issues_count": 8
}

message = "Analyze this repository data and tell me about its complexity"
```

**Test GitHub Explorer Agent:**
```python
message = "Search for repositories related to 'chainlit azure openai agent' and show me the top 3 results"
```

**Test Documentation Expert Agent:**
```python
message = "How do I set up Azure OpenAI service and connect to it using Python? Include authentication steps."
```

### 🔄 **Multi-Agent Workflow Demo**

Demonstrate how the agents complement each other:

1. **Step 1** - GitHub Explorer: *"Find Chainlit projects using Azure OpenAI"*
2. **Step 2** - Code Analyst: *"Analyze the complexity of the found repositories"* 
3. **Step 3** - Documentation Expert: *"Provide setup guidance for Chainlit and Azure OpenAI"*

---

## ✅ **Success Criteria**

Your multi-agent system should:

- **🤖 Three independent agents** working correctly
- **🎯 Specialized capabilities** - Each agent excels at its specific task
- **🔄 Complementary functions** - Together they provide comprehensive development assistance
- **📊 Code analysis** - Metrics and complexity assessment
- **🔍 Repository discovery** - Effective GitHub search functionality  
- **📚 Documentation access** - Up-to-date Microsoft Learn guidance

---

## 🚀 **What's Next?**

These three specialized agents are **perfectly prepared for orchestration**! In the next exercise (EX4), you'll learn how to coordinate multiple agents to work together automatically, creating sophisticated multi-agent workflows.

The foundation you're building here will enable:
- **Automatic agent coordination**
- **Complex multi-step workflows** 
- **Intelligent task delegation**
- **Scalable AI assistant systems**

---

## 🔧 **Common Issues & Solutions**

<details>
<summary>❌ <strong>Function Calling Issues</strong></summary>

- **Problem**: Custom function not being called
- **Solution**: Check function definition format and parameter types
- **Tip**: Test function independently before integrating

</details>

<details>
<summary>🐙 <strong>GitHub API Issues</strong></summary>

- **Problem**: API calls failing or rate limited
- **Solution**: Check query format and consider adding delays
- **Tip**: Use specific search terms for better results

</details>

<details>
<summary>📚 <strong>MCP Connection Issues</strong></summary>

- **Problem**: Cannot connect to Microsoft Learn MCP
- **Solution**: Verify URL and check network connectivity
- **Tip**: Test with simple queries first

</details>

---

## 🏆 **Completion Checklist**

- [ ] ✅ Code Analyst Agent created with custom function
- [ ] ✅ GitHub Explorer Agent connected to GitHub API
- [ ] ✅ Documentation Expert Agent connected to Microsoft Learn MCP
- [ ] ✅ All three agents tested independently
- [ ] ✅ Demonstrated how agents complement each other
- [ ] ✅ Ready for agent orchestration in the next exercise!

---

<div align="center">

**🎉 Congratulations!**  
You've built a complete multi-agent development assistance system!

**Next up**: Exercise 4 - Agent Orchestration! 🚀

</div>