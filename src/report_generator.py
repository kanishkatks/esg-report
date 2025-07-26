"""
ESG Report Generator with PDF export functionality
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


class ESGReportGenerator:
    """Generate comprehensive ESG reports with charts and professional styling"""
    
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
                       user_responses: Dict[str, Any], 
                       insights: Dict[str, Any]) -> bytes:
        """Generate complete ESG report as PDF"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build report content
        story = []
        
        # Title page
        story.extend(self._create_title_page(company_info))
        
        # Executive summary
        story.extend(self._create_executive_summary(insights, company_info))
        
        # ESG scores and charts
        story.extend(self._create_scores_section(insights))
        
        # Category analysis
        story.extend(self._create_category_analysis(insights, user_responses))
        
        # Compliance status
        story.extend(self._create_compliance_section(assessment_data))
        
        # Recommendations
        story.extend(self._create_recommendations_section(insights))
        
        # Appendix
        story.extend(self._create_appendix(user_responses, assessment_data))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _create_title_page(self, company_info: Dict[str, Any]) -> List:
        """Create report title page"""
        story = []
        
        # Title
        title = Paragraph(f"ESG Assessment Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Company name
        company_title = Paragraph(f"<b>{company_info.get('name', 'Company Name')}</b>", 
                                 self.styles['Heading1'])
        story.append(company_title)
        story.append(Spacer(1, 30))
        
        # Company details table
        company_data = [
            ['Industry:', company_info.get('industry', 'N/A')],
            ['Region:', company_info.get('region', 'N/A')],
            ['Company Size:', company_info.get('size', 'N/A')],
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
        
        # Disclaimer
        disclaimer = Paragraph(
            "<i>This report provides an assessment of Environmental, Social, and Governance (ESG) "
            "practices based on the information provided. It includes analysis of current performance, "
            "regulatory compliance status, and recommendations for improvement.</i>",
            self.styles['Normal']
        )
        story.append(disclaimer)
        
        # Page break
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
        
        return story
    
    def _create_executive_summary(self, insights: Dict[str, Any], company_info: Dict[str, Any]) -> List:
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        analysis = insights.get('insights', {})
        overall_score = analysis.get('overall_score', 75)
        
        # Summary paragraph
        summary_text = f"""
        {company_info.get('name', 'The company')} has achieved an overall ESG score of {overall_score}/100 
        in this comprehensive assessment. This evaluation covers Environmental, Social, and Governance 
        factors based on current regulatory requirements and industry best practices.
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Key metrics table
        category_scores = analysis.get('category_scores', {})
        metrics_data = [['Category', 'Score', 'Performance Level']]
        
        for category, score in category_scores.items():
            performance = self._get_performance_level(score)
            metrics_data.append([category, f"{score}/100", performance])
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 2*inch])
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
        
        # Key findings
        story.append(Paragraph("Key Findings", self.styles['SubHeader']))
        
        strengths = analysis.get('strengths', [])[:3]
        improvements = analysis.get('improvements', [])[:3]
        
        findings_text = "<b>Strengths:</b><br/>"
        for strength in strengths:
            findings_text += f"• {strength}<br/>"
        
        findings_text += "<br/><b>Areas for Improvement:</b><br/>"
        for improvement in improvements:
            findings_text += f"• {improvement}<br/>"
        
        story.append(Paragraph(findings_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_scores_section(self, insights: Dict[str, Any]) -> List:
        """Create ESG scores section with charts"""
        story = []
        
        story.append(Paragraph("ESG Performance Analysis", self.styles['SectionHeader']))
        
        analysis = insights.get('insights', {})
        category_scores = analysis.get('category_scores', {})
        
        # Create bar chart for category scores
        chart_buffer = self._create_category_chart(category_scores)
        if chart_buffer:
            chart_image = Image(chart_buffer, width=5*inch, height=3*inch)
            story.append(chart_image)
            story.append(Spacer(1, 20))
        
        # Score interpretation
        story.append(Paragraph("Score Interpretation", self.styles['SubHeader']))
        
        interpretation_text = """
        <b>Scoring Scale:</b><br/>
        • 90-100: Excellent - Industry leading performance<br/>
        • 80-89: Good - Above average performance<br/>
        • 70-79: Fair - Average performance with room for improvement<br/>
        • 60-69: Poor - Below average, immediate attention needed<br/>
        • Below 60: Critical - Significant gaps requiring urgent action<br/>
        """
        
        story.append(Paragraph(interpretation_text, self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_category_analysis(self, insights: Dict[str, Any], user_responses: Dict[str, Any]) -> List:
        """Create detailed category analysis"""
        story = []
        
        story.append(Paragraph("Detailed Category Analysis", self.styles['SectionHeader']))
        
        analysis = insights.get('insights', {})
        category_scores = analysis.get('category_scores', {})
        
        # Group responses by category
        category_responses = {}
        for response_id, response_data in user_responses.items():
            category = response_data.get('category', 'Other')
            if category not in category_responses:
                category_responses[category] = []
            category_responses[category].append(response_data)
        
        # Analyze each category
        for category, score in category_scores.items():
            story.append(Paragraph(f"{category} Assessment", self.styles['SubHeader']))
            
            # Category score and performance
            performance = self._get_performance_level(score)
            score_text = f"<b>Score:</b> {score}/100 ({performance})<br/><br/>"
            
            # Category-specific insights
            if category == "Environmental":
                score_text += self._get_environmental_insights(category_responses.get(category, []))
            elif category == "Social":
                score_text += self._get_social_insights(category_responses.get(category, []))
            elif category == "Governance":
                score_text += self._get_governance_insights(category_responses.get(category, []))
            
            story.append(Paragraph(score_text, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_compliance_section(self, assessment_data: Dict[str, Any]) -> List:
        """Create regulatory compliance section"""
        story = []
        
        story.append(Paragraph("Regulatory Compliance Status", self.styles['SectionHeader']))
        
        compliance_data = assessment_data.get('compliance_status', {})
        overall_score = compliance_data.get('overall_compliance_score', 75)
        
        # Compliance overview
        compliance_text = f"""
        <b>Overall Compliance Score:</b> {overall_score:.1f}/100<br/>
        <b>Compliant Regulations:</b> {compliance_data.get('compliant_count', 0)}<br/>
        <b>Non-compliant Regulations:</b> {compliance_data.get('non_compliant_count', 0)}<br/>
        <b>Partial Compliance:</b> {compliance_data.get('partial_compliance_count', 0)}<br/>
        """
        
        story.append(Paragraph(compliance_text, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # High-risk regulations
        high_risk_regs = compliance_data.get('high_risk_regulations', [])
        if high_risk_regs:
            story.append(Paragraph("High-Risk Compliance Areas", self.styles['SubHeader']))
            
            risk_text = "The following regulations require immediate attention:<br/><br/>"
            for reg in high_risk_regs[:5]:
                risk_text += f"• {reg}<br/>"
            
            story.append(Paragraph(risk_text, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_recommendations_section(self, insights: Dict[str, Any]) -> List:
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("Strategic Recommendations", self.styles['SectionHeader']))
        
        analysis = insights.get('insights', {})
        recommendations = analysis.get('recommendations', [])
        
        # Priority recommendations
        story.append(Paragraph("Priority Actions", self.styles['SubHeader']))
        
        for i, recommendation in enumerate(recommendations[:5], 1):
            rec_text = f"<b>{i}. {recommendation}</b><br/>"
            story.append(Paragraph(rec_text, self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Implementation roadmap
        story.append(Paragraph("Implementation Roadmap", self.styles['SubHeader']))
        
        roadmap_data = [
            ['Timeline', 'Priority', 'Action Items'],
            ['0-3 months', 'High', 'Address critical compliance gaps'],
            ['3-6 months', 'Medium', 'Implement governance improvements'],
            ['6-12 months', 'Medium', 'Develop comprehensive ESG strategy'],
            ['12+ months', 'Low', 'Achieve industry benchmark performance']
        ]
        
        roadmap_table = Table(roadmap_data, colWidths=[1.5*inch, 1*inch, 3*inch])
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
    
    def _create_appendix(self, user_responses: Dict[str, Any], assessment_data: Dict[str, Any]) -> List:
        """Create appendix with detailed data"""
        story = []
        
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
        
        story.append(Paragraph("Appendix", self.styles['SectionHeader']))
        
        # Assessment questions and responses
        story.append(Paragraph("Assessment Responses", self.styles['SubHeader']))
        
        response_data = [['Question', 'Category', 'Response']]
        
        for response_id, response in user_responses.items():
            question = response.get('question', 'N/A')[:50] + '...' if len(response.get('question', '')) > 50 else response.get('question', 'N/A')
            category = response.get('category', 'N/A')
            answer = str(response.get('answer', 'N/A'))[:30] + '...' if len(str(response.get('answer', ''))) > 30 else str(response.get('answer', 'N/A'))
            
            response_data.append([question, category, answer])
        
        if len(response_data) > 1:
            response_table = Table(response_data, colWidths=[3*inch, 1.5*inch, 2*inch])
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
    
    def _create_category_chart(self, category_scores: Dict[str, Any]) -> io.BytesIO:
        """Create category scores bar chart"""
        try:
            plt.figure(figsize=(10, 6))
            
            categories = list(category_scores.keys())
            scores = list(category_scores.values())
            
            colors_list = ['#2E8B57', '#4169E1', '#FF8C00']
            
            bars = plt.bar(categories, scores, color=colors_list[:len(categories)])
            
            plt.title('ESG Category Scores', fontsize=16, fontweight='bold')
            plt.ylabel('Score', fontsize=12)
            plt.ylim(0, 100)
            
            # Add score labels on bars
            for bar, score in zip(bars, scores):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{score}', ha='center', va='bottom', fontweight='bold')
            
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
    
    def _get_environmental_insights(self, responses: List[Dict[str, Any]]) -> str:
        """Get environmental category insights"""
        insights = """
        <b>Environmental Performance Analysis:</b><br/>
        Your environmental assessment covers key areas including carbon emissions, 
        energy management, water usage, and waste management. Focus areas for improvement 
        include implementing comprehensive emissions tracking and setting science-based targets.
        """
        return insights
    
    def _get_social_insights(self, responses: List[Dict[str, Any]]) -> str:
        """Get social category insights"""
        insights = """
        <b>Social Performance Analysis:</b><br/>
        Your social assessment evaluates employee relations, diversity & inclusion, 
        community impact, and human rights practices. Key opportunities include 
        enhancing diversity programs and strengthening community engagement initiatives.
        """
        return insights
    
    def _get_governance_insights(self, responses: List[Dict[str, Any]]) -> str:
        """Get governance category insights"""
        insights = """
        <b>Governance Performance Analysis:</b><br/>
        Your governance assessment covers board structure, business ethics, risk management, 
        and transparency practices. Priority areas include strengthening board independence 
        and enhancing ESG oversight capabilities.
        """
        return insights

    def create_download_link(self, pdf_bytes: bytes, filename: str) -> str:
        """Create download link for PDF"""
        b64 = base64.b64encode(pdf_bytes).decode()
        return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download {filename}</a>'