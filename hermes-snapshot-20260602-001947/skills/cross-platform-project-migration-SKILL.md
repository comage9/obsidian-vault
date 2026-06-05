---
name: cross-platform-project-migration
description: Run a Windows-developed Django+React (Vite) fullstack project on Linux — handle read-only mounts, incompatible .venv, platform-specific node_modules, and service verification
tags: []
related_skills: []
---

# Cross-Platform Project Migration (Windows → Linux)

## Trigger

Use this skill when a user asks you to:
- Run/verify a project that was developed on Windows and copied to Linux
- Set up a Django + React project from Windows source
- Start/fix a project with `node_modules` or `.venv` from Windows
- A `npm run dev` / `vite` / `django` command fails with "esbuild platform mismatch"
- A `python manage.py` command fails because activate script path is wrong
- A user says "이전에 실행한 적 있다" / "이전처럼 실행해줘" / "VF 실행해줘" — see "이전처럼 실행 워크플로우" below
- A user says "마스터에 수정 진행해" / "원본에서 작업해" / "이 폴더는 윈도우/리눅스 둘 다 실행한다" — see "Shared-master workflow" below
- A user points at a project root that lives on a shared (Windows+Linux) mount and asks you to run or edit it

## Diagnostic Flow

### 1. Check Filesystem Read-Write

```
mount | grep <mount_point>
# Look for "ro" in flags → read-only
```

If read-only (`fuseblk ro`), you CANNOT create venv/node_modules in-place. Must copy the project to a writable location first:

```bash
cp -r "<source>" <writable_home>/<project-name>
```

**However — confirm with the user where they want edits to land.** Some users run a Windows+Linux-shared project where the source is the single source of truth across both OSes (e.g. VF-new - 복사본 shared via NTFS mount). For those users, the workflow is:

- **Windows**: edit the master directly (e.g. `E:\coding\VF-new`)
- **Linux**: copy master → `/home/comage/<name>/` → regenerate `.venv` and `node_modules` on Linux → run from the copy → **never** write back to the master from Linux
- The copy is ephemeral, regenerated each session; the master is canonical

**Confirm the mount is actually read-only before assuming it.** On 2026-06-02 the `fuseblk ro` flag was misleading — `touch .test_write && rm .test_write` succeeded because the user-mode mount allows writes from the mounter. Always probe with a test file, not the mount flags.

**The "always copy to home first" reflex is wrong for shared NTFS projects.** Ask the user, or look for a `.git`/`.gitignore` in the mount root to see if it's a working tree, before reflexively copying.

### 2. Check Virtual Environment

Windows creates venv with `Scripts/activate` (not `bin/activate`):

```bash
# Linux-compatible venv check
ls .venv/bin/activate 2>/dev/null || ls .venv/Scripts/activate 2>/dev/null
```

If `Scripts/` (Windows) but no `bin/` (Linux):
- The venv is incompatible — the Python executable path, site-packages structure, and symlinks are Windows-specific
- The pyvenv.cfg will reference a Windows path like `C:\Users\...`
- **Solution:** Recreate venv with `uv venv --clear --python 3.12` or `python3 -m venv .venv`

```bash
# Check pyvenv.cfg to confirm
cat .venv/pyvenv.cfg
# If "home = C:\\..." → Windows-origin
```

**User may block `rm -rf .venv`.** Alternative: create the venv alongside with a different name, or use `uv venv --clear` (which replaces in place without rm).

**Best approach for existing Windows venv:** Use `uv venv --clear --python 3.12` which atomically replaces the venv directory.

### 3. Check node_modules Platform

The most common failure: esbuild has platform-specific native binaries.

```bash
# Try starting the frontend
cd <frontend_dir> && npm run dev
# Error: "You installed esbuild for another platform... @esbuild/win32-x64 present but @esbuild/linux-x64 needed"
```

**Solution (safe, no data loss):**

```bash
# Move Windows node_modules to backup first (user-approved)
mv node_modules /tmp/node_modules-windows-backup-$(date +%Y%m%d)
# Then install Linux-native packages
npm install
```

**If user blocks rm/mv:** Explain the situation — esbuild and other native modules (sharp, canvas, sqlite3, etc.) ship platform-specific binaries. Without reinstalling, the frontend cannot start on Linux. Offer `mv` as the zero-data-loss alternative.

