import os
import argparse
from dotenv import load_dotenv

from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.agent.agent import ReActAgent
from src.telemetry.logger import logger

# --- ĐỊNH NGHĨA TOOLS MẪU ---
def calculate(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error evaluating expression: {e}"

def check_stock(item_name: str) -> str:
    stock_db = {"iphone": 10, "macbook": 5}
    item_name = item_name.strip(" '\"").lower()
    return f"Stock for {item_name}: {stock_db.get(item_name, 0)}"

def broken_tool(args: str) -> str:
    # Cố tình gây lỗi để xem Agent xử lý thế nào
    raise ValueError("This tool is broken!")

def web_search_mock(query: str) -> str:
    # A mock search tool that returns dynamic content based on query
    query = query.lower()
    if "president" in query or "biden" in query:
        return "The current president is Joe Biden."
    elif "weather" in query:
        return "The weather is currently 25 degrees Celsius and sunny."
    else:
        return f"Search results for: {query}. Found 1,000,000 results."

tools = [
    {
        "name": "calculate",
        "description": "Evaluates a mathematical expression (e.g. '2 + 2'). Returns the result.",
        "func": calculate
    },
    {
        "name": "check_stock",
        "description": "Checks the stock quantity of an item. Argument should be the item name.",
        "func": check_stock
    },
    {
        "name": "broken_tool",
        "description": "A broken tool that throws an error. Use this to see how the agent handles failures.",
        "func": broken_tool
    },
    {
        "name": "web_search",
        "description": "Searches the web for real-time information. Argument should be the search query string.",
        "func": web_search_mock
    }
]

def get_provider(provider_name: str):
    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print(f"[DEBUG] Đã nạp thành công OPENAI_API_KEY từ file .env (bắt đầu bằng: {api_key[:12]}...)")
        else:
            print("[DEBUG] Không tìm thấy OPENAI_API_KEY trong file .env!")
        return OpenAIProvider(model_name="gpt-4o-mini", api_key=api_key)
    elif provider_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        return GeminiProvider(model_name="gemini-1.5-flash", api_key=api_key)
    elif provider_name == "local":
        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        return LocalProvider(model_path=model_path)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

def main():
    parser = argparse.ArgumentParser(description="Run ReAct Agent with Provider Switching")
    parser.add_argument("--provider", type=str, default="openai", choices=["openai", "gemini", "local"], help="LLM Provider to use")
    parser.add_argument("--test", type=str, default="success", choices=["success", "fail"], help="Test scenario")
    args = parser.parse_args()

    load_dotenv(override=True)
    
    print(f"\n=======================================================")
    print(f"--- 1. CHUYỂN ĐỔI NHÀ CUNG CẤP (Provider Switching) ---")
    print(f"Khởi tạo provider: {args.provider.upper()}")
    print(f"=======================================================")
    
    try:
        provider = get_provider(args.provider)
    except Exception as e:
        print(f"Lỗi khởi tạo provider (Có thể thiếu API Key): {e}")
        return
        
    agent = ReActAgent(llm=provider, tools=tools, max_steps=5)

    if args.test == "success":
        print("\n[Scenario: SUCCESS] Hỏi một câu đa bước:")
        query = "I want to buy an iPhone and a Macbook. Please check their stock and calculate the total items available."
    else:
        print("\n[Scenario: FAIL] Yêu cầu agent dùng một tool bị hỏng để tạo ra lỗi phân tích/ảo giác:")
        query = "Please use the broken_tool on 'test' and then calculate 10 + 20."

    print(f"\nUser: {query}\n")
    logger.info(f"=== BẮT ĐẦU CHẠY AGENT ({args.provider.upper()}) ===")
    
    result = agent.run(query)
    
    print(f"\nFinal Result: {result}")
    
    print(f"\n=======================================================")
    print(f"--- 2. PHÂN TÍCH LỖI (Failure Analysis) ---")
    print(f"=======================================================")
    print("Mở thư mục 'logs/' và xem file log (định dạng JSON).")
    print("Nếu chạy '--test fail', bạn sẽ thấy trong file log ghi lại chi tiết Agent bị crash/mắc kẹt khi gọi tool lỗi.")

if __name__ == "__main__":
    main()
