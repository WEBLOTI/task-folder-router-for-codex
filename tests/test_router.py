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
    def install_workspace(self):
        tmp = tempfile.TemporaryDirectory()
        workspace = Path(tmp.name)
        subprocess.run(
            [
                "python3",
                str(INSTALLER),
                "--target",
                str(workspace),
                "--routes",
                "project=projects,client=clients",
                "--yes",
            ],
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

    def test_missing_label_blocks(self):
        tmp, workspace, hook = self.install_workspace()
        with tmp:
            self.start_session(hook, workspace, "s2")
            result = self.submit_prompt(hook, workspace, "s2", "Build portal")
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


if __name__ == "__main__":
    unittest.main()
