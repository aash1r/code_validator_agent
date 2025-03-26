import os

from crewai import LLM, Agent

from tools import code_parser, code_validator, document_parser, generate_report

llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    verbose=True,
    api_key=os.getenv("GOOGLE_API_KEY"),
)
print(f"Using model: {llm.model}")

blueprint_parser = Agent(
    role="Blueprint Analysis Expert",
    goal="Extract and categorize coding guidelines from blueprint documents to create a structured set of rules.",
    backstory="""Expert in software development standards and best practices. 
    Specializes in analyzing technical documentation and extracting actionable guidelines.
    Has extensive experience in various programming paradigms and coding standards.""",
    tools=[document_parser],
    llm=llm,
    verbose=True,
)

code_analyzer = Agent(
    role="Code Analysis Specialist",
    goal="Perform comprehensive analysis of the codebase to identify patterns, structures, and potential issues.",
    backstory="""Senior software engineer with expertise in static code analysis.
    Experienced in identifying code smells, complexity issues, and architectural patterns.
    Proficient in AST analysis and code metrics calculation.""",
    tools=[code_parser],
    llm=llm,
    verbose=True,
)

code_verifier = Agent(
    role="Compliance Validator",
    goal="Validate codebase against blueprint rules and generate detailed compliance reports.",
    backstory="""Quality assurance expert specializing in code compliance and standards enforcement.
    Experienced in identifying violations and suggesting improvements.
    Skilled in generating clear, actionable reports for development teams.""",
    tools=[code_validator, generate_report],
    llm=llm,
    verbose=True,
)
