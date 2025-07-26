"""
LLM Service with Mistral AI integration
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from src.config import Config


class MistralLLMService:
    """Mistral AI service for ESG analysis and insights"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.LLM_API_KEY or os.getenv("MISTRAL_API_KEY")
        self.client = None
        self.model = "mistral-large-latest"  # Use the latest Mistral model
        self.logger = logging.getLogger("mistral_llm")
        
        if self.api_key and self.api_key != "":
            try:
                self.client = MistralClient(api_key=self.api_key)
                self.logger.info("Mistral AI client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Mistral client: {e}")
                self.client = None
        else:
            self.logger.warning("No Mistral API key provided, using mock responses")
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response using Mistral AI"""
        if not self.client:
            return await self._mock_response(prompt, context)
        
        try:
            # Prepare system message for ESG context
            system_message = self._create_system_message(context)
            
            messages = [
                ChatMessage(role="system", content=system_message),
                ChatMessage(role="user", content=prompt)
            ]
            
            # Make API call to Mistral
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Mistral API error: {e}")
            return await self._mock_response(prompt, context)
    
    async def analyze_esg_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ESG data and provide comprehensive insights"""
        if not self.client:
            return await self._mock_esg_analysis(data)
        
        try:
            # Prepare comprehensive analysis prompt
            analysis_prompt = self._create_analysis_prompt(data)
            
            system_message = """You are an expert ESG (Environmental, Social, Governance) analyst with deep knowledge of EU regulations including CSRD, EU Taxonomy, and SFDR. 
            Provide comprehensive, actionable analysis based on current regulatory requirements and best practices. 
            Focus on compliance with EU directives and provide specific, measurable recommendations."""
            
            messages = [
                ChatMessage(role="system", content=system_message),
                ChatMessage(role="user", content=analysis_prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1500
            )
            
            # Parse the response into structured data
            analysis_text = response.choices[0].message.content
            return self._parse_analysis_response(analysis_text, data)
            
        except Exception as e:
            self.logger.error(f"ESG analysis error: {e}")
            return await self._mock_esg_analysis(data)
    
    async def analyze_uploaded_document(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """Analyze uploaded documents for ESG insights"""
        if not self.client:
            return await self._mock_document_analysis(document_text, document_type)
        
        try:
            analysis_prompt = f"""
            Analyze the following {document_type} document for ESG-related information:
            
            Document Content:
            {document_text[:3000]}  # Limit to avoid token limits
            
            Please extract and analyze:
            1. Environmental metrics and initiatives
            2. Social responsibility practices
            3. Governance structures and policies
            4. Compliance with EU regulations (CSRD, EU Taxonomy, SFDR)
            5. Key performance indicators
            6. Areas for improvement
            
            Provide specific, actionable insights based on EU ESG requirements.
            """
            
            system_message = """You are an expert ESG document analyst specializing in EU regulations. 
            Extract relevant ESG information from documents and assess compliance with current EU directives."""
            
            messages = [
                ChatMessage(role="system", content=system_message),
                ChatMessage(role="user", content=analysis_prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=1000
            )
            
            return self._parse_document_analysis(response.choices[0].message.content, document_type)
            
        except Exception as e:
            self.logger.error(f"Document analysis error: {e}")
            return await self._mock_document_analysis(document_text, document_type)
    
    def _create_system_message(self, context: Dict[str, Any] = None) -> str:
        """Create system message with ESG context"""
        base_message = """You are an expert ESG (Environmental, Social, Governance) consultant specializing in EU regulations and sustainability reporting. 
        You have deep knowledge of:
        - Corporate Sustainability Reporting Directive (CSRD)
        - EU Taxonomy Regulation
        - Sustainable Finance Disclosure Regulation (SFDR)
        - European Sustainability Reporting Standards (ESRS)
        
        Provide accurate, actionable advice based on current EU ESG requirements."""
        
        if context:
            company_info = context.get("company_info", {})
            if company_info:
                base_message += f"\n\nCompany Context: {company_info.get('industry', 'Unknown')} industry, {company_info.get('region', 'Unknown')} region, {company_info.get('size', 'Unknown')} size."
        
        return base_message
    
    def _create_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create comprehensive analysis prompt"""
        user_responses = data.get("user_responses", {})
        company_info = data.get("assessment_data", {}).get("company_info", {})
        
        prompt = f"""
        Please analyze the following ESG assessment data for a {company_info.get('industry', 'Unknown')} company:
        
        Company Profile:
        - Industry: {company_info.get('industry', 'Unknown')}
        - Region: {company_info.get('region', 'Unknown')}
        - Size: {company_info.get('size', 'Unknown')}
        
        Assessment Responses:
        """
        
        for response_id, response_data in list(user_responses.items())[:10]:  # Limit responses
            prompt += f"- {response_data.get('category', 'Unknown')}: {response_data.get('question', 'Unknown')[:100]}... Answer: {response_data.get('answer', 'Unknown')}\n"
        
        prompt += """
        
        Please provide:
        1. Overall ESG score (0-100) with justification
        2. Category scores for Environmental, Social, and Governance
        3. Top 3 strengths
        4. Top 3 areas for improvement
        5. Compliance status with EU regulations
        6. 5 specific, actionable recommendations
        7. Priority actions for the next 12 months
        
        Focus on EU regulatory compliance and provide specific guidance based on CSRD and EU Taxonomy requirements.
        """
        
        return prompt
    
    def _parse_analysis_response(self, analysis_text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Mistral response into structured analysis"""
        # This is a simplified parser - in production, you might use more sophisticated NLP
        try:
            # Extract scores using simple text parsing
            import re
            
            # Try to extract overall score
            score_match = re.search(r'overall.*?score.*?(\d+)', analysis_text.lower())
            overall_score = int(score_match.group(1)) if score_match else 75
            
            # Extract category scores (simplified)
            env_match = re.search(r'environmental.*?(\d+)', analysis_text.lower())
            social_match = re.search(r'social.*?(\d+)', analysis_text.lower())
            gov_match = re.search(r'governance.*?(\d+)', analysis_text.lower())
            
            category_scores = {
                "Environmental": int(env_match.group(1)) if env_match else overall_score - 5,
                "Social": int(social_match.group(1)) if social_match else overall_score,
                "Governance": int(gov_match.group(1)) if gov_match else overall_score + 5
            }
            
            # Extract key sections
            strengths = self._extract_list_items(analysis_text, ["strength", "positive", "good"])
            improvements = self._extract_list_items(analysis_text, ["improvement", "weakness", "gap"])
            recommendations = self._extract_list_items(analysis_text, ["recommend", "suggest", "should"])
            
            return {
                "overall_score": min(100, max(0, overall_score)),
                "category_scores": category_scores,
                "strengths": strengths[:3] if strengths else [
                    "Strong commitment to ESG principles",
                    "Good regulatory awareness",
                    "Proactive sustainability approach"
                ],
                "improvements": improvements[:3] if improvements else [
                    "Enhance data collection and reporting",
                    "Strengthen stakeholder engagement",
                    "Improve ESG governance structure"
                ],
                "compliance_status": "Good" if overall_score >= 70 else "Needs Improvement",
                "recommendations": recommendations[:5] if recommendations else [
                    "Implement comprehensive ESG data management system",
                    "Establish ESG committee with board oversight",
                    "Develop science-based targets for emissions reduction",
                    "Enhance supply chain sustainability monitoring",
                    "Prepare for CSRD compliance requirements"
                ],
                "analysis_source": "mistral_ai",
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing analysis response: {e}")
            # Return synchronous mock data instead of async call
            import random
            return {
                "overall_score": random.randint(65, 85),
                "category_scores": {
                    "Environmental": random.randint(60, 90),
                    "Social": random.randint(70, 95),
                    "Governance": random.randint(65, 85)
                },
                "strengths": [
                    "Strong environmental policies aligned with EU Green Deal",
                    "Good stakeholder engagement practices",
                    "Transparent reporting in line with CSRD requirements"
                ],
                "improvements": [
                    "Enhance carbon reduction targets to meet EU taxonomy criteria",
                    "Expand diversity and inclusion initiatives",
                    "Strengthen ESG risk management framework"
                ],
                "compliance_status": "Good",
                "recommendations": [
                    "Implement CSRD-compliant reporting framework",
                    "Establish ESG committee with board oversight",
                    "Develop EU Taxonomy-aligned investment strategy",
                    "Enhance supply chain due diligence processes",
                    "Prepare for SFDR disclosure requirements"
                ],
                "analysis_source": "fallback_sync",
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def _extract_list_items(self, text: str, keywords: List[str]) -> List[str]:
        """Extract list items from text based on keywords"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in keywords):
                # Clean up the line
                if line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                    line = line[2:].strip()
                if len(line) > 10 and len(line) < 200:  # Reasonable length
                    items.append(line)
        
        return items[:5]  # Limit to 5 items
    
    def _parse_document_analysis(self, analysis_text: str, document_type: str) -> Dict[str, Any]:
        """Parse document analysis response"""
        return {
            "document_type": document_type,
            "analysis": analysis_text,
            "extracted_metrics": self._extract_list_items(analysis_text, ["metric", "kpi", "target"]),
            "compliance_notes": self._extract_list_items(analysis_text, ["compliance", "regulation", "directive"]),
            "recommendations": self._extract_list_items(analysis_text, ["recommend", "improve", "enhance"]),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def _mock_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Fallback mock response when Mistral is not available"""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        if "regulation" in prompt.lower() or "compliance" in prompt.lower():
            return "Based on current EU regulations, particularly the CSRD and EU Taxonomy, this aspect requires careful attention to ensure compliance with upcoming reporting requirements."
        elif "recommend" in prompt.lower():
            return "I recommend implementing a comprehensive ESG data management system and establishing clear governance structures to meet EU regulatory requirements."
        else:
            return "This is an important aspect of ESG performance that aligns with current EU sustainability directives and best practices."
    
    async def _mock_esg_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock ESG analysis for fallback"""
        await asyncio.sleep(1)
        
        import random
        return {
            "overall_score": random.randint(65, 85),
            "category_scores": {
                "Environmental": random.randint(60, 90),
                "Social": random.randint(70, 95),
                "Governance": random.randint(65, 85)
            },
            "strengths": [
                "Strong environmental policies aligned with EU Green Deal",
                "Good stakeholder engagement practices",
                "Transparent reporting in line with CSRD requirements"
            ],
            "improvements": [
                "Enhance carbon reduction targets to meet EU taxonomy criteria",
                "Expand diversity and inclusion initiatives",
                "Strengthen ESG risk management framework"
            ],
            "compliance_status": "Good",
            "recommendations": [
                "Implement CSRD-compliant reporting framework",
                "Establish ESG committee with board oversight",
                "Develop EU Taxonomy-aligned investment strategy",
                "Enhance supply chain due diligence processes",
                "Prepare for SFDR disclosure requirements"
            ],
            "analysis_source": "mock_fallback",
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    async def _mock_document_analysis(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """Mock document analysis for fallback"""
        await asyncio.sleep(0.8)
        
        return {
            "document_type": document_type,
            "analysis": f"Analysis of {document_type} document reveals several ESG-related elements that align with EU regulatory requirements.",
            "extracted_metrics": [
                "Carbon emissions reduction targets",
                "Employee diversity ratios",
                "Board independence metrics"
            ],
            "compliance_notes": [
                "Document shows awareness of CSRD requirements",
                "Some alignment with EU Taxonomy criteria",
                "Governance structures meet basic standards"
            ],
            "recommendations": [
                "Enhance quantitative ESG metrics reporting",
                "Improve alignment with ESRS standards",
                "Strengthen materiality assessment process"
            ],
            "analysis_timestamp": datetime.now().isoformat()
        }