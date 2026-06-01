import os
import re
import time
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        Implement the system prompt that instructs the agent to follow ReAct.
        Should include:
        1.  Available tools and their descriptions.
        2.  Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
        You are an intelligent assistant. You have access to the following tools:
        {tool_descriptions}
        Use the following format:
        Thought: your line of reasoning.
        Action: tool_name(arguments)
        
        CRITICAL RULES:
        1. You must ONLY output ONE Thought and ONE Action per response.
        2. DO NOT output the "Observation:" line. The system will run the tool and provide the observation to you.
        3. Once you have enough information from the observations, output:
        Final Answer: your final response.
        4. Nếu Observation có chữ 'Thành công...', BẮT BUỘC KHÔNG gọi tool nữa và phải dùng Final Answer.
        """

    def run(self, user_input: str) -> str:
        """
        Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = user_input
        steps = 0
        consecutive_errors = 0

        while steps < self.max_steps:
            # Generate LLM response
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            content = result.get("content", "")
            
            # Log raw LLM response & metrics
            logger.log_event("LLM_METRIC", {
                "step": steps + 1,
                "content": content,
                "usage": result.get("usage", {}),
                "latency_ms": result.get("latency_ms", 0)
            })
            
            current_prompt += f"\n{content}"
            
            # If Final Answer found -> Break loop
            final_answer_match = re.search(r"Final Answer:\s*(.*)", content, re.DOTALL)
            if final_answer_match:
                final_answer = final_answer_match.group(1).strip()
                logger.log_event("AGENT_END", {"steps": steps + 1, "final_answer": final_answer})
                return final_answer
            
            # If Action found -> Call tool -> Append Observation
            action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\((.*?)\)", content)
            if action_match:
                tool_name = action_match.group(1)
                args = action_match.group(2)
                observation = self._execute_tool(tool_name, args)
                consecutive_errors = 0 # Reset error count on successful action parse
                
                # Log tool execution and result
                logger.log_event("TOOL_EXECUTION", {
                    "step": steps + 1,
                    "tool": tool_name,
                    "args": args,
                    "observation": observation
                })
                
                current_prompt += f"\nObservation: {observation}"
            else:
                consecutive_errors += 1
                error_msg = "Could not parse Action or Final Answer. Please use the correct format."
                
                # Sophisticated Retry Guardrail
                if consecutive_errors >= 3:
                    fallback_msg = "Agent failed to parse correctly after 3 attempts. Aborting to save tokens."
                    logger.log_event("AGENT_CRASH", {"reason": "Too many parsing errors"})
                    return fallback_msg
                
                # Log parsing/hallucination error
                logger.log_event("PARSING_ERROR", {
                    "step": steps + 1,
                    "content": content,
                    "error": error_msg,
                    "retry_count": consecutive_errors
                })
                current_prompt += f"\nObservation: {error_msg} (Attempt {consecutive_errors}/3)"
            
            time.sleep(2.5)
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps})
        return "Max steps reached without finding a final answer."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                if 'func' in tool and callable(tool['func']):
                    try:
                        import ast
                        try:
                            parsed_args = ast.literal_eval(f"({args})")
                            if isinstance(parsed_args, tuple):
                                return str(tool['func'](*parsed_args))
                            elif isinstance(parsed_args, dict):
                                return str(tool['func'](**parsed_args))
                            else:
                                return str(tool['func'](parsed_args))
                        except (SyntaxError, ValueError):
                            # Fallback: pass raw string
                            return str(tool['func'](args))
                    except Exception as e:
                        return f"Error executing tool {tool_name}: {e}"
                else:
                    return f"Executed {tool_name} with args: {args}"
        return f"Tool {tool_name} not found."

    def run_with_trace(self, user_input: str) -> dict:
        """
        Runs the ReAct loop and returns a dict with 'final_answer' and 'traces' for UI display.
        """
        current_prompt = user_input
        steps = 0
        consecutive_errors = 0
        traces = []

        while steps < self.max_steps:
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            content = result.get("content", "")
            
            thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|Final Answer:|$)", content, re.DOTALL)
            thought = thought_match.group(1).strip() if thought_match else ""
            
            current_trace = {"thought": thought, "action": "", "observation": ""}
            current_prompt += f"\n{content}"
            
            final_answer_match = re.search(r"Final Answer:\s*(.*)", content, re.DOTALL)
            if final_answer_match:
                return {"final_answer": final_answer_match.group(1).strip(), "traces": traces}
            
            action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\((.*?)\)", content)
            if action_match:
                tool_name = action_match.group(1)
                args = action_match.group(2)
                observation = self._execute_tool(tool_name, args)
                consecutive_errors = 0
                
                current_trace["action"] = f"{tool_name}({args})"
                current_trace["observation"] = str(observation)
                traces.append(current_trace)
                
                current_prompt += f"\nObservation: {observation}"
            else:
                consecutive_errors += 1
                error_msg = "Could not parse Action or Final Answer."
                if consecutive_errors >= 3:
                    return {"final_answer": "Failed to parse after 3 attempts.", "traces": traces}
                
                current_trace["action"] = "ERROR"
                current_trace["observation"] = error_msg
                traces.append(current_trace)
                current_prompt += f"\nObservation: {error_msg} (Attempt {consecutive_errors}/3)"
            
            time.sleep(2.5)
            steps += 1
            
        return {"final_answer": "Max steps reached.", "traces": traces}
