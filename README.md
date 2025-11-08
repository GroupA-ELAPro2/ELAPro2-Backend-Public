# IELTS Essay Evaluator Backend

A sophisticated AI-powered backend system for automated IELTS essay evaluation using multiple specialised agents and LangGraph orchestration. This project provides comprehensive essay assessment across all four IELTS writing criteria with detailed feedback and gap analysis.

## 🎯 Overview

The IELTS Essay Evaluator is a multi-agent system that evaluates IELTS essays using specialised AI agents, each focusing on specific assessment criteria. The system provides detailed scoring, feedback, and actionable improvement suggestions aligned with official IELTS band descriptors.

## ✨ Features

### Multi-Agent Evaluation System
- **Grammar Agent**: Evaluates grammatical range and accuracy
- **Lexical Agent**: Assesses lexical resource and vocabulary usage
- **Task Agent**: Analyses task achievement and response quality
- **Coherence Agent**: Evaluates coherence and cohesion
- **Meta-Evaluation Agent**: Provides quality assessment of the evaluation process
- **Gap Analysis Agent**: Generates targeted improvement recommendations

### Key Capabilities
- **Comprehensive Scoring**: Band scores (0-9) for all four IELTS criteria
- **Detailed Feedback**: Specific comments and suggestions for each criterion
- **Gap Analysis**: Identifies weak areas and provides improvement plans
- **Image Description**: Handles visual prompts for Task 1 essays
- **Multiple Essay Types**: Supports both Academic and General Training modules
- **Target Band Alignment**: Customisable target band scoring

## 🏗️ Architecture

### Technology Stack
- **Framework**: FastAPI for REST API
- **AI Orchestration**: LangGraph for multi-agent workflows
- **Language Models**: Google Gemini AI
- **Data Validation**: Pydantic for type safety
- **Testing**: unittest with FastAPI TestClient

## 🔑 Access
Access to the backend evaluator is available via use of a valid API key.


### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───>│  Central Agent   │───>│  Specialised    │
│   (main.py)     │    │  (Orchestrator)  │    │  Agents         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Assessment      │
                       │  Tools &         │
                       │  Descriptors     │
                       └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Backend-main
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```python
   GEMINI_API_KEY="your_gemini_api_key_here"
   OPENAI_API_KEY="your_open_api_key_here"
   LANGSMITH_API_KEY="your_langsmith_api_key_here" #For llm monitoring
   LANGSMITH_PROJECT="langsmith project name" #name to group monitoring traces
   LANGSMITH_TRACING_V2=true #Turn langsmith monitoring on/off
   GRAMMAR_MODEL="chosen llm model" #e.g gemini-2.0-flash-lite
   LEXICAL_MODEL="chosen llm model" #e.g gemini-2.0-flash-lite
   TASK_MODEL="chosen llm model" #e.g gemini-2.0-flash-lite
   COHERENCE_MODEL="chosen llm model" #e.g gemini-2.0-flash-lite
   IMAGE_MODEL="chosen llm model" #for image processing
   EVAL_MODEL="chosen llm model" #e.g gemini-2.0-flash-lite
   EVAL_MONITORING=false #Turn on for agent meta evaluations
   OVERALL_MODEL="chosen llm model" #e.g gemini-2.0-flash-lite
   ELA_ENV="PROD" #The identifier for the environment to be shown when connecting to the front-end
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Endpoints

#### `POST /process_essay/`
Evaluates an IELTS essay and returns comprehensive feedback.

**Example Request Body:**
```json
{
  "track_id": "unique_identifier",
  "question": "IELTS essay question",
  "essay": "Student's essay text",
  "essay_type": 2,
  "target_band": 7,
  "image_url": "optional_image_url",
  "image_description": "optional_image_description"
}
```

**Essay Types:**
- `1`: General Writing Task 1
- `2`: General Writing Task 2
- `3`: Academic Writing Task 1
- `4`: Academic Writing Task 2

**Response Body:**
```json
{
  "data": {
    "track_id": "unique_identifier",
    "grammar_score": 7,
    "coherence_score": 6,
    "lexical_score": 7,
    "task_score": 6,
    "grammar_comment": "Detailed feedback...",
    "coherence_comment": "Detailed feedback...",
    "lexical_comment": "Detailed feedback...",
    "task_comment": "Detailed feedback...",
    "overall_feedback": "Comprehensive improvement plan...",
    "image_description": "Description if applicable"
  }
}
```

#### `GET /`
Health check endpoint returning service status.

### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## 🧪 Testing

Run the test suite:
```bash
python -m unittest tests/
```

Or run specific test files:
```bash
python -m unittest tests/test_fastapi.py
python -m unittest tests/test_grammar.py
```

## 📁 Project Structure

```
Backend-main/
├── agent_files/              # Multi-agent system components
│   ├── central_agent.py      # Main orchestration logic
│   ├── agent_states.py       # Pydantic models for data validation
│   ├── grammar_agent.py      # Grammar evaluation agent
│   ├── lexical_agent.py      # Vocabulary evaluation agent
│   ├── task_agent.py         # Task achievement agent
│   ├── coherence_agent.py    # Coherence evaluation agent
│   ├── eval_agent.py         # Meta-evaluation agent
│   ├── gap_analysis_agent.py # Improvement recommendations
│   └── image_description_agent.py #Image description generator
├── app/                      # FastAPI application
│   ├── main.py              # API endpoints and configuration
│   └── tools/               # Assessment tools and descriptors
│       ├── tools.py         # Tool definitions
│       ├── band_descriptor_tool.py
│       ├── key_assessment_criteria_tool.py
│       ├── prompt_templates.py #llm prompts for injection
│       └── *.json           # IELTS descriptors and criteria
├── tests/                    # Test suite
├── requirements.txt         # Python dependencies
├── render.yaml              # Deployment configuration
└── LICENSE                  # MIT License
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for Google Gemini AI access
- `GRAMMAR_MODEL`: Model for grammar evaluation (default: gemini-1.5-flash)
- `LEXICAL_MODEL`: Model for lexical evaluation
- `TASK_MODEL`: Model for task achievement evaluation
- `COHERENCE_MODEL`: Model for coherence evaluation
- `META_EVAL_MODEL`: Model for meta-evaluation
- `GAP_ANALYSIS_MODEL`: Model for gap analysis
- `ELA_ENV`: Environment identifier (development/production)

### Model Configuration
The system uses Google Gemini models for all evaluations. You can configure different models for different agents based on your requirements and API quotas.

## 🚀 Deployment

### Render Deployment
The project includes `render.yaml` for easy deployment on Render.com:

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy using the provided configuration

### Manual Deployment
1. Set up production environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run with production WSGI server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏫 Academic Context

This project was developed as part of the Capstone Project for UNISA SP4 and SP6/2025, representing Group A's contribution to the ELA Pro 2.0 enhanced system.


---

**Note**: This system is designed for educational and research purposes. Ensure compliance with IELTS testing policies when using in production environments.