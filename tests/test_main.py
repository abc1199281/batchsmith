import json
import os
import pytest
import sys
import types

# Stub external dependencies so the module can be imported without them
sys.modules.setdefault("langchain_google_genai", types.ModuleType("langchain_google_genai"))
prompts_module = types.ModuleType("langchain_core.prompts")
prompts_module.ChatPromptTemplate = object
sys.modules.setdefault("langchain_core.prompts", prompts_module)

from batchsmith import main


def test_load_json_valid(tmp_path):
    file = tmp_path / 'data.json'
    data = {'a': 1}
    file.write_text(json.dumps(data))
    assert main.load_json(str(file)) == data


def test_load_json_missing(tmp_path):
    missing_file = tmp_path / 'missing.json'
    with pytest.raises(SystemExit):
        main.load_json(str(missing_file))


def test_load_json_invalid(tmp_path):
    file = tmp_path / 'bad.json'
    file.write_text('{bad json}')
    with pytest.raises(SystemExit):
        main.load_json(str(file))
