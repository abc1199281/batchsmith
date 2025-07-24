import sys
import types

import pytest

try:
    from batchsmith.main import create_llm
except ModuleNotFoundError:
    # Stub external deps if the package cannot be imported
    sys.modules.setdefault(
        "langchain_core",
        types.ModuleType("langchain_core"),
    )
    prompts_mod = types.ModuleType("langchain_core.prompts")
    prompts_mod.ChatPromptTemplate = object
    sys.modules.setdefault("langchain_core.prompts", prompts_mod)
    from batchsmith.main import create_llm


@pytest.mark.requires_secrets
def test_create_llm_with_real_key(google_api_key):
    llm = create_llm()
    assert llm is not None
