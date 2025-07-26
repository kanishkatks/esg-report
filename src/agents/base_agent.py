"""
Base agent class for ESG system agents
"""
import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class BaseAgent(ABC):
    """Base class for all ESG system agents"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        self.status = "idle"
        self.last_update = None
        self.metrics = {
            "tasks_completed": 0,
            "errors": 0,
            "last_execution_time": 0
        }
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
    
    async def run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run a task with error handling and metrics"""
        start_time = datetime.now()
        self.status = "running"
        
        try:
            self.logger.info(f"Starting task: {task.get('type', 'unknown')}")
            result = await self.execute(task)
            
            self.metrics["tasks_completed"] += 1
            self.status = "completed"
            self.last_update = datetime.now()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics["last_execution_time"] = execution_time
            
            self.logger.info(f"Task completed in {execution_time:.2f}s")
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "timestamp": self.last_update.isoformat()
            }
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.status = "error"
            self.logger.error(f"Task failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "metrics": self.metrics
        }
    
    def reset_metrics(self):
        """Reset agent metrics"""
        self.metrics = {
            "tasks_completed": 0,
            "errors": 0,
            "last_execution_time": 0
        }


# Import the new Mistral LLM service
try:
    from src.llm_service import MistralLLMService
    LLM_SERVICE_AVAILABLE = True
except ImportError:
    LLM_SERVICE_AVAILABLE = False


class MockLLMService:
    """Mock LLM service for development and testing"""
    
    def __init__(self):
        self.responses = {
            "esg_analysis": [
                "Based on current EU ESG standards and CSRD requirements, this indicates a strong commitment to sustainability.",
                "This aligns well with emerging EU regulatory requirements in the ESG space, particularly the EU Taxonomy.",
                "Consider implementing additional measures to enhance your ESG performance in line with ESRS standards.",
                "This practice is becoming increasingly important for stakeholder confidence and EU compliance."
            ],
            "regulation_update": [
                "Recent EU regulatory changes emphasize the importance of this area under CSRD.",
                "New compliance requirements have been introduced for this category under EU Taxonomy.",
                "Industry best practices are evolving in this direction following SFDR guidelines.",
                "This aligns with the latest European Sustainability Reporting Standards (ESRS)."
            ],
            "recommendation": [
                "I recommend developing a comprehensive policy for this area in line with CSRD requirements.",
                "Consider establishing measurable targets and regular monitoring as per EU Taxonomy criteria.",
                "Stakeholder engagement would strengthen this initiative and support SFDR compliance.",
                "Documentation and transparency are key for this practice under ESRS standards."
            ]
        }
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a mock LLM response"""
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Simple keyword-based response selection
        if "regulation" in prompt.lower() or "compliance" in prompt.lower():
            response_type = "regulation_update"
        elif "recommend" in prompt.lower() or "suggest" in prompt.lower():
            response_type = "recommendation"
        else:
            response_type = "esg_analysis"
        
        import random
        return random.choice(self.responses[response_type])
    
    async def analyze_esg_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ESG data and provide insights"""
        await asyncio.sleep(1)  # Simulate processing time
        
        # Mock analysis results with EU focus
        return {
            "overall_score": random.randint(65, 95),
            "category_scores": {
                "Environmental": random.randint(60, 90),
                "Social": random.randint(70, 95),
                "Governance": random.randint(65, 85)
            },
            "strengths": [
                "Strong environmental policies aligned with EU Green Deal",
                "Good stakeholder engagement practices per CSRD requirements",
                "Transparent reporting practices following ESRS standards"
            ],
            "improvements": [
                "Enhance carbon reduction targets to meet EU Taxonomy criteria",
                "Expand diversity initiatives in line with EU social standards",
                "Strengthen risk management for SFDR compliance"
            ],
            "compliance_status": "Good",
            "recommendations": [
                "Implement CSRD-compliant quarterly ESG reviews",
                "Establish ESG committee with EU regulatory oversight",
                "Enhance data collection processes for ESRS reporting",
                "Develop EU Taxonomy alignment strategy",
                "Prepare for SFDR disclosure requirements"
            ]
        }
    
    async def analyze_uploaded_document(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """Mock document analysis"""
        await asyncio.sleep(0.8)
        
        return {
            "document_type": document_type,
            "analysis": f"Analysis of {document_type} document reveals several ESG-related elements that align with EU regulatory requirements including CSRD and EU Taxonomy.",
            "extracted_metrics": [
                "Carbon emissions reduction targets (EU Taxonomy aligned)",
                "Employee diversity ratios (CSRD compliant)",
                "Board independence metrics (ESRS standards)"
            ],
            "compliance_notes": [
                "Document shows awareness of CSRD requirements",
                "Some alignment with EU Taxonomy criteria identified",
                "Governance structures meet ESRS basic standards"
            ],
            "recommendations": [
                "Enhance quantitative ESG metrics reporting for CSRD",
                "Improve alignment with ESRS standards",
                "Strengthen materiality assessment process per EU guidelines"
            ],
            "analysis_timestamp": datetime.now().isoformat()
        }


def get_llm_service():
    """Get the appropriate LLM service (Mistral or Mock)"""
    if LLM_SERVICE_AVAILABLE:
        try:
            return MistralLLMService()
        except Exception as e:
            logging.getLogger("llm_service").warning(f"Failed to initialize Mistral service: {e}, using mock")
            return MockLLMService()
    else:
        return MockLLMService()