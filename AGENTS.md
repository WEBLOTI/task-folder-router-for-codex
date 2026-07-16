# Task Folder Router Workspace

This repository is a public template for adding safe task-folder routing to Codex workspaces.

## Repository Rules

- Keep this repository generic. Do not add workflow-specific references such as WordPress, clients, private projects, or local user paths.
- Do not store secrets, tokens, `.env` files, database dumps, credentials, or private project data.
- Treat generated task folders as local workspace content. They are ignored by default except for `.gitkeep` placeholders.
- Keep the hook local-only. It must not make network requests, run commands inside generated folders, or read project contents.

## Router Behavior

- Allowed labels are defined in `.codex/task-folder-router.json`.
- A new Codex task must include one allowed label line, such as `project: my-app`.
- The hook creates or reuses the configured folder, such as `projects/my-app/`.
- Labels not present in the config must be rejected.
- Folder names must be slugified and must never allow path traversal.

## Maintenance

- Validate Python syntax after editing scripts or hooks.
- Validate JSON after editing config or hook definitions.
- Keep documentation simple, step-by-step, and suitable for people using Codex for the first time.
