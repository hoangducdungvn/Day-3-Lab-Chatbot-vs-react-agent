# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Alpha
- **Team Members**: Hoang
- **Deployment Date**: 2026-06-01

---

## 1. Executive Summary

*Brief overview of the agent's goal and success rate compared to the baseline chatbot.*

- **Success Rate**: 100% on tested scenarios (successfully handled broken tools and multi-step logic).
- **Key Outcome**: Our agent solved 100% of multi-step queries by using the ReAct loop and correctly utilizing the `check_stock` and `web_search` tools. In contrast, the Chatbot baseline (tested via `chatbot.py`) severely hallucinated stock numbers because it lacked tool access.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
The system implements a strict `Thought-Action-Observation` loop. We modified the System Prompt to strictly forbid the LLM from generating its own `Observation`, forcing it to yield control back to the environment. We also implemented a retry mechanism that catches parsing errors up to 3 times before aborting.

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `calculate` | `string` | Evaluate mathematical expressions. |
| `check_stock` | `string` | Check the stock quantity of a specific item. |
| `broken_tool` | `string` | A tool designed to fail, used to test Agent's error recovery. |
| `web_search` | `string` | Retrieve real-time mock web data (e.g. Weather, President). |

### 2.3 LLM Providers Used
- **Primary**: GPT-4o-mini (openai)
- **Secondary (Backup)**: Gemini 1.5 Flash (google)

---

## 3. Telemetry & Performance Dashboard

*Analyze the industry metrics collected during the final test run.*

- **Average Latency (P50)**: ~1500ms per step
- **Average Tokens per Task**: ~250-300 tokens per step
- **Total Cost of Test Suite**: Calculated accurately in `metrics.py` based on industry standard pricing (e.g. $0.15 / 1M input tokens for GPT-4o-mini).

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Environment Hallucination
- **Input**: "Please use the broken_tool on 'test' and then calculate 10 + 20."
- **Observation**: The Agent initially generated the Thought, Action, Observation, and Final Answer all in one step without ever executing the tool.
- **Root Cause**: The System Prompt presented the format but did not strictly enforce stopping after the `Action`.
- **Fix**: Implemented `CRITICAL RULES` in the prompt and added a max retry mechanism (Guardrail).

---

## 5. Ablation Studies & Experiments

### Experiment 1: Strict vs Loose Prompt (via `ablation_test.py`)
- **Diff**: We tested a Strict Prompt (with CRITICAL RULES) vs a Loose Prompt (just format).
- **Result**: The Strict Prompt successfully caused the agent to pause, execute the tool, catch the error, and self-correct. The Loose Prompt failed instantly due to hallucination.

### Experiment 2 (Bonus): Chatbot vs Agent (via `chatbot.py`)
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Q | Correct | Correct | Draw |
| Multi-step | Hallucinated | Correct | **Agent** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**: Python's `eval()` in the `calculate` tool is highly insecure. Need to sandbox it or use a safe math parser in production.
- **Guardrails**: Added a `consecutive_errors` counter. Max 3 parsing errors before the system aborts to save billing costs.
- **Scaling**: Extracted cost calculation logic into `metrics.py` to allow tracking real billing across multiple providers.
