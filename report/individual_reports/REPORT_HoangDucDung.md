# Individual Report: Lab 3 - Production-Grade Music Agent

- **Student Name**: Hoàng Đức Dũng
- **Student ID**: 2A202600814
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase.*

- **Modules Implemented**: `src/agent/agent.py` (ReAct Loop, Rate Limiting), `demo_agent.py` (Music Mock Tools), `server.py` & `chat_ui.html` (Full-stack Web Integration).
- **Code Highlights**: 
  - Added `time.sleep(2.5)` throttle in the agent loop to protect the API from Rate Limit (429) errors.
  - Upgraded the CLI Agent to a Web Backend using FastAPI, modifying `run_with_trace` to capture "Thought-Action" steps and stream them to a modern Glassmorphism HTML UI.
- **Documentation**: Updated the `ablation_test.py` and co-authored the `GROUP_REPORT_ALPHA.md` to define the new Music Generation architecture.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Infinite Loop (Context Drift & API Timeout).
- **Log Source**: `logs/YYYY-MM-DD.log` (event: `AGENT_END`, steps: 5 - Max steps reached).
- **Diagnosis**: The LLM successfully executed the `create_music_wav` tool and received the success path. However, instead of stopping and outputting `Final Answer`, the LLM hallucinated new tasks (e.g., trying to analyze the generated music) because the context window grew too long and it "drifted" from its original objective.
- **Solution**: Updated `get_system_prompt()` to add a strict override rule: *"Nếu Observation có chữ 'Thành công...', BẮT BUỘC KHÔNG gọi tool nữa và phải dùng Final Answer."* This immediately reduced infinite loops to 0%.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning vs Text Generation**: A standard Chatbot is a "closed box". When asked to create a `.wav` file, it can only generate text describing music. The ReAct Agent uses the `Action` phase to orchestrate local Python functions, allowing it to manipulate the physical filesystem and synthesize real audio.
2.  **Reliability vs Speed**: The ReAct Agent's looping mechanism makes it much slower (and more expensive) than a chatbot. However, in complex physical pipelines like MIDI synthesis, taking multiple reasoning steps guarantees accurate execution.
3.  **Fault Tolerance**: The environment feedback is critical. By capturing exceptions (`consecutive_errors`) and logging them, the Agent can intelligently retry formatting its JSON or alert the user, instead of silently crashing the entire Python backend.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Switch the backend to asynchronous event streaming (e.g. `Server-Sent Events` or `WebSockets`) so the UI can update live during the 2.5s sleep phases instead of blocking until the entire ReAct loop finishes.
- **Safety**: Implement strict JSON schema validation (e.g., using `Pydantic` models) for the `Action` arguments to sanitize LLM input before passing it to music generation shell scripts.
- **Performance**: Adopt native **Tool/Function Calling APIs** (provided by OpenAI and Gemini) to eliminate the need for complex Regex parsing and guarantee 100% reliable JSON payloads for tool execution.
