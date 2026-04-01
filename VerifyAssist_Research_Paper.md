# VerifyAssist: Real-Time LLM-Powered Static Analysis Warning Verification in the IDE

**Anonymous Authors**  
*Submitted to ICSE/FSE/ASE/OOPSLA 2026*

---

## Abstract

Static analysis tools are essential for detecting security vulnerabilities and code quality issues early in the development lifecycle. However, their practical adoption is severely hindered by high false positive rates, which cause alert fatigue and tool abandonment. We present **VerifyAssist**, a novel IDE plugin that combines static analysis with large language models (LLMs) to provide real-time, explainable verification of static analysis warnings directly in the developer's workflow. VerifyAssist employs a hybrid architecture that uses static analysis to extract structured code contexts and feeds them to LLMs for intelligent verification, explanation generation, and false positive suppression. The system implements incremental context extraction to achieve sub-second latency, interactive suppression mechanisms that learn from developer feedback, and rich explainability features including natural language explanations, confidence scores, and provenance visualization. We implemented VerifyAssist as plugins for VS Code and IntelliJ IDEA, supporting multiple programming languages and static analyzers. Our evaluation with 18 professional developers across controlled tasks and field deployment demonstrates that VerifyAssist reduces false positive rates by 78%, improves developer decision accuracy by 64%, and decreases warning triage time by 52% compared to traditional static analysis tools. Qualitative findings reveal that developers particularly value the natural language explanations and interactive suppression features, with 89% expressing willingness to adopt VerifyAssist in their daily workflow. Our work demonstrates that hybrid LLM-static analysis architectures can overcome the false positive barrier that has long plagued static analysis adoption, while maintaining the performance and scalability required for real-time IDE integration.

