"""Read-only integration of vendored Lauren Tan pstack methods into SDLC routing.

The upstream materials are references. This module does not execute Cursor
commands, permit automation, dispatch agents, or change banking evidence policy.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from .contracts import ContractError, ROOT, load_json
from .mode import catalog, classify

VENDOR = ROOT / "vendor" / "pstack"
MANIFEST = VENDOR / "MANIFEST.json"
CONFIG = ROOT / "config" / "pstack-bridge.json"


def _source(relative, root=VENDOR):
    if not isinstance(relative, str) or not relative.strip():
        raise ContractError("pstack source path must be nonempty")
    base = Path(root).resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise ContractError("pstack source is missing or outside vendor tree: " + relative)
    return path


def git_blob_sha(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_sources(root=VENDOR, manifest=None):
    """Detect vendored source drift relative to recorded upstream Git blob IDs."""
    base = Path(root).resolve()
    meta = manifest if manifest is not None else load_json(base / "MANIFEST.json")
    files = meta.get("files")
    if meta.get("schema_version") != 1 or meta.get("license") != "MIT":
        raise ContractError("Unrecognized pstack source provenance")
    if not isinstance(files, dict) or not files:
        raise ContractError("pstack manifest must list source files")
    if "LICENSE" not in files or "plugin.json" not in files:
        raise ContractError("pstack license and plugin metadata are required")
    for relative, expected in files.items():
        path = _source(relative, base)
        if not isinstance(expected, str) or len(expected) != 40:
            raise ContractError("Invalid pstack source hash: " + relative)
        if git_blob_sha(path) != expected:
            raise ContractError("Vendored pstack content drift: " + relative)
    plugin = load_json(_source("plugin.json", base))
    if plugin.get("version") != meta.get("upstream_version") or plugin.get("license") != "MIT":
        raise ContractError("Vendored pstack plugin version/license mismatch")
    return {"status": "PASS", "source_files": len(files),
            "upstream_commit": meta["upstream_commit"],
            "upstream_version": meta["upstream_version"],
            "scope": meta.get("scope", "curated reference")}


def _bridge_config(config=None):
    doc = config if config is not None else load_json(CONFIG)
    if (doc.get("schema_version") != 1 or doc.get("mode") != "reference-only"
            or doc.get("enabled") is not True):
        raise ContractError("pstack bridge must stay explicitly reference-only")
    if set(doc.get("routes", {})) != set(catalog()):
        raise ContractError("pstack bridge must explicitly map all local Playbooks")
    manifest = load_json(MANIFEST)
    if doc.get("upstream_commit") != manifest.get("upstream_commit"):
        raise ContractError("pstack bridge and vendored manifest use different upstream commits")
    if doc.get("upstream_version") != manifest.get("upstream_version"):
        raise ContractError("pstack bridge and vendored manifest use different versions")
    if doc.get("license_path") != "vendor/pstack/LICENSE":
        raise ContractError("pstack MIT notice must be preserved")
    for name, mapping in doc["routes"].items():
        if not isinstance(mapping, dict):
            raise ContractError("Invalid pstack route: " + name)
        paths = ([mapping["playbook"]] if mapping.get("playbook") else [])
        for key in ("skills", "principles"):
            values = mapping.get(key)
            if not isinstance(values, list) or not values:
                raise ContractError("Missing " + key + " for pstack route " + name)
            paths.extend(values)
        for path in paths:
            if path not in manifest["files"]:
                raise ContractError("Untracked pstack source in " + name + ": " + str(path))
            _source(path)
    return doc


def for_playbook(playbook):
    """Return inspectable references only; never grant execution or bank changes."""
    doc = _bridge_config()
    if playbook not in doc["routes"]:
        raise ContractError("No pstack reference for local Playbook: " + playbook)
    binding = doc["routes"][playbook]
    def mapped(files):
        return [{"source": "Lauren Tan / pstack", "relative": file,
                 "path": str(_source(file))} for file in files]
    return {
        "mode": "REFERENCE_ONLY",
        "upstream_version": doc["upstream_version"],
        "upstream_commit": doc["upstream_commit"],
        "original_playbook": mapped([binding["playbook"]]) if binding.get("playbook") else [],
        "skills": mapped(binding["skills"]),
        "principles": mapped(binding["principles"]),
        "licence_notice": str(ROOT / doc["license_path"]),
        "rules": [
            "Local SDLC Playbook, Task Contract, banking risk policy and G4 gates take precedence.",
            "Read relevant upstream text for engineering methodology only.",
            "Do NOT execute Cursor-specific commands, model overrides or autonomous shipping.",
            "A reference is not a tool invocation, test result or permission grant.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only verification of pstack source and mapped methods")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    selected = sub.add_parser("route")
    args_group = selected.add_mutually_exclusive_group(required=True)
    args_group.add_argument("--goal")
    args_group.add_argument("--playbook")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            sources = verify_sources()
            _bridge_config()
            response = {**sources, "mapped_playbooks": len(catalog()),
                        "note": "Source integrity and mapping only; Copilot runtime not verified."}
        else:
            ident = args.playbook or classify(args.goal)["playbook"]
            response = for_playbook(ident)
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return 0
    except (ContractError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
