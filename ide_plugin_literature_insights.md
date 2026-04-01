## TL;DR

Real-time IDE plugins exist for static and ML-based analysis (commonly VS Code and IntelliJ); challenges include latency, context size, and false positives. Hybrid pipelines combining static analyses with LLMs, incremental analysis, and interactive suppression are promising research directions.

----

## Existing IDE plugin landscape

This section summarizes representative plugins, their architectures, and the IDEs targeted to ground design decisions for a real-time LLM verification plugin. The examples highlight common features (in-editor alerts, fixes, explanations), integration points, and documented limitations such as false positives or scalability.

- **Representative tools and targets**  
  - **AIBugHunter** integrates ML detectors and repair suggestions into Visual Studio Code, providing real-time detection, localization, severity estimation, explanations, and suggested repairs by combining prior models (LineVul, VulRepair) and transformer-based severity estimation [1].  
  - **DeepVulGuard** is an IDE-integrated detection-and-fix tool used by Microsoft developers; it surfaces alerts, natural-language explanations, and fix suggestions via IDE interfaces and chat interactions [2].  
  - **AICodeReview** implements an IntelliJ plugin that uses GPT-family models (GPT-3.5 / ChatGPT) for automated code review, showing how LLMs have been embedded into JetBrains IDEs [3].  
  - **I3DE** and similar plugins target the IntelliJ platform to surface inconsistency inspections in PL/SQL code [4].  
  - **FixBugs** and other research prototypes show interactive resolution integrations inside Eclipse for static findings [5].  
  - **VeriFly** demonstrates Emacs-based on-the-fly static checking using incremental analysis and editor tooltips [6].  
  - Frameworks and on-demand analyzers have been integrated via LSP or editor extensions in IntraJ and VS Code experiments, indicating LSP and VS Code are common integration targets [7] [8].

- **Typical architectures and features**  
  - **Client-side editor integration** that decorates code with warnings, tooltips, side panels, and quick fixes (AIBugHunter, interactive performance tool) [1] [8].  
  - **Backend analysis engines** (static analyzers, ML/LLM servers) that run asynchronously and return structured alerts and fixes [1] [2] [7].  
  - **Interactive UI affordances** such as explanation panels, chat interfaces, and quick-fix explorations (DeepVulGuard, FixBugs) [2] [5].  
  - **Customization and rule bundles** to tailor checks to team policies (Sensei approach for secure-coding rules) [9].

- **Limitations reported**  
  - **False positives and non-applicable fixes** reduce practical usefulness and trust in practice, reported in field studies of AI-powered vulnerability tools [2] [10].  
  - **Scalability and full-context needs** (whole-repo reasoning) are challenging for LLM-only approaches and motivate hybrid pipelines [11].  
  - **Performance and UI scalability** issues and tool abandonment arise when interfaces do not match developer workflows [10] [12].

----

## Real-time analysis technical challenges

This section explains the main engineering and UX hurdles for on-the-fly analysis and how prior work mitigates them with incremental, on-demand, or asynchronous designs. Focused examples show measured latency and analysis strategies where available.

- **Key technical challenges**  
  - **Latency and responsiveness**: continuous or “as-you-type” checks must keep UI latency low to avoid interrupting flow; per-file plugin timings range from single-digit milliseconds to a few hundred milliseconds in practice [13].  
  - **Whole-repo context and scale**: many security or cross-file defects require repository-scale reasoning that is expensive to compute in real time [11].  
  - **False alarms and noise**: high alarm volumes frustrate developers and cause abandonment unless relevance is improved [10] [12].  
  - **Resource and cost constraints**: running heavy models or analyses for every edit is infeasible on local machines; offloading introduces network latency and availability dependencies [7] [14].

