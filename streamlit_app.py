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
            
            # Extract key information
            is_escalation = "ESCALATION REQUIRED" in entry['response'].upper()
            time_str = entry['timestamp'].split()[1]
            alert_preview = entry['alert'][:60] + "..." if len(entry['alert']) > 60 else entry['alert']
            
            # Extract escalation reason or summary
            escalation_match = re.search(r'ESCALATION REQUIRED[:\*\s]*\n?(.+?)(?=\n\n|$)', entry['response'], re.IGNORECASE | re.DOTALL)
            what_happened_match = re.search(r'(?:What happened|What Happened)[:\*\s]*\n?(.+?)(?=\n\n|\n\*\*|What was|What to monitor|ESCALATION|$)', entry['response'], re.IGNORECASE | re.DOTALL)
            
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
            output = request.output()
            
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
            
            # Check for escalation
            is_escalation = "ESCALATION REQUIRED" in output_text.upper() or "escalate" in output_text.lower()
            
            if is_escalation:
                st.error("🚨 **ESCALATION REQUIRED**")
            else:
                st.success("✓ **Issue Handled by Agent**")
            
            st.markdown("---")
            
            # Beautified response display
            st.markdown("###  Analysis Results")
            
            # Clean and format the response
            import re
            
            # Remove markdown headers and clean up the text
            cleaned_response = output_text
            
            # Remove markdown headers (###, ##, #)
            cleaned_response = re.sub(r'^###+\s*', '', cleaned_response, flags=re.MULTILINE)
            cleaned_response = re.sub(r'^\*\*\s*', '', cleaned_response, flags=re.MULTILINE)
            cleaned_response = re.sub(r'\*\*', '', cleaned_response)
            
            # Extract sections more intelligently
            sections = {}
            
            # Helper function to clean text
            def clean_section_text(text):
                if not text:
                    return ""
                # Remove trailing "No", "No escalation", etc.
                text = re.sub(r'\s*(No|No escalation|No action needed|N/A|None)\s*$', '', text, flags=re.IGNORECASE)
                # Remove trailing bullet points
                text = re.sub(r'\s*[•·]\s*$', '', text)
                # Remove trailing dashes or asterisks
                text = re.sub(r'\s*[-*]\s*$', '', text)
                return text.strip()
            
            # What Happened
            what_happened = re.search(r'(?:What happened|What Happened)[:\*\s]*\n?(.+?)(?=\n\n|\n\*\*|What was|What to monitor|ESCALATION|$)', output_text, re.IGNORECASE | re.DOTALL)
            if what_happened:
                sections['what_happened'] = clean_section_text(what_happened.group(1))
            
            # What Was Done
            what_was_done = re.search(r'(?:What was done|What Was Done)[:\*\s]*\n?(.+?)(?=\n\n|\n\*\*|What to monitor|ESCALATION|$)', output_text, re.IGNORECASE | re.DOTALL)
            if what_was_done:
                sections['what_was_done'] = clean_section_text(what_was_done.group(1))
            
            # What to Monitor
            what_to_monitor = re.search(r'(?:What to monitor next|What to Monitor Next|What should be monitored)[:\*\s]*\n?(.+?)(?=\n\n|\n\*\*|ESCALATION|$)', output_text, re.IGNORECASE | re.DOTALL)
            if what_to_monitor:
                sections['what_to_monitor'] = clean_section_text(what_to_monitor.group(1))
            
            # Escalation
            escalation = re.search(r'ESCALATION REQUIRED[:\*\s]*\n?(.+?)(?=\n\n|$)', output_text, re.IGNORECASE | re.DOTALL)
            if escalation:
                sections['escalation'] = escalation.group(1).strip()
            
            # Display sections in clean format
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
            
            # If no structured sections found, display cleaned response
            if not sections:
                # Clean up any remaining markdown artifacts
                cleaned = re.sub(r'^[-*•]\s*', '', cleaned_response, flags=re.MULTILINE)
                cleaned = cleaned.strip()
                st.markdown(cleaned)
                
        except Exception as e:
            st.error(f"❌ Error running agent: {str(e)}")
            with st.expander("Error Details"):
                st.exception(e)

elif run_button and not alert_text.strip():
    st.warning("⚠️ Please enter an alert description before running the analysis.")
