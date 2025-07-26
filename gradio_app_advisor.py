"""
Enhanced ESG Report Generator with Intelligent Advisory Agent
Includes interactive consultation, regulatory advice, and improvement suggestions
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
from src.agents.report_advisor_agent import ReportAdvisorAgent
from src.config import Config
from src.enhanced_report_generator import EnhancedESGReportGenerator
from src.agents.enhanced_search_agent import EnhancedSearchAgent

# Global state management
class ESGAdvisoryWorkflowState:
    def __init__(self):
        self.orchestrator = None
        self.advisor_agent = None
        self.current_step = 1
        self.company_info = {}
        self.company_research = None
        self.conversation_data = {}
        self.assessment_complete = False
        self.uploaded_documents = []
        self.advisory_session = {}
        
    async def initialize_agents(self):
        """Initialize all agents"""
        if not self.orchestrator:
            self.orchestrator = AgentOrchestrator(Config.get_config())
            await self.orchestrator.initialize()
        
        if not self.advisor_agent:
            self.advisor_agent = ReportAdvisorAgent(Config.get_config())
        
        return self.orchestrator, self.advisor_agent

# Global app state
workflow_state = ESGAdvisoryWorkflowState()

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
        orchestrator, _ = await workflow_state.initialize_agents()
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
        orchestrator, _ = await workflow_state.initialize_agents()
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
        orchestrator, _ = await workflow_state.initialize_agents()
        response = await orchestrator.process_conversation_message(message)
        
        # Add assistant response
        assistant_message = response.get("message", "Thank you for your response.")
        
        # Check if assessment is complete
        if response.get("ready_for_report", False):
            workflow_state.assessment_complete = True
            workflow_state.conversation_data = orchestrator.get_conversation_data_for_report()
            workflow_state.current_step = 4
            
            completion_message = "\n\n🎉 **ESG Data Collection Complete!**\n\n✨ **Automatically proceeding to intelligent advisory and report generation...**"
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

async def get_regulatory_advice(regulation: str) -> str:
    """Get regulatory advice from advisor agent"""
    try:
        _, advisor_agent = await workflow_state.initialize_agents()
        
        advice_result = await advisor_agent.execute({
            "type": "regulatory_advice",
            "regulation": regulation,
            "context": workflow_state.company_info
        })
        
        if advice_result.get("error"):
            return f"❌ Error getting advice: {advice_result['error']}"
        
        # Format advice response
        advice_text = f"""## 📋 Regulatory Advice: {regulation}

**AI Expert Analysis:**
{advice_result.get('ai_advice', 'No AI advice available')}

**Priority Level:** {advice_result.get('priority_level', 'Medium')}

**Timeline:** {advice_result.get('timeline', {}).get('deadline', 'TBD')}

**Key Requirements:**
{chr(10).join(f'• {req}' for req in advice_result.get('structured_guidance', {}).get('key_requirements', []))}

**Preparation Steps:**
{chr(10).join(f'• {step}' for step in advice_result.get('structured_guidance', {}).get('preparation_steps', []))}

**Resources:**
{chr(10).join(f'• {resource}' for resource in advice_result.get('resources', []))}
"""
        
        return advice_text
        
    except Exception as e:
        return f"❌ Error getting regulatory advice: {str(e)}"

async def get_improvement_suggestions() -> str:
    """Get improvement suggestions from advisor agent"""
    if not workflow_state.assessment_complete:
        return "❌ Please complete the ESG data collection first to get personalized improvement suggestions."
    
    try:
        _, advisor_agent = await workflow_state.initialize_agents()
        
        suggestions_result = await advisor_agent.execute({
            "type": "improvement_suggestions",
            "knowledge_collected": workflow_state.conversation_data.get("knowledge_collected", {}),
            "company_info": workflow_state.company_info
        })
        
        if suggestions_result.get("error"):
            return f"❌ Error getting suggestions: {suggestions_result['error']}"
        
        # Format suggestions response
        suggestions_text = f"""## 🚀 Personalized Improvement Suggestions

**Company:** {suggestions_result.get('company', 'Your Company')}
**Industry:** {suggestions_result.get('industry', 'Technology')}

**AI-Powered Analysis:**
{suggestions_result.get('ai_suggestions', 'No AI suggestions available')}

**Framework-Based Recommendations:**
"""
        
        framework_suggestions = suggestions_result.get('framework_suggestions', {})
        for category, suggestions in framework_suggestions.items():
            suggestions_text += f"\n**{category.title()}:**\n"
            for suggestion in suggestions[:3]:
                suggestions_text += f"• {suggestion}\n"
        
        # Add priority matrix
        priority_matrix = suggestions_result.get('priority_matrix', {})
        if priority_matrix:
            suggestions_text += f"""
