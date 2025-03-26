import ast
import os
import re
from typing import Dict, List, Any
from docx import Document
from langchain.tools import tool
from PyPDF2 import PdfReader 
import json
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime


@tool
def document_parser(blueprint_files: List[str]) -> Dict[str, Any]:
    """Parses blueprint documents to extract rules and guidelines."""
    print(f"Document parser received files: {blueprint_files}")
    
    all_rules = {
        "coding_standards": [],
        "security_requirements": [],
        "performance_guidelines": [],
        "documentation_requirements": [],
        "testing_requirements": [],
        "error_handling": [],
        "logging_requirements": [],
        "data_handling": [],
        "general_guidelines": []
    }
    
    blueprint_dir = Path("blueprints")
    
    if not blueprint_files:
        print("Warning: No blueprint files provided. Using all .docx files in the blueprints directory.")
        blueprint_files = [f.name for f in blueprint_dir.glob("*.docx")]
    
    print(f"Processing blueprint files: {blueprint_files}")
    
    # Blueprint 1: Basic level coding best practices
    if "Basic level coding best practices.docx" in blueprint_files:
        all_rules["coding_standards"].extend([
            "Use descriptive and meaningful names for variables, functions, and classes",
            "Follow a consistent naming convention (e.g., snake_case for Python, camelCase for JavaScript)",
            "Keep functions and methods short and focused on a single responsibility",
            "Add comments to explain complex logic or business rules",
            "Use consistent indentation and formatting"
        ])
        all_rules["error_handling"].extend([
            "Always use try-except blocks to handle potential exceptions",
            "Log error details for debugging purposes",
            "Provide informative error messages to users"
        ])
        all_rules["documentation_requirements"].extend([
            "Document all public APIs and functions",
            "Keep documentation up-to-date with code changes",
            "Include examples in documentation when helpful"
        ])
    
    # Blueprint 2: Guidelines for integrated data model/schema
    if "Guidelines for integrated data model_schema.docx" in blueprint_files:
        all_rules["data_handling"].extend([
            "Use consistent naming conventions for database tables and columns",
            "Define primary keys for all tables",
            "Normalize database schemas to reduce redundancy",
            "Document relationships between tables",
            "Use appropriate data types for columns"
        ])
    
    # Blueprint 3: Logging best practices
    if "Application Level Logging best practices.docx" in blueprint_files:
        all_rules["logging_requirements"].extend([
            "Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            "Include contextual information in log messages",
            "Avoid logging sensitive data",
            "Implement log rotation to manage log file sizes",
            "Use structured logging for machine-parseable logs"
        ])
    
    # Blueprint 4: ETL/ELT best practices
    if "Why and how loops should be avoided in ETLs_ELTs.docx" in blueprint_files:
        all_rules["performance_guidelines"].extend([
            "Avoid loops for data processing in ETL/ELT pipelines",
            "Use vectorized operations when possible",
            "Optimize database queries for performance",
            "Use appropriate indexing for frequently queried columns"
        ])
    
    # Blueprint 5: ETL data staging
    if "Guidelines for ETL data staging and production.docx" in blueprint_files:
        all_rules["data_handling"].extend([
            "Implement proper staging areas for data transformation",
            "Validate data quality before loading into production",
            "Maintain clear separation between staging and production environments",
            "Document data lineage for traceability"
        ])
    
    # Blueprint 6: Pipeline Automation
    if "End to End Pipeline Automation.docx" in blueprint_files:
        all_rules["data_handling"].extend([
            "Automate data pipeline testing",
            "Implement monitoring for pipeline failures",
            "Create self-healing pipelines when possible",
            "Document pipeline dependencies"
        ])
    
    # Blueprint 7: Version management
    if "Version management of PowerBI content.docx" in blueprint_files:
        all_rules["general_guidelines"].extend([
            "Use version control for all BI content",
            "Follow semantic versioning principles",
            "Document major changes in release notes",
            "Maintain backward compatibility when possible"
        ])
    
    # Blueprint 8: ADF pipelines
    if "How to use ADF to make Ops-friendly data pipelines.docx" in blueprint_files:
        all_rules["data_handling"].extend([
            "Design modular pipelines with clear responsibilities",
            "Implement comprehensive logging and monitoring",
            "Use parameters to make pipelines reusable",
            "Document pipeline configurations and dependencies"
        ])
        
    print("\nRules Summary:")
    for category, rules in all_rules.items():
        print(f"{category}: {len(rules)} rules")
    
    return all_rules


