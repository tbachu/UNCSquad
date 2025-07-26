# DEMO.md

## Video Link
[Insert your public video link here]

## Timestamps

**00:00–00:30 - Intro & setup**
- Welcome to HIA (Health Insights Agent)
- Problem: Medical documents are hard to understand
- Solution: AI-powered health analysis agent
- Quick setup demonstration

**00:30–01:30 - User input → Planning**
- User uploads lab report PDF
- Agent identifies document type
- Planner breaks down analysis tasks:
  - Extract text from PDF
  - Identify health metrics
  - Compare with reference ranges
  - Generate insights
- Shows ReAct reasoning process

**01:30–02:30 - Tool calls & memory**
- Gemini API analyzes document content
- Document parser extracts values
- Memory store saves results
- ChromaDB indexes for future search
- Health API checks for drug interactions

**02:30–03:30 - Final output & edge case handling**
- Natural language summary of results
- Trend visualization over time
- Handling edge cases:
  - Unreadable scans → OCR fallback
  - Missing reference ranges → API lookup
  - Complex queries → Multi-step reasoning
- Doctor visit report generation