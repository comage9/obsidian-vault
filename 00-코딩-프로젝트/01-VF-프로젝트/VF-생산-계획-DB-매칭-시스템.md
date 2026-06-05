# VF 생산 계획 DB 매칭 시스템

## 📅 작성일: 2026-04-19
## 📝 작성자: OpenClaw Assistant
## 🔄 버전: 1.0

---

## 🎯 시스템 개요

### 문제 인식
1. **사용자가 불러주는 제품명**과 **DB에 있는 정식 제품명**이 다를 수 있음
2. 테스트 작업이 시스템에 남아있을 수 있음
3. 일관된 제품명 사용 필요

### 해결 방안
1. **제품명 매칭 시스템** 구현
2. **테스트 작업 자동 정리**
3. **DB 기반 정식 제품명 사용**

---

## 🔧 시스템 구성

### 1. 주요 컴포넌트

#### A. `ProductNameMatcher` 클래스
- **기능**: 사용자 제품명 → DB 정식 제품명 변환
- **데이터소스**: `vf_products_final.csv` (845개 제품)
- **매칭 방식**:
  1. 별칭 매핑 (사전 정의)
  2. 직접 검색 (유사도 기반)
  3. 키워드 매칭

#### B. `ProductionAdderWithMatching` 클래스
- **기능**: 매칭된 제품명으로 생산 계획 추가
- **특징**:
  - 자동 색상 추출
  - 영어 제품명 생성
  - 테스트 작업 정리

### 2. 데이터 흐름
```
사용자 입력 → 제품명 매칭 → DB 검증 → API 호출 → 생산 계획 등록
      ↓            ↓           ↓          ↓           ↓
  "모던 플러스 1번" → 별칭매핑 → 제품번호2 → 정식제품명 → 시스템등록
```

---

## 📋 사용 방법

### 1. 기본 사용법
```python
from product_name_matcher import ProductNameMatcher

matcher = ProductNameMatcher()
result = matcher.validate_and_correct("모던 플러스 1번")

if result['matched']:
    print(f"정식 제품명: {result['corrected']}")
    print(f"제품정보: {result['product_info']}")
```

### 2. 생산 계획 추가
```python
from add_production_with_matching import ProductionAdderWithMatching

adder = ProductionAdderWithMatching()
success = adder.add_production_task(
    user_product_name="로코스 M",
    machine_number="0",
    mold_number="41",
    quantity=1,
    unit="4"
)
```

### 3. 테스트 작업 정리
```python
adder.delete_test_tasks()  # 제품명이 비어있거나 '테스트' 포함 작업 삭제
```

---

## 🗂️ 별칭 매핑 테이블

| 사용자 입력 | DB 정식 제품명 | 제품번호 |
|------------|----------------|----------|
| 모던 플러스 1번 | 뉴모던플러스 우드형상판 5단 화이트 | 2 |
| 모던 플러스 2번 | 모던플러스 내츄럴오크 우드상판형 5단 | 1 |
| 모던 플러스 3번 | 보노하우스 템바보드 서랍장 5단 화이트 | 3 |
| 모던 플러스 4번 | 보노하우스 라탄플러스 우드상판 서랍장 모던 화이트 6단 1개 562mm | 4 |
| 모던 플러스 5번 | 보노하우스 템바보드 서랍장 5단 네이비 | 5 |
| 로코스 M | 로코스 M | 161 |
| 블랑 투명 | 블랑 투명 | 637 |
| 모던플러스 서랍 | 모던플러스 서랍 | 7 |

---

## 🔍 매칭 알고리즘

### 1. 우선순위
1. **별칭 매핑** (사전 정의된 매핑)
2. **정확한 매칭** (완전 일치)
3. **부분 매칭** (문자열 포함)
4. **키워드 매칭** (단어별 검색)

### 2. 점수 계산
- **정확한 매칭**: 100점
- **부분 매칭**: (검색어길이 / 제품명길이) × 100
- **키워드 매칭**: (일치키워드수 / 전체키워드수) × 100

