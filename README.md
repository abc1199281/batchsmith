# batchsmith

BatchSmith is a modular CLI tool for structured batch output generation using LangChain and Google Generative AI.

## Features

- **Structured JSON validation**: Define output schemas with JSON Schema.
- **Batch processing**: Generate multiple outputs in one run.
- **Templated prompts**: Customize system and user prompts with template variables.
- **Markdown conversion**: Convert the output JSON to Markdown sections (one per item) using the `--to-markdown` option. Each section expands the input data as bullet points in an **Input** subsection and the model’s response in an **Answer** subsection, ordering fields per the schema’s `required` array. String values containing newline characters are rendered with Markdown hard line breaks (two spaces). A `.md` file is auto-saved alongside the JSON output; use `--to-pdf` to also generate a PDF (requires pypandoc and a CJK-capable LaTeX font; e.g., install `fonts-noto-cjk`).

## Requirements

- Python >=3.12, <4.0
- Poetry

## Installation

Install runtime and development dependencies:

```bash
poetry install
```

Install and activate pre-commit hooks:

```bash
poetry run pre-commit install
```

## Configuration

Create a JSON schema file (e.g., `config.json`) to define the structure of the expected output.
See `tests/examples/jokes/config.json` for an example.

## Prompts

Define system and user prompts in a JSON file (e.g., `prompts.json`).
Use `{variable}` placeholders for template data.
See `tests/examples/jokes/prompts.json` for an example.

## Batch Data

Prepare batch input data as a JSON array of objects. Each object should provide values for the template variables.
See `tests/examples/jokes/batch_data.json` for an example.

## Usage

Set your Google API key:

```bash
export GOOGLE_API_KEY=your_api_key
```

Run the batch generation:

```bash
batchsmith \
  --config config.json \
  --prompts prompts.json \
  --batch_data batch_data.json \
  --output output.json \
  --to-markdown [--to-pdf]
```

## Examples

An end-to-end example is available under `tests/examples/jokes`. For example:

```bash
cd tests/examples/jokes
export GOOGLE_API_KEY=your_api_key
batchsmith \
  --config config.json \
  --prompts prompts.json \
  --batch_data batch_data.json \
  --output output.json \
  --to-markdown [--to-pdf]
```

## Testing

Run the test suite:

```bash
poetry run pytest
```

## Contributing

Contributions are welcome! Please open issues or pull requests for bug reports and feature requests.

## License

This project is licensed under the [MIT License](LICENSE).
