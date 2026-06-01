import os
from dotenv import load_dotenv

from src.core.gemini_provider import GeminiProvider
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.telemetry.logger import logger
from demo_agent import tools, get_provider

def main():
    load_dotenv(override=True)
    
    try:
        # Use Gemini for testing to save OpenAI credits, or change to openai if you prefer
        provider = get_provider("openai")
    except Exception as e:
        print(f"Error loading provider: {e}")
        return
        
    print("=======================================================")
    print("=== ABLATION EXPERIMENT: Strict vs Loose Prompt ===")
    print("=======================================================")
    
    query = "Please use the broken_tool on 'test', then calculate 50 + 50."
    print(f"Test Query: {query}")
    
    # 1. Strict Agent (uses the standard prompt we fixed)
    print("\n---> [Running Agent 1: STRICT Prompt (Default)]")
    strict_agent = ReActAgent(llm=provider, tools=tools, max_steps=5)
    result_strict = strict_agent.run(query)
    print(f"Result (Strict): {result_strict}")
    
    # 2. Loose Agent (uses a bad prompt to force hallucination)
    print("\n---> [Running Agent 2: LOOSE Prompt]")
    loose_agent = ReActAgent(llm=provider, tools=tools, max_steps=5)
    
    # Monkey-patch the prompt to be "loose"
    def loose_prompt():
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in tools])
        return f"""
        You are an intelligent assistant. You have access to the following tools:
        {tool_descriptions}
        
        Use the following format:
        Thought: your line of reasoning.
        Action: tool_name(arguments)
        Observation: result of the tool call.
        Final Answer: your final response.
        """
    loose_agent.get_system_prompt = loose_prompt
    
    result_loose = loose_agent.run(query)
    print(f"Result (Loose): {result_loose}")

    print("\n=======================================================")
    print("=== EXPERIMENT COMPLETE ===")
    print("Nhận xét Thực nghiệm (Ablation):")
    print("- Strict Agent (Agent 1) sẽ chạy qua nhiều bước, gọi tool và bắt lỗi thành công.")
    print("- Loose Agent (Agent 2) rất dễ bị 'ảo giác', tự bịa ra Observation và trả về kết quả ngay lập tức.")
    print("- Lưu kết quả này vào báo cáo để lấy điểm thưởng (Bonus) nhé!")

if __name__ == "__main__":
    main()
