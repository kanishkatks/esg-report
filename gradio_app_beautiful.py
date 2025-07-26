"""
SustainPilot - Beautiful ESG Assessment Interface
Enhanced with modern design, AI imagery concepts, and professional styling
"""
import gradio as gr
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import our enhanced agentic components
from src.agents.orchestrator import AgentOrchestrator
from src.agents.conversation_agent import ConversationAgent
from src.config import Config
from src.enhanced_report_generator import EnhancedESGReportGenerator
from src.agents.enhanced_search_agent import EnhancedSearchAgent

# Global state management
class ESGWorkflowState:
    def __init__(self):
        self.orchestrator = None
        self.current_step = 1
        self.company_info = {}
        self.company_research = None
        self.conversation_data = {}
        self.assessment_complete = False
        self.uploaded_documents = []
        
    async def initialize_orchestrator(self):
        """Initialize orchestrator if not already done"""
        if not self.orchestrator:
            self.orchestrator = AgentOrchestrator(Config.get_config())
            await self.orchestrator.initialize()
        return self.orchestrator

# Global app state
workflow_state = ESGWorkflowState()

# Minimalistic CSS with dark colors on light background
BEAUTIFUL_CSS = """
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Root Variables - Dark Green Color Palette */
:root {
    --primary-dark: #1b4332;
    --secondary-dark: #2d5a3d;
    --accent-dark: #40916c;
    --text-primary: #1b4332;
    --text-secondary: #2d5a3d;
    --text-muted: #52796f;
    --background-light: #ffffff;
    --background-subtle: #f8fffe;
    --border-light: #d8f3dc;
    --border-subtle: #e8f5e8;
    --success-color: #40916c;
    --error-color: #ef4444;
    --warning-color: #f59e0b;
    --shadow-subtle: 0 1px 3px rgba(27, 67, 50, 0.1);
    --shadow-medium: 0 4px 6px rgba(27, 67, 50, 0.1);
    --border-radius: 8px;
    --transition: all 0.2s ease;
}

/* Global Styles */
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--background-light) !important;
    min-height: 100vh;
    color: var(--text-primary) !important;
}

/* Hero Section - Compact and Minimal */
.hero-section {
    background: var(--background-light);
    padding: 40px 40px 32px;
    text-align: center;
    border-bottom: 1px solid var(--border-light);
    margin-bottom: 32px;
}

.hero-title {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.875rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    margin-bottom: 12px !important;
    letter-spacing: -0.025em;
}

.hero-subtitle {
    font-size: 1rem !important;
    color: var(--text-secondary) !important;
    margin-bottom: 0 !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}

.hero-features {
    display: none;
}

.hero-feature {
    display: none;
}

.hero-feature-icon {
    display: none;
}

.hero-feature-title {
    display: none;
}

.hero-feature-desc {
    display: none;
}

/* Step Containers - Clean Cards */
.step-container {
    background: var(--background-light);
    border: 1px solid var(--border-light);
    border-radius: var(--border-radius);
    padding: 32px;
    margin: 24px 0;
    transition: var(--transition);
}

.step-container:hover {
    border-color: var(--border-subtle);
    box-shadow: var(--shadow-subtle);
}

.step-header {
    display: flex;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-subtle);
}

.step-number {
    background: var(--primary-dark);
    color: white;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    font-weight: 600;
    font-size: 1rem;
    flex-shrink: 0;
}

.step-title {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    margin: 0 !important;
}

.step-description {
    color: var(--text-secondary) !important;
    font-size: 0.875rem !important;
    margin-top: 8px !important;
    line-height: 1.5 !important;
}

/* Buttons - Minimal Design */
.btn-primary {
    background: var(--primary-dark) !important;
    border: none !important;
    border-radius: var(--border-radius) !important;
    padding: 12px 24px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: white !important;
    transition: var(--transition) !important;
    cursor: pointer !important;
}

.btn-primary:hover {
    background: var(--secondary-dark) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-medium) !important;
}

.btn-secondary {
    background: var(--background-light) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--border-radius) !important;
    padding: 12px 24px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: var(--text-primary) !important;
    transition: var(--transition) !important;
    cursor: pointer !important;
}

.btn-secondary:hover {
    border-color: var(--primary-dark) !important;
    color: var(--primary-dark) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-subtle) !important;
}

/* Status Messages - Clean and Subtle */
.status-success {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: var(--border-radius);
    padding: 16px;
    color: #166534;
    margin: 16px 0;
}

.status-error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: var(--border-radius);
    padding: 16px;
    color: #dc2626;
    margin: 16px 0;
}

.status-info {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: var(--border-radius);
    padding: 16px;
    color: #0369a1;
    margin: 16px 0;
}

/* Form Elements */
.form-group {
    margin: 16px 0;
}

/* Chat Interface */
.chat-container {
    background: var(--background-light);
    border: 1px solid var(--border-light);
    border-radius: var(--border-radius);
    overflow: hidden;
}

/* Loading Animation - Minimal */
.loading-spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid var(--border-light);
    border-radius: 50%;
    border-top-color: var(--primary-dark);
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Typography */
.text-primary {
    color: var(--text-primary) !important;
}

.text-secondary {
    color: var(--text-secondary) !important;
}

.text-muted {
    color: var(--text-muted) !important;
}

/* Animations - Subtle */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.fade-in {
    animation: fadeIn 0.3s ease-out;
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem !important;
    }
    
    .hero-features {
        grid-template-columns: 1fr;
        gap: 24px;
    }
    
    .step-container {
        padding: 24px;
        margin: 16px 0;
    }
    
    .step-header {
        flex-direction: column;
        text-align: center;
        align-items: center;
    }
    
    .step-number {
        margin-right: 0;
        margin-bottom: 12px;
    }
}

/* Clean spacing and typography */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

p {
    color: var(--text-secondary) !important;
    line-height: 1.6 !important;
}

/* Input fields */
input, textarea, select {
    border: 1px solid var(--border-light) !important;
    border-radius: var(--border-radius) !important;
    padding: 8px 12px !important;
    font-size: 0.875rem !important;
    transition: var(--transition) !important;
}

input:focus, textarea:focus, select:focus {
    outline: none !important;
    border-color: var(--primary-dark) !important;
    box-shadow: 0 0 0 3px rgba(26, 26, 26, 0.1) !important;
}
"""

