# Frontend-Backend Error Tracing Pattern

When a migrated project's frontend shows errors in the browser console, the error message often contains a direct back-end Python traceback. This is a high-signal diagnostic path.

## The Pattern

1. User opens the app in a browser
2. Frontend JS console shows:
   ```
   Failed to load resource: the server responded with a status of 400
   Sync error: Error: Failed to fetch/parse CSV: No module named 'requests'
   ```
3. The **Python error message** (`No module named 'requests'`) leaks through to the browser because the backend catches the exception and includes `str(e)` in its JSON error response.

## Why This Happens

Django backend catches an `Exception` during CSV/API fetch and returns:
```python
return Response({'error': f'Failed to fetch/parse CSV: {str(e)}'}, status=400)
```

The `str(e)` contains the full Python traceback message, which the frontend displays verbatim.

## Diagnostic Value

- **Direct visibility into Python runtime issues** without checking server logs
- Common culprits visible this way:
  - Missing Python packages (`ModuleNotFoundError: No module named 'requests'`)
  - Network/URL errors (`401 Client Error`, `Connection refused`)
  - Authentication failures (`401 Unauthorized` for Google Sheets)
  - Parsing errors (`UnicodeDecodeError`, `KeyError`)

## Fix Pattern

**Layer 1: Fix the root cause (missing dependency)**
```bash
# requirements.txt
requests>=2.31

# Install
uv pip install requests
```

**Layer 2: Graceful error handling**
When the external data source (Google Sheets CSV, external API) is unreachable, the backend should not return HTTP 4xx/5xx — that triggers the frontend's destructive error handler. Instead:

```python
# Backend: return 200 with success=False for graceful handling
except Exception as e:
    if '401' in str(e):
        msg = '구글 시트 접근 권한이 없습니다.'
    elif 'timeout' in str(e).lower():
        msg = '네트워크 연결을 확인할 수 없습니다.'
    else:
        msg = f'데이터를 불러오지 못했습니다.'
    return Response({
        'success': False,
        'synced': 0,
        'message': msg,
    }, status=200)
```

```typescript
// Frontend: check success flag before !res.ok
const json = await res.json();
if (json?.success === false) {
  // Graceful info toast, NOT destructive error
  result = json;
  refreshWarning = json.message;
} else if (!res.ok) {
  throw new Error(json?.error);
} else {
  result = json;
}
```

## Common VF Project Sync Errors

| Browser Console Error | Root Cause | Fix |
|---|---|---|
| `No module named 'requests'` | Missing `requests` in requirements.txt | Add `requests>=2.31` to requirements, install |
| `401 Client Error: Unauthorized` | Google Sheets link expired/no longer public | Update OUTBOUND_GOOGLE_SHEET_URL in .env |
| `Failed to fetch/parse CSV: ...` | Generic CSV fetch failure | Check .env URL validity, network connectivity |
