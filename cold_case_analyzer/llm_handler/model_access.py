import subprocess
from openai import OpenAI
from config import OPENAI_API_KEY, LLAMA_API_KEY
import json
from llamaapi import LlamaAPI

OpenAI.api_key = OPENAI_API_KEY
llama = LlamaAPI(LLAMA_API_KEY)


def prompt_model(prompt_text, model):
    if model == "llama3.1":
        return prompt_llama(prompt_text)
    elif model == "gpt-4o":
        return prompt_gpt_4o(prompt_text)
    else:
        return None


def prompt_llama(prompt_text):
    api_request_json = {
        "model": "llama3.1-405b",
        "messages": [{"role": "user", "content": prompt_text}],
        "stream": False,
        "temperature": 0,
    }
    response = llama.run(api_request_json)
    parsed_response = json.dumps(response.json(), indent=2)
    return parsed_response["choices"][0]["message"]["content"]


def prompt_gpt_4o(prompt_text):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[{"role": "user", "content": prompt_text}],
    )
    return completion.choices[0].message.content
