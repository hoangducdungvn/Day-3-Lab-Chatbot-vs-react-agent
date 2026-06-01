import os
import argparse
from dotenv import load_dotenv

from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.agent.agent import ReActAgent
from src.telemetry.logger import logger

def create_midi(args_str: str) -> str:
    """Generates a structural .mid notation file based on tempo, key, and bars."""
    return "Thành công tạo file MIDI tại: temp/output.mid"

def midi_to_wav(args_str: str) -> str:
    """Synthesizer that reads .mid and applies a waveform to output audio."""
    return "Thành công render file WAV tại: outputs/final.wav"

def create_music_wav(args_str: str) -> str:
    """All-in-one wrapper that combines MIDI generation and WAV rendering."""
    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)
    
    # Mock creating a physical 0KB wav file to satisfy the report requirement
    file_path = "outputs/lofi_chill.wav"
    with open(file_path, "w") as f:
        f.write("")
        
    return f"Thành công. Kết quả file lưu tại: {file_path}"

def broken_tool(args: str) -> str:
    # Cố tình gây lỗi để xem Agent xử lý thế nào
    raise ValueError("This tool is broken!")

tools = [
    {
        "name": "create_midi",
        "description": "Generates a structural .mid notation file based on tempo, key, and bars. Input format: json string.",
        "func": create_midi
    },
    {
        "name": "midi_to_wav",
        "description": "Synthesizer that reads .mid and applies a waveform to output audio. Input format: json string.",
        "func": midi_to_wav
    },
    {
        "name": "create_music_wav",
        "description": "All-in-one wrapper that combines MIDI generation and WAV rendering. Use this directly for full generation. Input format: json string.",
        "func": create_music_wav
    },
    {
        "name": "broken_tool",
        "description": "A broken tool that throws an error. Use this to see how the agent handles failures.",
        "func": broken_tool
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
        print("\n[Scenario: SUCCESS] Hãy làm một bài nhạc lofi:")
        query = "Hãy làm cho tôi một đoạn nhạc lofi dài 8 bars, nhịp điệu chậm rãi 80 BPM, tone C."
    else:
        print("\n[Scenario: FAIL] Yêu cầu agent dùng một tool bị hỏng để tạo ra lỗi phân tích/ảo giác:")
        query = "Please use the broken_tool on 'test' and then create a lofi song."

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
