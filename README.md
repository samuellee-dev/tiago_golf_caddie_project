# ⛳ TIAGo Golf Caddie Project

TIAGo Dual과 MuJoCo를 기반으로 골프장 환경에서 이동, 골퍼 추종, 장애물 회피, 골프백 운반 및 카메라 인식 기능을 구현하는 교육용 로봇 시뮬레이션 프로젝트입니다.

## 개발 환경

| 항목 | 내용 |
|---|---|
| OS | Windows |
| 실행 환경 | Docker Desktop / Docker Compose |
| Python | 3.11 |
| MuJoCo | 3.6.0 |
| 기반 로봇 | PAL Robotics TIAGo Dual |

## 프로젝트 구조

```text
tiago_golf_caddie_project/
├─ models/
│  ├─ custom/golf_caddie_tiago/
│  │  ├─ golf_course_scene.xml
│  │  └─ pal_tiago_dual_golf/
│  │     ├─ golf_caddie_tiago_scene.xml
│  │     ├─ assets/
│  │     └─ tiago_dual_*.xml
│  ├─ mujoco_menagerie/          # 외부 원본, Git 제외
│  └─ simple_test.xml
├─ src/
│  ├─ test_mujoco.py
│  ├─ test_tiago_load.py
│  ├─ inspect_tiago_model.py
│  ├─ test_golf_course_load.py
│  └─ test_golf_caddie_scene.py
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ README.md
```

## 최초 실행

```powershell
git clone https://github.com/samuellee-dev/tiago_golf_caddie_project.git
cd tiago_golf_caddie_project

cd models
git clone https://github.com/google-deepmind/mujoco_menagerie.git
cd ..

docker compose build
docker compose up -d
docker compose exec tiago-golf-caddie bash
```

## 실행 테스트

Docker 컨테이너 안에서 실행합니다.

```bash
python src/test_mujoco.py
python src/test_tiago_load.py
python src/test_golf_course_load.py
python src/test_golf_caddie_scene.py
python src/test_golf_bag_attach.py
```

## 진행 현황

- [✅] 2단계: Docker 및 MuJoCo 개발 환경 구성
- [✅] 3단계: TIAGo Dual 모델 다운로드 및 로딩
- [✅] 4단계: 골프장 기본 환경 구성
- [✅] 5단계: TIAGo Dual과 골프장 환경 통합
- [✅] 6단계: 골프백 및 랙 모델 추가
- [ ] 7단계: Python 제어 루프 구현
- [ ] 8단계: 골퍼 추종 기능 구현
- [ ] 9단계: 장애물 감지 및 회피
- [ ] 10단계 이후: 카메라, 객체 인식 및 상태머신 구현

## GitHub 작업 순서

작업 시작 전:

```powershell
git pull origin main
```

작업 완료 후:

```powershell
git status
git add .
git commit -m "단계 및 작업 내용"
git push origin main
```

## 모델 관리

- `models/mujoco_menagerie/`: 외부 원본 저장소이므로 Git에서 제외
- `models/custom/golf_caddie_tiago/`: 프로젝트에서 사용하는 커스텀 모델이므로 Git에 포함
- 원본 TIAGo Dual 모델은 직접 수정하지 않음

## 참고

- MuJoCo Menagerie: https://github.com/google-deepmind/mujoco_menagerie