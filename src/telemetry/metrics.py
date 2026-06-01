import time
from typing import Dict, Any, List
from src.telemetry.logger import logger

class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs.
    """
    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Logs a single request metric to our telemetry.
        """
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(model, usage) # Mock cost calculation
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """
        Implement real pricing logic based on industry rates.
        """
        # Costs per 1M tokens in USD
        pricing = {
            "gpt-4o-mini": {"prompt": 0.150, "completion": 0.600},
            "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.300},
            "local": {"prompt": 0.0, "completion": 0.0} # Local models are free
        }
        
        # Determine the base model key for pricing
        model_key = "local"
        if "gpt" in model.lower():
            model_key = "gpt-4o-mini"
        elif "gemini" in model.lower():
            model_key = "gemini-1.5-flash"
            
        model_pricing = pricing.get(model_key, pricing["local"])
        
        prompt_cost = (usage.get("prompt_tokens", 0) / 1000000.0) * model_pricing["prompt"]
        completion_cost = (usage.get("completion_tokens", 0) / 1000000.0) * model_pricing["completion"]
        
        return prompt_cost + completion_cost

# Global tracker instance
tracker = PerformanceTracker()
