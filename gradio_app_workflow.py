"""
Gradio-based ESG Report Generator with Seamless Workflow
Single-page interface with automatic progression through steps
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
        """Initialize the agent orchestrator"""
        if not self.orchestrator:
            self.orchestrator = AgentOrchestrator(Config.get_config())
            await self.orchestrator.initialize()
        return self.orchestrator

# Global app state
workflow_state = ESGWorkflowState()

async def research_company_and_advance(company_url: str, company_name: str) -> Tuple[str, str, str, str, str, Dict]:
    """Research company and automatically advance to next step"""
    if not company_url.strip():
        # Skip research and go directly to manual setup
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
            gr.update(visible=False),  # Hide step 1
            "⏭️ **Skipping company research** - proceeding to manual setup.",
            gr.update(visible=True),   # Show step 2
            gr.update(visible=False),  # Keep step 3 hidden
            gr.update(visible=False),  # Keep step 4 hidden
            workflow_state.company_info
        )
    
    try:
        orchestrator = await workflow_state.initialize_orchestrator()
        research_result = await orchestrator.research_company_from_url(company_url, company_name)
        
        if research_result.get("success"):
            workflow_state.company_research = research_result
            workflow_state.current_step = 2
            company_info = research_result.get("company_info", {})
            
            # Format research results
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

**✨ Proceeding to company setup...**"""
            
            # Store company info
            workflow_state.company_info = {
                "name": basic_info.get('name', company_name),
                "industry": business_info.get('industry', 'Technology'),
                "size": business_info.get('size', 'Medium'),
                "region": "Europe",
                "website": company_url,
                "research_data": company_info
            }
            
            return (
                gr.update(visible=False),  # Hide step 1
                result_text,
                gr.update(visible=True),   # Show step 2
                gr.update(visible=False),  # Keep step 3 hidden
                gr.update(visible=False),  # Keep step 4 hidden
                workflow_state.company_info
            )
        else:
            return (
                gr.update(visible=True),   # Keep step 1 visible
                f"❌ Research failed: {research_result.get('error', 'Unknown error')}",
                gr.update(visible=False),  # Keep step 2 hidden
                gr.update(visible=False),  # Keep step 3 hidden
                gr.update(visible=False),  # Keep step 4 hidden
                {}
            )
            
    except Exception as e:
        return (
            gr.update(visible=True),   # Keep step 1 visible
            f"❌ Error during research: {str(e)}",
            gr.update(visible=False),  # Keep step 2 hidden
            gr.update(visible=False),  # Keep step 3 hidden
            gr.update(visible=False),  # Keep step 4 hidden
            {}
        )

async def start_conversation_and_advance(company_name: str, industry: str, size: str, region: str) -> Tuple[str, str, str, List]:
    """Start conversation and advance to chat step"""
    try:
        # Update company info if manually entered
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
            # Update with manual overrides
            workflow_state.company_info.update({
                "name": company_name or workflow_state.company_info.get("name", "Your Company"),
                "industry": industry,
                "size": size.split(" ")[0] if size else "Medium",
                "region": region
            })
        
        workflow_state.current_step = 3
        
        # Initialize conversation
        orchestrator = await workflow_state.initialize_orchestrator()
        conversation_result = await orchestrator.start_conversation(workflow_state.company_info)
        
        # Create initial chat history
        chat_history = [
            {"role": "assistant", "content": conversation_result.get("message", "Welcome to ESG data collection!")}
        ]
        
        return (
            gr.update(visible=False),  # Hide step 2
            gr.update(visible=True),   # Show step 3
            gr.update(visible=False),  # Keep step 4 hidden
            chat_history
        )
        
    except Exception as e:
        error_msg = f"Error starting conversation: {str(e)}"
        return (
            gr.update(visible=True),   # Keep step 2 visible
            gr.update(visible=False),  # Keep step 3 hidden
            gr.update(visible=False),  # Keep step 4 hidden
            [{"role": "assistant", "content": error_msg}]
        )