async def research_company_and_advance(company_url: str, company_name: str) -> Tuple[str, str, str, str, str, Dict]:
    """Research company and automatically advance to next step"""
    if not company_url.strip():
        workflow_state.current_step = 2
        workflow_state.company_info = {
            "name": company_name or "Your Company",
            "industry": "Technology",
            "size": "Medium",
            "region": "Europe",
            "website": "",
            "research_data": {}
        }
        
        return (
            gr.update(visible=False),
            "⏭️ **Skipping company research** - proceeding to manual setup.",
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            workflow_state.company_info
        )
    
    try:
        orchestrator = await workflow_state.initialize_orchestrator()
        research_result = await orchestrator.research_company_from_url(company_url, company_name)
        
        if research_result.get("success"):
            workflow_state.company_research = research_result
            workflow_state.current_step = 2
            company_info = research_result.get("company_info", {})
            
            basic_info = company_info.get("basic_info", {})
            business_info = company_info.get("business_info", {})
            esg_indicators = company_info.get("esg_indicators", {})
            
            result_text = f"""
            <div class="status-success fade-in-up">
                <h3>✅ Company Research Completed!</h3>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
                    <div class="glass-card" style="padding: 20px;">
                        <h4 class="text-gradient">📊 Basic Information</h4>
                        <p><strong>Company:</strong> {basic_info.get('name', 'Unknown')}</p>
                        <p><strong>Industry:</strong> {business_info.get('industry', 'Unknown')}</p>
                        <p><strong>Size:</strong> {business_info.get('size', 'Unknown')}</p>
                    </div>
                    
                    <div class="glass-card" style="padding: 20px;">
                        <h4 class="text-gradient">🌱 ESG Presence</h4>
                        <p><strong>Sustainability Page:</strong> {'✅ Yes' if esg_indicators.get('has_sustainability_page') else '❌ No'}</p>
                        <p><strong>ESG Mentions:</strong> {'✅ Yes' if esg_indicators.get('mentions_esg') else '❌ No'}</p>
                        <p><strong>CSR Report:</strong> {'✅ Yes' if esg_indicators.get('has_csr_report') else '❌ No'}</p>
                    </div>
                </div>
                
                <p style="margin-top: 20px; text-align: center;"><strong>✨ Proceeding to company setup...</strong></p>
            </div>
            """
            
            workflow_state.company_info = {
                "name": basic_info.get('name', company_name),
                "industry": business_info.get('industry', 'Technology'),
                "size": business_info.get('size', 'Medium'),
                "region": "Europe",
                "website": company_url,
                "research_data": company_info
            }
            
            return (
                gr.update(visible=False),
                result_text,
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                workflow_state.company_info
            )
        else:
            return (
                gr.update(visible=True),
                f'<div class="status-error">❌ Research failed: {research_result.get("error", "Unknown error")}</div>',
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                {}
            )
            
    except Exception as e:
        return (
            gr.update(visible=True),
            f'<div class="status-error">❌ Error during research: {str(e)}</div>',
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            {}
        )