- **How existing tools handle performance and UX**  
  - **On-demand and incremental analyses** use change-driven evaluation to avoid full re-analysis on every keystroke (IntraJ uses on-demand evaluation and Reference Attribute Grammars; VeriFly uses modular incremental analysis) [7] [6].  
  - **Asynchronous backend pipelines** decouple UI updates from long-running analysis, surfacing interim results and marking confidence levels so developers can continue working [8] [1].  
  - **Per-file latency reporting**: a VS Code Laravel plugin measured response times from 1 ms to 382 ms depending on token length, demonstrating feasibility of sub-second in-editor feedback for many checks [13].  
  - **Hybrid static+LLM architectures** mitigate whole-repo cost by using static analysis to extract concise contexts or candidates that are then fed to LLMs for reasoning, balancing accuracy and latency [11] [15].

----

## LLM integration and false positive reduction

This section surveys concrete integrations of LLMs with static analysis, the prompt/context strategies used, and techniques to reduce false positives through automation or interaction. Quantitative results demonstrate gains and remaining gaps.

- **Hybrid pipelines and context extraction**  
  - **IRIS** combines static analysis with GPT-4 to perform whole-repository vulnerability reasoning; it detected 69 of 120 validated vulnerabilities versus 27 by a state-of-the-art static tool, and reduced false alarms by up to **>80%** in the best case by using static analysis to extract relevant context for the LLM [11].  
  - **CrashTracker** extracts structured static-analysis summaries (exception-thrown summaries and candidate information summaries) and then prompts an LLM to produce explanations and rank buggy candidates; localization achieved an **MRR of 0.91**, and LLM explanations improved user satisfaction by **67.04%** [15].  
  - **EM-Assist** uses LLMs for extract-method refactoring by summarizing candidate contexts; it outperformed ML and static peers, e.g., top-5 correct suggestions **60.6%** vs **54.2%** (ML) and **52.2%** (static), and recall on replicated real refactorings **42.1%** vs **6.5%** [16].

- **Prompting strategies and interactive loops**  
  - Papers show practical strategies of precomputing concise, structured summaries (CIS, ETS) or candidate lists via static analysis, then prompting LLMs with focused contexts rather than whole files or repos to improve relevance and reduce hallucinations [15] [11].  
  - **Automated scientific debugging** (AutoSD) uses LLM prompting to generate hypotheses and then drives program debuggers to validate hypotheses, producing explanations and confidence signals that help judges decide correctness; participants preferred explanations and judged patches more accurately on many real bugs [17].  
  - **Editor chat and explanation UIs** are used to let developers query model outputs and provide feedback, which can be used to refine suggestions or suppress irrelevant alerts (DeepVulGuard, AICodeReview) [2] [3].

- **False positive reduction techniques and effectiveness**  
  - **Static prefiltering + LLM refinement**: IRIS demonstrates substantial false-alarm reduction by combining heavyweight static checks with targeted LLM reasoning [11].  
  - **Program-by-example suppression**: synthesis of tree automata from user examples to suppress bogus warnings systematically is effective for recurring patterns reported in production IDE heuristics [18].  
  - **Interactive suppression and design-space exploration**: FixBugs provides interactive resolution workflows (exploring multiple fixes) to avoid over-automated “quick fixes” that may be irrelevant [5].  
  - **Adaptive, feedback-driven notification systems**: proposals for continuous immediate SAST feedback suggest leveraging developer feedback to adapt per-developer or per-project notification thresholds to reduce noise [8] [19].  
  - **Quantitative outcomes**: IRIS reported detection gain (69/120 vs 27/120) and >80% false-alarm reduction best-case [11]; EM-Assist and CrashTracker report substantial metric improvements for refactoring and localization when LLMs are applied to structured contexts [16] [15].

----

## Evaluation methods explainability and research gaps

This section synthesizes study designs, evaluation metrics, explainability approaches, and open research opportunities that would be compelling for top-tier SE conferences.

