import ast
import os

from docx import Document
from langchain.tools import tool
from PyPDF2 import PdfReader


@tool
def document_parser(blueprint_path: str) -> list:
    """Parse company blueprints (.txt, .docx, .pdf) to extract coding rules."""

    def read_txt(file_path):
        with open(file_path, "r") as file:
            return file.readlines()

    def read_docx(file_path):
        doc = Document(file_path)
        return [p.text for p in doc.paragraphs]

    def read_pdf(file_path):
        reader = PdfReader(file_path)
        content = [
            page.extract_text() or "[Unable to extract text]" for page in reader.pages
        ]
        return content

    file_ext = os.path.splitext(blueprint_path)[-1].lower()
    print(f"Extracting rules from: {blueprint_path} ({file_ext})")

    if file_ext == ".txt":
        content = read_txt(blueprint_path)
    elif file_ext == ".docx":
        content = read_docx(blueprint_path)
    elif file_ext == ".pdf":
        content = read_pdf(blueprint_path)
    else:
        raise ValueError("Unsupported file type. Use .txt, .docx, or .pdf.")

    rules = [
        rule.strip() for line in content for rule in line.split("\n") if rule.strip()
    ]

    return rules


@tool
def code_parser(source_code: str) -> dict:
    """Extracts meaningful patterns from the given code."""

    tree = ast.parse(source_code)
    functions = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check for attributes
            functions[node.name] = {
                "has_exception_handling": any(
                    isinstance(n, ast.Try) for n in ast.walk(node)
                ),
                "uses_dependency_injection": any(
                    isinstance(n, ast.Call)
                    and hasattr(n.func, "attr")
                    and n.func.attr == "Depends"
                    for n in ast.walk(node)
                ),
                "performs_database_operations": any(
                    isinstance(n, ast.Call)
                    and hasattr(n.func, "attr")
                    and n.func.attr in ["query", "add", "commit", "delete"]
                    for n in ast.walk(node)
                ),
            }

    return {"functions": functions}


@tool
def code_validator(code_analysis: dict, blueprint_rules: list) -> dict:
    """Compare code patterns against best practices."""
    violations = []

    if "functions" not in code_analysis:
        return {"violations": ["Invalid input format for code analysis."]}

    for function_name, function_data in code_analysis["functions"].items():
        # Check for type hinting
        if "type_hinting" in blueprint_rules and not function_data.get(
            "type_hinting", False
        ):
            violations.append(f"⚠️ Function '{function_name}' is missing type hints.")

        # Check for exception handling
        if (
            "Error Handling is Mandatory" in blueprint_rules
            and not function_data["has_exception_handling"]
        ):
            violations.append(f"⚠️ Function '{function_name}' lacks exception handling.")

        # Check for dependency injection
        if (
            "Use Dependency Injection for Database Sessions" in blueprint_rules
            and not function_data["uses_dependency_injection"]
        ):
            violations.append(
                f"⚠️ Function '{function_name}' does not use dependency injection."
            )

    return {"violations": violations if violations else ["No violations found."]}
