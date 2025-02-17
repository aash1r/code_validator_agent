import os

from crewai import Crew

from tasks import analyze_code, parse_blueprint, verify_code

crew = Crew(
    tasks=[parse_blueprint, analyze_code, verify_code],
    verbose=True,
)

if __name__ == "__main__":
    blueprint_path = os.path.join("blueprints", "FastAPI_Blueprint.docx")
    codebase_path = os.path.join("ecommerce/app/routes", "sample.py")
    results = crew.kickoff(
        inputs={"blueprint_path": blueprint_path, "codebase_path": codebase_path}
    )
    print(results)
