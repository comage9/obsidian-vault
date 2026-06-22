# Windows Hermes Gateway: Python AST Recursion Error

## 증상

```
PS E:\hermes-backup> hermes gateway restart
✓ Gateway stopped
⚠️ Launched gateway via Scheduled Task 'Hermes_Gateway', but no process detected after 6s.
```

Gateway 로그(`%USERPROFILE%\AppData\Local\hermes\logs\gateway.log`):

```
SystemError: AST constructor recursion depth mismatch (before=120, after=172)
  File "C:\Users\kis\AppData\Local\hermes\hermes-agent\tools\registry.py", line 50, in _module_registers_tools
    tree = ast.parse(source, filename=str(module_path))
  File "C:\Users\kis\AppData\Local\Python\Python311\Lib\ast.py", line 50, in parse
    return compile(source, filename, mode, flags,
```

## 원인

Python 3.11의 `ast.parse()`가 깊이 중첩된 파이썬 파일(특히 `node_modules/`와 `.venv/`가 섞인 프로젝트)을 파싱할 때 기본 재귀 한도(1000)를 초과.

실제 크래시: Hermes가 시작 시 모든 `tools/*.py` 파일을 `ast.parse()`로 검사하는 과정에서 너무 깊은 AST를 만나 충돌.

## 해결

### 임시 (PowerShell 세션):
```powershell
$env:PYTHONRECURSIONLIMIT=3000
hermes gateway restart
```

### 영구:

`.env` 파일(`%USERPROFILE%\.hermes\.env`)에 추가:
```env
PYTHONRECURSIONLIMIT=3000
```

또는 시스템 환경 변수:
```powershell
[System.Environment]::SetEnvironmentVariable('PYTHONRECURSIONLIMIT','3000','User')
```

## 확인

```powershell
hermes gateway status
# → Running 으로 표시되어야 함
```
