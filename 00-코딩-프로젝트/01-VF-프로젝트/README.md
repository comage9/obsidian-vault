# VF 프로젝트 - 통합 관리 시스템

## 📁 프로젝트 구조

### 1. 생산 계획
- 생산 계획 관리 시스템
- Google Sheets 연동
- 실시간 데이터 동기화

### 2. 재고 관리  
- 재고 추적 및 관리
- 입출고 로그
- 재고 수준 모니터링

### 3. 모바일 UI
- 모바일 최적화 인터페이스
- 터치 기반 컨트롤
- 반응형 디자인

### 4. 색상 시스템
- 제품 색상 매핑
- 컬러 코드 관리
- 시각적 표시 시스템

### 5. 실제 소스 코드
- [source-code/](../source-code/) - 실제 VF 프로젝트 코드
- 프론트엔드: React + TypeScript
- 백엔드: Django + PostgreSQL

## 🔗 빠른 링크

### 문서
- [[생산 계획 문서]] - 생산-계획/
- [[재고 관리 문서]] - 재고-관리/
- [[모바일 UI 문서]] - 모바일-UI/
- [[색상 시스템 문서]] - 색상-시스템/

### 실제 코드
- [프론트엔드](../source-code/frontend/)
- [백엔드](../source-code/backend/)
- [컴포넌트](../source-code/components/)

### 웹 인터페이스
- **생산 계획**: http://localhost:5174/production
- **출고 관리**: http://localhost:5174/outbound
- **재고 관리**: http://localhost:5174/inventory

## 🛠️ 개발 환경

### 서버 실행
```bash
# 백엔드 (포트 5176)
cd /home/comage/coding/VF/backend
python manage.py runserver 5176

# 프론트엔드 (포트 5174)
cd /home/comage/coding/VF/frontend/client
npm run dev
```

### 데이터베이스
- **주 데이터베이스**: PostgreSQL (로컬)
- **Google Sheets**: 출고 데이터 연동
- **Windows 서버**: bonohouse.p-e.kr:5176

## 📊 시스템 상태
- **문서 수**: $(find "$VF_DOCS_DIR" -name "*.md" | wc -l)개
- **실제 코드**: $(find "$VF_SOURCE_DIR" -name "*.py" -o -name "*.ts" -o -name "*.tsx" | wc -l)개 파일
- **마지막 업데이트**: $(date +'%Y년 %m월 %d일 %H:%M')

> 이 시스템은 옵시디언 문서와 실제 코드를 통합 관리합니다.

## 🏭 창고 관리 시스템 (신규)

### 개요
생산동(A,B), 생산동 창고(C,D), 물류동 창고(E-J) 구분 시스템

### 주요 기능
1. **창고 구분**: A-J까지 10개 구역 관리
2. **자동 계산**: "로코스 8개 화이트 한 팔레트" → 32박스 자동 계산
3. **실시간 재고**: 매일 출고 수량에 따른 재고 변동 관리

### 문서
- [[창고 관리 시스템 설계]] - 상세 설계 문서
- [[재고 계산 규칙]] - 제품별 변환 규칙
- [[창고 위치 관리]] - A-J 구역 상세 정보

### 개발 상태
- ✅ 설계 완료
- ⏳ 개발 진행 중
- 🔜 테스트 예정

EOF && echo "✅ 창고 관리 시스템 문서 추가 완료"
