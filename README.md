# Task Folder Router for Codex

Task Folder Router for Codex is a small public template for organizing Codex workspaces into independent task folders.

It lets you define labels such as `project:`, `plugin:`, `client:`, `site:`, or `app:`. When a new Codex task starts with one of those labels, the hook creates or reuses the matching folder and tells Codex to work there.

By default, the router uses mixed mode: unlabeled tasks work normally in the workspace root, and labeled tasks are routed into subfolders.

```text
client: acme inc

Build a customer portal prototype.
```

creates or reuses:

```text
clients/acme-inc/
```

## What Problem It Solves

Codex workspaces can get messy when many unrelated tasks write files into the same root folder. This template keeps each task or subproject isolated in a predictable folder while still using one main workspace.

Useful examples:

- `project: crm` -> `projects/crm/`
- `project-task: crm` -> `projects/crm/`
- `project-continue: crm` -> `projects/crm/`
- `plugin: checkout tools` -> `plugins/checkout-tools/`
- `client: Acme Inc.` -> `clients/acme-inc/`
- `site: landing page` -> `sites/landing-page/`
- `app: admin panel` -> `apps/admin-panel/`

## What It Does

- Reads the first matching configured label from a new Codex task.
- Accepts only labels you predefine.
- Converts the name into a safe slug.
- Creates or reuses the matching folder.
- Stores local session state under `.codex/state/`.
- Adds context telling Codex which folder to use.

## What It Does Not Do

- It does not read project contents.
- It does not send data anywhere.
- It does not create GitHub repositories.
- It does not commit, push, deploy, or install packages.
- It does not accept arbitrary labels or user-provided paths.
- It does not rename folders when you rename a Codex task.

## Two Ways To Work

Use Codex normally without a label:

```text
Create a quick notes file for this workspace.
```

This stays in the workspace root.

Use a configured label when you want an independent task folder:

```text
project: my-dashboard

Build the first screen.
```

This creates or reuses:

```text
projects/my-dashboard/
```

`project-task:` and `project-continue:` are aliases for `project:`. They express intent but reuse the same folder:

```text
project-task: my-dashboard
project-continue: my-dashboard
```

Both route to:

```text
projects/my-dashboard/
```

## Quick Start

Want Codex to install it for you? Copy the prompt in [Copy-Paste Prompt For Codex](docs/copy-paste-prompt.md), paste it into Planning Mode, and let Codex ask which install flow you want.

For the simplest setup:

1. Open or create the folder where you want Codex to work.
2. Open that folder in Codex.
3. Paste the [Copy-Paste Prompt For Codex](docs/copy-paste-prompt.md) in Planning Mode.
4. Let Codex ask which install flow and labels you want.

If you prefer terminal commands, clone this template once into a tools folder, outside your Codex workspaces:

```bash
mkdir -p ~/CodexTools
cd ~/CodexTools
git clone https://github.com/WEBLOTI/task-folder-router-for-codex.git
cd task-folder-router-for-codex
```

If you use GitHub CLI, this is also supported:

```bash
mkdir -p ~/CodexTools
cd ~/CodexTools
gh repo clone WEBLOTI/task-folder-router-for-codex
cd task-folder-router-for-codex
```

Install it into the real Codex workspace where tasks should run:

```bash
python3 scripts/install.py --target "/path/to/my-codex-workspace"
```

You can also ask Codex to run that installer for you once the repository is cloned.

Important: open the target workspace in Codex after installation. If you cloned this template inside a project but did not install it into the project root, Codex will only see the router inside the cloned template folder. The workspace root must contain:

```text
.codex/hooks.json
.codex/task-folder-router.json
```

You can check a workspace install without changing files:

```bash
python3 scripts/doctor.py --target "/path/to/my-codex-workspace"
```

The installer asks which labels you want to allow, for example:

```text
project=projects, project-task=projects, project-continue=projects, plugin=plugins, client=clients
```

Then open that workspace in Codex, trust the hooks if Codex asks, and start a new task:

```text
project: my-dashboard

Build the first screen.
```

Codex will work inside:

```text
projects/my-dashboard/
```

To continue the same subproject from a different new Codex task, use `project-continue:` with the same name:

```text
project-continue: my-dashboard

Continue the settings screen.
```

The router reuses the same folder instead of creating a duplicate.

## Install Once, Reuse Many Times

You do not need to clone this repository for every Codex workspace. Clone it once, then run the installer for each workspace where you want the router:

```bash
python3 scripts/install.py --target "/path/to/workspace-a"
python3 scripts/install.py --target "/path/to/workspace-b"
python3 scripts/install.py --target "/path/to/workspace-c"
```

If you prefer to keep the cloned router inside a workspace, put it in a tools folder and still install into the workspace root:

```bash
cd "/path/to/my-codex-workspace"
mkdir -p _tools
cd _tools
gh repo clone WEBLOTI/task-folder-router-for-codex
cd task-folder-router-for-codex
python3 scripts/install.py --target "../.."
```

After that, open `/path/to/my-codex-workspace` in Codex, not `_tools/task-folder-router-for-codex`.

## Documentation

- [Installation](docs/installation.md)
- [Copy-Paste Prompt For Codex](docs/copy-paste-prompt.md)
- [Customization](docs/customization.md)
- [Security](docs/security.md)
- [Publishing](docs/publishing.md)
- [Troubleshooting](docs/troubleshooting.md)

## Requirements

- Codex with project hooks support.
- Python 3.8 or newer.
- A trusted Codex workspace where hooks are allowed.

## Run Tests

```bash
python3 -m unittest tests/test_router.py
```

The public repository also includes a GitHub Actions workflow that runs JSON validation, Python validation, and tests on pushes and pull requests.

## License

MIT
