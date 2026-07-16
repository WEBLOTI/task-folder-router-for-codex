# Contributing

Thanks for helping improve Task Folder Router for Codex.

## Project Goals

- Keep the router generic and useful for many Codex workflows.
- Keep the hook local-only and safe.
- Keep setup simple for non-expert users.
- Avoid dependencies unless they clearly improve safety or portability.

## Before Opening A Pull Request

Run:

```bash
python3 -m unittest tests/test_router.py
python3 -m py_compile .codex/hooks/task_folder_router.py scripts/install.py tests/test_router.py
python3 -m json.tool .codex/task-folder-router.json >/dev/null
python3 -m json.tool .codex/hooks.json >/dev/null
```

GitHub Actions runs the same validation on pushes and pull requests.

## Security Expectations

Do not add behavior that:

- reads generated project contents;
- sends local data to external services;
- runs commands inside routed folders;
- stores secrets;
- accepts arbitrary labels or absolute paths from prompts;
- creates remote repositories, commits, pushes, or deploys.

## Documentation Style

Use simple, practical language. Prefer step-by-step examples over abstract explanations.
