# Task Folder Router for Codex

Task Folder Router for Codex is a small public template for organizing Codex workspaces into independent task folders.

It lets you define labels such as `project:`, `plugin:`, `client:`, `site:`, or `app:`. When a new Codex task starts with one of those labels, the hook creates or reuses the matching folder and tells Codex to work there.

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

## Quick Start

Clone this template once into a tools folder:

```bash
git clone https://github.com/<owner>/task-folder-router-for-codex.git
cd task-folder-router-for-codex
```

Install it into any Codex workspace:

```bash
python3 scripts/install.py --target "/path/to/my-codex-workspace"
```

The installer asks which labels you want to allow, for example:

```text
project=projects, plugin=plugins, client=clients
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

## Install Once, Reuse Many Times

You do not need to clone this repository for every Codex workspace. Clone it once, then run the installer for each workspace where you want the router:

```bash
python3 scripts/install.py --target "/path/to/workspace-a"
python3 scripts/install.py --target "/path/to/workspace-b"
python3 scripts/install.py --target "/path/to/workspace-c"
```

## Documentation

- [Installation](docs/installation.md)
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
