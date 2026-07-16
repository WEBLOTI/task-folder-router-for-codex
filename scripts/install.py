#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from pathlib import Path


DEFAULT_ROUTE_TEXT = "project=projects, plugin=plugins, client=clients, site=sites, app=apps"
DEFAULT_REQUIRE_ROUTE_PREFIX = False


def parse_routes(value):
    routes = {}
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"Route `{item}` must use label=folder format.")
        label, folder = item.split("=", 1)
        label = label.strip().lower()
        folder = folder.strip()
        if not label or not folder:
            raise ValueError(f"Route `{item}` must include both label and folder.")
        routes[label] = folder
    if not routes:
        raise ValueError("At least one route is required.")
    return routes


def prompt_routes(default_text):
    print("Which labels do you want to allow?")
    print("Use label=folder pairs separated by commas.")
    print(f"Default: {default_text}")
    answer = input("Routes: ").strip()
    return answer or default_text


def prompt_require_route_prefix(default=False):
    default_text = "y" if default else "n"
    print("Should every new Codex task require a label?")
    print("Choose no for mixed mode: unlabeled tasks work normally, labeled tasks use routed folders.")
    answer = input(f"Require labels? [y/N]: ").strip().lower()
    if not answer:
        answer = default_text
    return answer in ("y", "yes")


def repo_root():
    return Path(__file__).resolve().parents[1]


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_hooks_json(target_root):
    hook_path = target_root / ".codex" / "hooks" / "task_folder_router.py"
    command = f'python3 "{hook_path}"'
    return {
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "startup",
                    "hooks": [
                        {
                            "type": "command",
                            "command": command,
                            "timeout": 30,
                            "statusMessage": "Preparing task folder router",
                        }
                    ],
                }
            ],
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": command,
                            "timeout": 30,
                            "statusMessage": "Checking task folder route",
                        }
                    ]
                }
            ],
        }
    }


def update_gitignore(target_root, routes):
    gitignore = target_root / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    additions = [
        "",
        "# Task Folder Router generated work folders",
        ".codex/state/",
    ]
    for folder in sorted(set(routes.values())):
        additions.append(f"{folder}/*")
        additions.append(f"!{folder}/.gitkeep")

    missing = [line for line in additions if line and line not in existing.splitlines()]
    if not missing:
        return

    prefix = "" if existing.endswith("\n") or not existing else "\n"
    gitignore.write_text(existing + prefix + "\n".join(additions).strip() + "\n", encoding="utf-8")


def install(target, routes, require_route_prefix=False):
    source_root = repo_root()
    target_root = Path(target).expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    codex_dir = target_root / ".codex"
    hooks_dir = codex_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source_root / ".codex" / "hooks" / "task_folder_router.py", hooks_dir / "task_folder_router.py")
    write_json(
        codex_dir / "task-folder-router.json",
        {"routes": routes, "require_route_prefix": bool(require_route_prefix)},
    )
    write_json(codex_dir / "hooks.json", build_hooks_json(target_root))

    for folder in sorted(set(routes.values())):
        folder_path = target_root / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        gitkeep = folder_path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")

    update_gitignore(target_root, routes)

    agents = target_root / "AGENTS.md"
    snippet = (
        "\n## Task Folder Router\n\n"
        "- To route a new Codex task into a subfolder, start the first message with one configured label, such as `project: my-app`.\n"
        "- If labels are optional in `.codex/task-folder-router.json`, unlabeled tasks work normally in the workspace root.\n"
        "- To continue the same subproject from a new Codex task, reuse the same label and name, such as `project: my-app`.\n"
        "- Work inside the folder created or reused by the router when a route label is used.\n"
        "- Configured labels live in `.codex/task-folder-router.json`.\n"
        "- Do not store secrets, tokens, dumps, or private credentials in this workspace.\n"
    )
    if agents.exists():
        content = agents.read_text(encoding="utf-8")
        if "## Task Folder Router" not in content:
            agents.write_text(content.rstrip() + "\n" + snippet, encoding="utf-8")
    else:
        agents.write_text("# Codex Workspace\n" + snippet, encoding="utf-8")

    return target_root


def main():
    parser = argparse.ArgumentParser(description="Install Task Folder Router into a Codex workspace.")
    parser.add_argument("--target", required=True, help="Codex workspace folder to install into.")
    parser.add_argument("--routes", help="Comma-separated label=folder pairs.")
    parser.add_argument("--yes", action="store_true", help="Use defaults without prompting when --routes is omitted.")
    parser.add_argument(
        "--require-label",
        action="store_true",
        help="Require every new task to start with a configured label.",
    )
    parser.add_argument(
        "--optional-label",
        action="store_true",
        help="Allow unlabeled tasks to work normally in the workspace root.",
    )
    args = parser.parse_args()

    route_text = args.routes
    if not route_text:
        route_text = DEFAULT_ROUTE_TEXT if args.yes else prompt_routes(DEFAULT_ROUTE_TEXT)

    if args.require_label and args.optional_label:
        print("Install failed: choose either --require-label or --optional-label, not both.", file=sys.stderr)
        return 1

    if args.require_label:
        require_route_prefix = True
    elif args.optional_label or args.yes:
        require_route_prefix = DEFAULT_REQUIRE_ROUTE_PREFIX
    else:
        require_route_prefix = prompt_require_route_prefix(DEFAULT_REQUIRE_ROUTE_PREFIX)

    try:
        routes = parse_routes(route_text)
        target_root = install(args.target, routes, require_route_prefix)
    except Exception as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1

    print(f"Task Folder Router installed in: {target_root}")
    print("Configured routes:")
    for label, folder in routes.items():
        print(f"  {label}: -> {folder}/")
    if require_route_prefix:
        print("Mode: required labels. New tasks without labels are blocked.")
    else:
        print("Mode: mixed. Unlabeled tasks work normally; labeled tasks use routed folders.")
    print("Open this folder in Codex, trust hooks if prompted, and start a task with a configured label.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