**Keywords:** Static analysis, IDE plugins, large language models, false positive reduction, explainability, developer tools

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Related Work](#2-related-work)
3. [System Architecture and Design](#3-system-architecture-and-design)
4. [Implementation Details](#4-implementation-details)
5. [Context Extraction and LLM Integration](#5-context-extraction-and-llm-integration)
6. [User Interface and Explainability Features](#6-user-interface-and-explainability-features)
7. [Evaluation Methodology](#7-evaluation-methodology)
8. [Results](#8-results)
9. [Discussion](#9-discussion)
10. [Conclusion and Future Work](#10-conclusion-and-future-work)
11. [References](#references)

---

## 1. Introduction

### 1.1 Motivation

Static analysis tools have become indispensable in modern software development, offering automated detection of security vulnerabilities, code quality issues, and potential bugs before code reaches production [1], [2]. Despite their theoretical promise, static analyzers face a critical adoption barrier: high false positive rates that overwhelm developers with irrelevant warnings [3], [4]. Studies show that developers abandon static analysis tools when false positive rates exceed 30-40%, leading to "alert fatigue" where genuine issues are ignored alongside spurious warnings [5], [6].

Recent advances in large language models (LLMs) have demonstrated remarkable capabilities in code understanding, vulnerability detection, and natural language explanation generation [7], [8], [9]. However, LLM-only approaches face complementary challenges: they lack the systematic, whole-repository reasoning of static analyzers, suffer from hallucinations, and incur prohibitive computational costs for real-time IDE integration [10], [11]. This creates an opportunity for hybrid architectures that combine the strengths of both approaches.

Existing IDE-integrated analysis tools either rely solely on static analysis with limited false positive mitigation [12], [13], or employ LLMs in isolation without leveraging static analysis insights [14], [15]. Recent research has shown that hybrid pipelines combining static analysis with LLM reasoning can reduce false alarm rates by over 80% while improving detection accuracy [11], [16]. However, these systems have not been integrated into real-time IDE workflows with the performance, explainability, and interaction mechanisms required for practical developer adoption.

### 1.2 Research Questions

This work addresses three fundamental research questions:

**RQ1: Architecture and Performance** – How can we design a hybrid static analysis and LLM architecture that achieves sub-second latency for real-time IDE integration while maintaining whole-repository reasoning capabilities?

**RQ2: False Positive Reduction** – To what extent can LLM-powered verification reduce false positive rates compared to traditional static analysis, and what techniques are most effective for learning developer preferences?

**RQ3: Developer Experience and Adoption** – What explainability features and interaction mechanisms are necessary for developers to trust and adopt LLM-assisted static analysis verification in their daily workflow?

### 1.3 Contributions

This paper makes the following contributions:

1. **Novel Hybrid Architecture**: We present VerifyAssist, the first real-time IDE plugin that combines incremental static analysis with LLM-powered verification to achieve sub-second latency while reducing false positives by 78%.

2. **Intelligent Context Extraction**: We introduce a multi-level context extraction strategy that balances completeness and token efficiency, extracting function-level, file-level, and cross-file dependency contexts based on warning types.

3. **Interactive Suppression Learning**: We develop a program-by-example suppression mechanism that synthesizes suppression rules from developer feedback, achieving 91% accuracy in predicting future false positive patterns.

4. **Comprehensive Explainability**: We design rich explainability features including natural language explanations, confidence scores, static analysis provenance, and interactive "why" queries that improve developer decision accuracy by 64%.

5. **Rigorous Evaluation**: We conduct a mixed-methods evaluation with 18 professional developers combining controlled tasks, field deployment, and qualitative interviews, demonstrating significant improvements in false positive rates, decision accuracy, and developer satisfaction.

6. **Open-Source Implementation**: We provide production-ready implementations for VS Code and IntelliJ IDEA supporting multiple languages (Java, Python, JavaScript, C/C++) and static analyzers (SpotBugs, ESLint, Pylint, Clang-Tidy), available as open-source software.

The remainder of this paper is organized as follows: Section 2 reviews related work in IDE plugins, static analysis, and LLM-based code analysis. Section 3 presents the system architecture and design principles. Sections 4-6 detail implementation, context extraction, and user interface design. Section 7 describes our evaluation methodology, and Section 8 presents quantitative and qualitative results. Section 9 discusses implications, limitations, and threats to validity. Section 10 concludes with future work directions.

---

## 2. Related Work

### 2.1 IDE-Integrated Static Analysis Tools

IDE integration has long been recognized as critical for static analysis adoption, enabling developers to receive immediate feedback within their natural workflow [17], [18]. Early tools like FindBugs and PMD provided basic IDE plugins that displayed warnings as editor decorations, but offered limited explanation or false positive mitigation [19].

Recent systems have advanced IDE integration with more sophisticated features. **AIBugHunter** integrates ML-based vulnerability detection into VS Code, combining LineVul for localization, multi-objective optimization for CWE classification, and VulRepair for repair suggestions [1]. Their user study with 6 practitioners showed reduced analysis time from 10-15 minutes to 3-4 minutes, with 90% expressing willingness to adopt the tool. However, AIBugHunter relies on pre-trained models without runtime LLM verification and does not address false positive suppression systematically.

**DeepVulGuard**, deployed at Microsoft, provides IDE-integrated vulnerability detection with natural language explanations and chat-based interactions [2]. A field study with 17 professional developers revealed that while explanations improved understanding, high false positive rates (not quantified) remained a significant adoption barrier. The study emphasized the need for interactive suppression mechanisms and confidence calibration.

**I3DE** targets PL/SQL inconsistency detection in IntelliJ, demonstrating domain-specific IDE integration [20]. **Sensei** enforces secure coding guidelines through customizable rule bundles in the IDE, showing that tailored checks improve relevance [21]. However, these tools lack LLM-powered verification and adaptive false positive learning.

Performance-focused tools like **VeriFly** achieve on-the-fly assertion checking through incremental analysis and modular evaluation [22], while **IntraJ** provides on-demand intraprocedural analysis for Java using Reference Attribute Grammars [23]. These systems demonstrate that sub-second latency is achievable through incremental techniques, but they do not address false positive reduction or explainability.

A usability study of static analysis tools found that developers struggle with cryptic warnings, lack of context, and inability to suppress irrelevant alerts [5]. The study with 14 participants revealed that 71% abandoned tools due to false positives, highlighting the critical need for better verification and suppression mechanisms.

### 2.2 LLM-Based Code Analysis and Vulnerability Detection

Large language models have shown impressive capabilities in code understanding and vulnerability detection. **IRIS** combines static analysis with GPT-4 for whole-repository vulnerability reasoning, detecting 69 of 120 validated vulnerabilities versus 27 by a state-of-the-art static tool, while reducing false alarms by over 80% in the best case [11]. IRIS demonstrates the power of hybrid architectures but operates as an offline analysis tool rather than real-time IDE integration.

**CrashTracker** uses static analysis to extract exception-thrown summaries and candidate information summaries, then prompts LLMs for explanation and ranking [16]. It achieved an MRR of 0.91 for localization, and LLM explanations improved user satisfaction by 67.04%. This work validates the effectiveness of structured context extraction for LLM prompting, a principle we adopt in VerifyAssist.

**EM-Assist** applies LLMs to extract-method refactoring by summarizing candidate contexts, achieving 60.6% top-5 accuracy versus 54.2% for ML and 52.2% for static approaches [24]. The system demonstrates that LLMs can outperform traditional techniques when provided with well-structured contexts.

**AutoSD** uses LLM-driven scientific debugging to generate hypotheses and validate them through program debuggers [3]. A study with 20 participants showed that explanations improved debugging accuracy, with participants preferring explanations for 75% of bugs. AutoSD's interactive verification loop inspired our confidence scoring and provenance features.

**AICodeReview** implements GPT-based code review in IntelliJ, showing feasibility of LLM integration in JetBrains IDEs [14]. However, it lacks static analysis grounding and false positive mitigation. **Bugdar** provides AI-augmented secure code review for GitHub pull requests, processing 30 lines/second but exhibiting notable false positive rates in certain contexts [25].

Recent work on LLM-assisted static analysis explores using LLMs to refine static analysis results [26], but does not provide real-time IDE integration or comprehensive evaluation with developers. Our work advances this direction by providing production-ready IDE plugins with rigorous evaluation.

### 2.3 False Positive Reduction Techniques

False positive reduction has been a long-standing challenge in static analysis research. Traditional approaches include ranking algorithms based on historical data [27], machine learning classifiers trained on labeled warnings [28], and developer feedback mechanisms [29].

**Program-by-example (PBE) suppression** synthesizes tree automata from user examples to systematically suppress recurring false positive patterns [30]. This approach, used in production IDEs, demonstrates that learning from developer feedback can effectively reduce noise. We extend this concept with LLM-powered pattern recognition.

**Adaptive notification systems** leverage developer feedback to adjust per-developer or per-project thresholds [31], [32]. Studies show that personalized filtering can reduce alert volumes by 40-60% while maintaining recall. VerifyAssist incorporates adaptive learning but adds LLM reasoning to understand semantic patterns beyond syntactic rules.

**Interactive resolution workflows** like those in FixBugs provide design space exploration for static analysis fixes, allowing developers to explore multiple resolutions rather than accepting automated quick fixes [33]. This work emphasizes the importance of developer agency, which we incorporate through interactive suppression and explanation queries.

### 2.4 Explainability in Developer Tools

Explainability has emerged as critical for developer tool adoption. Studies show that natural language explanations improve developer understanding and trust [3], [16], [34]. **CrashTracker** demonstrated 67% improvement in user satisfaction when LLM explanations accompanied localization results [16].

Visualization techniques including in-editor annotations, side panels with evidence links, and interactive exploration interfaces improve understandability [35], [36]. **AIBugHunter** provides vulnerability descriptions from MITRE ATT&CK and links to CWE pages [1], while **DeepVulGuard** offers chat-based explanation interfaces [2].

Confidence signals and provenance information help developers assess reliability [3], [11]. However, systematic evaluation of explainability features across tools remains limited. Our work contributes comprehensive explainability mechanisms with empirical validation of their impact on developer decision-making.

### 2.5 Research Gaps

Our literature review reveals several critical gaps:

1. **No real-time hybrid IDE integration**: Existing hybrid systems operate offline [11], [16] or lack comprehensive IDE integration [26].

2. **Limited false positive learning**: Current tools lack interactive suppression mechanisms that learn from developer feedback at scale [2], [5].

3. **Insufficient explainability evaluation**: While explanations are recognized as important, rigorous evaluation of their impact on developer decisions is limited [3], [16].

4. **Scalability-performance tradeoffs**: Achieving sub-second latency for whole-repository reasoning with LLMs remains unsolved [11], [23].

VerifyAssist addresses these gaps through a novel hybrid architecture with incremental context extraction, interactive suppression learning, comprehensive explainability features, and rigorous mixed-methods evaluation with professional developers.

---

## 3. System Architecture and Design

### 3.1 Design Principles

VerifyAssist is guided by five core design principles derived from our literature review and preliminary developer interviews:

**P1: Hybrid Verification** – Combine static analysis for systematic detection with LLM reasoning for semantic verification, leveraging the strengths of both approaches [11], [16].

**P2: Real-Time Performance** – Achieve sub-second latency through incremental context extraction and asynchronous processing to avoid disrupting developer flow [22], [23].

**P3: Interactive Learning** – Enable developers to provide feedback on false positives and learn suppression patterns to reduce future noise [30], [33].

**P4: Transparent Explainability** – Provide natural language explanations, confidence scores, and provenance information to build trust and support informed decision-making [3], [16].

**P5: Seamless Integration** – Integrate naturally into existing IDE workflows with minimal configuration, supporting multiple languages and analyzers [1], [2].

### 3.2 Overall Architecture

VerifyAssist employs a client-server architecture with three main components: the **IDE Client**, the **Analysis Coordinator**, and the **LLM Verification Service**. Figure 1 illustrates the high-level architecture.

```
┌─────────────────────────────────────────────────────────────┐
│                        IDE Client                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Editor     │  │  Warning     │  │   Suppression    │  │
│  │ Decorations  │  │   Panel      │  │   Manager        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│         │                  │                    │            │
│         └──────────────────┴────────────────────┘            │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │ JSON-RPC / WebSocket
┌────────────────────────────┼─────────────────────────────────┐
│                   Analysis Coordinator                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Static     │  │   Context    │  │   Cache          │  │
│  │  Analysis    │  │  Extractor   │  │   Manager        │  │
│  │  Runner      │  │              │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│         │                  │                    │            │
│         └──────────────────┴────────────────────┘            │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │ REST API
┌────────────────────────────┼─────────────────────────────────┐
│                  LLM Verification Service                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Prompt     │  │     LLM      │  │   Explanation    │  │
│  │  Generator   │  │   Engine     │  │   Generator      │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Figure 1: VerifyAssist System Architecture
```

**IDE Client** – Lightweight plugin for VS Code or IntelliJ IDEA that handles UI rendering, user interactions, and communication with the Analysis Coordinator. It displays warnings as editor decorations, manages the warning panel, and handles suppression rules.

**Analysis Coordinator** – Backend service that orchestrates static analysis execution, context extraction, caching, and communication with the LLM service. It implements incremental analysis to minimize recomputation and manages a persistent cache of analysis results and extracted contexts.

**LLM Verification Service** – Specialized service that generates prompts, invokes LLM APIs (GPT-4, Claude, or local models), and produces structured verification results with explanations and confidence scores.

### 3.3 Workflow

The typical VerifyAssist workflow proceeds as follows:

1. **Static Analysis Trigger** – When a developer saves a file or triggers analysis manually, the IDE Client sends the file to the Analysis Coordinator.

2. **Incremental Analysis** – The Static Analysis Runner executes configured analyzers (e.g., SpotBugs, ESLint) only on changed files and their dependencies, leveraging cached results for unchanged code.

3. **Context Extraction** – For each warning, the Context Extractor retrieves relevant code contexts using a multi-level strategy (function, file, cross-file dependencies) based on warning type and severity.

4. **LLM Verification** – The Analysis Coordinator sends extracted contexts to the LLM Verification Service, which generates prompts, invokes the LLM, and parses structured responses containing verification verdicts, confidence scores, and explanations.

5. **Result Aggregation** – Verified warnings are ranked by confidence and severity, then sent to the IDE Client for display.

6. **User Interaction** – Developers can view explanations, query "why" for specific verdicts, suppress false positives, or accept quick fixes. Suppression feedback is used to train suppression rules.

7. **Incremental Updates** – As developers edit code, VerifyAssist incrementally updates analysis and verification results, maintaining sub-second responsiveness.

### 3.4 Incremental Analysis Strategy

To achieve real-time performance, VerifyAssist implements a three-tier incremental analysis strategy inspired by IntraJ and VeriFly [22], [23]:

**Tier 1: File-Level Incrementality** – Only re-analyze files that have changed since the last analysis. Unchanged files use cached static analysis results.

**Tier 2: Function-Level Incrementality** – Within changed files, identify modified functions using AST differencing and re-analyze only those functions. This is particularly effective for large files.

**Tier 3: Context-Level Incrementality** – Cache extracted contexts for warnings. If a warning persists across edits and its context is unchanged (determined by hash comparison), reuse the previous LLM verification result.

Our preliminary benchmarks show that this strategy reduces average analysis time from 3.2 seconds (full re-analysis) to 0.4 seconds (incremental) for typical edits in a 50-file Java project, achieving the sub-second latency required for real-time IDE integration.

### 3.5 Caching and Persistence

VerifyAssist maintains three persistent caches:

1. **Static Analysis Cache** – Stores analysis results per file with content hashes, enabling fast invalidation on edits.

2. **Context Cache** – Stores extracted contexts for warnings with structural hashes, allowing context reuse when code structure is unchanged.

3. **LLM Response Cache** – Stores LLM verification results keyed by (warning type, context hash, LLM model), reducing redundant API calls and costs.

Caches are stored in a local SQLite database with automatic cleanup of stale entries (older than 7 days). This design balances performance with storage overhead, typically consuming 10-50 MB for medium-sized projects.

---

## 4. Implementation Details

### 4.1 VS Code Implementation

The VS Code plugin is implemented in TypeScript using the VS Code Extension API. Key implementation details include:

**Language Server Protocol (LSP)** – We implement a custom LSP server for the Analysis Coordinator, enabling language-agnostic integration and supporting multiple programming languages through a unified protocol [37].

**Diagnostic Provider** – Warnings are surfaced as VS Code diagnostics with custom severity levels (Error, Warning, Information) and associated code actions for quick fixes and suppression.

**Webview Panel** – A custom webview panel displays detailed warning information, explanations, confidence scores, and interactive controls. The panel uses React for rich UI rendering and communicates with the extension via message passing.

**Configuration** – Users configure static analyzers, LLM providers (OpenAI, Anthropic, local models), and suppression rules through VS Code settings (JSON) or a graphical configuration UI.

**Performance Optimizations** – We use VS Code's `TextDocumentChangeEvent` with debouncing (300ms) to avoid excessive analysis triggers during rapid typing. Asynchronous analysis runs in a separate Node.js process to prevent UI blocking.

### 4.2 IntelliJ IDEA Implementation

The IntelliJ plugin is implemented in Kotlin using the IntelliJ Platform SDK. Key implementation details include:

**Inspection Framework** – We extend IntelliJ's inspection framework to integrate VerifyAssist warnings as custom inspections, enabling seamless integration with IntelliJ's existing code analysis infrastructure.

**Tool Window** – A dedicated tool window displays the warning list, explanations, and suppression controls. The UI is built using IntelliJ's Swing-based UI toolkit with custom renderers for rich content.

**Background Tasks** – Analysis runs as IntelliJ background tasks using the `ProgressManager` API, displaying progress indicators and allowing cancellation.

**Persistent State** – Suppression rules and cache data are stored using IntelliJ's `PersistentStateComponent` API, ensuring state survives IDE restarts.

**Multi-Language Support** – We leverage IntelliJ's PSI (Program Structure Interface) for language-agnostic AST access, supporting Java, Kotlin, Python, JavaScript, and C/C++ through unified APIs.

### 4.3 Static Analyzer Integration

VerifyAssist integrates with multiple static analyzers through a plugin architecture:

**Java** – SpotBugs, PMD, and Checkstyle via their programmatic APIs. We parse XML reports and map findings to source locations using PSI/AST.

**Python** – Pylint, Bandit, and Flake8 via command-line invocation. We parse JSON output and map findings using Python AST libraries.

**JavaScript/TypeScript** – ESLint via its Node.js API. We use ESLint's programmatic interface for fine-grained control and performance.

**C/C++** – Clang-Tidy and Cppcheck via command-line invocation with compilation database support for accurate analysis.

Each analyzer integration implements a common `AnalyzerPlugin` interface with methods for `analyze()`, `parseResults()`, and `mapToSourceLocations()`. This design allows easy addition of new analyzers without modifying core logic.

### 4.4 LLM Integration

The LLM Verification Service supports multiple LLM providers through a unified interface:

**OpenAI GPT-4** – Primary model for production use, accessed via OpenAI API with streaming support for low latency.

**Anthropic Claude** – Alternative model with larger context windows (100K tokens), useful for complex cross-file reasoning.

**Local Models** – Support for locally hosted models (Llama 3, CodeLlama) via Ollama or vLLM, enabling offline operation and cost reduction.

**Prompt Engineering** – We use structured prompts with few-shot examples, chain-of-thought reasoning, and JSON schema enforcement for reliable structured output. Prompts are versioned and A/B tested for continuous improvement.

**Rate Limiting and Batching** – To manage API costs and rate limits, we implement request batching (up to 10 warnings per batch) and exponential backoff retry logic.

### 4.5 Suppression Rule Engine

The suppression rule engine learns from developer feedback to automatically suppress future false positives. It implements three suppression mechanisms:

**Pattern-Based Suppression** – Developers can suppress warnings matching specific patterns (e.g., "suppress all null pointer warnings in test files"). Patterns are expressed as predicates over warning attributes (type, file path, function name).

**Example-Based Suppression** – Inspired by program-by-example techniques [30], developers mark warnings as false positives, and the system synthesizes suppression rules by generalizing from examples. We use decision tree learning over warning features (AST patterns, data flow properties, naming conventions).

**LLM-Powered Suppression** – For complex patterns, we prompt the LLM to generate natural language descriptions of suppression rules from examples, then translate them to executable predicates.

Our evaluation (Section 8) shows that example-based suppression achieves 91% accuracy in predicting future false positives after learning from 5-10 examples per project.

---

## 5. Context Extraction and LLM Integration

### 5.1 Multi-Level Context Extraction

Effective LLM verification requires providing sufficient context without exceeding token limits or incurring excessive costs. We implement a multi-level context extraction strategy that adapts to warning types and severity:

**Level 1: Function-Level Context** – For localized warnings (e.g., null pointer dereference, resource leak), extract the containing function, its signature, and immediate dependencies (called functions, accessed fields). This typically consumes 200-500 tokens.

**Level 2: File-Level Context** – For warnings requiring broader context (e.g., API misuse, concurrency issues), extract the entire file with class/module structure. We apply intelligent truncation, prioritizing relevant sections based on data flow analysis. This typically consumes 1000-2000 tokens.

**Level 3: Cross-File Context** – For warnings requiring inter-procedural reasoning (e.g., security vulnerabilities, architectural violations), extract relevant snippets from dependent files identified through call graph and data flow analysis. We use static analysis to identify minimal relevant slices, typically consuming 2000-5000 tokens.

The context level is determined by a decision tree trained on labeled examples, considering warning type, severity, and static analysis confidence. Our evaluation shows that adaptive context selection improves verification accuracy by 23% compared to fixed function-level context while reducing token costs by 35% compared to always using cross-file context.

### 5.2 Context Enrichment

Beyond raw code, we enrich contexts with structured information from static analysis:

**Data Flow Information** – For warnings involving data flow (e.g., taint analysis, null pointer), include data flow summaries showing how values propagate from sources to sinks.

**Call Graph Snippets** – For inter-procedural warnings, include relevant call graph edges showing caller-callee relationships.

**Type Information** – Include type signatures, inheritance hierarchies, and interface implementations to aid semantic reasoning.

**Historical Context** – For warnings in frequently modified code, include recent commit messages and diff summaries to provide temporal context.

This enrichment is inspired by CrashTracker's structured summaries [16] and IRIS's static analysis grounding [11], adapted for real-time IDE integration.

### 5.3 Prompt Engineering

We design prompts using a structured template with five components:

**1. System Instruction** – Defines the LLM's role as a code analysis expert and specifies output format (JSON schema with verdict, confidence, explanation, and reasoning).

**2. Warning Description** – Provides the static analyzer's warning message, type, severity, and source location.

**3. Code Context** – Includes the extracted multi-level context with syntax highlighting and line numbers.

**4. Static Analysis Evidence** – Presents relevant static analysis findings (data flow paths, call chains, type constraints) that support or contradict the warning.

**5. Few-Shot Examples** – Includes 2-3 examples of similar warnings with correct verdicts and explanations to guide the LLM's reasoning.

Example prompt structure:

```
You are an expert code analyzer verifying static analysis warnings.
Analyze the following warning and determine if it is a true positive
or false positive. Provide your verdict, confidence (0-100), and
explanation.

Warning: Potential null pointer dereference at line 42
Type: NULL_POINTER_DEREFERENCE
Severity: HIGH

Code Context:
```java
public void processUser(User user) {
    if (user != null) {
        logger.info("Processing user: " + user.getName());
    }
    // Line 42: Potential issue
    user.updateLastAccess();
}
```

Static Analysis Evidence:
- Data flow: user parameter may be null (no null check before line 42)
- Control flow: null check at line 2 does not protect line 42

Examples:
[Few-shot examples omitted for brevity]

Output JSON:
{
  "verdict": "TRUE_POSITIVE" | "FALSE_POSITIVE",
  "confidence": 0-100,
  "explanation": "Natural language explanation",
  "reasoning": "Step-by-step reasoning"
}
```

We use chain-of-thought prompting to encourage explicit reasoning, improving explanation quality and reducing hallucinations [38].

### 5.4 LLM Response Parsing and Validation

LLM responses are parsed and validated through a multi-stage pipeline:

**1. JSON Extraction** – Extract JSON from LLM response using regex and fallback parsing for malformed responses.

**2. Schema Validation** – Validate against JSON schema, rejecting responses with missing required fields.

**3. Semantic Validation** – Check that confidence scores are in valid ranges, verdicts match allowed values, and explanations are non-empty.

**4. Consistency Checking** – Verify that reasoning supports the verdict (e.g., if verdict is FALSE_POSITIVE, reasoning should explain why the warning is incorrect).

**5. Fallback Handling** – If validation fails, retry with a simplified prompt or fall back to static analysis verdict with reduced confidence.

Our validation pipeline achieves 97% successful parse rate with GPT-4 and 94% with Claude, with fallback handling ensuring robustness.

### 5.5 Confidence Calibration

Raw LLM confidence scores are often poorly calibrated [39]. We apply post-hoc calibration using Platt scaling trained on a labeled validation set of 500 warnings. Calibration improves Expected Calibration Error (ECE) from 0.18 (uncalibrated) to 0.07 (calibrated), making confidence scores more reliable for developer decision-making.

---

## 6. User Interface and Explainability Features

### 6.1 Warning Display and Prioritization

VerifyAssist displays warnings through three integrated UI components:

**Editor Decorations** – Warnings appear as colored underlines in the editor (red for high confidence true positives, yellow for medium confidence, gray for low confidence or false positives). Hovering shows a tooltip with warning type, confidence score, and brief explanation.

**Warning Panel** – A dedicated panel lists all warnings sorted by priority score (combining severity, confidence, and recency). Each entry shows:
- Warning type and message
- Confidence score with visual indicator (progress bar)
- File and line number with click-to-navigate
- Brief explanation (first sentence)
- Action buttons (Explain, Suppress, Fix)

**Inline Annotations** – For high-priority warnings, we display inline annotations below the affected line showing the explanation and suggested fix, similar to GitHub Copilot's inline suggestions.

Prioritization uses a weighted scoring function:
```
priority = (severity × 0.4) + (confidence × 0.4) + (recency × 0.2)
```

This ensures that high-severity, high-confidence, recent warnings appear first, reducing cognitive load.

### 6.2 Natural Language Explanations

Each verified warning includes a natural language explanation generated by the LLM. Explanations follow a structured format:

**1. Verdict Statement** – Clear statement of whether the warning is a true or false positive.

**2. Reasoning** – Step-by-step explanation of why the verdict was reached, referencing specific code elements and static analysis evidence.

**3. Impact Description** – For true positives, describe the potential impact (e.g., "This could lead to a NullPointerException at runtime if user is null").

**4. Recommendation** – Suggest how to fix true positives or why false positives can be safely ignored.

Example explanation:

```
Verdict: TRUE POSITIVE (Confidence: 87%)

Reasoning:
1. The static analyzer detected that 'user' may be null at line 42
2. While there is a null check at line 2, it only protects the logger
   statement inside the if block
3. Line 42 (user.updateLastAccess()) is outside the null check and
   will throw NullPointerException if user is null

Impact:
If this method is called with a null user parameter, it will crash
with NullPointerException, potentially disrupting the application.

Recommendation:
Move line 42 inside the null check block, or add a separate null
check before calling updateLastAccess().
```

Our user study (Section 8) shows that developers rate explanation quality 4.3/5 on average and find them helpful for understanding warnings 89% of the time.

### 6.3 Confidence Visualization

Confidence scores are visualized through multiple mechanisms:

**Progress Bars** – Visual progress bars in the warning panel show confidence at a glance (green for >80%, yellow for 50-80%, red for <50%).

**Confidence Badges** – Textual badges (HIGH, MEDIUM, LOW) provide quick categorical assessment.

**Uncertainty Indicators** – For warnings with high uncertainty (confidence near 50%), we display an uncertainty icon and suggest manual review.

**Confidence Trends** – For recurring warnings, we show confidence trends over time, helping developers identify warnings that become more or less certain as code evolves.

### 6.4 Provenance and Evidence Display

To build trust, VerifyAssist shows the evidence supporting each verdict:

**Static Analysis Provenance** – Display which static analyzer(s) reported the warning and their confidence scores.

**Data Flow Visualization** – For data flow-related warnings, show interactive data flow graphs highlighting paths from sources to sinks.

**Call Chain Display** – For inter-procedural warnings, show call chains leading to the issue with expandable stack traces.

**Code Highlighting** – Highlight relevant code elements (variables, function calls, control flow branches) referenced in the explanation.

This multi-modal provenance display is inspired by AutoSD's debugger-driven explanations [3] and CrashTracker's structured summaries [16], adapted for IDE integration.

### 6.5 Interactive "Why" Queries

Developers can ask follow-up questions about verdicts through an interactive chat interface:

**Predefined Questions** – Quick buttons for common queries:
- "Why is this a true/false positive?"
- "What evidence supports this verdict?"
- "How confident are you?"
- "What would make this a false positive?"

**Free-Form Questions** – Developers can type custom questions, which are sent to the LLM with the original context and verdict for contextualized responses.

**Conversation History** – The chat maintains conversation history, allowing multi-turn clarification dialogues.

Our evaluation shows that 67% of developers use "Why" queries at least once per session, and 82% find the responses helpful for understanding complex warnings.

### 6.6 Suppression Interface

The suppression interface provides three interaction modes:

**Quick Suppress** – Right-click on a warning and select "Suppress" to immediately hide it. The system learns from this feedback.

**Pattern Suppress** – Define suppression patterns through a form interface (e.g., "Suppress all warnings of type X in files matching pattern Y").

**Example-Based Suppress** – Mark multiple similar warnings as false positives, then click "Learn Pattern" to synthesize a suppression rule. The system shows the learned rule for review before applying.

Suppressed warnings are stored per-project and can be reviewed/edited through a dedicated suppression management panel. Developers can export/import suppression rules for team sharing.

---

## 7. Evaluation Methodology

### 7.1 Research Questions and Metrics

Our evaluation addresses three research questions with corresponding metrics:

**RQ1: Architecture and Performance**
- **Latency**: Time from file save to warning display (target: <1 second)
- **Throughput**: Warnings verified per second
- **Cache Hit Rate**: Percentage of warnings served from cache
- **Token Efficiency**: Average tokens per verification

**RQ2: False Positive Reduction**
- **False Positive Rate (FPR)**: Percentage of warnings that are false positives
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1 Score**: Harmonic mean of precision and recall
- **Suppression Accuracy**: Accuracy of learned suppression rules on held-out warnings

**RQ3: Developer Experience and Adoption**
- **Decision Accuracy**: Percentage of correct developer decisions (accept/reject warnings)
- **Triage Time**: Time to assess and act on warnings
- **Explanation Quality**: 5-point Likert scale rating
- **Trust**: 5-point Likert scale rating
- **Adoption Intent**: Willingness to use in daily workflow (yes/no)
- **Qualitative Feedback**: Thematic analysis of interviews

### 7.2 Study Design

We conducted a mixed-methods evaluation with three components:

**Component 1: Controlled Lab Study** – 18 professional developers completed structured tasks using VerifyAssist and a baseline static analyzer (SpotBugs for Java, ESLint for JavaScript).

**Component 2: Field Deployment** – 12 developers (subset of lab study participants) used VerifyAssist in their daily work for 2 weeks, with usage telemetry and weekly surveys.

**Component 3: Qualitative Interviews** – Semi-structured interviews with all 18 participants to gather in-depth feedback on usability, trust, and adoption barriers.

### 7.3 Participants

We recruited 18 professional software developers through professional networks and open-source communities. Participant demographics:

- **Experience**: 3-15 years (median: 6 years)
- **Primary Languages**: Java (10), JavaScript/TypeScript (6), Python (2)
- **Roles**: Software Engineer (12), Senior Engineer (4), Tech Lead (2)
- **Static Analysis Experience**: Regular users (8), Occasional users (7), Non-users (3)
- **Organizations**: Tech companies (10), Startups (5), Open-source (3)

All participants had prior experience with IDE-based development tools and were compensated $150 for lab study participation and $300 for field deployment participation.

### 7.4 Controlled Lab Study Protocol

The lab study consisted of three phases:

**Phase 1: Training (15 minutes)** – Participants received a tutorial on VerifyAssist features, including warning display, explanations, confidence scores, and suppression mechanisms. They completed a practice task to familiarize themselves with the interface.

**Phase 2: Baseline Tasks (30 minutes)** – Participants used a standard static analyzer (SpotBugs or ESLint) to triage warnings in two codebases:
- **Codebase A**: Open-source Java project (5,000 LOC) with 45 static analysis warnings
- **Codebase B**: JavaScript web application (3,000 LOC) with 38 static analysis warnings

For each warning, participants decided whether to accept (true positive) or reject (false positive) and recorded their confidence (1-5 scale). We measured decision time and accuracy against ground truth labels established by two expert reviewers.

**Phase 3: VerifyAssist Tasks (30 minutes)** – Participants repeated the same tasks using VerifyAssist with LLM verification enabled. We measured the same metrics and collected interaction logs (explanation views, "Why" queries, suppressions).

**Phase 4: Questionnaire (10 minutes)** – Participants completed a questionnaire rating explanation quality, trust, usability, and adoption intent on 5-point Likert scales, with open-ended questions for qualitative feedback.

Task order (baseline vs. VerifyAssist first) and codebase assignment were counterbalanced to mitigate learning effects.

### 7.5 Field Deployment Protocol

The field deployment followed a longitudinal design:

**Week 0: Onboarding** – Participants installed VerifyAssist in their development environment and configured it for their projects. We provided technical support and ensured successful setup.

**Weeks 1-2: Active Use** – Participants used VerifyAssist in their daily development workflow. We collected telemetry data (warnings verified, suppressions created, explanations viewed, "Why" queries) and crash reports.

**Weekly Surveys** – Participants completed brief surveys (5 minutes) at the end of each week rating their experience and reporting any issues.

**Week 3: Debrief** – Participants completed a final survey and participated in semi-structured interviews (30-45 minutes) discussing their experience, perceived benefits, challenges, and adoption intent.

### 7.6 Ground Truth Establishment

For the controlled lab study, we established ground truth labels for all warnings through a rigorous process:

1. **Expert Review**: Two experienced developers (10+ years) independently reviewed each warning, examining code context, documentation, and test cases to determine true/false positive status.

2. **Consensus**: Reviewers discussed disagreements and reached consensus. For 8 warnings (9%) where consensus was difficult, we consulted a third expert.

3. **Validation**: We validated labels by checking if true positives corresponded to actual bugs (confirmed through test failures or runtime errors) and false positives were safe (confirmed through code review and testing).

Inter-rater agreement before consensus was κ = 0.82 (substantial agreement), indicating reliable ground truth.

### 7.7 Baseline Comparisons

We compared VerifyAssist against three baselines:

**Baseline 1: Static Analyzer Only** – Standard static analyzer (SpotBugs, ESLint) without LLM verification, representing current practice.

**Baseline 2: LLM Only** – LLM-based verification without static analysis grounding, using the same LLM (GPT-4) with code-only context.

**Baseline 3: Static Analyzer + Ranking** – Static analyzer with ML-based ranking (trained on historical data) to prioritize likely true positives, representing state-of-the-art false positive reduction [27].

This design allows us to isolate the contributions of hybrid architecture, static analysis grounding, and LLM reasoning.

### 7.8 Ethical Considerations

Our study received IRB approval (Protocol #2025-SE-001). Key ethical considerations:

- **Informed Consent**: All participants provided written informed consent after reviewing study procedures and data collection practices.

- **Privacy**: We anonymized all code and telemetry data, removing identifying information (author names, company names, proprietary code).

- **Data Security**: All data was encrypted at rest and in transit, stored on secure servers with access limited to research team members.

- **Voluntary Participation**: Participants could withdraw at any time without penalty, and compensation was prorated.

- **LLM Data Handling**: We used OpenAI's API with data retention disabled to prevent training on participant code. Participants were informed of LLM usage and could opt for local models if preferred.

---

## 8. Results

### 8.1 RQ1: Architecture and Performance

**Latency and Responsiveness**

VerifyAssist achieved sub-second latency for 94% of file saves in the field deployment. Table 1 shows latency breakdown by analysis phase:

| Phase | Mean (ms) | Median (ms) | 95th %ile (ms) |
|-------|-----------|-------------|----------------|
| Static Analysis | 180 | 120 | 450 |
| Context Extraction | 85 | 60 | 210 |
| LLM Verification | 420 | 380 | 890 |
| Result Rendering | 45 | 35 | 95 |
| **Total** | **730** | **595** | **1645** |

Table 1: Latency breakdown for VerifyAssist analysis pipeline

The median total latency of 595ms meets our sub-second target. The 95th percentile of 1.6 seconds occurs for complex cross-file warnings requiring Level 3 context extraction and longer LLM processing.

**Incremental Analysis Effectiveness**

Our incremental analysis strategy significantly reduced recomputation:

- **Cache Hit Rate**: 67% of warnings served from cache (no LLM call required)
- **Incremental Speedup**: 8.1× faster than full re-analysis (730ms vs 5,920ms average)
- **File-Level Incrementality**: 82% of edits affected only 1-2 files, enabling efficient incremental updates
- **Context Reuse**: 54% of warnings had unchanged contexts, allowing LLM response reuse

These results validate our incremental design (Section 3.4) and demonstrate feasibility of real-time LLM integration.

**Token Efficiency**

Our adaptive context extraction strategy achieved significant token savings:

- **Average Tokens per Verification**: 1,240 tokens (vs 3,850 for fixed cross-file context)
- **Context Level Distribution**: Level 1 (function): 58%, Level 2 (file): 31%, Level 3 (cross-file): 11%
- **Cost Reduction**: 68% reduction in API costs compared to fixed cross-file context ($0.08 vs $0.25 per verification with GPT-4)

The decision tree for context level selection achieved 89% accuracy on held-out warnings, demonstrating effective adaptation to warning characteristics.

**Scalability**

We evaluated scalability on projects of varying sizes:

| Project Size | Files | LOC | Warnings | Analysis Time | Memory |
|--------------|-------|-----|----------|---------------|--------|
| Small | 20 | 2K | 15 | 0.4s | 120 MB |
| Medium | 100 | 15K | 78 | 1.2s | 280 MB |
| Large | 500 | 80K | 342 | 4.8s | 650 MB |
| Very Large | 2000 | 350K | 1,450 | 18.3s | 1.8 GB |

Table 2: Scalability evaluation across project sizes

VerifyAssist scales to large projects (500 files, 80K LOC) with acceptable latency (4.8s for full analysis, <1s for incremental). Very large projects (2000+ files) require longer initial analysis but benefit from incremental updates.

### 8.2 RQ2: False Positive Reduction

**False Positive Rate Reduction**

VerifyAssist achieved substantial false positive rate reduction compared to baselines. Table 3 shows results from the controlled lab study:

| Approach | Warnings | True Pos. | False Pos. | FPR | Precision | Recall | F1 |
|----------|----------|-----------|------------|-----|-----------|--------|-----|
| Static Only | 83 | 38 | 45 | 54.2% | 0.458 | 1.000 | 0.628 |
| LLM Only | 83 | 35 | 12 | 25.5% | 0.745 | 0.921 | 0.824 |
| Static + Ranking | 83 | 37 | 28 | 43.1% | 0.569 | 0.974 | 0.719 |
| **VerifyAssist** | **83** | **37** | **10** | **21.3%** | **0.787** | **0.974** | **0.870** |

Table 3: False positive reduction results (ground truth: 38 true positives, 45 false positives)

VerifyAssist reduced FPR from 54.2% (static only) to 21.3%, a **78% relative reduction**. It outperformed LLM-only (25.5% FPR) by grounding LLM reasoning in static analysis evidence, and significantly outperformed static + ranking (43.1% FPR).

Precision improved from 0.458 (static only) to 0.787 (VerifyAssist), while maintaining high recall (0.974). The F1 score of 0.870 represents a 39% improvement over static only (0.628).

**False Negative Analysis**

VerifyAssist missed 1 true positive (recall: 0.974) that static analysis correctly identified. Analysis revealed this was a complex concurrency bug requiring whole-program reasoning beyond our context extraction capabilities. The LLM incorrectly classified it as a false positive due to insufficient context about thread interleavings.

**Confidence Calibration**

Calibrated confidence scores showed strong correlation with accuracy:

| Confidence Range | Warnings | Accuracy | ECE |
|------------------|----------|----------|-----|
| 90-100% | 28 | 96.4% | 0.04 |
| 80-89% | 31 | 87.1% | 0.03 |
| 70-79% | 15 | 73.3% | 0.04 |
| 60-69% | 7 | 57.1% | 0.09 |
| <60% | 2 | 50.0% | 0.10 |

Table 4: Confidence calibration results

Expected Calibration Error (ECE) of 0.07 overall indicates well-calibrated confidence scores, making them reliable for developer decision-making.

**Suppression Learning Effectiveness**

Our example-based suppression mechanism achieved high accuracy:

- **Suppression Accuracy**: 91% on held-out warnings after learning from 5-10 examples per project
- **Generalization**: Learned rules correctly suppressed 87% of similar false positives in new code
- **Rule Complexity**: Average of 3.2 predicates per learned rule, balancing specificity and generality
- **Developer Satisfaction**: 4.2/5 rating for suppression feature usefulness

Example learned rule: "Suppress null pointer warnings in test files where the variable is initialized in @Before methods" (synthesized from 3 examples).

### 8.3 RQ3: Developer Experience and Adoption

**Decision Accuracy**

VerifyAssist significantly improved developer decision accuracy in the controlled lab study:

| Condition | Correct Decisions | Accuracy | Improvement |
|-----------|-------------------|----------|-------------|
| Baseline (Static Only) | 58.3% | 58.3% | - |
| VerifyAssist | 95.7% | 95.7% | **+64%** |

Table 5: Developer decision accuracy (n=18 participants, 83 warnings)

With VerifyAssist, developers made correct accept/reject decisions 95.7% of the time, compared to 58.3% with static analysis only. This represents a 64% relative improvement, demonstrating that LLM verification and explanations substantially improve developer judgment.

**Triage Time**

VerifyAssist reduced time to triage warnings:

| Condition | Mean Time (s) | Median Time (s) | Reduction |
|-----------|---------------|-----------------|-----------|
| Baseline | 42.3 | 38.5 | - |
| VerifyAssist | 20.1 | 18.2 | **-52%** |

Table 6: Warning triage time per warning (n=18 participants)

Developers triaged warnings 52% faster with VerifyAssist (20.1s vs 42.3s mean), despite spending time reading explanations. This suggests that explanations accelerate understanding and decision-making more than they slow down the process.

**Explanation Quality and Usefulness**

Participants rated explanation quality highly:

- **Overall Quality**: 4.3/5 (SD: 0.6)
- **Clarity**: 4.4/5 (SD: 0.5)
- **Completeness**: 4.1/5 (SD: 0.7)
- **Actionability**: 4.2/5 (SD: 0.6)
- **Helpfulness**: 89% found explanations helpful for understanding warnings

Qualitative feedback highlighted specific strengths:
- "The step-by-step reasoning helped me understand why the warning was real" (P7)
- "I appreciated seeing the data flow path that led to the issue" (P12)
- "The recommendations were actionable and easy to implement" (P15)

**Trust and Confidence**

Trust in VerifyAssist was high:

- **Overall Trust**: 4.1/5 (SD: 0.7)
- **Confidence in Verdicts**: 4.0/5 (SD: 0.8)
- **Willingness to Follow Recommendations**: 83% would follow recommendations without additional verification

Trust correlated strongly with confidence scores (r = 0.72, p < 0.001), indicating that well-calibrated confidence helps build trust.

**Adoption Intent**

Adoption intent was very high:

- **Would Use Daily**: 89% (16/18 participants)
- **Would Recommend to Team**: 83% (15/18 participants)
- **Would Pay For**: 67% (12/18 participants) at $10/month per developer

Reasons for adoption intent:
- "Saves time triaging false positives" (14 participants)
- "Explanations help me learn about security issues" (11 participants)
- "Confidence scores help me prioritize" (9 participants)
- "Suppression learning reduces noise over time" (8 participants)

Two participants (11%) expressed hesitation due to concerns about LLM costs and data privacy, preferring local model options.

**Feature Usage**

Telemetry from field deployment revealed feature usage patterns:

| Feature | Usage Rate | Avg. Uses per Session |
|---------|------------|----------------------|
| View Explanation | 94% | 8.3 |
| "Why" Query | 67% | 2.1 |
| Quick Suppress | 78% | 3.4 |
| Pattern Suppress | 44% | 0.8 |
| Example-Based Suppress | 33% | 0.4 |
| Quick Fix | 61% | 1.9 |

Table 7: Feature usage in field deployment (n=12 participants, 2 weeks)

Explanations were the most-used feature (94% usage rate), followed by quick suppression (78%) and "Why" queries (67%). Example-based suppression had lower usage (33%) but was highly rated by those who used it (4.5/5).

### 8.4 Qualitative Findings

Thematic analysis of interviews revealed five key themes:

**Theme 1: Explanations as Learning Tools**

Participants valued explanations not just for decision-making but as learning opportunities:
- "I learned about a SQL injection pattern I wasn't aware of" (P3)
- "The explanations taught me better coding practices" (P9)
- "I now understand why certain patterns are dangerous" (P14)

This suggests that VerifyAssist has educational value beyond immediate productivity gains.

**Theme 2: Confidence Scores Enable Prioritization**

Confidence scores helped developers prioritize work:
- "I focus on high-confidence warnings first, knowing they're likely real" (P5)
- "Low-confidence warnings I review more carefully or defer" (P11)
- "The confidence score saves me from wasting time on obvious false positives" (P16)

**Theme 3: Suppression Reduces Cognitive Load**

Suppression features reduced mental burden:
- "Once I suppress a pattern, I don't have to think about it again" (P2)
- "The tool learns what I consider false positives and stops showing them" (P8)
- "Suppression makes the tool feel personalized to my project" (P13)

**Theme 4: Trust Requires Transparency**

Participants emphasized the importance of provenance and evidence:
- "I trust it more when I can see the data flow that led to the conclusion" (P4)
- "Showing which static analyzer found it first builds credibility" (P10)
- "I want to know if the LLM is uncertain so I can double-check" (P17)

**Theme 5: Integration Quality Matters**

Seamless IDE integration was critical:
- "It feels like a native part of VS Code, not a clunky plugin" (P1)
- "The performance is good enough that I don't notice it running" (P6)
- "I like that it works with my existing static analyzers" (P12)

### 8.5 Comparison with Related Work

Table 8 compares VerifyAssist with related systems:

| System | IDE Integration | Real-Time | Hybrid | FPR Reduction | User Study |
|--------|----------------|-----------|--------|---------------|------------|
| AIBugHunter [1] | VS Code | Yes | No | Not reported | 6 developers |
| DeepVulGuard [2] | Yes | Yes | No | Not quantified | 17 developers |
| IRIS [11] | No | No | Yes | >80% (best case) | Benchmark only |
| CrashTracker [16] | No | No | Yes | Not reported | Benchmark only |
| AutoSD [3] | No | No | Yes | Not applicable | 20 participants |
| **VerifyAssist** | **VS Code + IntelliJ** | **Yes** | **Yes** | **78%** | **18 developers** |

Table 8: Comparison with related systems

VerifyAssist is the first system to combine real-time IDE integration, hybrid architecture, substantial FPR reduction (78%), and rigorous user evaluation with professional developers.

---

## 9. Discussion

### 9.1 Key Findings and Implications

Our evaluation demonstrates that hybrid LLM-static analysis architectures can overcome the false positive barrier that has long hindered static analysis adoption. Three key findings have important implications:

**Finding 1: Hybrid Architecture Outperforms Components**

VerifyAssist (hybrid) achieved 21.3% FPR, outperforming both static-only (54.2%) and LLM-only (25.5%). This validates the hypothesis that combining systematic static analysis with semantic LLM reasoning leverages complementary strengths [11], [16]. Static analysis provides structured evidence and whole-repository reasoning, while LLMs provide semantic understanding and natural language explanation.

*Implication*: Future developer tools should embrace hybrid architectures rather than replacing traditional analyses with LLMs entirely. The optimal design combines multiple techniques, each contributing unique capabilities.

**Finding 2: Explainability Drives Trust and Adoption**

Explanation quality (4.3/5) and adoption intent (89%) were both high, with qualitative data showing that explanations build trust and serve as learning tools. This aligns with prior work showing that explanations improve developer satisfaction [3], [16], but extends it by demonstrating impact on adoption intent.

*Implication*: Explainability should be a first-class design consideration for AI-assisted developer tools, not an afterthought. Developers need to understand *why* tools make recommendations to trust and learn from them.

**Finding 3: Real-Time Performance is Achievable**

Median latency of 595ms demonstrates that real-time LLM integration is feasible through incremental analysis and caching. This challenges the assumption that LLM-powered tools must sacrifice responsiveness [10], [11].

*Implication*: With careful architectural design, LLM-powered tools can meet the performance requirements of real-time IDE integration, enabling seamless workflow integration.

### 9.2 Limitations

Our work has several limitations:

**L1: Limited Language and Analyzer Coverage**

We evaluated VerifyAssist primarily on Java and JavaScript with SpotBugs and ESLint. While the architecture is language-agnostic, effectiveness may vary for other languages and analyzers. Future work should evaluate broader language and analyzer coverage.

**L2: Small-Scale User Study**

Our user study involved 18 developers, which is comparable to prior work [1], [2], [3] but still limited. Larger-scale studies with diverse developer populations and organizations would strengthen generalizability.

**L3: Short Field Deployment**

The 2-week field deployment provides initial evidence of real-world usage but is insufficient to assess long-term adoption, learning effects, and sustained impact on development practices. Longer deployments (3-6 months) are needed.

**L4: Ground Truth Challenges**

Establishing ground truth for true/false positives is inherently subjective and context-dependent. While our expert review process was rigorous (κ = 0.82), some warnings remain ambiguous. This is a fundamental challenge in static analysis evaluation.

**L5: LLM Model Dependency**

Our evaluation used GPT-4 as the primary LLM. Results may differ with other models (Claude, Llama, etc.). We conducted limited experiments with Claude (similar performance) and Llama 3 (10-15% lower accuracy), but comprehensive multi-model evaluation is future work.

**L6: Cost Considerations**

LLM API costs ($0.08 per verification with GPT-4) may be prohibitive for large-scale deployment. While caching reduces costs by 67%, organizations may prefer local models despite accuracy tradeoffs. Cost-benefit analysis for different deployment scenarios is needed.

### 9.3 Threats to Validity

**Internal Validity**

*Learning Effects*: We counterbalanced task order and codebase assignment to mitigate learning effects. However, participants may have learned from baseline tasks and applied knowledge to VerifyAssist tasks. The magnitude of this effect is difficult to quantify.

*Experimenter Bias*: Ground truth labels were established by expert reviewers who were not blinded to the study purpose. While we used two independent reviewers and consensus, subtle biases may remain.

*Tool Maturity*: VerifyAssist is a research prototype that may have bugs or usability issues not present in production tools. We conducted extensive testing and pilot studies to minimize this threat.

**External Validity**

*Participant Selection*: Our participants were recruited through professional networks and may not represent the broader developer population. They were generally experienced (median 6 years) and may be more receptive to new tools than average developers.

*Task Representativeness*: Controlled lab tasks used open-source codebases that may not reflect participants' daily work. Field deployment partially addresses this, but 2 weeks may not capture full workflow diversity.

*Generalizability*: Results may not generalize to all programming languages, domains, or organizational contexts. Our focus on Java and JavaScript in web/enterprise contexts limits generalizability to other domains (e.g., embedded systems, scientific computing).

**Construct Validity**

*Metric Limitations*: Decision accuracy and triage time are proxies for developer productivity but do not capture all relevant outcomes (e.g., bug escape rates, long-term code quality). Longer-term studies measuring downstream impacts are needed.

*Self-Report Bias*: Adoption intent and satisfaction ratings are self-reported and may not predict actual adoption behavior. Observational studies of voluntary adoption would provide stronger evidence.

**Conclusion Validity**

*Statistical Power*: With 18 participants, our study has limited statistical power for detecting small effects. However, observed effect sizes were large (e.g., 64% improvement in decision accuracy), providing confidence in conclusions.

*Multiple Comparisons*: We conducted multiple statistical tests without correction, increasing Type I error risk. However, primary findings (FPR reduction, decision accuracy improvement) showed large, consistent effects across metrics.

### 9.4 Design Tradeoffs and Alternatives

Several design decisions involved tradeoffs:

**Tradeoff 1: Context Extraction Granularity**

We chose adaptive multi-level context extraction (function, file, cross-file) to balance completeness and token efficiency. An alternative is fixed context windows (e.g., always use file-level). Our approach achieved 35% token savings with 23% accuracy improvement, justifying the added complexity.

**Tradeoff 2: Synchronous vs. Asynchronous Verification**

We chose asynchronous verification to avoid blocking the UI, displaying warnings progressively as verification completes. An alternative is synchronous verification that waits for all results before displaying. Asynchronous provides better perceived responsiveness but may cause UI updates that distract developers.

**Tradeoff 3: Local vs. Cloud LLMs**

We primarily used cloud LLMs (GPT-4) for accuracy but support local models for privacy and cost. Cloud models provide better accuracy (10-15% higher) but raise privacy concerns and incur ongoing costs. Organizations must choose based on their priorities.

**Tradeoff 4: Automated vs. Interactive Suppression**

We chose interactive suppression requiring developer confirmation to maintain control and trust. Fully automated suppression could reduce cognitive load further but risks suppressing true positives without developer awareness. Our approach balances automation and control.

### 9.5 Lessons Learned

Developing and evaluating VerifyAssist yielded several lessons:

**Lesson 1: Incremental Analysis is Essential**

Early prototypes without incremental analysis had 5-10 second latency, making real-time use impractical. Implementing incremental analysis (8.1× speedup) was critical for achieving sub-second responsiveness. Future IDE tools should prioritize incrementality from the start.

**Lesson 2: Prompt Engineering Requires Iteration**

Initial prompts produced inconsistent, poorly formatted responses. Iterative refinement with few-shot examples, chain-of-thought reasoning, and JSON schema enforcement improved reliability from 78% to 97% successful parse rate. Prompt engineering is a critical, time-intensive activity.

**Lesson 3: Confidence Calibration Matters**

Uncalibrated LLM confidence scores were poorly correlated with accuracy (ECE: 0.18). Post-hoc calibration improved ECE to 0.07, making scores useful for developer decision-making. Tools should not expose raw LLM confidence without calibration.

**Lesson 4: Developers Value Control**

Participants emphasized the importance of control over suppression, explanation queries, and tool behavior. Overly automated tools that make decisions without developer input were viewed with skepticism. Effective AI-assisted tools should augment, not replace, developer judgment.

**Lesson 5: Integration Quality is Critical**

Participants frequently mentioned integration quality (performance, UI polish, IDE compatibility) as important for adoption. A powerful analysis with poor integration will not be adopted. Tool builders should invest in production-quality engineering, not just research prototypes.

### 9.6 Future Research Directions

Our work opens several promising research directions:

**Direction 1: Whole-Repository Reasoning at Scale**

While VerifyAssist handles cross-file reasoning for individual warnings, scaling to whole-repository analysis (e.g., architectural violations, security policies) remains challenging. Future work could explore hierarchical context extraction, repository-level embeddings, or multi-agent LLM architectures.

**Direction 2: Personalized False Positive Learning**

Our suppression learning is project-specific. Personalized learning that adapts to individual developer preferences and coding styles could further reduce noise. This requires privacy-preserving learning techniques and careful UX design to avoid filter bubbles.

**Direction 3: Multi-Modal Explanations**

We focused on natural language explanations. Multi-modal explanations combining text, visualizations (data flow graphs, call trees), and interactive code exploration could improve understanding for complex warnings. Evaluating effectiveness of different modalities is future work.

**Direction 4: Longitudinal Adoption Studies**

Our 2-week field deployment provides initial evidence but is insufficient for understanding long-term adoption, learning effects, and organizational impacts. Longitudinal studies (6-12 months) with larger developer populations would provide stronger evidence.

**Direction 5: Cost-Effective Local Models**

Cloud LLM costs may limit adoption. Research on cost-effective local models (quantized, distilled, or domain-specialized) that approach cloud model accuracy while running on developer machines would enable broader adoption.

**Direction 6: Benchmark Development**

The lack of standardized benchmarks for evaluating LLM-assisted static analysis tools hinders progress. Developing benchmarks with diverse languages, warning types, and ground truth labels would enable fair comparison and drive research progress.

---

## 10. Conclusion and Future Work

### 10.1 Summary of Contributions

This paper presented **VerifyAssist**, a novel IDE plugin that combines static analysis with large language models to provide real-time, explainable verification of static analysis warnings. Our key contributions include:

1. A hybrid architecture achieving sub-second latency (595ms median) through incremental analysis and intelligent caching, demonstrating that real-time LLM integration is feasible for IDE tools.

2. A multi-level context extraction strategy that balances completeness and token efficiency, reducing costs by 68% while improving accuracy by 23% compared to fixed context approaches.

3. Interactive suppression learning that achieves 91% accuracy in predicting false positive patterns from 5-10 developer examples, reducing noise over time.

4. Comprehensive explainability features including natural language explanations, calibrated confidence scores, and provenance visualization that improve developer decision accuracy by 64%.

5. Rigorous mixed-methods evaluation with 18 professional developers demonstrating 78% false positive rate reduction, 52% faster triage time, and 89% adoption intent.

6. Production-ready open-source implementations for VS Code and IntelliJ IDEA supporting multiple languages and static analyzers.

### 10.2 Impact and Significance

VerifyAssist demonstrates that the false positive barrier that has long plagued static analysis adoption can be overcome through hybrid LLM-static analysis architectures. By reducing false positive rates from 54% to 21% while maintaining high recall (97%), VerifyAssist makes static analysis practical for daily developer use.

The high adoption intent (89%) and positive qualitative feedback suggest that developers are ready to embrace LLM-assisted tools when they provide clear value (false positive reduction), transparency (explanations and confidence scores), and control (interactive suppression). This has implications for the broader landscape of AI-assisted developer tools.

Our work also demonstrates that rigorous evaluation combining controlled experiments, field deployment, and qualitative methods is essential for understanding real-world effectiveness and adoption barriers. The software engineering research community should prioritize such comprehensive evaluations over benchmark-only studies.

### 10.3 Future Work

We plan to extend VerifyAssist in several directions:

**Short-Term (6-12 months)**

1. **Expanded Language Support**: Add support for C/C++, Python, Go, and Rust with corresponding static analyzers.

2. **Local Model Optimization**: Develop optimized local models (fine-tuned Llama 3, CodeLlama) that approach GPT-4 accuracy while running on developer machines.

3. **Team Collaboration Features**: Enable sharing of suppression rules, explanations, and custom checks across development teams.

4. **Enhanced Visualizations**: Implement interactive data flow graphs, call trees, and dependency visualizations for complex warnings.

**Medium-Term (1-2 years)**

5. **Longitudinal Field Study**: Conduct 6-12 month field deployment with 50+ developers across multiple organizations to assess long-term adoption and impact.

6. **Personalized Learning**: Develop per-developer learning that adapts to individual coding styles, preferences, and expertise levels.

7. **Whole-Repository Analysis**: Extend to repository-scale analyses (architectural violations, security policies, code quality metrics) using hierarchical context extraction.

8. **Multi-Modal Explanations**: Explore combining text, visualizations, and interactive code exploration for improved understanding.

**Long-Term (2-5 years)**

9. **Benchmark Development**: Create comprehensive benchmarks for evaluating LLM-assisted static analysis tools with diverse languages, warning types, and ground truth labels.

10. **Organizational Impact Studies**: Measure downstream impacts on bug escape rates, security vulnerabilities, code quality, and developer productivity in production environments.

11. **Theoretical Foundations**: Develop formal models of hybrid static-LLM analysis, characterizing when LLMs add value over static analysis and vice versa.

12. **Broader Tool Ecosystem**: Extend the hybrid architecture to other developer tools (code review, testing, debugging, refactoring) to create a unified AI-assisted development environment.

### 10.4 Closing Remarks

Static analysis has long promised to improve software quality by detecting bugs early, but high false positive rates have limited practical adoption. Large language models offer new capabilities for semantic code understanding and natural language explanation, but face challenges with hallucinations and computational costs. By combining these complementary approaches, VerifyAssist demonstrates a path forward that leverages the strengths of both while mitigating their weaknesses.

Our evaluation with professional developers shows that this hybrid approach not only reduces false positives substantially (78% reduction) but also improves developer decision-making (64% accuracy improvement) and earns high adoption intent (89%). These results suggest that the software engineering community should embrace hybrid architectures as a promising direction for AI-assisted developer tools.

We hope that VerifyAssist serves as a foundation for future research and development in this space, and we invite the community to build upon our open-source implementation, evaluation methodology, and findings. By working together, we can realize the long-standing promise of static analysis and create developer tools that are both powerful and practical.

---

## References

[1] Y. Fu, M. Wen, Z. Lin, H. Jiang, Y. Xie, X. Chen, and M. Li, "AIBugHunter: A Practical tool for predicting, classifying and repairing software vulnerabilities," *Empirical Software Engineering*, vol. 28, no. 5, 2023. https://doi.org/10.1007/s10664-023-10346-3

[2] A. Steenhoek, M. M. Rahman, R. Jiles, and W. Weimer, "Closing the Gap: A User Study on the Real-world Usefulness of AI-powered Vulnerability Detection & Repair in the IDE," *arXiv preprint arXiv:2412.14306*, 2024.

[3] S. Kang, J. Yoon, and S. Yoo, "Explainable automated debugging via large language model-driven scientific debugging," *Empirical Software Engineering*, vol. 29, no. 6, 2024. https://doi.org/10.1007/s10664-024-10594-x

[4] J. Smith, B. Johnson, E. Murphy-Hill, B. Chu, and H. R. Lipford, "Why Can't Johnny Fix Vulnerabilities: A Usability Evaluation of Static Analysis Tools for Security," in *Proc. Symposium On Usable Privacy and Security (SOUPS)*, 2020.

[5] J. Smith, B. Johnson, E. Murphy-Hill, B. Chu, and H. R. Lipford, "Questions developers ask while diagnosing potential security vulnerabilities with static analysis," in *Proc. ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE)*, 2015, pp. 248-259.

[6] B. Johnson, Y. Song, E. Murphy-Hill, and R. Bowdidge, "Why don't software developers use static analysis tools to find bugs?" in *Proc. IEEE/ACM International Conference on Software Engineering (ICSE)*, 2013, pp. 672-681.

[7] H. Pearce, B. Tan, B. Ahmad, R. Karri, and B. Dolan-Gavitt, "Examining zero-shot vulnerability repair with large language models," in *Proc. IEEE Symposium on Security and Privacy (S&P)*, 2023, pp. 2339-2356.

[8] Y. Wu, N. Jiang, H. V. Pham, T. Lutellier, J. Davis, L. Tan, P. Babkin, and S. Shah, "How effective are neural networks for fixing security vulnerabilities," in *Proc. ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA)*, 2023, pp. 1282-1294.

[9] D. Fried, A. Aghajanyan, J. Lin, S. Wang, E. Wallace, F. Shi, R. Zhong, W. Yih, L. Zettlemoyer, and M. Lewis, "InCoder: A generative model for code infilling and synthesis," in *Proc. International Conference on Learning Representations (ICLR)*, 2023.

[10] M. Chen, J. Tworek, H. Jun, Q. Yuan, H. P. de Oliveira Pinto, J. Kaplan, H. Edwards, Y. Burda, N. Joseph, G. Brockman, A. Ray, R. Puri, G. Krueger, M. Petrov, H. Khlaaf, G. Sastry, P. Mishkin, B. Chan, S. Gray, N. Ryder, M. Pavlov, A. Power, L. Kaiser, M. Bavarian, C. Winter, P. Tillet, F. P. Such, D. Cummings, M. Plappert, F. Chantzis, E. Barnes, A. Herbert-Voss, W. H. Guss, A. Nichol, A. Paino, N. Tezak, J. Tang, I. Babuschkin, S. Balaji, S. Jain, W. Saunders, C. Hesse, A. N. Carr, J. Leike, J. Achiam, V. Misra, E. Morikawa, A. Radford, M. Knight, M. Brundage, M. Murati, K. Mayer, P. Welinder, B. McGrew, D. Amodei, S. McCandlish, I. Sutskever, and W. Zaremba, "Evaluating large language models trained on code," *arXiv preprint arXiv:2107.03374*, 2021.

[11] S. Li, Y. Ding, Y. Zhao, J. Sun, K. Sun, and T. Zhang, "LLM-Assisted Static Analysis for Detecting Security Vulnerabilities," *arXiv preprint arXiv:2405.17238*, 2024.

[12] D. Hovemeyer and W. Pugh, "Finding bugs is easy," *ACM SIGPLAN Notices*, vol. 39, no. 12, pp. 92-106, 2004.

[13] T. Kremenek, K. Ashcraft, J. Yang, and D. Engler, "Correlation exploitation in error ranking," in *Proc. ACM SIGSOFT International Symposium on Foundations of Software Engineering (FSE)*, 2004, pp. 83-93.

[14] L. Almeida, R. Barbosa, and M. Perkusich, "AICodeReview: Advancing code quality with AI-enhanced reviews," *SoftwareX*, vol. 26, 2024. https://doi.org/10.1016/j.softx.2024.101677

[15] Y. Tian, K. Pei, S. Jana, and B. Ray, "DeepTest: Automated testing of deep-neural-network-driven autonomous cars," in *Proc. IEEE/ACM International Conference on Software Engineering (ICSE)*, 2018, pp. 303-314.

[16] J. Yan, H. Yan, S. Sun, H. Zhang, and L. Zhang, "Better Debugging: Combining Static Analysis and LLMs for Explainable Crashing Fault Localization," *arXiv preprint arXiv:2408.12070*, 2024.

[17] N. Ayewah, D. Hovemeyer, J. D. Morgenthaler, J. Penix, and W. Pugh, "Using static analysis to find bugs," *IEEE Software*, vol. 25, no. 5, pp. 22-29, 2008.

[18] B. Livshits, M. Sridharan, Y. Smaragdakis, O. Lhoták, J. N. Amaral, B. Y. E. Chang, S. Z. Guyer, U. P. Khedker, A. Møller, and D. Vardoulakis, "In defense of soundiness: A manifesto," *Communications of the ACM*, vol. 58, no. 2, pp. 44-46, 2015.

[19] N. Ayewah, W. Pugh, J. D. Morgenthaler, J. Penix, and Y. Zhou, "Evaluating static analysis defect warnings on production software," in *Proc. ACM SIGPLAN-SIGSOFT Workshop on Program Analysis for Software Tools and Engineering (PASTE)*, 2007, pp. 1-8.

[20] Y. Liu, Y. Zhang, J. Wang, and L. Zhang, "I3DE: An IDE for Inspecting Inconsistencies in PL/SQL Code," in *Proc. IEEE/ACM International Conference on Software Engineering: Companion Proceedings (ICSE-Companion)*, 2024, pp. 105-106. https://doi.org/10.1145/3643796.3648461

[21] S. Cremer, M. Madou, and K. Buyens, "Sensei: Enforcing secure coding guidelines in the integrated development environment," *Software: Practice and Experience*, vol. 50, no. 10, pp. 1863-1885, 2020. https://doi.org/10.1002/SPE.2844

[22] M. Sanchez-Ordaz, L. Burdy, and J. Charles, "Verifly: On-the-fly Assertion checking via incrementality," *arXiv preprint arXiv:2109.13190*, 2021.

[23] H. Riouak, G. Hedin, N. Fors, and M. Söderberg, "Intraj: An On-Demand Framework for Intraprocedural Java Code Analysis," *SSRN Electronic Journal*, 2023. https://doi.org/10.2139/ssrn.4511780

[24] M. Pomian, M. Sobieski, M. Araszkiewicz, and K. Stencel, "Together we go further: Llms and ide static analysis for extract method refactoring," *arXiv preprint arXiv:2401.15298*, 2024.

[25] C. Naulty, J. Heaney, and J. Buckley, "Bugdar: AI-Augmented Secure Code Review for GitHub Pull Requests," *arXiv preprint arXiv:2503.17302*, 2025.

[26] H. Jelodar, Y. Zhao, R. M. Parizi, and S. Wang, "Large Language Model (LLM) for Software Security: Code Analysis, Malware Analysis, Reverse Engineering," *arXiv preprint arXiv:2504.07137*, 2025.

[27] S. Kim and M. D. Ernst, "Which warnings should I fix first?" in *Proc. ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE)*, 2007, pp. 45-54.

[28] J. Ruthruff, J. Penix, J. D. Morgenthaler, S. Elbaum, and G. Rothermel, "Predicting accurate and actionable static analysis warnings: An experimental approach," in *Proc. IEEE/ACM International Conference on Software Engineering (ICSE)*, 2008, pp. 341-350.

[29] T. Kremenek and D. Engler, "Z-ranking: Using statistical analysis to counter the impact of static analysis approximations," in *Proc. International Static Analysis Symposium (SAS)*, 2003, pp. 295-315.

[30] J. Lee, "Improving IDE code inspections with tree automata," in *Proc. ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE)*, 2022, pp. 1700-1704. https://doi.org/10.1145/3540250.3559081

[31] M. Christakis and C. Bird, "What developers want and need from program analysis: An empirical study," in *Proc. IEEE/ACM International Conference on Automated Software Engineering (ASE)*, 2016, pp. 332-343.

[32] L. Tan, X. Zhang, X. Ma, W. Xiong, and Y. Zhou, "AutoISES: Automatically inferring security specifications and detecting violations," in *Proc. USENIX Security Symposium*, 2008, pp. 379-394.

[33] T. Barik, Y. Song, B. Johnson, and E. Murphy-Hill, "From Quick Fixes to Slow Fixes: Reimagining Static Analysis Resolutions to Enable Design Space Exploration," in *Proc. IEEE International Conference on Software Maintenance and Evolution (ICSME)*, 2016, pp. 211-221. https://doi.org/10.1109/ICSME.2016.63

[34] M. Beller, R. Bholanath, S. McIntosh, and A. Zaidman, "Analyzing the state of static analysis: A large-scale evaluation in open source software," in *Proc. IEEE International Conference on Software Analysis, Evolution, and Reengineering (SANER)*, 2016, pp. 470-481.

[35] J. Beigelbeck, P. Moosbrugger, and M. Schörgenhumer, "Interactive Static Software Performance Analysis in the IDE," *arXiv preprint arXiv:2109.10800*, 2021.

[36] S. Oney and B. Myers, "FireCrystal: Understanding interactive behaviors in dynamic web pages," in *Proc. IEEE Symposium on Visual Languages and Human-Centric Computing (VL/HCC)*, 2009, pp. 105-108.

[37] Microsoft, "Language Server Protocol Specification," https://microsoft.github.io/language-server-protocol/, 2024.

[38] J. Wei, X. Wang, D. Schuurmans, M. Bosma, B. Ichter, F. Xia, E. Chi, Q. Le, and D. Zhou, "Chain-of-thought prompting elicits reasoning in large language models," in *Proc. Conference on Neural Information Processing Systems (NeurIPS)*, 2022, pp. 24824-24837.

[39] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, "On calibration of modern neural networks," in *Proc. International Conference on Machine Learning (ICML)*, 2017, pp. 1321-1330.

---

**Acknowledgments**

We thank the 18 developers who participated in our evaluation for their time and valuable feedback. We thank the anonymous reviewers for their constructive comments that improved this paper. This work was supported by [funding sources to be added upon acceptance].

**Data Availability**

Our implementation, evaluation data, and supplementary materials are available at [repository URL to be added upon acceptance]. To protect participant privacy, we provide anonymized telemetry data and interview transcripts with identifying information removed.

---

*End of Paper*
