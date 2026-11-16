"""Validate behavioral Feature Map and Cucumber/Scenario/Task links."""
import argparse
import json
import re
import sys
from pathlib import Path
from .contracts import ROOT, ContractError, load_json, repo_path, validate_scenario, validate_task

HEADERS = [
    "## Sub-features", "## How to get to it (user POV)",
    "## Driving it (runtime)", "## Gotchas", "## SDLC Cucumber Binding",
]
FENCE = re.compile(r"\x60{3}json\s*(\{.*?\})\s*\x60{3}", re.S)
SAFE_ID = re.compile(r"^[a-z][a-z0-9-]*$")


def load_feature_map(relative, project_root=ROOT):
    source = repo_path(relative, "docs/feature-map", project_root)
    if not source.is_file():
        raise ContractError("Feature Map does not exist: " + relative)
    markdown = source.read_text(encoding="utf-8")
    for header in HEADERS:
        if header not in markdown:
            raise ContractError("Feature Map is missing " + header)
    match = FENCE.search(markdown.split("## SDLC Cucumber Binding", 1)[1])
    if not match:
        raise ContractError("Feature Map needs a Cucumber binding JSON block")
    try:
        binding = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ContractError("Invalid Cucumber binding: " + str(exc)) from exc
    identifier = binding.get("feature_id")
    if not isinstance(identifier, str) or not SAFE_ID.fullmatch(identifier) or source.stem != identifier:
        raise ContractError("Feature Map id must match Markdown filename")
    for key, folder in (
        ("gherkin", "cucumber"), ("scenario", "scenarios"),
        ("contract", "contracts"), ("fixture", "fixtures")
    ):
        value = binding.get(key)
        if key == "gherkin" and isinstance(value, str) and value.replace(chr(92), "/").startswith("src/test/"):
            folder = "src/test"
        target = repo_path(value, folder, project_root)
        if not target.is_file():
            raise ContractError("Feature Map target missing: " + key)
    gherkin_path = binding["gherkin"]
    gherkin_folder = "src/test" if gherkin_path.replace(chr(92), "/").startswith("src/test/") else "cucumber"
    gherkin = repo_path(gherkin_path, gherkin_folder, project_root).read_text(encoding="utf-8")
    if not binding["gherkin"].endswith(".feature") or "@feature_" + identifier.replace("-", "_") not in gherkin:
        raise ContractError("Gherkin has no matching Feature Map tag")
    if "Scenario:" not in gherkin:
        raise ContractError("Feature Map points to an empty Gherkin feature")
    scenario = validate_scenario(load_json(repo_path(binding["scenario"], "scenarios", project_root)))
    task = validate_task(load_json(repo_path(binding["contract"], "contracts", project_root)), project_root=project_root)
    if scenario["id"] != binding.get("scenario_id") or task.get("scenario") != binding["scenario"]:
        raise ContractError("Scenario/Task Contract links mismatch")
    if set(binding.get("systems", [])) != set(scenario["systems"]):
        raise ContractError("Feature Map systems differ from scenario systems")
    if not set(scenario["systems"]).issubset(set(task["systems"])):
        raise ContractError("Task Contract is missing an involved system")
    if scenario.get("adapter") != "demo" or binding.get("adapter") != "demo":
        raise ContractError("Only demo adapter is configured in v0.3")
    return {"feature_id": identifier, "path": relative, "binding": binding}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate Feature Map / Gherkin link")
    parser.add_argument("command", choices=["validate", "list"])
    parser.add_argument("--feature", help="ID of Feature Map to check; default all")
    parser.add_argument("--project-root", default=str(ROOT))
    args = parser.parse_args(argv)
    try:
        project = Path(args.project_root).resolve()
        if not project.is_dir():
            raise ContractError("Invalid project root")
        if args.feature:
            if not SAFE_ID.fullmatch(args.feature):
                raise ContractError("Invalid feature id")
            paths = ["docs/feature-map/" + args.feature + ".md"]
        else:
            paths = [p.relative_to(project).as_posix() for p in sorted((project / "docs/feature-map").glob("*.md"))]
        if not paths:
            raise ContractError("No Feature Map files found")
        result = [load_feature_map(path, project_root=project) for path in paths]
        print(json.dumps({"status": "PASS", "features": result}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, ContractError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
