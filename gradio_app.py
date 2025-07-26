"""
Gradio-based ESG Report Generator with Enhanced Chat Interface
"""
import gradio as gr
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import our agentic components
from src.agents.orchestrator import AgentOrchestrator
from src.config import Config
from src.report_generator import ESGReportGenerator

# Global state management
class ESGAppState:
    def __init__(self):
        self.orchestrator = None
        self.company_info = {}
        self.conversation_started = False
        self.company_research = None
        self.conversation_data = {}
        self.assessment_complete = False
        self.uploaded_documents = []
        
    async def initialize_orchestrator(self):
        """Initialize the agent orchestrator"""
        if not self.orchestrator:
            self.orchestrator = AgentOrchestrator(Config.get_config())
            await self.orchestrator.initialize()
        return self.orchestrator

# Global app state
app_state = ESGAppState()

async def research_company_url(company_url: str, company_name: str) -> Tuple[str, Dict]:
    """Research company from URL"""
    if not company_url.strip():
        return "Please enter a company URL to research.", {}
    
    try:
        orchestrator = await app_state.initialize_orchestrator()
        research_result = await orchestrator.research_company_from_url(company_url, company_name)
        
        if research_result.get("success"):
            app_state.company_research = research_result
            company_info = research_result.get("company_info", {})
            
            # Format research results for display
            basic_info = company_info.get("basic_info", {})
            business_info = company_info.get("business_info", {})
            esg_indicators = company_info.get("esg_indicators", {})
            
            result_text = f"""✅ **Company Research Completed!**

**Basic Information:**
• Company: {basic_info.get('name', 'Unknown')}
• Industry: {business_info.get('industry', 'Unknown')}
• Size: {business_info.get('size', 'Unknown')}

**ESG Presence:**
• Sustainability Page: {'✅ Yes' if esg_indicators.get('has_sustainability_page') else '❌ No'}
• ESG Mentions: {'✅ Yes' if esg_indicators.get('mentions_esg') else '❌ No'}
• CSR Report: {'✅ Yes' if esg_indicators.get('has_csr_report') else '❌ No'}

**Environmental Commitments:**
{chr(10).join(f'• {commitment}' for commitment in esg_indicators.get('environmental_commitments', [])[:3])}

Ready to start ESG data collection with this information!"""
            
            return result_text, {
                "name": basic_info.get('name', ''),
                "industry": business_info.get('industry', 'Technology'),
                "size": business_info.get('size', 'Medium'),
                "website": company_url
            }
        else:
            return f"❌ Research failed: {research_result.get('error', 'Unknown error')}", {}
            
    except Exception as e:
        return f"❌ Error during research: {str(e)}", {}

async def start_esg_conversation(company_name: str, industry: str, size: str, region: str, website: str) -> Tuple[List, str]:
    """Start the ESG data collection conversation"""
    try:
        # Prepare company info
        company_info = {
            "name": company_name or "Your Company",
            "industry": industry,
            "size": size.split(" ")[0] if size else "Medium",
            "region": region,
            "website": website,
            "research_data": app_state.company_research.get("company_info", {}) if app_state.company_research else {}
        }
        
        app_state.company_info = company_info
        
        # Initialize orchestrator and start conversation
        orchestrator = await app_state.initialize_orchestrator()
        conversation_result = await orchestrator.start_conversation(company_info)
        
        app_state.conversation_started = True
        
        # Create initial chat history
        chat_history = [
            {"role": "assistant", "content": conversation_result.get("message", "Welcome to ESG data collection!")}
        ]
        
        return chat_history, "Conversation started! Please answer the questions to collect your ESG data."
        
    except Exception as e:
        error_msg = f"Error starting conversation: {str(e)}"
        return [[None, error_msg]], error_msg

async def process_chat_message(message: str, chat_history: List) -> Tuple[List, str]:
    """Process user message in the chat"""
    if not app_state.conversation_started:
        return chat_history, "Please start the conversation first by filling in company details."
    
    try:
        # Add user message to chat history
        chat_history.append({"role": "user", "content": message})
        
        # Process with orchestrator
        orchestrator = await app_state.initialize_orchestrator()
        response = await orchestrator.process_conversation_message(message)
        
        # Add assistant response
        assistant_message = response.get("message", "Thank you for your response.")
        
        # Check if assessment is complete
        if response.get("ready_for_report", False):
            app_state.assessment_complete = True
            app_state.conversation_data = orchestrator.get_conversation_data_for_report()
            
            completion_message = "\n\n🎉 **ESG Data Collection Complete!**\n\nYou can now generate your comprehensive ESG report using the 'Generate Report' button."
            assistant_message += completion_message
        
        chat_history.append({"role": "assistant", "content": assistant_message})
        
        return chat_history, ""
        
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        chat_history.append({"role": "assistant", "content": error_msg})
        return chat_history, ""