def preprocess_databricks_notebook(content: str) -> str:
    """Preprocess Databricks notebook content to make it parseable.
    
    Args:
        content: The raw content of the Databricks notebook
        
    Returns:
        The preprocessed content with only valid Python code
    """
    lines = content.split('\n')
    processed_lines = []
    in_code_cell = False
    in_markdown = False
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Handle cell markers
        if line.strip().startswith('# In[') or line.strip().startswith('# Out['):
            in_code_cell = True
            in_markdown = False
            continue
            
        # Handle markdown cells
        if line.strip().startswith('# %% [markdown]'):
            in_code_cell = False
            in_markdown = True
            continue
            
        # Skip markdown content
        if in_markdown:
            continue
            
        # Handle magic commands
        if line.strip().startswith('%'):
            # Skip IPython magic commands
            if any(line.strip().startswith(magic) for magic in ['%run', '%md', '%sql']):
                continue
            if line.strip().startswith('%python'):
                # Keep the Python code after %python
                code = line.strip()[7:].strip()
                if code:
                    processed_lines.append(code)
            continue
            
        # Skip comments at the start of cells
        if line.strip().startswith('# ') and not in_code_cell:
            continue
            
        # Keep regular Python code
        processed_lines.append(line)
        
        # Reset in_code_cell flag if we hit a blank line
        if not line.strip():
            in_code_cell = False
    
    return '\n'.join(processed_lines)

