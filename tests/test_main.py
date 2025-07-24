import json
import os
import sys
import types

import pytest

# Only stub external dependencies if they are not actually installed
try:
    import langchain_google_genai as _  # type: ignore  # noqa: F401
except ModuleNotFoundError:
    sys.modules["langchain_google_genai"] = types.ModuleType(
        "langchain_google_genai",
    )

try:
    from langchain_core import \
        prompts as _core_prompts  # type: ignore  # noqa: F401
except ModuleNotFoundError:
    core_mod = types.ModuleType("langchain_core")
    prompts_module = types.ModuleType("langchain_core.prompts")
    prompts_module.ChatPromptTemplate = object
    sys.modules["langchain_core"] = core_mod
    sys.modules["langchain_core.prompts"] = prompts_module

from batchsmith import main


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
    # Ensure API key prompt path is taken
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setattr(
        "batchsmith.main.getpass.getpass",
        lambda prompt: "xyz_key",
    )

    llm = main.create_llm()
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


def test_generate_files_from_idea(tmp_path, monkeypatch):
    idea = "test idea"
    meta_response = (
        "Here you go\n"
        '```json\n{"title": "X"}\n```\n'
        '```json\n{"system": "s", "user": "u"}\n```\n'
        '```json\n[{"a": 1}]\n```\n'
    )

    class DummyLLM:
        def invoke(self, prompt):
            assert idea in prompt
            return meta_response

    monkeypatch.setattr(main, "create_llm", lambda: DummyLLM())
    monkeypatch.setattr(main, "load_meta_prompt", lambda: "Idea: {idea}")

    config = tmp_path / "c.json"
    prompts = tmp_path / "p.json"
    batch = tmp_path / "b.json"
    main.generate_files_from_idea(idea, config, prompts, batch)

    assert json.loads(config.read_text()) == {"title": "X"}
    assert json.loads(prompts.read_text()) == {"system": "s", "user": "u"}
    assert json.loads(batch.read_text()) == [{"a": 1}]
