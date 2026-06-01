# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hoàng Đức Dũng
- **Student ID**: 2A202600814
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase.*

- **Modules Implementated**: `src/agent/agent.py` (ReAct Loop logic), `demo_agent.py` (Provider Switching implementation), `metrics.py` (Cost Tracking).
- **Code Highlights**: Implemented `consecutive_errors` guardrail in `agent.py` to break out of parsing/hallucination loops after 3 failed attempts, preventing infinite LLM API charges.
- **Documentation**: Built the `ablation_test.py` to scientifically prove the effectiveness of our prompt engineering approach.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: LLM Environment Hallucination (Skipping tool execution).
- **Log Source**: `logs/YYYY-MM-DD.log` (event: `LLM_METRIC`, steps: 1).
- **Diagnosis**: The LLM tried to complete the entire Thought-Action-Observation cycle in a single text generation block. It did this because the system prompt merely showed the format but did not explicitly command the LLM to STOP after outputting the Action.
- **Solution**: Updated `get_system_prompt()` to add `CRITICAL RULES`, explicitly commanding the model to NOT output the `Observation:` line and wait for the system to provide it.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: The `Thought` block acts as a "Chain of Thought" scratchpad, allowing the LLM to plan its steps before acting. This is impossible for a direct chatbot which just predicts the immediate final answer based on its training weights.
2.  **Reliability**: The Agent actually performs *worse* (slower and more expensive) than the Chatbot on trivial questions (e.g., "What is 1+1?") because of the overhead of parsing tools and multiple network trips.
3.  **Observation**: The environment feedback is the defining feature of the Agent. In the `broken_tool` test, the observation returned a Python `ValueError` exception. The Agent read this exception and intelligently decided to move on to the next step rather than crashing.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Switch the synchronous while loop to an async architecture (e.g. using `asyncio`) to allow multiple agents to run in parallel.
- **Safety**: Remove the dangerous `eval()` function in the calculation tool and replace it with a containerized code execution environment (like Docker or E2B).
- **Performance**: Stop using Regex for Action parsing. Instead, adopt native **Tool/Function Calling APIs** (provided by OpenAI and Gemini) to guarantee 100% reliable JSON outputs for tool arguments.
