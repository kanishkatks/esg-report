"""
Configuration settings for the ESG Report Generation Tool
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # App Settings
    APP_NAME = "ESG Report Generator"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # LLM Settings (Mock for now)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    
    # Agent Settings
    ENABLE_AGENTS = os.getenv("ENABLE_AGENTS", "True").lower() == "true"
    SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")
    UPDATE_INTERVAL_HOURS = int(os.getenv("UPDATE_INTERVAL_HOURS", "24"))
    
    # Database Settings
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vectordb")
    KNOWLEDGE_DB_PATH = os.getenv("KNOWLEDGE_DB_PATH", "./data/knowledge.json")
    
    # Report Settings
    REPORT_TEMPLATE_PATH = "./templates/report_template.html"
    COMPANY_LOGO_PATH = "./assets/logo.png"
    
    # ESG Categories and Weights
    ESG_CATEGORIES = {
        "Environmental": {
            "weight": 0.4,
            "subcategories": [
                "Carbon Emissions",
                "Energy Management",
                "Water Usage",
                "Waste Management",
                "Biodiversity"
            ]
        },
        "Social": {
            "weight": 0.35,
            "subcategories": [
                "Employee Relations",
                "Diversity & Inclusion",
                "Community Impact",
                "Product Safety",
                "Human Rights"
            ]
        },
        "Governance": {
            "weight": 0.25,
            "subcategories": [
                "Board Structure",
                "Executive Compensation",
                "Business Ethics",
                "Data Privacy",
                "Risk Management"
            ]
        }
    }
    
    # Regulatory Sources
    REGULATORY_SOURCES = [
        {
            "name": "SEC ESG Disclosure",
            "url": "https://www.sec.gov/rules/proposed/2022/33-11042.pdf",
            "type": "regulation"
        },
        {
            "name": "EU Taxonomy",
            "url": "https://ec.europa.eu/info/business-economy-euro/banking-and-finance/sustainable-finance/eu-taxonomy-sustainable-activities_en",
            "type": "framework"
        },
        {
            "name": "GRI Standards",
            "url": "https://www.globalreporting.org/standards/",
            "type": "standard"
        },
        {
            "name": "SASB Standards",
            "url": "https://www.sasb.org/standards/",
            "type": "standard"
        }
    ]
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }