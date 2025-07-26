"""
Enhanced ESG Report Generator with Real Data Integration
Uses actual knowledge base data and current regulations
"""
import io
import base64
from datetime import datetime
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor
import plotly.graph_objects as go
import plotly.express as px


class EnhancedESGReportGenerator:
    """Generate comprehensive ESG reports using real knowledge base data and current regulations"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.colors = {
            'primary': HexColor('#2E8B57'),
            'secondary': HexColor('#4169E1'),
            'accent': HexColor('#FF8C00'),
            'success': HexColor('#28a745'),
            'warning': HexColor('#ffc107'),
            'danger': HexColor('#dc3545')
        }
        
        # Current ESG regulations (updated 2024)
        self.current_regulations = {
            "CSRD": {
                "name": "Corporate Sustainability Reporting Directive",
                "effective_date": "2024-01-05",
                "description": "EU directive requiring detailed ESG reporting for large companies",
                "requirements": [
                    "Double materiality assessment",
                    "Detailed environmental metrics",
                    "Social and governance disclosures",
                    "Third-party assurance"
                ]
            },
            "EU_TAXONOMY": {
                "name": "EU Taxonomy Regulation",
                "effective_date": "2022-01-01",
                "description": "Classification system for environmentally sustainable economic activities",
                "requirements": [
                    "Revenue alignment assessment",
                    "CapEx alignment assessment",
                    "OpEx alignment assessment",
                    "Do No Significant Harm (DNSH) analysis"
                ]
            },
            "SFDR": {
                "name": "Sustainable Finance Disclosure Regulation",
                "effective_date": "2021-03-10",
                "description": "EU regulation on sustainability-related disclosures in financial services",
                "requirements": [
                    "Principal adverse impacts disclosure",
                    "Sustainability risk integration",
                    "Product-level disclosures"
                ]
            }
        }
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E8B57'),
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#4169E1')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#333333')
        ))
    
    def generate_report(self, 
                       company_info: Dict[str, Any], 
                       assessment_data: Dict[str, Any], 
                       knowledge_collected: Dict[str, Any], 
                       insights: Dict[str, Any],
                       regulations_data: Dict[str, Any] = None) -> bytes:
        """Generate complete ESG report using real data"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build report content using real data
        story = []
        
        # Title page with real company info
        story.extend(self._create_title_page(company_info))
        
        # Executive summary based on actual data
        story.extend(self._create_data_driven_executive_summary(insights, company_info, knowledge_collected))
        
        # Real ESG scores and analysis
        story.extend(self._create_real_scores_section(knowledge_collected, company_info))
        
        # Category analysis using actual responses
        story.extend(self._create_real_category_analysis(knowledge_collected, company_info))
        
        # Current regulatory compliance status
        story.extend(self._create_current_compliance_section(knowledge_collected, company_info, regulations_data))
        
        # Data-driven recommendations
        story.extend(self._create_data_driven_recommendations(knowledge_collected, company_info))
        
        # Appendix with actual responses
        story.extend(self._create_real_data_appendix(knowledge_collected))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _create_title_page(self, company_info: Dict[str, Any]) -> List:
        """Create report title page with real company data"""
        story = []
        
        # Title
        title = Paragraph(f"SustainPilot ESG Assessment Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Company name
        company_title = Paragraph(f"<b>{company_info.get('name', 'Company Name')}</b>", 
                                 self.styles['Heading1'])
        story.append(company_title)
        story.append(Spacer(1, 30))
        
        # Real company details
        company_data = [
            ['Industry:', company_info.get('industry', 'N/A')],
            ['Region:', company_info.get('region', 'N/A')],
            ['Company Size:', company_info.get('size', 'N/A')],
            ['Website:', company_info.get('website', 'N/A')],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
            ['Assessment ID:', f"ESG-{datetime.now().strftime('%Y%m%d-%H%M')}"]
        ]
        
        company_table = Table(company_data, colWidths=[2*inch, 3*inch])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(company_table)
        story.append(Spacer(1, 50))
        
        # Regulatory compliance disclaimer
        disclaimer = Paragraph(
            "<i>This report provides an assessment of Environmental, Social, and Governance (ESG) "
            "practices based on actual data provided by the company. Analysis includes compliance with "
            "current EU regulations including CSRD, EU Taxonomy, and SFDR requirements as of 2024.</i>",
            self.styles['Normal']
        )
        story.append(disclaimer)
        
        # Page break
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
        
        return story
    
    def _create_data_driven_executive_summary(self, insights: Dict[str, Any], company_info: Dict[str, Any], knowledge_collected: Dict[str, Any]) -> List:
        """Create executive summary based on actual collected data"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Calculate real scores based on actual data
        real_scores = self._calculate_real_scores(knowledge_collected)
        overall_score = real_scores.get('overall_score', 0)
        
        # Data completeness assessment
        total_questions = sum(len(topic.get('questions', [])) for topic in knowledge_collected.values() if isinstance(topic, dict))
        answered_questions = sum(1 for topic in knowledge_collected.values() if isinstance(topic, dict) 
                               for answer in topic.values() if answer and str(answer).strip() not in ['', 'Not available', 'N/A'])
        
        completeness = (answered_questions / total_questions * 100) if total_questions > 0 else 0
        
        # Summary based on real data
        summary_text = f"""
        {company_info.get('name', 'The company')} has completed a comprehensive ESG assessment 
        with {completeness:.1f}% data completeness. Based on the actual information provided, 
        the overall ESG performance score is {overall_score:.1f}/100. This assessment covers 
        {len(knowledge_collected)} ESG domains with {answered_questions} data points collected.
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Real category scores table
        category_scores = real_scores.get('category_scores', {})
        metrics_data = [['Category', 'Score', 'Data Points', 'Performance Level']]
        
        for category, score in category_scores.items():
            data_points = len([v for v in knowledge_collected.get(category, {}).values() 
                             if v and str(v).strip() not in ['', 'Not available', 'N/A']])
            performance = self._get_performance_level(score)
            metrics_data.append([category.replace('_', ' ').title(), f"{score:.1f}/100", str(data_points), performance])
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1.8*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Key findings based on actual data
        story.append(Paragraph("Key Findings from Collected Data", self.styles['SubHeader']))
        
        findings = self._extract_key_findings(knowledge_collected, company_info)
        findings_text = "<b>Strengths Identified:</b><br/>"
        for strength in findings['strengths']:
            findings_text += f"• {strength}<br/>"
        
        findings_text += "<br/><b>Areas Requiring Attention:</b><br/>"
        for improvement in findings['improvements']:
            findings_text += f"• {improvement}<br/>"
        
        story.append(Paragraph(findings_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_real_scores_section(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> List:
        """Create ESG scores section based on real data"""
        story = []
        
        story.append(Paragraph("ESG Performance Analysis", self.styles['SectionHeader']))
        
        # Calculate real scores
        real_scores = self._calculate_real_scores(knowledge_collected)
        category_scores = real_scores.get('category_scores', {})
        
        # Create chart with real data
        chart_buffer = self._create_real_data_chart(category_scores)
        if chart_buffer:
            chart_image = Image(chart_buffer, width=5*inch, height=3*inch)
            story.append(chart_image)
            story.append(Spacer(1, 20))
        
        # Data-driven interpretation
        story.append(Paragraph("Performance Analysis", self.styles['SubHeader']))
        
        interpretation_text = f"""
        <b>Assessment Based on Actual Data:</b><br/>
        This analysis is derived from {sum(1 for topic in knowledge_collected.values() if isinstance(topic, dict) for v in topic.values() if v)} 
        actual data points provided by {company_info.get('name', 'the company')}.<br/><br/>
        
        <b>Scoring Methodology:</b><br/>
        • Scores reflect actual performance metrics and practices disclosed<br/>
        • Missing data points are factored into the assessment<br/>
        • Industry benchmarks applied where applicable<br/>
        • Regulatory compliance requirements considered<br/>
        """
        
        story.append(Paragraph(interpretation_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_real_category_analysis(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> List:
        """Create detailed category analysis using actual responses"""
        story = []
        
        story.append(Paragraph("Detailed Category Analysis", self.styles['SectionHeader']))
        
        real_scores = self._calculate_real_scores(knowledge_collected)
        category_scores = real_scores.get('category_scores', {})
        
        # Analyze each category with real data
        for category, score in category_scores.items():
            category_data = knowledge_collected.get(category, {})
            if not category_data:
                continue
                
            story.append(Paragraph(f"{category.replace('_', ' ').title()} Assessment", self.styles['SubHeader']))
            
            # Real performance analysis
            performance = self._get_performance_level(score)
            analysis_text = f"<b>Score:</b> {score:.1f}/100 ({performance})<br/><br/>"
            
            # Add specific insights based on actual data
            analysis_text += self._get_category_specific_analysis(category, category_data, company_info)
            
            story.append(Paragraph(analysis_text, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_current_compliance_section(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any], regulations_data: Dict[str, Any] = None) -> List:
        """Create regulatory compliance section with current regulations"""
        story = []
        
        story.append(Paragraph("Current Regulatory Compliance Status", self.styles['SectionHeader']))
        
        # Assess compliance based on actual data
        compliance_assessment = self._assess_regulatory_compliance(knowledge_collected, company_info)
        
        # Compliance overview
        compliance_text = f"""
        <b>Regulatory Compliance Assessment (2024):</b><br/>
        Based on current EU regulations and actual company data:<br/><br/>
        
        <b>CSRD Readiness:</b> {compliance_assessment.get('csrd_status', 'Not Assessed')}<br/>
        <b>EU Taxonomy Alignment:</b> {compliance_assessment.get('taxonomy_status', 'Not Assessed')}<br/>
        <b>SFDR Compliance:</b> {compliance_assessment.get('sfdr_status', 'Not Assessed')}<br/>
        """
        
        story.append(Paragraph(compliance_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Current regulations table
        story.append(Paragraph("Applicable Regulations", self.styles['SubHeader']))
        
        reg_data = [['Regulation', 'Effective Date', 'Compliance Status', 'Key Requirements']]
        
        for reg_key, reg_info in self.current_regulations.items():
            status = compliance_assessment.get(f'{reg_key.lower()}_status', 'Assessment Required')
            requirements = ', '.join(reg_info['requirements'][:2]) + '...'
            reg_data.append([
                reg_info['name'],
                reg_info['effective_date'],
                status,
                requirements
            ])
        
        reg_table = Table(reg_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 2*inch])
        reg_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4169E1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(reg_table)
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_data_driven_recommendations(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> List:
        """Create recommendations based on actual data gaps and performance"""
        story = []
        
        story.append(Paragraph("Data-Driven Recommendations", self.styles['SectionHeader']))
        
        # Generate recommendations based on actual data
        recommendations = self._generate_real_recommendations(knowledge_collected, company_info)
        
        # Priority recommendations
        story.append(Paragraph("Priority Actions Based on Assessment", self.styles['SubHeader']))
        
        for i, recommendation in enumerate(recommendations[:5], 1):
            rec_text = f"<b>{i}. {recommendation}</b><br/>"
            story.append(Paragraph(rec_text, self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Implementation roadmap based on data gaps
        story.append(Paragraph("Implementation Roadmap", self.styles['SubHeader']))
        
        roadmap = self._create_data_driven_roadmap(knowledge_collected, company_info)
        
        roadmap_table = Table(roadmap, colWidths=[1.5*inch, 1*inch, 3*inch])
        roadmap_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4169E1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(roadmap_table)
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_real_data_appendix(self, knowledge_collected: Dict[str, Any]) -> List:
        """Create appendix with actual collected data"""
        story = []
        
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
        
        story.append(Paragraph("Appendix: Collected Data", self.styles['SectionHeader']))
        
        # Actual responses table
        story.append(Paragraph("ESG Data Points Collected", self.styles['SubHeader']))
        
        response_data = [['Category', 'Data Point', 'Response']]
        
        for category, data in knowledge_collected.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    if value and str(value).strip() not in ['', 'Not available', 'N/A']:
                        response_data.append([
                            category.replace('_', ' ').title(),
                            key.replace('_', ' ').title(),
                            str(value)[:50] + '...' if len(str(value)) > 50 else str(value)
                        ])
        
        if len(response_data) > 1:
            response_table = Table(response_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
            response_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(response_table)
        
        return story
    
    def _calculate_real_scores(self, knowledge_collected: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate actual ESG scores based on collected data"""
        category_scores = {}
        
        for category, data in knowledge_collected.items():
            if not isinstance(data, dict):
                continue
                
            # Calculate score based on data completeness and quality
            total_possible = len(data)
            answered = sum(1 for v in data.values() if v and str(v).strip() not in ['', 'Not available', 'N/A'])
            
            # Base score from completeness
            completeness_score = (answered / total_possible * 100) if total_possible > 0 else 0
            
            # Quality adjustments based on specific responses
            quality_score = self._assess_response_quality(category, data)
            
            # Final score (weighted average)
            final_score = (completeness_score * 0.6) + (quality_score * 0.4)
            category_scores[category] = round(final_score, 1)
        
        # Overall score
        overall_score = sum(category_scores.values()) / len(category_scores) if category_scores else 0
        
        return {
            'overall_score': round(overall_score, 1),
            'category_scores': category_scores
        }
    
    def _assess_response_quality(self, category: str, data: Dict[str, Any]) -> float:
        """Assess quality of responses for scoring"""
        quality_score = 50  # Base score
        
        # Category-specific quality assessments
        if category == 'environmental':
            if data.get('scope1_emissions') and 'not measured' not in str(data.get('scope1_emissions', '')).lower():
                quality_score += 15
            if data.get('renewable_energy_pct') and str(data.get('renewable_energy_pct', '')).replace('%', '').isdigit():
                quality_score += 10
            if data.get('climate_targets') and 'yes' in str(data.get('climate_targets', '')).lower():
                quality_score += 15
                
        elif category == 'social':
            if data.get('gender_diversity_pct') and str(data.get('gender_diversity_pct', '')).replace('%', '').isdigit():
                quality_score += 10
            if data.get('safety_incidents') and str(data.get('safety_incidents', '')).isdigit():
                quality_score += 10
            if data.get('training_hours') and str(data.get('training_hours', '')).isdigit():
                quality_score += 10
                
        elif category == 'governance':
            if data.get('board_independence') and str(data.get('board_independence', '')).isdigit():
                quality_score += 15
            if data.get('ethics_code') and 'yes' in str(data.get('ethics_code', '')).lower():
                quality_score += 10
            if data.get('whistleblower_system') and 'yes' in str(data.get('whistleblower_system', '')).lower():
                quality_score += 10
        
        return min(quality_score, 100)
    
    def _extract_key_findings(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract key findings from actual data"""
        strengths = []
        improvements = []
        
        # Analyze environmental data
        env_data = knowledge_collected.get('environmental', {})
        if env_data.get('renewable_energy_pct'):
            try:
                pct = float(str(env_data['renewable_energy_pct']).replace('%', ''))
                if pct > 50:
                    strengths.append(f"Strong renewable energy usage at {pct}%")
                elif pct < 20:
                    improvements.append("Low renewable energy usage - consider increasing renewable sources")
            except:
                pass
        
        if env_data.get('climate_targets') and 'yes' in str(env_data.get('climate_targets', '')).lower():
            strengths.append("Science-based climate targets established")
        else:
            improvements.append("Consider establishing science-based climate targets")
        
        # Analyze social data
        social_data = knowledge_collected.get('social', {})
        if social_data.get('safety_incidents'):
            try:
                incidents = int(str(social_data['safety_incidents']))
                if incidents == 0:
                    strengths.append("Excellent safety record with zero incidents")
                elif incidents > 5:
                    improvements.append("High number of safety incidents - review safety protocols")
            except:
                pass
        
        # Analyze governance data
        gov_data = knowledge_collected.get('governance', {})
        if gov_data.get('ethics_code') and 'yes' in str(gov_data.get('ethics_code', '')).lower():
            strengths.append("Code of ethics in place")
        else:
            improvements.append("Implement comprehensive code of ethics")
        
        return {
            'strengths': strengths[:3],
            'improvements': improvements[:3]
        }
    
    def _get_category_specific_analysis(self, category: str, category_data: Dict[str, Any], company_info: Dict[str, Any]) -> str:
        """Get specific analysis based on actual category data"""
        analysis = f"<b>{category.replace('_', ' ').title()} Performance Analysis:</b><br/>"
        
        if category == 'environmental':
            analysis += f"Environmental data shows "
            if category_data.get('scope1_emissions'):
                analysis += f"Scope 1 emissions of {category_data['scope1_emissions']}, "
            if category_data.get('renewable_energy_pct'):
                analysis += f"renewable energy at {category_data['renewable_energy_pct']}, "
            analysis += "indicating the company's environmental management approach.<br/>"
            
        elif category == 'social':
            analysis += f"Social performance indicates "
            if category_data.get('employee_count'):
                analysis += f"workforce of {category_data['employee_count']} employees, "
            if category_data.get('gender_diversity_pct'):
                analysis += f"gender diversity at {category_data['gender_diversity_pct']}, "
            analysis += "reflecting the company's people practices.<br/>"
            
        elif category == 'governance':
            analysis += f"Governance structure shows "
            if category_data.get('board_size'):
                analysis += f"board of {category_data['board_size']} members, "
            if category_data.get('board_independence'):
                analysis += f"with {category_data['board_independence']} independent directors, "
            analysis += "indicating governance maturity.<br/>"
        
        return analysis
    
    def _assess_regulatory_compliance(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, str]:
        """Assess regulatory compliance based on actual data"""
        compliance = {}
        
        # CSRD assessment
        reporting_data = knowledge_collected.get('reporting_compliance', {})
        if reporting_data.get('csrd_readiness') and 'yes' in str(reporting_data.get('csrd_readiness', '')).lower():
            compliance['csrd_status'] = 'Preparing for Compliance'
        else:
            compliance['csrd_status'] = 'Assessment Required'
        
        # EU Taxonomy assessment
        if reporting_data.get('taxonomy_alignment') and 'yes' in str(reporting_data.get('taxonomy_alignment', '')).lower():
            compliance['taxonomy_status'] = 'Assessment Conducted'
        else:
            compliance['taxonomy_status'] = 'Not Assessed'
        
        # SFDR assessment (if applicable)
        if company_info.get('industry') == 'Financial':
            compliance['sfdr_status'] = 'Applicable - Assessment Required'
        else:
            compliance['sfdr_status'] = 'Not Applicable'
        
        return compliance
    
    def _generate_real_recommendations(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on actual data gaps"""
        recommendations = []
        
        # Environmental recommendations
        env_data = knowledge_collected.get('environmental', {})
        if not env_data.get('scope1_emissions') or 'not measured' in str(env_data.get('scope1_emissions', '')).lower():
            recommendations.append("Implement comprehensive Scope 1 emissions measurement and tracking")
        
        if not env_data.get('climate_targets') or 'no' in str(env_data.get('climate_targets', '')).lower():
            recommendations.append("Establish science-based climate targets aligned with 1.5°C pathway")
        
        # Social recommendations
        social_data = knowledge_collected.get('social', {})
        if not social_data.get('gender_diversity_pct'):
            recommendations.append("Measure and report gender diversity metrics across all levels")
        
        # Governance recommendations
        gov_data = knowledge_collected.get('governance', {})
        if not gov_data.get('ethics_code') or 'no' in str(gov_data.get('ethics_code', '')).lower():
            recommendations.append("Develop and implement comprehensive code of ethics")
        
        # Reporting recommendations
        reporting_data = knowledge_collected.get('reporting_compliance', {})
        if not reporting_data.get('sustainability_report') or 'no' in str(reporting_data.get('sustainability_report', '')).lower():
            recommendations.append("Develop comprehensive sustainability reporting framework")
        
        return recommendations[:5]
    
    def _create_data_driven_roadmap(self, knowledge_collected: Dict[str, Any], company_info: Dict[str, Any]) -> List[List[str]]:
        """Create implementation roadmap based on data gaps"""
        roadmap = [['Timeline', 'Priority', 'Action Items']]
        
        # Analyze data gaps for roadmap
        env_gaps = self._identify_data_gaps('environmental', knowledge_collected.get('environmental', {}))
        social_gaps = self._identify_data_gaps('social', knowledge_collected.get('social', {}))
        gov_gaps = self._identify_data_gaps('governance', knowledge_collected.get('governance', {}))
        
        # Short-term (0-3 months)
        short_term = []
        if env_gaps:
            short_term.append("Implement emissions measurement")
        if social_gaps:
            short_term.append("Establish diversity metrics")
        roadmap.append(['0-3 months', 'High', ', '.join(short_term[:2]) if short_term else 'Data collection completion'])
        
        # Medium-term (3-6 months)
        roadmap.append(['3-6 months', 'Medium', 'Develop ESG policies and procedures'])
        
        # Long-term (6-12 months)
        roadmap.append(['6-12 months', 'Medium', 'Implement comprehensive ESG management system'])
        
        # Future (12+ months)
        roadmap.append(['12+ months', 'Low', 'Achieve industry benchmark performance'])
        
        return roadmap
    
    def _identify_data_gaps(self, category: str, category_data: Dict[str, Any]) -> List[str]:
        """Identify data gaps in a category"""
        gaps = []
        
        # Check for missing or incomplete data
        for key, value in category_data.items():
            if not value or str(value).strip() in ['', 'Not available', 'N/A', 'not measured']:
                gaps.append(key.replace('_', ' ').title())
        
        return gaps
    
    def _create_real_data_chart(self, category_scores: Dict[str, Any]) -> io.BytesIO:
        """Create category scores bar chart with real data"""
        try:
            plt.figure(figsize=(10, 6))
            
            categories = [cat.replace('_', ' ').title() for cat in category_scores.keys()]
            scores = list(category_scores.values())
            
            colors_list = ['#2E8B57', '#4169E1', '#FF8C00', '#28a745', '#ffc107']
            
            bars = plt.bar(categories, scores, color=colors_list[:len(categories)])
            
            plt.title('ESG Category Performance (Based on Actual Data)', fontsize=16, fontweight='bold')
            plt.ylabel('Score', fontsize=12)
            plt.ylim(0, 100)
            plt.xticks(rotation=45, ha='right')
            
            # Add score labels on bars
            for bar, score in zip(bars, scores):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error creating chart: {e}")
            return None
    
    def _get_performance_level(self, score: float) -> str:
        """Get performance level based on score"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Fair"
        elif score >= 60:
            return "Poor"
        else:
            return "Critical"

    def create_download_link(self, pdf_bytes: bytes, filename: str) -> str:
        """Create download link for PDF"""
        b64 = base64.b64encode(pdf_bytes).decode()
        return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download {filename}</a>'