async def process_chat_and_check_completion(message: str, chat_history: List) -> Tuple[List, str, str, str]:
    """Process chat message and check if ready for report generation"""
    try:
        # Add user message
        chat_history.append({"role": "user", "content": message})
        
        # Process with orchestrator
        orchestrator = await workflow_state.initialize_orchestrator()
        response = await orchestrator.process_conversation_message(message)
        
        # Add assistant response
        assistant_message = response.get("message", "Thank you for your response.")
        
        # Check if assessment is complete
        if response.get("ready_for_report", False):
            workflow_state.assessment_complete = True
            workflow_state.conversation_data = orchestrator.get_conversation_data_for_report()
            workflow_state.current_step = 4
            
            completion_message = "\n\n🎉 **ESG Data Collection Complete!**\n\n✨ **Automatically proceeding to report generation...**"
            assistant_message += completion_message
            
            chat_history.append({"role": "assistant", "content": assistant_message})
            
            return (
                chat_history,
                "",  # Clear input
                gr.update(visible=False),  # Hide step 3
                gr.update(visible=True)    # Show step 4
            )
        else:
            chat_history.append({"role": "assistant", "content": assistant_message})
            
            return (
                chat_history,
                "",  # Clear input
                gr.update(visible=True),   # Keep step 3 visible
                gr.update(visible=False)   # Keep step 4 hidden
            )
        
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        chat_history.append({"role": "assistant", "content": error_msg})
        return (
            chat_history,
            "",
            gr.update(visible=True),   # Keep step 3 visible
            gr.update(visible=False)   # Keep step 4 hidden
        )

async def generate_final_report() -> Tuple[str, str]:
    """Generate the final ESG report using enhanced generator with real data"""
    if not workflow_state.assessment_complete:
        return None, "❌ Please complete the ESG data collection first."
    
    try:
        # Initialize enhanced search agent for current regulations
        search_agent = EnhancedSearchAgent()
        
        # Get current regulations data
        regulations_data = await search_agent.get_current_regulations()
        
        # Generate insights
        orchestrator = await workflow_state.initialize_orchestrator()
        insights = await orchestrator.generate_esg_insights(
            {},
            workflow_state.conversation_data.get("knowledge_collected", {})
        )
        
        # Generate PDF report using enhanced generator
        report_generator = EnhancedESGReportGenerator()
        pdf_bytes = report_generator.generate_report(
            workflow_state.company_info,
            {},  # assessment_data (legacy parameter)
            workflow_state.conversation_data.get("knowledge_collected", {}),
            insights,
            regulations_data  # Current regulations data
        )
        
        # Save PDF
        import os
        filename = f"SustainPilot_ESG_Report_{workflow_state.company_info.get('name', 'Company').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        temp_path = os.path.join(os.getcwd(), filename)
        
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)
        
        return temp_path, "✅ **Enhanced ESG Report Generated Successfully!**\n\n🎊 **Congratulations!** Your comprehensive ESG assessment is complete with real data and current regulations. Click below to download your professional report."
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Enhanced report generation error: {error_details}")
        return None, f"❌ Error generating enhanced report: {str(e)}"

