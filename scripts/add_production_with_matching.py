#!/usr/bin/env python3
"""
DB 매칭을 통한 생산 계획 추가 시스템
사용자가 불러주는 제품명을 DB 정식 제품명으로 변환 후 추가
"""

import requests
import json
import sys
from product_name_matcher import ProductNameMatcher

class ProductionAdderWithMatching:
    def __init__(self):
        self.base_url = "http://localhost:5176/api"
        self.matcher = ProductNameMatcher()
        
    def add_production_task(self, user_product_name: str, machine_number: str = "0", 
                           mold_number: str = None, color1: str = None, color2: str = None,
                           unit: str = "1", quantity: int = 1, date: str = "2026-04-19"):
        """
        DB 매칭을 통한 생산 계획 추가
        
        Args:
            user_product_name: 사용자가 불러주는 제품명
            machine_number: 기계번호 (기본값: 0)
            mold_number: 금형번호/제품번호 (제공되지 않으면 자동 검색)
            color1, color2: 색상 (제공되지 않으면 DB에서 가져옴)
            unit: 단위
            quantity: 수량
            date: 생산 날짜
        """
        print(f"\n{'='*60}")
        print(f"생산 계획 추가: '{user_product_name}'")
        print(f"{'='*60}")
        
        # 1. 제품명 매칭
        match_result = self.matcher.validate_and_correct(user_product_name, mold_number)
        
        if not match_result['matched']:
            print(f"❌ 추가 실패: {match_result['message']}")
            return False
        
        product_info = match_result['product_info']
        official_name = match_result['corrected']
        
        print(f"✅ 매칭 성공:")
        print(f"   원본: '{user_product_name}'")
        print(f"   정식: '{official_name}'")
        print(f"   제품번호: {product_info['id']}")
        print(f"   카테고리: {product_info['category']}")
        print(f"   색상: {product_info['color']}")
        
        # 2. 파라미터 설정
        # 금형번호가 제공되지 않으면 제품번호 사용
        if mold_number is None:
            mold_number = product_info['id']
        
        # 색상이 제공되지 않으면 DB 색상 사용
        if color1 is None and product_info['color']:
            color1 = product_info['color']
            color2 = product_info['color']  # 간단히 동일하게 설정
        
        if color2 is None:
            color2 = color1 if color1 else "WHITE 180"
        
        # 3. API 요청 데이터 준비
        task_data = {
            "date": date,
            "machineNumber": machine_number,
            "moldNumber": mold_number,
            "productName": official_name,
            "productNameEng": self._generate_english_name(official_name),
            "color1": color1 if color1 else "WHITE1",
            "color2": color2 if color2 else "WHITE 180",
            "unit": unit,
            "quantity": quantity,
            "unitQuantity": int(unit) if unit.isdigit() else 1,
            "total": int(unit) * quantity if unit.isdigit() else quantity,
            "status": "pending"
        }
        
        print(f"\n📋 추가 정보:")
        print(f"   기계번호: {machine_number}")
        print(f"   금형번호: {mold_number}")
        print(f"   색상: {color1} / {color2}")
        print(f"   수량: {quantity} (단위: {unit})")
        print(f"   날짜: {date}")
        
        # 4. API 호출
        return self._call_api(task_data)
    
    def _generate_english_name(self, korean_name: str) -> str:
        """한글 제품명을 영어 제품명으로 변환 (간단한 변환)"""
        # 실제로는 더 정교한 변환 필요
        mappings = {
            "모던": "Modern",
            "플러스": "Plus",
            "서랍": "Drawer",
            "프레임": "Frame",
            "앞판": "Front Panel",
            "로코스": "Locos",
            "화이트": "White",
            "블랑": "Blanc",
            "투명": "Transparent",
            "해피": "Happy",
            "바디": "Body",
            "이유": "EU",
            "와이드": "Wide",
            "슬림": "Slim",
            "맥스": "Max",
            "초대형": "Extra Large",
            "데크타일": "Deck Tiles",
            "핸들러": "Handler",
            "바스켓": "Basket",
        }
        
        result = korean_name
        for kr, en in mappings.items():
            if kr in result:
                result = result.replace(kr, en)
        
        return result
    
    def _call_api(self, task_data: dict) -> bool:
        """API 호출로 생산 계획 추가"""
        url = f"{self.base_url}/production-log"
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, json=task_data, headers=headers)
            
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('success'):
                    record_id = result.get('record', {}).get('id', '?')
                    print(f"\n🎉 생산 계획 추가 성공! (ID: {record_id})")
                    return True
                else:
                    print(f"\n❌ API 응답 실패: {result}")
                    return False
            else:
                print(f"\n❌ HTTP 오류 ({response.status_code}): {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"\n❌ API 호출 오류: {e}")
            return False
    
    def delete_test_tasks(self):
        """테스트 작업 삭제"""
        print("\n🧹 테스트 작업 정리 중...")
        
        # 오늘 날짜의 모든 작업 조회
        response = requests.get(f"{self.base_url}/production?date=2026-04-19")
        if response.status_code == 200:
            data = response.json()
            tasks = data.get('results', {}).get('latestData', [])
            
            deleted_count = 0
            for task in tasks:
                # 제품명이 비어있거나 '테스트'가 포함된 작업 삭제
                product_name = task.get('product_name', '')
                if not product_name or '테스트' in product_name:
                    task_id = task.get('id')
                    if task_id:
                        delete_url = f"{self.base_url}/production-log/{task_id}"
                        del_response = requests.delete(delete_url)
                        if del_response.status_code == 200:
                            deleted_count += 1
                            print(f"   삭제: ID {task_id} ({product_name})")
            
            print(f"✅ {deleted_count}개 테스트 작업 삭제 완료")
        else:
            print("❌ 작업 조회 실패")

def main():
    """메인 실행 함수"""
    adder = ProductionAdderWithMatching()
    
    print("=" * 60)
    print("VF 생산 계획 추가 시스템 (DB 매칭 버전)")
    print("=" * 60)
    
    # 테스트 작업 정리
    adder.delete_test_tasks()
    
    # 예제 추가
    examples = [
        {
            "name": "모던 플러스 1번",
            "machine": "0",
            "mold": "2",
            "quantity": 2,
            "unit": "1"
        },
        {
            "name": "로코스 M",
            "machine": "0", 
            "mold": "41",
            "quantity": 1,
            "unit": "4"
        },
        {
            "name": "블랑 투명",
            "machine": "3",
            "mold": "3",
            "quantity": 1,
            "unit": "1"
        }
    ]
    
    print("\n📋 예제 작업 추가:")
    for example in examples:
        success = adder.add_production_task(
            user_product_name=example["name"],
            machine_number=example["machine"],
            mold_number=example["mold"],
            quantity=example["quantity"],
            unit=example["unit"]
        )
        
        if not success:
            print(f"⚠️ '{example['name']}' 추가 실패, 다음 작업으로 넘어갑니다.")
    
    print("\n" + "=" * 60)
    print("✅ 작업 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()