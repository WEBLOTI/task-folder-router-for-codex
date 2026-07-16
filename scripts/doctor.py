#!/usr/bin/env python3
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


DEFAULT_LABEL = "client"
DEFAULT_NAME = "Budget Calculator"


def slugify(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def read_config(target):
    config_path = target / ".codex" / "task-folder-router.json"
    if not config_path.exists():
        return None
    return json.loads(config_path.read_text(encoding="utf-8"))


def nested_router_configs(target):
    configs = []
    root_config = target / ".codex" / "task-folder-router.json"
    for path in target.glob("**/.codex/task-folder-router.json"):
        if path == root_config:
            continue
        if "task-folder-router-for-codex" in path.parts:
            configs.append(path)
    return sorted(configs)


def diagnose(target, label, name):
    target = Path(target).expanduser().resolve()
    config = read_config(target)
    nested = nested_router_configs(target)
    lines = [f"Task Folder Router doctor for: {target}"]
    exit_code = 0

    if config:
        lines.append("OK: router config exists at workspace root.")
    else:
        lines.append("ERROR: router config is missing at workspace root.")
        exit_code = 1

    hooks_path = target / ".codex" / "hooks.json"
    hook_script = target / ".codex" / "hooks" / "task_folder_router.py"
    if hooks_path.exists():
        lines.append("OK: .codex/hooks.json exists at workspace root.")
    else:
        lines.append("ERROR: .codex/hooks.json is missing at workspace root.")
        exit_code = 1

    if hook_script.exists():
        lines.append("OK: router hook script exists at workspace root.")
    else:
        lines.append("ERROR: router hook script is missing at workspace root.")
        exit_code = 1

    if nested and not config:
        lines.append("Detected likely mistake: router files exist only inside a cloned task-folder-router-for-codex folder.")
        lines.append("Run the installer with --target pointing to the workspace root.")
    elif nested:
        lines.append("Notice: a cloned task-folder-router-for-codex folder also exists inside this workspace.")

    if config:
        routes = config.get("routes", {})
        route_root = routes.get(label)
        if route_root:
            expected = target / route_root / slugify(name)
            lines.append(f"Expected route for `{label}: {name}`:")
            lines.append(str(expected))
        else:
            lines.append(f"ERROR: label `{label}` is not configured.")
            exit_code = 1

    return exit_code, "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Diagnose a Task Folder Router workspace install.")
    parser.add_argument("--target", required=True, help="Codex workspace folder to inspect.")
    parser.add_argument("--label", default=DEFAULT_LABEL, help="Configured label to preview.")
    parser.add_argument("--name", default=DEFAULT_NAME, help="Task name to preview.")
    args = parser.parse_args()

    try:
        exit_code, output = diagnose(args.target, args.label, args.name)
    except Exception as exc:
        print(f"Doctor failed: {exc}", file=sys.stderr)
        return 2

    print(output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
