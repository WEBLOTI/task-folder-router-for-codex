#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from pathlib import Path


DEFAULT_ROUTE_TEXT = (
    "project=projects, project-task=projects, project-continue=projects, "
    "plugin=plugins, client=clients, site=sites, app=apps"
)
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


def path_is_relative_to(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


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


def agents_snippet():
    return (
        "## Task Folder Router\n\n"
        "- To route a new Codex task into a subfolder, start the first message with one configured label, such as `client: Acme Inc.`.\n"
        "- When a configured label is used, create and edit files inside the routed folder, such as `clients/acme-inc/`.\n"
        "- Do not create a sibling folder from the visible Codex task title when a routed folder was provided.\n"
        "- The visible Codex task name does not control or rename the folder path.\n"
        "- If labels are optional in `.codex/task-folder-router.json`, unlabeled tasks work normally in the workspace root.\n"
        "- To continue the same subproject from a new Codex task, reuse the same label and name or use a configured continuation alias, such as `project-continue: my-app`.\n"
        "- Configured labels live in `.codex/task-folder-router.json`.\n"
        "- Do not store secrets, tokens, dumps, or private credentials in this workspace.\n"
    )


def upsert_agents_section(agents):
    snippet = agents_snippet()
    if not agents.exists():
        agents.write_text("# Codex Workspace\n\n" + snippet, encoding="utf-8")
        return

    content = agents.read_text(encoding="utf-8")
    heading = "## Task Folder Router"
    if heading not in content:
        agents.write_text(content.rstrip() + "\n\n" + snippet, encoding="utf-8")
        return

    start = content.index(heading)
    next_heading = re_search_next_heading(content, start + len(heading))
    replacement = snippet.rstrip()
    if next_heading is None:
        updated = content[:start].rstrip() + "\n\n" + replacement + "\n"
    else:
        updated = content[:start].rstrip() + "\n\n" + replacement + "\n\n" + content[next_heading:].lstrip()
    agents.write_text(updated, encoding="utf-8")


def re_search_next_heading(content, start):
    for index in range(start, len(content)):
        if content.startswith("\n## ", index):
            return index + 1
    return None


def example_routes(routes):
    examples = []
    preferred_labels = ["client", "project", "app"]
    ordered_labels = preferred_labels + [label for label in routes if label not in preferred_labels]
    for label in ordered_labels:
        if label not in routes:
            continue
        folder = routes[label]
        examples.append(f"{label}: Budget Calculator -> {folder}/budget-calculator/")
        if len(examples) == 3:
            break
    return examples


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
    upsert_agents_section(agents)

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
    source_root = repo_root()
    if path_is_relative_to(source_root, target_root) and source_root != target_root:
        print("Notice: this router clone is inside the target workspace.")
        print("That is allowed, but Codex must open the target workspace root, not only the cloned router folder.")
    print("Configured routes:")
    for label, folder in routes.items():
        print(f"  {label}: -> {folder}/")
    if require_route_prefix:
        print("Mode: required labels. New tasks without labels are blocked.")
    else:
        print("Mode: mixed. Unlabeled tasks work normally; labeled tasks use routed folders.")
    print("Important: open the target folder above in Codex, not the cloned template folder, unless they are the same on purpose.")
    print("The target folder should now contain .codex/hooks.json and .codex/task-folder-router.json.")
    print("Examples:")
    for example in example_routes(routes):
        print(f"  {example}")
    print("Trust hooks if prompted, then start a task with a configured label.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
