#!/usr/bin/env python3
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install.py"
DOCTOR = ROOT / "scripts" / "doctor.py"


def run_doctor(target, check=False):
    return subprocess.run(
        ["python3", str(DOCTOR), "--target", str(target)],
        check=check,
        capture_output=True,
        text=True,
    )


class TaskFolderRouterDoctorTests(unittest.TestCase):
    def test_doctor_passes_for_installed_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            subprocess.run(
                ["python3", str(INSTALLER), "--target", str(workspace), "--yes"],
                check=True,
                capture_output=True,
                text=True,
            )
            result = run_doctor(workspace, check=True)
            self.assertIn("OK: router config exists at workspace root.", result.stdout)
            self.assertIn("clients/budget-calculator", result.stdout)

    def test_doctor_detects_nested_clone_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            nested = workspace / "task-folder-router-for-codex"
            subprocess.run(
                ["python3", str(INSTALLER), "--target", str(nested), "--yes"],
                check=True,
                capture_output=True,
                text=True,
            )
            result = run_doctor(workspace)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("router config is missing at workspace root", result.stdout)
            self.assertIn("router files exist only inside", result.stdout)

    def test_doctor_detects_nested_tools_clone_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            nested_config = workspace / "_tools" / "task-folder-router-for-codex" / ".codex" / "task-folder-router.json"
            nested_config.parent.mkdir(parents=True)
            nested_config.write_text('{"routes":{"client":"clients"},"require_route_prefix":false}\n', encoding="utf-8")

            result = run_doctor(workspace)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("router config is missing at workspace root", result.stdout)
            self.assertIn("router files exist only inside", result.stdout)

    def test_doctor_detects_missing_router(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_doctor(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("router config is missing at workspace root", result.stdout)


if __name__ == "__main__":
    unittest.main()
