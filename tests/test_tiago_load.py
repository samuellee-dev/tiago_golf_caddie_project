from pathlib import Path

import mujoco


def find_first_xml(model_dir: Path) -> Path:
    """
    pal_tiago_dual 폴더 안에서 우선순위에 따라 로딩할 XML을 찾는다.

    초보자용 설명:
    - MuJoCo 모델은 XML 파일에서 시작한다.
    - 현재 저장소에는 scene.xml 대신 scene_position.xml이 있다.
    - scene 파일은 로봇 + 바닥 + 조명 + 카메라를 포함할 가능성이 높다.
    """

    preferred_names = [
        "scene_position.xml",
        "scene_motor.xml",
        "scene_velocity.xml",
        "tiago_dual.xml",
    ]

    for name in preferred_names:
        candidate = model_dir / name

        if candidate.exists():
            return candidate

    xml_files = list(model_dir.glob("*.xml"))

    if not xml_files:
        raise FileNotFoundError(
            f"XML 파일을 찾을 수 없습니다: {model_dir}"
        )

    return xml_files[0]


def main():
    # ------------------------------------------------------------
    # 1. pal_tiago_dual 모델 폴더 지정
    # ------------------------------------------------------------
    model_dir = Path(
        "models/mujoco_menagerie/pal_tiago_dual"
    )

    if not model_dir.exists():
        raise FileNotFoundError(
            "pal_tiago_dual 폴더를 찾을 수 없습니다.\n"
            "먼저 다음 명령을 실행했는지 확인하세요:\n"
            "cd /workspace/models\n"
            "git clone "
            "https://github.com/google-deepmind/"
            "mujoco_menagerie.git"
        )

    # ------------------------------------------------------------
    # 2. 로딩할 XML 파일 선택
    # ------------------------------------------------------------
    xml_path = find_first_xml(model_dir)

    print(f"[INFO] 선택된 XML 파일: {xml_path}")

    # ------------------------------------------------------------
    # 3. MuJoCo 모델 로딩
    # ------------------------------------------------------------
    # 여기서 오류가 나면 보통 다음 중 하나입니다.
    # - include 경로 오류
    # - mesh 파일 경로 오류
    # - XML 문법 오류
    # - MuJoCo 버전 호환 문제
    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data = mujoco.MjData(model)

    # ------------------------------------------------------------
    # 4. 모델 기본 정보 출력
    # ------------------------------------------------------------
    print("[SUCCESS] pal_tiago_dual 모델 로딩 성공")
    print(f"nq = {model.nq} # generalized position 개수")
    print(f"nv = {model.nv} # generalized velocity 개수")
    print(f"nu = {model.nu} # actuator 개수")
    print(f"nbody = {model.nbody} # body 개수")
    print(f"njnt = {model.njnt} # joint 개수")
    print(f"ngeom = {model.ngeom} # geom 개수")
    print(f"nsensor = {model.nsensor} # sensor 개수")

    # ------------------------------------------------------------
    # 5. 몇 스텝 실행해 보기
    # ------------------------------------------------------------
    for step in range(10):
        mujoco.mj_step(model, data)

    print("[SUCCESS] 10 step 시뮬레이션 실행 성공")


if __name__ == "__main__":
    main()