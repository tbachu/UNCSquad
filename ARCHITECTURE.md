# Architecture Overview

HIA (Health Insights Agent) is built with a modular, agentic architecture that enables intelligent health data analysis and personalized insights.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                       │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Streamlit Web  │  │   CLI Tool   │  │   Mobile App     │  │
│  │   Interface     │  │   (Future)   │  │   (Future)       │  │
│  └────────┬────────┘  └──────┬───────┘  └─────────┬────────┘  │
└───────────┼───────────────────┼────────────────────┼───────────┘
            │                   │                     │
            └───────────────────┴─────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                          Agent Core                              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Health Agent Orchestrator              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │  │
│  │  │   Planner   │  │  Executor   │  │  Memory Store  │  │  │
│  │  │             │  │             │  │                │  │  │
│  │  │ - ReAct     │  │ - Task      │  │ - ChromaDB     │  │  │
│  │  │ - Task      │  │   Runner    │  │ - SQLite       │  │  │
│  │  │   Decomp.   │  │ - Tool      │  │ - Embeddings   │  │  │
│  │  └─────────────┘  │   Caller    │  └────────────────┘  │  │
│  │                    └─────────────┘                       │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Tools & APIs Layer                       │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐   │
│  │ Gemini API   │  │ Health APIs   │  │ Document Parser  │   │
│  │              │  │               │  │                  │   │
│  │ - Text       │  │ - Drug Inter. │  │ - PDF Extract    │   │
│  │ - Vision     │  │ - FDA Data    │  │ - OCR (Images)   │   │
│  │ - Multimodal │  │ - Lab Ranges  │  │ - Text Process   │   │
│  └──────────────┘  └───────────────┘  └──────────────────┘   │
│                                                                 │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐   │
│  │ Visualizer   │  │ Security Mgr  │  │ Analysis Tools   │   │
│  │              │  │               │  │                  │   │
│  │ - Charts     │  │ - Encryption  │  │ - Lab Extract    │   │
│  │ - Reports    │  │ - Auth        │  │ - Trend Calc     │   │
│  │ - Dashboards │  │ - Audit       │  │ - Health Score   │   │
│  └──────────────┘  └───────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Data Storage Layer                         │
│  ┌────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │  Vector Store  │  │ Relational DB   │  │  File Storage  │  │
│  │  (ChromaDB)    │  │   (SQLite)      │  │                │  │
│  │                │  │                 │  │                │  │
│  │ - Documents    │  │ - Metrics       │  │ - Encrypted    │  │
│  │ - Insights     │  │ - Medications   │  │   Documents    │  │
│  │ - Embeddings   │  │ - Preferences   │  │ - Reports      │  │
│  └────────────────┘  └─────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. **User Interface**
- **Streamlit Web App**: Primary interface for users to interact with HIA
- **Future CLI**: Command-line interface for power users
- **Future Mobile**: Mobile application for on-the-go access

### 2. **Agent Core**
The brain of HIA, consisting of three main components:

#### **Planner**
- Uses ReAct (Reasoning + Acting) pattern
- Decomposes user requests into actionable tasks
- Prioritizes and sequences tasks based on dependencies
- Identifies required tools and data sources

#### **Executor**
- Executes tasks planned by the Planner
- Manages tool calls to Gemini API and other services
- Handles error recovery and retries
- Aggregates results from multiple sources

#### **Memory Store**
- **Vector Store (ChromaDB)**: Stores document embeddings and insights for semantic search
- **Relational DB (SQLite)**: Stores structured health metrics, medications, and user preferences
- Maintains conversation context and historical analysis

### 3. **Tools / APIs**

#### **Google Gemini API**
- Text analysis for medical document understanding
- Vision capabilities for image/PDF processing
- Multimodal analysis for complex documents
- Natural language Q&A and explanations

#### **Health APIs**
- Drug interaction checking (RxNav)
- FDA medication information
- Lab reference ranges
- Vaccine recommendations

#### **Document Parser**
- PDF text extraction
- OCR for scanned documents
- Medical value extraction
- Section identification

#### **Analysis Tools**
- Lab value extraction and normalization
- Trend calculation and pattern detection
- Health score computation
- Recommendation generation

### 4. **Observability**
- Comprehensive logging at each step
- Task execution tracking
- Error handling and recovery
- Audit trails for security compliance

## Data Flow

1. **User Input** → UI receives query/document
2. **Planning** → Planner analyzes request and creates task plan
3. **Execution** → Executor runs tasks using appropriate tools
4. **Processing** → Tools process data (OCR, API calls, analysis)
5. **Storage** → Results stored in memory for future reference
6. **Response** → Formatted insights returned to user

## Security Architecture

- **End-to-end encryption** for sensitive health data
- **Session management** with timeout controls
- **Audit logging** for all data access
- **Secure file storage** with encryption at rest
- **API key management** with environment variables

## Scalability Considerations

- **Modular design** allows independent scaling of components
- **Async processing** for concurrent task execution
- **Caching layer** for frequently accessed data
- **Vector embeddings** for efficient similarity search
- **Lightweight SQLite** can be replaced with PostgreSQL for production

## Integration Points

- **Gemini API**: Primary LLM for intelligence
- **Health APIs**: External medical databases
- **Future**: Apple Health, Google Fit, wearables
- **Export**: PDF reports, CSV data, HL7/FHIR