async def start_conversation_and_advance(company_name: str, industry: str, size: str, region: str) -> Tuple[str, str, str, List]:
    """Start conversation and advance to chat step"""
    try:
        if not workflow_state.company_info:
            workflow_state.company_info = {
                "name": company_name or "Your Company",
                "industry": industry,
                "size": size.split(" ")[0] if size else "Medium",
                "region": region,
                "website": "",
                "research_data": {}
            }
        else:
            workflow_state.company_info.update({
                "name": company_name or workflow_state.company_info.get("name", "Your Company"),
                "industry": industry,
                "size": size.split(" ")[0] if size else "Medium",
                "region": region
            })
        
        workflow_state.current_step = 3
        
        orchestrator = await workflow_state.initialize_orchestrator()
        conversation_result = await orchestrator.start_conversation(workflow_state.company_info)
        
        default_msg = "Let's begin your ESG assessment journey!"
        welcome_msg = f"🌟 Welcome to 🍃 SustainPilot 🍃! {conversation_result.get('message', default_msg)}"
        chat_history = [
            {"role": "assistant", "content": welcome_msg}
        ]
        
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            chat_history
        )
        
    except Exception as e:
        error_msg = f"❌ Error starting conversation: {str(e)}"
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            [{"role": "assistant", "content": error_msg}]
        )

async def process_chat_and_check_completion(message: str, chat_history: List) -> Tuple[List, str, str, str]:
    """Process chat message and check if ready for report generation"""
    try:
        chat_history.append({"role": "user", "content": message})
        
        orchestrator = await workflow_state.initialize_orchestrator()
        response = await orchestrator.process_conversation_message(message)
        
        assistant_message = response.get("message", "Thank you for your response.")
        
        if response.get("ready_for_report", False):
            workflow_state.assessment_complete = True
            workflow_state.conversation_data = orchestrator.get_conversation_data_for_report()
            workflow_state.current_step = 4
            
            completion_message = """
            <div class="status-success fade-in-up">
                <h3>🎉 ESG Data Collection Complete!</h3>
                <p>✨ <strong>Automatically proceeding to intelligent report generation...</strong></p>
                <div class="loading-spinner" style="margin: 20px auto;"></div>
            </div>
            """
            assistant_message += completion_message
            
            chat_history.append({"role": "assistant", "content": assistant_message})
            
            return (
                chat_history,
                "",
                gr.update(visible=False),
                gr.update(visible=True)
            )
        else:
            chat_history.append({"role": "assistant", "content": assistant_message})
            
            return (
                chat_history,
                "",
                gr.update(visible=True),
                gr.update(visible=False)
            )
        
    except Exception as e:
        error_msg = f'<div class="status-error">❌ Error processing message: {str(e)}</div>'
        chat_history.append({"role": "assistant", "content": error_msg})
        return (
            chat_history,
            "",
            gr.update(visible=True),
            gr.update(visible=False)
        )