**Priority Matrix:**
• **High Impact, Low Effort:** {', '.join(priority_matrix.get('high_impact_low_effort', []))}
• **High Impact, High Effort:** {', '.join(priority_matrix.get('high_impact_high_effort', []))}
"""
        
        return suggestions_text
        
    except Exception as e:
        return f"❌ Error getting improvement suggestions: {str(e)}"

async def get_future_roadmap() -> str:
    """Get future roadmap from advisor agent"""
    if not workflow_state.assessment_complete:
        return "❌ Please complete the ESG data collection first to get a personalized roadmap."
    
    try:
        _, advisor_agent = await workflow_state.initialize_agents()
        
        roadmap_result = await advisor_agent.execute({
            "type": "future_roadmap",
            "knowledge_collected": workflow_state.conversation_data.get("knowledge_collected", {}),
            "company_info": workflow_state.company_info
        })
        
        if roadmap_result.get("error"):
            return f"❌ Error creating roadmap: {roadmap_result['error']}"
        
        # Format roadmap response
        roadmap_text = f"""## 🗺️ Strategic ESG Roadmap (2024-2026)

**Company:** {roadmap_result.get('company', 'Your Company')}

**AI-Generated Strategic Roadmap:**
{roadmap_result.get('ai_roadmap', 'No roadmap available')}

**Strategic Themes:**
{chr(10).join(f'• {theme}' for theme in roadmap_result.get('strategic_themes', []))}

**Investment Priorities:**
"""
        
        investment_priorities = roadmap_result.get('investment_priorities', {})
        for category, priority in investment_priorities.items():
            roadmap_text += f"• **{category}:** {priority}\n"
        
        roadmap_text += f"""
**Success Metrics:**
{chr(10).join(f'• {metric}' for metric in roadmap_result.get('success_metrics', []))}

**Risk Considerations:**
{chr(10).join(f'• {risk}' for risk in roadmap_result.get('risk_considerations', []))}
"""
        
        return roadmap_text
        
    except Exception as e:
        return f"❌ Error creating future roadmap: {str(e)}"

async def interactive_consultation(question: str, consultation_history: List) -> Tuple[List, str]:
    """Handle interactive consultation with advisor agent"""
    if not question.strip():
        return consultation_history, ""
    
    try:
        # Add user question
        consultation_history.append({"role": "user", "content": question})
        
        _, advisor_agent = await workflow_state.initialize_agents()
        
        consultation_result = await advisor_agent.execute({
            "type": "interactive_consultation",
            "question": question,
            "context": {
                "company_info": workflow_state.company_info,
                "assessment_complete": workflow_state.assessment_complete,
                "knowledge_collected": workflow_state.conversation_data.get("knowledge_collected", {})
            }
        })
        
        if consultation_result.get("error"):
            response = f"❌ Error in consultation: {consultation_result['error']}"
        else:
            # Format consultation response
            response = f"""**Expert Response:**
{consultation_result.get('expert_response', 'No response available')}

**Regulatory Context:**
{chr(10).join(f'• {context}' for context in consultation_result.get('regulatory_context', []))}

**Related Topics:**
{chr(10).join(f'• {topic}' for topic in consultation_result.get('related_topics', []))}

