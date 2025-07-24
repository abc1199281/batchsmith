"""
This script demonstrates a modular approach to using LangChain for structured
output generation. It loads configuration, prompts, and batch data from JSON
files,
creates an LLM, constructs a chain with structured output,
and processes a batch of requests, saving the results to a JSON file.
"""

import argparse
import getpass
import json
import os
import re
import sys
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

BASE_DIR = Path(__file__).resolve().parents[1]
META_PROMPT_FILE = BASE_DIR / "META_PROMPT.md"


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


def create_llm():
    """Creates and configures the ChatGoogleGenerativeAI LLM."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    if "GOOGLE_API_KEY" not in os.environ:
        prompt_text = "Enter your Google AI API key: "
        os.environ["GOOGLE_API_KEY"] = getpass.getpass(prompt_text)
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )


def create_chain(llm, json_schema, prompts):
    """Creates the LangChain for structured output generation."""
    structured_llm = llm.with_structured_output(json_schema)
    prompt = ChatPromptTemplate.from_messages(
        [("system", prompts["system"]), ("user", prompts["user"])]
    )
    return prompt | structured_llm


def load_meta_prompt():
    """Return the meta prompt template as a string."""
    if META_PROMPT_FILE.exists():
        text = META_PROMPT_FILE.read_text()
        match = re.search(r"```(.*)```", text, re.S)
        if match:
            return match.group(1).strip()
        return text.strip()
    raise FileNotFoundError("META_PROMPT.md not found")


def parse_meta_response(response):
    """Extract JSON blocks from the meta prompt response."""
    blocks = re.findall(r"```(?:json)?\n(.*?)\n```", response, re.S)
    if len(blocks) < 3:
        raise ValueError("Expected at least three JSON code blocks")
    return (
        json.loads(blocks[0]),
        json.loads(blocks[1]),
        json.loads(blocks[2]),
    )


def generate_files_from_idea(
    idea,
    config_path,
    prompts_path,
    batch_path,
    llm=None,
):
    """Generate config, prompts and batch data files from a high level idea."""
    if llm is None:
        llm = create_llm()
    prompt_template = load_meta_prompt()
    prompt = prompt_template.replace("{idea}", idea)
    response = llm.invoke(prompt)
    config, prompts, batch_data = parse_meta_response(response)
    Path(config_path).write_text(json.dumps(config, indent=4))
    Path(prompts_path).write_text(json.dumps(prompts, indent=4))
    Path(batch_path).write_text(json.dumps(batch_data, indent=4))


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
    help_parts = (
        "Generate config, prompts, and batch data from this high level ",
        "idea",
    )
    parser.add_argument("--idea", help="".join(help_parts))
    args = parser.parse_args()

    if args.idea:
        generate_files_from_idea(
            args.idea,
            args.config,
            args.prompts,
            args.batch_data,
        )
        print(
            f"Generated {args.config}, {args.prompts}, and "
            f"{args.batch_data} from idea."
        )
        return

    json_schema = load_json(args.config)
    prompts = load_json(args.prompts)
    batch_data = load_json(args.batch_data)

    llm = create_llm()
    chain = create_chain(llm, json_schema, prompts)

    response = chain.batch(batch_data)
    with open(args.output, "w") as f:
        json.dump(response, f, indent=4)


if __name__ == "__main__":
    main()
