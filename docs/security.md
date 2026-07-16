# Security

Task Folder Router is designed to be local, minimal, and predictable.

## Local Only

The hook does not make network requests. It does not send prompts, file names, or project data to any external service.

## Minimal File Access

The hook only needs to:

- read `.codex/task-folder-router.json`;
- read the hook event from standard input;
- create or reuse a configured folder;
- write local session state under `.codex/state/task-folder-router/`.

It does not read the contents of generated task folders.

## Predefined Labels Only

The router accepts only labels configured in `.codex/task-folder-router.json`.

This prevents accidental folder creation from arbitrary prompt text.

## Path Safety

The hook rejects task folder names containing:

- `../`
- `/`
- `\`
- `~`
- `:`
- control characters

It also resolves the final path and verifies it stays inside the workspace and inside the configured route root.

## Git Safety

Generated work folders are ignored by default in this template:

```text
projects/*
plugins/*
clients/*
sites/*
apps/*
```

Only `.gitkeep` placeholders are tracked. This helps prevent accidentally publishing project code, private files, or generated work.

## What The Router Will Not Do

- It will not create remote repositories.
- It will not run commands inside generated folders.
- It will not install dependencies.
- It will not deploy anything.
- It will not commit or push code.
- It will not store secrets.

## User Responsibility

Review hooks before trusting them in Codex. Do not put credentials, `.env` files, database dumps, private customer data, or production secrets in a public template repository.
