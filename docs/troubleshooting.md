# Troubleshooting

## Codex Says A Label Is Required

Start the first message of a new task with one configured label:

```text
project: my-app
```

Check allowed labels in:

```text
.codex/task-folder-router.json
```

## My Label Is Rejected

The label is probably not configured.

Example: if the config only contains `project`, then this is rejected:

```text
client: acme
```

Add `client` to `.codex/task-folder-router.json` or use an existing label.

## The Folder Was Not Created

Check:

- the workspace is trusted in Codex;
- hooks are enabled/trusted;
- Python 3 is installed;
- `.codex/hooks.json` exists in the workspace;
- `.codex/hooks/task_folder_router.py` exists in the workspace.

## Python Is Not Found

Install Python 3 or edit `.codex/hooks.json` to use the full path to Python on your system.

Example:

```json
"command": "/usr/bin/python3 \"/path/to/workspace/.codex/hooks/task_folder_router.py\""
```

## I Cloned The Template But Nothing Happens

Cloning the template is not enough. Run the installer for the workspace where you want the router:

```bash
python3 scripts/install.py --target "/path/to/codex-workspace"
```

Then open that target workspace in Codex.

## I Want To Use It In Multiple Workspaces

Keep one clone of the template and run the installer for each workspace:

```bash
python3 scripts/install.py --target "/path/to/workspace-a"
python3 scripts/install.py --target "/path/to/workspace-b"
```

## I Want To Verify The Router

From this template repository, run:

```bash
python3 -m unittest tests/test_router.py
```

## Continue Task Created Another Folder

That should not happen if session state is preserved. Check whether `.codex/state/task-folder-router/` exists and whether Codex started a truly new task instead of continuing an existing one.