### 3. 매칭 결과
```python
{
    'original': '사용자 입력',
    'corrected': '정식 제품명',
    'product_info': {...},  # DB 제품정보
    'matched': True/False,
    'message': '상태 메시지'
}
```

---

## ⚙️ 시스템 설정

### 1. 데이터베이스 경로
```python
# 기본값: /home/comage/gbrain-docker/cleaned_data/vf_products_final.csv
matcher = ProductNameMatcher(product_db_path="경로")
```

### 2. API 설정
```python
# 기본값: http://localhost:5176/api
adder.base_url = "API_BASE_URL"
```

### 3. 기본값 설정
- **기계번호**: "0" (지정되지 않음)
- **색상**: DB에서 자동 추출
- **단위**: "1"
- **상태**: "pending"
- **날짜**: 오늘 날짜

---

## 🚀 실제 적용 예시

### 예시 1: 모던 플러스 추가
```bash
python3 add_production_with_matching.py
```

**출력:**
```
생산 계획 추가: '모던 플러스 1번'
별칭 매핑: '모던 플러스 1번' → '뉴모던플러스 우드형상판 5단 화이트'
매칭 성공: 제품번호 2, 색상 WHITE
생산 계획 추가 성공! (ID: 18725)
```

### 예시 2: 로코스 M 추가
```bash
python3 -c "
from add_production_with_matching import ProductionAdderWithMatching
adder = ProductionAdderWithMatching()
adder.add_production_task('로코스 M', machine_number='3', quantity=1, unit='4')
"
```

---

## 🔄 유지보수

### 1. 별칭 매핑 추가
```python
# product_name_matcher.py의 _create_alias_mapping 메서드 수정
mapping = {
    '새로운 별칭': 'DB 정식 제품명',
    # ... 기존 매핑
}
```

### 2. 데이터베이스 업데이트
- CSV 파일이 업데이트되면 시스템 자동 인식
- 새로운 제품 추가 시 별칭 매핑 필요

### 3. 매칭 알고리즘 개선
- 유사도 알고리즘 향상
- 카테고리 기반 검색 추가
- 색상 자동 매칭 개선

---

## 📊 성능 및 제한사항

### ✅ 장점
1. **일관성**: 항상 정식 제품명 사용
2. **자동화**: 색상, 영어명 자동 생성
3. **유연성**: 다양한 입력 형식 지원
4. **정리**: 테스트 작업 자동 삭제

### ⚠️ 제한사항
1. **DB 의존성**: CSV 파일 정확성 필요
2. **별칭 관리**: 새로운 별칭 수동 추가 필요
3. **색상 정확도**: DB 색상 정보에 의존

### 🔧 개선 필요사항
1. 실시간 DB 연동 (API 기반)
2. 머신러닝 기반 유사도 계산
3. 사용자 피드백 기반 매칭 학습

---

## 📞 문제 해결

### 1. 매칭 실패 시
```python
# 수동 검색
results = matcher.find_product_by_name("검색어")
for r in results[:3]:  # 상위 3개
    print(f"{r['product']['name']} (점수: {r['score']:.1f})")
```

### 2. API 오류 시
```bash
# 서버 상태 확인
curl http://localhost:5176/api/health
```

### 3. 데이터 오류 시
```bash
# CSV 파일 확인
head -5 /home/comage/gbrain-docker/cleaned_data/vf_products_final.csv
```

---

## 🎯 결론

### 핵심 가치
1. **정확성**: DB 기반 정식 제품명 사용
2. **효율성**: 자동 매칭으로 수작업 감소
3. **일관성**: 시스템 전체 통일된 제품명
4. **관리성**: 테스트 작업 자동 정리

### 적용 범위
- VF 생산 계획 시스템
- 재고 관리 시스템
- 주문 처리 시스템
- 보고서 생성 시스템

*이 시스템은 지속적인 개선이 필요하며, 사용자 피드백을 통해 발전해 나갈 것입니다.*