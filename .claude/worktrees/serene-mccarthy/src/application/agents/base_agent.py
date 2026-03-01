"""
Base Agent class for the Multi-Agent System.
All specialized agents (Router, Logic, Human) inherit from this.
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

class BaseAgent(ABC):
    """Abstract base class for AI Agents."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url  # For DeepSeek compatibility
        )
        
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return structured output."""
        pass

    async def _call_llm(self, system_prompt: str, user_message: str, temperature: float = 0.7) -> str:
        """Low-level LLM call with error handling."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"❌ LLM Error ({self.model}): {e}")
            return ""
