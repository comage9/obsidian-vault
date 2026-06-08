# VF2 프로젝트 자가 학습 Nightly

> 소속: Hermes 자가 학습 Cron
> 분야: VF2 프로젝트 (백엔드/프론트엔드/DB 상태)
> Cron ID: `27c1b2555f38`
> 시간: 06:30 KST
> 사용 스킬: `mandatory-verification`

---

## 점검 항목

| # | 항목 | 방법 | 비고 |
|:-:|:----|:-----|:-----|
| 1 | 백엔드 API 상태 | GET /api/health 응답 확인 | database: connected, uptime |
| 2 | 프론트엔드 상태 | Vite dev 서버 프로세스 확인 | 5174 포트 Listen 여부 |
| 3 | POST 라우트 점검 | main.go 라우트 vs 실제 핸들러 비교 | 누락된 POST 라우트 탐지 |
| 4 | DB 연결 상태 | production_logs/barcode_transfer_records/outbound_records 건수 확인 | 0건 이상 정상 수집 확인 |
| 5 | 시스템 리소스 | 디스크 사용량 / CPU / 메모리 체크 | 90% 이상 경고 |

## 동작 흐름

```
1. skill_view(name='mandatory-verification') 로드
2. Wiki {VF2 관련 문서} 읽기
3. curl로 /api/health 호출
4. 프로세스 목록 (ps aux) 확인
5. main.go 라우트 목록 확인
6. DB 건수 체크 (production_logs 등)
7. 디스크/메모리 확인
8. 변경/이슈 발견 시
   - Wiki 새 파일 저장
9. "정상 (YYYY-MM-DD)" 또는 발견 내용 보고
```

## 제약 조건

- 코드/데이터 직접 수정 금지 (Read-only 점검)
- 실제 API 호출은 허용 (건수/상태 확인용)
- 사용자 명령 도착 시 즉시 중단
