# ⛳ TIAGo Golf Caddie Project

<p align="center">
    <img src="docs/images/tiago_golf_caddie_banner.png" width="100%">
</p>

<h2 align="center">
Autonomous Golf Caddie Robot Simulation
</h2>

<p align="center">
MuJoCo • TIAGo Dual • OpenCV • Python
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue)
![MuJoCo](https://img.shields.io/badge/MuJoCo-3.6.0-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Portfolio](https://img.shields.io/badge/Portfolio-Robotics-success)

</p>

---

# 📌 Overview

**TIAGo Golf Caddie Project**는 PAL Robotics의 **TIAGo Dual** 모델을 기반으로 **MuJoCo 시뮬레이션 환경**에서 자율 골프 캐디 로봇을 구현한 Robotics Portfolio Project입니다.

본 프로젝트는 실제 TIAGo 로봇을 사용하지 않고 **MuJoCo 기반 시뮬레이션**만을 대상으로 개발하였습니다.

모바일 서비스 로봇에서 사용되는 **Perception → Behavior → Controller** 구조를 기반으로 다음 기능들을 하나의 시스템으로 통합하였습니다.

- Autonomous Golfer Following
- Obstacle Avoidance
- Camera Rendering
- OpenCV Vision
- Camera Targeting
- Heading Controller
- Visual Servoing
- Vision-based State Machine
- Final Autonomous Demo

---

# ✨ Key Features

## 🤖 Robot

- TIAGo Dual Integration
- Mobile Robot Base
- Golf Bag Rack
- Golf Bag Mount

### 🚶 Navigation

- Golfer Following
- Safe Following Distance
- Obstacle Avoidance
- Target Controller

### 👀 Computer Vision

- Robot Front Camera
- MuJoCo Offscreen Rendering
- OpenCV Color Detection
- Golf Ball Detection
- Flag Detection
- Camera Targeting

### 🧠 Robot Intelligence

- Heading Controller
- Visual Servo Controller
- State Machine
- Vision State Machine

### 🚀 Integration

- Autonomous Demo
- Vision + Motion Integration
- Complete Simulation Pipeline

---

# 🏗 System Architecture

```text
                 MuJoCo Simulation

                         │

     ┌───────────────────┴───────────────────┐

     ▼                                       ▼

TIAGo Dual                          Golf Environment

                         │

                         ▼

====================================================

               Perception Layer

====================================================

FakeGolferTracker

ObstacleDetector

OpenCV Detection

CameraTargeting

                         │

                         ▼

====================================================

                Behavior Layer

====================================================

FollowBehavior

ObstacleAvoidance

CaddieStateMachine

                         │

                         ▼

====================================================

               Controller Layer

====================================================

DirectBaseController

HeadingController

VisualServoController

                         │

                         ▼

====================================================

         Autonomous Golf Caddie Robot
```

본 프로젝트는 **Perception → Behavior → Controller** 계층 구조를 기반으로 구현하였으며, 실제 모바일 서비스 로봇 소프트웨어의 구조를 참고하여 설계하였습니다.

---

# 🛠 Tech Stack

| Category | Technology |
|-----------|------------|
| Robot | PAL Robotics TIAGo Dual |
| Simulation | MuJoCo 3.6.0 |
| Programming | Python 3.11 |
| Vision | OpenCV |
| Rendering | MuJoCo Offscreen Rendering |
| Container | Docker / Docker Compose |
| Version Control | Git / GitHub |
| Platform | Windows |

---

# 📁 Project Structure

```text
tiago_golf_caddie_project/

├── docs/
│   └── images/
│
├── models/
│   ├── custom/
│   └── mujoco_menagerie/
│
├── src/
│   ├── behavior/
│   ├── controller/
│   ├── perception/
│   ├── vision/
│   └── main.py
│
├── tests/
├── scripts/
├── outputs/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🚀 Quick Start

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

# 📈 Development Journey

This project was developed incrementally through functional milestones rather than implementing all features at once.

Each stage was independently verified before proceeding to the next stage, ensuring stable integration throughout the development process.

| Stage | Description |
|--------|-------------|
| **Stage 1** | Development Environment (Docker, MuJoCo, TIAGo Dual) |
| **Stage 2** | Custom Golf Course & Golf Bag Integration |
| **Stage 3** | Mobile Robot Motion Control |
| **Stage 4** | Golfer Following & Obstacle Avoidance |
| **Stage 5** | Camera Rendering & OpenCV Vision |
| **Stage 6** | Heading Controller & Visual Servoing |
| **Stage 7** | Vision-based State Machine Integration |
| **Stage 8** | Project Refinement & Portfolio Documentation |

The project was completed by continuously integrating, testing, and validating each subsystem before moving on to the next development stage.

---

# 🎯 Implemented Features

- ✅ TIAGo Dual Simulation
- ✅ Custom Golf Course
- ✅ Golf Bag Mount
- ✅ Golfer Following
- ✅ Obstacle Avoidance
- ✅ Camera Rendering
- ✅ OpenCV Vision
- ✅ Camera Targeting
- ✅ Heading Controller
- ✅ Visual Servoing
- ✅ Vision State Machine
- ✅ Autonomous Demo

---

# 🔮 Future Work

현재 프로젝트는 **MuJoCo 기반 시뮬레이션**까지 구현하였습니다.

향후에는 다음과 같은 방향으로 확장할 수 있습니다.

```text
MuJoCo

    │

    ▼

ROS2

    │

    ▼

Gazebo

    │

    ▼

Real TIAGo Robot
```

Planned Extensions

- ROS2 Integration
- Navigation2
- SLAM
- YOLO Detection
- Manipulator Motion Planning
- Pick & Place
- Real Camera
- Real LiDAR

---

# 📚 References

- MuJoCo
- MuJoCo Menagerie
- PAL Robotics TIAGo
- OpenCV
- Docker
- Python

---

# 📄 License

This project was developed for educational purposes and as a robotics portfolio.

External assets and models follow the licenses of their respective projects.

---

# 📝 Project Summary

This project demonstrates the implementation of an **Autonomous Golf Caddie Robot** using the **PAL Robotics TIAGo Dual** model in a **MuJoCo simulation environment**.

The project integrates multiple robotics software components into a single autonomous system, including:

- Mobile Robot Control
- Computer Vision
- Autonomous Navigation
- Behavior Planning
- State Machine
- Visual Servoing

The overall software architecture follows a **Perception → Behavior → Controller** pipeline, a common design pattern used in modern mobile robotics systems.

Although this project focuses on simulation, the architecture has been designed to be extensible toward ROS2, Gazebo, and real robot deployment in future work.

---

<p align="center">

⭐ If you found this project interesting, consider giving it a star on GitHub.

</p>