# Demo Video

## HIA - Health Insights Agent Demo

HIA is your personal AI health analyst that securely analyzes medical documents, tracks health trends, and provides actionable insights using Google's Gemini API.

---

📺 **Demo Video Link:**  
[Insert your demo video URL here]

### Video Outline

#### **00:00–00:30** — Introduction & Problem Statement
- Overview of HIA's purpose
- The challenge: Complex medical data that's hard to understand
- Our solution: AI-powered health insights agent

#### **00:30–01:30** — Document Analysis Demo
- Upload a sample lab report PDF
- Show real-time document parsing
- Demonstrate metric extraction and explanation
- Highlight Gemini's role in simplifying medical jargon

#### **01:30–02:30** — Agentic Planning & Execution
- User asks: "How have my cholesterol levels changed?"
- Show task planning breakdown
- Demonstrate memory retrieval of historical data
- Display trend visualization
- Gemini generates personalized insights

#### **02:30–03:30** — Health Q&A and Recommendations
- Natural language health questions
- Drug interaction checking
- Proactive health recommendations
- Doctor visit report generation

#### **03:30–04:00** — Technical Architecture
- Brief overview of agentic architecture
- Gemini API integration highlights
- Security and privacy features
- Future roadmap

### Key Features Demonstrated

1. **Multi-format Document Analysis**
   - PDF lab report processing
   - Automatic value extraction
   - Plain language explanations

2. **Intelligent Task Planning**
   - ReAct pattern in action
   - Task decomposition visualization
   - Tool selection logic

3. **Personalized Insights**
   - Trend analysis over time
   - Context-aware recommendations
   - Natural language Q&A

4. **Security & Privacy**
   - Encrypted storage
   - Local processing options
   - User consent controls

### Technical Highlights

- **Gemini Integration**: Multimodal analysis, medical text understanding
- **Agentic Architecture**: Planner → Executor → Memory pattern
- **Tool Orchestration**: Seamless integration of multiple APIs
- **Scalable Design**: Modular components for easy extension

---

## Running the Demo Locally

```bash
# Clone the repository
git clone [repository-url]
cd UNCSquad

# Set up environment
conda env create -f environment.yml
conda activate hia-health-insights

# Set Gemini API key
export GEMINI_API_KEY=your_api_key_here

# Run the application
python src/main.py web

# Access at http://localhost:8501
```

## Sample Test Data

The demo includes sample medical documents in various formats:
- Lab reports (PDF)
- Prescription images (PNG/JPG)
- Doctor's notes (Text)

These demonstrate HIA's versatility in handling different medical document types.