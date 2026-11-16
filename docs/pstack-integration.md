# Lauren Tan pstack upstream integration (v0.8)

## Source, license and scope

- Source: https://github.com/cursor/plugins/tree/bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7/pstack
- Author: Lauren Tan (poteto).
- Source plugin version: **0.15.42**.
- License: **MIT**, full upstream notice retained at vendor/pstack/LICENSE.
- Version manifest: vendor/pstack/MANIFEST.json, with Git blob hashes for every file.
- The vendored snapshot includes the **original pstack mode, all 23 playbook text files,
  and 18 selected original method/verification/principle Skill files** (44 imported
  upstream files total, including LICENSE and plugin.json; the local MANIFEST
  is an additional provenance file).
- It is a **curated source reference**, not the full 560-file pstack plugin.
  Original material inside vendor/pstack is left unchanged.
- This is an independent adaptation for Copilot CLI, not an official pstack release.

## How it integrates with existing SDLC

The original pstack files live under vendor/pstack, outside .github/skills.
This avoids registering dozens of overlapping global Skills in the default
Copilot CLI session.

config/pstack-bridge.json maps **all eleven** local SDLC Playbook IDs to an
appropriate pstack playbook and/or principle/verification reference.

sdlc/entrypoint.py now adds pstack_reference to a normal route result.
The Orchestrator reads the relevant **reference** and translates its general
engineering guidance to existing Copilot CLI capabilities. This does not
replace the local stages, Task Contract, approval policy or evidence gates.

~~~powershell
cd D:\git\Copilot_sdlc
python -m sdlc.pstack_bridge check
python -m sdlc.pstack_bridge route --goal "修正申請查詢錯誤"
python -m sdlc.entrypoint route --project-root "D:\git\bank-application" --goal "修正申請查詢錯誤"
~~~

A normal SDLC launch is unchanged:

~~~powershell
.\scripts\start-sdlc.ps1 -ProjectRoot "D:\git\bank-application" -Isolated -Goal "修正申請查詢錯誤"
~~~

## Priority / safety rules

1. User intent and explicit restrictions override any upstream example.
2. Target Java project facts and approved banking business rules are authoritative.
3. Central SDLC model policy, Task Contracts, human approval and G1-G6 govern.
4. Real staging G4 remains BLOCKED until an approved adapter and evidence exists.
5. Upstream scripts, Cursor commands, model names, subagent definitions and
   autonomous PR babysitting, shipping or autopilot are **not executable** here.
6. Do not copy vendor/pstack/skills into ~/.copilot/skills or the Java project.
   Read only mapped source references during the relevant Playbook stage.

Upstream documentation may propose broad autonomy or model switching. Those
directions are not permissions in this banking framework. No new Agent has
been registered and no source code in bank-application was modified.

## To update upstream later

Compare the current source commit against a newer public pstack release.
Refresh the curated files and MANIFEST atomically, retain the MIT LICENSE,
recheck route mapping and user permission boundaries, and run:

~~~bash
python -m sdlc.pstack_bridge check
python -m unittest discover -s tests -v
python -m sdlc.model_policy check
~~~

Check the real Copilot session separately: Python can validate file integrity
and routing references, but not confirm model availability or actual subagent
execution. The original Cursor plugin can be used in Cursor; these reference
files are not a drop-in Copilot implementation of /poteto-mode.
