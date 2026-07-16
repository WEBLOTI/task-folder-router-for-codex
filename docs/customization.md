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
  "require_route_prefix": true
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

## Add A Label

Add a new route:

```json
{
  "routes": {
    "project": "projects",
    "experiment": "experiments"
  },
  "require_route_prefix": true
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
