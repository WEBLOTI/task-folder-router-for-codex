# Publishing The Template

Use this guide when publishing Task Folder Router for Codex to GitHub.

## 1. Create The GitHub Repository

Create an empty public repository named:

```text
task-folder-router-for-codex
```

Recommended settings:

- Visibility: public
- Initialize with README: no
- Add `.gitignore`: no
- Add license: no

This repository already includes README, `.gitignore`, and MIT license files.

## 2. Push The Local Repository

From the local template folder:

```bash
cd "/Users/booming/Documents/task-folder-router-for-codex"
git remote add origin https://github.com/<owner>/task-folder-router-for-codex.git
git push -u origin main
```

If `origin` already exists:

```bash
git remote set-url origin https://github.com/<owner>/task-folder-router-for-codex.git
git push -u origin main
```

Or use the included publishing helper:

```bash
scripts/publish.sh https://github.com/<owner>/task-folder-router-for-codex.git
```

The helper runs tests and validation before pushing. It does not create the GitHub repository and does not store credentials.

## 3. Mark As Template

In GitHub:

1. Open the repository.
2. Go to **Settings**.
3. Enable **Template repository**.

This lets other people use the **Use this template** button.

## 4. Recommended About Section

Description:

```text
A safe task-folder router for Codex workspaces using configurable labels like project:, plugin:, client:, site:, and app:.
```

Topics:

```text
codex
codex-hooks
automation
workspace
template
developer-tools
task-management
```

## 5. Verify After Publishing

Clone the public repo into a temporary folder and run:

```bash
python3 -m unittest tests/test_router.py
```

Then test installing into a temporary workspace:

```bash
tmp=$(mktemp -d)
python3 scripts/install.py --target "$tmp" --routes "project=projects" --yes
```

The repository also includes a GitHub Actions workflow in `.github/workflows/test.yml`. After publishing, confirm the first workflow run passes.
