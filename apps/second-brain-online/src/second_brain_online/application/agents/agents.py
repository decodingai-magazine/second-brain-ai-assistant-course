from pathlib import Path
from typing import Any

import opik
from loguru import logger
from opik import opik_context
from smolagents import LiteLLMModel, MessageRole, MultiStepAgent, ToolCallingAgent

from second_brain_online.config import settings

from .tools import (
    HuggingFaceEndpointSummarizerTool,
    MongoDBRetrieverTool,
    OpenAISummarizerTool,
    what_can_i_do,
)


def get_agent(retriever_config_path: Path) -> "AgentWrapper":
    agent = AgentWrapper.build_from_smolagents(
        retriever_config_path=retriever_config_path
    )

    return agent


class AgentWrapper:
    def __init__(self, agent: MultiStepAgent) -> None:
        self.__agent = agent

    @property
    def input_messages(self) -> list[dict]:
        return self.__agent.input_messages

    @property
    def agent_name(self) -> str:
        return self.__agent.agent_name

    @property
    def max_steps(self) -> str:
        return self.__agent.max_steps

    @classmethod
    def build_from_smolagents(cls, retriever_config_path: Path) -> "AgentWrapper":
        retriever_tool = MongoDBRetrieverTool(config_path=retriever_config_path)
        if settings.USE_HUGGINGFACE_DEDICATED_ENDPOINT:
            logger.warning(
                f"Using Hugging Face dedicated endpoint as the summarizer with URL: {settings.HUGGINGFACE_DEDICATED_ENDPOINT}"
            )
            summarizer_tool = HuggingFaceEndpointSummarizerTool()
        else:
            logger.warning(
                f"Using OpenAI as the summarizer with model: {settings.OPENAI_MODEL_ID}"
            )
            summarizer_tool = OpenAISummarizerTool(stream=False)

        if settings.USE_ASTRAFLOW:
            logger.warning(
                "Using Astraflow (global endpoint) as the LLM backend: https://api-us-ca.umodelverse.ai/v1"
            )
            model = LiteLLMModel(
                model_id=settings.OPENAI_MODEL_ID,
                api_base="https://api-us-ca.umodelverse.ai/v1",
                api_key=settings.ASTRAFLOW_API_KEY,
            )
        else:
            model = LiteLLMModel(
                model_id=settings.OPENAI_MODEL_ID,
                api_base="https://api.openai.com/v1",
                api_key=settings.OPENAI_API_KEY,
            )

        agent = ToolCallingAgent(
            tools=[what_can_i_do, retriever_tool, summarizer_tool],
            model=model,
            max_steps=3,
            verbosity_level=2,
        )

        return cls(agent)

    @opik.track(name="Agent.run")
    def run(self, task: str, **kwargs) -> Any:
        result = self.__agent.run(task, **kwargs)

        model = self.__agent.model
        metadata = {
            "system_prompt": self.__agent.system_prompt,
            "system_prompt_template": self.__agent.system_prompt_template,
            "tool_description_template": self.__agent.tool_description_template,
            "tools": self.__agent.tools,
            "model_id": self.__agent.model.model_id,
            "api_base": self.__agent.model.api_base,
            "input_token_count": model.last_input_token_count,
            "output_token_count": model.last_output_token_count,
        }
        if hasattr(self.__agent, "step_number"):
            metadata["step_number"] = self.__agent.step_number
        opik_context.update_current_trace(
            tags=["agent"],
            metadata=metadata,
        )

        return result


def extract_tool_responses(agent: ToolCallingAgent) -> str:
    """
    Extracts and concatenates all tool response contents with numbered observation delimiters.

    Args:
        input_messages (List[Dict]): List of message dictionaries containing 'role' and 'content' keys

    Returns:
        str: Tool response contents separated by numbered observation delimiters

    Example:
        >>> messages = [
        ...     {"role": MessageRole.TOOL_RESPONSE, "content": "First response"},
        ...     {"role": MessageRole.USER, "content": "Question"},
        ...     {"role": MessageRole.TOOL_RESPONSE, "content": "Second response"}
        ... ]
        >>> extract_tool_responses(messages)
        "-------- OBSERVATION 1 --------\nFirst response\n-------- OBSERVATION 2 --------\nSecond response"
    """

    tool_responses = [
        msg["content"]
        for msg in agent.input_messages
        if msg["role"] == MessageRole.TOOL_RESPONSE
    ]

    return "\n".join(
        f"-------- OBSERVATION {i + 1} --------\n{response}"
        for i, response in enumerate(tool_responses)
    )


class OpikAgentMonitorCallback:
    def __init__(self) -> None:
        self.output_state: dict = {}

    def __call__(self, step_log) -> None:
        input_state = {
            "agent_memory": step_log.agent_memory,
            "tool_calls": step_log.tool_calls,
        }
        self.output_state = {"observations": step_log.observations}

        self.trace(input_state)

    @opik.track(name="Callback.agent_step")
    def trace(self, step_log) -> dict:
        return self.output_state
