# Installation

Install Task Folder Router once, then reuse it across many Codex workspaces.

By default, the installer uses mixed mode:

- tasks without labels work normally in the workspace root;
- tasks with configured labels are routed into subfolders.

If you want Codex to guide the install, use [Copy-Paste Prompt For Codex](copy-paste-prompt.md). Paste that prompt into Planning Mode from the workspace where you want routed folders.

## 1. Create Or Choose A Codex Workspace

Pick the folder where you want Codex to work. It can be a new empty folder or an existing project.

Example:

```bash
mkdir -p ~/CodexWorkspaces/my-workspace
```

## 2. Clone This Template Once

Recommended: clone this repository into a tools folder outside your Codex workspaces. You do not need to clone it again for every workspace.

```bash
mkdir -p ~/CodexTools
cd ~/CodexTools
git clone https://github.com/WEBLOTI/task-folder-router-for-codex.git
cd task-folder-router-for-codex
```

If you use GitHub CLI:

```bash
mkdir -p ~/CodexTools
cd ~/CodexTools
gh repo clone WEBLOTI/task-folder-router-for-codex
cd task-folder-router-for-codex
```

Recommended shape:

```text
CodexTools/
  task-folder-router-for-codex/

CodexWorkspaces/
  my-workspace/
```

The cloned template is the installer source. Your Codex workspace is the target where your tasks will run.

Alternative shape when you want the router clone inside a workspace:

```text
my-workspace/
  _tools/
    task-folder-router-for-codex/
```

That is supported, but you still must install into `my-workspace/`, not into `_tools/task-folder-router-for-codex/`.

## 3. Run The Installer

Point the installer to the Codex workspace where you want the router.

```bash
python3 scripts/install.py --target "~/CodexWorkspaces/my-workspace"
```

If the router clone is inside the workspace under `_tools/task-folder-router-for-codex`, run:

```bash
python3 scripts/install.py --target "../.."
```

The installer asks which labels you want to allow:

```text
Which labels do you want to allow?
Default: project=projects, project-task=projects, project-continue=projects, plugin=plugins, client=clients, site=sites, app=apps
Routes:
```

Press Enter to accept the default or enter your own:

```text
project=projects, project-task=projects, project-continue=projects, client=clients, app=apps
```

The installer also asks whether every new task should require a label. Choose `no` for the recommended mixed mode.

For a non-interactive install using the defaults:

```bash
python3 scripts/install.py --target "~/CodexWorkspaces/my-workspace" --yes
```

For strict mode, where unlabeled tasks are blocked:

```bash
python3 scripts/install.py --target "~/CodexWorkspaces/my-workspace" --require-label
```

## 4. Open The Workspace In Codex

Open the target workspace in Codex, not the cloned template repository unless you intentionally installed the router into that same folder.

After installation, the target workspace should contain:

```text
.codex/hooks.json
.codex/task-folder-router.json
```

If those files only exist inside `task-folder-router-for-codex/.codex/`, the router was cloned but not installed into the workspace root.

To verify before opening Codex:

```bash
python3 scripts/doctor.py --target "~/CodexWorkspaces/my-workspace"
```

If Codex asks whether to trust hooks, review and trust them only if you are comfortable with the local hook behavior.

## 5. Start A New Task

Use one configured label at the beginning of your first message when you want a routed folder:

```text
project: my-dashboard

Build a simple dashboard.
```

The router creates or reuses:

```text
projects/my-dashboard/
```

Or start without a label when you want to use the workspace normally:

```text
Create a general README for this workspace.
```

In mixed mode, this does not create a routed subfolder.

## 6. Continue The Same Subproject From A New Task

Open a new Codex task and use the continuation alias with the same name:

```text
project-continue: my-dashboard

Continue the dashboard navigation.
```

The router reuses:

```text
projects/my-dashboard/
```

Renaming the visible Codex task does not rename this folder.

`project-task:` is also available when you want to open a new task that belongs to the same project folder:

```text
project-task: my-dashboard

Add the user menu.
```

## 7. Reuse In Other Workspaces

Run the installer again for another workspace:

```bash
python3 scripts/install.py --target "~/CodexWorkspaces/another-workspace"
```

You still clone the template only once.
