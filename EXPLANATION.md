# Technical Explanation

## 1. Agent Workflow

HIA processes health-related requests through an intelligent agent workflow:

### Step-by-Step Process:

1. **Receive User Input**
   - User uploads medical document (PDF, image, text)
   - User asks health-related question
   - User requests trend analysis or report

2. **Context Retrieval**
   - Memory store queries relevant historical data
   - ChromaDB performs semantic search on past documents
   - SQLite retrieves structured metrics and medications

3. **Task Planning (ReAct Pattern)**
   - Planner analyzes input to identify intent
   - Decomposes complex requests into atomic tasks
   - Creates dependency graph for task execution
   - Example: "Analyze my lab report" becomes:
     - Extract text from document
     - Identify lab values
     - Compare with reference ranges
     - Check historical trends
     - Generate insights

4. **Tool Execution**
   - Executor runs tasks in dependency order
   - Calls appropriate tools:
     - Gemini API for text/image analysis
     - Health APIs for drug/reference data
     - Document parser for extraction
     - Visualizer for charts

5. **Result Synthesis**
   - Aggregates results from all tasks
   - Gemini generates natural language insights
   - Stores results in memory for future reference
   - Returns formatted response to user

## 2. Key Modules

### **Planner** (`agent/planner.py`)
- Implements ReAct (Reasoning + Acting) pattern
- Task types: DOCUMENT_ANALYSIS, HEALTH_QUERY, TREND_ANALYSIS, etc.
- Intelligent task decomposition based on keywords and context
- Manages task dependencies and priorities

### **Executor** (`agent/executor.py`)
- Asynchronous task execution engine
- Manages API calls and tool invocations
- Error handling with graceful degradation
- Result aggregation and formatting

### **Memory Store** (`agent/memory.py`)
- Dual storage system:
  - ChromaDB for unstructured data (documents, insights)
  - SQLite for structured data (metrics, medications)
- Embedding-based semantic search
- Time-series data management for trends

## 3. Tool Integration

### **Google Gemini API**
```python
# Text analysis
response = await gemini_client.analyze_text(prompt, context)

# Multimodal analysis (text + images)
response = await gemini_client.analyze_multimodal([prompt, image])
```

### **Health APIs**
- **RxNav API**: Drug interaction checking
  ```python
  interactions = await health_api.check_drug_interactions(["aspirin", "warfarin"])
  ```
- **OpenFDA API**: Medication information
- **Reference Ranges**: Lab value interpretation

### **Document Parser**
- PDF extraction with PyPDF2
- OCR with Tesseract for scanned documents
- Medical value extraction using regex patterns
- Section identification (medications, diagnosis, etc.)

## 4. Observability & Testing

### Logging Strategy
- Structured logging at INFO level
- Task execution tracking with unique IDs
- API call monitoring with response times
- Error logging with full stack traces

### Testing Approach
```bash
# Run tests
pytest tests/

# Test document parsing
python -m src.utils.document_parser test_files/sample_lab.pdf

# Test API integration
python -m src.api.gemini_client --test
```

### Monitoring
- Task success/failure rates
- API response times
- Memory usage tracking
- User interaction patterns

## 5. Known Limitations

### Current Limitations
1. **OCR Accuracy**: Scanned documents may have reduced accuracy
2. **API Rate Limits**: Gemini API has usage quotas
3. **Language Support**: Currently optimized for English
4. **Complex Medications**: Some drug interactions may not be in database

### Performance Considerations
- Document processing: ~2-5 seconds per page
- Trend analysis: Scales with data volume
- Memory usage: ~500MB baseline + data

### Edge Cases
1. **Handwritten Notes**: Limited OCR support
2. **Non-standard Formats**: May require manual parsing
3. **Historical Data**: Requires consistent metric names
4. **Multi-user**: Session management in development

## 6. Agentic Features

### Proactive Capabilities
- **Automatic Metric Extraction**: Identifies and extracts values without explicit instruction
- **Trend Detection**: Proactively identifies concerning patterns
- **Recommendation Generation**: Suggests actions based on data
- **Context Awareness**: Remembers previous interactions

### Learning & Adaptation
- Stores successful task patterns
- Improves extraction accuracy over time
- Adapts to user preferences
- Builds personalized health profile

### Tool Selection Intelligence
- Chooses optimal tool based on input type
- Falls back gracefully when tools fail
- Combines multiple tools for complex queries
- Prioritizes accuracy over speed

## 7. Security & Privacy

### Data Protection
- All health data encrypted at rest
- Session-based access control
- Audit logging for compliance
- No data sharing without consent

### API Security
- API keys stored in environment variables
- Rate limiting to prevent abuse
- Input sanitization for all user data
- Secure file upload with validation