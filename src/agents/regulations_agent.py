"""
Regulations Updater Agent for maintaining current ESG compliance requirements
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from .base_agent import BaseAgent


class RegulationsAgent(BaseAgent):
    """Agent responsible for tracking and updating ESG regulations and compliance requirements"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="RegulationsAgent",
            description="Monitors and updates ESG regulations and compliance requirements",
            config=config
        )
        self.regulations_db = {}
        self.compliance_frameworks = {}
        self.update_schedule = {}
        self.last_full_update = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute regulations update task"""
        task_type = task.get("type", "update_regulations")
        
        if task_type == "update_regulations":
            return await self.update_regulations()
        elif task_type == "check_compliance":
            return await self.check_compliance_status(task.get("company_data", {}))
        elif task_type == "get_applicable_regulations":
            return await self.get_applicable_regulations(
                task.get("industry", ""), 
                task.get("region", "")
            )
        elif task_type == "track_changes":
            return await self.track_regulation_changes()
        else:
            return await self.update_regulations()
    
    async def update_regulations(self) -> Dict[str, Any]:
        """Update the regulations database with latest information"""
        await asyncio.sleep(2)  # Simulate API calls and processing
        
        # Mock regulation updates
        updated_regulations = {
            "SEC_Climate_Disclosure": {
                "name": "SEC Climate-Related Disclosures",
                "jurisdiction": "United States",
                "status": "Proposed",
                "effective_date": "2024-12-31",
                "last_updated": datetime.now().isoformat(),
                "requirements": [
                    "Scope 1 and 2 GHG emissions disclosure",
                    "Climate-related risks and opportunities",
                    "Governance and risk management processes",
                    "Climate-related targets and goals"
                ],
                "applicability": {
                    "company_types": ["Public companies", "Large accelerated filers"],
                    "industries": ["All"],
                    "minimum_size": "Large accelerated filer status"
                },
                "penalties": {
                    "non_compliance": "SEC enforcement action",
                    "false_reporting": "Civil and criminal penalties"
                }
            },
            "EU_CSRD": {
                "name": "Corporate Sustainability Reporting Directive",
                "jurisdiction": "European Union",
                "status": "Active",
                "effective_date": "2024-01-01",
                "last_updated": datetime.now().isoformat(),
                "requirements": [
                    "Double materiality assessment",
                    "Sustainability reporting standards compliance",
                    "Third-party assurance",
                    "Digital reporting format"
                ],
                "applicability": {
                    "company_types": ["Large companies", "Listed SMEs"],
                    "industries": ["All"],
                    "minimum_size": "500+ employees or €40M+ revenue"
                },
                "penalties": {
                    "non_compliance": "Member state penalties",
                    "false_reporting": "Administrative fines up to 5% of revenue"
                }
            },
            "UK_TCFD": {
                "name": "TCFD-aligned Disclosures",
                "jurisdiction": "United Kingdom",
                "status": "Active",
                "effective_date": "2022-01-01",
                "last_updated": datetime.now().isoformat(),
                "requirements": [
                    "Climate governance disclosure",
                    "Strategy and risk management",
                    "Metrics and targets",
                    "Scenario analysis"
                ],
                "applicability": {
                    "company_types": ["Premium listed companies", "Large private companies"],
                    "industries": ["All"],
                    "minimum_size": "500+ employees"
                },
                "penalties": {
                    "non_compliance": "FCA enforcement",
                    "false_reporting": "Unlimited fines"
                }
            }
        }
        
        # Update internal database
        self.regulations_db.update(updated_regulations)
        self.last_full_update = datetime.now()
        
        # Track changes
        changes_detected = await self._detect_changes(updated_regulations)
        
        return {
            "updated_regulations": len(updated_regulations),
            "total_regulations": len(self.regulations_db),
            "changes_detected": changes_detected,
            "last_update": self.last_full_update.isoformat(),
            "next_update": (self.last_full_update + timedelta(hours=24)).isoformat()
        }
    
    async def check_compliance_status(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check company's compliance status against current regulations"""
        await asyncio.sleep(1)  # Simulate analysis
        
        industry = company_data.get("industry", "technology")
        region = company_data.get("region", "US")
        company_size = company_data.get("size", "large")
        
        applicable_regs = await self.get_applicable_regulations(industry, region)
        
        compliance_status = {}
        overall_score = 0
        total_regs = len(applicable_regs.get("regulations", []))
        
        for reg_id, regulation in applicable_regs.get("regulations", {}).items():
            # Mock compliance assessment
            compliance_score = self._assess_regulation_compliance(regulation, company_data)
            compliance_status[reg_id] = {
                "regulation_name": regulation["name"],
                "compliance_score": compliance_score,
                "status": "Compliant" if compliance_score >= 80 else "Non-compliant" if compliance_score < 60 else "Partial",
                "required_actions": self._get_required_actions(regulation, compliance_score),
                "deadline": regulation.get("effective_date", ""),
                "risk_level": "High" if compliance_score < 60 else "Medium" if compliance_score < 80 else "Low"
            }
            overall_score += compliance_score
        
        overall_score = overall_score / total_regs if total_regs > 0 else 0
        
        return {
            "overall_compliance_score": round(overall_score, 2),
            "total_regulations": total_regs,
            "compliant_count": sum(1 for status in compliance_status.values() if status["compliance_score"] >= 80),
            "non_compliant_count": sum(1 for status in compliance_status.values() if status["compliance_score"] < 60),
            "partial_compliance_count": sum(1 for status in compliance_status.values() if 60 <= status["compliance_score"] < 80),
            "detailed_status": compliance_status,
            "assessment_date": datetime.now().isoformat(),
            "high_risk_regulations": [
                reg_id for reg_id, status in compliance_status.items() 
                if status["risk_level"] == "High"
            ]
        }
    
    async def get_applicable_regulations(self, industry: str, region: str) -> Dict[str, Any]:
        """Get regulations applicable to specific industry and region"""
        await asyncio.sleep(0.5)
        
        applicable_regs = {}
        
        for reg_id, regulation in self.regulations_db.items():
            # Check jurisdiction match
            if region.upper() in regulation["jurisdiction"].upper() or regulation["jurisdiction"] == "Global":
                # Check industry applicability
                if "All" in regulation["applicability"]["industries"] or industry.lower() in [ind.lower() for ind in regulation["applicability"]["industries"]]:
                    applicable_regs[reg_id] = regulation
        
        return {
            "regulations": applicable_regs,
            "industry": industry,
            "region": region,
            "total_applicable": len(applicable_regs),
            "query_date": datetime.now().isoformat()
        }
    
    async def track_regulation_changes(self) -> Dict[str, Any]:
        """Track changes in regulations over time"""
        await asyncio.sleep(0.8)
        
        # Mock change tracking
        recent_changes = [
            {
                "regulation_id": "SEC_Climate_Disclosure",
                "change_type": "Amendment",
                "change_date": "2024-01-15",
                "description": "Updated Scope 3 emissions disclosure requirements",
                "impact": "Medium",
                "affected_companies": "Large accelerated filers"
            },
            {
                "regulation_id": "EU_CSRD",
                "change_type": "Implementation Guidance",
                "change_date": "2024-01-10",
                "description": "New ESRS implementation guidelines published",
                "impact": "High",
                "affected_companies": "All EU companies subject to CSRD"
            },
            {
                "regulation_id": "UK_TCFD",
                "change_type": "Enforcement Update",
                "change_date": "2024-01-05",
                "description": "FCA published new enforcement priorities",
                "impact": "Low",
                "affected_companies": "UK listed companies"
            }
        ]
        
        return {
            "recent_changes": recent_changes,
            "total_changes": len(recent_changes),
            "tracking_period": "Last 30 days",
            "last_tracked": datetime.now().isoformat()
        }
    
    def _assess_regulation_compliance(self, regulation: Dict[str, Any], company_data: Dict[str, Any]) -> float:
        """Assess company's compliance with a specific regulation"""
        # Mock compliance scoring based on available data
        base_score = 70  # Assume partial compliance by default
        
        # Adjust based on company characteristics
        if company_data.get("has_esg_policy", False):
            base_score += 10
        if company_data.get("has_sustainability_report", False):
            base_score += 10
        if company_data.get("has_esg_committee", False):
            base_score += 5
        if company_data.get("third_party_assurance", False):
            base_score += 5
        
        # Random variation for demonstration
        import random
        variation = random.randint(-10, 10)
        final_score = max(0, min(100, base_score + variation))
        
        return final_score
    
    def _get_required_actions(self, regulation: Dict[str, Any], compliance_score: float) -> List[str]:
        """Get required actions based on compliance score"""
        if compliance_score >= 80:
            return ["Maintain current compliance level", "Monitor for regulation updates"]
        elif compliance_score >= 60:
            return [
                "Enhance current ESG reporting processes",
                "Implement missing disclosure requirements",
                "Consider third-party assurance"
            ]
        else:
            return [
                "Urgent: Develop comprehensive ESG policy",
                "Establish ESG governance structure",
                "Implement full disclosure requirements",
                "Engage ESG compliance consultant",
                "Prepare for potential penalties"
            ]
    
    async def _detect_changes(self, new_regulations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect changes in regulations"""
        changes = []
        
        for reg_id, new_reg in new_regulations.items():
            if reg_id in self.regulations_db:
                old_reg = self.regulations_db[reg_id]
                if old_reg.get("last_updated") != new_reg.get("last_updated"):
                    changes.append({
                        "regulation_id": reg_id,
                        "change_type": "Update",
                        "old_version": old_reg.get("last_updated"),
                        "new_version": new_reg.get("last_updated")
                    })
            else:
                changes.append({
                    "regulation_id": reg_id,
                    "change_type": "New",
                    "description": f"New regulation added: {new_reg['name']}"
                })
        
        return changes
    
    def get_regulation_summary(self) -> Dict[str, Any]:
        """Get summary of all tracked regulations"""
        return {
            "total_regulations": len(self.regulations_db),
            "by_jurisdiction": self._group_by_jurisdiction(),
            "by_status": self._group_by_status(),
            "last_update": self.last_full_update.isoformat() if self.last_full_update else None,
            "regulations": list(self.regulations_db.keys())
        }
    
    def _group_by_jurisdiction(self) -> Dict[str, int]:
        """Group regulations by jurisdiction"""
        jurisdictions = {}
        for regulation in self.regulations_db.values():
            jurisdiction = regulation["jurisdiction"]
            jurisdictions[jurisdiction] = jurisdictions.get(jurisdiction, 0) + 1
        return jurisdictions
    
    def _group_by_status(self) -> Dict[str, int]:
        """Group regulations by status"""
        statuses = {}
        for regulation in self.regulations_db.values():
            status = regulation["status"]
            statuses[status] = statuses.get(status, 0) + 1
        return statuses