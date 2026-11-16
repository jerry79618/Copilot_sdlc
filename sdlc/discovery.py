"""Read-only Feature Map discovery and maintenance support.

Inspects local Java Spring annotations, Gherkin tags and existing map bindings.
Outputs conservative drafts. Static source evidence is never runtime proof.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from .contracts import ContractError, ROOT
from .feature_map import load_feature_map

IGNORE = {".git", ".venv", "node_modules", "target", "build", "dist",
          ".gradle", "__pycache__", "artifacts"}
CLASS = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)")
BASE = re.compile(r'@RequestMapping\s*\(\s*(?:value\s*=\s*|path\s*=\s*)?"([^"]+)"')
ENDPOINT = re.compile(
    r'@(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RequestMapping)'
    r'\s*(?:\(\s*(?:value\s*=\s*|path\s*=\s*)?"([^"]*)"[^\)]*\))?'
)
FEATURE_TAG = re.compile(r"@feature_([a-z][a-z0-9_]*)")
SAFE = re.compile(r"[^a-z0-9-]+")


def _files(project, suffix):
    """Do not traverse symlink folders or external source paths."""
    root = Path(project).resolve()
    if not root.is_dir():
        raise ContractError("Project root does not exist: " + str(root))
    for path in sorted(root.rglob("*")):
        if any(part in IGNORE for part in path.relative_to(root).parts):
            continue
        if path.is_symlink() or not path.is_file() or path.suffix != suffix:
            continue
        if not path.resolve().is_relative_to(root):
            continue
        yield path


def _slug(text):
    s = SAFE.sub("-", text.lower().replace("_", "-")).strip("-")
    return s or "unknown-feature"


def inspect(project=ROOT):
    """Return candidate inventory; endpoints are syntactic hints only."""
    root = Path(project).resolve()
    controllers, features = [], []
    for path in _files(root, ".java"):
        if path.stat().st_size > 1_000_000:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        if not any(a in source for a in ("@RestController", "@Controller")):
            continue
        cls = CLASS.search(source)
        name = cls.group(1) if cls else path.stem
        prefix = BASE.search(source)
        mappings = []
        for match in ENDPOINT.finditer(source):
            method = match.group(1).replace("Mapping", "").upper()
            if method == "REQUEST":
                method = "ANY"
            endpoint = match.group(2) or ""
            if method == "ANY" and prefix and endpoint == prefix.group(1):
                continue  # class-level path is not itself an operation
            mappings.append({"method": method, "path_hint": endpoint})
        if not mappings:
            continue
        controllers.append({
            "feature_id": _slug(name.removesuffix("Controller")),
            "controller": name,
            "source": path.relative_to(root).as_posix(),
            "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "base_path_hint": prefix.group(1) if prefix else None,
            "mappings": mappings,
            "status": "SOURCE_CANDIDATE_NOT_RUNTIME_VERIFIED",
        })
    for path in _files(root, ".feature"):
        raw = path.read_text(encoding="utf-8", errors="replace")
        tags = sorted(set(FEATURE_TAG.findall(raw)))
        features.append({"path": path.relative_to(root).as_posix(),
                         "tagged_features": [t.replace("_", "-") for t in tags],
                         "scenarios": len(re.findall(r"^\s*Scenario(?: Outline)?:", raw, re.M)),
                         "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest()})
    return {
        "project": str(root), "mode": "static-discovery-only",
        "limitations": [
            "Regex does not resolve Java aliases, meta-annotations, inheritance or runtime routes.",
            "Endpoints and scenarios have not been driven through a running application.",
            "Business rules and negative cases must be confirmed by owners.",
        ],
        "java_controllers": controllers, "gherkin_features": features,
    }


def draft_map(controller):
    """Generate a *candidate* that intentionally cannot be mistaken for a verified map."""
    endpoints = controller["mappings"]
    lines = [
        "# Proposed Feature Map — " + controller["controller"],
        "",
        "> STATUS: DRAFT / SOURCE-DERIVED / NOT VERIFIED. Requires owner review and runtime test.",
        "",
        "## Sub-features",
    ]
    for mapping in endpoints:
        lines.append("- Candidate " + mapping["method"] + " " +
                     (controller.get("base_path_hint") or "") + mapping["path_hint"])
    lines.extend([
        "", "## How to get to it (user POV)",
        "- TODO: confirm actual UI/CLI/API entry point by running the system.",
        "", "## Driving it (runtime)",
        "- TODO: create an approved harness, fixture and Cucumber journey.",
        "- Runtime proof not available from static code discovery.",
        "", "## Gotchas",
        "- TODO: confirm auth, data, business rules, asynchronous dependencies, and cleanup.",
        "", "## Source discovery evidence",
        "- Controller: " + controller["source"],
        "- Source SHA256: " + controller["source_sha256"],
        "- Result: PROPOSED (not a passing test)",
        "",
    ])
    return "\n".join(lines)


def map_health(project=ROOT):
    """Static drift checks for known maps; failures are visible, not auto-patched."""
    root = Path(project).resolve()
    maps = sorted((root / "docs" / "feature-map").glob("*.md"))
    findings = []
    for file in maps:
        relative = file.relative_to(root).as_posix()
        raw = file.read_text(encoding="utf-8", errors="replace")
        if "## SDLC Cucumber Binding" not in raw:
            findings.append({"path": relative, "status": "CANDIDATE_REVIEW_REQUIRED",
                             "note": "No executable binding; business and runtime review needed"})
            continue
        try:
            verified = load_feature_map(relative, project_root=root)
            findings.append({"path": relative, "status": "STATIC_LINKS_VALID",
                             "feature_id": verified["feature_id"],
                             "note": "Source links valid; runtime correctness NOT established"})
        except (ContractError, OSError, ValueError) as exc:
            findings.append({"path": relative, "status": "DRIFT", "reason": str(exc)})
    return findings


def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only Java/Cucumber Feature Map discovery")
    p.add_argument("command", choices=["inspect", "candidates", "health"])
    p.add_argument("--project-root", default=str(ROOT))
    p.add_argument("--output-dir", help="Candidate directory inside selected project; defaults to artifacts/discovery")
    args = p.parse_args(argv)
    try:
        root = Path(args.project_root).resolve()
        if not root.is_dir():
            raise ContractError("Invalid project root")
        output = (Path(args.output_dir) if args.output_dir else root / "artifacts" / "discovery").resolve()
        if not output.is_relative_to(root / "artifacts"):
            raise ContractError("Candidate output must stay inside the target project's artifacts directory")
        data = inspect(root) if args.command != "health" else {
            "project": str(root), "map_health": map_health(root),
        }
        if args.command == "candidates":
            output.mkdir(parents=True, exist_ok=True)
            for controller in data["java_controllers"]:
                path = output / (controller["feature_id"] + ".candidate.md")
                if path.exists():
                    raise ContractError("Refusing to overwrite existing candidate: " + str(path))
                path.write_text(draft_map(controller), encoding="utf-8")
            data["candidate_output_dir"] = str(output)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        if args.command == "health" and any(f["status"] == "DRIFT" for f in data["map_health"]):
            return 2
        return 0
    except (ContractError, ValueError, OSError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
