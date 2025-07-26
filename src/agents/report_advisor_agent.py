"""
Intelligent Report Advisor Agent
Provides interactive ESG advice, suggestions, and guidance based on current regulations
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from .base_agent import BaseAgent
from .enhanced_search_agent import EnhancedSearchAgent
from ..llm_service import MistralLLMService


class ReportAdvisorAgent(BaseAgent):
    """Intelligent agent that provides ESG advice, suggestions, and regulatory guidance"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="ReportAdvisorAgent",
            description="Provides intelligent ESG advice, regulatory guidance, and improvement suggestions",
            config=config
        )
        
        self.search_agent = EnhancedSearchAgent(config)
        self.llm_service = MistralLLMService()
        
        # ESG Advisory Knowledge Base
        self.advisory_knowledge = {
            "regulatory_priorities": {
                "2024": ["CSRD compliance", "EU Taxonomy alignment", "SFDR implementation"],
                "2025": ["Enhanced CSRD reporting", "Scope 3 emissions", "Nature-related disclosures"],
                "2026": ["ISSB standards adoption", "Climate transition plans", "Biodiversity reporting"]
            },
            "improvement_frameworks": {
                "environmental": {
                    "quick_wins": ["Energy efficiency audit", "Waste reduction program", "Digital sustainability"],
                    "medium_term": ["Renewable energy transition", "Scope 3 mapping", "Science-based targets"],
                    "long_term": ["Net-zero strategy", "Circular economy model", "Nature-positive goals"]
                },
                "social": {
                    "quick_wins": ["Diversity metrics tracking", "Employee wellbeing survey", "Community engagement"],
                    "medium_term": ["Inclusive hiring practices", "Skills development programs", "Supply chain standards"],
                    "long_term": ["Social impact measurement", "Stakeholder governance", "Human rights due diligence"]
                },
                "governance": {
                    "quick_wins": ["Board diversity assessment", "Ethics code update", "Risk register review"],
                    "medium_term": ["ESG oversight structure", "Executive compensation alignment", "Stakeholder engagement"],
                    "long_term": ["Integrated governance model", "Purpose-driven strategy", "Long-term value creation"]
                }
            },
            "regulatory_guidance": {
                "CSRD": {
                    "key_requirements": [
                        "Double materiality assessment",
                        "Value chain impact analysis",
                        "Forward-looking information",
                        "Third-party assurance"
                    ],
                    "preparation_steps": [
                        "Conduct materiality assessment",
                        "Map value chain impacts",
                        "Establish data collection systems",
                        "Engage with assurance providers"
                    ]
                },
                "EU_TAXONOMY": {
                    "key_requirements": [
                        "Economic activity screening",
                        "Technical screening criteria",
                        "Do No Significant Harm assessment",
                        "Minimum safeguards compliance"
                    ],
                    "preparation_steps": [
                        "Identify eligible activities",
                        "Assess alignment criteria",
                        "Document DNSH analysis",
                        "Implement safeguards"
                    ]
                }
            }
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute advisory task"""
        task_type = task.get("type", "general_advice")
        
        if task_type == "regulatory_advice":
            return await self.provide_regulatory_advice(task.get("regulation", ""), task.get("context", {}))
        elif task_type == "improvement_suggestions":
            return await self.suggest_improvements(task.get("knowledge_collected", {}), task.get("company_info", {}))
        elif task_type == "compliance_guidance":
            return await self.provide_compliance_guidance(task.get("regulation", ""), task.get("current_status", {}))
        elif task_type == "future_roadmap":
            return await self.create_future_roadmap(task.get("knowledge_collected", {}), task.get("company_info", {}))
        elif task_type == "interactive_consultation":
            return await self.interactive_consultation(task.get("question", ""), task.get("context", {}))
        else:
            return await self.general_esg_advice(task.get("query", ""), task.get("context", {}))
    
    async def provide_regulatory_advice(self, regulation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide specific regulatory advice and guidance"""
        
        # Get current regulatory information
        current_regs = await self.search_agent.get_current_regulations(regulation)
        
        # Generate contextual advice
        advice_prompt = f"""
        As an ESG regulatory expert, provide specific advice for {regulation} compliance.
        
        Current regulatory context: {json.dumps(current_regs.get('regulations', [])[:2], indent=2)}
        Company context: {json.dumps(context, indent=2)}
        
        Provide:
        1. Key compliance requirements
        2. Immediate action items
        3. Timeline considerations
        4. Common pitfalls to avoid
        5. Best practices recommendations
        
        Format as structured advice with clear action points.
        """
        
        try:
            advice_response = await self.llm_service.generate_response(advice_prompt)
            
            # Get regulatory guidance from knowledge base
            reg_guidance = self.advisory_knowledge.get("regulatory_guidance", {}).get(regulation.upper(), {})
            
            return {
                "regulation": regulation,
                "ai_advice": advice_response,
                "structured_guidance": reg_guidance,
                "current_requirements": current_regs.get('regulations', [])[:3],
                "priority_level": self._assess_regulatory_priority(regulation),
                "timeline": self._get_regulatory_timeline(regulation),
                "resources": self._get_regulatory_resources(regulation),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error providing regulatory advice: {e}")
            return {
                "regulation": regulation,
                "error": str(e),
                "fallback_guidance": reg_guidance,
                "generated_at": datetime.now().isoformat()
            }
    
    async def suggest_improvements(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest specific improvements based on collected data and current regulations"""
        
        # Analyze current performance
        performance_analysis = self._analyze_performance(knowledge_collected)
        
        # Get industry benchmarks
        industry = company_info.get("industry", "Technology")
        benchmarks = await self.search_agent.get_real_industry_benchmarks(industry)
        
        # Generate AI-powered suggestions
        suggestions_prompt = f"""
        As an ESG improvement consultant, analyze this company's performance and suggest specific improvements.
        
        Company: {company_info.get('name', 'Company')} ({industry})
        Performance Analysis: {json.dumps(performance_analysis, indent=2)}
        Industry Benchmarks: {json.dumps(benchmarks.get('benchmarks', {}), indent=2)}
        
        Provide specific, actionable improvement suggestions in these categories:
        1. Quick wins (0-3 months)
        2. Medium-term improvements (3-12 months)
        3. Long-term strategic initiatives (1-3 years)
        
        For each suggestion, include:
        - Specific action
        - Expected impact
        - Resource requirements
        - Regulatory alignment
        
        Focus on practical, measurable improvements.
        """
        
        try:
            ai_suggestions = await self.llm_service.generate_response(suggestions_prompt)
            
            # Get framework-based suggestions
            framework_suggestions = self._get_framework_suggestions(performance_analysis, company_info)
            
            return {
                "company": company_info.get('name', 'Company'),
                "industry": industry,
                "performance_analysis": performance_analysis,
                "ai_suggestions": ai_suggestions,
                "framework_suggestions": framework_suggestions,
                "industry_benchmarks": benchmarks.get('benchmarks', {}),
                "priority_matrix": self._create_priority_matrix(performance_analysis),
                "regulatory_alignment": self._assess_regulatory_alignment(knowledge_collected),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating improvement suggestions: {e}")
            return {
                "error": str(e),
                "fallback_suggestions": framework_suggestions,
                "generated_at": datetime.now().isoformat()
            }
    
    async def provide_compliance_guidance(self, regulation: str, current_status: Dict[str, Any]) -> Dict[str, Any]:
        """Provide step-by-step compliance guidance"""
        
        # Get current regulatory updates
        reg_updates = await self.search_agent.search_regulation_updates(regulation)
        
        # Generate compliance roadmap
        guidance_prompt = f"""
        As an ESG compliance expert, create a step-by-step compliance guide for {regulation}.
        
        Current Status: {json.dumps(current_status, indent=2)}
        Recent Updates: {json.dumps(reg_updates.get('updates', [])[:2], indent=2)}
        
        Provide:
        1. Compliance readiness assessment
        2. Step-by-step implementation guide
        3. Key milestones and deadlines
        4. Resource requirements
        5. Risk mitigation strategies
        
        Make it actionable and specific to the current status.
        """
        
        try:
            compliance_guide = await self.llm_service.generate_response(guidance_prompt)
            
            # Get structured guidance
            structured_guidance = self.advisory_knowledge.get("regulatory_guidance", {}).get(regulation.upper(), {})
            
            return {
                "regulation": regulation,
                "compliance_guide": compliance_guide,
                "structured_steps": structured_guidance.get("preparation_steps", []),
                "key_requirements": structured_guidance.get("key_requirements", []),
                "recent_updates": reg_updates.get('updates', [])[:3],
                "readiness_score": self._assess_compliance_readiness(current_status, regulation),
                "next_actions": self._get_next_compliance_actions(current_status, regulation),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error providing compliance guidance: {e}")
            return {
                "error": str(e),
                "fallback_guidance": structured_guidance,
                "generated_at": datetime.now().isoformat()
            }
    
    async def create_future_roadmap(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a future-focused ESG improvement roadmap"""
        
        # Get future regulatory priorities
        future_priorities = self.advisory_knowledge.get("regulatory_priorities", {})
        
        # Generate future roadmap
        roadmap_prompt = f"""
        As an ESG strategy consultant, create a 3-year ESG roadmap for this company.
        
        Company: {company_info.get('name', 'Company')} ({company_info.get('industry', 'Technology')})
        Current ESG Data: {json.dumps(knowledge_collected, indent=2)}
        Future Regulatory Priorities: {json.dumps(future_priorities, indent=2)}
        
        Create a roadmap with:
        1. 2024 priorities and actions
        2. 2025 strategic initiatives
        3. 2026 long-term goals
        4. Regulatory preparation timeline
        5. Investment requirements
        6. Success metrics
        
        Focus on future-proofing the ESG strategy.
        """
        
        try:
            future_roadmap = await self.llm_service.generate_response(roadmap_prompt)
            
            return {
                "company": company_info.get('name', 'Company'),
                "roadmap_period": "2024-2026",
                "ai_roadmap": future_roadmap,
                "regulatory_timeline": future_priorities,
                "strategic_themes": self._identify_strategic_themes(knowledge_collected, company_info),
                "investment_priorities": self._assess_investment_priorities(knowledge_collected),
                "success_metrics": self._define_success_metrics(knowledge_collected, company_info),
                "risk_considerations": self._identify_future_risks(company_info),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating future roadmap: {e}")
            return {
                "error": str(e),
                "fallback_roadmap": self._get_fallback_roadmap(company_info),
                "generated_at": datetime.now().isoformat()
            }
    
    async def interactive_consultation(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide interactive ESG consultation and advice"""
        
        # Get relevant regulatory information
        search_results = await self.search_agent.real_time_esg_search(question)
        
        # Generate contextual response
        consultation_prompt = f"""
        As an expert ESG consultant, answer this question with practical, actionable advice.
        
        Question: {question}
        Context: {json.dumps(context, indent=2)}
        Current Information: {json.dumps(search_results.get('results', [])[:2], indent=2)}
        
        Provide:
        1. Direct answer to the question
        2. Practical recommendations
        3. Regulatory considerations
        4. Implementation guidance
        5. Follow-up suggestions
        
        Be specific, actionable, and current with 2024 regulations.
        """
        
        try:
            consultation_response = await self.llm_service.generate_response(consultation_prompt)
            
            return {
                "question": question,
                "expert_response": consultation_response,
                "supporting_information": search_results.get('results', [])[:3],
                "regulatory_context": self._get_regulatory_context(question),
                "related_topics": self._suggest_related_topics(question),
                "follow_up_questions": self._generate_follow_up_questions(question, context),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in interactive consultation: {e}")
            return {
                "question": question,
                "error": str(e),
                "fallback_response": self._get_fallback_consultation(question),
                "generated_at": datetime.now().isoformat()
            }
    
    async def general_esg_advice(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general ESG advice and guidance"""
        
        # Search for relevant information
        search_results = await self.search_agent.real_time_esg_search(query)
        
        # Generate advice
        advice_prompt = f"""
        As an ESG expert, provide comprehensive advice on: {query}
        
        Context: {json.dumps(context, indent=2)}
        Current Information: {json.dumps(search_results.get('results', [])[:2], indent=2)}
        
        Provide practical, actionable advice with current regulatory context.
        """
        
        try:
            advice = await self.llm_service.generate_response(advice_prompt)
            
            return {
                "query": query,
                "advice": advice,
                "supporting_information": search_results.get('results', [])[:3],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _analyze_performance(self, knowledge_collected: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current ESG performance from collected data"""
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "data_gaps": [],
            "scores": {}
        }
        
        for category, data in knowledge_collected.items():
            if isinstance(data, dict):
                # Count available vs missing data
                total_fields = len(data)
                available_fields = sum(1 for v in data.values() if v and str(v).strip() not in ['', 'Not available', 'N/A'])
                
                completeness = (available_fields / total_fields * 100) if total_fields > 0 else 0
                analysis["scores"][category] = completeness
                
                if completeness > 80:
                    analysis["strengths"].append(f"Good data coverage in {category}")
                elif completeness < 50:
                    analysis["weaknesses"].append(f"Limited data in {category}")
                    analysis["data_gaps"].append(category)
        
        return analysis
    
    def _get_framework_suggestions(self, performance_analysis: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get framework-based improvement suggestions"""
        suggestions = {}
        
        for category in ["environmental", "social", "governance"]:
            if category in performance_analysis.get("data_gaps", []):
                suggestions[category] = self.advisory_knowledge["improvement_frameworks"][category]["quick_wins"]
            else:
                suggestions[category] = self.advisory_knowledge["improvement_frameworks"][category]["medium_term"]
        
        return suggestions
    
    def _assess_regulatory_priority(self, regulation: str) -> str:
        """Assess priority level of regulation"""
        high_priority = ["CSRD", "EU_TAXONOMY", "SFDR"]
        return "High" if regulation.upper() in high_priority else "Medium"
    
    def _get_regulatory_timeline(self, regulation: str) -> Dict[str, str]:
        """Get regulatory timeline information"""
        timelines = {
            "CSRD": {"deadline": "2025", "preparation_time": "12-18 months"},
            "EU_TAXONOMY": {"deadline": "Ongoing", "preparation_time": "6-12 months"},
            "SFDR": {"deadline": "Ongoing", "preparation_time": "3-6 months"}
        }
        return timelines.get(regulation.upper(), {"deadline": "TBD", "preparation_time": "6-12 months"})
    
    def _get_regulatory_resources(self, regulation: str) -> List[str]:
        """Get regulatory resources and guidance"""
        resources = {
            "CSRD": ["EFRAG guidance documents", "EU Commission Q&A", "Industry implementation guides"],
            "EU_TAXONOMY": ["EU Platform guidance", "Technical screening criteria", "DNSH guidance"],
            "SFDR": ["ESMA guidelines", "RTS documentation", "Industry best practices"]
        }
        return resources.get(regulation.upper(), ["Official regulatory guidance", "Industry associations", "Professional advisors"])
    
    def _create_priority_matrix(self, performance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create improvement priority matrix"""
        return {
            "high_impact_low_effort": ["Data collection systems", "Policy updates"],
            "high_impact_high_effort": ["Science-based targets", "Supply chain engagement"],
            "low_impact_low_effort": ["Reporting templates", "Training programs"],
            "low_impact_high_effort": ["Full lifecycle assessments", "Comprehensive audits"]
        }
    
    def _assess_regulatory_alignment(self, knowledge_collected: Dict[str, Any]) -> Dict[str, str]:
        """Assess alignment with current regulations"""
        alignment = {}
        
        # Check for key regulatory indicators
        if knowledge_collected.get("reporting_compliance", {}).get("csrd_readiness"):
            alignment["CSRD"] = "In Progress"
        else:
            alignment["CSRD"] = "Not Started"
        
        if knowledge_collected.get("environmental", {}).get("taxonomy_alignment"):
            alignment["EU_Taxonomy"] = "Assessment Conducted"
        else:
            alignment["EU_Taxonomy"] = "Assessment Required"
        
        return alignment
    
    def _assess_compliance_readiness(self, current_status: Dict[str, Any], regulation: str) -> int:
        """Assess compliance readiness score (0-100)"""
        # Simple scoring based on available data
        if not current_status:
            return 20
        
        score = 40  # Base score
        
        # Add points for various readiness indicators
        if current_status.get("data_collection_system"):
            score += 20
        if current_status.get("governance_structure"):
            score += 20
        if current_status.get("reporting_process"):
            score += 20
        
        return min(score, 100)
    
    def _get_next_compliance_actions(self, current_status: Dict[str, Any], regulation: str) -> List[str]:
        """Get next compliance actions"""
        actions = []
        
        if not current_status.get("data_collection_system"):
            actions.append("Establish data collection systems")
        if not current_status.get("governance_structure"):
            actions.append("Set up ESG governance structure")
        if not current_status.get("reporting_process"):
            actions.append("Develop reporting processes")
        
        return actions[:3]  # Top 3 actions
    
    def _identify_strategic_themes(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> List[str]:
        """Identify strategic themes for roadmap"""
        themes = ["Regulatory Compliance", "Data & Reporting Excellence"]
        
        industry = company_info.get("industry", "").lower()
        if "tech" in industry:
            themes.extend(["Digital Sustainability", "Responsible AI"])
        elif "manufacturing" in industry:
            themes.extend(["Circular Economy", "Supply Chain Sustainability"])
        elif "financial" in industry:
            themes.extend(["Sustainable Finance", "Climate Risk Management"])
        
        return themes
    
    def _assess_investment_priorities(self, knowledge_collected: Dict[str, Any]) -> Dict[str, str]:
        """Assess investment priorities"""
        return {
            "Technology & Systems": "High - Data collection and reporting systems",
            "Human Resources": "Medium - ESG expertise and training",
            "External Support": "Medium - Consultants and assurance providers",
            "Operational Changes": "High - Process improvements and controls"
        }
    
    def _define_success_metrics(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> List[str]:
        """Define success metrics for roadmap"""
        return [
            "Regulatory compliance achievement",
            "ESG data quality and completeness",
            "Stakeholder engagement scores",
            "ESG performance improvements",
            "Cost efficiency of ESG programs"
        ]
    
    def _identify_future_risks(self, company_info: Dict[str, Any]) -> List[str]:
        """Identify future ESG risks"""
        return [
            "Evolving regulatory requirements",
            "Increased stakeholder expectations",
            "Climate-related physical risks",
            "Supply chain disruptions",
            "Technology and data security risks"
        ]
    
    def _get_fallback_roadmap(self, company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback roadmap when AI fails"""
        return {
            "2024": ["Establish ESG governance", "Implement data collection", "Begin CSRD preparation"],
            "2025": ["Achieve regulatory compliance", "Enhance reporting quality", "Expand stakeholder engagement"],
            "2026": ["Optimize ESG performance", "Lead industry practices", "Integrate sustainability strategy"]
        }
    
    def _get_regulatory_context(self, question: str) -> List[str]:
        """Get regulatory context for question"""
        context = []
        question_lower = question.lower()
        
        if any(term in question_lower for term in ["csrd", "reporting", "disclosure"]):
            context.append("CSRD - Corporate Sustainability Reporting Directive")
        if any(term in question_lower for term in ["taxonomy", "sustainable", "green"]):
            context.append("EU Taxonomy - Sustainable Activities Classification")
        if any(term in question_lower for term in ["climate", "carbon", "emissions"]):
            context.append("Climate regulations and carbon reporting requirements")
        
        return context
    
    def _suggest_related_topics(self, question: str) -> List[str]:
        """Suggest related topics"""
        return [
            "Regulatory compliance strategies",
            "ESG data management",
            "Stakeholder engagement",
            "Industry best practices",
            "Future regulatory trends"
        ]
    
    def _generate_follow_up_questions(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate follow-up questions"""
        return [
            "What are the specific implementation steps?",
            "What resources will be required?",
            "How does this align with current regulations?",
            "What are the potential risks and mitigation strategies?",
            "How can we measure success?"
        ]
    
    def _get_fallback_consultation(self, question: str) -> str:
        """Get fallback consultation response"""
        return f"I understand you're asking about {question}. This is an important ESG topic that requires careful consideration of current regulations and best practices. I recommend consulting with ESG experts and reviewing the latest regulatory guidance for specific implementation advice."