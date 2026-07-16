# Security Policy

Task Folder Router for Codex is designed to be local-only and minimal.

## Supported Versions

Security fixes should target the latest version on `main`.

## Reporting A Vulnerability

If you find a security issue, please open a private GitHub security advisory if available for the repository, or contact the repository owner privately before publishing exploit details.

## Security Boundaries

The router should never:

- send data to external services;
- read the contents of generated task folders;
- execute commands inside generated folders;
- store credentials or secrets;
- create remote repositories;
- commit, push, deploy, or install dependencies;
- accept prompt-provided paths as destinations.

Expected behavior is limited to reading the hook event, reading local router configuration, creating a safe folder, and writing local session state.