### 4. Handle .env Files

Read the `.env.example` for the project structure. The actual `.env` may contain secrets (API keys, passwords). If the file tool blocks reading `.env`, use terminal:

```bash
cat .env
# or check via head -c 200 if sensitive
```

**Key variables for Django+React projects:**
- `DJANGO_BASE_URL` or `REACT_APP_API_URL` — backend URL
- `PORT` — frontend port
- `SECRET_KEY` — Django secret
- Google Sheets CSV URLs (common in data dashboard projects)
- AI model settings (Ollama, Anthropic)

Many of these are public (CSV URLs published to web) and won't be redacted. Use terminal if the file tool blocks.

**Important: Django settings.py often auto-loads `.env` via python-dotenv.**
This means `python manage.py migrate` and `python manage.py runserver` already see the env vars without needing to `source .env` manually. If you see env vars logged during `migrate`/`check`/`runserver` startup, that's the settings.py loading them — you don't need a separate `source` step.

**⚠️ Debug log truncation trap:** Some projects log env values during Django startup (e.g. `[DEBUG] Set OUTBOUND_GOOGLE_SHEET_URL = https://docs.google.com/spreadsheets/d/e/2PACX-1vQ`). The log may TRUNCATE long URLs at ~55 chars for display. This does NOT mean the env value is corrupted — verify the full value via terminal `cat .env` or `python3 -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print(len(os.environ.get('KEY', '')))"`.

### 5. Start Backend (Django)

```bash
cd <backend_dir>
source .venv/bin/activate
```

**Venv setup (if Windows-origin):**
```bash
uv venv --clear --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Migration and check:**
```bash
python manage.py migrate
python manage.py check
```

**Start with background=true + notify_on_complete:**
```bash
python manage.py runserver 0.0.0.0:<port>
```

### 6. Start Frontend (Vite/React)

```bash
cd <frontend_or_client_dir>
npm run dev -- --host 0.0.0.0 --port <port>
```

### 7. Verification

Check backend API responds:
```bash
curl -s http://localhost:<backend_port>/api/
```

Check frontend serves:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:<frontend_port>/
```

Verify data endpoints (project-specific):
```bash
curl -s http://localhost:<backend_port>/api/<endpoint> | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Records: {len(d) if isinstance(d, list) else d.get(\"count\", \"?\")}')"
```

## Shared-master workflow (Windows+Linux share one source tree)

Some users run a single project from a shared mount (NTFS, exFAT, Syncthing) and edit it from **both** Windows and Linux. On 2026-06-02 the user explicitly corrected the agent's reflex of "copy project to home, then edit the copy" — for them, the master is the source of truth, **edits go to the master**, and the Linux copy is a throwaway build/run target.

The shape:

