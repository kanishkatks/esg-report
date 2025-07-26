"""
EU-focused Knowledge Base Manager for ESG questions based on current EU directives
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from .base_agent import BaseAgent


class EUKnowledgeManager(BaseAgent):
    """Agent responsible for managing EU directive-based ESG questions and knowledge"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="EUKnowledgeManager",
            description="Manages ESG knowledge base with focus on EU directives (CSRD, EU Taxonomy, SFDR)",
            config=config
        )
        self.question_bank = {}
        self.knowledge_base = {}
        self.question_weights = {}
        self.last_update = None
        self.version = "2.0.0-EU"
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute knowledge management task"""
        task_type = task.get("type", "update_questions")
        
        if task_type == "update_questions":
            return await self.update_question_bank()
        elif task_type == "get_questions":
            return await self.get_questions_for_assessment(
                task.get("industry", ""), 
                task.get("region", ""),
                task.get("company_size", "")
            )
        elif task_type == "add_knowledge":
            return await self.add_knowledge_item(task.get("knowledge_item", {}))
        elif task_type == "refresh_weights":
            return await self.refresh_question_weights()
        else:
            return await self.update_question_bank()
    
    async def update_question_bank(self) -> Dict[str, Any]:
        """Update the question bank with latest EU directive-based ESG requirements"""
        await asyncio.sleep(1.5)  # Simulate processing
        
        # Initialize comprehensive EU-focused ESG question bank
        updated_questions = {
            "environmental": {
                "climate_change": [
                    {
                        "id": "env_001",
                        "question": "Does your organization measure and report Scope 1, 2, and 3 greenhouse gas emissions in accordance with CSRD requirements?",
                        "type": "yes_no",
                        "weight": 1.0,
                        "category": "Environmental",
                        "subcategory": "Climate Change",
                        "regulation_refs": ["EU_CSRD", "ESRS_E1"],
                        "eu_directive": "CSRD - ESRS E1 Climate Change",
                        "follow_up": {
                            "yes": "Do you use the GHG Protocol methodology and have third-party verification?",
                            "no": "What is your timeline for implementing comprehensive GHG emissions measurement per CSRD?"
                        }
                    },
                    {
                        "id": "env_002",
                        "question": "Has your organization conducted a climate-related scenario analysis as required by CSRD?",
                        "type": "yes_no",
                        "weight": 0.9,
                        "category": "Environmental",
                        "subcategory": "Climate Change",
                        "regulation_refs": ["EU_CSRD", "ESRS_E1"],
                        "eu_directive": "CSRD - ESRS E1 Climate Change",
                        "follow_up": {
                            "yes": "Which climate scenarios did you use (e.g., NGFS, IEA) and what time horizons?",
                            "no": "What are the main challenges in conducting climate scenario analysis?"
                        }
                    },
                    {
                        "id": "env_003",
                        "question": "What percentage of your organization's activities are aligned with the EU Taxonomy for sustainable activities?",
                        "type": "percentage",
                        "weight": 1.0,
                        "category": "Environmental",
                        "subcategory": "Climate Change",
                        "regulation_refs": ["EU_Taxonomy", "SFDR"],
                        "eu_directive": "EU Taxonomy Regulation",
                        "follow_up": {
                            "high": "Which EU Taxonomy objectives do your activities contribute to most?",
                            "low": "What steps are you taking to increase EU Taxonomy alignment?"
                        }
                    },
                    {
                        "id": "env_004",
                        "question": "Does your organization have science-based targets validated by SBTi and aligned with 1.5°C pathway?",
                        "type": "yes_no",
                        "weight": 0.8,
                        "category": "Environmental",
                        "subcategory": "Climate Change",
                        "regulation_refs": ["EU_CSRD", "ESRS_E1"],
                        "eu_directive": "CSRD - ESRS E1 Climate Change",
                        "follow_up": {
                            "yes": "What is your target year for net-zero emissions and interim milestones?",
                            "no": "What is preventing your organization from setting science-based targets?"
                        }
                    }
                ],
                "circular_economy": [
                    {
                        "id": "env_005",
                        "question": "Does your organization implement circular economy principles in line with EU Circular Economy Action Plan?",
                        "type": "yes_no",
                        "weight": 0.8,
                        "category": "Environmental",
                        "subcategory": "Circular Economy",
                        "regulation_refs": ["EU_CSRD", "ESRS_E5"],
                        "eu_directive": "CSRD - ESRS E5 Resource Use and Circular Economy",
                        "follow_up": {
                            "yes": "What specific circular economy practices have you implemented?",
                            "no": "What are the main barriers to implementing circular economy principles?"
                        }
                    },
                    {
                        "id": "env_006",
                        "question": "What percentage of your organization's waste is recycled, reused, or recovered?",
                        "type": "percentage",
                        "weight": 0.7,
                        "category": "Environmental",
                        "subcategory": "Circular Economy",
                        "regulation_refs": ["EU_CSRD", "ESRS_E5"],
                        "eu_directive": "CSRD - ESRS E5 Resource Use and Circular Economy",
                        "follow_up": {
                            "high": "How do you track and verify your waste management data?",
                            "low": "What initiatives are planned to improve waste management?"
                        }
                    }
                ],
                "biodiversity": [
                    {
                        "id": "env_007",
                        "question": "Has your organization conducted a biodiversity impact assessment as required by CSRD?",
                        "type": "yes_no",
                        "weight": 0.7,
                        "category": "Environmental",
                        "subcategory": "Biodiversity",
                        "regulation_refs": ["EU_CSRD", "ESRS_E4"],
                        "eu_directive": "CSRD - ESRS E4 Biodiversity and Ecosystems",
                        "follow_up": {
                            "yes": "What methodology did you use for the biodiversity assessment?",
                            "no": "Do you operate in or near biodiversity-sensitive areas?"
                        }
                    }
                ]
            },
            "social": {
                "workforce": [
                    {
                        "id": "soc_001",
                        "question": "Does your organization have a comprehensive diversity, equity, and inclusion policy compliant with EU standards?",
                        "type": "yes_no",
                        "weight": 0.9,
                        "category": "Social",
                        "subcategory": "Workforce",
                        "regulation_refs": ["EU_CSRD", "ESRS_S1"],
                        "eu_directive": "CSRD - ESRS S1 Own Workforce",
                        "follow_up": {
                            "yes": "What specific DEI metrics do you track and report publicly?",
                            "no": "What steps are you taking to develop a comprehensive DEI policy?"
                        }
                    },
                    {
                        "id": "soc_002",
                        "question": "What is the gender pay gap in your organization across all levels?",
                        "type": "percentage",
                        "weight": 0.8,
                        "category": "Social",
                        "subcategory": "Workforce",
                        "regulation_refs": ["EU_Pay_Transparency", "ESRS_S1"],
                        "eu_directive": "EU Pay Transparency Directive",
                        "follow_up": {
                            "high": "What measures are you implementing to address the gender pay gap?",
                            "low": "How do you ensure pay equity across your organization?"
                        }
                    },
                    {
                        "id": "soc_003",
                        "question": "Does your organization provide comprehensive health and safety programs meeting EU standards?",
                        "type": "yes_no",
                        "weight": 0.8,
                        "category": "Social",
                        "subcategory": "Workforce",
                        "regulation_refs": ["EU_CSRD", "ESRS_S1"],
                        "eu_directive": "CSRD - ESRS S1 Own Workforce",
                        "follow_up": {
                            "yes": "What is your organization's injury/incident rate compared to industry average?",
                            "no": "What are the main challenges in implementing comprehensive health and safety programs?"
                        }
                    }
                ],
                "value_chain": [
                    {
                        "id": "soc_004",
                        "question": "Does your organization conduct human rights due diligence throughout its value chain as required by CSRD?",
                        "type": "yes_no",
                        "weight": 0.9,
                        "category": "Social",
                        "subcategory": "Value Chain",
                        "regulation_refs": ["EU_CSRD", "ESRS_S2", "EU_CSDDD"],
                        "eu_directive": "CSRD - ESRS S2 Workers in Value Chain & Corporate Sustainability Due Diligence Directive",
                        "follow_up": {
                            "yes": "What methodology do you use for human rights due diligence?",
                            "no": "What are the main challenges in implementing value chain due diligence?"
                        }
                    },
                    {
                        "id": "soc_005",
                        "question": "Does your organization have grievance mechanisms accessible to affected communities?",
                        "type": "yes_no",
                        "weight": 0.7,
                        "category": "Social",
                        "subcategory": "Value Chain",
                        "regulation_refs": ["EU_CSRD", "ESRS_S3"],
                        "eu_directive": "CSRD - ESRS S3 Affected Communities",
                        "follow_up": {
                            "yes": "How many grievances were received and resolved in the last year?",
                            "no": "What plans do you have to establish grievance mechanisms?"
                        }
                    }
                ]
            },
            "governance": {
                "business_conduct": [
                    {
                        "id": "gov_001",
                        "question": "Does your organization have a comprehensive anti-corruption and bribery policy compliant with EU standards?",
                        "type": "yes_no",
                        "weight": 0.9,
                        "category": "Governance",
                        "subcategory": "Business Conduct",
                        "regulation_refs": ["EU_CSRD", "ESRS_G1"],
                        "eu_directive": "CSRD - ESRS G1 Business Conduct",
                        "follow_up": {
                            "yes": "How do you monitor and ensure compliance across all operations?",
                            "no": "What timeline exists for developing a comprehensive anti-corruption policy?"
                        }
                    },
                    {
                        "id": "gov_002",
                        "question": "Does your organization have robust data protection and privacy policies compliant with GDPR?",
                        "type": "yes_no",
                        "weight": 0.8,
                        "category": "Governance",
                        "subcategory": "Business Conduct",
                        "regulation_refs": ["GDPR", "ESRS_G1"],
                        "eu_directive": "General Data Protection Regulation (GDPR)",
                        "follow_up": {
                            "yes": "How do you assess and report on data protection risks?",
                            "no": "What are the main challenges in achieving GDPR compliance?"
                        }
                    }
                ],
                "management_supervision": [
                    {
                        "id": "gov_003",
                        "question": "What percentage of your board of directors consists of independent directors?",
                        "type": "percentage",
                        "weight": 0.8,
                        "category": "Governance",
                        "subcategory": "Management and Supervision",
                        "regulation_refs": ["EU_CSRD", "EU_Corporate_Governance"],
                        "eu_directive": "EU Corporate Governance Framework",
                        "follow_up": {
                            "high": "How does the board oversee ESG risks and opportunities?",
                            "low": "What plans exist to increase board independence?"
                        }
                    },
                    {
                        "id": "gov_004",
                        "question": "Does your organization have a dedicated sustainability committee at the board level?",
                        "type": "yes_no",
                        "weight": 0.7,
                        "category": "Governance",
                        "subcategory": "Management and Supervision",
                        "regulation_refs": ["EU_CSRD"],
                        "eu_directive": "CSRD - Governance Requirements",
                        "follow_up": {
                            "yes": "How frequently does the sustainability committee meet and report to the full board?",
                            "no": "How does the board currently oversee sustainability matters?"
                        }
                    }
                ]
            }
        }
        
        # Update internal question bank
        self.question_bank = updated_questions
        self.last_update = datetime.now()
        
        # Calculate total questions
        total_questions = sum(
            len(subcategory_questions)
            for category in updated_questions.values()
            for subcategory_questions in category.values()
        )
        
        return {
            "questions_updated": total_questions,
            "categories": list(updated_questions.keys()),
            "version": self.version,
            "last_update": self.last_update.isoformat(),
            "eu_directive_coverage": self._get_eu_directive_coverage()
        }
    
    async def get_questions_for_assessment(self, industry: str, region: str, company_size: str) -> Dict[str, Any]:
        """Get tailored questions for specific assessment context with EU focus"""
        await asyncio.sleep(0.8)
        
        # Filter and prioritize questions based on context
        tailored_questions = []
        
        for category_name, category in self.question_bank.items():
            for subcategory_name, questions in category.items():
                for question in questions:
                    # Apply contextual filtering with EU focus
                    relevance_score = self._calculate_question_relevance(
                        question, industry, region, company_size
                    )
                    
                    if relevance_score > 0.3:  # Threshold for inclusion
                        question_copy = question.copy()
                        question_copy["relevance_score"] = relevance_score
                        question_copy["context_notes"] = self._get_context_notes(
                            question, industry, region
                        )
                        tailored_questions.append(question_copy)
        
        # Sort by relevance and weight, prioritizing EU-specific questions
        tailored_questions.sort(
            key=lambda q: (q["relevance_score"] * q["weight"] * (1.2 if "EU" in str(q.get("regulation_refs", [])) else 1.0)), 
            reverse=True
        )
        
        return {
            "questions": tailored_questions[:25],  # Limit to top 25 questions
            "total_available": len(tailored_questions),
            "industry": industry,
            "region": region,
            "company_size": company_size,
            "assessment_id": f"eu_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "eu_focus": True
        }
    
    def _calculate_question_relevance(self, question: Dict[str, Any], industry: str, region: str, company_size: str) -> float:
        """Calculate question relevance based on context with EU emphasis"""
        base_relevance = 0.7
        
        # EU region gets higher relevance for EU-specific questions
        if region.upper() in ["EU", "EUROPE", "EUROPEAN UNION"]:
            if any("EU" in ref for ref in question.get("regulation_refs", [])):
                base_relevance += 0.3
            if question.get("eu_directive"):
                base_relevance += 0.2
        
        # Industry-specific adjustments
        if industry.lower() == "technology":
            if "data protection" in question.get("question", "").lower() or "gdpr" in question.get("question", "").lower():
                base_relevance += 0.2
            if "circular economy" in question.get("subcategory", "").lower():
                base_relevance += 0.1
        elif industry.lower() == "manufacturing":
            if "circular economy" in question.get("subcategory", "").lower():
                base_relevance += 0.2
            if "biodiversity" in question.get("subcategory", "").lower():
                base_relevance += 0.15
        elif industry.lower() == "financial":
            if "SFDR" in question.get("regulation_refs", []):
                base_relevance += 0.25
            if "EU_Taxonomy" in question.get("regulation_refs", []):
                base_relevance += 0.2
        
        # Company size adjustments
        if company_size.lower() == "large":
            base_relevance += 0.1
        elif company_size.lower() == "small":
            # Small companies may have different CSRD timelines
            if "CSRD" in question.get("regulation_refs", []):
                base_relevance -= 0.1
        
        return min(1.0, max(0.0, base_relevance))
    
    def _get_context_notes(self, question: Dict[str, Any], industry: str, region: str) -> List[str]:
        """Get context-specific notes for a question with EU focus"""
        notes = []
        
        if question.get("eu_directive"):
            notes.append(f"Required under {question['eu_directive']}")
        
        if region.upper() in ["EU", "EUROPE"] and "CSRD" in question.get("regulation_refs", []):
            notes.append("Mandatory for EU companies under Corporate Sustainability Reporting Directive")
        
        if "EU_Taxonomy" in question.get("regulation_refs", []):
            notes.append("Important for EU Taxonomy alignment and sustainable finance")
        
        if question.get("weight", 0) > 0.8:
            notes.append("High priority question for EU ESG compliance")
        
        return notes
    
    def _get_eu_directive_coverage(self) -> Dict[str, int]:
        """Get coverage statistics for EU directives"""
        coverage = {}
        
        for category in self.question_bank.values():
            for subcategory in category.values():
                for question in subcategory:
                    for reg_ref in question.get("regulation_refs", []):
                        if "EU" in reg_ref or "ESRS" in reg_ref or "CSRD" in reg_ref:
                            coverage[reg_ref] = coverage.get(reg_ref, 0) + 1
                    
                    # Also count EU directives
                    eu_directive = question.get("eu_directive")
                    if eu_directive:
                        coverage[eu_directive] = coverage.get(eu_directive, 0) + 1
        
        return coverage
    
    async def add_knowledge_item(self, knowledge_item: Dict[str, Any]) -> Dict[str, Any]:
        """Add new knowledge item to the knowledge base"""
        await asyncio.sleep(0.3)
        
        item_id = knowledge_item.get("id", f"eu_kb_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        self.knowledge_base[item_id] = {
            **knowledge_item,
            "added_date": datetime.now().isoformat(),
            "version": self.version,
            "eu_focused": True
        }
        
        return {
            "item_id": item_id,
            "status": "added",
            "total_knowledge_items": len(self.knowledge_base)
        }
    
    async def refresh_question_weights(self) -> Dict[str, Any]:
        """Refresh question weights based on current EU regulations and trends"""
        await asyncio.sleep(1)
        
        updated_weights = 0
        
        for category in self.question_bank.values():
            for subcategory in category.values():
                for question in subcategory:
                    old_weight = question["weight"]
                    new_weight = self._calculate_updated_weight(question)
                    
                    if abs(old_weight - new_weight) > 0.1:
                        question["weight"] = new_weight
                        updated_weights += 1
        
        return {
            "weights_updated": updated_weights,
            "total_questions": sum(
                len(subcategory)
                for category in self.question_bank.values()
                for subcategory in category.values()
            ),
            "update_date": datetime.now().isoformat(),
            "eu_focus": True
        }
    
    def _calculate_updated_weight(self, question: Dict[str, Any]) -> float:
        """Calculate updated weight based on current EU regulatory importance"""
        base_weight = question["weight"]
        
        # Increase weight for EU-specific regulations
        regulation_refs = question.get("regulation_refs", [])
        if "EU_CSRD" in regulation_refs:
            base_weight += 0.15
        if "EU_Taxonomy" in regulation_refs:
            base_weight += 0.1
        if "SFDR" in regulation_refs:
            base_weight += 0.1
        
        # Adjust based on question type importance for EU compliance
        if question.get("type") == "yes_no" and question.get("subcategory") in ["Climate Change", "Business Conduct"]:
            base_weight += 0.05
        
        return min(1.0, base_weight)
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of EU-focused knowledge base status"""
        total_questions = sum(
            len(subcategory)
            for category in self.question_bank.values()
            for subcategory in category.values()
        )
        
        return {
            "total_questions": total_questions,
            "categories": len(self.question_bank),
            "knowledge_items": len(self.knowledge_base),
            "version": self.version,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "eu_directive_coverage": self._get_eu_directive_coverage(),
            "eu_focused": True
        }