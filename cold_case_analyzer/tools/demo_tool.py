from pydantic import BaseModel, Field
from langchain.tools import Tool

class EchoInput(BaseModel):
    text: str = Field(..., description="Input text to echo")

def run_echo(text: str) -> str:
    return f"Echo: {text}"

echo_tool = Tool(
    name="EchoTool",
    func=run_echo,
    description="A demo tool that simply echoes the input text.",
    args_schema=EchoInput,
)