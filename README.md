# Outage Agent

A serverless AI agent deployed on Tensorlake Cloud that simulates an always-on on-call engineer for Tensorlake services.

## Overview

The Outage Agent automatically analyzes alerts, gathers evidence using semantic search and web browsing, and either resolves low-risk issues or escalates uncertain/high-impact situations to human engineers.

## Features

- **Intelligent Analysis**: Uses Groq LLM for fast inference and decision-making
- **Evidence Gathering**: 
  - Semantic search via Exa for similar outages and root causes
  - HTTP GET tool for checking status pages and documentation
- **Smart Escalation**: Escalates only when truly necessary (high impact, unclear causes, or ongoing issues)
- **Structured Output**: Provides clear summaries of what happened, what was done, and what to monitor
- **Web UI**: Beautiful Streamlit interface for interactive alert analysis
- **History Management**: Track and reuse previous analyses

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

```bash
python outage_agent.py
```

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

### Web UI (Streamlit)

Run the interactive web interface:

```bash
streamlit run streamlit_app.py
```

The UI provides:
- Interactive alert input
- Real-time agent analysis
- Analysis history with click-to-reuse
- Beautiful, modern interface

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

The agent follows strict behavioral rules:

1. **Analyze**: Quickly analyzes the alert description
2. **Gather Evidence**: Uses tools to find similar incidents and check relevant URLs
3. **Decide**: 
   - Handles expected, scheduled, known, or already resolved issues without escalation
   - Confirms recovery for transient issues that have recovered
   - Escalates only for high impact, ongoing issues, unclear causes, or conflicting information
4. **Never Guess**: Always prioritizes service stability
5. **Structured Summary**: Provides clear output with:
   - What happened
   - What was done (or why nothing was done)
   - What should be monitored next
   - Escalation reason (if escalated)

## Project Structure

```
.
├── outage_agent.py              # Main application with @application decorator
├── streamlit_app.py             # Streamlit web UI for the agent
├── test_remote_outage_agent.py  # Remote testing script
├── outage_agent_cli.py          # Optional CLI wrapper (requires click)
├── requirements.txt             # Python dependencies
├── Assets/
│   └── Logo.png                # Tensorlake logo
├── DEPLOYMENT.md               # Detailed deployment instructions
├── QUICKSTART.md               # Quick start guide
└── README.md                   # This file
```

## Configuration

### LLM Model

Edit the model in `outage_agent.py` to change the Groq model:

```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Change model here (e.g., "mixtral-8x7b-instant")
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