- **Master** (e.g. `/media/comage/data/coding/VF-new - 복사본/` or `E:\coding\VF-new\` on Windows): the canonical source. **All code edits land here.** Both OSes treat this as the only project.
- **Linux run target** (e.g. `/home/comage/VF-project/`): a regenerated copy used only to run with Linux-native `.venv` and `node_modules`. The user does `cp -r master /home/comage/VF-project` (or has a sync rule), and the agent regenerates the Linux-native dependencies each session. **Never edit the run target — the edits don't propagate back.**
- **Windows run target**: usually the master itself, or a copy with the same path on Windows. Windows handles its own `.venv` (Scripts/) and node_modules.
- **Simultaneous execution forbidden**: SQLite locks, file watches, port 5176/5174 conflicts. The user explicitly cited "데이터 누락/시간차" as the reason for picking one OS at a time.

Pitfalls specific to this workflow:

- **Don't sed-fix `dist/` and call it done.** `dist/index.js` is a `vite build` artifact that embeds the source's `allowedHosts` array. Sed-fixing the dist file is cosmetic — the next `vite build` on either OS rewrites the same stale list. **Fix the source (`vite.config.ts`).**
- **Don't trust the .env in the master.** It may be a Windows-shaped file (CRLF line endings, placeholder values like `***`). The `start_all.sh` pre-flight check (`-x .venv/bin/python`, `-d node_modules`) will catch missing pieces, but value-level staleness needs terminal `cat .env` or `python3 -c "from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('KEY'))"`.
- **The placeholders are placeholders, not secrets.** On 2026-06-02 the master `.env` had `GOOGLE_SHEETS_API_KEY=***`. The user didn't know the value; the placeholder was literal `***` in `.env.example` and `.env.sample` too. Don't try to "preserve" or "uncover" the placeholder — **delete the line** if it's not needed for the current run, or leave it as `# GOOGLE_SHEETS_API_KEY=` if you want to mark it intentionally disabled.

The full VF-specific re-run reference is at `references/vf-project-rerun-workflow.md` — read it before any "이전처럼" / "재실행" request for that project.

## Pitfalls

- **Read-only filesystem** (`fuseblk ro`): Cannot create files in-place. Must copy to home directory first. This is NOT an error — it's a standard Linux mount for NTFS/exFAT external drives.
- **The "always copy to home first" reflex is wrong for shared Windows+Linux projects.** If the user has a single source of truth on a shared mount and runs both OSes against it, copy to a writable location is correct on Linux (so you can rebuild venv/node_modules), but the master is still the source of truth. Don't read from or edit the copy and assume the master is up to date — and never write back to the master from Linux (cross-OS path/line-ending corruption). On 2026-06-02 the user had to explicitly correct this: "이 폴더는 윈도우에서도 실행한다... 수정이 있다면 마스터에 바로 진행한다."
- **The `fuseblk ro` flag can lie.** A 2026-06-02 NTFS mount showed `ro` in `mount` output but `touch .test_write && rm .test_write` succeeded because user-mode fuse mounts allow writes from the mounter. Probe with a real file, not the mount flags, before assuming a backup will fail.
- **Stale IPs in `dist/` regenerate from source.** On 2026-06-02, `frontend/dist/index.js` (a `vite build` artifact) contained a hardcoded `allowedHosts: [..., "220.121.225.76", "211.233.30.206", "121.132.232.117", ...]` array. Sed-fixing the dist file is cosmetic — the next `vite build` will rewrite the same stale list from the source `vite.config.ts`. **Always fix the source.** If you can't, document the build-time rewrite so the next session doesn't rediscover the regression.
- **External IPs in wiki/MEMORY are stale by default.** The user explicitly called out 2026-04-08 wiki entries pointing to `http://220.121.225.76:5174/` as a falsehood. The machine's real IP at 2026-06-02 was `59.9.19.188` (verified via `hostname -I` + `curl -s -m 5 https://ifconfig.me`). Always re-probe with `hostname -I` and cross-check `ifconfig.me` before quoting an "external URL" — DHCP, ISP, VPN, and NAT can all change it, AND the wiki entry may have referred to a different machine entirely.
- **User may block destructive operations** (`rm -rf`, `rm node_modules`). Always use `mv` (backup) + fresh install as the alternative.
- **User may block `rm -rf .venv`** — use `uv venv --clear` which replaces in place.
- **Django version constraints** in requirements.txt may conflict with what's actually installed. Check `python -c "import django; print(django.__version__)"`.
- **Port already in use:** Check with `ss -tlnp | grep <port>` or `lsof -i:<port>`.
- **Trailing slash in Django URLs:** Some projects may have `trailing_slash=False` in router config. Try both `/api/endpoint/` and `/api/endpoint`.
- **Frontend port ≠ backend port.** Common: backend on 5176, frontend on 5174 (or 3000, 8000).
- **Frontend `.env`** may contain `DJANGO_BASE_URL=http://localhost:<backend_port>` for the proxy/API target.
- **Frontend console errors may reveal backend Python module issues.** When a sync fails, the error message often includes the Python traceback verbatim (e.g. `No module named 'requests'`). See `references/frontend-backend-error-tracing.md` for the diagnostic pattern and graceful error handling fix.
- **"이전처럼 실행" 요청 패턴**: 사용자가 "이전에 실행한 적 있다" / "이전처럼" 식으로 말할 때 단일 소스(스크립트만, 환경만)로 결정하지 말 것. **3중 검증** (위키 세션로그 → start 스크립트 → 실제 환경)이 정답. VF 프로젝트는 5174(프론트) + 5176(백엔드). `references/vf-project-rerun-workflow.md` 참조.
- **백업 폴더의 다중 역할 오인**: `/media/comage/data/hermes-backup/` 같은 NTFS 마운트는 (1) Hermes 메모리/스킬/위키 백업 정본, (2) 여러 Linux 머신 + Windows 에이전트 간 **공유 폴더**, (3) Syncthing 마운트(rw) — **세 역할을 동시에 함**. "백업 폴더 = 단순 백업"으로만 보면 다른 OS/에이전트가 동시에 작업하는 공유 데이터가 누락될 수 있음. 운영원칙 작성 시 3가지 역할 모두 명시.
- **마스터에서 Linux 실행본 재생성 시 `cp -r` 후 `mv` + 재생성 패턴 (2026-06-02)**: `rm -rf`는 사용자가 차단할 수 있음. 패턴: (1) `cp -r <master> /home/comage/<name>/` (2) `cd <copy>/backend && mv .venv .venv.win.bak && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` (3) `cd <copy>/frontend/client && mv node_modules node_modules.win.bak && npm install`. `.venv.win.bak`, `node_modules.win.bak`은 디버깅용으로 보존 (디스크 여유 있으면). 사용자: "이전처럼 따로 실행한다" / "필요하면 생성해서 실행해줘" → 이 패턴이 정답.

## Next.js-Specific Pitfalls

Next.js projects (especially v15+) have additional cross-platform issues beyond basic esbuild:

### 1. Lightningcss native binary

Next.js + Tailwind CSS v4 use `lightningcss` which ships platform-specific optional binaries:

```
Error: Cannot find module '../lightningcss.linux-x64-gnu.node'
```

**Fix — install the platform-specific optional dep:**
```
npm install lightningcss-linux-x64-gnu   # for glibc Linux
npm install lightningcss-linux-x64-musl  # for musl Linux (Alpine)
```

This is an *optional dependency* — `npm install` should auto-detect it, but if the lockfile was generated on Windows, the optional dep may be skipped. Manually installing it triggers the correct resolution.

### 2. Stale `.next` dev cache

When `.next/` was created on Windows and the project moves to Linux, the Turbopack dev cache retains references to Windows paths/binaries. Even after fixing node_modules, dev mode (`next dev`) still fails because it reads cached chunks:

```
Error: Cannot find module '../lightningcss.linux-x64-gnu.node'
Require stack:
  - /home/.../.next/dev/build/chunks/[root-of-the-server]__....js
```

**Fix (two approaches, try in order):**

**A) Production build (preferred — no cache deletion):**
```
npx next build          # creates fresh production build
npx next start -p 3000  # serve production build
```

