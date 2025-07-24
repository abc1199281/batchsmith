import getpass
import os

from langchain_google_genai import ChatGoogleGenerativeAI


def create_llm():
    """Return a configured Google Generative AI chat model."""
    if "GOOGLE_API_KEY" not in os.environ:
        prompt = "Enter your Google AI API key: "
        os.environ["GOOGLE_API_KEY"] = getpass.getpass(prompt)
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
