# SEQ_SONIC - AI-Powered Sequence Analysis Platform

## 🚀 Overview

SEQ_SONIC is an AI-powered platform for analyzing, comparing, and migrating integration sequences between middleware technologies, focusing on Apache Camel to WSO2 transformations. It features three specialized AI agents built with LangGraph and FastAPI.

## 🏗️ Architecture

### System Components
- **Frontend**: Chainlit-based conversational UI
- **Backend**: FastAPI with streaming responses
- **Agents**: Three specialized LangGraph agents
- **Persistence**: MongoDB for conversation state
- **Deployment**: Docker containerized services

### Agent Flow
```
User Input → Chainlit UI → FastAPI Backend → Agent Selection → 
LangGraph Processing → Tool Execution → Streaming Response
```

## 🤖 AI Agents

### 1. Sonic Agent 🚀
- **Purpose**: General-purpose AI assistant
- **Features**: Fast responses, conversational AI
- **Use Cases**: Quick queries, basic assistance

### 2. Smart WSO2 Assistant ⚡
- **Purpose**: WSO2 platform specialist
- **Tools**:
  - `java_analyzer_tool`: Analyze Camel/MyBatis code
  - `sequence_analyzer_tool`: Analyze WSO2 XML
  - `code_comparator_tool`: Compare platforms
  - `edit_code_tool`: Refine WSO2 configurations
  - `review_code_tool`: Check WSO2 6.0.0 compatibility
- **Workflow**: Analysis → Comparison → Refinement → Validation

### 3. MW Migration Agent 🔄
- **Purpose**: Apache Camel to WSO2 migration
- **Tools**:
  - `generate_wso2_request_sequence`: Convert request flows
  - `generate_wso2_response_sequence`: Convert response flows  
  - `generate_wso2_dataservice`: Create data services
- **Process**: Source Analysis → Dependency Mapping → Transformation → Validation

## 🔧 Technical Stack

**Backend**: FastAPI, LangGraph, LangChain, MongoDB, Pydantic
**Frontend**: Chainlit, Aiohttp, Server-Sent Events
**AI/ML**: OpenAI GPT, LangSmith tracing, Tool calling
**Deployment**: Docker, Docker Compose, Nginx

## 📁 Project Structure

```
SEQ_SONIC/
├── src/
│   ├── Agents/                    # AI Agent implementations
│   │   ├── sonic/                # General agent
│   │   ├── smart_wso2_assistant/ # WSO2 specialist
│   │   ├── mw_migration/         # Migration specialist
│   │   └── runtime.py           # Agent management
│   ├── Backend/routes/          # FastAPI endpoints
│   ├── Frontend/app.py          # Chainlit UI
│   └── config/                  # Configuration
├── Docker/                      # Container setup
└── main.py                     # Application entry point
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key
- Environment variables in `.env`

### Run Application
```bash
cd Docker
docker-compose up -d
```

### Access Points
- **Frontend**: http://localhost:8001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB UI**: http://localhost:8081

## 🔑 Key Features

### Multi-Agent Architecture
- Dynamic agent selection during conversation
- Persistent sessions with MongoDB
- Specialized tools per agent
- Async processing for performance

### Advanced Capabilities
- File upload and processing
- Real-time streaming responses
- Cross-platform code analysis
- WSO2 6.0.0 compatibility checking
- Step-by-step migration guidance

### Enterprise Features
- Container-based deployment
- Health monitoring
- Session management
- Error handling and recovery

## 🎯 Use Cases

### Integration Developers
- Convert Apache Camel routes to WSO2
- Validate WSO2 compatibility
- Analyze integration patterns

### Enterprise Architects  
- Plan migration strategies
- Compare integration platforms
- Assess migration risks

### Development Teams
- Learn WSO2/Camel patterns
- Review code quality
- Troubleshoot issues

## 🐳 Docker Services

- **backend**: FastAPI app (port 8000)
- **frontend**: Chainlit UI (port 8001)  
- **mongo**: Database (port 27017)
- **mongo-express**: DB admin (port 8081)
- **nginx**: Reverse proxy (port 80, production only)

## 📊 Application Flow

### Main Processing Flow
1. User sends message via Chainlit UI
2. Frontend streams to FastAPI backend
3. Backend selects appropriate agent
4. Agent processes with LangGraph workflow
5. Tools execute if needed
6. Response streams back to UI
7. Conversation state saved to MongoDB

### Agent-Specific Flows

**WSO2 Assistant**: Code Upload → Analysis → Comparison → Fixes → Validation
**MW Migration**: Camel Code → Dependency Analysis → WSO2 Generation → Testing
**Sonic Agent**: Query → LLM Processing → Direct Response

## ⚙️ Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_key
MONGODB_URI=mongodb://mongo:27017
MONGODB_DB_NAME=seq_sonic
LANGCHAIN_API_KEY=your_key
LANGCHAIN_TRACING_V2=true
```

### Agent Selection
Agents are selected via the Chainlit UI settings panel and can be switched during conversation without losing context.

---

*SEQ_SONIC - Empowering Enterprise Integration Through AI*