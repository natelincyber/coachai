from types import CoroutineType
from typing import Any
from dotenv import load_dotenv

import asyncio

from utils.utils import run_async

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

load_dotenv()

provider = GoogleProvider()
model_settings = GoogleModelSettings(google_thinking_config={'thinking_budget': 0})
model = GoogleModel('gemini-2.5-flash', provider=provider)
agent = Agent(model, model_settings=model_settings)

async def _run_async(prompt: str, output_type: BaseModel):
    return await agent.run(prompt, output_type=output_type)

def llm_async(prompt: str, output_type: BaseModel) -> AgentRunResult[str]:
    return agent.run_sync(prompt, output_type=output_type)
