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
        animation: fadeIn 0.3s ease-in;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f1f8e9;
        margin-right: 2rem;
        border-left: 4px solid #4caf50;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-input-container {
        position: sticky;
        bottom: 0;
        background-color: white;
        padding: 1rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 1rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 12px 20px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2196f3 !important;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2) !important;
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
    
    # Company URL Research Section
    st.markdown("#### 🔍 Automatic Company Research")
    st.markdown("*Provide your company website URL to automatically gather public ESG information*")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        company_url = st.text_input(
            "Company Website URL",
            placeholder="https://www.yourcompany.com",
            help="We'll analyze your website to gather publicly available ESG information"
        )
    with col2:
        research_company = st.button("🔍 Research Company", type="secondary")
    
    # Show research results if available
    if 'company_research' in st.session_state and st.session_state.company_research:
        research_data = st.session_state.company_research
        if research_data.get("success"):
            st.success("✅ Company research completed!")
            company_info = research_data.get("company_info", {})
            
            with st.expander("📊 Discovered Company Information", expanded=True):
                basic_info = company_info.get("basic_info", {})
                business_info = company_info.get("business_info", {})
                esg_indicators = company_info.get("esg_indicators", {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Basic Info**")
                    st.write(f"• Industry: {business_info.get('industry', 'Unknown')}")
                    st.write(f"• Size: {business_info.get('size', 'Unknown')}")
                    st.write(f"• Founded: {basic_info.get('founded', 'Unknown')}")
                
                with col2:
                    st.markdown("**ESG Presence**")
                    st.write(f"• Sustainability Page: {'✅' if esg_indicators.get('has_sustainability_page') else '❌'}")
                    st.write(f"• ESG Mentions: {'✅' if esg_indicators.get('mentions_esg') else '❌'}")
                    st.write(f"• CSR Report: {'✅' if esg_indicators.get('has_csr_report') else '❌'}")
                
                with col3:
                    st.markdown("**Commitments**")
                    env_commitments = esg_indicators.get('environmental_commitments', [])
                    for commitment in env_commitments[:2]:
                        st.write(f"• {commitment}")
        else:
            st.warning(f"⚠️ Research failed: {research_data.get('error', 'Unknown error')}")
    
    st.markdown("---")
    st.markdown("#### Manual Company Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pre-fill from research if available
        default_name = ""
        default_industry = "Technology"
        default_size = "Large"
        
        if 'company_research' in st.session_state and st.session_state.company_research.get("success"):
            research_info = st.session_state.company_research.get("company_info", {})
            default_name = research_info.get("basic_info", {}).get("name", "")
            default_industry = research_info.get("business_info", {}).get("industry", "Technology")
            size_mapping = {"Small": "Small (< 50 employees)", "Medium": "Medium (50-500 employees)", "Large": "Large (> 500 employees)"}
            research_size = research_info.get("business_info", {}).get("size", "Large")
            default_size = research_size if research_size in size_mapping.values() else size_mapping.get(research_size.split()[0], "Large (> 500 employees)")
        
        company_name = st.text_input("Company Name", value=st.session_state.company_info.get("name", default_name))
        industry = st.selectbox(
            "Industry",
            ["Technology", "Manufacturing", "Financial", "Healthcare", "Energy", "Retail", "Other"],
            index=["Technology", "Manufacturing", "Financial", "Healthcare", "Energy", "Retail", "Other"].index(default_industry) if default_industry in ["Technology", "Manufacturing", "Financial", "Healthcare", "Energy", "Retail", "Other"] else 0
        )
        company_size = st.selectbox(
            "Company Size",
            ["Small (< 50 employees)", "Medium (50-500 employees)", "Large (> 500 employees)"],
            index=["Small (< 50 employees)", "Medium (50-500 employees)", "Large (> 500 employees)"].index(default_size) if default_size in ["Small (< 50 employees)", "Medium (50-500 employees)", "Large (> 500 employees)"] else 2
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
    
    # Handle company research
    if research_company and company_url:
        with st.spinner("🔍 Researching company information..."):
            research_result = asyncio.run(research_company_from_url(company_url, company_name))
            st.session_state.company_research = research_result
            st.rerun()
    
    if st.button("Start ESG Assessment", type="primary"):
        # Store company information
        company_info = {
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
        
        # Enhance with research data if available
        if 'company_research' in st.session_state and st.session_state.company_research.get("success"):
            research_info = st.session_state.company_research.get("company_info", {})
            
            # Add research-based enhancements
            company_info.update({
                "website": company_url,
                "research_data": research_info,
                "has_sustainability_report": research_info.get("sustainability_data", {}).get("sustainability_report_available", False),
                "has_esg_policy": research_info.get("esg_indicators", {}).get("mentions_esg", has_esg_policy),
                "esg_frameworks": research_info.get("sustainability_data", {}).get("esg_frameworks_mentioned", []),
                "sustainability_commitments": research_info.get("esg_indicators", {}).get("environmental_commitments", [])
            })
        
        st.session_state.company_info = company_info
        
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

async def research_company_from_url(company_url: str, company_name: str = "") -> Dict[str, Any]:
    """Research company information from URL using orchestrator"""
    try:
        if st.session_state.orchestrator:
            return await st.session_state.orchestrator.research_company_from_url(company_url, company_name)
        else:
            return {
                "success": False,
                "error": "Orchestrator not initialized",
                "company_info": {}
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "company_info": {}
        }

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
    """Display the natural conversational chatbot interface"""
    st.markdown("### 💬 ESG Assessment Conversation")
    st.markdown("*Have a natural conversation about your company's ESG practices*")
    
    # Initialize conversation if not started
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    
    if not st.session_state.conversation_started:
        if st.button("Start ESG Conversation", type="primary"):
            # Start conversation with the conversation agent
            asyncio.run(start_conversation())
            st.rerun()
        return
    
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
    
    # Check if conversation is complete
    if st.session_state.get('assessment_complete', False):
        st.success("🎉 Conversation Complete!")
        st.markdown("Thank you for the comprehensive discussion about your ESG practices.")
        
        if st.button("Generate ESG Report", type="primary"):
            st.session_state.show_report = True
            st.rerun()
        return
    
    # Chat input section with better styling
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # Show current topic context
    if 'current_topic' in st.session_state and st.session_state.current_topic:
        topic_info = get_topic_info(st.session_state.current_topic)
        st.markdown(f"💬 **Current Topic:** {topic_info}")
    
    # Create input form for better UX
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Your response:",
            placeholder="Tell me about your ESG practices, policies, or any questions you have...",
            key="chat_input_form",
            help="Type your message and press Enter or click Send"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("Send Message", type="primary")
    
    # Process message when form is submitted
    if submitted and user_input.strip():
        # Process user message with conversation agent
        asyncio.run(process_chat_message(user_input.strip()))
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show conversation progress
    if 'conversation_progress' in st.session_state:
        progress = st.session_state.conversation_progress
        st.progress(progress)
        st.caption(f"Conversation progress: {progress:.0%}")

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

async def start_conversation():
    """Initialize the conversational ESG assessment"""
    try:
        # Initialize conversation agent
        orchestrator = st.session_state.orchestrator
        
        # Start conversation with company info
        conversation_result = await orchestrator.start_conversation(st.session_state.company_info)
        
        # Add welcome message to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": conversation_result.get("message", "Welcome to your ESG Assessment!")
        })
        
        st.session_state.conversation_started = True
        st.session_state.current_topic = conversation_result.get("topic", "company_overview")
        st.session_state.conversation_progress = conversation_result.get("knowledge_progress", 0.0)
        
    except Exception as e:
        st.error(f"Error starting conversation: {str(e)}")
        # Fallback welcome message
        welcome_message = """
        Welcome to your ESG Assessment! 🌱
        
        I'm here to help you evaluate your company's Environmental, Social, and Governance practices through a natural conversation.
        
        Let's start by telling me a bit about your company - what industry are you in, and what size is your organization?
        """
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": welcome_message
        })
        
        st.session_state.conversation_started = True
        st.session_state.current_topic = "company_overview"
        st.session_state.conversation_progress = 0.0

async def process_chat_message(user_message):
    """Process user message and generate response"""
    try:
        # Prevent duplicate processing
        if user_message == st.session_state.get("last_processed_message", ""):
            return
        
        st.session_state.last_processed_message = user_message
        
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Show processing indicator
        with st.spinner("ESG Assistant is thinking..."):
            # Process with orchestrator
            orchestrator = st.session_state.orchestrator
            response = await orchestrator.process_conversation_message(user_message)
        
        # Add only ONE AI response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["message"]
        })
        
        # Update conversation state
        if "topic" in response:
            st.session_state.current_topic = response["topic"]
        
        if "progress" in response:
            st.session_state.conversation_progress = response["progress"]
        
        # Check if ready for report generation
        if response.get("ready_for_report", False):
            st.session_state.assessment_complete = True
            st.session_state.knowledge_summary = response.get("knowledge_summary", {})
            
        # Handle topic transitions
        next_action = response.get("next_action", {})
        if next_action.get("action") == "transition_topic":
            # Show transition message if provided
            if next_action.get("transition_message"):
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": next_action["transition_message"]
                })
            
        # Store extracted data with better structure
        if "extracted_data" in response and response["extracted_data"]:
            current_topic = st.session_state.current_topic
            if current_topic not in st.session_state.user_responses:
                st.session_state.user_responses[current_topic] = {}
            
            # Store extracted data by topic
            for key, value in response["extracted_data"].items():
                st.session_state.user_responses[current_topic][key] = {
                    "question": key,
                    "answer": value,
                    "category": "ESG Knowledge",
                    "subcategory": current_topic,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Clear input after processing
        st.session_state.chat_input = ""
        st.session_state.last_input = ""
        
    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
        # Add fallback response only if no response was added
        if not st.session_state.chat_history or st.session_state.chat_history[-1]["role"] != "assistant":
            fallback_response = "I understand. Could you tell me more about that aspect of your ESG practices?"
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": fallback_response
            })

