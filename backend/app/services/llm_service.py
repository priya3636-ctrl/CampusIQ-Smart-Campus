import os

from langchain_groq import ChatGroq


DEFAULT_MODEL = "openai/gpt-oss-20b"


def get_groq_llm(temperature: float = 0.2) -> ChatGroq:
    """Create the shared hosted Groq chat model used by CampusIQ."""

    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is not configured.")

    model_name = os.getenv("GROQ_MODEL", DEFAULT_MODEL)

    return ChatGroq(
        model=model_name,
        temperature=temperature
    )
