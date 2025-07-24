"""Example CLI for structured batch generation with LangChain.
This script demonstrates a modular approach to using LangChain for structured
output generation. It loads configuration, prompts, and batch data from JSON
files, creates an LLM, constructs a chain with structured output, and processes
a batch of requests, saving the results to a JSON file.
"""

import argparse
import json
import os
import sys

from langchain_core.prompts import ChatPromptTemplate

from .providers import create_llm


def load_json(file_path):
    """Loads a JSON file and returns its content."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}.")
        sys.exit(1)


def create_chain(llm, json_schema, prompts):
    """Creates the LangChain for structured output generation."""
    structured_llm = llm.with_structured_output(json_schema)
    prompt = ChatPromptTemplate.from_messages(
        [("system", prompts["system"]), ("user", prompts["user"])]
    )
    return prompt | structured_llm


def json_to_markdown(
    data, order: list[str] | None = None, batch_data: list[dict] | None = None
):
    """Convert JSON data to Markdown sections (one per query/item).

    If ``batch_data`` is provided, each section will also contain an
    ``original_query`` field showing the corresponding input object.

    Fields in ``data`` are ordered according to ``order`` when given.
    """
    md_lines: list[str] = []
    if isinstance(data, list):
        for idx, item in enumerate(data, start=1):
            md_lines.append(f"## Query {idx}")
            # Input subsection: expand original query as bullet points
            if batch_data and idx - 1 < len(batch_data):
                md_lines.append("### Input")
                for key, val in batch_data[idx - 1].items():
                    md_lines.append(f"- **{key}**: {val}")
                md_lines.append("")
            # Answer subsection
            md_lines.append("### Answer")
            if isinstance(item, dict):
                # determine key order: required first then others
                if order:
                    keys = list(order) + [k for k in item if k not in order]
                else:
                    keys = list(item)
                for key in keys:
                    if key not in item:
                        continue
                    value = item[key]
                    if isinstance(value, str) and "\n" in value:
                        lines = value.split("\n")
                        # hard line break for Markdown: two spaces at end
                        md_lines.append(f"- **{key}**: {lines[0]}  ")
                        for line in lines[1:]:
                            md_lines.append(f"    {line}  ")
                    else:
                        md_lines.append(f"- **{key}**: {value}")
            else:
                md_lines.append("```json")
                md_lines.append(json.dumps(item, indent=4))
                md_lines.append("```")
            md_lines.append("")
    elif isinstance(data, dict):
        if order:
            for key in order:
                if key in data:
                    md_lines.append(f"- **{key}**: {data[key]}")
            for key in data:
                if key not in order:
                    md_lines.append(f"- **{key}**: {data[key]}")
        else:
            for key, value in data.items():
                md_lines.append(f"- **{key}**: {value}")
    else:
        md_lines.append("```json")
        md_lines.append(json.dumps(data, indent=4))
        md_lines.append("```")
    return "\n".join(md_lines).rstrip()


def main():
    """Main function to run the generation pipeline."""
    parser = argparse.ArgumentParser(
        description="Generate structured data using a language model."
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to the configuration file (JSON schema).",
    )
    parser.add_argument(
        "--prompts", default="prompts.json", help="Path to the prompts file."
    )
    parser.add_argument(
        "--batch_data",
        default="batch_data.json",
        help="Path to the batch data file.",
    )
    parser.add_argument(
        "--output", default="output.json", help="Path to the output file."
    )
    parser.add_argument(
        "--provider",
        default="google",
        choices=["google", "openai"],
        help="LLM provider to use (google or openai)",
    )
    parser.add_argument(
        "--to-markdown",
        action="store_true",
        help=(
            "Convert the output JSON file to a Markdown table and save to a .md file "
            "with the same basename."
        ),
    )
    args = parser.parse_args()

    json_schema = load_json(args.config)
    prompts = load_json(args.prompts)
    batch_data = load_json(args.batch_data)

    llm = create_llm(provider=args.provider)
    chain = create_chain(llm, json_schema, prompts)

    response = chain.batch(batch_data)
    with open(args.output, "w") as f:
        json.dump(response, f, indent=4)
    if args.to_markdown:
        md = json_to_markdown(
            response, order=json_schema.get("required"), batch_data=batch_data
        )
        # write markdown to a .md file matching the output JSON basename
        md_path = os.path.splitext(args.output)[0] + ".md"
        with open(md_path, "w") as mf:
            mf.write(md)


if __name__ == "__main__":
    main()
