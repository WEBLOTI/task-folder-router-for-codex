# Installation

Task Folder Router helps Codex keep each task or subproject inside its own folder.

By default, it uses mixed mode:

- tasks without labels work normally in the main workspace folder;
- tasks with labels are routed into organized subfolders.

## Quick Installation

Use this path if you want the simplest setup.

### 1. Create Or Open Your Codex Workspace

In Codex, create or open the folder where you want to work.

You can use:

- a new empty folder;
- an existing project folder;
- a folder you already use to keep client, app, site, or project work.

Examples of normal folder names:

```text
Clients App
My Projects
Websites
Apps
```

This folder is your workspace root. It is the main folder where Codex should install the router.

### 2. Paste The Install Prompt In Planning Mode

Open the workspace in Codex, switch to Planning Mode, and paste the prompt from:

[Copy-Paste Prompt For Codex](copy-paste-prompt.md)

That prompt tells Codex to ask which flow you want:

- keep the router in a general tools folder;
- keep the router inside this workspace under `_tools/`.

For most people, choose the first option Codex recommends.

### 3. Choose Your Labels

Codex will ask which labels you want to use.

The recommended labels are:

```text
project, project-task, project-continue, plugin, client, site, app
```

These labels create folders like:

```text
client: Acme Inc.     -> clients/acme-inc/
project: CRM          -> projects/crm/
app: Admin Panel      -> apps/admin-panel/
```

### 4. Keep Labels Optional

Codex will ask whether every task should require a label.

Recommended answer: keep labels optional.

That means:

- if you start a task without a label, Codex works normally in the workspace root;
- if you start with a label, Codex works inside the routed folder.

### 5. Approve The Install Plan

Codex should show you the install plan before changing files.

Approve it only if the target workspace is the folder you actually want to use.

After installation, the workspace root should contain:

```text
.codex/hooks.json
.codex/task-folder-router.json
```

### 6. Start Using Routed Tasks

Start a new Codex task with a label when you want an organized subfolder:

```text
client: Acme Inc.

Build a customer portal prototype.
```

Codex will work inside:

```text
clients/acme-inc/
```

To continue the same project from another new task:

```text
project-continue: CRM

Continue the settings screen.
```

Codex will reuse:

```text
projects/crm/
```

## Technical Installation

Use this path if you prefer terminal commands.

### Option A: Keep The Router In A Tools Folder

Clone the router once:

```bash
mkdir -p ~/CodexTools
cd ~/CodexTools
git clone https://github.com/WEBLOTI/task-folder-router-for-codex.git
cd task-folder-router-for-codex
```

Or with GitHub CLI:

```bash
mkdir -p ~/CodexTools
cd ~/CodexTools
gh repo clone WEBLOTI/task-folder-router-for-codex
cd task-folder-router-for-codex
```

Then install it into your Codex workspace:

```bash
python3 scripts/install.py --target "/path/to/your/workspace"
```

### Option B: Keep The Router Inside A Workspace

From your workspace folder:

```bash
mkdir -p _tools
cd _tools
gh repo clone WEBLOTI/task-folder-router-for-codex
cd task-folder-router-for-codex
python3 scripts/install.py --target "../.."
```

After that, open the workspace root in Codex, not `_tools/task-folder-router-for-codex`.

## Verify The Install

From the router folder, run:

```bash
python3 scripts/doctor.py --target "/path/to/your/workspace"
```

The doctor should say that the router config, hooks file, and hook script exist at the workspace root.

## Common Mistake

Do not only clone the router and then start working inside the cloned `task-folder-router-for-codex` folder.

The real workspace root must receive the `.codex` folder. If `.codex` exists only inside the cloned router folder, Codex will not route tasks correctly from the parent workspace.
