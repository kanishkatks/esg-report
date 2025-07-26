"""
Knowledge Base Manager for dynamic ESG question updates and management
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from .base_agent import BaseAgent


class KnowledgeManager(BaseAgent):
    """Agent responsible for managing and updating the ESG knowledge base and questions"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="KnowledgeManager",
            description="Manages ESG knowledge base and dynamically updates question bank",
            config=config
        )
        self.question_bank = {}
        self.knowledge_base = {}
        self.question_weights = {}
        self.last_update = None
        self.version = "1.0.0"
    
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
        """Update the question bank with latest ESG requirements"""
        await asyncio.sleep(1.5)  # Simulate processing
        
        # Initialize comprehensive ESG question bank
        updated_questions = {
            "environmental": {
                "carbon_emissions": [
                    {
                        "id": "env_001",
                        "question": "Does your organization measure and report Scope 1 (direct) greenhouse gas emissions?",
                        "type": "yes_no",
                        "weight": 0.9,
                        "category": "Environmental",
                        "subcategory": "Carbon Emissions",
                        "regulation_refs": ["SEC_Climate_Disclosure", "EU_CSRD"],
                        "follow_up": {
                            "yes": "What methodology do you use for measuring Scope 1 emissions?",
                            "no": "What are the main barriers to implementing Scope 1 emissions measurement?"
                        }
                    },
                    {
                        "id": "env_002",
                        "question": "Does your organization measure and report Scope 2 (indirect energy) greenhouse gas emissions?",
                        "type": "yes_no",
                        "weight": 0.9,
                        "category": "Environmental",
                        "subcategory": "Carbon Emissions",
                        "regulation_refs": ["SEC_Climate_Disclosure", "EU_CSRD"],
                        "follow_up": {
                            "yes": "Do you use location-based or market-based accounting for Scope 2 emissions?",
                            "no": "What steps are you taking to begin Scope 2 emissions measurement?"
                        }
                    },
                    {
                        "id": "env_003",
                        "question": "Has your organization set science-based targets for carbon emission reduction?",
                        "type": "yes_no",
                        "weight": 0.8,
                        "category": "Environmental",
                        "subcategory": "Carbon Emissions",
                        "regulation_refs": ["UK_TCFD"],
                        "follow_up": {
                            "yes": "Are these targets validated by the Science Based Targets initiative (SBTi)?",
                            "no": "What is your timeline for establishing science-based targets?"
                        }
                    }
                ],
                "energy_management": [
                    {
                        "id": "env_004",
                        "question": "What percentage of your organization's energy consumption comes from renewable sources?",
                        "type": "percentage",
                        "weight": 0.7,
                        "category": "Environmental",
                        "subcategory": "Energy Management",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "high": "What renewable energy procurement strategies do you use?",
                            "low": "What are your plans for increasing renewable energy usage?"
                        }
                    },
                    {
                        "id": "env_005",
                        "question": "Does your organization have an energy efficiency improvement program?",
                        "type": "yes_no",
                        "weight": 0.6,
                        "category": "Environmental",
                        "subcategory": "Energy Management",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "yes": "What energy efficiency measures have you implemented?",
                            "no": "What barriers prevent implementation of energy efficiency programs?"
                        }
                    }
                ],
                "water_waste": [
                    {
                        "id": "env_006",
                        "question": "Does your organization monitor and report water consumption and quality impacts?",
                        "type": "yes_no",
                        "weight": 0.5,
                        "category": "Environmental",
                        "subcategory": "Water Usage",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "yes": "Do you have water reduction targets and strategies?",
                            "no": "Is water usage material to your business operations?"
                        }
                    },
                    {
                        "id": "env_007",
                        "question": "What percentage of your organization's waste is recycled or reused?",
                        "type": "percentage",
                        "weight": 0.6,
                        "category": "Environmental",
                        "subcategory": "Waste Management",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "high": "What circular economy principles does your organization follow?",
                            "low": "What are the main challenges in improving waste recycling rates?"
                        }
                    }
                ]
            },
            "social": {
                "employee_relations": [
                    {
                        "id": "soc_001",
                        "question": "Does your organization have a formal diversity, equity, and inclusion (DEI) policy?",
                        "type": "yes_no",
                        "weight": 0.8,
                        "category": "Social",
                        "subcategory": "Diversity & Inclusion",
                        "regulation_refs": ["SEC_Climate_Disclosure"],
                        "follow_up": {
                            "yes": "What specific DEI metrics do you track and report?",
                            "no": "What steps are you taking to develop a DEI policy?"
                        }
                    },
                    {
                        "id": "soc_002",
                        "question": "What is the gender diversity ratio in your organization's leadership positions?",
                        "type": "percentage",
                        "weight": 0.7,
                        "category": "Social",
                        "subcategory": "Diversity & Inclusion",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "high": "What programs support advancement of underrepresented groups?",
                            "low": "What initiatives are planned to improve leadership diversity?"
                        }
                    },
                    {
                        "id": "soc_003",
                        "question": "Does your organization provide comprehensive employee health and safety programs?",
                        "type": "yes_no",
                        "weight": 0.8,
                        "category": "Social",
                        "subcategory": "Employee Relations",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "yes": "What is your organization's injury/incident rate compared to industry average?",
                            "no": "What are the main challenges in implementing health and safety programs?"
                        }
                    }
                ],
                "community_impact": [
                    {
                        "id": "soc_004",
                        "question": "Does your organization have formal community engagement and investment programs?",
                        "type": "yes_no",
                        "weight": 0.6,
                        "category": "Social",
                        "subcategory": "Community Impact",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "yes": "How do you measure the impact of your community programs?",
                            "no": "What community needs has your organization identified as priorities?"
                        }
                    },
                    {
                        "id": "soc_005",
                        "question": "Does your organization ensure responsible supply chain practices?",
                        "type": "yes_no",
                        "weight": 0.7,
                        "category": "Social",
                        "subcategory": "Human Rights",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "yes": "What due diligence processes do you use for supply chain monitoring?",
                            "no": "What are the main challenges in implementing supply chain oversight?"
                        }
                    }
                ]
            },
            "governance": {
                "board_structure": [
                    {
                        "id": "gov_001",
                        "question": "What percentage of your board of directors consists of independent directors?",
                        "type": "percentage",
                        "weight": 0.8,
                        "category": "Governance",
                        "subcategory": "Board Structure",
                        "regulation_refs": ["SEC_Climate_Disclosure"],
                        "follow_up": {
                            "high": "How does the board oversee ESG risks and opportunities?",
                            "low": "What plans exist to increase board independence?"
                        }
                    },
                    {
                        "id": "gov_002",
                        "question": "Does your organization have a dedicated ESG or sustainability committee at the board level?",
                        "type": "yes_no",
                        "weight": 0.7,
                        "category": "Governance",
                        "subcategory": "Board Structure",
                        "regulation_refs": ["UK_TCFD"],
                        "follow_up": {
                            "yes": "How frequently does the ESG committee meet and report to the full board?",
                            "no": "How does the board currently oversee ESG matters?"
                        }
                    }
                ],
                "ethics_compliance": [
                    {
                        "id": "gov_003",
                        "question": "Does your organization have a comprehensive code of ethics and business conduct?",
                        "type": "yes_no",
                        "weight": 0.8,
                        "category": "Governance",
                        "subcategory": "Business Ethics",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "yes": "How do you ensure compliance with the code across all operations?",
                            "no": "What timeline exists for developing a comprehensive ethics code?"
                        }
                    },
                    {
                        "id": "gov_004",
                        "question": "Does your organization have robust data privacy and cybersecurity policies?",
                        "type": "yes_no",
                        "weight": 0.7,
                        "category": "Governance",
                        "subcategory": "Data Privacy",
                        "regulation_refs": ["EU_CSRD"],
                        "follow_up": {
                            "yes": "How do you assess and report on cybersecurity risks?",
                            "no": "What are the main challenges in implementing data privacy policies?"
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
            "regulation_coverage": self._get_regulation_coverage()
        }
    
    async def get_questions_for_assessment(self, industry: str, region: str, company_size: str) -> Dict[str, Any]:
        """Get tailored questions for specific assessment context"""
        await asyncio.sleep(0.8)
        
        # Filter and prioritize questions based on context
        tailored_questions = []
        
        for category_name, category in self.question_bank.items():
            for subcategory_name, questions in category.items():
                for question in questions:
                    # Apply contextual filtering
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
        
        # Sort by relevance and weight
        tailored_questions.sort(
            key=lambda q: (q["relevance_score"] * q["weight"]), 
            reverse=True
        )
        
        return {
            "questions": tailored_questions[:25],  # Limit to top 25 questions
            "total_available": len(tailored_questions),
            "industry": industry,
            "region": region,
            "company_size": company_size,
            "assessment_id": f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat()
        }
    
    async def add_knowledge_item(self, knowledge_item: Dict[str, Any]) -> Dict[str, Any]:
        """Add new knowledge item to the knowledge base"""
        await asyncio.sleep(0.3)
        
        item_id = knowledge_item.get("id", f"kb_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        self.knowledge_base[item_id] = {
            **knowledge_item,
            "added_date": datetime.now().isoformat(),
            "version": self.version
        }
        
        return {
            "item_id": item_id,
            "status": "added",
            "total_knowledge_items": len(self.knowledge_base)
        }
    
    async def refresh_question_weights(self) -> Dict[str, Any]:
        """Refresh question weights based on current regulations and trends"""
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
            "update_date": datetime.now().isoformat()
        }
    
    def _calculate_question_relevance(self, question: Dict[str, Any], industry: str, region: str, company_size: str) -> float:
        """Calculate question relevance based on context"""
        base_relevance = 0.7
        
        # Industry-specific adjustments
        if industry.lower() == "technology":
            if "data privacy" in question.get("subcategory", "").lower():
                base_relevance += 0.2
            if "carbon emissions" in question.get("subcategory", "").lower():
                base_relevance += 0.1
        elif industry.lower() == "manufacturing":
            if "waste management" in question.get("subcategory", "").lower():
                base_relevance += 0.2
            if "employee relations" in question.get("subcategory", "").lower():
                base_relevance += 0.15
        
        # Region-specific adjustments
        if region.upper() in ["EU", "EUROPE"]:
            if "EU_CSRD" in question.get("regulation_refs", []):
                base_relevance += 0.15
        elif region.upper() in ["US", "USA"]:
            if "SEC_Climate_Disclosure" in question.get("regulation_refs", []):
                base_relevance += 0.15
        
        # Company size adjustments
        if company_size.lower() == "large":
            base_relevance += 0.1
        elif company_size.lower() == "small":
            base_relevance -= 0.1
        
        return min(1.0, max(0.0, base_relevance))
    
    def _get_context_notes(self, question: Dict[str, Any], industry: str, region: str) -> List[str]:
        """Get context-specific notes for a question"""
        notes = []
        
        if industry.lower() == "technology" and "data privacy" in question.get("subcategory", "").lower():
            notes.append("Particularly important for technology companies due to data handling responsibilities")
        
        if region.upper() in ["EU", "EUROPE"] and "EU_CSRD" in question.get("regulation_refs", []):
            notes.append("Required under EU Corporate Sustainability Reporting Directive")
        
        if question.get("weight", 0) > 0.8:
            notes.append("High priority question for ESG assessment")
        
        return notes
    
    def _calculate_updated_weight(self, question: Dict[str, Any]) -> float:
        """Calculate updated weight based on current regulatory importance"""
        base_weight = question["weight"]
        
        # Increase weight for questions with recent regulatory references
        regulation_refs = question.get("regulation_refs", [])
        if "SEC_Climate_Disclosure" in regulation_refs:
            base_weight += 0.1
        if "EU_CSRD" in regulation_refs:
            base_weight += 0.1
        
        # Adjust based on question type importance
        if question.get("type") == "yes_no" and question.get("subcategory") in ["Carbon Emissions", "Board Structure"]:
            base_weight += 0.05
        
        return min(1.0, base_weight)
    
    def _get_regulation_coverage(self) -> Dict[str, int]:
        """Get coverage statistics for regulations"""
        coverage = {}
        
        for category in self.question_bank.values():
            for subcategory in category.values():
                for question in subcategory:
                    for reg_ref in question.get("regulation_refs", []):
                        coverage[reg_ref] = coverage.get(reg_ref, 0) + 1
        
        return coverage
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of knowledge base status"""
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
            "regulation_coverage": self._get_regulation_coverage()
        }