- **User study methodologies and typical metrics**  
  - **Study types**: lab-based controlled tasks, field deployments with professional developers, surveys, and mixed-methods (quantitative + qualitative) are commonly used (examples: DeepVulGuard field study with 17 professionals; AutoSD lab study with 20 participants; EM-Assist warehouse surveys with ~20 developers) [2] [17] [16].  
  - **Common metrics**: precision/recall/F1 for detectors, MRR for localization, adoption/resolution rates (e.g., 73.8% of automated comments resolved in one large-scale automated review deployment), time-to-merge or pull-request closure time, subjective satisfaction and trust, and qualitative feedback on workflow fit [20] [2] [15].  
  - **Sample sizes and designs**: practitioner field studies often range from a dozen to a few dozen participants (e.g., 16–20 participants) or larger observational deployments across many PRs (thousands of PRs in industrial studies) to capture real-world behavior [16] [5] [2] [20]. Controlled lab studies typically use smaller samples (10–30) with focused tasks [17] [5].

- **Explainability and trust techniques**  
  - **Natural-language explanations** returned by LLMs improve developer judgments and satisfaction (AutoSD reported participants wanted explanations and were more accurate on most bugs; CrashTracker saw a 67% satisfaction improvement) [17] [15].  
  - **Structured visualizations** such as in-editor annotations, side-panels with evidence and links to offending lines, and interactive exploration of alternative fixes increase understandability (interactive performance tool, FixBugs, AIBugHunter) [8] [5] [1].  
  - **Confidence signals and provenance** (e.g., showing which static checks or code slices informed the LLM result) are highlighted as valuable for trust but need more systematic evaluation across tools [17] [11].

- **System architecture patterns for integration**  
  - **Hybrid client-server model**: lightweight editor client (decorations, quick fixes) + backend analysis servers (static analyzers, ML/LLM) is common; communication often uses LSP or custom RPCs [7] [1].  
  - **Incrementality and caching**: on-demand or incremental re-analysis (IntraJ, VeriFly) combined with caching of static analysis artifacts reduces recomputation and latency [7] [6].  
  - **Context extraction pipeline**: static analysis extracts concise contexts or candidate sets that are cached and then sent to an LLM for expensive reasoning; this reduces token usage and latency while improving precision [11] [15].  
  - **Error recovery and UX**: asynchronous results, graceful degradation when backends are unavailable, and interactive suppression or correction workflows improve robustness and developer experience [8] [2] [9].

- **Open problems and opportunities for novel contributions**  
  - **Scalable, low-latency whole-repo reasoning**: improving how to extract, cache, and incrementally update LLM-relevant contexts for repository-scale checks remains an open challenge [11] [7].  
  - **False-positive calibration and personalized suppression**: combining programmatic suppression (PBE/automata) with per-developer feedback loops and trust calibration would address the main practical adoption barrier noted in field studies [18] [8] [10].  
  - **Interactive verification loops**: designs that tightly couple LLM hypotheses with executable checks (e.g., AutoSD’s debugger-driven loop) to produce verifiable explanations and confidence signals deserve more scale and diversity of evaluation [17].  
  - **Robust evaluation at scale**: larger industrial deployments that measure long-term adoption, workflow impact (e.g., PR closure times, bug escape rates), and cost-benefit analyses would strengthen evidence for deployment claims [2] [20].  
  - **Benchmarks for explainability and trust**: standardized tasks and measures (e.g., explanation usefulness, decision accuracy, MRR with explanation) would allow fair comparison across hybrid LLM+static systems [15] [11].

- **What would be novel and conference-worthy**  
  - A system that demonstrates (1) sub-second, incremental LLM verification in-editor at repository scale via cached context extraction, (2) automated, provable false-positive suppression synthesizable from a few developer examples, and (3) a mixed field+lab evaluation showing measurable improvements in precision, developer decision accuracy, and sustained adoption would address multiple gaps identified by prior work and be a strong contribution to ICSE/FSE/ASe/OOPSLA [11] [18] [17] [2].

## References

[1]M. C. Fu et al., “AIBugHunter: A Practical tool for predicting, classifying and repairing software vulnerabilities,” Empirical Software Engineering, vol. 29, no. 1, Nov. 2023, doi: 10.1007/s10664-023-10346-3.

[2]S. Kang, B. Chen, S. Yoo, and J. Lou, “Explainable automated debugging via large language model-driven scientific debugging,” Empirical Software Engineering, vol. 30, no. 2, Dec. 2024, doi: 10.1007/s10664-024-10594-x.

