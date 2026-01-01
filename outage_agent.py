# outage_agent.py
# Outage Agent using Tensorlake - Modern tool-calling agent (no create_react_agent)

from tensorlake.applications import application, function, Image
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from exa_py import Exa
import requests
import os

# Explicitly use Python 3.11-slim (fully supported and stable with LangChain/Pydantic)
agent_image = (
    Image(base_image="python:3.11-slim")
    .run("apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*")
    .run("pip install --no-cache-dir langchain langchain-groq langchain-core exa-py requests")
)

# Tool: Exa semantic search
@function(image=agent_image, secrets=["EXA_API_KEY"])
def search_exa(query: str) -> str:
    """Search Exa for similar incidents or known issues."""
    try:
        exa = Exa(api_key=os.environ["EXA_API_KEY"])
        results = exa.search(query, num_results=5, type="neural")
        formatted = []
        for r in results.results:
            snippet = (r.snippet or r.text or "")[:400]
            formatted.append(f"Title: {r.title}\nURL: {r.url}\nSnippet: {snippet}\n")
        return "\n".join(formatted) or "No relevant results found."
    except Exception as e:
        return f"Exa search failed: {str(e)}"

# Tool: Browse URL
@function(image=agent_image)
def browse_url(url: str) -> str:
    """Fetch and return content from a URL (e.g., status page)."""
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "TensorlakeOutageAgent/1.0"})
        response.raise_for_status()
        content = response.text
        return content[:3000] + ("\n... [truncated]" if len(content) > 3000 else "")
    except Exception as e:
        return f"Failed to fetch {url}: {str(e)}"