def get_topic_info(topic):
    """Get human-readable topic information"""
    topic_map = {
        "company_overview": "Company Overview & ESG Strategy",
        "environmental": "Environmental Performance",
        "social": "Social & Human Rights",
        "governance": "Corporate Governance",
        "reporting_compliance": "ESG Reporting & Compliance",
        "strategy": "ESG Strategy & Goals",
        "risk_management": "Risk Management",
        "stakeholder_engagement": "Stakeholder Engagement"
    }
    return topic_map.get(topic, topic.replace("_", " ").title())

async def display_report_generation():
    """Display the report generation interface"""
    st.markdown("### 📊 ESG Report Generation")
    
    if st.session_state.orchestrator:
        with st.spinner("Generating your comprehensive ESG report..."):
            # Get conversation data for report generation
            conversation_data = st.session_state.orchestrator.get_conversation_data_for_report()
            
            # Generate insights using the orchestrator
            insights = await st.session_state.orchestrator.generate_esg_insights(
                st.session_state.current_assessment or {},
                conversation_data.get("knowledge_collected", {})
            )
            
            st.session_state.esg_insights = insights
            st.session_state.conversation_data = conversation_data
            
            # Display report preview
            display_report_preview(insights, conversation_data)

def display_report_preview(insights: Dict[str, Any], conversation_data: Dict[str, Any]):
    """Display a preview of the ESG report"""
    st.markdown("## 📋 ESG Report Preview")
    
    # Executive Summary
    st.markdown("### Executive Summary")
    analysis = insights.get("insights", {})
    readiness_status = conversation_data.get("readiness_status", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Overall Completion</h3>
            <h2 style="color: #2E8B57;">{:.0f}%</h2>
        </div>
        """.format(conversation_data.get("completion_percentage", 0)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Topics Covered</h3>
            <h2 style="color: #FF8C00;">{}</h2>
        </div>
        """.format(len(conversation_data.get("topics_covered", []))), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Knowledge Points</h3>
            <h2 style="color: #4169E1;">{}</h2>
        </div>
        """.format(readiness_status.get("total_knowledge_points", 0)), unsafe_allow_html=True)
    
    # Topic Status
    st.markdown("### ESG Topic Coverage")
    topic_status = readiness_status.get("topic_status", {})
    
    for topic, status in topic_status.items():
        topic_name = get_topic_info(topic)
        coverage_score = status.get("coverage_score", 0)
        knowledge_score = status.get("knowledge_score", 0)
        is_covered = status.get("covered", False)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{topic_name}**")
            st.progress(coverage_score)
            st.caption(f"Coverage: {coverage_score:.0%} | Knowledge: {knowledge_score:.0%}")
        with col2:
            if is_covered:
                st.success("✅ Complete")
            else:
                st.warning("⏳ In Progress")
    
    # Knowledge Summary
    knowledge_summary = conversation_data.get("knowledge_summary", {})
    if knowledge_summary:
        st.markdown("### 📊 Knowledge Collected")
        for topic, summary in knowledge_summary.items():
            with st.expander(f"{get_topic_info(topic)} ({summary.get('data_points', 0)} data points)"):
                key_findings = summary.get("key_findings", [])
                for finding in key_findings:
                    st.markdown(f"• {finding}")
    
    # Key Insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💪 Strengths")
        for strength in analysis.get("strengths", ["Comprehensive ESG data collection", "Systematic approach to sustainability", "Good stakeholder engagement"])[:3]:
            st.markdown(f"• {strength}")
    
    with col2:
        st.markdown("### 🎯 Areas for Improvement")
        for improvement in analysis.get("improvements", ["Enhanced data measurement", "Expanded reporting frameworks", "Increased transparency"])[:3]:
            st.markdown(f"• {improvement}")
    
    # Recommendations
    st.markdown("### 📋 Recommendations")
    recommendations = analysis.get("recommendations", [
        "Develop comprehensive ESG strategy aligned with EU directives",
        "Implement systematic data collection processes",
        "Enhance stakeholder engagement programs",
        "Prepare for CSRD compliance requirements",
        "Establish science-based targets for emissions reduction"
    ])
    
    for i, recommendation in enumerate(recommendations[:5], 1):
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
                        st.session_state.current_assessment or {},
                        conversation_data.get("knowledge_collected", {}),
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