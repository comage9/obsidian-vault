# 키 프로젝트 - 키움증권 AI 트레이딩 시스템

## 📁 프로젝트 구조

### 1. API 연동
- 키움증권 OpenAPI 연결
- 실시간 시세 데이터 수신
- 주문 및 계좌 관리

### 2. AI 모델
- 머신러닝/딥러닝 모델
- 예측 알고리즘
- 모델 학습 및 평가

### 3. 백테스팅
- 역사적 데이터 기반 테스트
- 전략 성능 평가
- 리스크 관리

### 4. 전략 개발
- 매매 전략 설계
- 신호 생성 시스템
- 포트폴리오 관리

### 5. 데이터 관리
- 시세 데이터 저장
- 전처리 및 정제
- 데이터 파이프라인

### 6. 실제 소스 코드
- [source-code/](../source-code/) - 실제 키 프로젝트 코드
- Python 기반 트레이딩 시스템
- 키움증권 API 통합

## 🔗 빠른 링크

### 문서
- [[API 연동 문서]] - API-연동/
- [[AI 모델 문서]] - AI-모델/
- [[백테스팅 문서]] - 백테스팅/
- [[전략 개발 문서]] - 전략-개발/
- [[데이터 관리 문서]] - 데이터-관리/

### 실제 코드
- [소스 코드](../source-code/)
- [설정 파일](../source-code/config/)
- [데이터 스크립트](../source-code/data/)

## 🛠️ 개발 환경

### 필수 패키지
```bash
# 키움증권 API
pip install pykiwoom

# 데이터 분석
pip install pandas numpy matplotlib

# 머신러닝
pip install scikit-learn tensorflow torch
```

### 실행 방법
```bash
cd /home/comage/coding/ki-ai-trader

# 데이터 수집
python data_collector.py

# 모델 학습
python train_model.py

# 트레이딩 실행
python trading_bot.py
```

## 📊 시스템 정보
- **문서 수**: $(find "$KI_DOCS_DIR" -name "*.md" | wc -l)개
- **실제 코드**: $(find "$KI_SOURCE_DIR" -name "*.py" | wc -l)개 Python 파일
- **마지막 업데이트**: $(date +'%Y년 %m월 %d일 %H:%M')

## ⚠️ 주의사항
1. **API 키 관리**: 키움증권 API 키는 안전하게 보관
2. **실제 거래**: 백테스팅 완료 후 실제 거래 진행
3. **리스크 관리**: 손실 제한 설정 필수

> 이 시스템은 키움증권 API 기반 AI 자동 매매 시스템입니다.
