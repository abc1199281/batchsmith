import importlib.util
import json
import os
import sys
import types

import pytest

# Only stub external dependencies if they are not actually installed
try:
    found = importlib.util.find_spec("langchain_google_genai")
except Exception:
    found = None
if not found:
    mod = types.ModuleType("langchain_google_genai")
    sys.modules["langchain_google_genai"] = mod

try:
    found = importlib.util.find_spec("langchain_openai")
except Exception:
    found = None
if not found:
    mod = types.ModuleType("langchain_openai")
    sys.modules["langchain_openai"] = mod

try:
    found = importlib.util.find_spec("langchain_core.prompts")
except Exception:
    found = None
if not found:
    prompts_module = types.ModuleType("langchain_core.prompts")
    prompts_module.ChatPromptTemplate = object
    sys.modules["langchain_core.prompts"] = prompts_module

from batchsmith import main, providers


def test_load_json_valid(tmp_path):
    file = tmp_path / "data.json"
    data = {"a": 1}
    file.write_text(json.dumps(data))
    assert main.load_json(str(file)) == data


def test_load_json_missing(tmp_path):
    missing_file = tmp_path / "missing.json"
    with pytest.raises(SystemExit):
        main.load_json(str(missing_file))


def test_load_json_invalid(tmp_path):
    file = tmp_path / "bad.json"
    file.write_text("{bad json}")
    with pytest.raises(SystemExit):
        main.load_json(str(file))


def test_create_llm(monkeypatch):
    # Stub ChatGoogleGenerativeAI to capture init arguments
    calls = {}

    class DummyLLM:
        def __init__(
            self,
            model,
            temperature,
            max_tokens,
            timeout,
            max_retries,
        ):
            calls["init_args"] = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": timeout,
                "max_retries": max_retries,
            }

    dummy_mod = types.ModuleType("langchain_google_genai")
    dummy_mod.ChatGoogleGenerativeAI = DummyLLM
    monkeypatch.setitem(sys.modules, "langchain_google_genai", dummy_mod)
    sys.modules.pop("batchsmith.providers.google", None)
    # Ensure API key prompt path is taken
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setattr(
        "batchsmith.providers.google.getpass.getpass",
        lambda prompt: "xyz_key",
    )

    llm = providers.create_llm()
    assert isinstance(llm, DummyLLM)
    # Key should be stored in environment
    assert os.environ["GOOGLE_API_KEY"] == "xyz_key"
    # Verify init arguments
    assert calls["init_args"] == {
        "model": "gemini-1.5-flash",
        "temperature": 0,
        "max_tokens": None,
        "timeout": None,
        "max_retries": 2,
    }


def test_create_llm_openai(monkeypatch):
    calls = {}

    class DummyLLM:
        def __init__(
            self,
            model,
            temperature,
            max_tokens,
            timeout,
            max_retries,
        ):
            calls["init_args"] = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": timeout,
                "max_retries": max_retries,
            }

    dummy_mod = types.ModuleType("langchain_openai")
    dummy_mod.ChatOpenAI = DummyLLM
    monkeypatch.setitem(sys.modules, "langchain_openai", dummy_mod)
    sys.modules.pop("batchsmith.providers.openai", None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        "batchsmith.providers.openai.getpass.getpass",
        lambda prompt: "open_key",
    )

    llm = providers.create_llm(provider="openai")
    assert isinstance(llm, DummyLLM)
    assert os.environ["OPENAI_API_KEY"] == "open_key"
    assert calls["init_args"] == {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": None,
        "timeout": None,
        "max_retries": 2,
    }


def test_json_to_markdown_includes_query():
    data = [{"result": "ok"}]
    batch = [{"query": "foo"}]
    md = main.json_to_markdown(data, batch_data=batch)
    # Input subsection should list the original query fields as bullets
    assert "### Input" in md
    assert "- **query**: foo" in md
    # Answer subsection should be present with the result
    assert "### Answer" in md
    assert "- **result**: ok" in md
