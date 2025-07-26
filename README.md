# 🌱 SustainPilot

**Agentic ESG Assessment Tool with Real-time Regulation Updates**

*Hackathon - Power of Europe*

## Overview

The ESG Report Generator is an intelligent, agentic system that provides comprehensive Environmental, Social, and Governance (ESG) assessments for companies. It uses AI agents to automatically update ESG regulations, search for current best practices, and generate professional PDF reports with actionable insights.

## 🚀 Key Features

### Agentic AI System
- **Search Agent**: Real-time ESG regulation updates and industry research
- **Regulations Agent**: Monitors compliance requirements and regulatory changes
- **Knowledge Manager**: Dynamically updates question bank based on current standards
- **Agent Orchestrator**: Coordinates all agents for seamless operation

### Interactive Assessment
- **Chatbot Interface**: Conversational ESG assessment experience
- **Dynamic Questions**: Questions adapt based on industry, region, and company size
- **Progress Tracking**: Real-time progress monitoring with category breakdown
- **Smart Follow-ups**: Context-aware follow-up questions

### Professional Reporting
- **PDF Generation**: Professional reports with charts and visualizations
- **Compliance Analysis**: Current regulatory compliance status
- **Industry Benchmarking**: Performance comparison against industry standards
- **Actionable Recommendations**: Prioritized improvement suggestions

### Real-time Updates
- **Regulation Monitoring**: Automatic tracking of ESG regulation changes
- **Standards Updates**: Latest GRI, SASB, TCFD framework updates
- **Industry Insights**: Current ESG trends and best practices

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Search Agent  │    │Regulations Agent│    │Knowledge Manager│
│                 │    │                 │    │                 │
│ • ESG Research  │    │ • Compliance    │    │ • Question Bank │
│ • Benchmarking  │    │ • Reg Updates   │    │ • Dynamic Updates│
│ • News Tracking │    │ • Risk Analysis │    │ • Relevance Score│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │Agent Orchestrator│
                    │                 │
                    │ • Coordination  │
                    │ • Task Routing  │
                    │ • Data Fusion   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Streamlit App   │
                    │                 │
                    │ • Chat Interface│
                    │ • Progress Track│
                    │ • PDF Reports   │
                    └─────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Setup Instructions

**Option 1: Automated Installation (Recommended)**
```bash
python install.py
```

**Option 2: Manual Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd esg-report
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # For full features:
   pip install -r requirements.txt
   
   # Or for minimal installation:
   pip install -r requirements-minimal.txt
   ```

4. **Configure Mistral AI (optional)**
   ```bash
   cp .env.example .env
   # Edit .env and add your Mistral API key:
   # MISTRAL_API_KEY=your_mistral_api_key_here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run app.py
   ```

### Troubleshooting Installation

If you encounter dependency issues:

1. **Use minimal requirements**:
   ```bash
   pip install -r requirements-minimal.txt
   ```

2. **Install dependencies individually**:
   ```bash
   pip install streamlit pandas plotly matplotlib reportlab pillow
   pip install python-dotenv pydantic requests PyPDF2 python-docx
   # Optional: pip install mistralai
   ```

3. **Skip problematic packages**: The system will work with fallbacks for optional dependencies.

## 🎯 Usage

### Starting an Assessment

1. **Company Information**: Enter your company details (name, industry, region, size)
2. **Agent Initialization**: AI agents automatically initialize and update their knowledge
3. **Interactive Assessment**: Answer ESG questions through the chat interface
4. **Real-time Insights**: Receive immediate feedback and context-aware follow-ups
5. **Report Generation**: Generate and download comprehensive PDF reports

### Assessment Flow

```
Company Info → Agent Setup → Dynamic Questions → AI Analysis → PDF Report
     ↓              ↓              ↓              ↓           ↓
  Basic Info    Regulations    Tailored Q&A    Insights   Download
  Industry      Standards      Progress        Scoring    Professional
  Region        Benchmarks     Tracking        Analysis   Report
