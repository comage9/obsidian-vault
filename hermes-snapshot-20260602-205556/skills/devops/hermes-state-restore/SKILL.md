---
name: hermes-state-restore
description: Restore Hermes Agent state (memories, user profile, skills) from a flat backup directory — load MEMORY.md/USER.md via the memory tool, copy skill files, verify obsidian connectivity
---

# Hermes State Restoration from Backup

## Trigger

Use this skill when a user asks you to:
- "Restore from backup" (Hermes memories/skills)
- "Apply 운영원칙/소울 from backup"
- "Load my Hermes configuration from the backup"
- "Copy memories and skills from [path]"
- Has a directory with `memories/`, `skills/`, and/or `obsidian/` subdirectories

## Overview

Unlike file-level restoration (cp -r), Hermes state restoration requires using the `memory` tool to load MEMORY.md and USER.md entries so they become part of the persistent cross-session memory system. Skills are file-level and can be copied directly, but their content should be validated against the skill registry.

## Step 1: Inventory the Backup

```bash
ls -la <backup_path>/
```

Expected subdirectories:
| Path | Content | Action |
|------|---------|--------|
| `memories/MEMORY.md` | Technical notes, environment facts | Load via `memory` tool |
| `memories/USER.md` | User profile, operating principles | Load via `memory` tool |
| `skills/` | SKILL.md files + categories | Copy to `~/.hermes/skills/` |
| `obsidian/` | Wiki / knowledge base | Verify path; read-only access OK |

## Step 2: Load MEMORY.md → memory store

Read each line block and load it as a memory entry:

```python
# For each meaningful paragraph/line in MEMORY.md:
# memory(action="add", target="memory", content="<fact>")
```

**Crucial:** MEMORY.md uses the SEPARATOR `§` between entries. Each `§`-delimited block is one memory entry. Do NOT save the entire file as one entry — that wastes capacity and makes individual facts un-searchable.

## Step 3: Load USER.md → user profile

Read USER.md line by line. Each numbered line or paragraph is a distinct user preference or operating principle.

**Crucial:** USER.md content is high-priority — this is the user's operating principles and "soul" (소울). Missing any entry will cause the user extreme frustration (극도분노). Each principle must be saved as a separate memory entry with target="user".

**Common USER.md categories to look for:**
- Communication style preferences
- Workflow preferences ("step by step", "one at a time")
- Technical constraints (Reasonix ACP, wiki-first, etc.)
- Data handling rules (no create/update/delete without instruction)
- Prohibited behaviors (assumptions, premature conclusions)
- Verification requirements

## Step 4: Copy Skills

```bash
cp -r <backup_path>/skills/* ~/.hermes/skills/
```

**Validation:** After copy, check that the skill shows up:
```bash
ls ~/.hermes/skills/
```

**Important:** The `curator` service uses `.usage.json`, `.curator_state`, and `.hub/` metadata files. These are in the backup's skills/ directory. Copying them along with the actual skills preserves usage tracking. The `.stfolder` Syncthing marker should NOT be copied.

## Step 5: Verify Obsidian (if present)

```bash
ls <backup_path>/obsidian/
```

Obsidian vaults are typically large and read-only OK. Just verify the directory structure exists and is accessible. No copy needed unless the user asks for it — the vault likely lives at its own path on each machine.

## Step 6: Final Validation

Verify the loaded memories are actually accessible:

```bash
# They are loaded into the conversation's memory tool state.
# Future sessions will auto-inject them.
```

## Pitfalls

- **Do NOT save MEMORY.md as one big entry.** Split by `§` separator or logical paragraphs. One entry = one fact.
- **Do NOT skip USER.md.** It contains the user's operating principles. Missing even one principle will cause "극도분노" (extreme anger).
- **Do NOT create/update/delete actual data without explicit instruction.** USER.md will almost certainly contain a rule about this.
- **The `skills/.hub/` directory** contains hub-index metadata. Copying this during restoration ensures skill search/browse works properly.
- **Lock files** (`.lock` suffix in backup) should be skipped — they're write-locks from concurrent access, not actual content.
- **Windows-created files** in the backup might have UTF-8 BOM or CRLF line endings. The memory tool handles these fine, but terminal/file operations might need care.
- **If skills already exist** with the same name, the copy overwrites them. Consider backing up existing skills first: `cp -r ~/.hermes/skills ~/.hermes/skills.bak.$(date +%Y%m%d)`.

## How This Differs from Multi-Device Sync

| Aspect | `hermes-multi-device-sync` | `hermes-state-restore` |
|--------|---------------------------|------------------------|
| Trigger | "Share config", "sync" | "Backup restore", "apply 운영원칙" |
| Method | Syncthing P2P continuous sync | One-time manual load from flat files |
| Memory ingestion | File copy only | `memory` tool (semantic ingestion) |
| User profile | File copy only | `memory` tool (semantic ingestion) |
| Risk profile | Data loss from sendreceive | Overwrite existing, not data loss |