[3]S. Kang, B. Chen, S. Yoo, and J.-G. Lou, “Explainable Automated Debugging via Large Language Model-driven Scientific Debugging,” arXiv.org, vol. abs/2304.02195, Apr. 2023, doi: 10.48550/arXiv.2304.02195.

[4]A. Beigelbeck, M. Aniche, and J. Cito, “Interactive Static Software Performance Analysis in the IDE,” arXiv: Software Engineering, May 2021.

[5]M. Fu et al., “AIBugHunter: A Practical Tool for Predicting, Classifying and Repairing Software Vulnerabilities,” arXiv.org, vol. abs/2305.16615, May 2023, doi: 10.48550/arXiv.2305.16615.

[6]“AIBugHunter: A Practical Tool for Predicting, Classifying and Repairing   Software Vulnerabilities,” May 2023, doi: 10.48550/arxiv.2305.16615.

[7]J. Liu, S. Liu, and J. Chen, “I3DE: An IDE for Inspecting Inconsistencies in PL/SQL Code,” Mar. 2024, doi: 10.1145/3643796.3648461.

[8]“Towards Immediate Feedback for Security Relevant Code in Development   Environments,” July 2022, doi: 10.48550/arxiv.2207.03225.

[9]Y. Lee, “Improving IDE code inspections with tree automata,” Nov. 2022, doi: 10.1145/3540250.3559081.

[10]U. Cihan et al., “Automated Code Review In Practice,” Dec. 2024, doi: 10.48550/arxiv.2412.18531.

[11]T. Barik, Y. Song, B. Johnson, and E. Murphy-Hill, “From Quick Fixes to Slow Fixes: Reimagining Static Analysis Resolutions to Enable Design Space Exploration,” pp. 211–221, Oct. 2016, doi: 10.1109/ICSME.2016.63.

[12]J. Smith, L. N. Q. Do, and E. Murphy-Hill, “Why Can’t Johnny Fix Vulnerabilities: A Usability Evaluation of Static Analysis Tools for Security,” pp. 221–238, Jan. 2020.

[13]B. Steenhoek, K. Sivaraman, R. H. González, Y. Mohylevskyy, R. Z. Moghaddam, and W. Le, “Closing the Gap: A User Study on the Real-world Usefulness of AI-powered   Vulnerability Detection & Repair in the IDE,” Dec. 2024, doi: 10.48550/arxiv.2412.14306.

[14]M. A. Sanchez-Ordaz, I. Garcia-Contreras, V. Perez-Carrasco, J. F. Morales, P. López-García, and M. V. Hermenegildo, “VeriFly: On-the-fly Assertion Checking via Incrementality,” arXiv: Programming Languages, June 2021.

[15]Y. Almeida, D. Albuquerque, Â. Perkusich, and K. de F. Santos, “AICodeReview: Uma Ferramenta para Revisão de Código por Meio de Inteligência Artificial,” Aug. 2023, doi: 10.5753/semish.2023.230568.

[16]Y. Almeida et al., “AICodeReview: Advancing code quality with AI-enhanced reviews,” SoftwareX, May 2024, doi: 10.1016/j.softx.2024.101677.

[17]Z. Li, S. Dutta, and M. Naik, “LLM-Assisted Static Analysis for Detecting Security Vulnerabilities,” May 2024, doi: 10.48550/arxiv.2405.17238.

[18]J. Yan, J. Huang, C. Fang, J. Yan, and J. Zhang, “Better Debugging: Combining Static Analysis and LLMs for Explainable Crashing Fault Localization,” arXiv.org, vol. abs/2408.12070, Aug. 2024, doi: 10.48550/arxiv.2408.12070.

[19]“Towards Immediate Feedback for Security Relevant Code in Development Environments,” pp. 68–75, Jan. 2022, doi: 10.1007/978-3-031-18304-1_4.

[20]Y. Huang, T. D. LaToza, and Z. Yao, “IntelliExplain: Enhancing Interactive Code Generation through Natural   Language Explanations for Non-Professional Programmers,” May 2024, doi: 10.48550/arxiv.2405.10250.