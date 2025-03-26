import os
from datetime import datetime
from pathlib import Path
from crewai import Crew
from crewai.crews.crew_output import CrewOutput

from tasks import parse_blueprints, analyze_codebase, verify_compliance

def create_output_directory():
    """Create a timestamped output directory for reports."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("reports") / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def get_blueprint_files(blueprints_dir: Path) -> list:
    """Get all .docx files from the blueprints directory."""
    docx_files = list(blueprints_dir.glob("*.docx"))
    if not docx_files:
        raise ValueError(f"No .docx files found in {blueprints_dir}")
    return docx_files

def validate_codebase_path(codebase_path: Path):
    """Validate that the codebase path exists and contains Python files."""
    if not codebase_path.exists():
        raise ValueError(f"Codebase directory not found: {codebase_path}")
    
    # Find Python files recursively in all subdirectories, excluding system directories
    exclude_dirs = {'venv', '__pycache__', '.git', '.pytest_cache', '.vscode'}
    python_files = []
    
    for root, dirs, files in os.walk(codebase_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                python_files.append(file_path)
    
    if not python_files:
        raise ValueError(f"No Python files found in {codebase_path}")
    
    return python_files

def main():
    # Create output directory for reports
    output_dir = create_output_directory()
    
    # Define paths
    blueprints_dir = Path("blueprints").resolve()
    codebase_path = Path("Lipton-DSR").resolve()
    
    # Validate paths and get files
    if not blueprints_dir.exists():
        raise ValueError(f"Blueprints directory not found: {blueprints_dir}")
    
    blueprint_files = get_blueprint_files(blueprints_dir)
    python_files = validate_codebase_path(codebase_path)
    
    print(f"\nFound {len(blueprint_files)} blueprint files:")
    for bp_file in blueprint_files:
        print(f"- {bp_file.name}")
        
    print(f"\nFound {len(python_files)} Python files in codebase:")
    for py_file in python_files:
        rel_path = py_file.relative_to(codebase_path)
        print(f"- {rel_path}")

    # Initialize the crew with enhanced tasks
    crew = Crew(
        tasks=[parse_blueprints, analyze_codebase, verify_compliance],
        verbose=True,
    )

    # Run the analysis
    results: CrewOutput = crew.kickoff(
        inputs={
            # For parse_blueprints
            "blueprint_files": [f.name for f in blueprint_files],
            # For analyze_codebase
            "codebase_path": str(codebase_path),
            # For all tasks
            "output_dir": str(output_dir)
        }
    )

    # Generate final report path
    report_path = output_dir / "validation_report.json"
    
    # Print summary
    print("\nAnalysis Complete!")
    print(f"Reports generated in: {output_dir}")
    print(f"Main report: {report_path}")
    print("\nSummary of Results:")
    print(results)

if __name__ == "__main__":
    main()
