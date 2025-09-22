# 📚 Challenge 3: Microsoft Learn Documentation Agent

<div align="center">

![Challenge 3](https://img.shields.io/badge/Challenge-3-blue?style=for-the-badge)
![Difficulty](https://img.shields.io/badge/Difficulty-Beginner-green?style=for-the-badge)
![Time](https://img.shields.io/badge/Time-20%20minutes-orange?style=for-the-badge)

**Connect your AI agent to Microsoft Learn documentation using MCP!**

</div>

---

## 🎯 **Objective**

Transform the `ex3-s3-AgentWithMCP.py` example into a specialized documentation assistant that connects to Microsoft Learn through the Model Context Protocol. Learn how to integrate external knowledge sources to enhance your AI agent's capabilities!

## ✨ **What You'll Learn**

<table>
<tr>
<td>

### 🔄 **Core Skills**
- Model Context Protocol (MCP) integration
- Microsoft Learn MCP server configuration
- External documentation access
- Real-time knowledge retrieval

</td>
<td>

### 🧠 **AI Concepts**  
- Knowledge augmentation patterns
- External service integration
- Documentation-driven assistance
- Preparing for multi-agent systems

</td>
</tr>
</table>

---

## 📝 **Challenge Description**

Based on the example `ex3-s3-AgentWithMCP.py`, create a documentation assistant that connects to Microsoft Learn's official MCP server to provide up-to-date technical guidance:

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 15px 0; color: white;">

### 🎯 **Your Mission**

1. **🔗 Connect to Microsoft Learn MCP** - Configure your agent to use the official Microsoft Learn MCP server
2. **📖 Create a documentation expert** - Build an agent that can answer technical questions using real documentation
3. **🧪 Test with real queries** - Ask complex questions about Azure, .NET, Python, and other Microsoft technologies
4. **🚀 Prepare for orchestration** - This agent will be one of three in the next challenge!

**🌟 Special Note**: You'll be connecting to Microsoft's **official MCP server** with live documentation!

</div>

---

## 📋 **Technical Requirements**

### 🥇 **Basic Level (15-20 minutes)** ✅ MAIN GOAL

<div style="background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin: 10px 0;">

**Perfect for getting started with MCP integration!**

- [ ] ✅ **Configure Microsoft Learn MCP** server at `https://learn.microsoft.com/api/mcp`
- [ ] ✅ **Create a documentation agent** with clear instructions for technical guidance
- [ ] ✅ **Test documentation queries** - Ask about Azure services, .NET concepts, or Python libraries
- [ ] ✅ **Handle approval workflow** - Successfully approve tool calls and get responses

</div>

### 🌟 **Advanced Level (Extra 5 minutes for fast finishers)** ⭐ BONUS

<div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 10px 0;">

**For those who finish early and want extra functionality!**

- [ ] 🔥 **Multi-question conversation** - Ask follow-up questions in the same thread
- [ ] 🔥 **Specific technology focus** - Test with complex Azure AI or ML questions
- [ ] 🔥 **Error handling** - Test what happens when documentation isn't found

</div>

---

## 💡 **Getting Started Hints**

### 🟢 **Basic Level Implementation**

<details>
<summary>🔍 <strong>Click to see MCP configuration</strong></summary>

```python
# Update the MCP server configuration
mcp_server_url = "https://learn.microsoft.com/api/mcp"
mcp_server_label = "microsoft_learn"

# Initialize agent MCP tool
mcp_tool = McpTool(
    server_label=mcp_server_label,
    server_url=mcp_server_url,
    allowed_tools=[],  # Let it use all available tools
)
```

</details>

<details>
<summary>🤖 <strong>Click to see agent instructions</strong></summary>

```python
agent = agents_client.create_agent(
    model=azure_foundry_deployment,
    name="Microsoft Learn Documentation Assistant",
    instructions="""You are a specialized documentation assistant that helps developers find ............. (describe it!).""",
    tools=mcp_tool.definitions,
)
```

</details>

<details>
<summary>💬 <strong>Click to see example questions</strong></summary>

```python
# Test these types of questions:
test_questions = [
    "How do I create an Azure OpenAI service and connect to it with Python?",
    "What are the best practices for using Azure AI Services?", 
    "How do I implement authentication in a .NET Core web API?",
    "What's the difference between Azure Functions and Azure Container Apps?",
    "How do I use Azure Cognitive Search with semantic search?"
]
```

</details>

---

## 🧪 **Testing Your Agent**

### 📝 **Sample Conversation**

Try asking your agent questions like:

```
"I'm building a Python application that needs to use Azure OpenAI. 
Can you help me understand how to set up authentication and make my first API call?"
```

### ✅ **Success Criteria**

Your agent should:
- Successfully connect to Microsoft Learn MCP
- Retrieve relevant documentation
- Provide accurate, actionable guidance
- Handle the approval workflow smoothly

---

## 🎯 **What's Next?**

This documentation agent will become **one of three specialized agents** in Challenge 4, where you'll learn to orchestrate multiple agents working together! 

Perfect preparation for building complex AI systems! 🚀

---

## 🔧 **Common Issues & Solutions**

<details>
<summary>❌ <strong>MCP Connection Issues</strong></summary>

- **Problem**: Cannot connect to MCP server
- **Solution**: Verify the URL is exactly `https://learn.microsoft.com/api/mcp`
- **Check**: Ensure your network allows HTTPS connections

</details>

<details>
<summary>⏳ <strong>Approval Workflow Problems</strong></summary>

- **Problem**: Tool calls not getting approved
- **Solution**: Make sure you're handling the `requires_action` status properly
- **Check**: Verify `ToolApproval` objects are created correctly

</details>

<details>
<summary>🔍 <strong>No Documentation Found</strong></summary>

- **Problem**: Agent says it can't find information
- **Solution**: Try rephrasing your question with more specific Microsoft technology terms
- **Tip**: Use terms like "Azure", ".NET", "Microsoft Graph", etc.

</details>

---

## 🏆 **Completion Checklist**

- [ ] ✅ MCP server configured correctly
- [ ] ✅ Agent created with appropriate instructions  
- [ ] ✅ Successfully asked at least 3 technical questions
- [ ] ✅ Received helpful documentation-based responses
- [ ] ✅ Understood the approval workflow
- [ ] ✅ Ready for multi-agent orchestration in Challenge 4!

---

<div align="center">

**🎉 Congratulations!**  
You've built a powerful documentation assistant that can access live Microsoft Learn content!

**Next up**: Challenge 4 - Multi-Agent System! 🚀

</div>
