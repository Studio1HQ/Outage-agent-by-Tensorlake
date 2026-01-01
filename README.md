# Outage Agent

A serverless AI agent deployed on Tensorlake Cloud that simulates an always-on on-call engineer for Tensorlake services. Features a modern Streamlit web interface for easy interaction and management.

## Overview

The Outage Agent automatically analyzes alerts, gathers evidence using semantic search and web browsing, and either resolves low-risk issues or escalates uncertain/high-impact situations to human engineers. The agent uses intelligent decision-making to handle routine issues while escalating only when truly necessary.

## Features

- **Intelligent Analysis**: Uses Groq LLM (llama-3.3-70b-versatile) for fast inference and decision-making
- **Evidence Gathering**: 
  - Semantic search via Exa for similar outages and root causes
  - HTTP GET tool for checking status pages and documentation
- **Smart Escalation**: Only escalates when truly necessary (high impact, ongoing issues, or unclear causes)
- **Structured Output**: Provides clear summaries of what happened, what was done, and what to monitor
- **Modern Web UI**: Beautiful Streamlit interface with:
  - Real-time alert analysis
  - Analysis history with one-click reuse
  - Color-coded results (gradient cards for different sections)
  - Compact, expandable history items

## Architecture

- **Platform**: Tensorlake Applications (deployed to Tensorlake Cloud)
- **LLM**: Groq (llama-3.3-70b-versatile)
- **Tools**: Exa search, HTTP GET (all implemented as `@function` decorators)
- **Orchestration**: LangChain for prompt templates and agent loops

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### 2. Set Up Secrets

```bash
# Set Tensorlake API Key
export TENSORLAKE_API_KEY="your_tensorlake_api_key"

# Set service API keys
tensorlake secrets set GROQ_API_KEY "your_groq_api_key"
tensorlake secrets set EXA_API_KEY "your_exa_api_key"
```

### 3. Test Locally

**Option A: Run the agent directly**
```bash
python outage_agent.py
```

**Option B: Use the Streamlit web interface (Recommended)**
```bash
streamlit run streamlit_app.py
```
Then open your browser to `http://localhost:8501`

### 4. Deploy to Tensorlake Cloud

```bash
tensorlake deploy outage_agent.py
```

### 5. Test Remotely

```bash
python test_remote_outage_agent.py
```

## Usage

### Local Execution

```python
from tensorlake.applications import run_local_application, Request

alert = "Alert: High error rate detected in API service"
request: Request = run_local_application(outage_agent, alert)
output = request.output()
print(output)
```

### Remote Execution

```python
from tensorlake.applications import run_remote_application

alert = "Alert: Service degradation detected"
request = run_remote_application("outage_agent", alert)
output = request.output()
print(output)
```

### Web Interface (Streamlit)

The easiest way to interact with the agent is through the Streamlit web interface:

```bash
streamlit run streamlit_app.py
```

**Features:**
- Enter alerts in a clean text input
- Real-time analysis with progress indicators
- Color-coded results with gradient cards
- Analysis history with one-click reuse
- Sidebar configuration for API keys

### Command Line

**Using the test script:**
```bash
# Test with default alert
python test_remote_outage_agent.py

# Test with custom alert
python test_remote_outage_agent.py "Alert: Database connection pool exhausted"
```

**Using the CLI wrapper (optional):**
```bash
# Install CLI dependencies
pip install click

# Run locally
python outage_agent_cli.py local "Alert: Service degradation detected"

# Run remotely
python outage_agent_cli.py remote "Alert: Service degradation detected"

# Run test alert
python outage_agent_cli.py test

# Read alert from file
python outage_agent_cli.py local --file alert.txt

# JSON output
python outage_agent_cli.py local "Alert text" --json-output
```

## Agent Behavior

The agent follows intelligent decision-making rules:

1. **Analyze**: Quickly analyzes the alert description
2. **Gather Evidence**: Uses tools to find similar incidents and check relevant URLs
3. **Smart Decision Making**: 
   - **Handles** expected, scheduled, known, or already resolved issues
   - **Handles** transient issues that have recovered
   - **Handles** routine, low-impact problems with analysis and recommendations
   - **Escalates** only when:
     - High impact on users (data loss, complete outage, critical service)
     - Issue is ongoing/not resolved
     - No clear explanation from alert description
     - Tools reveal conflicting or worrying information
4. **Tool Failure Handling**: When tools fail, relies on alert description rather than automatically escalating
5. **Structured Summary**: Provides clear output with:
   - What happened
   - What was done (or why nothing was done)
   - What should be monitored next
   - Escalation reason (if escalated)

## Project Structure

```
.
├── outage_agent.py              # Main application with @application decorator
├── streamlit_app.py             # Streamlit web interface (recommended)
├── test_remote_outage_agent.py  # Remote testing script
├── outage_agent_cli.py          # Optional CLI wrapper (requires click)
├── requirements.txt             # Python dependencies
├── DEPLOYMENT.md               # Detailed deployment instructions
├── QUICKSTART.md               # Quick start guide
├── Assets/
│   └── Logo.png                # Tensorlake logo for UI
└── README.md                   # This file
```

## Configuration

### LLM Model

The agent uses Groq's `llama-3.3-70b-versatile` model by default. To change the model, edit the `outage_agent()` function in `outage_agent.py`:

```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Change to "mixtral-8x7b-instant" or other available models
    groq_api_key=os.environ["GROQ_API_KEY"],
    temperature=0.1,
)
```

### Tool Settings

- **Exa Search**: Default `num_results=5`
- **HTTP GET**: Default `timeout=10` seconds

## API Keys

The following API keys are required:

- **TENSORLAKE_API_KEY**: Your Tensorlake Cloud API key
- **GROQ_API_KEY**: Groq API key for LLM inference
- **EXA_API_KEY**: Exa API key for semantic search

See `DEPLOYMENT.md` for detailed setup instructions.

## Troubleshooting

See `DEPLOYMENT.md` for common issues and troubleshooting steps.

## License

This project is part of the Tensorlake ecosystem.

