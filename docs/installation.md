# Installation

Install Task Folder Router once, then reuse it across many Codex workspaces.

By default, the installer uses mixed mode:

- tasks without labels work normally in the workspace root;
- tasks with configured labels are routed into subfolders.

## 1. Create Or Choose A Codex Workspace

Pick the folder where you want Codex to work. It can be a new empty folder or an existing project.

Example:

```bash
mkdir -p ~/CodexWorkspaces/my-workspace
```

## 2. Clone This Template Once

Clone this repository into a tools folder. You do not need to clone it again for every workspace.

```bash
git clone https://github.com/<owner>/task-folder-router-for-codex.git
cd task-folder-router-for-codex
```

## 3. Run The Installer

Point the installer to the Codex workspace where you want the router.

```bash
python3 scripts/install.py --target "~/CodexWorkspaces/my-workspace"
```

The installer asks which labels you want to allow:

```text
Which labels do you want to allow?
Default: project=projects, plugin=plugins, client=clients, site=sites, app=apps
Routes:
```

Press Enter to accept the default or enter your own:

```text
project=projects, client=clients, app=apps
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

Open the target workspace in Codex, not necessarily this template repository.

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

Open a new Codex task and reuse the same label and name:

```text
project: my-dashboard

Continue the dashboard navigation.
```

The router reuses:

```text
projects/my-dashboard/
```

Renaming the visible Codex task does not rename this folder.

## 7. Reuse In Other Workspaces

Run the installer again for another workspace:

```bash
python3 scripts/install.py --target "~/CodexWorkspaces/another-workspace"
```

You still clone the template only once.
