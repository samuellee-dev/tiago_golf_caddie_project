import time
from pathlib import Path

import mujoco


def main():
    # ------------------------------------------------------------
    # 1. XML 모델 경로 설정
    # ------------------------------------------------------------
    # /workspace 기준으로 simple_test.xml을 찾는다.
    model_path = Path("models/simple_test.xml")

    if not model_path.exists():
        raise FileNotFoundError(
            f"모델 파일을 찾을 수 없습니다: {model_path}"
        )

    # ------------------------------------------------------------
    # 2. MuJoCo 모델 로딩
    # ------------------------------------------------------------
    model = mujoco.MjModel.from_xml_path(str(model_path))
    data = mujoco.MjData(model)

    # ------------------------------------------------------------
    # 3. 시뮬레이션 반복 실행
    # ------------------------------------------------------------
    # viewer 없이 물리 엔진만 실행한다.
    for step in range(300):

        mujoco.mj_step(model, data)

        if step % 30 == 0:

            ball_z = data.qpos[2]

            print(f"step={step:03d}, ball_z={ball_z:.4f}")

        time.sleep(0.01)


if __name__ == "__main__":
    main()