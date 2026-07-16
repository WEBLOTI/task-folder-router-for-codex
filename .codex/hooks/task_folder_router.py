#!/usr/bin/env python3
import datetime as _datetime
import json
import re
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / ".codex" / "task-folder-router.json"
STATE_DIR = ROOT / ".codex" / "state" / "task-folder-router"
DEFAULT_ROUTES = {
    "project": "projects",
    "project-task": "projects",
    "project-continue": "projects",
    "plugin": "plugins",
    "client": "clients",
    "site": "sites",
    "app": "apps",
}
DEFAULT_REQUIRE_ROUTE_PREFIX = False


class RouterError(Exception):
    pass


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def now_iso():
    return _datetime.datetime.now(_datetime.timezone.utc).isoformat()


def read_event():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def safe_session_id(session_id):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", session_id or "unknown")


def marker_path(session_id):
    return STATE_DIR / f"{safe_session_id(session_id)}.json"


def has_path_signal(value):
    if not value:
        return True
    if any(ord(char) < 32 for char in value):
        return True
    forbidden = ("/", "\\", "~", ":", "\x00")
    if any(item in value for item in forbidden):
        return True
    if ".." in value:
        return True
    return False


def slugify(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug


def validate_label(label):
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", label):
        raise RouterError(
            f"Invalid route label `{label}`. Use lowercase letters, numbers, hyphen, or underscore."
        )


def validate_route_path(route_path):
    path = Path(route_path)
    if path.is_absolute():
        raise RouterError(f"Route path `{route_path}` must be relative.")
    parts = path.parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise RouterError(f"Route path `{route_path}` is not safe.")
    for part in parts:
        if not re.fullmatch(r"[A-Za-z0-9._-]+", part):
            raise RouterError(
                f"Route path `{route_path}` contains unsupported characters."
            )


def load_config():
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    else:
        config = {
            "routes": DEFAULT_ROUTES,
            "require_route_prefix": DEFAULT_REQUIRE_ROUTE_PREFIX,
        }

    routes = config.get("routes")
    if not isinstance(routes, dict) or not routes:
        raise RouterError("Config must define a non-empty `routes` object.")

    clean_routes = {}
    for label, route_path in routes.items():
        label = str(label).strip().lower()
        route_path = str(route_path).strip()
        validate_label(label)
        validate_route_path(route_path)
        clean_routes[label] = route_path

    return {
        "routes": clean_routes,
        "require_route_prefix": bool(
            config.get("require_route_prefix", DEFAULT_REQUIRE_ROUTE_PREFIX)
        ),
    }


def allowed_examples(routes):
    examples = []
    for label in sorted(routes):
        examples.append(f"`{label}: my-{label}`")
    return ", ".join(examples)


def first_non_empty_line(prompt):
    for line in (prompt or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def extract_route(prompt, routes):
    line = first_non_empty_line(prompt)
    if not line:
        return None

    label_pattern = "|".join(
        re.escape(label) for label in sorted(routes, key=len, reverse=True)
    )
    pattern = re.compile(
        rf"^(?P<label>{label_pattern})\s*:\s*(?P<name>.+?)\s*$",
        re.IGNORECASE,
    )
    match = pattern.match(line)
    if not match:
        return None

    label = match.group("label").strip().lower()
    name = match.group("name").strip().strip("\"'")
    name = re.sub(r"\s+#.*$", "", name).strip()
    return label, name


def detect_unknown_label(prompt, routes):
    line = first_non_empty_line(prompt)
    pattern = re.compile(r"^(?P<label>[A-Za-z][A-Za-z0-9_-]{0,31})\s*:\s*.+$")
    match = pattern.match(line)
    if not match:
        return None

    label = match.group("label").strip().lower()
    if label not in routes:
        return label
    return None


def safe_join(root, route_path, slug):
    route_root = (root / route_path).resolve()
    target = (route_root / slug).resolve()
    if root.resolve() not in target.parents:
        raise RouterError("Resolved target escaped the workspace root.")
    if route_root not in target.parents:
        raise RouterError("Resolved target escaped the configured route root.")
    return target


def handle_session_start(event, config):
    if event.get("source") != "startup":
        return

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    session_id = event.get("session_id") or "unknown"
    path = marker_path(session_id)
    path.write_text(
        json.dumps(
            {
                "status": "pending",
                "session_id": session_id,
                "created_at": now_iso(),
                "cwd": event.get("cwd"),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    "This workspace uses Task Folder Router. "
                    f"Configured labels include {allowed_examples(config['routes'])}. "
                    + (
                        "The first message of a new task must start with one configured label. "
                        if config["require_route_prefix"]
                        else "A task may start without a label to use the workspace normally, "
                        "or start with a configured label to route work into a subfolder. "
                    )
                    + "When a label is used, Codex should work inside the created or reused task folder."
                ),
            }
        }
    )


def handle_user_prompt_submit(event, config):
    session_id = event.get("session_id") or "unknown"
    path = marker_path(session_id)
    if not path.exists():
        return

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        state = {"status": "pending", "session_id": session_id}

    if state.get("status") in ("processed", "bypassed"):
        return

    prompt = event.get("prompt", "")
    route = extract_route(prompt, config["routes"])
    if not route:
        unknown_label = detect_unknown_label(prompt, config["routes"])
        if unknown_label:
            emit(
                {
                    "decision": "block",
                    "reason": (
                        f"`{unknown_label}:` is not configured for this workspace. "
                        f"Use one of: {allowed_examples(config['routes'])}, "
                        "or remove the first-line label to work normally in the workspace root."
                    ),
                }
            )
            return

        if config["require_route_prefix"]:
            emit(
                {
                    "decision": "block",
                    "reason": (
                        "This workspace requires a configured task-folder label on the first "
                        f"new-task message. Use one of: {allowed_examples(config['routes'])}."
                    ),
                }
            )
            return

        state.update(
            {
                "status": "bypassed",
                "mode": "workspace-root",
                "processed_at": now_iso(),
            }
        )
        path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        "No configured task-folder label was provided for this task. "
                        "Use the workspace root normally unless the user explicitly asks "
                        "for a different location."
                    ),
                }
            }
        )
        return

    label, raw_name = route
    if has_path_signal(raw_name):
        emit(
            {
                "decision": "block",
                "reason": (
                    "The task folder name cannot contain paths, `..`, `~`, slashes, "
                    "colons, or control characters. Use a plain name like "
                    f"`{label}: my-work-item`."
                ),
            }
        )
        return

    slug = slugify(raw_name)
    if not slug:
        emit(
            {
                "decision": "block",
                "reason": f"Could not convert `{label}: {raw_name}` into a safe folder name.",
            }
        )
        return

    route_path = config["routes"][label]
    try:
        target = safe_join(ROOT, route_path, slug)
        target.mkdir(parents=True, exist_ok=True)
    except (OSError, RouterError) as exc:
        emit({"decision": "block", "reason": f"Could not prepare task folder: {exc}"})
        return

    state.update(
        {
            "status": "processed",
            "label": label,
            "raw_name": raw_name,
            "slug": slug,
            "route_path": route_path,
            "task_dir": str(target),
            "processed_at": now_iso(),
        }
    )
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"Task folder for this Codex task: `{target}`. "
                    "Create and edit files for this task inside that folder unless "
                    "the user explicitly asks for a different location."
                ),
            }
        }
    )


def main():
    event = read_event()
    event_name = event.get("hook_event_name") or event.get("hookEventName")

    try:
        config = load_config()
    except (json.JSONDecodeError, RouterError) as exc:
        emit({"decision": "block", "reason": f"Task Folder Router config error: {exc}"})
        return

    if event_name == "SessionStart":
        handle_session_start(event, config)
    elif event_name == "UserPromptSubmit":
        handle_user_prompt_submit(event, config)


if __name__ == "__main__":
    main()