def create_workflow_interface():
    """Create the seamless workflow interface"""
    
    with gr.Blocks(
        title="SustainPilot - Seamless ESG Workflow",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1000px !important;
        }
        .step-container {
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        }
        .step-header {
            font-size: 24px;
            font-weight: bold;
            color: #2E8B57;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .step-number {
            background: #2E8B57;
            color: white;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
        }
        .progress-bar {
            height: 8px;
            background: #e1e5e9;
            border-radius: 4px;
            margin: 20px 0;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #2E8B57, #4169E1);
            transition: width 0.5s ease;
        }
        """
    ) as interface:
        
        gr.Markdown(
            """
            # 🌱 SustainPilot
            
            **Seamless ESG Workflow - From Company Research to Professional Report**
            
            Follow the guided steps below. The interface will automatically advance as you complete each section.
            """
        )
        
        # Progress indicator
        progress_html = gr.HTML(
            """
            <div class="progress-bar">
                <div class="progress-fill" style="width: 25%"></div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">
                <strong>Step 1 of 4:</strong> Company Research & Setup
            </p>
            """
        )
        
        # Step 1: Company Research
        with gr.Group(visible=True) as step1:
            gr.HTML('<div class="step-header"><div class="step-number">1</div>Company Research & Information</div>')
            
            gr.Markdown("### 🔍 Company Research (Optional)")
            gr.Markdown("*Enter your company website URL for automatic ESG data collection, or skip directly to manual setup.*")
            
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
                    research_btn = gr.Button("🔍 Research & Continue", variant="primary", size="lg")
                    skip_btn = gr.Button("⏭️ Skip to Manual Setup", variant="secondary", size="lg")
            
            research_output = gr.Markdown()
        
        # Step 2: Company Details
        with gr.Group(visible=False) as step2:
            gr.HTML('<div class="step-header"><div class="step-number">2</div>Company Details Confirmation</div>')
            
            gr.Markdown("### ✏️ Confirm or Update Company Information")
            gr.Markdown("*Review and update the information below, then proceed to data collection.*")
            
            with gr.Row():
                company_name_final = gr.Textbox(
                    label="Company Name",
                    placeholder="Your Company Name"
                )
                industry_input = gr.Dropdown(
                    choices=["Technology", "Manufacturing", "Financial", "Healthcare", "Energy", "Retail", "Other"],
                    label="Industry",
                    value="Technology"
                )
            
            with gr.Row():
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
        
        # Step 3: ESG Data Collection
        with gr.Group(visible=False) as step3:
            gr.HTML('<div class="step-header"><div class="step-number">3</div>ESG Data Collection Chat</div>')
            
            gr.Markdown("### 💬 Interactive ESG Assessment")
            gr.Markdown("*Answer the questions below to collect your ESG data. The system will automatically proceed to report generation when complete.*")
            
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
            
            gr.Markdown("*💡 Tip: Provide specific, factual answers. The interface will automatically advance when data collection is complete.*")
        
        # Step 4: Report Generation
        with gr.Group(visible=False) as step4:
            gr.HTML('<div class="step-header"><div class="step-number">4</div>ESG Report Generation</div>')
            
            gr.Markdown("### 📊 Generate Your Professional ESG Report")
            gr.Markdown("*Your data collection is complete! Generate and download your comprehensive ESG assessment report.*")
            
            generate_btn = gr.Button("📥 Generate ESG Report", variant="primary", size="lg")
            report_status = gr.Markdown()
            report_download = gr.File(label="Download Your ESG Report", visible=False)
        
        # Event handlers with automatic progression
        
        # Step 1 -> Step 2 (Research)
        research_btn.click(
            fn=lambda url, name: asyncio.run(research_company_and_advance(url, name)),
            inputs=[company_url_input, company_name_input],
            outputs=[step1, research_output, step2, step3, step4, gr.State()]
        ).then(
            fn=lambda: """
            <div class="progress-bar">
                <div class="progress-fill" style="width: 50%"></div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">
                <strong>Step 2 of 4:</strong> Company Details Confirmation
            </p>
            """,
            outputs=[progress_html]
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
            fn=lambda: """
            <div class="progress-bar">
                <div class="progress-fill" style="width: 50%"></div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">
                <strong>Step 2 of 4:</strong> Company Details Setup
            </p>
            """,
            outputs=[progress_html]
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
        ).then(
            fn=lambda: """
            <div class="progress-bar">
                <div class="progress-fill" style="width: 75%"></div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">
                <strong>Step 3 of 4:</strong> ESG Data Collection in Progress
            </p>
            """,
            outputs=[progress_html]
        )
        
        # Chat processing with automatic advancement to Step 4
        def submit_message(message, history):
            return asyncio.run(process_chat_and_check_completion(message, history))
        
        msg_input.submit(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input, step3, step4]
        ).then(
            fn=lambda step4_visible: """
            <div class="progress-bar">
                <div class="progress-fill" style="width: 100%"></div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">
                <strong>Step 4 of 4:</strong> Ready for Report Generation! 🎉
            </p>
            """ if step4_visible else """
            <div class="progress-bar">
                <div class="progress-fill" style="width: 75%"></div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">
                <strong>Step 3 of 4:</strong> ESG Data Collection in Progress
            </p>
            """,
            inputs=[step4],
            outputs=[progress_html]
        )
        
        send_btn.click(
            fn=submit_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input, step3, step4]
        ).then(
            fn=lambda step4_visible: """
            <div class="progress-bar">
                <div class="progress-fill" style="width: 100%"></div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">
                <strong>Step 4 of 4:</strong> Ready for Report Generation! 🎉
            </p>
            """ if step4_visible else """
            <div class="progress-bar">
                <div class="progress-fill" style="width: 75%"></div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">
                <strong>Step 3 of 4:</strong> ESG Data Collection in Progress
            </p>
            """,
            inputs=[step4],
            outputs=[progress_html]
        )
        
        # Final report generation
        def generate_report():
            file_path, status = asyncio.run(generate_final_report())
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
    # Create and launch the workflow interface
    interface = create_workflow_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        debug=True
    )