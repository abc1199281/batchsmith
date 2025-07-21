# batchsmith

A modular script for batch structured output generation using LangChain + Google Generative AI.

## Requirements

- Python >=3.12, <4.0
- Poetry

## Installation

Install dependencies via Poetry:

```bash
poetry install
```

## Usage

Set your `GOOGLE_API_KEY` environment variable and run:

```bash
python -m batchsmith.main --config config.json --prompts prompts.json --batch_data batch_data.json --output output.json
```
