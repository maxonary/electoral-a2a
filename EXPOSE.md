# Governance for Multi-Agent AI Systems: An Empirical Study of Coordination Architectures

## Introduction
Multi-Agent Systems (MAS) represent a paradigm for solving complex, distributed problems by orchestrating the collaborative and autonomous actions of multiple AI agents. Their increasing prevalence across diverse domains, from autonomous vehicles and supply chain optimization to financial modeling and diagnostic systems, requires robust and measurable coordination mechanisms that can manage heterogeneous inputs and ensure coherent system-level decisions.

### Application domain
This research is specifically applicable to multi-agent AI systems that must merge inputs from expert agents (e.g., planning, data analysis, security assessment) across potentially conflicting objectives or priorities, to ultimately converge on one actionable, system-wide decision.

### Problem
Flat majority voting can overweight populous domains, whereas supervisor models create single points of failure. We lack systematicempirical evidence on how fixed‑weight, winner‑take‑all aggregation influences decision quality and interpretability.

### Research hypothesis  
**H0** Electoral‑style coordination yields decision quality, fairness, and interpretability equal to or worse than baseline models.  
**H1** Electoral‑style coordination leads to **higher interpretability and domain‑level fairness**—and no loss of decision quality—compared with (a) LangGraph Supervisor and (b) LangGraph Swarm architectures.  


## Approach and preliminary results
I will implement three coordination architectures solving an identical decision task (“Select the best cloud‑deployment strategy”):

1. **Electoral model** – the system developed in this thesis.  
2. **Supervisor model** – LangGraph’s `create_supervisor` orchestration.  
3. **Swarm model** – LangGraph’s `create_swarm` hand‑off architecture.

### Experiments
Each model runs 50 trials per scenario across four scenarios: simple consensus, domain conflict, agent‑count imbalance, adversarial noise.

### Metrics
– **Decision quality** semantic correctness  
– **Consensus ratio** weighted votes for winner / total weight  
– **Domain fairness** Gini index of domain influence  
– **Interpretability** qualitative trace rating (1‑5)  
– **Efficiency** latency & token cost  

*Implementation assets* Python 3.12; LangGraph libraries; Streamlit; Plotly; OpenAI ChatGPT4o, Anthropic Claude 4.0 Sonnet, Google Gemini 2.5 Flash

### Preliminary results
![Multi-Agent Architectures](https://langchain-ai.github.io/langgraph/concepts/img/multi_agent/architectures.png)


## Preliminary Structure
1. **Introduction**  
1.1 Background  
1.2 Problem Statement  
1.3 Research Hypothesis  
1.4 Scope and Objectives  
2. **Literature Review**  
2.1 Agent roles and tooling  
2.2 Multi‑agent orchestration  
2.3 Electoral‑College coordination, voting theory  
3. **Methodology (System Design)**
3.1 Electoral‑College model   
3.2 Baseline architectures (Supervisor, Swarm)   
3.3 Experimental Design  
    3.3.1 Tasks and scenarios  
    3.3.2 Metrics  
    3.3.3 Implementation Assets  
4. **Analysis and Results**  
4.1 Quantitative comparison  
4.2 Qualitative analysis  
5. **Discussion and Limitations**  
5.1 Key Findings  
5.2 Secondary Findings  
5.3 Limitations  
5.4 Future Research  
6. **Conclusion**  


Roadmap
| Week | Milestone | Deliverable |
|------|-----------|-------------|
| 1 | Finalise literature survey & detailed design | Chapter 2 draft |
| 2–3 | Implement baseline LangGraph models | Reproducible code |
| 4–5 | Implement Electoral model & logging | Code + system diagram |
| 6 | Run full experiment matrix | Raw result dataset |
| 7 | Analyse results, create figures | Chapters 4–5 drafts |
| 8 | Write Discussion & Conclusion | Chapter 6 draft |
| 9 | Full thesis draft to supervisors | — |
| 10 | Revise & submit | Final PDF + code repo |
