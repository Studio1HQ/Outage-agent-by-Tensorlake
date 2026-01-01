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

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  # Fast, reliable, and widely available on Groq
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

Given an alert, your job is to:
- Quickly understand the issue
- Use tools to gather evidence (search for similar incidents, check status pages)
- Determine the most likely cause and resolution

Decision rules:
- If the alert itself clearly states that the situation is expected, scheduled, known, a false positive, or already resolved → treat it as low-risk and do NOT escalate.
  Example: "expected behavior during monthly index rebuild", "job completed successfully", "memory returning to normal"

- If the alert describes a transient issue that has already recovered (error rate back to normal, job finished, etc.) → confirm recovery and do NOT escalate.

- Escalate only if at least one of the following is true:
  1. High or potentially high impact on users (data loss, complete outage, critical service affected)
  2. The issue is ongoing / not resolved
  3. No clear explanation or root cause is apparent from the alert description
  4. Tools reveal conflicting or worrying information

- When tools fail (search or browse errors), do NOT automatically escalate. 
  Instead, rely on the information provided in the alert description. 
  If the alert gives a plausible benign explanation, accept it unless contradicted by other evidence.

Always end your response with a clear summary:
• What happened
• What was done (or why nothing was done)
• What to monitor next
• Only include "ESCALATION REQUIRED" if the issue genuinely needs human intervention based on the criteria above

Be practical: Most alerts can be analyzed and handled. Only escalate when truly necessary."""

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
    print(output)