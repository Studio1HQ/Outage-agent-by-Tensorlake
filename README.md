<div align="center">

<img src="https://raw.githubusercontent.com/Studio1HQ/Studio1HQ/main/assets/banners/Outage-agent-by-Tensorlake.webp" alt="Outage Agent on Tensorlake Cloud: A serverless on-call agent with a Streamlit UI" width="100%" />

<br />
<br />

# Outage Agent on Tensorlake Cloud

### A serverless on-call agent with a Streamlit UI

A tool-calling agent deployed on Tensorlake Cloud that analyses incident alerts with Groq, gathers evidence with Exa and HTTP GET, and decides whether to escalate. Includes a Streamlit UI and a CLI.

<br />

[![Built by Studio1](https://img.shields.io/badge/Built_by_Studio1-f97316?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNjAgMTYwIiBmaWxsPSJub25lIj48cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTAgMzVDMCAxNi42ODA3IDE0LjA3NDQgMS42NDg0NCAzMiAwLjEyNjk1M1YxNDFINTEuMDUyM0M1Mi40MzA4IDEzNy4zNDQgNTQuNzQ0NiAxMzMuNjg5IDU3Ljk5MzggMTMwLjAzM0M2MS4xNDQ2IDEyNi41MDggNjQuNjg5MiAxMjMuNDQgNjguNjI3NyAxMjAuODI5QzcyLjU2NjIgMTE4LjM0OSA3Ni4zNTY5IDExNi43ODIgODAgMTE2LjEyOVY4Ni43NTQ0Qzc1LjQ3MDggODcuOTI5MiA3MS4zODQ2IDg5LjY5MTkgNjcuNzQxNSA5Mi4wNDE1QzY0IDk0LjUyMjUgNjAuNzUwOCA5Ny40NiA1Ny45OTM4IDEwMC44NTRDNTYuNTM0NSAxMDIuNzIgNTUuMjU0NSAxMDQuNjU5IDU0LjE1MzkgMTA2LjY3MVYwSDEyNUMxNDQuMzMgMCAxNjAgMTUuNjY5OSAxNjAgMzVWMTI1QzE2MCAxNDQuMzMgMTQ0LjMzIDE2MCAxMjUgMTYwSDEyNFYxOEgxMDQuOTQ4QzEwMy41NjkgMjEuNjgxNiAxMDEuMjU1IDI1LjM2MjggOTguMDA2MiAyOS4wNDQ0Qzk0Ljg1NTQgMzIuNTk0MiA5MS4zMTA4IDM1LjY4NDEgODcuMzcyMyAzOC4zMTRDODMuNDMzOCA0MC44MTIgNzkuNjQzMSA0Mi4zODk2IDc2IDQzLjA0NzRWNzIuNjMwNEM4MC41MjkyIDcxLjQ0NzMgODQuNjE1NCA2OS42NzI0IDg4LjI1ODUgNjcuMzA1N0M5MiA2NC44MDc2IDk1LjI0OTIgNjEuODQ5MSA5OC4wMDYyIDU4LjQzMDdDOTkuNDY1NSA1Ni41NTEzIDEwMC43NDUgNTQuNTk4NiAxMDEuODQ2IDUyLjU3MjNWMTYwSDM1QzE1LjY3IDE2MCAwIDE0NC4zMyAwIDEyNVYzNVoiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4K)](https://studio1hq.com)
[![Built with Tensorlake](https://img.shields.io/badge/Built_with_Tensorlake-141414?style=for-the-badge)](https://tensorlake.ai)

[Tensorlake docs](https://docs.tensorlake.ai) &nbsp;·&nbsp; [Tensorlake](https://tensorlake.ai) &nbsp;·&nbsp; [More examples](https://github.com/Studio1HQ) &nbsp;·&nbsp; [studio1hq.com](https://studio1hq.com)

</div>

<br />

## Overview

This is an always-on, on-call style agent that runs as a serverless application on Tensorlake Cloud. You give it a plain-text alert. It analyses the alert, looks for similar incidents and checks status pages, then decides whether to handle the issue or escalate it to a human, and returns a structured summary.

The agent runs on Groq with a LangChain tool-calling loop. Its two tools, Exa semantic search and an HTTP GET fetcher, are Tensorlake `@function`s. A Streamlit app, a test script and a small CLI wrap the deployed agent.

## Features

- **Alert analysis**: Groq `llama-3.3-70b-versatile` at temperature 0.1 reads the alert and picks tools.
- **Evidence gathering**: Exa neural search (5 results by default) for similar outages, and an HTTP GET tool (timeout 10 to 15 seconds) for status pages and docs.
- **Smart escalation**: The agent handles expected, scheduled, resolved, transient or low-impact issues. It escalates for high user impact, ongoing issues, unclear cause or conflicting evidence. If a tool fails, it relies on the alert text rather than escalating by default.
- **Structured output**: A one-paragraph summary, a JSON record (incident ID, service, severity, status, root cause with confidence, actions, escalation decision) and a Slack-friendly version.
- **Streamlit UI**: Alert input, progress indicators, colour-coded results, analysis history with one-click reuse and a sidebar for API keys.
- **CLI and test script**: `outage_agent_cli.py` for local or remote runs, and `test_remote_outage_agent.py` for the deployed app.

## Tech stack

| Layer | Tool |
| --- | --- |
| Platform | [Tensorlake](https://tensorlake.ai) applications (cloud deployment) |
| LLM | [Groq](https://groq.com) (`llama-3.3-70b-versatile`) |
| Search | [Exa](https://exa.ai) |
| Orchestration | [LangChain](https://langchain.com) |
| UI | [Streamlit](https://streamlit.io) |
| CLI | Click |

## Getting started

### Prerequisites

- Python 3.11 (the container image uses `python:3.11-slim`; the dev container uses Python 3.11)
- A [Tensorlake](https://tensorlake.ai) API key
- A [Groq](https://console.groq.com) API key
- An [Exa](https://exa.ai) API key

### Installation

```bash
git clone https://github.com/Studio1HQ/Outage-agent-by-Tensorlake.git
cd Outage-agent-by-Tensorlake
pip install -r requirements.txt --upgrade
```

### Environment variables

| Variable | Description |
| --- | --- |
| `TENSORLAKE_API_KEY` | Your Tensorlake Cloud API key. |
| `GROQ_API_KEY` | Groq key for LLM inference. Stored as a Tensorlake secret for the deployed app. |
| `EXA_API_KEY` | Exa key for semantic search. Stored as a Tensorlake secret for the deployed app. |

```bash
export TENSORLAKE_API_KEY="your_tensorlake_api_key"
tensorlake secrets set GROQ_API_KEY "your_groq_api_key"
tensorlake secrets set EXA_API_KEY "your_exa_api_key"
```

### Run

Run the agent locally:

```bash
python outage_agent.py
```

Or use the Streamlit interface and open [http://localhost:8501](http://localhost:8501):

```bash
streamlit run streamlit_app.py
```

Deploy to Tensorlake Cloud and test the deployed agent:

```bash
tensorlake deploy outage_agent.py
python test_remote_outage_agent.py
python test_remote_outage_agent.py "Alert: Database connection pool exhausted"
```

CLI wrapper (needs `click`):

```bash
python outage_agent_cli.py local "Alert: Service degradation detected"
python outage_agent_cli.py remote "Alert: Service degradation detected"
python outage_agent_cli.py test
python outage_agent_cli.py local --file alert.txt
python outage_agent_cli.py local "Alert text" --json-output
```

Call it from Python:

```python
from tensorlake.applications import run_local_application, run_remote_application

# Local
request = run_local_application(outage_agent, "Alert: High error rate detected in API service")
print(request.output())

# Deployed
request = run_remote_application("outage_agent", "Alert: Service degradation detected")
print(request.output())
```

To change the model, edit the `ChatGroq(...)` call in `outage_agent()` in `outage_agent.py`. See `DEPLOYMENT.md` for detailed deployment steps and troubleshooting, and `QUICKSTART.md` for a short guide.

## How it works

1. `outage_agent` in `outage_agent.py` is the `@application()` entry point. It validates the alert text and builds the Groq model.
2. Two Tensorlake functions act as tools: `search_exa` (needs `EXA_API_KEY`) and `browse_url`. They are wrapped as LangChain tools inside the agent.
3. A tool-calling loop lets the model gather evidence, then it writes the summary and escalation decision.
4. The Streamlit app and CLI call the same application locally or on Tensorlake Cloud.

```text
.
├── outage_agent.py              # @application entry point and tools
├── streamlit_app.py             # Streamlit web interface
├── test_remote_outage_agent.py  # Remote test script
├── outage_agent_cli.py          # Optional CLI wrapper
├── requirements.txt
├── DEPLOYMENT.md
├── QUICKSTART.md
├── CONTRIBUTING.md
└── Assets/Logo.png
```

## Resources

- [Tensorlake docs](https://docs.tensorlake.ai): applications, secrets and deployment.
- [Tensorlake](https://tensorlake.ai): the platform used here.
- [Groq](https://groq.com): fast LLM inference.
- [Exa](https://exa.ai): semantic search API.
- [Streamlit](https://streamlit.io): the UI framework.
- [CONTRIBUTING.md](CONTRIBUTING.md): contribution guidelines.

## License

Released under the [MIT License](LICENSE).

<br />

---

<div align="center">

<a href="https://studio1hq.com">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Studio1HQ/website/main/brand/studio1-logo-on-dark.svg" />
    <img src="https://raw.githubusercontent.com/Studio1HQ/website/main/brand/studio1-logo-on-light.svg" alt="Studio1" width="160" />
  </picture>
</a>

Built by **[Studio1](https://studio1hq.com)**, the technical content and DevRel partner for devtool teams. Made with [Tensorlake](https://tensorlake.ai).<br />
Browse more open-source examples at [github.com/Studio1HQ](https://github.com/Studio1HQ).

[![Website](https://img.shields.io/badge/studio1hq.com-0b0807?style=for-the-badge&logo=googlechrome&logoColor=white)](https://studio1hq.com)
[![Book a call](https://img.shields.io/badge/Book_a_strategy_call-f97316?style=for-the-badge&logo=googlecalendar&logoColor=white)](https://cal.com/studio1/collab)
[![X](https://img.shields.io/badge/%40Studio1HQ-141414?style=for-the-badge&logo=x&logoColor=white)](https://x.com/Studio1HQ)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0a66c2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/company/studio1hq/)

<sub><a href="https://studio1hq.com">studio1hq.com</a> · Technical content, docs, video and DevRel for devtools</sub>

</div>
