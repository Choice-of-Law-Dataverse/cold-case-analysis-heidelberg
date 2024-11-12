import subprocess
from openai import OpenAI
from config import OPENAI_API_KEY

OpenAI.api_key = OPENAI_API_KEY

def prompt_model(prompt_text, model):
    if model == "llama3.1":
        return prompt_llama(prompt_text)
    elif model == "gpt-4o":
        return prompt_gpt_4o(prompt_text)
    else:
        return None

def prompt_llama(prompt_text):
    # Pass the prompt text directly as input without flags
    process = subprocess.run(
        ["ollama", "run", "llama3.1"],
        input=prompt_text,  # Provide the prompt directly
        capture_output=True,
        text=True
    )

    # Handle errors if they occur
    if process.returncode != 0:
        print("Error:", process.stderr)
        return None
    
    # Return the model's output
    return process.stdout.strip()

def prompt_gpt_4o(prompt_text):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )
    return completion.choices[0].message.content
