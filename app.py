"""
Main Streamlit Application for Agentic ESG Report Generation
"""
import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import our agentic components
from src.agents.orchestrator import AgentOrchestrator
from src.config import Config
from src.report_generator import ESGReportGenerator
from src.document_processor import document_processor

# Page configuration
st.set_page_config(
    page_title="ESG Report Generator",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-status {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .agent-active {
        border-left: 4px solid #28a745;
    }
    
    .agent-inactive {
        border-left: 4px solid #dc3545;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #f1f8e9;
        margin-right: 2rem;
    }
    
    .progress-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_assessment' not in st.session_state:
        st.session_state.current_assessment = None
    
    if 'company_info' not in st.session_state:
        st.session_state.company_info = {}
    
    if 'assessment_questions' not in st.session_state:
        st.session_state.assessment_questions = []
    
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    
    if 'user_responses' not in st.session_state:
        st.session_state.user_responses = {}
    
    if 'assessment_complete' not in st.session_state:
        st.session_state.assessment_complete = False
    
    if 'agents_initialized' not in st.session_state:
        st.session_state.agents_initialized = False
    
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = []
    
    if 'document_analysis' not in st.session_state:
        st.session_state.document_analysis = None

@st.cache_resource
def get_orchestrator():
    """Get or create the agent orchestrator"""
    return AgentOrchestrator(Config.get_config())

async def initialize_agents():
    """Initialize the agent orchestrator"""
    if not st.session_state.agents_initialized:
        with st.spinner("Initializing AI agents..."):
            orchestrator = get_orchestrator()
            result = await orchestrator.initialize()
            st.session_state.orchestrator = orchestrator
            st.session_state.agents_initialized = True
            return result
    return {"status": "already_initialized"}

def display_agent_status():
    """Display the status of all agents in the sidebar"""
    st.sidebar.markdown("## 🤖 Agent Status")
    
    if st.session_state.orchestrator:
        status = st.session_state.orchestrator.get_orchestrator_status()
        
        for agent_name, agent_status in status.get("agents", {}).items():
            status_class = "agent-active" if agent_status["status"] != "error" else "agent-inactive"
            
            st.sidebar.markdown(f"""
            <div class="agent-status {status_class}">
                <strong>{agent_name.title()} Agent</strong><br>
                Status: {agent_status["status"]}<br>
                Tasks: {agent_status["metrics"]["tasks_completed"]}<br>
                Errors: {agent_status["metrics"]["errors"]}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.warning("Agents not initialized")

def display_progress_tracker():
    """Display assessment progress"""
    st.sidebar.markdown("## 📊 Assessment Progress")
    
    if st.session_state.assessment_questions:
        total_questions = len(st.session_state.assessment_questions)
        current_index = st.session_state.current_question_index
        progress = min(current_index / total_questions, 1.0) if total_questions > 0 else 0
        
        st.sidebar.progress(progress)
        st.sidebar.write(f"Question {current_index + 1} of {total_questions}")
        
        # Category breakdown
        if st.session_state.assessment_questions:
            categories = {}
            for i, question in enumerate(st.session_state.assessment_questions):
                category = question.get("category", "Unknown")
                if category not in categories:
                    categories[category] = {"total": 0, "completed": 0}
                categories[category]["total"] += 1
                if i < current_index:
                    categories[category]["completed"] += 1
            
            st.sidebar.markdown("### Category Progress")
            for category, stats in categories.items():
                completion = stats["completed"] / stats["total"] if stats["total"] > 0 else 0
                st.sidebar.write(f"{category}: {stats['completed']}/{stats['total']} ({completion:.0%})")

def company_info_form():
    """Display company information form"""
    st.markdown('<div class="main-header">🌱 ESG Report Generator</div>', unsafe_allow_html=True)
    st.markdown("### Company Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("Company Name", value=st.session_state.company_info.get("name", ""))
        industry = st.selectbox(
            "Industry",
            ["Technology", "Manufacturing", "Financial", "Healthcare", "Energy", "Retail", "Other"],
            index=0 if not st.session_state.company_info.get("industry") else 
                  ["Technology", "Manufacturing", "Financial", "Healthcare", "Energy", "Retail", "Other"].index(
                      st.session_state.company_info.get("industry", "Technology")
                  )
        )
        company_size = st.selectbox(
            "Company Size",
            ["Small (< 50 employees)", "Medium (50-500 employees)", "Large (> 500 employees)"],
            index=2 if not st.session_state.company_info.get("size") else 
                  ["Small", "Medium", "Large"].index(st.session_state.company_info.get("size", "Large"))
        )
    
    with col2:
        region = st.selectbox(
            "Primary Region",
            ["North America", "Europe", "Asia Pacific", "Latin America", "Africa", "Global"],
            index=0 if not st.session_state.company_info.get("region") else 
                  ["North America", "Europe", "Asia Pacific", "Latin America", "Africa", "Global"].index(
                      st.session_state.company_info.get("region", "North America")
                  )
        )
        revenue = st.selectbox(
            "Annual Revenue",
            ["< $10M", "$10M - $100M", "$100M - $1B", "> $1B"],
            index=0
        )
        has_esg_policy = st.checkbox("Has existing ESG policy", value=st.session_state.company_info.get("has_esg_policy", False))
    
    # Document Upload Section
    st.markdown("### 📄 Upload ESG Documents (Optional)")
    st.markdown("Upload your existing ESG reports, sustainability documents, or policies for enhanced analysis.")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt', 'csv', 'xlsx'],
        help="Supported formats: PDF, DOCX, TXT, CSV, XLSX (Max 10MB per file)"
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        for file in uploaded_files:
            st.markdown(f"• {file.name} ({file.size / 1024:.1f} KB)")
    
    if st.button("Start ESG Assessment", type="primary"):
        # Store company information
        st.session_state.company_info = {
            "name": company_name,
            "industry": industry,
            "size": company_size.split(" ")[0],  # Extract size category
            "region": region,
            "revenue": revenue,
            "has_esg_policy": has_esg_policy,
            "has_sustainability_report": False,  # Default values
            "has_esg_committee": False,
            "third_party_assurance": False
        }
        
        # Process uploaded files if any
        if uploaded_files:
            st.session_state.uploaded_documents = []
            for file in uploaded_files:
                file_data = {
                    "filename": file.name,
                    "content": file.read(),
                    "type": "sustainability_report",  # Default type
                    "size": file.size
                }
                st.session_state.uploaded_documents.append(file_data)
        
        # Start assessment
        st.rerun()

async def start_assessment():
    """Start the ESG assessment process"""
    if st.session_state.orchestrator and st.session_state.company_info:
        with st.spinner("Preparing your personalized ESG assessment..."):
            # Process uploaded documents first if any
            if st.session_state.uploaded_documents:
                with st.spinner("Analyzing uploaded documents..."):
                    doc_result = await st.session_state.orchestrator.process_uploaded_documents(
                        st.session_state.uploaded_documents
                    )
                    st.session_state.document_analysis = doc_result
                    
                    if doc_result.get("total_processed", 0) > 0:
                        st.success(f"✅ Processed {doc_result['total_processed']} document(s) successfully!")
                    if doc_result.get("total_failed", 0) > 0:
                        st.warning(f"⚠️ Failed to process {doc_result['total_failed']} document(s)")
            
            # Process ESG assessment with agents
            assessment_data = await st.session_state.orchestrator.process_esg_assessment(
                st.session_state.company_info
            )
            
            st.session_state.current_assessment = assessment_data
            
            # Extract questions for the chat interface
            questions_data = assessment_data.get("assessment_questions", {})
            st.session_state.assessment_questions = questions_data.get("questions", [])
            st.session_state.current_question_index = 0
            
            return True
    return False

def display_chat_interface():
    """Display the chat-based assessment interface"""
    st.markdown("### 💬 ESG Assessment Chat")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>ESG Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Current question
    if (st.session_state.current_question_index < len(st.session_state.assessment_questions) 
        and not st.session_state.assessment_complete):
        
        current_question = st.session_state.assessment_questions[st.session_state.current_question_index]
        
        st.markdown("---")
        st.markdown(f"**Question {st.session_state.current_question_index + 1}:**")
        st.markdown(f"*{current_question.get('category', 'General')} - {current_question.get('subcategory', 'Assessment')}*")
        st.markdown(f"### {current_question['question']}")
        
        # Handle different question types
        question_type = current_question.get("type", "text")
        response = None
        
        if question_type == "yes_no":
            response = st.radio(
                "Select your answer:",
                ["Yes", "No"],
                key=f"question_{st.session_state.current_question_index}"
            )
        elif question_type == "percentage":
            response = st.slider(
                "Select percentage:",
                0, 100, 50,
                key=f"question_{st.session_state.current_question_index}"
            )
        else:
            response = st.text_area(
                "Your answer:",
                key=f"question_{st.session_state.current_question_index}",
                height=100
            )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("Submit Answer", type="primary"):
                # Store response
                st.session_state.user_responses[current_question["id"]] = {
                    "question": current_question["question"],
                    "answer": response,
                    "category": current_question.get("category"),
                    "subcategory": current_question.get("subcategory"),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": f"Q: {current_question['question']}\nA: {response}"
                })
                
                # Generate AI response (mock)
                ai_response = generate_ai_response(current_question, response)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                # Move to next question
                st.session_state.current_question_index += 1
                
                # Check if assessment is complete
                if st.session_state.current_question_index >= len(st.session_state.assessment_questions):
                    st.session_state.assessment_complete = True
                
                st.rerun()
    
    elif st.session_state.assessment_complete:
        st.success("🎉 Assessment Complete!")
        st.markdown("Thank you for completing the ESG assessment. Your report is being generated...")
        
        if st.button("Generate ESG Report", type="primary"):
            st.session_state.show_report = True
            st.rerun()

def generate_ai_response(question: Dict[str, Any], user_response: Any) -> str:
    """Generate AI response to user answer (mock implementation)"""
    responses = [
        f"Thank you for that information. This is an important aspect of {question.get('subcategory', 'ESG')} performance.",
        f"I understand. This relates to current {question.get('category', 'ESG')} regulations and best practices.",
        f"That's valuable insight. This will help us assess your {question.get('subcategory', 'ESG')} maturity.",
        f"Good to know. This information will be included in your comprehensive ESG analysis."
    ]
    
    import random
    return random.choice(responses)

async def display_report_generation():
    """Display the report generation interface"""
    st.markdown("### 📊 ESG Report Generation")
    
    if st.session_state.orchestrator and st.session_state.user_responses:
        with st.spinner("Generating your comprehensive ESG report..."):
            # Generate insights using the orchestrator
            insights = await st.session_state.orchestrator.generate_esg_insights(
                st.session_state.current_assessment,
                st.session_state.user_responses
            )
            
            st.session_state.esg_insights = insights
            
            # Display report preview
            display_report_preview(insights)

def display_report_preview(insights: Dict[str, Any]):
    """Display a preview of the ESG report"""
    st.markdown("## 📋 ESG Report Preview")
    
    # Executive Summary
    st.markdown("### Executive Summary")
    analysis = insights.get("insights", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Overall ESG Score</h3>
            <h2 style="color: #2E8B57;">{}/100</h2>
        </div>
        """.format(analysis.get("overall_score", 75)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Compliance Status</h3>
            <h2 style="color: #FF8C00;">{}</h2>
        </div>
        """.format(analysis.get("compliance_status", "Good")), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Questions Answered</h3>
            <h2 style="color: #4169E1;">{}</h2>
        </div>
        """.format(len(st.session_state.user_responses)), unsafe_allow_html=True)
    
    # Category Scores
    st.markdown("### Category Performance")
    category_scores = analysis.get("category_scores", {})
    
    for category, score in category_scores.items():
        st.markdown(f"**{category}**: {score}/100")
        st.progress(score / 100)
    
    # Key Insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💪 Strengths")
        for strength in analysis.get("strengths", [])[:3]:
            st.markdown(f"• {strength}")
    
    with col2:
        st.markdown("### 🎯 Areas for Improvement")
        for improvement in analysis.get("improvements", [])[:3]:
            st.markdown(f"• {improvement}")
    
    # Recommendations
    st.markdown("### 📋 Recommendations")
    for i, recommendation in enumerate(analysis.get("recommendations", [])[:5], 1):
        st.markdown(f"{i}. {recommendation}")
    
    # Download button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("📥 Download Full Report (PDF)", type="primary"):
            # Generate PDF report
            with st.spinner("Generating PDF report..."):
                try:
                    report_generator = ESGReportGenerator()
                    pdf_bytes = report_generator.generate_report(
                        st.session_state.company_info,
                        st.session_state.current_assessment,
                        st.session_state.user_responses,
                        insights
                    )
                    
                    # Create download
                    filename = f"ESG_Report_{st.session_state.company_info.get('name', 'Company').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary"
                    )
                    
                    st.success("✅ PDF report generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")

def main():
    """Main application function"""
    initialize_session_state()
    
    # Initialize agents
    if not st.session_state.agents_initialized:
        init_result = asyncio.run(initialize_agents())
        if init_result.get("status") == "initialized":
            st.success("✅ AI agents initialized successfully!")
        elif init_result.get("status") == "failed":
            st.error(f"❌ Failed to initialize agents: {init_result.get('error', 'Unknown error')}")
    
    # Display agent status in sidebar
    display_agent_status()
    display_progress_tracker()
    
    # Main application flow
    if not st.session_state.company_info:
        # Step 1: Company information
        company_info_form()
    
    elif not st.session_state.current_assessment:
        # Step 2: Start assessment
        if asyncio.run(start_assessment()):
            st.success("✅ Assessment prepared successfully!")
            st.rerun()
    
    elif not st.session_state.assessment_complete:
        # Step 3: Chat-based assessment
        display_chat_interface()
    
    elif st.session_state.assessment_complete and not st.session_state.get("show_report", False):
        # Step 4: Assessment complete, show completion message
        st.success("🎉 Assessment Complete!")
        if st.button("Generate ESG Report", type="primary"):
            st.session_state.show_report = True
            st.rerun()
    
    else:
        # Step 5: Report generation and display
        asyncio.run(display_report_generation())

if __name__ == "__main__":
    main()