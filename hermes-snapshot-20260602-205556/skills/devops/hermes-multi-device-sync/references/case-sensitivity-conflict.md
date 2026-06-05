# Syncthing: Linux ↔ Windows 간 대소문자 충돌 문제

## 증상

동기화 실패, 오류 로그:
```
WRN Failed to sync ... remote "backup\obsidian-vault\wiki" uses different upper or lowercase 
characters than local "backup\obsidian-vault\Wiki"
```

## 원인

- Linux (ext4): 대소문자 구분 — `wiki/`와 `Wiki/`는 다른 폴더
- Windows (NTFS): 대소문자 미구분 — `wiki/`와 `Wiki/`를 같은 폴더로 인식
- Syncthing이 양쪽 폴더를 동기화하려다 충돌 감지

## 해결

**Linux 측에서 실행:**

```bash
# 1. 대소문자 중복 폴더 찾기
find ~/obsidian-vault/ -maxdepth 3 -type d | sort | uniq -i -d

# 2. 결정: 어떤 케이스를 유지할지 선택
# 주요 데이터가 있는 쪽(Wiki/ 대문자 W) 유지

# 3. 소문자 폴더 내용을 대문자 폴더로 병합
mv ~/obsidian-vault/wiki/sources ~/obsidian-vault/Wiki/sources
rm -rf ~/obsidian-vault/wiki

# 4. backup/ 디렉토리 등 구 데이터가 있는 경우 전체 삭제
rm -rf ~/obsidian-vault/backup/
```

## 예방

- Obsidian vault 폴더명은 일관되게 `Wiki`(대문자 W) 사용
- Linux에서 `mkdir wiki`와 `mkdir Wiki`를 실수로 만들지 않도록 주의
- `backup/` 디렉토리는 `.stignore`에 추가 (백업 데이터가 대소문자 혼란 유발)
