Hermes Agent 메모리 시스템:
- memory.tool: key-value 형태로 영구 기억 저장
- session_search: 과거 대화 검색 (FTS5)
- cronjob.output: 실행 결과 기억
- memory는简短하게 유지, 경로는 full path 사용
- 파일 경로/설정/사용자 선호도等重点 저장
§
Obsidian Vault 경로: /home/comage/obsidian-vault/06-Wiki-시스템/
GitHub: https://github.com/comage9/obsidian-vault
Wiki 구조: Raw/, Wiki/, Logs/, 클로드.md
Scripts: ~/.hermes/scripts/wiki-*.sh
Cronjob: 3개 (인제스트/린트/동기화)
§
# Hermes Agent 공식 문서 (중요 링크 — 항상 참조)
## 핵심 문서
- Quickstart: https://hermes-agent.nousresearch.com/docs/getting-started/quickstart
- Skills Hub: https://hermes-agent.nousresearch.com/docs/skills
- ACP Internals: https://hermes-agent.nousresearch.com/docs/developer-guide/acp-internals
## Architecture: https://hermes-agent.nousresearch.com/docs/developer-guide/architecture
## AI Providers: https://hermes-agent.nousresearch.com/docs/providers
## 설치: curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
## 최소 컨텍스트: 64K tokens 필수
§
## Hermes Wiki 현재 통합 범위
✅ 완료: 06-Wiki-시스템/ (Raw/Wiki/Logs, 스크립트4개, Cronjob3개)
❌ 미진행: 01-VF-프로젝트/, 02-금형정보/, 04-일반/ — 동일 구조로 확장 가능
§
VF 생산: http://bonohouse.p-e.kr:5174 (포트 5174/5176)
§
VF 제품명 규칙: 모던[단수][앞판색상]오크=모던플러스내추럴오크우드상판형[단수], 맥스[단수]투명=맥스서랍장투명[단수]단, 맥스[단수]투명오크=어반우드상판베이직서랍장[단수]단투명
VF 색상: Gray2=라이트그레이=그레이2
VF 생산: http://bonohouse.p-e.kr:5174
§
VF 생산 계획 메모3 (2026-04-30):
- 와이드 728: 1팔레트
- 737: 1팔레트
- 727: 1팔레트
- 748: 1팔레트
- 796: 1팔레트
§
재고 메모 (2026-04-30):
- 277: 1팔레트
- 697: 1팔레트
- 300: 3팔레트
- 306: 2팔레트 (중복)
- 276: 1팔레트
- 289: 2팔레트 (중복)
- 528: 1팔레트
- 150: 2팔레트 (중복)
- 301: 3팔레트 (중복)
- 291: 1팔레트
- 281: 2팔레트 (중복)
- 272: 1팔레트
- 280: 2팔레트
- 508: 1팔레트
- 558: 1팔레트
- 516: 1팔레트
- 520: 1팔레트
- 2034: 2팔레트
- 540: 1팔레트
- 맥스 6단 투명: 1팔레트
- 532: 1팔레트
- 695: 1팔레트
- 690: 1팔레트
§
응답 원칙: 사실만 말하기, 거짓 만들지 않기, 모르면 모른다고 하기
§
§
GoClaw 설치 (2026-05-02): PostgreSQL 18+pgvector, Go 1.26.2, 포트18789/18790, onboard완료(v57), 프로세스명openclaw-gateway, setupWizard미실행, skill deps一部欠損, github installer경로오류(/app权限), GoClaw≠OpenClova혼동금지