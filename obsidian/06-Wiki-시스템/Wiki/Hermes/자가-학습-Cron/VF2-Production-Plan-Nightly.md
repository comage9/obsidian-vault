# VF2 생산 계획 자가 학습 Nightly

> 소속: Hermes 자가 학습 Cron
> 분야: VF2 생산 계획 (기계/금형/제품/색상 일관성)
> Cron ID: `48144ff13cee`
> 시간: 05:30 KST
> 사용 스킬: `mandatory-verification`, `vf2-production-plan-conventions`

---

## 점검 항목

| # | 항목 | 방법 | 비고 |
|:-:|:----|:-----|:-----|
| 1 | 색상코드 정합성 | DB color1 값 vs 엑셀 색상 시트 매핑 비교 | WHITE1/White 180/Cream 등 미등록 색상 탐지 |
| 2 | 금형명 일관성 | production_logs productName vs 금형 시트 금형명 비교 | 같은 금형 다른 제품명 발견 |
| 3 | upsert 덮어쓰기 위험 | 같은 금형+같은 color1+같은 unitQty 중복 레코드 탐지 | 조건부 upsert 병합 위험 |
| 4 | CAP 코드 일관성 | 로코스 L WHITE-CAP(WHITE) vs WHITE1 혼용 여부 | 뚜껑 포함/미포함 구분 정합성 |
| 5 | DB ↔ 기준 문서 차이 | production_logs vs 엑셀 Sheet3/일별생산계획(2) 비교 | 누락/불일치 레코드 탐지 |

## 동작 흐름

```
1. skill_view(name='mandatory-verification') 로드
2. skill_view(name='vf2-production-plan-conventions') 로드
3. Wiki {Hermes/} 읽기 (VF2 관련 문서)
4. DB {production_logs} API 조회 (GET /api/production?all=true)
5. 위 5개 항목 점검
6. 변경/이슈 발견 시
   - vf2-production-plan-conventions/SKILL.md 갱신
   - Wiki 새 파일 저장
7. "변경 없음 (YYYY-MM-DD)" 또는 발견 내용 보고
```

## 제약 조건

- DB 직접 수정 금지 (Read-only 점검)
- 생산 계획 등록/수정/삭제 금지
- 사용자 명령 도착 시 즉시 중단
