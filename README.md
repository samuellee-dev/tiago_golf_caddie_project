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
│  ├─ custom/
│  │  └─ golf_caddie_tiago/
│  │     ├─ golf_course_scene.xml
│  │     └─ pal_tiago_dual_golf/
│  │        ├─ golf_caddie_tiago_scene.xml
│  │        ├─ assets/
│  │        └─ tiago_dual_*.xml
│  │
│  ├─ mujoco_menagerie/          # 외부 원본 (Git 제외)
│  └─ simple_test.xml
│
├─ src/
│  ├─ controller/
│  │  ├─ base_controller.py
│  │  └─ target_controller.py
│  │
│  ├─ perception/
│  │  ├─ fake_golfer_tracker.py
│  │  └─ obstacle_detector.py
│  │
│  ├─ behavior/
│  │  ├─ follow_behavior.py
│  │  ├─ obstacle_avoidance.py
│  │  └─ caddie_state_machine.py
│  │
│  ├─ inspect_tiago_model.py
│  ├─ inspect_actuators.py
│  ├─ inspect_joints.py
│  │
│  ├─ test_mujoco.py
│  ├─ test_tiago_load.py
│  ├─ test_golf_course_load.py
│  ├─ test_golf_caddie_scene.py
│  ├─ test_golf_bag_attach.py
│  ├─ test_golf_bag_mounted.py
│  ├─ test_base_drive_actuator.py
│  ├─ test_direct_base_controller.py
│  ├─ test_follow_golfer.py
│  ├─ test_follow_with_obstacle_avoidance.py
│  ├─ test_follow_moving_golfer.py
│  ├─ test_caddie_state_machine_unit.py
│  └─ test_caddie_state_machine.py
│
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

---

## 실행 테스트

Docker 컨테이너 안(`/workspace`)에서 실행합니다.

```bash
# MuJoCo 설치 확인
python src/test_mujoco.py
# TIAGo Dual 모델 로딩
python src/test_tiago_load.py
# 골프장 환경 로딩
python src/test_golf_course_load.py
# TIAGo + 골프장 통합 Scene 로딩
python src/test_golf_caddie_scene.py
# 골프백 장착 확인
python src/test_golf_bag_attach.py
# 골프백 장착 Scene 확인
python src/test_golf_bag_mounted.py
# Actuator 목록 확인
python src/inspect_actuators.py
# Joint와 free joint 구조 확인
python src/inspect_joints.py
# 바퀴 velocity actuator를 이용한 베이스 이동 테스트
python src/test_base_drive_actuator.py
# DirectBaseController 목표 좌표 이동 테스트
PYTHONPATH=src python src/test_direct_base_controller.py
# golfer_target 기본 추종 테스트
PYTHONPATH=src python src/test_follow_golfer.py
# 장애물 감지 확인
PYTHONPATH=src python - <<'PY'
from pathlib import Path

import mujoco

from perception.obstacle_detector import (
    SimpleObstacleDetector,
)

xml_path = Path(
    "models/custom/golf_caddie_tiago/"
    "pal_tiago_dual_golf/"
    "golf_caddie_tiago_scene.xml"
)

model = mujoco.MjModel.from_xml_path(str(xml_path))
data = mujoco.MjData(model)

mujoco.mj_forward(model, data)

detector = SimpleObstacleDetector(
    model=model,
    obstacle_body_names=[
        "obstacle_tree_01",
        "obstacle_tree_02",
        "obstacle_marker_box",
    ],
)

robot_xy = [0.0, 0.0]

nearest = detector.find_nearest_obstacle(
    data=data,
    robot_xy=robot_xy,
)

print(nearest)
PY

# 골퍼 추종 + 장애물 회피 통합 테스트
PYTHONPATH=src python src/test_follow_with_obstacle_avoidance.py
# 움직이는 golfer_target 추종 테스트
PYTHONPATH=src python src/test_follow_moving_golfer.py
# 상태머신 단독 테스트
PYTHONPATH=src python src/test_caddie_state_machine_unit.py
# 상태머신 MuJoCo 통합 테스트
PYTHONPATH=src python src/test_caddie_state_machine.py
```

---

## 진행 현황

- [✅] 2단계: Docker 및 MuJoCo 개발 환경 구성
- [✅] 3단계: TIAGo Dual 모델 다운로드 및 로딩
- [✅] 4단계: 골프장 기본 환경 구성
- [✅] 5단계: TIAGo Dual과 골프장 환경 통합
- [✅] 6단계: 골프백 및 랙 모델 추가
- [✅] 7단계: TIAGo 베이스에 골프백 장착
- [✅] 8단계: TIAGo 베이스 이동 제어 구조 구현
- [✅] 9단계: 골퍼(Target) 기본 추종 알고리즘 구현
- [✅] 10단계: 장애물 감지 및 회피 구현
- [✅] 11단계: 캐디 로봇 상태머신 구현 및 MuJoCo 통합
- [ ] 12단계: (PDF 다음 단계)

---

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