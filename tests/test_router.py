#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install.py"


def run_json(script, payload, cwd=None):
    result = subprocess.run(
        ["python3", str(script)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=cwd,
        check=True,
    )
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)


class TaskFolderRouterTests(unittest.TestCase):
    def install_workspace(self, require_label=False):
        tmp = tempfile.TemporaryDirectory()
        workspace = Path(tmp.name)
        command = [
            "python3",
            str(INSTALLER),
            "--target",
            str(workspace),
            "--routes",
            "project=projects,project-task=projects,project-continue=projects,client=clients",
            "--yes",
        ]
        if require_label:
            command.append("--require-label")
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return tmp, workspace, workspace / ".codex" / "hooks" / "task_folder_router.py"

    def start_session(self, hook, workspace, session_id):
        return run_json(
            hook,
            {
                "hook_event_name": "SessionStart",
                "source": "startup",
                "session_id": session_id,
                "cwd": str(workspace),
            },
            cwd=workspace,
        )

    def submit_prompt(self, hook, workspace, session_id, prompt):
        return run_json(
            hook,
            {
                "hook_event_name": "UserPromptSubmit",
                "session_id": session_id,
                "prompt": prompt,
            },
            cwd=workspace,
        )

    def test_valid_label_creates_folder(self):
        tmp, workspace, hook = self.install_workspace()
        with tmp:
            self.start_session(hook, workspace, "s1")
            result = self.submit_prompt(hook, workspace, "s1", "client: Acme Inc.\n\nBuild portal")
            self.assertIn("hookSpecificOutput", result)
            self.assertTrue((workspace / "clients" / "acme-inc").is_dir())

    def test_missing_label_uses_workspace_root_by_default(self):
        tmp, workspace, hook = self.install_workspace()
        with tmp:
            self.start_session(hook, workspace, "s2")
            result = self.submit_prompt(hook, workspace, "s2", "Build portal")
            self.assertIn("hookSpecificOutput", result)
            self.assertIn("workspace root", result["hookSpecificOutput"]["additionalContext"])
            self.assertFalse((workspace / "projects" / "build-portal").exists())

    def test_missing_label_blocks_in_strict_mode(self):
        tmp, workspace, hook = self.install_workspace(require_label=True)
        with tmp:
            self.start_session(hook, workspace, "s2-strict")
            result = self.submit_prompt(hook, workspace, "s2-strict", "Build portal")
            self.assertEqual(result["decision"], "block")
            self.assertIn("configured task-folder label", result["reason"])

    def test_unknown_label_blocks(self):
        tmp, workspace, hook = self.install_workspace()
        with tmp:
            self.start_session(hook, workspace, "s3")
            result = self.submit_prompt(hook, workspace, "s3", "secret: vault")
            self.assertEqual(result["decision"], "block")
            self.assertIn("not configured", result["reason"])

    def test_path_traversal_blocks(self):
        tmp, workspace, hook = self.install_workspace()
        with tmp:
            self.start_session(hook, workspace, "s4")
            result = self.submit_prompt(hook, workspace, "s4", "project: ../../secret")
            self.assertEqual(result["decision"], "block")
            self.assertIn("cannot contain paths", result["reason"])
            self.assertFalse((workspace.parent / "secret").exists())

    def test_processed_session_does_not_create_second_folder(self):
        tmp, workspace, hook = self.install_workspace()
        with tmp:
            self.start_session(hook, workspace, "s5")
            self.submit_prompt(hook, workspace, "s5", "project: first")
            result = self.submit_prompt(hook, workspace, "s5", "project: second")
            self.assertIsNone(result)
            self.assertTrue((workspace / "projects" / "first").is_dir())
            self.assertFalse((workspace / "projects" / "second").exists())

    def test_new_session_with_same_label_reuses_folder(self):
        tmp, workspace, hook = self.install_workspace()
        with tmp:
            self.start_session(hook, workspace, "s6-a")
            self.submit_prompt(hook, workspace, "s6-a", "project: shared")
            first = workspace / "projects" / "shared"
            self.assertTrue(first.is_dir())

            self.start_session(hook, workspace, "s6-b")
            self.submit_prompt(hook, workspace, "s6-b", "project: shared")
            self.assertTrue(first.is_dir())
            task_dirs = [
                path.name
                for path in (workspace / "projects").iterdir()
                if path.is_dir()
            ]
            self.assertEqual(task_dirs, ["shared"])

    def test_project_aliases_reuse_same_folder(self):
        tmp, workspace, hook = self.install_workspace()
        with tmp:
            self.start_session(hook, workspace, "s7-a")
            self.submit_prompt(hook, workspace, "s7-a", "project: crm")
            target = workspace / "projects" / "crm"
            self.assertTrue(target.is_dir())

            self.start_session(hook, workspace, "s7-b")
            self.submit_prompt(hook, workspace, "s7-b", "project-task: crm")
            self.assertTrue(target.is_dir())

            self.start_session(hook, workspace, "s7-c")
            self.submit_prompt(hook, workspace, "s7-c", "project-continue: crm")
            self.assertTrue(target.is_dir())

            task_dirs = [
                path.name
                for path in (workspace / "projects").iterdir()
                if path.is_dir()
            ]
            self.assertEqual(task_dirs, ["crm"])


if __name__ == "__main__":
    unittest.main()
