# Reasonix ACP Delegation Pattern

## Standard Hermes Delegate Call

```python
delegate_task(
    acp_command="reasonix",
    acp_args=["acp", "-model", "deepseek-flash"],
    goal="<task description>",
    context="<relevant context - file paths, project structure, constraints>"
)
```

## What ACP Mode Provides

- stdio JSON-RPC session (Agent Client Protocol v1)
- Each session is isolated — fresh terminal, no conversation history
- Returns a summary of what was done
- Reasonix gets file read/write, bash, and its own thinking tools

## When to Use

- Complex multi-file coding tasks (3+ files to modify)
- Tasks requiring root cause analysis before fix
- Tasks where intermediate tool output would bloat your context window
- User explicitly says "Reasonix로 해" or "ACP로"

## Session Example (2026-06-01): VF Outbound Sync Fix

**Task:** Fix graceful error handling in outbound sync (Google Sheets 401)

**Context provided:**
- File paths: `/home/comage/VF-project/backend/sales_api/views.py` (outbound_sync func at line 2765)
- File paths: `/home/comage/VF-project/frontend/client/src/components/outbound-tabs.tsx` (handleSync)
- Root cause: Backend returns HTTP 400 on CSV fetch failure → frontend shows destructive error
- requests module already installed

**Result:** Reasonix analyzed all 3 files, produced exact patch instructions for graceful error handling (HTTP 200 with success=False pattern), and identified the toast message improvement.

**Key outcome:** Reasonix could read files and analyze but was blocked from writing directly. The Hermes parent applied the patches manually from the analysis. This is the expected pattern — Reasonix analyzes/recommends, Hermes executes.