async def generate_esg_report() -> Tuple[str, str]:
    """Generate the ESG report"""
    if not app_state.assessment_complete:
        return None, "❌ Please complete the ESG data collection first."
    
    try:
        # Generate insights using the orchestrator
        orchestrator = await app_state.initialize_orchestrator()
        insights = await orchestrator.generate_esg_insights(
            {},  # assessment data
            app_state.conversation_data.get("knowledge_collected", {})
        )
        
        # Generate PDF report
        report_generator = ESGReportGenerator()
        pdf_bytes = report_generator.generate_report(
            app_state.company_info,
            {},  # assessment data
            app_state.conversation_data.get("knowledge_collected", {}),
            insights
        )
        
        # Save PDF to temporary file (use current directory instead of /tmp)
        import os
        filename = f"ESG_Report_{app_state.company_info.get('name', 'Company').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        temp_path = os.path.join(os.getcwd(), filename)
        
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)
        
        return temp_path, "✅ ESG Report generated successfully! Click below to download."
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Report generation error: {error_details}")
        return None, f"❌ Error generating report: {str(e)}"

def create_gradio_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        title="ESG Report Generator",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .chat-message {
            font-size: 14px !important;
        }
        .company-info {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        """
    ) as interface:
        
        gr.Markdown(
            """
            # 🌱 ESG Report Generator
            
            **Comprehensive ESG Assessment & Reporting Platform**
            
            This tool helps you collect ESG data through a structured conversation and generates professional reports compliant with EU regulations (CSRD, EU Taxonomy, SFDR).
            """
        )
        
        with gr.Tab("🏢 Company Setup"):
            gr.Markdown("### Company Information & Research")
            
            with gr.Row():
                with gr.Column(scale=2):
                    company_url_input = gr.Textbox(
                        label="Company Website URL",
                        placeholder="https://www.yourcompany.com",
                        info="We'll analyze your website to gather public ESG information"
                    )
                    company_name_input = gr.Textbox(
                        label="Company Name",
                        placeholder="Your Company Name"
                    )
                with gr.Column(scale=1):
                    research_btn = gr.Button("🔍 Research Company", variant="secondary")
            
            research_output = gr.Markdown(label="Research Results")
            
            gr.Markdown("### Manual Company Details")
            
            with gr.Row():
                industry_input = gr.Dropdown(
                    choices=["Technology", "Manufacturing", "Financial", "Healthcare", "Energy", "Retail", "Other"],
                    label="Industry",
                    value="Technology"
                )
                size_input = gr.Dropdown(
                    choices=["Small (< 50 employees)", "Medium (50-500 employees)", "Large (> 500 employees)"],
                    label="Company Size",
                    value="Medium (50-500 employees)"
                )
                region_input = gr.Dropdown(
                    choices=["North America", "Europe", "Asia Pacific", "Latin America", "Africa", "Global"],
                    label="Primary Region",
                    value="Europe"
                )
            
            start_conversation_btn = gr.Button("🚀 Start ESG Data Collection", variant="primary", size="lg")
            conversation_status = gr.Markdown()
        
        with gr.Tab("💬 ESG Data Collection"):
            gr.Markdown("### ESG Knowledge Collection Chat")
            gr.Markdown("*Answer the questions below to collect your ESG data. Provide concise, factual responses.*")
            
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
            
            gr.Markdown("*💡 Tip: Provide specific, factual answers. Examples: '150 employees', '30%', 'Yes', 'No', etc.*")
        
        with gr.Tab("📊 Report Generation"):
            gr.Markdown("### Generate Your ESG Report")
            gr.Markdown("*Complete the data collection to generate your comprehensive ESG assessment report.*")
            
            generate_btn = gr.Button("📥 Generate ESG Report", variant="primary", size="lg")
            report_status = gr.Markdown()
            report_download = gr.File(label="Download Report", visible=False)
        
        # Event handlers
        def research_wrapper(company_url, company_name):
            result_text, research_data = asyncio.run(research_company_url(company_url, company_name))
            return (
                result_text,
                research_data.get("name", ""),
                research_data.get("industry", "Technology"),
                research_data.get("size", "Medium (50-500 employees)")
            )
        
        research_btn.click(
            fn=research_wrapper,
            inputs=[company_url_input, company_name_input],
            outputs=[research_output, company_name_input, industry_input, size_input]
        )
        
        def start_conversation_wrapper(company_name, industry, size, region, website):
            return asyncio.run(start_esg_conversation(company_name, industry, size, region, website))
        
        start_conversation_btn.click(
            fn=start_conversation_wrapper,
            inputs=[company_name_input, industry_input, size_input, region_input, company_url_input],
            outputs=[chatbot, conversation_status]
        )
        
        # Chat functionality
        def submit_message(message, history):
            return asyncio.run(process_chat_message(message, history))
        
        msg_input.submit(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        send_btn.click(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        # Report generation
        def generate_report():
            file_path, status = asyncio.run(generate_esg_report())
            if file_path:
                return gr.File(value=file_path, visible=True), status
            else:
                return gr.File(visible=False), status
        
        generate_btn.click(
            fn=generate_report,
            outputs=[report_download, report_status]
        )
    
    return interface

if __name__ == "__main__":
    # Create and launch the Gradio interface
    interface = create_gradio_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        debug=True
    )