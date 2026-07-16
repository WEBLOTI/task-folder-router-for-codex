# Task Folder Router Workspace

This repository is a public template for adding safe task-folder routing to Codex workspaces.

## Repository Rules

- Keep this repository generic. Do not add workflow-specific references such as WordPress, clients, private projects, or local user paths.
- Do not store secrets, tokens, `.env` files, database dumps, credentials, or private project data.
- Treat generated task folders as local workspace content. They are ignored by default except for `.gitkeep` placeholders.
- Keep the hook local-only. It must not make network requests, run commands inside generated folders, or read project contents.

## Router Behavior

- Allowed labels are defined in `.codex/task-folder-router.json`.
- In mixed mode, a new Codex task may omit a label and work normally in the workspace root.
- To route a new Codex task into a subfolder, the first non-empty line must include one allowed label, such as `project: my-app`.
- The hook creates or reuses the configured folder, such as `projects/my-app/`, when a label is used.
- When a route label is used, create and edit files inside the routed folder. Do not create a sibling folder based on the visible Codex task title.
- The visible Codex task name never controls or renames the folder path.
- `project-task:` and `project-continue:` are aliases for `project:` by default and must reuse the same `projects/<slug>/` folder.
- To continue the same subproject from a different new Codex task, reuse the same label and name or use the matching continuation alias.
- Labels not present in the config must be rejected.
- Folder names must be slugified and must never allow path traversal.

## Maintenance

- Validate Python syntax after editing scripts or hooks.
- Validate JSON after editing config or hook definitions.
- Keep documentation simple, step-by-step, and suitable for people using Codex for the first time.
