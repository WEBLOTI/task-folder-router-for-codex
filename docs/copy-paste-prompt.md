# Copy-Paste Prompt For Codex

Use this when you want Codex to install Task Folder Router for you.

Open the Codex workspace where you want routed task folders, switch to Planning Mode, and paste this prompt.

```text
I want to install Task Folder Router for Codex in this workspace.

Repository:
https://github.com/WEBLOTI/task-folder-router-for-codex.git

GitHub CLI option:
gh repo clone WEBLOTI/task-folder-router-for-codex

Workspace root:
[USE THE CURRENT CODEX WORKSPACE ROOT]

Please do this in Planning Mode first:

1. Ask me which install flow I want:
   A. Recommended global tools flow:
      Clone the router once into ~/CodexTools/task-folder-router-for-codex and install it into this workspace.
   B. Workspace-local tools flow:
      Clone the router into this workspace under _tools/task-folder-router-for-codex and install it into the workspace root.

2. Ask me which labels I want to allow.
   Suggest this default:
   project=projects, project-task=projects, project-continue=projects, plugin=plugins, client=clients, site=sites, app=apps

3. Ask me whether labels should be optional or required.
   Recommend optional labels / mixed mode, so normal unlabeled tasks still work in the workspace root.

4. After I answer, give me the exact install plan and wait for me to approve implementation.

5. When implemented, verify that the workspace root contains:
   .codex/hooks.json
   .codex/task-folder-router.json

6. Run the router doctor command and explain the result:
   python3 scripts/doctor.py --target "[WORKSPACE ROOT]"

7. Explain how I should start routed tasks after installation.
   Include examples like:
   client: Acme Inc.
   project: CRM
   app: Admin Panel

Important:
- Do not install only inside the cloned task-folder-router-for-codex folder.
- The real workspace root must receive the .codex folder.
- If a route label is used, Codex should create and edit files inside the routed folder, not in a sibling folder based on the visible task title.
```

## What Codex Should Explain After Installing

After installation, Codex should explain the chosen flow and show the user examples like these:

```text
client: Acme Inc.

Build a customer portal prototype.
```

Routes to:

```text
clients/acme-inc/
```

```text
project: CRM

Build the dashboard shell.
```

Routes to:

```text
projects/crm/
```

To continue a project from a new task:

```text
project-continue: CRM

Continue the settings screen.
```

Routes to:

```text
projects/crm/
```
