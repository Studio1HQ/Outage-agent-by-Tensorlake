"""
Streamlit UI for the Outage Agent - Advanced Design
"""
import streamlit as st
import os
from datetime import datetime
from outage_agent import outage_agent
from tensorlake.applications import run_local_application, Request

# Page config
st.set_page_config(
    page_title="Outage Agent",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "alert_text" not in st.session_state:
    st.session_state.alert_text = ""

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Make sidebar narrower */
    section[data-testid="stSidebar"] {
        min-width: 250px !important;
        max-width: 280px !important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #3b82f6;
        padding: 1.2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        border: 1px solid #2563eb;
    }
    .feature-box h3 {
        color: white;
        margin-top: 0;
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
    }
    .feature-box p {
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.95);
    }
    .feature-box ul {
        margin-top: 0.3rem;
        padding-left: 1.2rem;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.9);
    }
    .feature-box li {
        margin-bottom: 0.2rem;
        color: rgba(255, 255, 255, 0.9);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    .history-item {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Logo
    try:
        st.image("Assets/Logo.png", use_container_width=True)
    except:
        st.markdown("### 🚨 Tensorlake")
    
    st.markdown("---")
    
    # API Configuration
    st.markdown("### 🔧 API Configuration")
    
    groq_key = st.text_input(
        "GROQ API Key", 
        type="password", 
        value=os.getenv("GROQ_API_KEY", ""),
        help="Your Groq API key for LLM inference"
    )
    exa_key = st.text_input(
        "EXA API Key", 
        type="password", 
        value=os.getenv("EXA_API_KEY", ""),
        help="Your Exa API key for semantic search"
    )
    tensorlake_key = st.text_input(
        "Tensorlake API Key", 
        type="password", 
        value=os.getenv("TENSORLAKE_API_KEY", ""),
        help="Your Tensorlake API key"
    )
    
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    if exa_key:
        os.environ["EXA_API_KEY"] = exa_key
    if tensorlake_key:
        os.environ["TENSORLAKE_API_KEY"] = tensorlake_key
    
    if st.button("💾 Save API Keys", use_container_width=True):
        st.success("API keys saved to session!")
    
    st.markdown("---")
    
    # History Section in Sidebar (moved above Key Capabilities)
    st.markdown("### 📜 Analysis History")
    
    if st.session_state.history:
        st.caption(f"Total: {len(st.session_state.history)} analyses")
        
        # Clear history button
        if st.button("🗑️ Clear History", use_container_width=True, type="secondary"):
            st.session_state.history = []
            st.rerun()
        
        st.markdown("---")
        
        # Display history (newest first, limited to 10) - ChatGPT style
        for idx, entry in enumerate(reversed(st.session_state.history[-10:])):
            history_idx = len(st.session_state.history) - idx
            import re
            import json
            
            # Check escalation status from JSON if available
            is_escalation = False
            response_text = entry['response']
            
            # Try to parse JSON from response
            json_match = re.search(r'\{[^{}]*"incident_id"[^{}]*\}', response_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{.*"should_escalate".*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    json_str = json_match.group(0)
                    json_str = re.sub(r'```json\s*', '', json_str)
                    json_str = re.sub(r'```\s*', '', json_str)
                    json_data = json.loads(json_str)
                    is_escalation = json_data.get('should_escalate', False) == True
                except:
                    # Fallback to text search if JSON parsing fails
                    is_escalation = "ESCALATION REQUIRED" in response_text.upper() and "not required" not in response_text.lower()
            else:
                # Fallback to text search
                is_escalation = "ESCALATION REQUIRED" in response_text.upper() and "not required" not in response_text.lower()
            
            time_str = entry['timestamp'].split()[1]
            alert_preview = entry['alert'][:60] + "..." if len(entry['alert']) > 60 else entry['alert']
            
            # Extract escalation reason or summary
            escalation_match = re.search(r'ESCALATION REQUIRED[:\*\s]*\n?(.+?)(?=\n\n|$)', response_text, re.IGNORECASE | re.DOTALL)
            what_happened_match = re.search(r'(?:What happened|What Happened)[:\*\s]*\n?(.+?)(?=\n\n|\n\*\*|What was|What to monitor|ESCALATION|$)', response_text, re.IGNORECASE | re.DOTALL)
            
            # Get brief summary
            brief_summary = ""
            if is_escalation and escalation_match:
                brief_summary = escalation_match.group(1).strip()[:80] + "..." if len(escalation_match.group(1)) > 80 else escalation_match.group(1).strip()
            elif what_happened_match:
                brief_summary = what_happened_match.group(1).strip()[:80] + "..." if len(what_happened_match.group(1)) > 80 else what_happened_match.group(1).strip()
            
            # Clean up
            brief_summary = re.sub(r'\s*(No|No escalation|No action needed|N/A|None)\s*$', '', brief_summary, flags=re.IGNORECASE)
            brief_summary = re.sub(r'\s*[•·]\s*$', '', brief_summary)
            
            # Compact display - ChatGPT style
            status_badge = "🚨 Escalated" if is_escalation else "✓ Handled"
            
            # Collapsible item
            with st.expander(f"#{history_idx} - {time_str} | {status_badge}", expanded=False):
                st.caption(f"**Alert:** {alert_preview}")
                
                if brief_summary:
                    if is_escalation:
                        st.warning(f"**Reason:** {brief_summary}")
                    else:
                        st.info(f"**Summary:** {brief_summary}")
                
                # Reuse button
                if st.button(f"↻ Reuse Alert", key=f"reuse_{idx}", use_container_width=True):
                    st.session_state.alert_text = entry['alert']
                    st.rerun()
    else:
        st.info("No history yet. Run an analysis to see it here.")
    
    st.markdown("---")
    
    # Key Capabilities
    st.markdown("### 🔑 Key Capabilities")
    st.markdown("""
    - **Fast Inference**: Groq LLM for rapid analysis
    - **Semantic Search**: Exa for finding similar incidents
    - **Evidence Gathering**: Automated status page checks
    - **Smart Escalation**: AI-powered decision making
    - **Structured Output**: Clear summaries and recommendations
    """)
    
    st.markdown("---")
    st.markdown(
        """
       <div style='text-align: center; color: #666; font-size: 0.8rem;'>
    Developed with ❤️ by <a href="https://www.linkedin.com/in/arindam2004" target="_blank" style="color: #666; text-decoration: underline;">Arindam</a>
</div>
        """,
        unsafe_allow_html=True
    )

# Main content area
# Title and description
st.title("🚨 Outage Agent by Tensorlake - AI On-Call Engineer")


# Header card with gradient (matching reference design exactly)
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; color: white;">
    <h2 style="color: white; margin-bottom: 0.8rem; font-size: 1.5rem; font-weight: 600; line-height: 1.3;">✨ Advanced interface for your deployed Outage Agent on Tensorlake Cloud.</h2>
    <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.95rem; line-height: 1.5; margin: 0;">Generate professional outage analysis from your alerts. Get comprehensive incident investigation, similar incident search, and intelligent escalation recommendations with structured action items.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Input section
st.markdown("**Enter Alert Description:**")

alert_text = st.text_input(
    "Alert Description",
    value=st.session_state.alert_text,
    placeholder="Enter the alert description here...",
    help="Describe the outage, error, or incident that needs investigation",
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 5])

with col1:
    run_button = st.button("🚀 Analyze Alert", type="primary", use_container_width=True)

with col2:
    clear_button = st.button("Clear Input", use_container_width=True)

if clear_button:
    st.session_state.alert_text = ""
    st.rerun()

# Run the agent
if run_button and alert_text.strip():
    # Validate API keys
    if not os.getenv("GROQ_API_KEY"):
        st.error("❌ GROQ_API_KEY not set. Please set it in the sidebar.")
        st.stop()
    
    if not os.getenv("EXA_API_KEY"):
        st.error("❌ EXA_API_KEY not set. Please set it in the sidebar.")
        st.stop()
    
    if not os.getenv("TENSORLAKE_API_KEY"):
        st.warning("⚠️ TENSORLAKE_API_KEY not set. Local execution may still work.")
    
    # Show progress
    with st.spinner("🤖 Agent is analyzing the alert and gathering evidence..."):
        try:
            # Run the agent locally
            request: Request = run_local_application(outage_agent, alert_text.strip())
            
            # Try to get output - this will raise an exception if there's an error
            try:
                output = request.output()
            except Exception as output_error:
                # Try to get more details from the request object
                error_details = str(output_error)
                
                # Check if request has error attribute
                if hasattr(request, '_error') and request._error:
                    error_details = str(request._error)
                    # Try to get more info from the error
                    if hasattr(request._error, '__dict__'):
                        error_details += f"\n\nError details: {request._error.__dict__}"
                
                # Check for specific error types
                if "rate limit" in error_details.lower() or "429" in error_details:
                    st.error("❌ **Rate Limit Error**")
                    st.warning("""
                    Your Groq API has hit the rate limit. Please:
                    - Wait a few minutes and try again
                    - Or upgrade your Groq account at https://console.groq.com/settings/billing
                    """)
                    st.stop()
                else:
                    raise output_error
            
            # Store in history
            history_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "alert": alert_text.strip(),
                "response": str(output)
            }
            st.session_state.history.append(history_entry)
            
            st.success("✅ Analysis Complete!")
            st.markdown("---")
            
            # Display results (beautified, only once)
            output_text = str(output)
            
            import re
            import json
            
            # Parse the new structured output format first to determine escalation status
            # 2. Extract JSON structured output (check this first for accurate escalation status)
            json_match = re.search(r'\{[^{}]*"incident_id"[^{}]*\}', output_text, re.DOTALL)
            if not json_match:
                # Try broader JSON match
                json_match = re.search(r'\{.*"should_escalate".*\}', output_text, re.DOTALL)
            
            # Determine escalation status from JSON if available, otherwise fallback to text search
            is_escalation = False
            if json_match:
                try:
                    json_str = json_match.group(0)
                    json_str = re.sub(r'```json\s*', '', json_str)
                    json_str = re.sub(r'```\s*', '', json_str)
                    json_data = json.loads(json_str)
                    is_escalation = json_data.get('should_escalate', False) == True
                except:
                    # If JSON parsing fails, fallback to careful text search
                    is_escalation = "ESCALATION REQUIRED" in output_text.upper() and "not required" not in output_text.lower()
            else:
                # Fallback: check text but be careful about false positives
                is_escalation = "ESCALATION REQUIRED" in output_text.upper() and "not required" not in output_text.lower()
            
            # Show escalation banner only if escalation is actually required
            if is_escalation:
                st.error("🚨 **ESCALATION REQUIRED**")
            else:
                st.success("✓ **Issue Handled by Agent**")
            
            st.markdown("---")
            
            # Beautified response display
            st.markdown("### 📊 Analysis Results")
            
            # Parse the new structured output format
            # 1. Extract one-paragraph summary
            summary_match = re.search(r'(?:Summary|1\.\s*ONE-PARAGRAPH SUMMARY)[:\*\s]*\n?(.+?)(?=\n\n|2\.|STRUCTURED|$)', output_text, re.IGNORECASE | re.DOTALL)
            summary_text = None
            if summary_match:
                summary_text = summary_match.group(1).strip()
            else:
                # Try to find first paragraph if no explicit summary marker
                lines = output_text.split('\n')
                first_para = []
                for line in lines[:5]:  # Check first 5 lines
                    if line.strip() and not line.strip().startswith(('{', '[', '2.', '3.', '🚨')):
                        first_para.append(line.strip())
                if first_para:
                    summary_text = ' '.join(first_para)
            
            # 3. Extract Slack-friendly condensed version
            slack_match = re.search(r'🚨\s*Incident.*?Escalation:.*?(?=\n\n|$)', output_text, re.DOTALL)
            
            # Display Summary (for humans)
            if summary_text:
                # Clean up the summary
                summary_text = re.sub(r'^\*\*', '', summary_text)
                summary_text = re.sub(r'\*\*$', '', summary_text)
                summary_text = summary_text.strip()
                
                st.markdown("#### 📝 Summary")
                st.info(summary_text)
            
            # Display Structured JSON (for systems)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    # Clean up JSON string (remove markdown code blocks if present)
                    json_str = re.sub(r'```json\s*', '', json_str)
                    json_str = re.sub(r'```\s*', '', json_str)
                    json_data = json.loads(json_str)
                    
                    st.markdown("#### 🔍 Structured Decision Output")
                    
                    # Display key information in cards
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Service", json_data.get('service', 'N/A'))
                    with col2:
                        severity = json_data.get('severity', 'unknown')
                        severity_colors = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
                        st.metric("Severity", f"{severity_colors.get(severity, '⚪')} {severity}")
                    with col3:
                        status = json_data.get('status', 'unknown')
                        st.metric("Status", status)
                    with col4:
                        should_escalate = json_data.get('should_escalate', False)
                        st.metric("Escalation", "⚠️ Required" if should_escalate else "✅ Not Required")
                    
                    # Display Root Cause, Actions Taken, and Verification in a beautified table
                    st.markdown("**Details:**")
                    
                    # Build table data
                    table_data = []
                    
                    # Root Cause row
                    if json_data.get('root_cause'):
                        table_data.append({
                            "Field": "Root Cause",
                            "Details": json_data.get('root_cause')
                        })
                    
                    # Actions Taken row
                    if json_data.get('actions_taken'):
                        actions = json_data.get('actions_taken', [])
                        if isinstance(actions, list) and len(actions) > 0:
                            # Format actions with line breaks using markdown
                            actions_text = "\n\n".join([f"• {action}" for action in actions])
                            table_data.append({
                                "Field": "Actions Taken",
                                "Details": actions_text
                            })
                    
                    # Verification row
                    if json_data.get('verification'):
                        verification = json_data.get('verification', {})
                        if isinstance(verification, dict) and len(verification) > 0:
                            # Format verification with line breaks using markdown
                            verification_text = "\n\n".join([f"• {key}: {value}" for key, value in verification.items()])
                            table_data.append({
                                "Field": "Verification",
                                "Details": verification_text
                            })
                    
                    # Display as a clean table using columns
                    if table_data:
                        # Create a styled container for the table
                        for row in table_data:
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.markdown(f"**{row['Field']}:**")
                            with col2:
                                # Split by double newline to show each bullet on new line
                                details = row['Details']
                                if '\n\n' in details:
                                    # Split and display each line separately
                                    lines = details.split('\n\n')
                                    for line in lines:
                                        if line.strip():
                                            st.markdown(line)
                                else:
                                    st.markdown(details)
                            st.markdown("---")
                    
                    # Display next recommendation
                    if json_data.get('next_recommendation'):
                        st.markdown("**Next Recommendation:**")
                        st.warning(json_data.get('next_recommendation'))
                    
                    # Show raw JSON in expander
                    with st.expander("📋 View Raw JSON"):
                        st.json(json_data)
                        
                except json.JSONDecodeError:
                    st.warning("Could not parse JSON output. Displaying raw text.")
                    st.code(json_match.group(0))
            
            # Display Slack-friendly condensed version
            if slack_match:
                st.markdown("#### 💬 Slack Summary")
                slack_text = slack_match.group(0).strip()
                st.code(slack_text, language=None)
            
            # If no structured format found, try to parse old format
            if not summary_match and not json_match:
                # Fallback to old parsing logic
                sections = {}
                
                def clean_section_text(text):
                    if not text:
                        return ""
                    text = re.sub(r'\s*(No|No escalation|No action needed|N/A|None)\s*$', '', text, flags=re.IGNORECASE)
                    text = re.sub(r'\s*[•·]\s*$', '', text)
                    text = re.sub(r'\s*[-*]\s*$', '', text)
                    return text.strip()
                
                what_happened = re.search(r'(?:What happened|What Happened)[:\*\s]*\n?(.+?)(?=\n\n|\n\*\*|What was|What to monitor|ESCALATION|$)', output_text, re.IGNORECASE | re.DOTALL)
                if what_happened:
                    sections['what_happened'] = clean_section_text(what_happened.group(1))
                
                what_was_done = re.search(r'(?:What was done|What Was Done)[:\*\s]*\n?(.+?)(?=\n\n|\n\*\*|What to monitor|ESCALATION|$)', output_text, re.IGNORECASE | re.DOTALL)
                if what_was_done:
                    sections['what_was_done'] = clean_section_text(what_was_done.group(1))
                
                what_to_monitor = re.search(r'(?:What to monitor next|What to Monitor Next|What should be monitored)[:\*\s]*\n?(.+?)(?=\n\n|\n\*\*|ESCALATION|$)', output_text, re.IGNORECASE | re.DOTALL)
                if what_to_monitor:
                    sections['what_to_monitor'] = clean_section_text(what_to_monitor.group(1))
                
                escalation = re.search(r'ESCALATION REQUIRED[:\*\s]*\n?(.+?)(?=\n\n|$)', output_text, re.IGNORECASE | re.DOTALL)
                if escalation:
                    sections['escalation'] = escalation.group(1).strip()
                
                if sections.get('what_happened'):
                    st.markdown("#### 📋 What Happened")
                    st.info(sections['what_happened'])
                
                if sections.get('what_was_done'):
                    st.markdown("#### ✅ What Was Done")
                    st.success(sections['what_was_done'])
                
                if sections.get('what_to_monitor'):
                    st.markdown("#### 👀 What to Monitor Next")
                    st.warning(sections['what_to_monitor'])
                
                if sections.get('escalation'):
                    st.markdown("#### 🚨 ESCALATION REQUIRED")
                    st.error(sections['escalation'])
                
                if not sections:
                    # Display raw output
                    st.markdown(output_text)
                
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            st.error(f"❌ Error running agent: {error_type}")
            
            # Show more detailed error information
            with st.expander("🔍 Error Details", expanded=True):
                st.code(error_msg, language="text")
                st.markdown("**Full Traceback:**")
                st.exception(e)
                
                # Try to get more details from the request if available
                try:
                    if 'request' in locals():
                        st.markdown("**Request Object Info:**")
                        if hasattr(request, '_error'):
                            st.code(f"Request._error: {request._error}", language="text")
                        if hasattr(request, '__dict__'):
                            st.code(f"Request attributes: {list(request.__dict__.keys())}", language="text")
                except Exception as req_err:
                    st.text(f"Could not inspect request object: {req_err}")
                
                st.markdown("**Troubleshooting Steps:**")
                
                # Check for specific error types
                if "rate limit" in error_msg.lower() or "429" in error_msg or "RateLimitError" in error_type:
                    st.warning("""
                    **Rate Limit Error Detected:**
                    - Your Groq API has hit the rate limit
                    - Wait a few minutes and try again
                    - Or upgrade your Groq account at https://console.groq.com/settings/billing
                    """)
                elif "function_error" in error_msg.lower() or "FunctionError" in error_type:
                    st.warning("""
                    **Function Execution Error:**
                    - The agent function encountered an error during execution
                    - This could be due to:
                      * Invalid API keys
                      * Network connectivity issues
                      * Model availability issues
                      * Code errors in the agent
                    - Try running `python outage_agent.py` directly to see the full error traceback
                    """)
                else:
                    st.markdown("""
                    1. **Check API Keys**: Verify all API keys are set correctly in the sidebar
                    2. **Test Directly**: Run `python outage_agent.py` in terminal to see detailed error
                    3. **Check Internet**: Ensure you have internet connectivity
                    4. **Verify Keys**: Make sure GROQ_API_KEY and EXA_API_KEY are valid
                    5. **Check Logs**: Look at the terminal where Streamlit is running for more details
                    """)

elif run_button and not alert_text.strip():
    st.warning("⚠️ Please enter an alert description before running the analysis.")