async def generate_final_report() -> Tuple[str, str]:
    """Generate the final ESG report using enhanced generator with real data"""
    if not workflow_state.assessment_complete:
        return None, '<div class="status-error">❌ Please complete the ESG data collection first.</div>'
    
    try:
        search_agent = EnhancedSearchAgent()
        regulations_data = await search_agent.get_current_regulations()
        
        orchestrator = await workflow_state.initialize_orchestrator()
        insights = await orchestrator.generate_esg_insights(
            {},
            workflow_state.conversation_data.get("knowledge_collected", {})
        )
        
        report_generator = EnhancedESGReportGenerator()
        pdf_bytes = report_generator.generate_report(
            workflow_state.company_info,
            {},
            workflow_state.conversation_data.get("knowledge_collected", {}),
            insights,
            regulations_data
        )
        
        import os
        filename = f"SustainPilot_ESG_Report_{workflow_state.company_info.get('name', 'Company').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        temp_path = os.path.join(os.getcwd(), filename)
        
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)
        
        success_message = """
        <div class="status-success fade-in-up">
            <h3>✅ 🍃 SustainPilot 🍃 ESG Report Generated Successfully!</h3>
            <div class="glass-card" style="padding: 20px; margin-top: 20px;">
                <h4 class="text-gradient">🎊 Congratulations!</h4>
                <p>Your comprehensive ESG assessment is complete with real data and current regulations. 
                Your professional SustainPilot report includes:</p>
                <ul>
                    <li>📊 Detailed ESG performance analysis</li>
                    <li>📋 Current regulatory compliance status</li>
                    <li>🚀 Personalized improvement recommendations</li>
                    <li>🗺️ Strategic roadmap for ESG excellence</li>
                </ul>
                <p style="text-align: center; margin-top: 20px;">
                    <strong>Click below to download your professional 🍃 SustainPilot 🍃 report!</strong>
                </p>
            </div>
        </div>
        """
        
        return temp_path, success_message
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Enhanced report generation error: {error_details}")
        return None, f'<div class="status-error">❌ Error generating enhanced report: {str(e)}</div>'

