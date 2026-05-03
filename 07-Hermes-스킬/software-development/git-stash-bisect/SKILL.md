---
name: git-stash-bisect
description: "Large uncommitted changes break a page — isolate the culprit by applying stash in small chunks."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, debugging, frontend, react, vite, bisection]
    related_skills: [systematic-debugging]
---

# Git Stash Bisect — Large Uncommitted Change Isolation

## Overview

When `git stash pop` or applying 500+ lines of uncommitted changes breaks a page (blank screen, crash, console errors), you need to isolate which change causes the problem.

**Core principle:** Apply changes in small, testable chunks. Binary-search your way to the culprit.

## When to Use

- **Trigger:** Stash or uncommitted changes (500+ lines) break a specific page or component
- **Symptom:** Page goes blank, React throws error, or behavior changes only when ALL changes are applied
- **Prerequisite:** You have `git stash` or uncommitted changes and a reproducible test (e.g., browser refresh shows blank page)

**Don't use when:**
- Changes are already committed (use `git bisect` instead)
- The bug is immediately reproducible from a single file (just read that file)

---

## The Workflow

### Step 1: Verify Baseline

Before touching anything, confirm the page works WITHOUT the changes:

```bash
# Option A: stash temporarily
git stash push
# → refresh page → should work
git stash pop

# Option B: commit first (recommended)
git add -A
git commit -m "WIP: before big change"
```

### Step 2: Save Your Changes as a Patch

```bash
# Save uncommitted changes to a patch file
git diff > ~/big-change.patch

# If patch has trailing whitespace issues, fix them:
sed -i 's/[[:space:]]*$//' ~/big-change.patch
```

**IMPORTANT:** `git diff` outputs paths relative to the repo ROOT, not the subdirectory. If you're in a subdirectory (e.g., `frontend/client/`), either:
- Run `git diff` from the repo root
- Or use `git apply` from the repo root instead of `patch -p1`

```bash
# WRONG — patch -p1 from subdirectory fails with git diff output
cd frontend/client && patch -p1 < ~/big-change.patch  # FAILS

# CORRECT — use git apply from repo root
cd /repo/root && git apply ~/big-change.patch

# Or copy patch to root and apply from there
cp ~/big-change.patch /repo/root/big-change.patch
cd /repo/root && git apply big-change.patch
```

**Stash safety:** `git stash pop` DROPS the stash on failure. Use `git stash apply` (doesn't drop) or save the patch BEFORE testing:
```bash
# Save stash content as patch before applying
git stash show -p > ~/stash-content.patch
git stash show -p > ~/stash-content.patch  # stash is NOT dropped
```

### Step 3: Apply in Chunks using `git stash push -p`

The `-p` (patch) flag lets you interactively select which hunks to stage:

```bash
# Start interactive patch staging
git stash push -p
```

In patch mode:
- `y` = stage this hunk
- `n` = skip this hunk
- `s` = split into smaller hunks (if available)
- `q` = quit — hunks you've already marked will be staged

**Strategy:**
1. Stage the **first 30-50%** of changes
2. `git stash push -p` again to stage **another 30-50%**
3. Each time, test: does the page still work?
4. When page breaks → the culprit is in the LAST batch you added

### Step 4: Binary Search to Isolate

Once you know which batch contains the bug:

```bash
# Unstage the bad batch
git checkout -- .

# Re-stage only HALF of the bad batch
git stash push -p
```

Repeat: halve the bad batch each time until you find the exact file or block.

### Step 5: Fix or Commit

- **Option A:** Fix the bad code inline, then `git stash drop` (if you stashed)
- **Option B:** Stage everything except the bad file, commit, then fix the bad file separately
- **Option C:** Use `git stash push -p` to stage all EXCEPT the bad lines

---

## Non-Interactive Alternative: `git add -p`

If you don't want to use `git stash`, use `git add` directly:

```bash
# Interactively stage chunks
git add -p

# Review what you've staged
git diff --cached | wc -l

# Commit staged chunks as a "working checkpoint"
git commit -m "WIP: partial changes (batch 1)"
```

Then continue staging and committing in batches.

---

## With Vite/Cache: Clear Cache After Each Batch

Vite caches compiled assets in `node_modules/.vite`. After each successful batch:

```bash
rm -rf frontend/client/node_modules/.vite
# Then refresh browser
```

**If you forget:** Hard refresh (Ctrl+Shift+R / Cmd+Shift+R) or use Vite's `--force` flag.

---

## Real Example (This Session)

**Context:** 750-line stash applied to React/Vite frontend → production page blank.

**Steps taken:**
1. `git stash push` → page works → confirms stash contains the bug
2. Tried `patch -p1` from subdirectory → FAILED (paths in git diff are relative to repo root)
3. Tried `git apply` from subdirectory → FAILED (same reason)
4. Used `git checkout` to reset, losing the uncommitted changes entirely

**What went wrong:**
- `git diff` outputs paths like `frontend/client/src/file.tsx`
- When in `frontend/client/`, `patch -p1` strips `frontend/client/` but the paths still say `frontend/client/src/...` → can't find file
- `patch -p2` from `frontend/client/` would work for `frontend/client/src/...` paths, but git diff only gives `-p0` paths

**Correct approach (from real session):**
```bash
cd /repo/root
git diff > ~/big-change.patch
sed -i 's/[[:space:]]*$//' ~/big-change.patch  # fix trailing whitespace
git apply ~/big-change.patch  # from repo root, not patch -p1
```

**Key insight:** `git stash push -p` with **non-interactive** mode can also work via scripting:

```bash
# Apply patch in reverse order to find when it breaks
git checkout HEAD -- .   # reset to clean
# Then apply chunks one by one
patch -p1 < chunk1.patch && test && patch -R -p1 < chunk1.patch
```

---

## Quick Reference

| Situation | Command |
|-----------|---------|
| Start interactive patch stash | `git stash push -p` |
| Save diff as patch | `git diff > ~/change.patch` |
| Apply patch (from repo root) | `cd /repo/root && git apply ~/change.patch` |
| Unapply patch | `cd /repo/root && git apply -R ~/change.patch` |
| Clear Vite cache | `rm -rf node_modules/.vite` |
| Check what changed in file | `git diff src/some/File.tsx` |
| Stage hunks non-interactively | `git add -p` |
| Save stash without dropping | `git stash show -p > ~/stash.patch` |

## Related

- `systematic-debugging` — Always use the 4-phase process BEFORE attempting fixes
- `vf-production` — VF project context for this specific codebase
