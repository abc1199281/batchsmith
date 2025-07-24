import getpass
import os

from langchain_openai import ChatOpenAI


def create_llm():
    """Return a configured OpenAI chat model."""
    if "OPENAI_API_KEY" not in os.environ:
        prompt = "Enter your OpenAI API key: "
        os.environ["OPENAI_API_KEY"] = getpass.getpass(prompt)
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
