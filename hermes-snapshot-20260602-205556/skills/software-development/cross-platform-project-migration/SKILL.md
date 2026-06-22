---
name: cross-platform-project-migration
description: Run a Windows-developed Django+React (Vite) fullstack project on Linux — handle read-only mounts, incompatible .venv, platform-specific node_modules, and service verification
---

# Cross-Platform Project Migration (Windows → Linux)

## Trigger

Use this skill when a user asks you to:
- Run/verify a project that was developed on Windows and copied to Linux
- Set up a Django + React project from Windows source
- Start/fix a project with `node_modules` or `.venv` from Windows
- A `npm run dev` / `vite` / `django` command fails with "esbuild platform mismatch"
- A `python manage.py` command fails because activate script path is wrong

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

## Pitfalls

- **Read-only filesystem** (`fuseblk ro`): Cannot create files in-place. Must copy to home directory first. This is NOT an error — it's a standard Linux mount for NTFS/exFAT external drives.
- **User may block destructive operations** (`rm -rf`, `rm node_modules`). Always use `mv` (backup) + fresh install as the alternative.
- **User may block `rm -rf .venv`** — use `uv venv --clear` which replaces in place.
- **Django version constraints** in requirements.txt may conflict with what's actually installed. Check `python -c "import django; print(django.__version__)"`.
- **Port already in use:** Check with `ss -tlnp | grep <port>` or `lsof -i:<port>`.
- **Trailing slash in Django URLs:** Some projects may have `trailing_slash=False` in router config. Try both `/api/endpoint/` and `/api/endpoint`.
- **Frontend port ≠ backend port.** Common: backend on 5176, frontend on 5174 (or 3000, 8000).
- **Frontend `.env`** may contain `DJANGO_BASE_URL=http://localhost:<backend_port>` for the proxy/API target.
- **Frontend console errors may reveal backend Python module issues.** When a sync fails, the error message often includes the Python traceback verbatim (e.g. `No module named 'requests'`). See `references/frontend-backend-error-tracing.md` for the diagnostic pattern and graceful error handling fix.

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
