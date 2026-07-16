# Customization

Task Folder Router is configured with labels and folder roots.

The config file lives in the installed workspace:

```text
.codex/task-folder-router.json
```

## Default Config

```json
{
  "routes": {
    "project": "projects",
    "plugin": "plugins",
    "client": "clients",
    "site": "sites",
    "app": "apps"
  },
  "require_route_prefix": false
}
```

## How Routes Work

The key is the label you type in Codex. The value is the folder root.

```text
project: crm        -> projects/crm/
plugin: checkout   -> plugins/checkout/
client: acme inc   -> clients/acme-inc/
site: landing page -> sites/landing-page/
app: admin panel   -> apps/admin-panel/
```

The router only reads the first non-empty line of the first message in a new task.

## Add A Label

Add a new route:

```json
{
  "routes": {
    "project": "projects",
    "experiment": "experiments"
  },
  "require_route_prefix": false
}
```

Then start a task with:

```text
experiment: pricing test
```

The router creates:

```text
experiments/pricing-test/
```

## Remove A Label

Remove the label from `routes`. The hook will reject that label in future tasks.

## Mixed Mode Or Strict Mode

Use mixed mode when you want normal Codex tasks and routed folder tasks in the same workspace:

```json
{
  "routes": {
    "project": "projects",
    "client": "clients"
  },
  "require_route_prefix": false
}
```

In mixed mode:

```text
Create a scratch note.
```

uses the workspace root, while:

```text
project: crm

Build the first screen.
```

uses:

```text
projects/crm/
```

Use strict mode when every new task must be routed:

```json
{
  "routes": {
    "project": "projects",
    "client": "clients"
  },
  "require_route_prefix": true
}
```

In strict mode, a new task without a configured label is blocked.

## Reuse A Folder From Another New Task

Use the same label and name:

```text
client: acme inc

Continue the portal work.
```

This reuses:

```text
clients/acme-inc/
```

## Keep Labels Predefined

Labels are not accepted dynamically. This is intentional. Predefined labels prevent typos or prompt text from creating unexpected folders.

## Safe Names

The task name after the label must be a plain name, not a path.

Good:

```text
project: customer portal
```

Rejected:

```text
project: ../../private
project: ~/secrets
project: folder/name
```
