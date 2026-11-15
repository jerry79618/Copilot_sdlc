"""Translate Cucumber-JVM JSON results into the existing SDLC evidence contract."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .contracts import ContractError, load_json, validate_task
from .feature_map import load_feature_map


def convert(task, feature_map, report):
    validate_task(task)
    binding = feature_map["binding"]
    output = {
        "task_id": task["id"], "scenario_id": binding["scenario_id"],
        "feature_map": feature_map["path"], "environment": task["environment"],
        "runner": "cucumber-jvm", "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "BLOCKED", "classification": "CUCUMBER_REPORT_UNAVAILABLE", "checks": [],
        "limitations": ["Synthetic in-memory adapter: this is NOT real multi-system E2E."],
    }
    if task["environment"] != "demo" or task.get("scenario") != binding["scenario"]:
        output["classification"] = "CONFIGURATION"
        return output
    if not isinstance(report, list):
        raise ContractError("Expected Cucumber JSON array")
    required_tag = "@feature_" + binding["feature_id"].replace("-", "_")
    scenarios = []
    for feat in report:
        if not isinstance(feat, dict):
            continue
        feature_tags = {tag.get("name") for tag in feat.get("tags", []) if isinstance(tag, dict)}
        for elem in feat.get("elements", []):
            if not isinstance(elem, dict) or elem.get("type") != "scenario":
                continue
            tags = feature_tags | {t.get("name") for t in elem.get("tags", []) if isinstance(t, dict)}
            if required_tag in tags:
                scenarios.append(elem)
    if not scenarios:
        output["classification"] = "FEATURE_TAG_MISSING"
        return output
    failed = []
    for scenario in scenarios:
        steps = scenario.get("steps", [])
        if not steps:
            failed.append("No executable steps: " + scenario.get("name", "unknown"))
        for step in steps:
            status = step.get("result", {}).get("status", "undefined")
            output["checks"].append({
                "scenario": scenario.get("name", ""),
                "step": step.get("name", ""), "status": status,
            })
            if status != "passed":
                failed.append(scenario.get("name", "unknown") + ": " + status)
    if failed:
        output.update(status="FAIL", classification="CUCUMBER_STEP_FAILURE",
                      reason="; ".join(failed))
    else:
        output.update(status="PASS", classification="CUCUMBER_DEMO_VERIFIED",
                      reason="All matching Cucumber scenarios passed against the sandbox adapter")
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convert Cucumber JSON into SDLC G4 evidence")
    parser.add_argument("--task", required=True)
    parser.add_argument("--feature", required=True)
    parser.add_argument("--report", default="cucumber/target/cucumber-report/cucumber.json")
    parser.add_argument("--output", default="artifacts/cucumber-evidence.json")
    args = parser.parse_args(argv)
    try:
        fm = load_feature_map("docs/feature-map/" + args.feature + ".md")
        evidence = convert(load_json(args.task), fm, load_json(args.report))
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": evidence["status"], "classification": evidence["classification"],
                          "evidence_file": str(target)}, ensure_ascii=False))
        return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[evidence["status"]]
    except (OSError, ValueError, KeyError, ContractError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