```

## 🤖 Agent System

### Search Agent
- **Real-time Research**: Searches for latest ESG trends and regulations
- **Industry Benchmarking**: Gathers competitive ESG performance data
- **News Integration**: Monitors ESG-related news and regulatory updates
- **Best Practices**: Identifies current industry best practices

### Regulations Agent
- **Compliance Monitoring**: Tracks SEC, EU, UK, and other regulatory changes
- **Risk Assessment**: Evaluates compliance gaps and risks
- **Framework Updates**: Monitors GRI, SASB, TCFD standard changes
- **Penalty Analysis**: Assesses potential compliance penalties

### Knowledge Manager
- **Dynamic Questions**: Updates question bank based on current regulations
- **Relevance Scoring**: Prioritizes questions by importance and context
- **Context Adaptation**: Tailors questions to industry and region
- **Version Control**: Maintains question bank versioning

### Agent Orchestrator
- **Task Coordination**: Manages agent interactions and data flow
- **Background Updates**: Schedules automatic knowledge updates
- **Health Monitoring**: Tracks agent performance and errors
- **Data Fusion**: Combines insights from multiple agents

## 📊 Report Features

### Executive Summary
- Overall ESG score and performance level
- Category breakdown (Environmental, Social, Governance)
- Key findings and compliance status

### Detailed Analysis
- **Environmental**: Carbon emissions, energy, water, waste management
- **Social**: Employee relations, diversity, community impact, human rights
- **Governance**: Board structure, ethics, risk management, transparency

### Compliance Assessment
- Current regulatory compliance status
- High-risk compliance areas
- Required actions and timelines

### Strategic Recommendations
- Priority actions with timelines
- Implementation roadmap
- Industry-specific guidance

## 🔧 Configuration

### Environment Variables
```bash
# LLM Configuration
LLM_PROVIDER=mock  # Change to 'openai' or 'anthropic' for real LLM
LLM_API_KEY=your_api_key_here

# Agent Settings
ENABLE_AGENTS=True
UPDATE_INTERVAL_HOURS=24

# Search Configuration
SEARCH_API_KEY=your_search_api_key_here
```

### Customization Options
- **Question Bank**: Modify questions in `src/agents/knowledge_manager.py`
- **Regulations**: Update regulatory sources in `src/config.py`
- **Styling**: Customize UI in the CSS section of `app.py`
- **Report Template**: Modify PDF layout in `src/report_generator.py`

## 🧪 Development

### Project Structure
```
esg-report/
├── src/
│   ├── agents/
│   │   ├── base_agent.py          # Base agent class
│   │   ├── search_agent.py        # Search and research agent
│   │   ├── regulations_agent.py   # Compliance monitoring agent
│   │   ├── knowledge_manager.py   # Question bank management
│   │   └── orchestrator.py        # Agent coordination
│   ├── config.py                  # Configuration settings
│   └── report_generator.py        # PDF report generation
├── app.py                         # Main Streamlit application
├── main.py                        # Entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### Adding New Agents
1. Extend `BaseAgent` class
2. Implement `execute()` method
3. Register with orchestrator
4. Add configuration options

### Extending Question Bank
1. Modify `knowledge_manager.py`
2. Add new categories/subcategories
3. Include regulation references
4. Set appropriate weights

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Production Deployment
- **Streamlit Cloud**: Deploy directly from GitHub
- **Docker**: Use provided Dockerfile (if available)
- **Cloud Platforms**: Deploy to AWS, GCP, or Azure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is developed for the "Power of Europe" Hackathon.

## 🆘 Support

For questions or issues:
1. Check the documentation above
2. Review the code comments
3. Create an issue in the repository

## 🔮 Future Enhancements

- **Real LLM Integration**: Replace mock LLM with OpenAI/Anthropic
- **Advanced Analytics**: Machine learning-based ESG scoring
- **Multi-language Support**: Internationalization
- **API Integration**: Connect to real regulatory databases
- **Collaborative Features**: Multi-user assessments
- **Advanced Visualizations**: Interactive dashboards

---

**Built with ❤️ for sustainable business practices**
