# Publishing Topology

## Purpose

This reference defines the publish topology for Claude plugins, with `workflow-kit` as the primary example.

It answers four questions:

1. Which file is the canonical source?
2. Which file is the marketplace index?
3. Which local files prove installation state?
4. Which checks prove that a new version is actually present?

## Topology Layers

### Layer 1: Repository canonical source

Repository files are the only place where a release should originate.

For `workflow-kit`:

- Plugin manifest: `skills/workflow-kit/plugin.json`
- Plugin payload root: `skills/workflow-kit/`
- Marketplace index: `.claude-plugin/marketplace.json`

Release changes should start here first.

### Layer 2: Remote marketplace source

After repository changes are pushed, Claude marketplace consumers read from the marketplace repository.

For Cytopia:

- Marketplace repository contains `.claude-plugin/marketplace.json`
- The plugin entry points to `./skills/workflow-kit`

This means the following must stay aligned:

- plugin manifest version
- marketplace entry version
- plugin source path
- plugin name

### Layer 3: Local marketplace metadata

On the user machine, Claude stores marketplace and install metadata under:

- `~/.claude/plugins/known_marketplaces.json`
- `~/.claude/plugins/installed_plugins.json`

These files prove whether the local Claude installation knows about the marketplace and believes a plugin is installed.

### Layer 4: Local cache payload

The actual installed plugin files live under a cache path like:

- `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`

This directory proves what payload was installed, not just what metadata claims.

## Canonical Source Invariants

These are release invariants and should be treated as non-negotiable.

1. `plugin.json.version` must match the marketplace entry version.
2. Marketplace plugin `name` must match the plugin manifest `name`.
3. Marketplace plugin `source` must resolve to the plugin payload root.
4. The plugin payload must already contain the new skill/content before release.
5. Verification must be anchored on a file or string that only exists in the new version.

## Variable Inputs Per Release

These inputs may change from release to release:

- target version number
- target branch
- release tag name
- content anchor used for verification
- whether this is local-only validation or remote publication

## Recommended Release Sequence

1. Confirm canonical source path and branch.
2. Update plugin payload content.
3. Update `skills/workflow-kit/plugin.json` version.
4. Update `.claude-plugin/marketplace.json` version entry.
5. Validate the plugin manifest shape.
6. Verify repository payload contains the new anchor.
7. After user confirmation, push/publish remotely.
8. After user confirmation, run local marketplace update/install.
9. Run three-layer verification.
10. Perform separate session-adoption verification.

## Example: workflow-kit adding a new internal skill

If `workflow-kit` adds a new internal skill named `plugin-publisher`, then the publish topology should confirm:

- repository contains `skills/workflow-kit/skills/plugin-publisher/SKILL.md`
- `skills/workflow-kit/plugin.json` version is bumped
- `.claude-plugin/marketplace.json` plugin entry version is bumped
- local cache path contains `skills/plugin-publisher/SKILL.md`
- verification anchor confirms the new skill exists in installed payload

## Failure Mapping

| Symptom | Likely layer | Typical cause |
|---|---|---|
| Remote marketplace still shows old version | Layer 2 | push/release not complete, wrong branch, stale marketplace source |
| Local install metadata updated but files are old | Layer 4 | wrong source path, stale cache, failed install payload refresh |
| Files are new but current chat behaves old | Session layer | current session has not reloaded the new plugin context |

## Practical Rule

Never treat one layer as proof for another layer.

- Marketplace metadata is not proof of cache payload.
- Cache payload is not proof of current-session adoption.
- Current-session adoption claims require direct session evidence.