def create_beautiful_interface():
    """Create the beautiful, modern interface"""
    
    with gr.Blocks(
        title="SustainPilot - Beautiful ESG Assessment",
        theme=gr.themes.Soft(),
        css=BEAUTIFUL_CSS
    ) as interface:
        
        # Hero Section
        gr.HTML("""
        <div class="hero-section">
            <h1 class="hero-title">🍃 SustainPilot 🍃</h1>
            <p class="hero-subtitle">
                AI-powered ESG assessment with real-time regulatory intelligence
                and personalized sustainability insights for modern businesses.
            </p>
        </div>
        """)
        
        # Step 1: Company Research
        with gr.Group(visible=True) as step1:
            gr.HTML("""
            <div class="step-container">
                <div class="step-header">
                    <div class="step-number">1</div>
                    <div>
                        <div class="step-title">Company Discovery</div>
                        <div class="step-description">Research your company's ESG footprint automatically, or proceed with manual setup</div>
                    </div>
                </div>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    company_url_input = gr.Textbox(
                        label="Company Website URL (Optional)",
                        placeholder="https://www.yourcompany.com",
                        info="Leave empty to skip automatic research"
                    )
                    company_name_input = gr.Textbox(
                        label="Company Name",
                        placeholder="Your Company Name"
                    )
                with gr.Column(scale=1):
                    research_btn = gr.Button("Research & Continue", variant="primary", size="lg")
                    skip_btn = gr.Button("Skip to Manual Setup", variant="secondary", size="lg")
            
            research_output = gr.HTML()
        
        # Step 2: Company Details
        with gr.Group(visible=False) as step2:
            gr.HTML("""
            <div class="step-container">
                <div class="step-header">
                    <div class="step-number">2</div>
                    <div>
                        <div class="step-title">Company Profile</div>
                        <div class="step-description">Confirm or update your company information for personalized assessment</div>
                    </div>
                </div>
            </div>
            """)
            
            with gr.Row():
                company_name_final = gr.Textbox(label="Company Name", placeholder="Your Company Name")
                industry_input = gr.Dropdown(
                    choices=["Technology", "Manufacturing", "Financial", "Healthcare", "Energy", "Retail", "Other"],
                    label="Industry", value="Technology"
                )
            
            with gr.Row():
                size_input = gr.Dropdown(
                    choices=["Small (< 50 employees)", "Medium (50-500 employees)", "Large (> 500 employees)"],
                    label="Company Size", value="Medium (50-500 employees)"
                )
                region_input = gr.Dropdown(
                    choices=["North America", "Europe", "Asia Pacific", "Latin America", "Africa", "Global"],
                    label="Primary Region", value="Europe"
                )
            
            start_conversation_btn = gr.Button("Start ESG Assessment", variant="primary", size="lg")
        
        # Step 3: ESG Data Collection
        with gr.Group(visible=False) as step3:
            gr.HTML("""
            <div class="step-container">
                <div class="step-header">
                    <div class="step-number">3</div>
                    <div>
                        <div class="step-title">ESG Assessment</div>
                        <div class="step-description">Engage with our AI assistant for comprehensive ESG data collection</div>
                    </div>
                </div>
            </div>
            """)
            
            chatbot = gr.Chatbot(
                label="ESG Data Collection Assistant",
                height=500,
                show_label=True,
                container=True,
                type="messages"
            )
            
            with gr.Row():
                msg_input = gr.Textbox(
                    label="Your Response",
                    placeholder="Type your answer here...",
                    scale=4,
                    container=False
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
        
        # Step 4: Report Generation
        with gr.Group(visible=False) as step4:
            gr.HTML("""
            <div class="step-container">
                <div class="step-header">
                    <div class="step-number">4</div>
                    <div>
                        <div class="step-title">Report Generation</div>
                        <div class="step-description">Generate your comprehensive ESG report with AI insights and regulatory compliance</div>
                    </div>
                </div>
            </div>
            """)
            
            generate_report_btn = gr.Button("Generate Report", variant="primary", size="lg")
            report_status = gr.HTML()
            report_download = gr.File(label="Download Your 🍃 SustainPilot 🍃 ESG Report", visible=False)
        
        # Event handlers
        
        # Step 1 -> Step 2 (Research)
        research_btn.click(
            fn=lambda url, name: asyncio.run(research_company_and_advance(url, name)),
            inputs=[company_url_input, company_name_input],
            outputs=[step1, research_output, step2, step3, step4, gr.State()]
        ).then(
            fn=lambda state: (
                state.get("name", ""),
                state.get("industry", "Technology"),
                state.get("size", "Medium (50-500 employees)")
            ) if state else ("", "Technology", "Medium (50-500 employees)"),
            inputs=[gr.State()],
            outputs=[company_name_final, industry_input, size_input]
        )
        
        # Step 1 -> Step 2 (Skip)
        skip_btn.click(
            fn=lambda name: asyncio.run(research_company_and_advance("", name)),
            inputs=[company_name_input],
            outputs=[step1, research_output, step2, step3, step4, gr.State()]
        ).then(
            fn=lambda state: (
                state.get("name", ""),
                state.get("industry", "Technology"),
                state.get("size", "Medium (50-500 employees)")
            ) if state else ("", "Technology", "Medium (50-500 employees)"),
            inputs=[gr.State()],
            outputs=[company_name_final, industry_input, size_input]
        )
        
        # Step 2 -> Step 3
        start_conversation_btn.click(
            fn=lambda name, industry, size, region: asyncio.run(start_conversation_and_advance(name, industry, size, region)),
            inputs=[company_name_final, industry_input, size_input, region_input],
            outputs=[step2, step3, step4, chatbot]
        )
        
        # Chat processing with automatic advancement to Step 4
        def submit_message(message, history):
            return asyncio.run(process_chat_and_check_completion(message, history))
        
        msg_input.submit(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input, step3, step4]
        )
        
        send_btn.click(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input, step3, step4]
        )
        
        # Final report generation
        def generate_report():
            file_path, status = asyncio.run(generate_final_report())
            if file_path:
                return gr.File(value=file_path, visible=True), status
            else:
                return gr.File(visible=False), status
        
        generate_report_btn.click(
            fn=generate_report,
            outputs=[report_download, report_status]
        )
    
    return interface

if __name__ == "__main__":
    # Create and launch the beautiful interface
    interface = create_beautiful_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7865,
        share=False,
        debug=True
    )
                