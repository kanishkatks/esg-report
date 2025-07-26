"""
Agent Orchestrator for coordinating ESG system agents
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from .base_agent import BaseAgent, get_llm_service
from .search_agent import SearchAgent
from .regulations_agent import RegulationsAgent
from .eu_knowledge_manager import EUKnowledgeManager
from ..document_processor import document_processor


class AgentOrchestrator:
    """Orchestrates and coordinates multiple ESG system agents"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("orchestrator")
        
        # Initialize agents
        self.search_agent = SearchAgent(config)
        self.regulations_agent = RegulationsAgent(config)
        self.knowledge_manager = EUKnowledgeManager(config)
        self.llm_service = get_llm_service()
        self.document_processor = document_processor
        
        # Agent registry
        self.agents = {
            "search": self.search_agent,
            "regulations": self.regulations_agent,
            "knowledge": self.knowledge_manager
        }
        
        # Document processing state
        self.processed_documents: List[Dict[str, Any]] = []
        
        # Orchestrator state
        self.active_tasks: Dict[str, Any] = {}
        self.task_history: List[Dict[str, Any]] = []
        self.last_sync: Optional[datetime] = None
        
        # Background task scheduler
        self.background_tasks = set()
        self.update_intervals = {
            "regulations": 24 * 3600,  # 24 hours
            "knowledge": 12 * 3600,    # 12 hours
            "search_cache": 6 * 3600   # 6 hours
        }
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize all agents and perform initial sync"""
        self.logger.info("Initializing agent orchestrator...")
        
        initialization_results = {}
        
        try:
            # Initialize regulations database
            reg_result = await self.regulations_agent.run_task({
                "type": "update_regulations"
            })
            initialization_results["regulations"] = reg_result
            
            # Initialize knowledge base
            kb_result = await self.knowledge_manager.run_task({
                "type": "update_questions"
            })
            initialization_results["knowledge"] = kb_result
            
            # Perform initial search for current ESG trends
            search_result = await self.search_agent.run_task({
                "type": "standards_update"
            })
            initialization_results["search"] = search_result
            
            self.last_sync = datetime.now()
            
            self.logger.info("Agent orchestrator initialized successfully")
            
            return {
                "status": "initialized",
                "timestamp": self.last_sync.isoformat(),
                "agents_initialized": len(self.agents),
                "initialization_results": initialization_results
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def process_esg_assessment(self, company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process complete ESG assessment using coordinated agents"""
        assessment_id = f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Starting ESG assessment {assessment_id}")
        
        try:
            # Step 1: Get applicable regulations
            regulations_task = {
                "type": "get_applicable_regulations",
                "industry": company_info.get("industry", ""),
                "region": company_info.get("region", "")
            }
            regulations_result = await self.regulations_agent.run_task(regulations_task)
            
            # Step 2: Get tailored questions
            questions_task = {
                "type": "get_questions",
                "industry": company_info.get("industry", ""),
                "region": company_info.get("region", ""),
                "company_size": company_info.get("size", "")
            }
            questions_result = await self.knowledge_manager.run_task(questions_task)
            
            # Step 3: Get industry benchmarks
            benchmarks_task = {
                "type": "industry_benchmarks",
                "industry": company_info.get("industry", "")
            }
            benchmarks_result = await self.search_agent.run_task(benchmarks_task)
            
            # Step 4: Check compliance status
            compliance_task = {
                "type": "check_compliance",
                "company_data": company_info
            }
            compliance_result = await self.regulations_agent.run_task(compliance_task)
            
            return {
                "assessment_id": assessment_id,
                "status": "completed",
                "company_info": company_info,
                "applicable_regulations": regulations_result.get("result", {}),
                "assessment_questions": questions_result.get("result", {}),
                "industry_benchmarks": benchmarks_result.get("result", {}),
                "compliance_status": compliance_result.get("result", {}),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"ESG assessment failed: {str(e)}")
            return {
                "assessment_id": assessment_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def process_uploaded_documents(self, uploaded_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process uploaded documents and integrate with ESG assessment"""
        
        self.logger.info(f"Processing {len(uploaded_files)} uploaded documents")
        
        processing_results = []
        
        for file_info in uploaded_files:
            try:
                filename = file_info.get("filename", "unknown")
                file_content = file_info.get("content", b"")
                document_type = file_info.get("type", "sustainability_report")
                
                # Process document
                result = await self.document_processor.process_document(
                    file_content, filename, document_type
                )
                
                processing_results.append(result)
                
                # Store successful results
                if result.get("success"):
                    self.processed_documents.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing uploaded file: {str(e)}")
                processing_results.append({
                    "success": False,
                    "error": str(e),
                    "filename": file_info.get("filename", "unknown")
                })
        
        # Generate insights from all processed documents
        document_insights = self.document_processor.get_document_insights(self.processed_documents)
        
        return {
            "processing_results": processing_results,
            "total_processed": len([r for r in processing_results if r.get("success")]),
            "total_failed": len([r for r in processing_results if not r.get("success")]),
            "document_insights": document_insights,
            "processed_at": datetime.now().isoformat()
        }
    
    def get_processed_documents_summary(self) -> Dict[str, Any]:
        """Get summary of all processed documents"""
        return {
            "total_documents": len(self.processed_documents),
            "document_types": {},
            "processing_dates": [doc.get("processing_timestamp") for doc in self.processed_documents],
            "insights": self.document_processor.get_document_insights(self.processed_documents)
        }
    
    async def generate_esg_insights(self, assessment_data: Dict[str, Any], user_responses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ESG insights using LLM and agent data"""
        
        try:
            # Prepare context for LLM
            context = {
                "assessment_data": assessment_data,
                "user_responses": user_responses,
                "regulations": assessment_data.get("applicable_regulations", {}),
                "benchmarks": assessment_data.get("industry_benchmarks", {}),
                "compliance": assessment_data.get("compliance_status", {}),
                "processed_documents": self.processed_documents
            }
            
            # Generate analysis using LLM
            analysis_result = await self.llm_service.analyze_esg_data(context)
            
            # Enhance with agent-specific insights
            enhanced_insights = await self._enhance_insights_with_agents(analysis_result, context)
            
            return {
                "insights": enhanced_insights,
                "analysis_date": datetime.now().isoformat(),
                "data_sources": ["regulations_agent", "search_agent", "eu_knowledge_manager", "llm_service"],
                "document_insights": self.document_processor.get_document_insights(self.processed_documents) if self.processed_documents else None
            }
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {str(e)}")
            return {
                "insights": {"error": str(e)},
                "analysis_date": datetime.now().isoformat()
            }
    
    async def _enhance_insights_with_agents(self, base_insights: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance LLM insights with agent-specific data"""
        
        # Get latest regulatory updates
        reg_updates = await self.search_agent.run_task({
            "type": "regulation_search",
            "query": "latest ESG requirements"
        })
        
        # Get current standards
        standards = await self.search_agent.run_task({
            "type": "standards_update"
        })
        
        enhanced_insights = base_insights.copy()
        
        # Add regulatory context
        enhanced_insights["regulatory_context"] = {
            "recent_updates": reg_updates.get("result", {}).get("regulations", [])[:3],
            "current_standards": standards.get("result", {}).get("standards", [])[:3],
            "compliance_gaps": self._identify_compliance_gaps(context)
        }
        
        # Add industry-specific recommendations
        enhanced_insights["industry_recommendations"] = await self._get_industry_recommendations(
            context.get("assessment_data", {}).get("company_info", {}).get("industry", "")
        )
        
        # Add priority actions based on agent data
        enhanced_insights["priority_actions"] = self._generate_priority_actions(context, enhanced_insights)
        
        # Add document-based insights if available
        if context.get("processed_documents"):
            enhanced_insights["document_based_insights"] = self._extract_document_insights(context["processed_documents"])
        
        return enhanced_insights
    
    def _extract_document_insights(self, processed_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract insights from processed documents"""
        insights = {
            "total_documents": len(processed_documents),
            "key_findings": [],
            "compliance_indicators": [],
            "data_gaps": []
        }
        
        for doc in processed_documents:
            if doc.get("success") and doc.get("llm_analysis"):
                analysis = doc["llm_analysis"]
                
                # Extract key findings
                if analysis.get("extracted_metrics"):
                    insights["key_findings"].extend(analysis["extracted_metrics"][:3])
                
                # Extract compliance indicators
                if analysis.get("compliance_notes"):
                    insights["compliance_indicators"].extend(analysis["compliance_notes"][:2])
        
        return insights
    
    def _identify_compliance_gaps(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify compliance gaps from agent data"""
        gaps = []
        
        compliance_data = context.get("compliance", {})
        detailed_status = compliance_data.get("detailed_status", {})
        
        for reg_id, status in detailed_status.items():
            if status.get("compliance_score", 100) < 80:
                gaps.append({
                    "regulation": status.get("regulation_name", reg_id),
                    "score": status.get("compliance_score", 0),
                    "risk_level": status.get("risk_level", "Unknown"),
                    "required_actions": status.get("required_actions", [])
                })
        
        return gaps
    
    async def _get_industry_recommendations(self, industry: str) -> List[str]:
        """Get industry-specific recommendations with EU focus"""
        industry_recommendations = {
            "technology": [
                "Implement GDPR-compliant data privacy governance",
                "Establish carbon-neutral cloud infrastructure goals per EU Green Deal",
                "Develop AI ethics framework aligned with EU AI Act",
                "Enhance cybersecurity risk management for CSRD compliance"
            ],
            "manufacturing": [
                "Implement circular economy principles per EU Circular Economy Action Plan",
                "Establish comprehensive waste reduction programs for EU Taxonomy alignment",
                "Enhance supply chain due diligence per Corporate Sustainability Due Diligence Directive",
                "Develop worker safety programs meeting EU standards"
            ],
            "financial": [
                "Integrate ESG factors into investment decisions per SFDR",
                "Develop EU Taxonomy-aligned sustainable finance products",
                "Enhance climate risk assessment capabilities for CSRD",
                "Implement responsible lending practices per EU Banking regulations"
            ]
        }
        
        return industry_recommendations.get(industry.lower(), [
            "Develop comprehensive ESG governance framework per CSRD",
            "Establish stakeholder engagement processes for EU compliance",
            "Implement ESG performance monitoring aligned with ESRS",
            "Enhance sustainability reporting practices for EU Taxonomy"
        ])
    
    def _generate_priority_actions(self, context: Dict[str, Any], insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate priority actions based on all available data"""
        actions = []
        
        # High-priority actions from compliance gaps
        for gap in insights.get("regulatory_context", {}).get("compliance_gaps", []):
            if gap.get("risk_level") == "High":
                actions.append({
                    "priority": "High",
                    "action": f"Address compliance gap in {gap.get('regulation', 'Unknown')}",
                    "timeline": "Immediate (0-3 months)",
                    "impact": "EU regulatory compliance"
                })
        
        # Medium-priority actions from benchmarking
        benchmarks = context.get("benchmarks", {})
        if benchmarks.get("benchmarks"):
            actions.append({
                "priority": "Medium",
                "action": "Improve performance against industry benchmarks",
                "timeline": "Short-term (3-6 months)",
                "impact": "Competitive positioning"
            })
        
        # Document-based actions
        if context.get("processed_documents"):
            actions.append({
                "priority": "Medium",
                "action": "Address data gaps identified in uploaded documents",
                "timeline": "Short-term (3-6 months)",
                "impact": "Data quality and reporting"
            })
        
        # Long-term strategic actions
        actions.append({
            "priority": "Medium",
            "action": "Develop comprehensive ESG strategy aligned with EU directives",
            "timeline": "Medium-term (6-12 months)",
            "impact": "Strategic alignment with EU regulations"
        })
        
        return actions[:5]  # Return top 5 priority actions
    
    async def run_background_updates(self):
        """Run background updates for all agents"""
        self.logger.info("Starting background updates...")
        
        try:
            # Create background tasks
            tasks = [
                self._schedule_agent_updates(),
                self._monitor_agent_health(),
                self._cleanup_old_data()
            ]
            
            # Run tasks concurrently
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Background updates failed: {str(e)}")
    
    async def _schedule_agent_updates(self):
        """Schedule periodic agent updates"""
        while True:
            try:
                # Update regulations every 24 hours
                await self.regulations_agent.run_task({"type": "update_regulations"})
                
                # Update knowledge base every 12 hours
                await self.knowledge_manager.run_task({"type": "update_questions"})
                
                # Clear search cache every 6 hours
                self.search_agent.clear_cache()
                
                # Wait for next update cycle
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Scheduled updates failed: {str(e)}")
                await asyncio.sleep(3600)  # Wait before retrying
    
    async def _monitor_agent_health(self):
        """Monitor agent health and performance"""
        while True:
            try:
                for agent_name, agent in self.agents.items():
                    status = agent.get_status()
                    if status["metrics"]["errors"] > 10:
                        self.logger.warning(f"Agent {agent_name} has high error count: {status['metrics']['errors']}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Health monitoring failed: {str(e)}")
                await asyncio.sleep(300)
    
    async def _cleanup_old_data(self):
        """Cleanup old data and cache entries"""
        while True:
            try:
                # Clear old task history
                if len(self.task_history) > 1000:
                    self.task_history = self.task_history[-500:]
                
                # Clear old active tasks
                current_time = datetime.now()
                expired_tasks = [
                    task_id for task_id, task_data in self.active_tasks.items()
                    if (current_time - task_data.get("start_time", current_time)).total_seconds() > 3600
                ]
                
                for task_id in expired_tasks:
                    del self.active_tasks[task_id]
                
                await asyncio.sleep(1800)  # Cleanup every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Data cleanup failed: {str(e)}")
                await asyncio.sleep(1800)
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get overall orchestrator status"""
        agent_statuses = {
            name: agent.get_status() for name, agent in self.agents.items()
        }
        
        return {
            "orchestrator_status": "active",
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "active_tasks": len(self.active_tasks),
            "task_history_count": len(self.task_history),
            "processed_documents": len(self.processed_documents),
            "agents": agent_statuses,
            "background_tasks": len(self.background_tasks),
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        self.logger.info("Shutting down agent orchestrator...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for active tasks to complete
        if self.active_tasks:
            self.logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete...")
            await asyncio.sleep(5)  # Give tasks time to complete
        
        self.logger.info("Agent orchestrator shutdown complete")