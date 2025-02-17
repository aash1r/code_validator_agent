from crewai import Task

import agents

parse_blueprint = Task(
    description="Parse the blueprint file and extract coding rules from the {blueprint_path}.",
    agent=agents.blueprint_parser_agent,
    expected_input="blueprints/Why and how loops should be avoided in ETLs_ELTs.docx",
    expected_output="A list of coding rules extracted from the blueprint.",
)

analyze_code = Task(
    description="Analyze the code and extract structural and coding components from the {codebase_path}.",
    agent=agents.code_analyzer_agent,
    expected_input="ecommerce/app/routes/products.py",
    expected_output="A dictionary containing the imports, functions, and classes extracted from the codebase.",
)


verify_code = Task(
    description="Compare extracted code components against blueprint rules.",
    agent=agents.code_verifier_agent,
    expected_input="Extracted code components and structured blueprint rules.",
    expected_output="A dictionary containing compliance results, listing which rules were followed and which were violated.",
    context=[parse_blueprint, analyze_code],  # Ensure dependencies are respected
)


generate_report = Task(
    description="Generate a compliance report based on verification results.",
    agent=agents.report_generator_agent,
    expected_input="verification_results",
    expected_output="A formatted text or JSON report summarizing the compliance results and any violations.",
)
