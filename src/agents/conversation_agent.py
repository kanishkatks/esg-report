"""
Conversational Agent for natural ESG discussions
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from .base_agent import BaseAgent, get_llm_service


class ConversationAgent(BaseAgent):
    """Agent responsible for natural conversational ESG assessment"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="ConversationAgent",
            description="Conducts natural conversations about ESG practices and compliance",
            config=config
        )
        self.llm_service = get_llm_service()
        self.conversation_history = []
        self.extracted_data = {}
        self.current_topic = None
        self.topics_covered = set()
        self.conversation_context = {}
        
        # Define structured ESG data collection questions (form-like)
        self.esg_topics = {
            "company_overview": {
                "name": "Company Overview",
                "questions": [
                    {"id": "company_size", "question": "How many employees does your company have?", "type": "number", "example": "e.g., 150"},
                    {"id": "annual_revenue", "question": "What is your annual revenue?", "type": "text", "example": "e.g., €10M, $50M, or 'Not disclosed'"},
                    {"id": "main_products", "question": "What are your main products or services?", "type": "text", "example": "e.g., Software solutions, Manufacturing equipment"},
                    {"id": "esg_strategy_exists", "question": "Do you have a formal ESG strategy?", "type": "yes_no", "example": "Yes or No"},
                    {"id": "materiality_assessment", "question": "Have you conducted a materiality assessment?", "type": "yes_no", "example": "Yes or No"},
                    {"id": "stakeholder_groups", "question": "Who are your main stakeholder groups?", "type": "text", "example": "e.g., Customers, Employees, Investors, Communities"}
                ]
            },
            "environmental": {
                "name": "Environmental Data",
                "questions": [
                    {"id": "scope1_emissions", "question": "What are your Scope 1 emissions (tonnes CO2e)?", "type": "number", "example": "e.g., 500 or 'Not measured'"},
                    {"id": "scope2_emissions", "question": "What are your Scope 2 emissions (tonnes CO2e)?", "type": "number", "example": "e.g., 1200 or 'Not measured'"},
                    {"id": "scope3_emissions", "question": "What are your Scope 3 emissions (tonnes CO2e)?", "type": "number", "example": "e.g., 3000 or 'Not measured'"},
                    {"id": "renewable_energy_pct", "question": "What percentage of your energy is renewable?", "type": "percentage", "example": "e.g., 30% or 'Unknown'"},
                    {"id": "water_usage", "question": "What is your annual water usage (cubic meters)?", "type": "number", "example": "e.g., 10000 or 'Not tracked'"},
                    {"id": "waste_recycling_rate", "question": "What is your waste recycling rate?", "type": "percentage", "example": "e.g., 75% or 'Not measured'"},
                    {"id": "climate_targets", "question": "Do you have science-based climate targets?", "type": "yes_no", "example": "Yes or No"}
                ]
            },
            "social": {
                "name": "Social Data",
                "questions": [
                    {"id": "employee_count", "question": "Total number of employees?", "type": "number", "example": "e.g., 250"},
                    {"id": "gender_diversity_pct", "question": "What percentage of employees are women?", "type": "percentage", "example": "e.g., 45%"},
                    {"id": "safety_incidents", "question": "Number of workplace safety incidents last year?", "type": "number", "example": "e.g., 2 or 0"},
                    {"id": "training_hours", "question": "Average training hours per employee per year?", "type": "number", "example": "e.g., 40 hours"},
                    {"id": "community_investment", "question": "Annual community investment amount?", "type": "text", "example": "e.g., €50,000 or 'No formal program'"},
                    {"id": "supplier_assessments", "question": "Do you conduct ESG assessments of suppliers?", "type": "yes_no", "example": "Yes or No"}
                ]
            },
            "governance": {
                "name": "Governance Data",
                "questions": [
                    {"id": "board_size", "question": "How many board members do you have?", "type": "number", "example": "e.g., 7"},
                    {"id": "board_independence", "question": "How many board members are independent?", "type": "number", "example": "e.g., 4"},
                    {"id": "board_diversity", "question": "How many board members are women?", "type": "number", "example": "e.g., 3"},
                    {"id": "ethics_code", "question": "Do you have a code of ethics?", "type": "yes_no", "example": "Yes or No"},
                    {"id": "whistleblower_system", "question": "Do you have a whistleblower system?", "type": "yes_no", "example": "Yes or No"},
                    {"id": "compliance_violations", "question": "Any significant compliance violations last year?", "type": "yes_no", "example": "Yes or No"}
                ]
            },
            "reporting_compliance": {
                "name": "Reporting & Compliance",
                "questions": [
                    {"id": "sustainability_report", "question": "Do you publish a sustainability report?", "type": "yes_no", "example": "Yes or No"},
                    {"id": "reporting_frameworks", "question": "Which reporting frameworks do you use?", "type": "text", "example": "e.g., GRI, SASB, TCFD, or 'None'"},
                    {"id": "third_party_assurance", "question": "Do you get third-party assurance for ESG data?", "type": "yes_no", "example": "Yes or No"},
                    {"id": "csrd_readiness", "question": "Are you preparing for CSRD compliance?", "type": "yes_no", "example": "Yes or No"},
                    {"id": "taxonomy_alignment", "question": "Do you assess EU Taxonomy alignment?", "type": "yes_no", "example": "Yes or No"}
                ]
            }
        }
        
        # Track data collection progress
        self.knowledge_collected = {}
        self.completion_threshold = 0.8  # 80% of topics covered to generate report
        self.current_question_index = 0
        self.current_question = None
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute conversation task"""
        task_type = task.get("type", "chat")
        
        if task_type == "start_conversation":
            return await self.start_conversation(task.get("company_info", {}))
        elif task_type == "process_message":
            return await self.process_user_message(task.get("message", ""), task.get("context", {}))
        elif task_type == "get_next_question":
            return await self.get_next_question()
        elif task_type == "summarize_conversation":
            return await self.summarize_conversation()
        else:
            return await self.process_user_message(task.get("message", ""), task.get("context", {}))
    
    async def start_conversation(self, company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Start the ESG data collection conversation"""
        self.conversation_context = company_info
        
        # Create concise opening message focused on data collection
        company_name = company_info.get("name", "your company")
        
        # Check if we have research data to pre-populate
        research_data = company_info.get("research_data", {})
        has_research = bool(research_data)
        
        if has_research:
            # Pre-populate knowledge base with research findings
            self._integrate_research_data(research_data)
        
        # Start with first topic and first question
        self.current_topic = "company_overview"
        self.current_question_index = 0
        
        # Get first question
        first_question = self._get_next_question()
        
        opening_message = f"""Hello! I'm collecting ESG data for {company_name}.

I'll ask you a series of specific questions to gather the information needed for your ESG report. Please provide concise, factual answers.

{first_question}"""
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": opening_message,
            "timestamp": datetime.now().isoformat(),
            "topic": self.current_topic
        })
        
        return {
            "message": opening_message,
            "topic": self.current_topic,
            "conversation_started": True,
            "context": self.conversation_context,
            "knowledge_progress": 0.1 if has_research else 0.0
        }
    
    async def process_user_message(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user message and collect data"""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat(),
            "topic": self.current_topic
        })
        
        # Check if this is a help request
        help_response = self._check_for_help_request(user_message)
        if help_response:
            # Add help response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": help_response,
                "timestamp": datetime.now().isoformat(),
                "topic": self.current_topic,
                "type": "help"
            })
            
            return {
                "message": help_response,
                "topic": self.current_topic,
                "extracted_data": {},
                "next_action": {"action": "continue_topic"},
                "ready_for_report": False,
                "conversation_progress": self._calculate_progress()
            }
        
        # Store the answer for current question
        if self.current_question:
            self._store_answer(self.current_question["id"], user_message)
        
        # Move to next question
        self.current_question_index += 1
        next_question = self._get_next_question()
        
        if next_question:
            # Continue with next question
            response = f"Got it. {next_question}"
        else:
            # All questions completed
            response = "Thank you! I've collected all the necessary ESG data. Your report is now ready to be generated."
            self.topics_covered = set(self.esg_topics.keys())  # Mark all as covered
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat(),
            "topic": self.current_topic
        })
        
        # Check if data collection is complete
        is_complete = next_question is None
        
        return {
            "message": response,
            "topic": self.current_topic,
            "extracted_data": {},
            "next_action": {"action": "ready_for_report" if is_complete else "continue_topic"},
            "ready_for_report": is_complete,
            "conversation_progress": self._calculate_progress()
        }
    
    def _check_for_help_request(self, user_message: str) -> Optional[str]:
        """Check if user is asking for help and provide explanation"""
        message_lower = user_message.lower().strip()
        
        # Help request patterns
        help_patterns = [
            "what is that", "what's that", "what is this", "what's this",
            "how do i get that", "how do i get this", "how to get",
            "what does that mean", "what does this mean", "explain",
            "i don't understand", "don't understand", "unclear",
            "help", "?", "what", "how"
        ]
        
        # Check if message matches help patterns
        is_help_request = any(pattern in message_lower for pattern in help_patterns)
        
        if not is_help_request:
            return None
        
        # Get current question context for explanation
        if not self.current_question:
            return "💡 I'm here to help with ESG data collection. Ask me about any ESG terms you need clarified."
        
        question_id = self.current_question["id"]
        question_text = self.current_question["question"]
        
        # Provide concise 1-2 line explanations
        explanations = {
            "scope1_emissions": "Direct emissions from sources you own/control (company vehicles, on-site fuel use). Measured in tonnes CO2e.",
            "scope2_emissions": "Indirect emissions from purchased electricity, steam, heating/cooling. Usually from your energy bills.",
            "scope3_emissions": "All other indirect emissions in your value chain (business travel, suppliers, commuting). Often the largest category.",
            "renewable_energy_pct": "Percentage of total energy from renewable sources (solar, wind, hydro). Check your energy contracts or bills.",
            "materiality_assessment": "Process to identify which ESG topics matter most to your business and stakeholders. Helps prioritize efforts.",
            "climate_targets": "Science-based targets are emission reduction goals aligned with limiting global warming to 1.5°C.",
            "board_independence": "Independent directors have no material relationship with the company beyond their board role.",
            "csrd_readiness": "EU regulation requiring detailed ESG reporting starting 2024-2028. Applies to large companies and listed SMEs.",
            "taxonomy_alignment": "EU classification system for sustainable activities. Companies assess what % of revenue/capex qualifies.",
            "whistleblower_system": "Confidential way for employees to report misconduct or violations without fear of retaliation.",
            "third_party_assurance": "Independent verification of ESG data by external auditors to ensure accuracy and credibility.",
            "reporting_frameworks": "Standards like GRI, SASB, TCFD that guide how to structure and present ESG information.",
            "sustainability_report": "Annual document detailing company's environmental, social and governance performance and initiatives.",
            "ethics_code": "Written standards defining acceptable behavior and business practices for employees and management.",
            "supplier_assessments": "Evaluating suppliers on ESG criteria to ensure responsible sourcing and supply chain practices."
        }
        
        # Get specific explanation or provide general help
        if question_id in explanations:
            explanation = explanations[question_id]
        else:
            # Generate contextual explanation based on question content
            if "emissions" in question_text.lower():
                explanation = "Greenhouse gases released, measured in tonnes CO2 equivalent. Check energy bills or sustainability reports."
            elif "percentage" in question_text.lower() or "%" in question_text:
                explanation = "Provide a percentage value (e.g., 30%) or say 'Not tracked' if you don't measure this."
            elif "number" in question_text.lower() or "how many" in question_text.lower():
                explanation = "Provide a specific number or say 'Not available' if you don't have this information."
            elif "yes" in self.current_question.get("example", "").lower():
                explanation = "Answer 'Yes' if you have this in place, 'No' if you don't."
            else:
                explanation = f"This asks about {question_text.lower()}. Provide the information or say 'Not available'."
        
        return f"💡 {explanation}\n\n{question_text} ({self.current_question['example']})"
    
    def _get_next_question(self) -> Optional[str]:
        """Get the next question in the sequence"""
        # Get all questions from all topics
        all_questions = []
        for topic_key, topic_data in self.esg_topics.items():
            for question in topic_data["questions"]:
                question["topic"] = topic_key
                all_questions.append(question)
        
        # Check if we have more questions
        if self.current_question_index < len(all_questions):
            self.current_question = all_questions[self.current_question_index]
            
            # Update current topic if needed
            if self.current_question["topic"] != self.current_topic:
                self.current_topic = self.current_question["topic"]
                topic_name = self.esg_topics[self.current_topic]["name"]
                return f"\n**{topic_name}**\n\n{self.current_question['question']} ({self.current_question['example']})"
            else:
                return f"{self.current_question['question']} ({self.current_question['example']})"
        else:
            self.current_question = None
            return None
    
    def _store_answer(self, question_id: str, answer: str):
        """Store the answer for a specific question"""
        if self.current_topic not in self.knowledge_collected:
            self.knowledge_collected[self.current_topic] = {}
        
        # Clean and store the answer
        cleaned_answer = answer.strip()
        self.knowledge_collected[self.current_topic][question_id] = cleaned_answer
        
        self.logger.info(f"Stored answer for {question_id}: {cleaned_answer}")
    
    def _calculate_progress(self) -> float:
        """Calculate overall progress"""
        total_questions = sum(len(topic["questions"]) for topic in self.esg_topics.values())
        return min(self.current_question_index / total_questions, 1.0)
    
    async def _extract_esg_data(self, user_message: str) -> Dict[str, Any]:
        """Extract structured ESG knowledge from user's response"""
        
        current_topic_info = self.esg_topics.get(self.current_topic, {})
        data_to_collect = current_topic_info.get("data_to_collect", [])
        
        extraction_prompt = f"""
        Extract specific ESG knowledge from this user response: "{user_message}"
        
        Current Topic: {current_topic_info.get('name', self.current_topic)}
        
        Look for these specific data points: {', '.join(data_to_collect)}
        
        Extract:
        - Quantitative metrics (numbers, percentages, amounts)
        - Qualitative information (policies, practices, initiatives)
        - Compliance status (yes/no, implemented/not implemented)
        - Specific programs or frameworks mentioned
        - Gaps or challenges identified
        
        Return structured JSON with keys matching the data points we're collecting.
        For missing information, use null values.
        
        Example format:
        {{
            "company_size": "150 employees",
            "esg_strategy_exists": true,
            "materiality_topics": ["climate change", "employee welfare"],
            "scope1_emissions": "500 tonnes CO2e",
            "renewable_energy_pct": 30
        }}
        """
        
        try:
            llm_response = await self.llm_service.generate_response(
                extraction_prompt,
                {"current_topic": self.current_topic, "company_info": self.conversation_context}
            )
            
            # Try to parse as JSON, fallback to structured extraction
            try:
                extracted = json.loads(llm_response)
            except:
                # Fallback: structured keyword extraction
                extracted = self._structured_extraction(user_message, data_to_collect)
            
            # Store in knowledge base
            self._update_knowledge_base(extracted)
            
            return extracted
            
        except Exception as e:
            self.logger.error(f"Error extracting ESG data: {e}")
            return self._structured_extraction(user_message, data_to_collect)
    
    def _structured_extraction(self, user_message: str, data_to_collect: List[str]) -> Dict[str, Any]:
        """Structured fallback extraction method based on current topic"""
        message_lower = user_message.lower()
        extracted = {}
        
        # Import regex for pattern matching
        import re
        
        # Extract based on data points we're looking for
        for data_point in data_to_collect:
            if "size" in data_point or "count" in data_point:
                # Look for numbers with employee/people context
                numbers = re.findall(r'(\d+(?:,\d+)*)\s*(?:employees?|people|staff|workers)', message_lower)
                if numbers:
                    extracted[data_point] = f"{numbers[0]} employees"
            
            elif "pct" in data_point or "percentage" in data_point:
                # Look for percentages
                percentages = re.findall(r'(\d+(?:\.\d+)?)\s*(?:%|percent)', message_lower)
                if percentages:
                    extracted[data_point] = float(percentages[0])
            
            elif "emissions" in data_point:
                # Look for emission values
                emissions = re.findall(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:tonnes?|tons?|kg|mt)\s*(?:co2e?|carbon)', message_lower)
                if emissions:
                    extracted[data_point] = f"{emissions[0]} tonnes CO2e"
            
            elif "exists" in data_point or "strategy" in data_point:
                # Look for yes/no answers
                if any(word in message_lower for word in ["yes", "we do", "we have", "implemented", "established"]):
                    extracted[data_point] = True
                elif any(word in message_lower for word in ["no", "we don't", "not yet", "haven't", "don't have"]):
                    extracted[data_point] = False
            
            elif "topics" in data_point or "frameworks" in data_point:
                # Look for lists of items
                common_topics = ["climate change", "biodiversity", "water", "waste", "energy", "emissions",
                               "diversity", "safety", "training", "community", "governance", "ethics"]
                found_topics = [topic for topic in common_topics if topic in message_lower]
                if found_topics:
                    extracted[data_point] = found_topics
        
        return extracted
    
    def _update_knowledge_base(self, extracted_data: Dict[str, Any]):
        """Update the knowledge base with extracted data"""
        if self.current_topic not in self.knowledge_collected:
            self.knowledge_collected[self.current_topic] = {}
        
        # Merge extracted data into knowledge base
        for key, value in extracted_data.items():
            if value is not None:  # Only store non-null values
                self.knowledge_collected[self.current_topic][key] = value
        
        # Log progress
        self.logger.info(f"Updated knowledge for {self.current_topic}: {list(extracted_data.keys())}")
    
    def _simple_extraction(self, user_message: str) -> Dict[str, Any]:
        """Simple fallback extraction method"""
        message_lower = user_message.lower()
        
        extracted = {
            "metrics": [],
            "compliance": {},
            "frameworks": [],
            "initiatives": [],
            "challenges": []
        }
        
        # Look for common ESG keywords and patterns
        if any(word in message_lower for word in ["yes", "we do", "we have", "we measure"]):
            extracted["compliance"][self.current_topic] = "positive"
        elif any(word in message_lower for word in ["no", "we don't", "not yet", "haven't"]):
            extracted["compliance"][self.current_topic] = "negative"
        
        # Look for frameworks
        frameworks = ["gri", "sasb", "tcfd", "csrd", "eu taxonomy", "sfdr"]
        for framework in frameworks:
            if framework in message_lower:
                extracted["frameworks"].append(framework.upper())
        
        # Look for numbers (potential metrics)
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?(?:%|percent|tonnes?|kwh|mwh)', message_lower)
        extracted["metrics"] = numbers
        
        return extracted
    
    async def _generate_contextual_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Generate contextual response using LLM"""
        
        # Build conversation context
        recent_history = self.conversation_history[-4:]  # Last 4 messages
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])
        
        company_info = self.conversation_context
        current_topic_info = self.esg_topics.get(self.current_topic, {})
        
        response_prompt = f"""
        You are an expert ESG consultant having a natural conversation with a company about their sustainability practices. 
        
        Company Context:
        - Name: {company_info.get('name', 'Unknown')}
        - Industry: {company_info.get('industry', 'Unknown')}
        - Region: {company_info.get('region', 'Unknown')}
        - Size: {company_info.get('size', 'Unknown')}
        
        Current Topic: {current_topic_info.get('name', self.current_topic)}
        Key Points to Cover: {', '.join(current_topic_info.get('key_points', []))}
        
        Recent Conversation:
        {history_text}
        
        User's Latest Message: "{user_message}"
        
        Generate a natural, conversational response that:
        1. Acknowledges what the user shared
        2. Provides relevant ESG insights or guidance
        3. References EU regulations (CSRD, EU Taxonomy, SFDR) when relevant
        4. Asks a thoughtful follow-up question to continue the conversation
        5. Keeps the tone professional but friendly and conversational
        
        Focus on being helpful and educational while gathering information for their ESG assessment.
        """
        
        try:
            response = await self.llm_service.generate_response(
                response_prompt,
                {"conversation_context": self.conversation_context}
            )
            return response
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._fallback_response(user_message)
    
    def _fallback_response(self, user_message: str) -> str:
        """Fallback response when LLM is unavailable"""
        responses = {
            "emissions": "That's helpful information about your emissions. Understanding your current measurement and reporting practices is crucial for CSRD compliance. Can you tell me more about your emission reduction targets?",
            "energy": "Thanks for sharing about your energy practices. Energy management is a key part of ESG performance. How do you track and report your energy consumption?",
            "governance": "I appreciate you sharing about your governance structure. Strong ESG governance is essential for regulatory compliance. How does your board currently oversee ESG matters?",
            "social": "That's valuable insight into your social practices. Employee and community engagement are important ESG factors. Can you elaborate on your diversity and inclusion initiatives?",
            "reporting": "Thank you for that information about your reporting practices. Transparent ESG reporting is increasingly important, especially with new EU regulations. Which reporting frameworks do you currently use?"
        }
        
        return responses.get(self.current_topic, "Thank you for sharing that information. Can you tell me more about your ESG practices in this area?")
    
    async def _determine_next_action(self, user_message: str) -> Dict[str, Any]:
        """Determine what to do next in the conversation"""
        
        # Check if current topic is sufficiently covered
        topic_coverage = self._assess_topic_coverage(self.current_topic)
        knowledge_completeness = self._assess_knowledge_completeness(self.current_topic)
        
        # Topic is well covered if we have good coverage AND sufficient knowledge
        topic_complete = topic_coverage > 0.6 and knowledge_completeness > 0.5
        
        if topic_complete:
            self.topics_covered.add(self.current_topic)
            
            # Check overall completion
            overall_completion = len(self.topics_covered) / len(self.esg_topics)
            
            if overall_completion >= self.completion_threshold:
                return {
                    "action": "ready_for_report",
                    "message": "Excellent! We've gathered comprehensive information across all ESG areas. I can now generate your ESG assessment report.",
                    "completion_percentage": overall_completion * 100,
                    "knowledge_summary": self._get_knowledge_summary()
                }
            
            # Move to next topic
            next_topic = self._get_next_topic()
            if next_topic:
                self.current_topic = next_topic
                topic_info = self.esg_topics[next_topic]
                return {
                    "action": "transition_topic",
                    "next_topic": next_topic,
                    "transition_message": f"Great! Now let's move on to {topic_info['name']}. {self._get_topic_introduction(next_topic)}"
                }
            else:
                return {
                    "action": "complete_assessment",
                    "message": "We've covered all the main ESG topics. Let me prepare your assessment report.",
                    "completion_percentage": overall_completion * 100
                }
        else:
            # Continue with current topic
            return {
                "action": "continue_topic",
                "follow_up_question": self._get_targeted_follow_up(),
                "topic_progress": {
                    "coverage": topic_coverage,
                    "knowledge": knowledge_completeness,
                    "missing_data": self._get_missing_data_points()
                }
            }
    
    def _assess_topic_coverage(self, topic: str) -> float:
        """Assess how well a topic has been covered"""
        topic_messages = [msg for msg in self.conversation_history if msg.get("topic") == topic]
        
        # Simple heuristic: coverage based on number of exchanges and data extracted
        exchanges = len([msg for msg in topic_messages if msg["role"] == "user"])
        has_data = topic in self.extracted_data and bool(self.extracted_data[topic])
        
        base_coverage = min(exchanges / 3, 1.0)  # 3 exchanges = full coverage
        data_bonus = 0.3 if has_data else 0
        
        return min(base_coverage + data_bonus, 1.0)
    
    def _assess_knowledge_completeness(self, topic: str) -> float:
        """Assess how complete our knowledge is for a topic"""
        if topic not in self.esg_topics:
            return 0.0
        
        expected_data_points = self.esg_topics[topic].get("data_to_collect", [])
        if not expected_data_points:
            return 1.0  # No specific data expected
        
        collected_data = self.knowledge_collected.get(topic, {})
        collected_count = len([v for v in collected_data.values() if v is not None])
        
        return min(collected_count / len(expected_data_points), 1.0)
    
    def _get_knowledge_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected knowledge"""
        summary = {}
        for topic, data in self.knowledge_collected.items():
            if data:
                summary[topic] = {
                    "data_points": len(data),
                    "key_findings": list(data.keys())[:3]  # Top 3 findings
                }
        return summary
    
    def _get_topic_introduction(self, topic: str) -> str:
        """Get an introduction for a new topic"""
        topic_info = self.esg_topics.get(topic, {})
        key_points = topic_info.get("key_points", [])
        
        intros = {
            "environmental": f"I'd like to understand your environmental impact and sustainability practices, particularly around {', '.join(key_points[:3])}.",
            "social": f"Let's discuss your social impact and people practices, focusing on {', '.join(key_points[:3])}.",
            "governance": f"Now I'd like to learn about your governance structure and practices, especially {', '.join(key_points[:3])}.",
            "reporting_compliance": f"Finally, let's talk about your ESG reporting and compliance, including {', '.join(key_points[:3])}."
        }
        
        return intros.get(topic, f"Let's explore {topic_info.get('name', topic)}.")
    
    def _get_targeted_follow_up(self) -> str:
        """Get a targeted follow-up question based on missing data"""
        if self.current_topic not in self.esg_topics:
            return "Can you tell me more about your practices in this area?"
        
        topic_info = self.esg_topics[self.current_topic]
        collected_data = self.knowledge_collected.get(self.current_topic, {})
        missing_data = self._get_missing_data_points()
        
        if missing_data:
            # Ask about the first missing data point
            missing_point = missing_data[0]
            questions = topic_info.get("questions", [])
            
            # Try to find a relevant question
            for question in questions:
                if any(keyword in question.lower() for keyword in missing_point.split('_')):
                    return question
        
        # Fallback to general questions
        questions = topic_info.get("questions", [])
        asked_questions = [msg["content"] for msg in self.conversation_history if msg["role"] == "assistant"]
        
        for question in questions:
            if not any(question.lower() in asked.lower() for asked in asked_questions):
                return question
        
        return "Is there anything else you'd like to share about this area?"
    
    def _get_missing_data_points(self) -> List[str]:
        """Get list of missing data points for current topic"""
        if self.current_topic not in self.esg_topics:
            return []
        
        expected_data = self.esg_topics[self.current_topic].get("data_to_collect", [])
        collected_data = self.knowledge_collected.get(self.current_topic, {})
        
        return [point for point in expected_data if point not in collected_data or collected_data[point] is None]
    
    def _get_next_topic(self) -> Optional[str]:
        """Get the next topic to discuss"""
        uncovered_topics = set(self.esg_topics.keys()) - self.topics_covered
        
        if not uncovered_topics:
            return None
        
        # Prioritize topics based on company context
        industry = self.conversation_context.get("industry", "").lower()
        region = self.conversation_context.get("region", "").lower()
        
        # Priority order based on context
        if "manufacturing" in industry:
            priority = ["emissions", "energy", "social", "governance", "reporting"]
        elif "financial" in industry:
            priority = ["governance", "reporting", "social", "emissions", "energy"]
        elif "europe" in region or "eu" in region:
            priority = ["emissions", "reporting", "governance", "social", "energy"]
        else:
            priority = ["emissions", "governance", "social", "energy", "reporting"]
        
        for topic in priority:
            if topic in uncovered_topics:
                return topic
        
        return list(uncovered_topics)[0]  # Fallback
    
    def _update_extracted_data(self, new_data: Dict[str, Any]):
        """Update the extracted ESG data"""
        if self.current_topic not in self.extracted_data:
            self.extracted_data[self.current_topic] = {}
        
        # Merge new data with existing data
        for key, value in new_data.items():
            if key not in self.extracted_data[self.current_topic]:
                self.extracted_data[self.current_topic][key] = value
            else:
                # Merge lists and dicts
                if isinstance(value, list):
                    self.extracted_data[self.current_topic][key].extend(value)
                elif isinstance(value, dict):
                    self.extracted_data[self.current_topic][key].update(value)
                else:
                    self.extracted_data[self.current_topic][key] = value
    
    async def get_next_question(self) -> Dict[str, Any]:
        """Get the next question to ask"""
        if self.current_topic and self.current_topic in self.esg_topics:
            follow_ups = self.esg_topics[self.current_topic]["follow_ups"]
            
            # Select follow-up based on conversation history
            asked_questions = [msg["content"] for msg in self.conversation_history if msg["role"] == "assistant"]
            
            for question in follow_ups:
                if not any(question.lower() in asked.lower() for asked in asked_questions):
                    return {
                        "question": question,
                        "topic": self.current_topic,
                        "type": "follow_up"
                    }
        
        return {
            "question": "Is there anything else you'd like to share about your ESG practices?",
            "topic": self.current_topic,
            "type": "open_ended"
        }
    
    async def summarize_conversation(self) -> Dict[str, Any]:
        """Summarize the entire conversation and extracted data"""
        
        summary_prompt = f"""
        Summarize this ESG conversation and provide an assessment based on the extracted data:
        
        Company: {self.conversation_context.get('name', 'Unknown')}
        Industry: {self.conversation_context.get('industry', 'Unknown')}
        
        Topics Covered: {', '.join(self.topics_covered)}
        
        Extracted Data: {json.dumps(self.extracted_data, indent=2)}
        
        Provide:
        1. Summary of key ESG practices discussed
        2. Strengths identified
        3. Areas for improvement
        4. EU regulatory compliance status
        5. Recommendations for next steps
        """
        
        try:
            summary = await self.llm_service.generate_response(summary_prompt, self.conversation_context)
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            summary = "Conversation completed. ESG data has been collected for report generation."
        
        return {
            "summary": summary,
            "topics_covered": list(self.topics_covered),
            "extracted_data": self.extracted_data,
            "conversation_length": len(self.conversation_history),
            "completion_percentage": len(self.topics_covered) / len(self.esg_topics) * 100
        }
    
    def get_conversation_data(self) -> Dict[str, Any]:
        """Get all conversation data for report generation"""
        return {
            "conversation_history": self.conversation_history,
            "extracted_data": self.extracted_data,
            "knowledge_collected": self.knowledge_collected,
            "topics_covered": list(self.topics_covered),
            "conversation_context": self.conversation_context,
            "current_topic": self.current_topic,
            "completion_percentage": len(self.topics_covered) / len(self.esg_topics) * 100,
            "knowledge_summary": self._get_knowledge_summary()
        }
    
    def is_ready_for_report(self) -> bool:
        """Check if we have enough information to generate a report"""
        completion_rate = len(self.topics_covered) / len(self.esg_topics)
        
        # Check if we have minimum knowledge across topics
        knowledge_scores = []
        for topic in self.esg_topics.keys():
            knowledge_scores.append(self._assess_knowledge_completeness(topic))
        
        avg_knowledge = sum(knowledge_scores) / len(knowledge_scores) if knowledge_scores else 0
        
        return completion_rate >= self.completion_threshold and avg_knowledge >= 0.4
    
    def get_report_readiness_status(self) -> Dict[str, Any]:
        """Get detailed status of report readiness"""
        topic_status = {}
        for topic in self.esg_topics.keys():
            topic_status[topic] = {
                "covered": topic in self.topics_covered,
                "coverage_score": self._assess_topic_coverage(topic),
                "knowledge_score": self._assess_knowledge_completeness(topic),
                "missing_data": self._get_missing_data_points() if topic == self.current_topic else []
            }
        
        return {
            "ready_for_report": self.is_ready_for_report(),
            "overall_completion": len(self.topics_covered) / len(self.esg_topics) * 100,
            "topic_status": topic_status,
            "total_knowledge_points": sum(len(data) for data in self.knowledge_collected.values()),
            "conversation_length": len(self.conversation_history)
        }
    def _integrate_research_data(self, research_data: Dict[str, Any]):
        """Integrate research data into knowledge base"""
        try:
            # Extract relevant information from research data
            basic_info = research_data.get("basic_info", {})
            business_info = research_data.get("business_info", {})
            esg_indicators = research_data.get("esg_indicators", {})
            sustainability_data = research_data.get("sustainability_data", {})
            public_commitments = research_data.get("public_commitments", {})
            
            # Pre-populate company overview knowledge
            if "company_overview" not in self.knowledge_collected:
                self.knowledge_collected["company_overview"] = {}
            
            # Add basic company information
            if basic_info.get("description"):
                self.knowledge_collected["company_overview"]["company_description"] = basic_info["description"]
            
            if business_info.get("main_products"):
                self.knowledge_collected["company_overview"]["main_products"] = business_info["main_products"]
            
            if esg_indicators.get("mentions_esg"):
                self.knowledge_collected["company_overview"]["esg_strategy_exists"] = True
            
            # Pre-populate environmental knowledge
            if "environmental" not in self.knowledge_collected:
                self.knowledge_collected["environmental"] = {}
            
            environmental_commitments = esg_indicators.get("environmental_commitments", [])
            if environmental_commitments:
                self.knowledge_collected["environmental"]["environmental_commitments"] = environmental_commitments
            
            climate_targets = sustainability_data.get("climate_targets", {})
            if climate_targets.get("net_zero_commitment"):
                self.knowledge_collected["environmental"]["climate_targets"] = "Net zero commitment"
            
            if climate_targets.get("renewable_energy_target"):
                self.knowledge_collected["environmental"]["renewable_energy_target"] = climate_targets["renewable_energy_target"]
            
            # Pre-populate social knowledge
            if "social" not in self.knowledge_collected:
                self.knowledge_collected["social"] = {}
            
            social_commitments = esg_indicators.get("social_commitments", [])
            if social_commitments:
                self.knowledge_collected["social"]["social_commitments"] = social_commitments
            
            # Pre-populate governance knowledge
            if "governance" not in self.knowledge_collected:
                self.knowledge_collected["governance"] = {}
            
            governance_indicators = esg_indicators.get("governance_indicators", [])
            if governance_indicators:
                self.knowledge_collected["governance"]["governance_practices"] = governance_indicators
            
            # Pre-populate reporting compliance knowledge
            if "reporting_compliance" not in self.knowledge_collected:
                self.knowledge_collected["reporting_compliance"] = {}
            
            if sustainability_data.get("sustainability_report_available"):
                self.knowledge_collected["reporting_compliance"]["sustainability_report"] = True
            
            esg_frameworks = sustainability_data.get("esg_frameworks_mentioned", [])
            if esg_frameworks:
                self.knowledge_collected["reporting_compliance"]["reporting_frameworks"] = esg_frameworks
            
            if sustainability_data.get("sustainability_certifications"):
                self.knowledge_collected["reporting_compliance"]["certifications"] = sustainability_data["sustainability_certifications"]
            
            # Log the integration
            self.logger.info(f"Integrated research data into knowledge base: {list(self.knowledge_collected.keys())}")
            
        except Exception as e:
            self.logger.error(f"Error integrating research data: {e}")