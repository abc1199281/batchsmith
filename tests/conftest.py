import os
import sys

from dotenv import load_dotenv
import pytest

# Load environment variables from .env for local development.
load_dotenv()

# Add project src directory to sys.path for test imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

def _get_env_or_skip(name):
    val = os.getenv(name)
    if not val:
        pytest.skip(f"Skipping test: required env var {name!r} not set")
    return val

@pytest.fixture(scope="session")
def google_api_key():
    return _get_env_or_skip("GOOGLE_API_KEY")

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_secrets: mark tests that require real environment credentials"
    )
