FROM python:3.11-slim

# ------------------------------------------------------------
# 1. 기본 시스템 패키지 설치
# ------------------------------------------------------------
# MuJoCo viewer, OpenCV, GLFW 실행에 필요한 라이브러리 설치
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    libgl1 \
    libglib2.0-0 \
    libglfw3 \
    libglew2.2 \
    libosmesa6 \
    libxrender1 \
    libxext6 \
    libsm6 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 2. 작업 디렉터리 생성
# ------------------------------------------------------------
WORKDIR /workspace

# ------------------------------------------------------------
# 3. Python 패키지 설치
# ------------------------------------------------------------
COPY requirements.txt /workspace/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# ------------------------------------------------------------
# 4. 기본 실행 명령
# ------------------------------------------------------------
CMD ["bash"]