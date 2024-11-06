import subprocess

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