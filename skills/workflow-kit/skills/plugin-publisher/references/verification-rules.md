# Verification Rules

## Goal

These rules define the minimum proof required to say a Claude plugin release is successful.

A release is not considered complete just because a command returned success.

## Verification Levels

### Level 0: Repository readiness

Before any publication:

- target plugin files exist in repository
- `plugin.json` is internally valid
- `.claude-plugin/marketplace.json` references the correct plugin and version
- the new version includes at least one unique content anchor

### Level 1: Installed state verification

Read `~/.claude/plugins/installed_plugins.json` and verify:

- the `<plugin>@<marketplace>` key exists
- `version` equals the target version when available
- `installPath` exists and points to the expected cache tree
- `gitCommitSha` is recorded if the install flow provides it

This level proves Claude believes the plugin is installed.

### Level 2: Cache verification

Inspect the installed payload directory and verify:

- the directory exists
- expected files are present
- the plugin manifest exists in the installed payload
- the new skill/references/scripts are physically present

This level proves the payload exists on disk.

### Level 3: Content anchor verification

Search for a release-specific anchor inside the installed payload.

Good anchors are:

- a new skill directory name
- a new markdown heading
- a unique explanatory sentence
- a unique script help string

Weak anchors to avoid:

- generic version strings appearing in multiple places
- filenames that existed before release
- descriptions copied from older docs

This level proves the installed payload is specifically the new payload, not just any payload.

## Session Verification

Session verification is separate and mandatory if anyone claims the current session is already using the new version.

Accepted evidence includes:

1. Starting a fresh Claude session and loading the updated skill successfully.
2. Triggering the updated skill in the current session and observing a new anchor in behavior or output.
3. Showing that a newly added instruction path is available and used.

Without one of these, the strongest allowed conclusion is:

- installation state is updated
- current session adoption is not yet confirmed

## Failure Branches

### Branch A: installed_plugins.json still old

Meaning:
- local install did not update or wrong plugin key was checked

Actions:
- re-check plugin key format
- re-run marketplace update/install after user confirmation
- inspect CLI output for partial failure

### Branch B: installed state updated, cache missing new files

Meaning:
- metadata and payload diverged

Actions:
- inspect installPath
- inspect cached version directory
- verify marketplace source path maps to the intended plugin root

### Branch C: cache has files, anchor missing

Meaning:
- installed payload may still be old, incomplete, or built from wrong source

Actions:
- inspect installed `plugin.json`
- inspect the new file list
- verify the anchor chosen is truly unique to the target release

### Branch D: all local checks pass, but behavior still old

Meaning:
- likely session staleness rather than installation failure

Actions:
- state this clearly
- recommend fresh session or explicit skill reload path
- do not collapse this into a false “fully effective” conclusion

## Minimal Release Success Criteria

A first-pass release may be called successful only if all of the following are true:

1. repository versions are synchronized
2. remote publication step completed, if remote publish was in scope
3. local marketplace update/install completed, if local verification was in scope
4. installed state check passed
5. cache check passed
6. content anchor check passed

To additionally say “the current Claude session is using the new version”, session verification must also pass.

## Suggested Report Language

### If only local installation is proven

Use wording like:

- "已确认本地安装态更新到目标版本。"
- "已确认缓存内容包含新版锚点。"
- "当前会话是否已切换到新版上下文，尚未确认。"

### If session adoption is also proven

Use wording like:

- "已确认本地安装态更新，且当前会话已读取到新版 Skill 内容。"

### If publication was not actually performed

Use wording like:

- "已完成发布前审查与本地可执行闭环准备，但尚未执行云端发布。"
