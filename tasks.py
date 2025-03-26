from crewai import Task

from agents import blueprint_parser, code_analyzer, code_verifier

parse_blueprints = Task(
    description="""Extract and merge structured coding rules from all blueprint documents.
    For each .docx file in the blueprint_files list:
    1. Parse the document and extract rules
    2. Categorize rules into aspects like:
       - naming conventions
       - code structure
       - error handling
       - documentation
       - performance
       - security
       - testing
       - database
       - logging
    3. Merge rules from all documents into a single structured dictionary
    4. Remove duplicates and conflicting rules
    5. Maintain rule sources for traceability""",
    agent=blueprint_parser,
    expected_input="""List of paths to blueprint documents and output directory.
    Input format: {
        'blueprint_files': List[str],  # Full paths to .docx files
        'output_dir': str  # Directory for output reports
    }""",
    expected_output="A structured dictionary of merged coding rules organized by category.",
)

analyze_codebase = Task(
    description="""Analyze the entire codebase in the specified directory.
    For each Python file:
    1. Extract comprehensive information about:
       - Functions and their characteristics (parameters, return types, docstrings)
       - Classes and their methods
       - Import statements and dependencies
       - Code complexity metrics
       - Patterns related to error handling, logging, database operations
    2. Calculate overall metrics and patterns
    3. Generate a detailed analysis report""",
    agent=code_analyzer,
    expected_input="""Source codebase directory path and output directory for reports.
    Input format: {
        'codebase_path': str,  # Full path to codebase directory
        'output_dir': str  # Directory for output reports
    }""",
    expected_output="A comprehensive dictionary of code analysis results.",
)

verify_compliance = Task(
    description="""Compare the analyzed codebase against the merged blueprint rules.
    Generate a detailed validation report that includes:
    1. Overall compliance metrics:
       - Rule coverage percentage
       - Compliance rate by category
       - Critical violations count
    2. Detailed findings:
       - Rule violations with severity levels
       - Warnings for potential improvements
       - Best practice suggestions
    3. Generate a JSON report with:
       - Summary metrics
       - Detailed findings
       - Actionable recommendations""",
    agent=code_verifier,
    expected_input="""Code analysis results, merged blueprint rules, and output directory.
    Input format: {
        'code_analysis': Dict,  # Results from code analysis
        'blueprint_rules': Dict,  # Merged rules from blueprints
        'output_dir': str  # Directory for output reports
    }""",
    expected_output="A detailed validation report with metrics, violations, warnings, and suggestions.",
    context=[parse_blueprints, analyze_codebase],
)
