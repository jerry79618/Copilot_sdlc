"""Read-only project inventory and progressive natural-language SDLC task context.

A draft context is NOT a validated Task Contract, permission grant, or test evidence.
"""
from pathlib import Path

from .contracts import ContractError, ROOT
from .mode import classify


def project_root(path):
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise ContractError("Project root does not exist: " + str(root))
    return root


def inspect_project(path):
    root = project_root(path)

    def exists(relative):
        target = root / relative
        return target.is_file() and target.resolve().is_relative_to(root)

    build_files = [path for path in (
        "pom.xml", "build.gradle", "build.gradle.kts",
        "settings.gradle", "settings.gradle.kts", "gradlew", "mvnw"
    ) if exists(path)]
    docs = [path for path in ("AGENTS.md", "README.md", "docs/architecture.md")
            if exists(path)]
    folder = root / "docs" / "feature-map"
    maps = []
    if folder.is_dir() and not folder.is_symlink():
        maps = [item.relative_to(root).as_posix()
                for item in sorted(folder.glob("*.md"))
                if item.is_file() and not item.is_symlink() and item.resolve().is_relative_to(root)]
    # No source code/PII is read during preflight, only known file paths.
    return {
        "project_root": str(root),
        "build_files": build_files,
        "orientation_documents": docs,
        "feature_map_files": maps,
        "feature_map_count": len(maps),
        "inventory_level": "paths_only_not_verified",
    }


def prepare(goal, path="."):
    inventory = inspect_project(path)
    route = classify(goal)
    intent = route["intent"]
    return {
        "schema_version": 1,
        "type": "SDLC_TASK_CONTEXT_DRAFT",
        "state": "DRAFT_NOT_EXECUTABLE",
        "goal": goal,
        "project": inventory,
        "framework_root": str(ROOT.resolve()),
        "routing": route,
        "authorization": {
            "product_code_changes": ("NOT_ALLOWED" if intent != "development" else "REVIEW_USER_SCOPE"),
            "test_code_changes": ("NOT_ALLOWED" if intent == "investigation" else "REVIEW_USER_SCOPE"),
            "production_data_writes": "NOT_AUTHORIZED",
            "deployment_or_merge": "NOT_AUTHORIZED",
        },
        "unconfirmed": [
            "acceptance_criteria", "affected_systems", "risk_and_impact_flags",
            "approved_environment", "runtime_adapter_and_evidence"
        ],
        "next_action": "Inspect relevant project sources, clarify actual business constraints, then create a validated Task Contract when prerequisites are established.",
        "limitations": [
            "Routing is a suggestion, not authenticated Agent dispatch.",
            "Draft does not authorize modifications or constitute a runnable Task Contract.",
            "Missing bank policy, privileged permissions and real adapters cannot be guessed.",
        ],
    }