This bypasses the dev cache entirely and works even when `.next/` cannot be deleted (user blocked rm).

**B) Clear dev cache (if user allows):**
```
rm -rf .next/cache .next/dev
npx next dev
```

**C) Different port doesn't help** — the `.next/cache` and `.next/dev` directories are project-level, not port-level. `next dev -p 3000` and `next dev -p 3001` share the same cached chunks. Only approach A (production build) or B (clear cache + dev) works.

### 3. npm install may skip optional deps

When `package-lock.json` was generated on Windows, `npm install` on Linux may skip platform-specific optional dependencies from `node_modules` entirely. The lockfile caches the `optional: true` flag, so npm doesn't re-evaluate on the new platform.

**Fix:** Remove `package-lock.json` and reinstall:
```
rm package-lock.json
npm install
```

**If the user blocks deleting package-lock.json,** try these workarounds in order:

A) `npm rebuild <native-package>` — triggers npm to re-evaluate and install the correct platform binary for the specific package without touching the lockfile:
```
npm rebuild lightningcss
```

B) Manually install the Linux optional dep package (npm creates a symlink / copies the .node file):
```
npm install lightningcss-linux-x64-gnu
npm install @esbuild/linux-x64
```

C) If all else fails and the only issue is a cached `.next/` dev bundle referencing old paths, use a production build instead (see section below).

### 4. Next.js package.json scripts check

Some Next.js projects have custom build scripts that reference Windows batch files:
```json
"build:exe": "pyinstaller ... 배포판제작.bat ..."
```

These are unrelated to the core `dev`/`build`/`start` commands and can be ignored on Linux. Only the standard Next.js lifecycle commands matter:
```json
"dev": "next dev",
"build": "next build",
"start": "next start"
```

