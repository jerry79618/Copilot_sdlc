import tempfile
import unittest
from pathlib import Path

from sdlc.contracts import ROOT
from sdlc.entrypoint import doctor, route
from sdlc.mode import catalog


class PotetoModeTests(unittest.TestCase):
    def test_native_skill_and_agent_follow_copilot_conventions(self):
        skill = ROOT / '.github/skills/poteto-mode/SKILL.md'
        agent = ROOT / '.github/agents/orchestrator.agent.md'
        body = skill.read_text(encoding='utf-8')
        self.assertTrue(body.startswith('---\n'))
        header = body.split('---', 2)[1]
        self.assertIn('name: poteto-mode', header)
        self.assertIn('description:', header)
        self.assertIn('entry point', body.lower())
        self.assertIn('.github/skills/poteto-mode/SKILL.md', agent.read_text(encoding='utf-8'))

    def test_legacy_skill_is_only_an_alias(self):
        body = (ROOT / '.github/skills/sdlc-mode/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('name: sdlc-mode', body)
        self.assertIn('../poteto-mode/SKILL.md', body)
        self.assertIn('legacy', body.lower())

    def test_doctor_reports_canonical_mode_and_actual_path(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / 'home'
            project = Path(d) / 'bank'
            home.mkdir()
            project.mkdir()
            result = doctor(project, copilot_home=home)
            self.assertEqual(result['status'], 'READY')
            mode = result['mode']
            self.assertEqual(mode['name'], 'poteto-mode')
            self.assertEqual(mode['owner'], 'session-main-agent')
            self.assertEqual(mode['optional_coordinator'], 'orchestrator')
            self.assertFalse(result['dedicated_orchestrator_required'])
            self.assertTrue(Path(mode['skill_path']).is_file())
            self.assertEqual(mode['legacy_skill'], 'sdlc-mode')
            self.assertIn('poteto-mode', [x['name'] for x in result['source_candidates']])

    def test_short_goal_routes_playbook_with_mode_and_pstack_reference(self):
        with tempfile.TemporaryDirectory() as d:
            result = route('修正查詢錯誤', project_root=d)
            self.assertEqual(result['mode']['name'], 'poteto-mode')
            self.assertEqual(result['mode']['owner'], 'session-main-agent')
            self.assertEqual(result['mode']['optional_coordinator'], 'orchestrator')
            self.assertEqual(result['execution_strategy']['owner'], 'current-copilot-session-main-agent')
            self.assertEqual(result['decision']['playbook'], 'bug-fix')
            self.assertEqual(result['pstack_reference']['mode'], 'REFERENCE_ONLY')
            self.assertEqual(len(catalog()), 11)

    def test_global_poteto_shadow_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / '.copilot'
            override = home / 'skills/poteto-mode/SKILL.md'
            override.parent.mkdir(parents=True)
            override.write_text('old mode', encoding='utf-8')
            result = doctor(ROOT, copilot_home=home)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertTrue(any(x['kind'] == 'skill' for x in result['shadow_conflicts']))

    def test_project_poteto_shadow_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'bank'
            home = Path(d) / 'home'
            root.mkdir()
            home.mkdir()
            override = root / '.github/skills/poteto-mode/SKILL.md'
            override.parent.mkdir(parents=True)
            override.write_text('old mode', encoding='utf-8')
            result = doctor(root, copilot_home=home)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertTrue(any(str(override) == c['path'] for c in result['shadow_conflicts']))

    def test_old_launcher_delegates_to_new_one(self):
        launcher = (ROOT / 'scripts/start-poteto.ps1').read_text(encoding='utf-8')
        legacy = (ROOT / 'scripts/start-sdlc.ps1').read_text(encoding='utf-8')
        self.assertIn('$cliArguments = @("--add-dir=$frameworkRoot")', launcher)
        self.assertIn('if ($UseLegacyOrchestrator)', launcher)
        self.assertIn('--agent=orchestrator', launcher)
        self.assertIn('Use the /poteto-mode skill', launcher)
        self.assertIn('--add-dir=', launcher)
        self.assertIn('python -m sdlc.entrypoint doctor', launcher)
        self.assertIn('start-poteto.ps1', legacy)
        self.assertIn('@PSBoundParameters', legacy)


if __name__ == '__main__':
    unittest.main()