# Main application
@application()
@function(
    image=agent_image,
    secrets=["GROQ_API_KEY", "EXA_API_KEY"],
    cpu=2,
    memory=4,
    timeout=300
)
def outage_agent(alert_description: str) -> str:
    if not alert_description or not alert_description.strip():
        return "Error: No alert description provided."

    # Try to use llama-3.3-70b-versatile, fallback to mixtral-8x7b-instant if rate limited
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",  # Fast, reliable, and widely available on Groq
            groq_api_key=os.environ["GROQ_API_KEY"],
            temperature=0.1,
        )
    except Exception as e:
        # Fallback to alternative model if primary fails
        llm = ChatGroq(
            model="mixtral-8x7b-instant",  # Alternative model
            groq_api_key=os.environ["GROQ_API_KEY"],
            temperature=0.1,
        )

    # Define LangChain tools that wrap Tensorlake functions
    @tool
    def exa_search(query: str) -> str:
        """Search for known outages, root causes, or similar incidents using semantic search."""
        return search_exa(query)

    @tool
    def browse_web(url: str) -> str:
        """Browse a specific URL such as a status page or documentation."""
        return browse_url(url)

    tools = [exa_search, browse_web]
    llm_with_tools = llm.bind_tools(tools)

    system_prompt = """You are an always-on on-call engineer responsible for service stability.

Your job is to analyze alerts and provide structured, actionable output. Answer exactly five questions:
1. What broke?
2. Why did it break?
3. What did you do about it?
4. Did it work?
5. Do humans need to step in?

OUTPUT FORMAT (follow this exactly):

1. ONE-PARAGRAPH SUMMARY (for humans - appears first)
Write a concise, single-paragraph summary that a human can read quickly. Include: what happened, root cause, actions taken, and current status.

2. STRUCTURED DECISION OUTPUT (JSON format for systems)
You MUST output valid, parseable JSON. Follow this EXACT format with proper syntax:

Example of CORRECT JSON:
{{
  "incident_id": "inc-2024-01-15-1430",
  "service": "authentication-service",
  "severity": "high",
  "status": "ongoing",
  "root_cause": "Database connection pool exhausted due to spike in traffic",
  "confidence": 0.75,
  "actions_taken": ["Restarted connection pool", "Increased pool size", "Added monitoring"],
  "verification": {{
    "metrics_before": "100 connections",
    "metrics_after": "200 connections"
  }},
  "should_escalate": true,
  "next_recommendation": "Monitor connection pool usage and consider auto-scaling"
}}

CRITICAL JSON RULES - READ CAREFULLY:
1. EVERY field MUST have a comma after it EXCEPT the last field in the object
2. Arrays MUST use this format: ["value1", "value2", "value3"] - NO indexes like 0: or 1:
3. Strings MUST be in double quotes: "text"
4. Numbers have NO quotes: 0.85 (not "0.85")
5. Booleans are lowercase: true or false (not "true" or True)
6. Nested objects use curly braces: {{"key": "value"}}
7. After every key-value pair, add a comma: "key": "value",

WRONG: "actions_taken": [0: "action1", 1: "action2"]  ❌
RIGHT: "actions_taken": ["action1", "action2"]  ✅

WRONG: "key": "value" "key2": "value2"  ❌ (missing comma)
RIGHT: "key": "value", "key2": "value2"  ✅

Before outputting, verify your JSON is valid by checking:
- Every field (except the last) has a comma
- Arrays use ["item1", "item2"] format, NOT [0: item1, 1: item2]
- All strings are in double quotes
- No trailing commas

3. SLACK-FRIENDLY CONDENSED VERSION (optional, if applicable)
🚨 Incident [Auto-Handled | Requires Attention]
Service: [service-name]
Cause: [brief root cause]
Action: [what was done]
Result: [outcome]
Escalation: [Not required ✅ | Required ⚠️]

IMPORTANT OUTPUT RULES:
- NEVER output long chain-of-thought reasoning
- NEVER dump raw logs or technical details without context
- NEVER use uncertain language like "maybe", "possibly", "I think" - be decisive
- NEVER use technical jargon without explaining the decision
- ALWAYS be clear and actionable
- If you cannot determine root cause, state "Root cause unclear - requires investigation" and set confidence < 0.5

ESCALATION RULES:
DO NOT ESCALATE if:
- Alert describes expected, scheduled, known, or already resolved situations
- Alert describes a transient issue that has recovered
- Alert describes a routine issue with a clear explanation
- You can provide reasonable analysis and recommendations

ONLY ESCALATE if ALL are true:
1. Issue is CURRENTLY ONGOING (not resolved, not expected, not transient)
2. HIGH IMPACT (data loss, complete outage, critical service down, security breach)
3. Cannot provide reasonable analysis OR requires immediate human intervention

When tools fail, do NOT escalate. Provide analysis based on alert description alone.

Remember: Most alerts should result in analysis and recommendations, NOT escalation."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm_with_tools

    # Conversation state
    history = []

    # Initial input
    input_msg = alert_description.strip()

    for iteration in range(6):  # Safe upper limit
        response = chain.invoke({"input": input_msg, "history": history})

        # Add assistant response
        history.append(response)

        if not hasattr(response, "tool_calls") or not response.tool_calls:
            # Final answer
            final_answer = response.content
            break

        # Process tool calls
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            args = tool_call["args"]
            tool_id = tool_call["id"]

            try:
                if tool_name == "exa_search":
                    result = exa_search.invoke(args["query"])
                elif tool_name == "browse_web":
                    result = browse_web.invoke(args["url"])
                else:
                    result = "Error: Unknown tool"
            except Exception as e:
                result = f"Tool execution failed: {str(e)}"

            # Add tool result to history
            history.append(ToolMessage(content=result, tool_call_id=tool_id))

        # Next input is not needed — chain continues from history
        input_msg = ""  # Prevent re-sending original alert

    else:
        final_answer = "Error: Maximum iterations reached without conclusion."

    return final_answer

# Local testing
if __name__ == "__main__":
    from tensorlake.applications import run_local_application, Request

    alert = """
    Alert: High error rate detected in Tensorlake API service.
    Error rate increased from 0.1% to 5.2% in the last 5 minutes.
    Affected endpoints: /api/v1/query, /api/v1/ingest
    Error codes: 500, 503
    """

    print("Running Outage Agent locally...\n")
    print(f"Alert:\n{alert.strip()}\n")
    print("=" * 80)

    request: Request = run_local_application(outage_agent, alert.strip())
    output = request.output()
    # Handle Unicode encoding for Windows console
    try:
        print(output)
    except UnicodeEncodeError:
        # Fallback for Windows console that doesn't support all Unicode
        import sys
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        print(output)