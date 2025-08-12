#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
#     "python-dotenv",
#     "aci-sdk",
# ]
# ///

import json
from dotenv import load_dotenv
from openai import OpenAI
from aci import ACI

load_dotenv()

openai = OpenAI()
aci = ACI()

def main() -> None:
    github_get_repo_function = aci.functions.get_definition("GITHUB__GET_REPOSITORY")

    response = openai.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant with access to a variety of tools.",
            },
            {
                "role": "user",
                "content": "Get information about the aipotheosis-labs/aci github repository, including the number of stars",
            },
        ],
        tools=[github_get_repo_function],
        tool_choice="required",
    )
    tool_call = (
        response.choices[0].message.tool_calls[0]
        if response.choices[0].message.tool_calls
        else None
    )

    if tool_call:
        result = aci.handle_function_call(
            tool_call.function.name,
            json.loads(tool_call.function.arguments),
            linked_account_owner_id="robert-local-dev",
        )
        
        if result and result.get('success') and result.get('data'):
            stars = result['data'].get('stargazers_count', 0)
            print(f"Stars: {stars}")


if __name__ == "__main__":
    main()
