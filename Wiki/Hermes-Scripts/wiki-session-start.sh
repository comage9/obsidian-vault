#!/bin/bash
# Session Summary to Wiki Script
# 현재 세션의 작업 내용을 Raw 폴더에 저장

VAULT="/home/comage/obsidian-vault/06-Wiki-시스템"
RAW="$VAULT/Raw"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
DATE=$(date '+%Y-%m-%d')
FILENAME="$RAW/${DATE}-세션로그.md"

# 세션 정보를 수집
cat > "$FILENAME" << EOF
# $DATE 세션 작업 기록

## 작업 시간
$TIMESTAMP

## 주요 작업 내용

<!-- 이 섹션은 세션 중에 채워집니다 -->

## 결정사항

<!-- 세션 중 결정된 사항들을 기록 -->

## 다음 작업

<!-- 세션 종료 시 확인해야 할 항목 -->

## 사용된 도구/스킬

- 

## 참고 사항

EOF

echo "✅ 세션 로그 파일 생성 완료: $FILENAME"
echo "$FILENAME"
