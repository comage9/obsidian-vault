#!/usr/bin/env python3
"""
VF 생산 계획 제품명 매칭 시스템
사용자가 불러주는 제품명을 DB에 있는 정식 제품명으로 변환
"""

import json
import re
from typing import Dict, List, Optional, Tuple

class ProductNameMatcher:
    def __init__(self, product_db_path: str = "/home/comage/gbrain-docker/cleaned_data/vf_products_final.csv"):
        """제품명 매칭 시스템 초기화"""
        self.product_db_path = product_db_path
        self.product_db = self._load_product_database()
        self.alias_mapping = self._create_alias_mapping()
        
    def _load_product_database(self) -> List[Dict]:
        """제품 데이터베이스 로드"""
        products = []
        try:
            with open(self.product_db_path, 'r', encoding='utf-8') as f:
                # CSV 헤더: 인덱스,제품번호,,바코드,품번,제품명,카테고리,색상,단수,규격,재질,특징,로케이션
                for line_num, line in enumerate(f, 1):
                    if line_num == 1:
                        continue  # 헤더 스킵
                    
                    parts = line.strip().split(',')
                    if len(parts) >= 13:
                        product = {
                            'id': parts[1],  # 제품번호
                            'name': parts[5],  # 제품명
                            'category': parts[6],  # 카테고리
                            'color': parts[7],  # 색상
                            'size': parts[9] if len(parts) > 9 else '',  # 규격
                            'material': parts[10] if len(parts) > 10 else '',  # 재질
                            'feature': parts[11] if len(parts) > 11 else '',  # 특징
                        }
                        products.append(product)
            
            print(f"✅ 제품 데이터베이스 로드 완료: {len(products)}개 제품")
            return products
            
        except Exception as e:
            print(f"❌ 제품 데이터베이스 로드 실패: {e}")
            return []
    
    def _create_alias_mapping(self) -> Dict[str, str]:
        """별칭 매핑 생성"""
        mapping = {
            # 모던 플러스 시리즈
            '모던 플러스 1번': '뉴모던플러스 우드형상판 5단 화이트',
            '모던 플러스 2번': '모던플러스 내츄럴오크 우드상판형 5단',
            '모던 플러스 3번': '보노하우스 템바보드 서랍장 5단 화이트',
            '모던 플러스 4번': '보노하우스 라탄플러스 우드상판 서랍장 모던 화이트 6단 1개 562mm',
            '모던 플러스 5번': '보노하우스 템바보드 서랍장 5단 네이비',
            
            # 로코스 시리즈
            '로코스 M': '로코스 M',
            '로코스 L': '로코스 L',
            '로코스엠 화이트 캡': '로코스엠 화이트 캡',
            '로코스 M 여섯 개 화이트': '로코스 M 여섯 개 화이트',
            
            # 일반 제품
            '블랑 투명': '블랑 투명',
            '모던플러스 서랍': '모던플러스 서랍',
            '모던플러스 프레임': '신규 모던플러스 프레임',
            '모던플러스 앞판': '모던플러스 앞판',
            
            # 카테고리 기반
            '토이': '토이 바디',
            '해피': '해피 바디',
            '이유': '이유',
            '와이드': '와이드 서랍',
            '슬림': '슬림 서랍장 프레임 신규',
            '맥스': '맥스 서랍장 프레임',
            '초대형': '초대형 바디',
            '데크타일': '데크타일',
            '핸들러': '핸들러 바스켓 슬림(S)',
        }
        return mapping
    
    def find_product_by_id(self, product_id: str) -> Optional[Dict]:
        """제품번호로 제품 찾기"""
        for product in self.product_db:
            if product['id'] == product_id:
                return product
        return None
    
    def find_product_by_name(self, search_name: str) -> List[Dict]:
        """제품명으로 제품 검색 (유사도 기반)"""
        results = []
        search_name_lower = search_name.lower()
        
        for product in self.product_db:
            product_name_lower = product['name'].lower()
            
            # 정확한 매칭
            if search_name_lower == product_name_lower:
                results.append({'product': product, 'score': 100, 'match_type': 'exact'})
                continue
                
            # 부분 매칭
            if search_name_lower in product_name_lower:
                score = len(search_name_lower) / len(product_name_lower) * 100
                results.append({'product': product, 'score': score, 'match_type': 'partial'})
                continue
                
            # 키워드 매칭
            keywords = search_name_lower.split()
            matched_keywords = sum(1 for kw in keywords if kw in product_name_lower)
            if matched_keywords > 0:
                score = (matched_keywords / len(keywords)) * 100
                results.append({'product': product, 'score': score, 'match_type': 'keyword'})
        
        # 점수 기준 정렬
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def match_user_input(self, user_input: str) -> Tuple[Optional[Dict], str]:
        """
        사용자 입력을 정식 제품명으로 매칭
        
        Returns:
            Tuple[제품정보, 매칭된_정식_제품명]
        """
        # 1. 별칭 매핑 확인
        if user_input in self.alias_mapping:
            official_name = self.alias_mapping[user_input]
            print(f"📌 별칭 매핑: '{user_input}' → '{official_name}'")
            
            # 정식 제품명으로 검색
            results = self.find_product_by_name(official_name)
            if results:
                return results[0]['product'], official_name
        
        # 2. 직접 검색
        print(f"🔍 직접 검색: '{user_input}'")
        results = self.find_product_by_name(user_input)
        
        if results:
            best_match = results[0]
            print(f"   → 최적 매칭: '{best_match['product']['name']}' (점수: {best_match['score']:.1f}, 유형: {best_match['match_type']})")
            return best_match['product'], best_match['product']['name']
        
        # 3. 매칭 실패
        print(f"❌ 매칭 실패: '{user_input}'")
        return None, user_input
    
    def validate_and_correct(self, user_product_name: str, user_product_id: str = None) -> Dict:
        """
        사용자 제품명 검증 및 수정
        
        Returns:
            {
                'original': 원본_제품명,
                'corrected': 수정된_제품명,
                'product_info': 제품정보,
                'matched': 매칭성공여부,
                'message': 메시지
            }
        """
        product_info, official_name = self.match_user_input(user_product_name)
        
        result = {
            'original': user_product_name,
            'corrected': official_name,
            'product_info': product_info,
            'matched': product_info is not None,
            'message': ''
        }
        
        if product_info:
            # 제품번호 검증 (제공된 경우)
            if user_product_id and product_info['id'] != user_product_id:
                result['message'] = f"⚠️ 주의: 입력 제품번호({user_product_id})와 DB 제품번호({product_info['id']})가 다릅니다"
            else:
                result['message'] = f"✅ 매칭 성공: '{user_product_name}' → '{official_name}'"
        else:
            result['message'] = f"❌ 매칭 실패: '{user_product_name}'에 해당하는 제품을 찾을 수 없습니다"
            
        return result

def main():
    """테스트 실행"""
    print("=" * 60)
    print("VF 제품명 매칭 시스템 테스트")
    print("=" * 60)
    
    matcher = ProductNameMatcher()
    
    # 테스트 케이스
    test_cases = [
        "모던 플러스 1번",
        "로코스 M",
        "블랑 투명",
        "모던플러스 서랍",
        "존재하지 않는 제품",
        "토이",
        "해피 바디",
    ]
    
    for test in test_cases:
        print(f"\n테스트: '{test}'")
        result = matcher.validate_and_correct(test)
        
        if result['matched']:
            product = result['product_info']
            print(f"  제품번호: {product['id']}")
            print(f"  카테고리: {product['category']}")
            print(f"  색상: {product['color']}")
        else:
            print(f"  {result['message']}")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료")

if __name__ == "__main__":
    main()