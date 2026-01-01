# Quick Start Guide

Get the Outage Agent up and running in 5 minutes.

## 1. Install Dependencies

```bash
pip install -r requirements.txt --upgrade
```

## 2. Set API Keys

```bash
# Set Tensorlake API Key (Windows PowerShell)
$env:TENSORLAKE_API_KEY = "your_tensorlake_api_key_here"

# Set secrets for the application
tensorlake secrets set GROQ_API_KEY=your_groq_api_key_here
tensorlake secrets set EXA_API_KEY=your_exa_api_key_here
```

## 3. Test Locally

```bash
python outage_agent.py
```

## 4. Deploy to Tensorlake Cloud

```bash
tensorlake deploy outage_agent.py
```

## 5. Test Remotely

```bash
python test_remote_outage_agent.py
```

## That's It!

Your Outage Agent is now deployed and ready to handle alerts.

### Next Steps

- Integrate with your monitoring system (webhook to the deployed endpoint)
- Customize the agent behavior in `outage_agent.py`
- Add more tools as needed
- Monitor agent performance

### Example Usage

**Local:**
```python
from tensorlake.applications import run_local_application
from outage_agent import outage_agent

alert = "Alert: High error rate in API service"
request = run_local_application(outage_agent, alert)
output = request.output()
print(output)
```

**Remote:**
```python
from tensorlake.applications import run_remote_application

alert = "Alert: Service degradation detected"
request = run_remote_application("outage_agent", alert)
output = request.output()
print(output)
```

**CLI:**
```bash
python outage_agent_cli.py local "Alert: Database connection issues"
python outage_agent_cli.py remote "Alert: API timeout errors"
```

For detailed information, see `README.md` and `DEPLOYMENT.md`.




