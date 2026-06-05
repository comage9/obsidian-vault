# VF Outbound Sync Graceful Error Handling

Fixed during session 2026-06-01 using Reasonix ACP delegation.

## Problem

프론트엔드 "Sync" 버튼 클릭 시:
1. Google Sheets CSV URL이 401 Unauthorized (시트 접근 권한 없음)
2. 백엔드가 HTTP 400 에러 반환 → 프론트엔드가 빨간 에러 토스트 표시
3. `No module named 'requests'` 오류도 추가 발견

## Fix Summary

### Backend (`views.py` — `outbound_sync` function)

Changed CSV fetch failure from HTTP 400 error to HTTP 200 with `success: false`:

```python
# Before
except Exception as e:
    return Response({'error': f'Failed to fetch/parse CSV: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST)

# After
except Exception as e:
    error_msg = str(e)
    if '401' in error_msg or 'Unauthorized' in error_msg or ...:
        friendly_msg = '구글 시트 접근 권한이 없습니다. 시트 공유 설정을 확인해주세요.'
    elif 'ConnectionError' in error_msg or 'timeout' in error_msg.lower():
        friendly_msg = '네트워크 연결을 확인할 수 없습니다. (오프라인 상태)'
    else:
        friendly_msg = f'데이터를 불러오지 못했습니다. ({error_msg[:80]})'
    return Response({
        'success': False, 'synced': 0, 'message': friendly_msg, 'error': error_msg,
    }, status=status.HTTP_200_OK)
```

### Frontend (`outbound-tabs.tsx` — `handleSync`)

Changed error handling to check `json?.success === false` before `!res.ok`:

```typescript
// Before
const json = await res.json().catch(() => ({}));
if (!res.ok) {
  throw new Error(json?.error || json?.message || 'Sync failed');
}

// After
const json = await res.json().catch(() => ({}));
if (json?.success === false) {
  result = json;
  refreshWarning = json.message || '동기화 실패';
} else if (!res.ok) {
  throw new Error(json?.error || json?.message || 'Sync failed');
} else {
  result = json;
}
```

Also changed toast title from `"성공"` to `"알림"` when `refreshWarning` is set.

## Requirements Added

```txt
requests>=2.31
```