@tool
def code_parser(codebase_path: str) -> Dict[str, Any]:
    """Analyzes all Python files in the codebase directory."""
    def analyze_file(file_path: str, source_code: str) -> Dict[str, Any]:
        try:
            # Preprocess Databricks notebook content
            cleaned_code = preprocess_databricks_notebook(source_code)
            
            if not cleaned_code.strip():
                print(f"Warning: No valid Python code found in {file_path} after preprocessing")
                return {
                    "data_operations": {},
                    "transformations": [],
                    "dependencies": [],
                    "data_quality_checks": [],
                    "performance_metrics": {
                        "partitioning": False,
                        "caching": False,
                        "optimization_hints": []
                    },
                    "patterns": {
                        "has_data_validation": False,
                        "has_error_handling": False,
                        "has_logging": False,
                        "has_data_quality_checks": False,
                        "has_performance_optimizations": False,
                        "has_documentation": False
                    }
                }

            tree = ast.parse(cleaned_code)
            analysis = {
                "data_operations": {},
                "transformations": [],
                "dependencies": [],
                "data_quality_checks": [],
                "performance_metrics": {
                    "partitioning": False,
                    "caching": False,
                    "optimization_hints": []
                },
                "patterns": {
                    "has_data_validation": False,
                    "has_error_handling": False,
                    "has_logging": False,
                    "has_data_quality_checks": False,
                    "has_performance_optimizations": False,
                    "has_documentation": False
                }
            }

            # Extract imports and dependencies
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    analysis["dependencies"].extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["dependencies"].extend(f"{node.module}.{alias.name}" for alias in node.names)
                    else:
                        analysis["dependencies"].extend(alias.name for alias in node.names)

            # Analyze data operations and transformations
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check for data operations
                    if hasattr(node.func, 'attr'):
                        if node.func.attr in ['read', 'write', 'createOrReplaceTempView', 'cache', 'persist']:
                            analysis["data_operations"][node.func.attr] = {
                                "line_number": node.lineno,
                                "arguments": [ast.unparse(arg) for arg in node.args]
                            }
                        
                        # Check for data quality checks
                        if node.func.attr in ['filter', 'dropna', 'fillna', 'isNotNull']:
                            analysis["data_quality_checks"].append({
                                "type": node.func.attr,
                                "line_number": node.lineno,
                                "arguments": [ast.unparse(arg) for arg in node.args]
                            })
                        
                        # Check for performance optimizations
                        if node.func.attr in ['repartition', 'coalesce', 'cache', 'persist']:
                            analysis["performance_metrics"]["optimization_hints"].append({
                                "type": node.func.attr,
                                "line_number": node.lineno,
                                "arguments": [ast.unparse(arg) for arg in node.args]
                            })
                            if node.func.attr in ['cache', 'persist']:
                                analysis["performance_metrics"]["caching"] = True
                            elif node.func.attr in ['repartition', 'coalesce']:
                                analysis["performance_metrics"]["partitioning"] = True

                # Check for transformations
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    if isinstance(node.value, ast.Call):
                        if hasattr(node.value.func, 'attr'):
                            if node.value.func.attr in ['select', 'withColumn', 'groupBy', 'agg', 'join']:
                                analysis["transformations"].append({
                                    "type": node.value.func.attr,
                                    "line_number": node.lineno,
                                    "target": ast.unparse(node.targets[0]) if isinstance(node, ast.Assign) else ast.unparse(node.target),
                                    "arguments": [ast.unparse(arg) for arg in node.value.args]
                                })

            # Update patterns
            analysis["patterns"]["has_data_validation"] = len(analysis["data_quality_checks"]) > 0
            analysis["patterns"]["has_performance_optimizations"] = len(analysis["performance_metrics"]["optimization_hints"]) > 0
            analysis["patterns"]["has_error_handling"] = any(isinstance(n, ast.Try) for n in ast.walk(tree))
            analysis["patterns"]["has_logging"] = any(
                isinstance(n, ast.Call) and 
                hasattr(n.func, "attr") and 
                n.func.attr in ["info", "error", "warning", "debug"]
                for n in ast.walk(tree)
            )
            analysis["patterns"]["has_documentation"] = bool(ast.get_docstring(tree))

            return analysis
        except Exception as e:
            print(f"Error analyzing {file_path}: {str(e)}")
            return {"error": str(e)}

    # Initialize results dictionary
    codebase_analysis = {
        "files": {},
        "summary": {
            "total_files": 0,
            "total_transformations": 0,
            "total_data_operations": 0,
            "patterns": {
                "files_with_data_validation": 0,
                "files_with_error_handling": 0,
                "files_with_logging": 0,
                "files_with_performance_optimizations": 0,
                "files_with_documentation": 0
            }
        }
    }

    # Convert codebase_path to Path object for better path handling
    codebase_path = Path(codebase_path)
    
    # Define directories to exclude
    exclude_dirs = {'venv', '__pycache__', '.git', '.pytest_cache', '.vscode'}
    
    # Walk through the codebase directory recursively
    try:
        for root, dirs, files in os.walk(codebase_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(codebase_path)
                    
                    try:
                        print(f"\nAnalyzing: {relative_path}")
                        with open(file_path, 'r', encoding='utf-8') as f:
                            source_code = f.read()
                        
                        # Analyze the file
                        analysis = analyze_file(str(relative_path), source_code)
                        
                        if "error" not in analysis:
                            # Store the analysis
                            codebase_analysis["files"][str(relative_path)] = analysis
                            
                            # Update summary statistics
                            codebase_analysis["summary"]["total_files"] += 1
                            codebase_analysis["summary"]["total_transformations"] += len(analysis["transformations"])
                            codebase_analysis["summary"]["total_data_operations"] += len(analysis["data_operations"])
                            
                            if analysis["patterns"]["has_data_validation"]:
                                codebase_analysis["summary"]["patterns"]["files_with_data_validation"] += 1
                            if analysis["patterns"]["has_error_handling"]:
                                codebase_analysis["summary"]["patterns"]["files_with_error_handling"] += 1
                            if analysis["patterns"]["has_logging"]:
                                codebase_analysis["summary"]["patterns"]["files_with_logging"] += 1
                            if analysis["patterns"]["has_performance_optimizations"]:
                                codebase_analysis["summary"]["patterns"]["files_with_performance_optimizations"] += 1
                            if analysis["patterns"]["has_documentation"]:
                                codebase_analysis["summary"]["patterns"]["files_with_documentation"] += 1
                            
                            print(f"Found {len(analysis['transformations'])} transformations and {len(analysis['data_operations'])} data operations")
                        else:
                            print(f"Skipping {relative_path} due to error: {analysis['error']}")
                    
                    except Exception as e:
                        print(f"Error processing {relative_path}: {str(e)}")
                        continue

    except Exception as e:
        print(f"Error accessing directory {codebase_path}: {str(e)}")
        return {"error": str(e)}

    # Print summary
    print("\nCodebase Analysis Summary:")
    print(f"Total Python files: {codebase_analysis['summary']['total_files']}")
    print(f"Total transformations: {codebase_analysis['summary']['total_transformations']}")
    print(f"Total data operations: {codebase_analysis['summary']['total_data_operations']}")
    print("\nPatterns found:")
    for pattern, count in codebase_analysis["summary"]["patterns"].items():
        print(f"- {pattern}: {count} files")

    return codebase_analysis


@tool
def code_validator(code_analysis: Dict[str, Any], blueprint_rules: Dict[str, List[str]]) -> Dict[str, Any]:
    """Compare code patterns against blueprint rules and generate detailed validation report."""
    validation_results = {
        "compliant": [],
        "violations": [],
        "warnings": [],
        "suggestions": [],
        "metrics": {
            "overall_compliance": 0,
            "rule_coverage": 0,
            "data_quality_score": 0,
            "performance_score": 0
        }
    }

    def check_data_quality():
        if blueprint_rules.get("data_handling"):
            for file_path, analysis in code_analysis.get("files", {}).items():
                if not analysis["patterns"]["has_data_validation"]:
                    validation_results["violations"].append({
                        "type": "data_quality",
                        "message": f"File '{file_path}' lacks data quality checks",
                        "severity": "high"
                    })
                else:
                    validation_results["compliant"].append({
                        "type": "data_quality",
                        "message": f"File '{file_path}' has data quality checks",
                        "details": analysis["data_quality_checks"]
                    })

    def check_performance_optimizations():
        if blueprint_rules.get("performance_guidelines"):
            for file_path, analysis in code_analysis.get("files", {}).items():
                if not analysis["patterns"]["has_performance_optimizations"]:
                    validation_results["warnings"].append({
                        "type": "performance",
                        "message": f"File '{file_path}' lacks performance optimizations",
                        "severity": "medium"
                    })
                else:
                    validation_results["compliant"].append({
                        "type": "performance",
                        "message": f"File '{file_path}' has performance optimizations",
                        "details": analysis["performance_metrics"]
                    })

    def check_error_handling():
        if blueprint_rules.get("error_handling"):
            for file_path, analysis in code_analysis.get("files", {}).items():
                if not analysis["patterns"]["has_error_handling"]:
                    validation_results["violations"].append({
                        "type": "error_handling",
                        "message": f"File '{file_path}' lacks proper error handling",
                        "severity": "high"
                    })

    def check_documentation():
        if blueprint_rules.get("documentation"):
            for file_path, analysis in code_analysis.get("files", {}).items():
                if not analysis["patterns"]["has_documentation"]:
                    validation_results["warnings"].append({
                        "type": "documentation",
                        "message": f"File '{file_path}' is missing documentation",
                        "severity": "medium"
                    })

    def check_data_operations():
        if blueprint_rules.get("data_handling"):
            for file_path, analysis in code_analysis.get("files", {}).items():
                if not analysis["data_operations"]:
                    validation_results["warnings"].append({
                        "type": "data_operations",
                        "message": f"File '{file_path}' has no data read/write operations",
                        "severity": "medium"
                    })
                else:
                    validation_results["compliant"].append({
                        "type": "data_operations",
                        "message": f"File '{file_path}' has data operations",
                        "details": analysis["data_operations"]
                    })

    # Run all checks
    check_data_quality()
    check_performance_optimizations()
    check_error_handling()
    check_documentation()
    check_data_operations()

    # Calculate metrics
    total_rules = sum(len(rules) for rules in blueprint_rules.values())
    total_violations = len(validation_results["violations"])
    total_warnings = len(validation_results["warnings"])
    
    if total_rules > 0:
        validation_results["metrics"]["rule_coverage"] = (total_violations + total_warnings) / total_rules
        validation_results["metrics"]["overall_compliance"] = 1 - (total_violations / total_rules)
        
        # Calculate data quality score
        data_quality_compliant = len([c for c in validation_results["compliant"] if c["type"] == "data_quality"])
        total_files = len(code_analysis.get("files", {}))
        if total_files > 0:
            validation_results["metrics"]["data_quality_score"] = data_quality_compliant / total_files
        
        # Calculate performance score
        performance_compliant = len([c for c in validation_results["compliant"] if c["type"] == "performance"])
        if total_files > 0:
            validation_results["metrics"]["performance_score"] = performance_compliant / total_files

    return validation_results


@tool
def generate_report(validation_results: Dict[str, Any], output_path: str) -> str:
    """Generate a detailed JSON report from validation results."""
    # Create a structured JSON report
    report = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "overall_compliance": validation_results["metrics"]["overall_compliance"],
            "rule_coverage": validation_results["metrics"]["rule_coverage"],
            "data_quality_score": validation_results["metrics"]["data_quality_score"],
            "performance_score": validation_results["metrics"]["performance_score"]
        },
        "violations": [
            {
                "type": v["type"],
                "message": v["message"],
                "severity": v["severity"]
            }
            for v in validation_results["violations"]
        ],
        "warnings": [
            {
                "type": w["type"],
                "message": w["message"],
                "severity": w["severity"]
            }
            for w in validation_results["warnings"]
        ],
        "compliant": [
            {
                "type": c["type"],
                "message": c["message"],
                "details": c.get("details", {})
            }
            for c in validation_results["compliant"]
        ],
        "suggestions": validation_results["suggestions"],
        "summary": {
            "total_violations": len(validation_results["violations"]),
            "total_warnings": len(validation_results["warnings"]),
            "total_compliant": len(validation_results["compliant"]),
            "violations_by_type": {},
            "warnings_by_type": {},
            "compliant_by_type": {}
        }
    }
    
    # Calculate summaries by type
    for v in validation_results["violations"]:
        report["summary"]["violations_by_type"][v["type"]] = report["summary"]["violations_by_type"].get(v["type"], 0) + 1
    
    for w in validation_results["warnings"]:
        report["summary"]["warnings_by_type"][w["type"]] = report["summary"]["warnings_by_type"].get(w["type"], 0) + 1
    
    for c in validation_results["compliant"]:
        report["summary"]["compliant_by_type"][c["type"]] = report["summary"]["compliant_by_type"].get(c["type"], 0) + 1
    
    # Write the JSON report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return output_path