## Verification Checklist

- [ ] Filesystem is writable
- [ ] .venv is Linux-compatible
- [ ] node_modules is Linux-native
- [ ] .env files have correct target URLs
- [ ] Python dependencies installed
- [ ] Database migrations ran successfully
- [ ] `python manage.py check` passes (0 issues)
- [ ] Backend server responds via curl
- [ ] Frontend server responds HTTP 200
- [ ] Key API endpoints return real data

## Co-launch orchestration: start_all.sh + stop_all.sh

When the user will repeatedly ask "다시 띄워줘" / "재시작해줘" / "다음에도 실행해달라" for the same multi-service project, **do not have them memorize two `nohup ... &` commands**. Add `start_all.sh` (co-launch + health check) and `stop_all.sh` (PID-file + port-fallback) to the project root. The VF-project (보노하우스 production dashboard) shipped these on 2026-06-02 and the user now uses them as the canonical execution path.

The full template is in `scripts/start_all.sh.template` — copy, set ROOT_DIR / VENV_PY / FRONTEND_DIR / ports, done.

**What the orchestration buys you (vs raw nohup):**
- **Single command** — `./start_all.sh` instead of two backgrounded processes
- **Pre-flight checks** — refuses to launch if `.venv/bin/python` or `node_modules/` is missing, or if the target ports are already bound (offers to kill the holder)
- **Health-check loop** — 5 seconds in, prints `curl HTTP %{http_code}` for each service so you immediately see "5176: 200, 5174: 200" or the failure mode
- **PID files** — `/tmp/vf-{backend,frontend}.pid` so `stop_all.sh` knows what to kill even if the user invoked start from a different shell
- **Log files** — `/tmp/vf-logs/{backend,frontend}.log` instead of stdout noise; `tail -f` works as expected
- **Trap-based cleanup** — `Ctrl+C` kills both children, removes PID files, no orphans
- **wait -n fallback** — if one child dies unexpectedly, the other is killed too (no half-running dashboard)

**Stop script pattern (idempotent):**
```bash
# Try PID files first
for f in /tmp/<project>-{backend,frontend}.pid; do
  [[ -f $f ]] && kill $(cat $f) 2>/dev/null
  rm -f $f
done
# Fall back to pkill on port+command pattern (in case started outside the script)
pkill -f "manage.py runserver.*<port>" 2>/dev/null
pkill -f "vite.*--port.*<port>" 2>/dev/null
# Verify
ss -tln | grep -E ":<port>" && echo "STILL UP — check manually" || echo "cleanly stopped"
```

**Pitfall — `wait -n` is bash 4.3+.** Older distros may not have it. If you target a portable script, replace with `wait` (blocks until both children exit) and rely on user Ctrl+C.

**Pitfall — Hermes `terminal(background=true)` ≠ script-level `nohup ... &`.** The orchestration script uses `nohup`-style backgrounding internally because each service is a long-lived server. Don't conflate the two: the agent uses `background=true` for its OWN command lifecycle tracking; the user's `start_all.sh` is a separate beast for the user's own terminals.

**Don't put the script in a read-only mount.** VF-project lives at `/home/comage/VF-project/` (writable copy from `/media/comage/data/coding/VF-new - 복사본/`). The script goes in the writable copy, not the source-of-truth mount.

**Source it in MEMORY.md once stable** — a single line like "VF 실행: cd /home/comage/VF-project && ./start_all.sh | ./stop_all.sh" is enough; the user and the bot both reach for this every time.

## Related references

- `references/frontend-backend-error-tracing.md` — when frontend console shows backend Python traceback
- `references/vf-project-rerun-workflow.md` — "이전처럼 실행해줘" / "이전에 실행한 적 있다" 요청 시 3중 검증 (위키 세션로그 → start 스크립트 → 실제 환경) 워크플로우. VF 프로젝트 포트(5174/5176), mandatory-verification 5단계, 띄우는 순서, 함정 8개 포함.
- `scripts/start_all.sh.template` — co-launch template (backend + frontend + health check + PID files + log dir + trap cleanup). Copy, edit ROOT_DIR / VENV_PY / FRONTEND_DIR / ports, drop into the project root.
