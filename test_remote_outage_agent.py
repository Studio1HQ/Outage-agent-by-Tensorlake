"""
Test script for remote execution of the Outage Agent on Tensorlake Cloud.

This script demonstrates how to invoke the deployed outage_agent application
remotely using the Tensorlake Python SDK.
"""

import json
import sys
from tensorlake.applications import run_remote_application


def test_remote_agent(alert_description: str = None):
    """
    Test the remote outage agent with an alert description.
    
    Args:
        alert_description: Alert description to send to the agent.
                          If None, uses a default test alert.
    """
    if alert_description is None:
        alert_description = """
        Alert: High error rate detected in Tensorlake API service.
        Error rate increased from 0.1% to 5.2% in the last 5 minutes.
        Affected endpoints: /api/v1/query, /api/v1/ingest
        Error codes: 500, 503
        """
    
    print("="*80)
    print("TESTING REMOTE OUTAGE AGENT")
    print("="*80)
    print(f"\nAlert Description:\n{alert_description}\n")
    print("Sending request to Tensorlake Cloud...")
    print("-"*80)
    
    try:
        # Use the simple run_remote_application pattern
        request = run_remote_application("outage_agent", alert_description)
        
        print("Request submitted. Waiting for response...")
        
        # Get output (handles waiting internally)
        output = request.output()
        
        print("\n" + "="*80)
        print("AGENT RESPONSE")
        print("="*80)
        print(json.dumps(output, indent=2))
        
        # Extract key information
        if isinstance(output, dict):
            status = output.get("status", "unknown")
            agent_response = output.get("agent_response", "")
            summary = output.get("summary", {})
            
            print("\n" + "="*80)
            print("SUMMARY")
            print("="*80)
            print(f"Status: {status}")
            
            if summary.get("escalation"):
                print("\n⚠️  ESCALATION REQUIRED")
                print(f"Reason: {summary.get('escalation_reason', 'N/A')}")
            else:
                print("\n✓ Issue handled by agent")
            
            if agent_response:
                print(f"\nAgent Response:\n{agent_response}")
        
        return output
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Allow alert description to be passed as command-line argument
    if len(sys.argv) > 1:
        alert_description = " ".join(sys.argv[1:])
    else:
        alert_description = None
    
    test_remote_agent(alert_description)




