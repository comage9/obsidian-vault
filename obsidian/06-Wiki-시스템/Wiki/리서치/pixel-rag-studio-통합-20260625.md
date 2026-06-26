# PixelRAG 스튜디오 통합 보고서 (2026-06-25)

**참고 영상**: https://youtu.be/TuL1wwsk4Fo - 바이브랩스의 PixelRAG 스튜디오
**작업 일자**: 2026-06-25
**작업자**: Hermes Agent

---

## 1. 개요

바이브랩스의 PixelRAG 스튜디오 영상을 차용하여 ki-ai-trader 시스템에 다음을 통합:
1. **한글 OCR** (영상: macOS Vision OCR → 우리는 EasyOCR)
2. **하이브리드 검색** (영상: "검색은 글자로 빠르게, 읽기는 그림으로 깊게")
3. **Neo4j 마인드맵** (영상: 시각 마인드맵 → 우리는 Neo4j 그래프)

---

## 2. Phase A: 한글 OCR (EasyOCR)

### 2.1 영상과의 차이
| 항목 | 영상 | 우리 |
|:----|:----|:----|
| **OCR 엔진** | macOS Vision OCR | **EasyOCR** (Python) |
| **한국어** | ✅ | ✅ |
| **스크린샷** | ✅ | ✅ |
| **PDF** | ✅ | ⚠ 차트/이미지 |

### 2.2 설치
```bash
uv pip install --python .venv-3.12/bin/python3 easyocr
# 자동 다운로드: 한국어 인식 모델 (~80MB)
```

### 2.3 사용
```python
from src.data_sources.korean_ocr import extract_combined_text
text = extract_combined_text('/tmp/chart.png')
```

**결과**: 한글 차트 이미지 → 8건 텍스트 추출 (평균 신뢰도 0.95)

### 2.4 한계
- **sudo 미설치** 환경 → Tesseract 대신 EasyOCR 채택
- GPU 가속은 미사용 (CPU 모드 충분)
- 손글씨 인식은 낮음 (인쇄체 중심)

---

## 3. Phase B: 하이브리드 검색

### 3.1 영상 차용
"검색은 글자로 빠르게, 읽기는 그림으로 깊게" — 바이브랩스

### 3.2 구현
```python
# 한글 → 영문 자동 번역 (50+ 도메인 단어 사전)
translate_query("삼성전자 주가 분석")
# → "Samsung Electronics 주가 analysis"
# → PixelRAG API 검색 → "Samsung_Electronics" 매칭!
```

### 3.3 사전 매핑 (KR_EN_DICT)
50+ 도메인 특화 단어:
- 주식: 주식, 자동매매, 손절, 익절, RSI, 거래량
- 기업: 삼성전자, SK하이닉스, LG에너지솔루션, 현대차, NAVER, 카카오
- 시장: 코스피, 코스닥, 한국주식, 미국주식
- 분석: 기술분석, PER, PBR, ROE

### 3.4 API 키 미사용
- 사용자 지시: "API 키 없음"
- **DeepL API ❌ → 사전 매핑 방식 ✅**
- M2M100/NLLB-200 로컬 모델은 1~1.5GB 모델 다운로드 필요 (현실성 낮음)
- **사전 매핑이 가장 실용적**

### 3.5 결과
| 한글 쿼리 | 자동 번역 | PixelRAG 결과 |
|:----|:----|:----|
| 삼성전자 주가 분석 | Samsung Electronics 주가 analysis | ✅ Samsung_Electronics |
| 자동매매 전략 | algorithmic trading 전략 | ✅ Algorithmic_trading |
| 모멘텀 반전 매매 | momentum reversal trading | ✅ Island_reversal |
| KOSPI 기술분석 | KOSPI technical analysis | ✅ KOSPI |

---

## 4. Phase C: Neo4j 마인드맵

### 4.1 영상 차용
바이브랩스의 마인드맵 → 우리는 **Neo4j 그래프 + Browser URL**

### 4.2 POLE+O 엔티티 추출
| 타입 | 정규식 예시 | 추출 결과 |
|:----|:----|:----|
| Person | (이재용)\s*회장 | 이재용 |
| Object | \d{6}\s*종목, *전자/*증권 | 삼성전자 |
| Location | 한국, 미국, 서울 | 미국 |
| Event | \d{4}년\s*\d{1,2}월 | 2024 5 |

### 4.3 Neo4j 그래프 노드/관계
- **Document** → MENTIONS → **Entity** (Document → 4 Entity)
- **Entity** → CO_OCCURS → **Entity** (3 관계)

### 4.4 Browser URL 4종 자동 생성
1. **전체 그래프**: `MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 100`
2. **마인드맵**: `MATCH (d:Document)-[r:MENTIONS]->(e:Entity)`
3. **전략/백테스트**: `MATCH (s:Strategy)-[r:HAS_BACKTEST]->(b:Backtest)`
4. **매매 추적**: `MATCH (s:Stock)-[r:HAS_ORDER]->(o:Order)`

### 4.5 대시보드 임베드
`dashboard/STATUS.md`에 자동 추가:
- 노드/관계 카운트
- 라벨별 분포
- 4가지 Browser URL

---

## 5. 누적 Neo4j 상태

| 노드 | 개수 |
|:----|:---:|
| Stock | 108 |
| Order | 8 |
| Entity | 4 |
| Strategy | 2 |
| Document | 1 |
| Backtest | 1 |
| **합계** | **124** |

| 관계 | 개수 |
|:----|:---:|
| HAS_ORDER | 8 |
| MENTIONS | 4 |
| CO_OCCURS | 3 |
| HAS_BACKTEST | 1 |
| **합계** | **16** |

---

## 6. 향후 작업

| # | 작업 | 우선순위 |
|:-:|:----|:----:|
| 1 | **Neo4j Browser 접근성** (외부 노출 또는 reverse proxy) | 🟢 |
| 2 | **M2M100 로컬 모델** (사전 매핑 한계 보완) | 🟡 |
| 3 | **PDF OCR** (PyMuPDF + EasyOCR) | 🟡 |
| 4 | **마인드맵 자동 갱신** (crontab) | 🟢 |
| 5 | **POLE+O 정확도 개선** (LLM 활용) | 🟡 |

---

## 7. 핵심 명령

```bash
# 한글 OCR
cd /workspace/ki-ai-trader && .venv-3.12/bin/python3 src/data_sources/korean_ocr.py <image>

# 하이브리드 검색
cd /workspace/ki-ai-trader && .venv-3.12/bin/python3 src/crawlers/hybrid_search.py

# Neo4j 마인드맵 빌드
cd /workspace/ki-ai-trader && .venv-3.12/bin/python3 scripts/build_mindmap.py

# Neo4j Browser URL 임베드
/usr/bin/python3 /workspace/scripts/embed_neo4j_in_dashboard.py

# Neo4j Browser 열기
# http://localhost:7474/browser
```