**Follow-up Questions:**
{chr(10).join(f'• {q}' for q in consultation_result.get('follow_up_questions', []))}
"""
        
        consultation_history.append({"role": "assistant", "content": response})
        
        return consultation_history, ""
        
    except Exception as e:
        error_msg = f"❌ Error in consultation: {str(e)}"
        consultation_history.append({"role": "assistant", "content": error_msg})
        return consultation_history, ""

async def generate_enhanced_report() -> Tuple[str, str]:
    """Generate the enhanced ESG report with advisory insights"""
    if not workflow_state.assessment_complete:
        return None, "❌ Please complete the ESG data collection first."
    
    try:
        # Initialize enhanced search agent for current regulations
        search_agent = EnhancedSearchAgent()
        
        # Get current regulations data
        regulations_data = await search_agent.get_current_regulations()
        
        # Generate insights
        orchestrator, _ = await workflow_state.initialize_agents()
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
        
        return temp_path, "✅ **Enhanced ESG Report Generated Successfully!**\n\n🎊 **Congratulations!** Your comprehensive ESG assessment with intelligent advisory insights is complete. The report includes real data, current regulations, and personalized recommendations. Click below to download your professional report."
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Enhanced report generation error: {error_details}")
        return None, f"❌ Error generating enhanced report: {str(e)}"

def create_advisory_workflow_interface():
    """Create the enhanced workflow interface with advisory capabilities"""
    
    with gr.Blocks(
        title="SustainPilot - Intelligent ESG Advisory",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .step-container {
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        }
        .advisory-container {
            border: 2px solid #2E8B57;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            background: linear-gradient(135deg, #f0f8f0 0%, #ffffff 100%);
        }
        .step-header {
            font-size: 24px;
            font-weight: bold;
            color: #2E8B57;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .advisory-header {
            font-size: 20px;
            font-weight: bold;
            color: #2E8B57;
            margin-bottom: 15px;
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
        """
    ) as interface:
        
        gr.Markdown(
            """
            # 🌱 SustainPilot
            
            **Complete ESG Assessment with AI-Powered Consultation and Regulatory Guidance**
            
            This enhanced system provides:
            • **Data Collection**: Comprehensive ESG data gathering
            • **Intelligent Advisory**: AI-powered regulatory advice and improvement suggestions
            • **Interactive Consultation**: Real-time ESG expert guidance
            • **Enhanced Reporting**: Professional reports with current regulations and personalized recommendations
            """
        )
        
        # Main workflow tabs
        with gr.Tabs():
            # Tab 1: ESG Assessment Workflow
            with gr.TabItem("📊 ESG Assessment Workflow"):
                
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
                    
                    start_conversation_btn = gr.Button("🚀 Start ESG Data Collection", variant="primary", size="lg")
                
                # Step 3: ESG Data Collection
                with gr.Group(visible=False) as step3:
                    gr.HTML('<div class="step-header"><div class="step-number">3</div>ESG Data Collection Chat</div>')
                    
                    gr.Markdown("### 💬 Interactive ESG Assessment")
                    
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
                
                # Step 4: Advisory and Report Generation
                with gr.Group(visible=False) as step4:
                    gr.HTML('<div class="step-header"><div class="step-number">4</div>Intelligent Advisory & Report Generation</div>')
                    
                    gr.Markdown("### 🤖 AI-Powered ESG Advisory Services")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("#### Quick Advisory Services")
                            
                            regulation_dropdown = gr.Dropdown(
                                choices=["CSRD", "EU_TAXONOMY", "SFDR", "SEC_CLIMATE"],
                                label="Select Regulation for Advice",
                                value="CSRD"
                            )
                            get_advice_btn = gr.Button("📋 Get Regulatory Advice", variant="secondary")
                            
                            get_suggestions_btn = gr.Button("🚀 Get Improvement Suggestions", variant="secondary")
                            get_roadmap_btn = gr.Button("🗺️ Get Future Roadmap", variant="secondary")
                            
                            generate_report_btn = gr.Button("📥 Generate Enhanced Report", variant="primary", size="lg")
                        
                        with gr.Column(scale=2):
                            advisory_output = gr.Markdown(label="Advisory Output", height=400)
                    
                    report_status = gr.Markdown()
                    report_download = gr.File(label="Download Your Enhanced ESG Report", visible=False)
            
            # Tab 2: Interactive ESG Consultation
            with gr.TabItem("💬 Interactive ESG Consultation"):
                
                with gr.Group():
                    gr.HTML('<div class="advisory-header">🤖 AI ESG Expert Consultation</div>')
                    
                    gr.Markdown("""
                    ### Ask Your ESG Questions
                    
                    Get expert advice on:
                    • **Regulatory Compliance**: CSRD, EU Taxonomy, SFDR requirements
                    • **Implementation Guidance**: Step-by-step compliance strategies
                    • **Best Practices**: Industry-specific ESG recommendations
                    • **Future Planning**: Strategic ESG roadmaps and trends
                    """)
                    
                    consultation_chatbot = gr.Chatbot(
                        label="ESG Expert Consultation",
                        height=600,
                        show_label=True,
                        container=True,
                        type="messages",
                        value=[{"role": "assistant", "content": "👋 Hello! I'm your AI ESG expert. Ask me anything about ESG regulations, compliance strategies, best practices, or implementation guidance. How can I help you today?"}]
                    )
                    
                    with gr.Row():
                        consultation_input = gr.Textbox(
                            label="Your ESG Question",
                            placeholder="Ask about regulations, compliance, best practices, implementation strategies...",
                            scale=4,
                            container=False
                        )
                        consultation_send_btn = gr.Button("Ask Expert", variant="primary", scale=1)
                    
                    gr.Markdown("""
                    **Example Questions:**
                    • "How do I prepare for CSRD compliance?"
                    • "What are the key requirements for EU Taxonomy alignment?"
                    • "How can I improve our Scope 3 emissions reporting?"
                    • "What ESG metrics should we track for our industry?"
                    """)
        
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
        
        # Advisory services
        get_advice_btn.click(
            fn=lambda reg: asyncio.run(get_regulatory_advice(reg)),
            inputs=[regulation_dropdown],
            outputs=[advisory_output]
        )
        
        get_suggestions_btn.click(
            fn=lambda: asyncio.run(get_improvement_suggestions()),
            outputs=[advisory_output]
        )
        
        get_roadmap_btn.click(
            fn=lambda: asyncio.run(get_future_roadmap()),
            outputs=[advisory_output]
        )
        
        # Interactive consultation
        def handle_consultation(question, history):
            return asyncio.run(interactive_consultation(question, history))
        
        consultation_input.submit(
            fn=handle_consultation,
            inputs=[consultation_input, consultation_chatbot],
            outputs=[consultation_chatbot, consultation_input]
        )
        
        consultation_send_btn.click(
            fn=handle_consultation,
            inputs=[consultation_input, consultation_chatbot],
            outputs=[consultation_chatbot, consultation_input]
        )
        
        # Final report generation
        def generate_report():
            file_path, status = asyncio.run(generate_enhanced_report())
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
    # Create and launch the enhanced advisory interface
    interface = create_advisory_workflow_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7863,
        share=False,
        debug=True
    )