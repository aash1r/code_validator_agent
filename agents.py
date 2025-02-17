import os

from crewai import LLM, Agent

from tools import code_parser, code_validator, document_parser

llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    verbose=True,
    api_key=os.getenv("GOOGLE_API_KEY"),
)
print(f"Using model: {llm.model}")

blueprint_parser = Agent(
    role="Blueprint Parser",
    goal="Extract structured coding guidelines from blueprint documents.",
    backstory="Expert in company guidelines and coding practices.",
    tools=[document_parser],
    llm=llm,
    verbose=True,
)

code_analyzer = Agent(
    role="Code Analyzer",
    goal="Extract functions, imports, and classes from source code.",
    tools=[code_parser],
    backstory="Senior Engineer specializing in code analysis.",
    llm=llm,
    verbose=True,
)

code_verifier = Agent(
    role="Code Verifier",
    goal="Compare extracted code structure with blueprint rules and report violations.",
    tools=[code_validator],
    backstory="Strict compliance officer enforcing rules.",
    llm=llm,
    verbose=True,
)
