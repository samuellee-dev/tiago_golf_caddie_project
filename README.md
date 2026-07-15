# ⛳ TIAGo Golf Caddie Project

TIAGo Dual과 MuJoCo를 기반으로 골프 캐디 로봇 시뮬레이션을 구현하는 프로젝트입니다.

현재 목표는 TIAGo Dual 로봇 모델을 이용하여 골프장 환경에서 이동, 골퍼 추종, 장애물 회피, 골프백 운반, 카메라 인식 기능을 단계적으로 구현하는 것입니다.

---

## 개발 환경

| 항목 | 내용 |
|---|---|
| 운영체제 | Windows |
| 컨테이너 | Docker Desktop / Docker Compose |
| Python | 3.11 |
| MuJoCo | 3.6.0 |
| 기반 로봇 | PAL Robotics TIAGo Dual |

---

## 프로젝트 구조

```text
tiago_golf_caddie_project/
├─ models/
│  ├─ custom/
│  │  └─ golf_caddie_tiago/
│  ├─ mujoco_menagerie/       # 별도 다운로드, GitHub 업로드 제외
│  └─ simple_test.xml
├─ src/
│  ├─ test_mujoco.py
│  ├─ test_tiago_load.py
│  └─ inspect_tiago_model.py
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## 최초 실행 방법

### 1. 프로젝트 저장소 복제

```powershell
git clone https://github.com/samuellee-dev/tiago_golf_caddie_project.git
cd tiago_golf_caddie_project
```

### 2. MuJoCo Menagerie 다운로드

`mujoco_menagerie`는 외부 저장소이므로 이 프로젝트의 GitHub에는 포함하지 않습니다.

프로젝트를 처음 내려받은 PC에서는 아래 명령을 한 번 실행해야 합니다.

```powershell
cd models
git clone https://github.com/google-deepmind/mujoco_menagerie.git
cd ..
```

다운로드 후 다음 경로가 존재해야 합니다.

```text
models/mujoco_menagerie/pal_tiago_dual
```

### 3. Docker 이미지 빌드

```powershell
docker compose build
```

### 4. Docker 컨테이너 실행

```powershell
docker compose up -d
```

### 5. 컨테이너 상태 확인

```powershell
docker compose ps
```

### 6. Docker 컨테이너 접속

```powershell
docker compose exec tiago-golf-caddie bash
```

---

## 실행 테스트

### MuJoCo 기본 공 낙하 테스트

Docker 컨테이너 내부에서 실행합니다.

```bash
python src/test_mujoco.py
```

`ball_z` 값이 점점 감소하면 정상입니다.

### TIAGo Dual 모델 로딩 테스트

Docker 컨테이너 내부에서 실행합니다.

```bash
python src/test_tiago_load.py
```

아래 메시지가 출력되면 정상입니다.

```text
[SUCCESS] pal_tiago_dual 모델 로딩 성공
[SUCCESS] 10 step 시뮬레이션 실행 성공
```

### TIAGo Dual 모델 이름 확인

```bash
python src/inspect_tiago_model.py
```

출력 결과를 파일로 저장하려면 다음 명령을 사용합니다.

```bash
python src/inspect_tiago_model.py > tiago_model_names.txt
```

---

## GitHub 작업 순서

노트북과 데스크톱에서 이어서 작업할 때는 항상 아래 순서를 사용합니다.

### 작업 시작 전

Windows PowerShell에서 실행합니다.

```powershell
git pull origin main
```

외부 모델 폴더가 없다면 다음 명령으로 다시 다운로드합니다.

```powershell
cd models
git clone https://github.com/google-deepmind/mujoco_menagerie.git
cd ..
```

### 작업 완료 후

먼저 변경 내용을 확인합니다.

```powershell
git status
```

변경 파일을 등록합니다.

```powershell
git add .
```

단계에 맞는 한국어 커밋을 작성합니다.

```powershell
git commit -m "3단계 완료: TIAGo Dual 모델 로딩"
```

GitHub에 업로드합니다.

```powershell
git push origin main
```

---

## 진행 현황

- [x] 2단계: Docker 및 MuJoCo 개발환경 구성
- [x] 3단계: TIAGo Dual 모델 다운로드 및 로딩
- [x] 4단계: 골프장 기본 환경 구성
- [ ] 5단계: 골프백 및 랙 모델 추가
- [ ] 6단계: Python 제어 루프 구현
- [ ] 7단계: 골퍼 추종 기능 구현
- [ ] 8단계: 장애물 감지 및 회피 기능 구현
- [ ] 9단계: 카메라 센서 추가
- [ ] 10단계: OpenCV 및 YOLO 연동
- [ ] 11단계: 행동 상태머신 구현
- [ ] 12단계: 코드 리팩토링 및 AI 개발도구 활용
- [ ] 13단계: 프로젝트 문서화 및 최종 정리

---

## 외부 모델 관리 원칙

`models/mujoco_menagerie/`는 Google DeepMind의 외부 저장소입니다.

다음 이유로 이 프로젝트의 GitHub에는 포함하지 않습니다.

- 저장소 용량 증가 방지
- Git 저장소 내부에 다른 Git 저장소가 포함되는 문제 방지
- 외부 원본과 사용자 작성 코드를 분리하여 관리
- 원본 TIAGo Dual 모델을 직접 수정하지 않기 위함

골프 캐디용 커스텀 모델은 다음 경로에서 관리합니다.

```text
models/custom/golf_caddie_tiago/
```

---

## 참고 저장소

MuJoCo Menagerie:

```text
https://github.com/google-deepmind/mujoco_menagerie
```