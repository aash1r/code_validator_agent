import os

from crewai import Crew

from tasks import analyze_code, generate_report, parse_blueprint, verify_code

# Define Crew
crew = Crew(
    tasks=[
        parse_blueprint,
        analyze_code,
        verify_code,
        generate_report,
    ],
    verbose=True,
)

# Run the workflow
if __name__ == "__main__":
    blueprint_path = os.path.join(
        "blueprints", "Why and how loops should be avoided in ETLs_ELTs.docx"
    )
    codebase_path = os.path.join("ecommerce/app/routes", "products.py")
    # Kick off Crew tasks
    results = crew.kickoff(
        inputs={"blueprint_path": blueprint_path, "codebase_path": codebase_path}
    )
    print(results)
