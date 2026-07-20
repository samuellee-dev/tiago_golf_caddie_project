import numpy as np

from behavior.caddie_state_machine import (
    CaddieContext,
    CaddieState,
    CaddieStateMachine,
)


def make_context(
    start_follow: bool = True,
    return_home: bool = False,
    emergency_stop: bool = False,
    distance_to_golfer: float = 2.0,
    nearest_obstacle_distance: float = 10.0,
) -> CaddieContext:
    robot_xy = np.array(
        [
            0.0,
            -7.0,
        ]
    )

    golfer_xy = np.array(
        [
            0.0,
            -5.0,
        ]
    )

    home_xy = np.array(
        [
            0.0,
            -7.0,
        ]
    )

    return CaddieContext(
        start_follow=start_follow,
        return_home=return_home,
        emergency_stop=emergency_stop,
        robot_xy=robot_xy,
        golfer_xy=golfer_xy,
        home_xy=home_xy,
        distance_to_golfer=distance_to_golfer,
        nearest_obstacle_name=None,
        nearest_obstacle_distance=(
            nearest_obstacle_distance
        ),
        nearest_obstacle_xy=None,
        desired_distance=1.5,
        tolerance=0.2,
        safety_radius=1.0,
    )


def main() -> None:
    state_machine = CaddieStateMachine()

    print(
        f"initial state = "
        f"{state_machine.state}"
    )

    # ------------------------------------------------------------
    # 1. IDLE → FOLLOW
    # ------------------------------------------------------------
    state = state_machine.update(
        make_context(
            start_follow=True,
            distance_to_golfer=2.0,
        )
    )

    print(
        f"after start_follow = "
        f"{state}"
    )

    assert state == CaddieState.FOLLOW

    # ------------------------------------------------------------
    # 2. FOLLOW → STOP
    # ------------------------------------------------------------
    state = state_machine.update(
        make_context(
            distance_to_golfer=1.5,
        )
    )

    print(
        f"after proper distance = "
        f"{state}"
    )

    assert state == CaddieState.STOP

    # ------------------------------------------------------------
    # 3. STOP → FOLLOW
    # ------------------------------------------------------------
    state = state_machine.update(
        make_context(
            distance_to_golfer=2.2,
        )
    )

    print(
        f"after golfer far = "
        f"{state}"
    )

    assert state == CaddieState.FOLLOW

    # ------------------------------------------------------------
    # 4. FOLLOW → AVOID
    # ------------------------------------------------------------
    state = state_machine.update(
        make_context(
            distance_to_golfer=2.2,
            nearest_obstacle_distance=0.7,
        )
    )

    print(
        f"after obstacle close = "
        f"{state}"
    )

    assert state == CaddieState.AVOID

    # ------------------------------------------------------------
    # 5. AVOID → FOLLOW
    # ------------------------------------------------------------
    state = state_machine.update(
        make_context(
            distance_to_golfer=2.2,
            nearest_obstacle_distance=2.0,
        )
    )

    print(
        f"after obstacle cleared = "
        f"{state}"
    )

    assert state == CaddieState.FOLLOW

    # ------------------------------------------------------------
    # 6. FOLLOW → EMERGENCY_STOP
    # ------------------------------------------------------------
    state = state_machine.update(
        make_context(
            emergency_stop=True,
        )
    )

    print(
        f"after emergency = "
        f"{state}"
    )

    assert state == CaddieState.EMERGENCY_STOP

    print(
        "[SUCCESS] 상태머신 단독 테스트 성공"
    )


if __name__ == "__main__":
    main()