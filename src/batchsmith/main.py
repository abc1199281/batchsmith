"""
This script demonstrates a modular approach to using LangChain for structured output generation.
It loads configuration, prompts, and batch data from JSON files,
creates an LLM, constructs a chain with structured output,
and processes a batch of requests, saving the results to a JSON file.
"""

import argparse
import getpass
import os
import json
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


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
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
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
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompts["system"]),
        ("user", prompts["user"])
    ])
    return prompt | structured_llm


def main():
    """Main function to run the generation pipeline."""
    parser = argparse.ArgumentParser(description="Generate structured data using a language model.")
    parser.add_argument("--config", default="config.json", help="Path to the configuration file (JSON schema).")
    parser.add_argument("--prompts", default="prompts.json", help="Path to the prompts file.")
    parser.add_argument("--batch_data", default="batch_data.json", help="Path to the batch data file.")
    parser.add_argument("--output", default="output.json", help="Path to the output file.")
    args = parser.parse_args()

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