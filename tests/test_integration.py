import pytest

from batchsmith.main import create_llm


@pytest.mark.requires_secrets
def test_create_llm_with_real_key(google_api_key):
    llm = create_llm()
    assert llm is not None
