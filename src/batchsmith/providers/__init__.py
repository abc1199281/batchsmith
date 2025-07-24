def create_llm(provider: str = "google"):
    """Instantiate an LLM for the given provider."""
    if provider == "google":
        from .google import create_llm as google_llm

        return google_llm()
    if provider == "openai":
        from .openai import create_llm as openai_llm

        return openai_llm()
    raise ValueError(f"Unknown provider: {provider}")
