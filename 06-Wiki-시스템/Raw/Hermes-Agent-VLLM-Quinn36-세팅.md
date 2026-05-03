# Hermes Agent + Quinn 3.6 27B + VLLM 세팅 가이드

원본 영상: https://youtu.be/kB9a5nXCwkA
날짜: 2026-05-04
채널: Geeky Needs

## 핵심 요약

로컬 AI 에이전트( Hermes Agent )를 Quinn 3.6 27B 모델과 VLLM으로 구동하는 전체 과정. VLLM 서빙 설정과 Hermes Agent 활용법 중심.

---

## 인프라 구성

### 하드웨어
- **머신:** 8GPU rig (RTX 4090 x2, RTX 3090 x2)
- **GPU 구성:** Device 0, 3, 4, 5 (각 x16带宽)
- **CUDA VISIBLE DEVICES:** 0, 3, 4, 5 (총 6GPU — 나머지는 VM용)
- **VM:** Llama.cpp용으로 별도 GPU 할당

### 소프트웨어
- **Proxmox** (가상화 플랫폼)
- **Lexi containers** + VM 혼합 구성
- **VLLM** 서빙 (Quinn 3.6 27B)
- **Hermes Agent** (vLLM 연결)

---

## VLLM 설정 (핵심)

### 추천 파라미터

```bash
# 모델
--model Quinn36-27B
--host 0.0.0.0
--port 9876

# GPU
--gpu-memory-utilization 0.9      # 0.92도 가능하나 0.9가 안정
--tensor-parallel-size 4           # 4 GPU 사용 (expert parallel 아님)

# 메모리/캐시
--mm-processor-cache-type shm
--enable-chunk-prefill
--enable-prefix-caching
--mamba-cache-mode align

# 컨텍스트
--max-model-length 131072          # 128K 컨텍스트

# 추론
--max-number-batch-tokens 8192     # 대용량 문서 인제스트에 최적
--max-number-sequences 4            # 본인 + 아내 + 서브에이전트 병렬

# 툴콜
--enable-auto-tool-choice
--tool-call-parser Quinn3Coder
--reasoning-parser Quinn3
```

### ⚠️ 주의할 설정

#### `preserve-thinking: false` (중요)

모델 카드에서는 `enable-thinking: true`를 권장하지만, **Hermes Agent 활용 시 `preserve-thinking`은 false로 설정해야 함.**

**이유:**
- `preserve-thinking: true` → 에이전트	harness에서 **결과大幅 악화**
- Hermes Agent 사용 시 반드시 `preserve-thinking` 제거 또는 false로 설정

#### `expandable-segments: true` (PCIe GPU)

PCIe GPU 사용 시 `expandable-segments true`는 나쁜 선택이 아님.

---

## Hermes Agent 활용

### 멀티 에이전트 구성
- **본인 Hermes Agent** — 별도 VM/컨테이너
- **아내 Hermes Agent** — 별도 VM/컨테이너
- 관심사, 방향 분리 → 병렬 리서치 가능

### CLI 원격 접속
- SSH로 81번 포트 → DSP의 Hermes Agent 인스턴스에 원격 접속
- RAM: 16GB (충분)
- CPU 코어: 8코어 (2코어 fully utilized 확인)
- SSD 할당: 비교적 작게 해도 무방 (파일 저장 용도만)

### Git Service的重要性
- **타임키핑** (타임라인 추적, 커밋 히스토리)
- 에이전트 작업의 타임스탬프 추적
- `commithistories`로 작업 이력 추적

---

## Quinn 3.6 27B 모델 특징

- **VLLM 서빙 시:** 풀 3.627B 파라미터 제공
- **토큰:** 128K 컨텍스트
- **장점:** 로컬에서 훌륭한 퍼포먼스 + 최고의 툴콜 능력
- **추론 파서:** Quinn3 (thinking 모드)

---

## 환경 변수 (VLLM용)

```bash
CUDA_VISIBLE_DEVICES=0,3,4,5
```

---

## 관련 링크

- Hermes Agent 문서: https://hermes-agent.nousresearch.com/docs
- VLLM 문서: https://docs.vllm.ai
- Quinn 모델: https://openrouter.ai/models?search=quinn

---

## 태그

#HermesAgent #VLLM #Quinn3 #로컬AI #Proxmox #AI에이전트
