import importlib.util
import sys
import types

import pytest

# Stub external dependencies for imports
try:
    found = importlib.util.find_spec("langchain_core.prompts")
except Exception:
    found = None
if not found:
    prompts_module = types.ModuleType("langchain_core.prompts")
    prompts_module.ChatPromptTemplate = object
    sys.modules["langchain_core.prompts"] = prompts_module

if importlib.util.find_spec("langchain_google_genai") is None:
    mod = types.ModuleType("langchain_google_genai")
    sys.modules["langchain_google_genai"] = mod

from batchsmith.providers import create_llm


@pytest.mark.requires_secrets
def test_create_llm_with_real_key(google_api_key):
    llm = create_llm()
    assert llm is not None
