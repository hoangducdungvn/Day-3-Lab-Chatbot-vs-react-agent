import os
import argparse
from dotenv import load_dotenv

from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.telemetry.logger import logger

def get_provider(provider_name: str):
    if provider_name == "openai":
        return OpenAIProvider(model_name="gpt-4o-mini")
    elif provider_name == "gemini":
        return GeminiProvider(model_name="gemini-1.5-flash")
    elif provider_name == "local":
        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        return LocalProvider(model_path=model_path)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

def main():
    parser = argparse.ArgumentParser(description="Run Baseline Chatbot (No Tools)")
    parser.add_argument("--provider", type=str, default="local", choices=["openai", "gemini", "local"], help="LLM Provider to use")
    args = parser.parse_args()

    load_dotenv(override=True)
    
    print(f"\n=======================================================")
    print(f"--- CHATBOT BASELINE (Không có Tools) ---")
    print(f"Khởi tạo provider: {args.provider.upper()}")
    print(f"=======================================================")
    
    try:
        provider = get_provider(args.provider)
    except Exception as e:
        print(f"Lỗi khởi tạo provider: {e}")
        return

    # A complex multi-step query that requires real-world data and local file creation
    query = "Hãy làm cho tôi một đoạn nhạc lofi dài 8 bars, nhịp điệu chậm rãi 80 BPM, tone C."
    
    print(f"\nUser: {query}\n")
    logger.info(f"=== BẮT ĐẦU CHẠY CHATBOT ({args.provider.upper()}) ===")
    
    system_prompt = "You are a helpful AI Music Generator. Answer the user's questions to the best of your ability."
    
    try:
        result = provider.generate(query, system_prompt=system_prompt)
        print(f"\nChatbot Response:\n{result.get('content')}")
        
        # Log metric for chatbot to show token usage
        logger.log_event("CHATBOT_METRIC", {
            "content": result.get("content"),
            "usage": result.get("usage", {}),
            "latency_ms": result.get("latency_ms", 0)
        })
        
    except Exception as e:
        print(f"\nLỗi khi gọi LLM: {e}")
        
    print(f"\n=======================================================")
    print("NHẬN XÉT (Baseline Limitations):")
    print("Chatbot không có khả năng gọi Tool nội bộ để tạo file MIDI hoặc WAV.")
    print("Do đó, nó chỉ có thể sinh ra chữ (Text) mô tả nốt nhạc, không thể tạo ra file .wav thật.")
    print("Đây chính là lý do chúng ta cần đến ReAct Agent!")

if __name__ == "__main__":
    main()
