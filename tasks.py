from crewai import Task

from agents import blueprint_parser, code_analyzer, code_verifier

parse_blueprint = Task(
    description="Extract structured coding rules from the {blueprint_path}.",
    agent=blueprint_parser,
    expected_input="Blueprint document path.",
    expected_output="A structured list of coding rules.",
)

analyze_code = Task(
    description="Extract functions, imports, and classes from the {codebase_path}.",
    agent=code_analyzer,
    expected_input="Source code file.",
    expected_output="A dictionary of extracted code components.",
)

verify_code = Task(
    description="Compare extracted code components against blueprint rules.",
    agent=code_verifier,
    expected_input="Extracted code components and structured blueprint rules.",
    expected_output="A list of compliance results, including rule violations.",
    context=[parse_blueprint, analyze_code],
)
