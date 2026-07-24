from dataclasses import dataclass
from typing import Any


@dataclass
class LLMPayload:
    """
    Represents the payload to be sent to a Language Model (LLM) for processing.
    """

    user_prompt: str
    """
    The raw text prompt provided by the user to the LLM for processing.
    """
    model: str | None = None
    """
    The specific LLM model to be used for processing the prompt.
    """
    system_prompt: str | None = None
    """
    The system-level prompt that provides context or instructions to the LLM.
    """
    temperature: float | None = None
    """
    The temperature setting for the LLM, influencing the randomness of its output.
    """
    max_tokens: int | None = None
    """
    The maximum number of tokens to be generated in the LLM's response.
    """
    structured_output: Any | None = None
    """
    An optional structured format for the LLM's output, if applicable.
    """
