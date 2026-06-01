import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from src.core.gemini_provider import GeminiProvider
from src.agent.agent import ReActAgent
from demo_agent import tools, get_provider

load_dotenv(override=True)

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    mode: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # User is successfully using OpenAI based on previous logs
        provider = get_provider("openai")
    except Exception as e:
        return {"error": f"LLM Provider Error: {str(e)}"}

    if req.mode == "baseline":
        system_prompt = "You are a helpful AI Music Generator. Answer the user's questions to the best of your ability."
        result = provider.generate(req.message, system_prompt=system_prompt)
        return {
            "final_answer": result.get("content", "Error generating baseline response."),
            "traces": []
        }
    else:
        # ReAct Agent mode
        agent = ReActAgent(llm=provider, tools=tools, max_steps=5)
        # Use our new method that returns trace UI data
        return agent.run_with_trace(req.message)

@app.get("/")
def serve_ui():
    return FileResponse("chat_ui.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
