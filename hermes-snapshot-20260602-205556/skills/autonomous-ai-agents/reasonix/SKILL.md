---
name: reasonix
description: Install, configure, and use Reasonix — a DeepSeek-native Go ACP agent for delegated coding tasks.
category: autonomous-ai-agents
---

# Reasonix ACP Agent

Reasonix is a config-driven, plugin-extensible AI coding agent in a single Go binary, tuned for DeepSeek's prefix cache. This skill covers **installation from source, configuration, and ACP-mode delegation** via Hermes `delegate_task`.

## When to Load

- User says "Reasonix" or mentions installing/configuring/using it.
- User wants to delegate a coding task and says "ACP로" or "Reasonix로".
- The operating principle says Reasonix ACP is the primary coding tool (Codex replacement).

## Install from Source

```sh
# Prerequisites: Go (1.22+)
git clone https://github.com/esengine/DeepSeek-Reasonix.git /tmp/reasonix-src
cd /tmp/reasonix-src
make build                    # → bin/reasonix
cp bin/reasonix ~/.local/bin/  # ensure ~/.local/bin is in PATH
reasonix --version
```

## Setup (one-time)

```sh
cd <project-root>
export DEEPSEEK_API_KEY=sk-...
reasonix setup                # interactive wizard → ./reasonix.toml
```

The generated `reasonix.toml` defaults to `deepseek-v4-flash` on `api.deepseek.com`. Config resolution: flag > ./reasonix.toml > ~/.config/reasonix/config.toml > built-in.

## Model Selection

The config supports multiple providers. Key models:
- **`deepseek-flash`** (default): `deepseek-v4-flash` — fast, cheap, general tasks
- **`deepseek-pro`**: `deepseek-v4-pro` — higher quality, use for:
  - User explicitly says "Pro로", "더 상위 모델로", or "flash 아닌"
  - Complex multi-file refactoring
  - Tasks needing deep analysis without many iterations

**User preference:** When user says Pro로/더 상위 모델, use `deepseek-pro` — never default to flash.

## Usage Modes

### 1. Direct Chat / Run

```sh
reasonix chat
reasonix run "implement the TODOs in main.go"
reasonix run --model mimo-pro "add unit tests"
echo "explain this" | reasonix run
```

### 2. ACP Mode (for Hermes delegate_task)

```sh
reasonix acp -model deepseek-flash   # stdio JSON-RPC
```

### 3. Hermes Delegate (preferred for coding tasks)

```python
delegate_task(
    acp_command="reasonix",
    acp_args=["acp", "-model", "deepseek-flash"],  # or deepseek-pro
    goal="<task description>",
    context="<relevant context - file paths, project structure, constraints>"
)
```

## Config Tuning for ACP Mode

ACP mode needs relaxed permissions to write files:

```toml
# reasonix.toml
[permissions]
mode = "allow"        # "ask" blocks write_file in ACP (no interactive prompts)

[sandbox]
allow_write = ["/home/comage/문서"]  # extra dirs for file writes outside project
```

Without `mode = "allow"`, ACP agents get stuck in **plan mode** — they can analyze and produce plans, but all file writers are silently blocked. Hermes sees "completed" summaries that are actually plans, not executed work.

Without `allow_write` for target paths outside the project root, ACP agents are denied when trying to write to directories like `/home/comage/문서/`.

ACP mode communicates over stdio JSON-RPC (Agent Client Protocol v1). Hermes spawns Reasonix as a child, sends tasks, and receives summaries.

## User Runtime Preferences (this session)

- **Model choice**: When user says "더 상위 모델" or "Pro로" or "flash 아닌", use `deepseek-pro` (`deepseek-v4-pro`), never the default flash.
- **ACP args format**: Use `["acp", "-model", "deepseek-pro"]` (single dash, not `--model`). The flags `--dir` and `--yolo` do NOT exist in the acp subcommand.
- **Default model in config**: Set `default_model = "deepseek-pro"` in reasonix.toml, not flash. The user consistently selects pro for important work.
- **Verification quirk**: ACP tasks always show `deepseek-v4-flash` in the summary model field regardless of the `-model` flag. The model IS respected at runtime — the summary display is cosmetic. Verify by reading the actual response content.

## ACP Timeout & Reliability

**DeepSeek Pro timeout risk:** When using `-model deepseek-pro`, ACP tasks may time out after ~151 seconds (`exit_reason: "interrupted"` with status `"waiting for model response"`). This is likely due to longer inference time. Mitigations:

- Short/simple tasks: `deepseek-flash` works reliably within ACP timeout
- Complex multi-step tasks needing Pro: prefer `reasonix run` (direct CLI) instead of ACP delegation
- If ACP with Pro is essential, break into smaller sub-tasks (< 150 seconds each)

**Model display bug:** ACP task summaries always show `model: "deepseek-v4-flash"` regardless of the `-model` flag. The correct model IS used at runtime — the summary field is cosmetic. Verify model by reading response content, not summary metadata.

## Pitfalls

- **`reasonix acp` is a separate subcommand** — it is NOT shown in `reasonix --help` top-level help. Use `reasonix acp --help` to see its flags.
- **`make build` requires Go** — if `go` is not installed: `sudo apt install golang-go` (Ubuntu) or download from go.dev.
- **`reasonix setup` writes to CWD** — always `cd` to your project root first. The config file is `./reasonix.toml`.
- **API key from `.env`** — `reasonix setup` can scaffold a `.env` file. Otherwise, export `DEEPSEEK_API_KEY` before running.
- **Model name mismatch** — the config's `model` field must match an actual DeepSeek model name (e.g. `deepseek-v4-flash`, not `deepseek-flash`). Verify with `reasonix chat` or check provider docs.
- **--dir and --yolo flags don't exist** — the `acp` subcommand only accepts `-model`. Remove unsupported flags from delegate_task args.
- **Permission mode "ask" blocks ACP writes** — The generated config defaults `[permissions] mode = "ask"`, which causes ACP mode to enter plan-only mode (it analyzes but cannot write files). Change to `mode = "allow"` before delegating.
- **Sandbox restricts write paths** — When the file to create/modify is outside the project root (e.g. `/home/comage/문서/`), add it to `[sandbox] allow_write` or the ACP agent will be denied. The reasonix.toml lives in the project root; write targets outside it need explicit permission.
- **ACP mode shows `deepseek-v4-flash` in summary regardless of `-model` flag** — The model flag is respected at runtime but the summary title may display flash. Verify by checking the actual model in the response content.

## Verification

```sh
# Test ACP handshake
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","clientInfo":{"name":"hermes","version":"1.0"},"capabilities":{}}}' | reasonix acp -model deepseek-flash
# Expected: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":1,...}}
```
