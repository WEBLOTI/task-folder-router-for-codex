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

This usually means strict mode is enabled:

```json
"require_route_prefix": true
```

Set it to `false` if you want mixed mode, where unlabeled tasks work normally in the workspace root.

## I Started Without A Label And No Folder Was Created

That is expected in mixed mode. Without a label, the router lets the task work normally in the workspace root.

Start with a configured label if you want a subfolder:

```text
project: my-app
```

## My Label Is Rejected

The label is probably not configured.

Example: if the config only contains `project`, then this is rejected:

```text
client: acme
```

Add `client` to `.codex/task-folder-router.json` or use an existing label.

If you did not mean to route the task, remove the first-line label and write the request normally.

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

You can also run:

```bash
python3 scripts/doctor.py --target "/path/to/codex-workspace"
```

## My Folder Was Created Above The Label Folder

This usually means the router was installed inside the cloned template folder instead of the real Codex workspace root.

Example of the problem:

```text
my-workspace/
  task-folder-router-for-codex/
    .codex/
    clients/budget-calculator/
  job-search-prototype/
```

In that case, install the router into `my-workspace/` itself:

```bash
python3 /path/to/task-folder-router-for-codex/scripts/install.py --target "/path/to/my-workspace"
```

Then open `/path/to/my-workspace` in Codex. The workspace root should contain:

```text
my-workspace/
  .codex/hooks.json
  .codex/task-folder-router.json
  clients/
```

After that, a task starting with:

```text
client: Jobs App
```

will route to:

```text
clients/jobs-app/
```

Use the doctor command to confirm:

```bash
python3 /path/to/task-folder-router-for-codex/scripts/doctor.py --target "/path/to/my-workspace"
```

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

## I Want To Continue The Same Subproject In A New Task

Use the continuation alias with the same name:

```text
project-continue: crm

Continue the reports screen.
```

This reuses:

```text
projects/crm/
```

The visible Codex task name does not control the folder name.

## Will `project-task:` Or `project-continue:` Create Another Project?

No, not with the default configuration. These labels are aliases that point to the same folder root as `project:`.

```text
project: crm          -> projects/crm/
project-task: crm     -> projects/crm/
project-continue: crm -> projects/crm/
```

They only create a different folder if you edit `.codex/task-folder-router.json` and point them to another root.
