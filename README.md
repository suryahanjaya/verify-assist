# VerifyAssist — LLM-Based Static Analysis Warning Verification

# Overview
Static analysis tools (like ESLint) generate many false positive warnings. VerifyAssist solves this problem by using a Large Language Model to evaluate warnings. The system analyzes the code context and classifies each warning as a real bug, a false alarm, or a tolerable issue.

# Features
- Automatically verifies static analysis warnings.
- Extracts code context around each warning.
- Classifies warnings into TRUE_POSITIVE, FALSE_POSITIVE, or TOLERABLE.
- Provides a calibrated confidence score.
- Explains the reasoning in clear, simple language.
- Outputs the exact code snippet as evidence.

# System Architecture
The system uses a sequential pipeline:
1. ESLint generates warnings.
2. The Node.js CLI tool extracts the warning and surrounding code context.
3. The CLI sends the data to the FastAPI backend API.
4. The backend constructs a structured prompt.
5. The backend sends the prompt to the Groq API (llama-3.3-70b-versatile).
6. A parser extracts the classification and structured fields.
7. The CLI prints the final results to the user.

# Tech Stack
- Backend System: Python (FastAPI)
- LLM Integration: Groq API (llama-3.3-70b-versatile)
- CLI Tool: Node.js (ESLint integration, Axios)
- Evaluation Pipeline: Python
- Dataset Format: JSON

# How It Works
1. A developer runs the CLI tool on a source file.
2. The tool runs a static analyzer to extract warnings.
3. For each warning, it grabs 10 lines of code before and after the issue.
4. It sends this context to the local verification API.
5. The LLM acts as an expert reviewer and classifies the warning based on strict decision rules.
6. The user receives a summarized terminal output of valid bugs and dismissed false positives.

# Evaluation
The system was evaluated using a dataset of 20 labeled warnings representing various flaw categories.

Baseline Results (no LLM, all assumed TRUE):
- Accuracy: 65%

Final System Results:
- Accuracy: 90%
- Precision: 86.67%
- Recall: 100%
- F1 Score: 0.93

# Key Insights
1. LLM integration is highly effective. It improved accuracy from 65% to 90%, representing a 25% absolute increase.
2. Prompt engineering is critical. Small changes significantly impact classification behavior. Overloading the prompt with rules reduces performance.
3. There is a trade-off between accuracy and interpretability. Highly technical explanations are accurate but hard to read. Overly simple explanations are readable but reduce accuracy if the underlying logic is too loose. The solution is strict internal decision logic coupled with simple output requirements.
4. The TOLERABLE classification is a critical factor. When used too often, overall accuracy drops. Restricting its scope restores precision.
5. The model tends to be conservative. It occasionally defaults to TOLERABLE for ambiguous cases rather than making a definitive choice.

# Project Progress
The project evolved through a structured experimentation process:

1. Initial Baseline
Method: All warnings are considered TRUE.
Result: 65% Accuracy (13/20). The system could not distinguish bugs from false alarms.
Insight: Static analysis produces many false positives.

2. Initial VerifyAssist (LLM without tuning)
Result: 90% Accuracy, ~92% Precision, ~92% Recall.
Insight: The LLM immediately improved accuracy and significantly reduced false positives.

3. Added Readability and Conservative Rules
Changes: Simplified explanations, added tolerance rules, and made the prompt beginner-friendly.
Result: Accuracy dropped to 80%. Precision dropped. The system overused the TOLERABLE class.
Insight: Too much tolerance decreases accuracy. The model begins to under-classify real bugs.

4. Tightened Decision Rules
Changes: Restricted TOLERABLE usage, clarified TRUE_POSITIVE vs FALSE_POSITIVE differences, added a priority rule, and removed rigid constraints.
Result: Accuracy increased to 85%.
Insight: Controlling the core decision logic is more important than maintaining a lengthy prompt.

5. Final Version (Balanced Prompt)
Changes: TOLERABLE usage is strictly limited. Categorization rules are flexible but structured. Explanations remain simple. The output format remains strict.
Final Result: 90% Accuracy (18/20), 86.67% Precision, 100% Recall, 0.93 F1 Score.
Confusion Matrix: True Positives (13), True Negatives (5), False Positives (2), False Negatives (0).

# Limitations
- Dependent on external API availability and network latency.
- Occasionally falls back to default values if the LLM output violates strict formatting rules.
- Certain generic warnings may still cause misclassification.

# Future Work
- Implement persistent caching to reduce cost and latency.
- Expand support for more static analysis tools beyond ESLint.
- Fine-tune a smaller, local model to eliminate external dependencies.

# Setup Instructions
Follow these steps to run the system locally.

### 1. Backend Setup
Navigate to the backend directory, install dependencies, set up your API key, and start the server:

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate # On Mac/Linux
pip install -r requirements.txt
cp .env.example .env       # Edit .env and add your GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

### 2. CLI Setup
Navigate to the CLI directory and install the required Node.js packages:

```bash
cd cli
npm install
```

### 3. Evaluation Setup
To run the evaluation script against the benchmark dataset (ensure the backend is running first):

```bash
cd evaluation
..\backend\venv\Scripts\python evaluate.py
```

# Usage Example
To run the CLI tool against a sample file and see it in action:

Ensure the backend server is running, then open a new terminal:

```bash
cd cli
node check.js example.js
```

The CLI will print a list of warnings, their LLM classifications, confidence scores, simple explanations, and code evidence.
