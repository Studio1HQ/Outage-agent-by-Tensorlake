# Outage Agent - Deployment Instructions

This document provides step-by-step instructions for deploying the Outage Agent to Tensorlake Cloud.

## Prerequisites

1. **Tensorlake CLI installed**
   ```bash
   pip install tensorlake --upgrade
   ```

2. **Tensorlake API Key**
   - Set the `TENSORLAKE_API_KEY` environment variable
   - Or configure it via Tensorlake CLI

3. **API Keys for External Services**
   - Groq API Key (for LLM inference)
   - Exa API Key (for semantic search)

## Deployment Steps

### 1. Set Environment Variables

Set your Tensorlake API key:

```bash
# Windows PowerShell
$env:TENSORLAKE_API_KEY = "your_tensorlake_api_key_here"

# Windows CMD
set TENSORLAKE_API_KEY=your_tensorlake_api_key_here

# Linux/Mac
export TENSORLAKE_API_KEY="your_tensorlake_api_key_here"
```

### 2. Set Secrets

Configure the required API keys as Tensorlake secrets:

```bash
# Set Groq API Key
tensorlake secrets set GROQ_API_KEY=your_groq_api_key_here

# Set Exa API Key
tensorlake secrets set EXA_API_KEY=your_exa_api_key_here
```

### 3. Deploy the Application

Deploy the outage agent to Tensorlake Cloud:

```bash
tensorlake deploy outage_agent.py
```

The deployment process will:
- Upload your application code
- Create the application on Tensorlake Cloud
- Set up the HTTP endpoint for remote execution

### 4. Verify Deployment

After deployment, you should see output indicating:
- Application name (e.g., `outage_agent`)
- Deployment status
- Endpoint URL (if provided)

## Testing

### Local Testing

Test the agent locally before deploying:

```bash
python outage_agent.py
```

This will run the agent with a sample alert and display the response.

### Remote Testing

Test the deployed agent using the test script:

```bash
python test_remote_outage_agent.py
```

Or with a custom alert:

```bash
python test_remote_outage_agent.py "Alert: Service degradation detected in region us-east-1"
```

## Application Structure

The application follows Tensorlake's standard structure:

- **Main file**: `outage_agent.py`
  - `@application` decorator on the entrypoint function
  - `@function` decorators on tool functions
  - Local execution block for testing

- **Test file**: `test_remote_outage_agent.py`
  - Uses `run_remote_application` for remote execution
  - Handles request submission and output retrieval

## Configuration

### LLM Model Selection

The agent uses Groq's `llama-3.3-70b-versatile` model by default. To change the model, edit the `get_llm()` function in `outage_agent.py`:

```python
return ChatGroq(
    model="llama-3.3-70b-versatile",  # Change model here (e.g., "mixtral-8x7b-instant")
    groq_api_key=api_key,
    temperature=0.1,
)
```

### Tool Configuration

- **Exa Search**: Configured with `num_results=5` by default. Adjust in `search_similar_outages` function.
- **HTTP GET**: Configured with `timeout=10` seconds. Adjust in `fetch_url` function.

## Monitoring

After deployment, monitor the agent through:
- Tensorlake Cloud dashboard
- Application logs (if available)
- Response times and error rates

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure all secrets are set: `tensorlake secrets list`
   - Verify environment variables are accessible

2. **Deployment Failures**
   - Check Tensorlake API key is set correctly
   - Verify network connectivity
   - Review error messages in deployment output

3. **Runtime Errors**
   - Check application logs
   - Verify tool functions are properly decorated with `@function`
   - Ensure all dependencies are included

### Getting Help

- Check Tensorlake documentation: https://github.com/tensorlakeai/tensorlake
- Review example applications: https://github.com/tensorlakeai/tensorlake/tree/main/examples
- Contact Tensorlake support if issues persist

## CLI Wrapper (Optional)

A CLI wrapper is provided for easier interaction with the agent:

```bash
# Install CLI dependencies
pip install click

# Run locally
python outage_agent_cli.py local "Alert: Service degradation detected"

# Run remotely
python outage_agent_cli.py remote "Alert: Service degradation detected"

# Run test alert
python outage_agent_cli.py test

# See help
python outage_agent_cli.py --help
```

## Next Steps

- Set up alerting integration (e.g., webhook from monitoring system)
- Configure custom escalation workflows
- Add additional tools as needed
- Implement monitoring and alerting for the agent itself

