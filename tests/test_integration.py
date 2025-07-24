import importlib.util
import sys
import types

import pytest

# Stub langchain_core.prompts if missing to allow importing create_llm
try:
    found = importlib.util.find_spec("langchain_core.prompts")
except Exception:
    found = None
if not found:
    prompts_module = types.ModuleType("langchain_core.prompts")
    prompts_module.ChatPromptTemplate = object
    sys.modules["langchain_core.prompts"] = prompts_module

from batchsmith.providers import create_llm


@pytest.mark.requires_secrets
def test_create_llm_with_real_key(google_api_key):
    llm = create_llm()
    assert llm is not None
