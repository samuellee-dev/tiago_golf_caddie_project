from dataclasses import dataclass
from enum import Enum, auto

import numpy as np


class CaddieState(Enum):
    """
    골프 캐디 로봇의 행동 상태.

    Enum을 쓰는 이유:
    - 문자열 오타를 줄일 수 있다.
    - 상태 목록을 명확히 관리할 수 있다.
    - 로그 출력과 디버깅이 쉬워진다.
    """

    IDLE = auto()
    FOLLOW = auto()
    AVOID = auto()
    STOP = auto()
    TOO_CLOSE = auto()
    RETURN_HOME = auto()
    EMERGENCY_STOP = auto()


@dataclass
class CaddieContext:
    """
    상태 판단에 필요한 현재 상황 정보.

    상태머신은 직접 MuJoCo를 알 필요가 없다.
    대신 현재 거리, 장애물 여부, 명령 여부 같은
    추상화된 정보만 받는다.
    """

    start_follow: bool
    return_home: bool
    emergency_stop: bool

    robot_xy: np.ndarray
    golfer_xy: np.ndarray
    home_xy: np.ndarray

    distance_to_golfer: float

    nearest_obstacle_name: str | None
    nearest_obstacle_distance: float
    nearest_obstacle_xy: np.ndarray | None

    desired_distance: float
    tolerance: float
    safety_radius: float

    home_tolerance: float = 0.2


class CaddieStateMachine:
    """
    골프 캐디 로봇 상태머신.

    이 클래스는 어떤 상태로 전환할지만 판단한다.
    실제 이동은 외부 controller가 수행한다.

    역할 분리:
    - StateMachine: 상태 판단
    - Controller: 이동 실행
    - Perception: 위치와 장애물 정보 수집
    """

    def __init__(self):
        self.state = CaddieState.IDLE
        self.previous_state = None
        self.transition_count = 0

    def transition_to(
        self,
        new_state: CaddieState,
    ) -> None:
        """
        현재 상태를 새로운 상태로 변경한다.
        """

        if new_state != self.state:
            self.previous_state = self.state
            self.state = new_state
            self.transition_count += 1

    def update(
        self,
        context: CaddieContext,
    ) -> CaddieState:
        """
        현재 context를 보고 다음 상태를 결정한다.
        """

        # --------------------------------------------------------
        # 1. 긴급 정지는 항상 최우선
        # --------------------------------------------------------
        if context.emergency_stop:
            self.transition_to(
                CaddieState.EMERGENCY_STOP
            )

            return self.state

        # --------------------------------------------------------
        # 2. 복귀 명령
        # --------------------------------------------------------
        if context.return_home:
            self.transition_to(
                CaddieState.RETURN_HOME
            )

            return self.state

        # --------------------------------------------------------
        # 3. 현재 상태별 전환 규칙
        # --------------------------------------------------------
        if self.state == CaddieState.IDLE:
            return self._update_idle(context)

        if self.state == CaddieState.FOLLOW:
            return self._update_follow(context)

        if self.state == CaddieState.AVOID:
            return self._update_avoid(context)

        if self.state == CaddieState.STOP:
            return self._update_stop(context)

        if self.state == CaddieState.TOO_CLOSE:
            return self._update_too_close(context)

        if self.state == CaddieState.RETURN_HOME:
            return self._update_return_home(context)

        if self.state == CaddieState.EMERGENCY_STOP:
            return self.state

        return self.state

    def _is_obstacle_too_close(
        self,
        context: CaddieContext,
    ) -> bool:
        """
        최근접 장애물이 safety_radius 안에 있는지 판단한다.
        """

        return (
            context.nearest_obstacle_distance
            < context.safety_radius
        )

    def _distance_min(
        self,
        context: CaddieContext,
    ) -> float:
        """
        골퍼와 유지해야 할 최소 거리.
        """

        return (
            context.desired_distance
            - context.tolerance
        )

    def _distance_max(
        self,
        context: CaddieContext,
    ) -> float:
        """
        골퍼와 유지해야 할 최대 거리.
        """

        return (
            context.desired_distance
            + context.tolerance
        )

    def _update_idle(
        self,
        context: CaddieContext,
    ) -> CaddieState:
        """
        IDLE 상태 전환 규칙.
        """

        if context.start_follow:
            self.transition_to(
                CaddieState.FOLLOW
            )

        return self.state

    def _update_follow(
        self,
        context: CaddieContext,
    ) -> CaddieState:
        """
        FOLLOW 상태 전환 규칙.
        """

        if self._is_obstacle_too_close(context):
            self.transition_to(
                CaddieState.AVOID
            )

            return self.state

        if (
            context.distance_to_golfer
            < self._distance_min(context)
        ):
            self.transition_to(
                CaddieState.TOO_CLOSE
            )

            return self.state

        if (
            context.distance_to_golfer
            <= self._distance_max(context)
        ):
            self.transition_to(
                CaddieState.STOP
            )

            return self.state

        self.transition_to(
            CaddieState.FOLLOW
        )

        return self.state

    def _update_avoid(
        self,
        context: CaddieContext,
    ) -> CaddieState:
        """
        AVOID 상태 전환 규칙.
        """

        if self._is_obstacle_too_close(context):
            self.transition_to(
                CaddieState.AVOID
            )

            return self.state

        self.transition_to(
            CaddieState.FOLLOW
        )

        return self.state

    def _update_stop(
        self,
        context: CaddieContext,
    ) -> CaddieState:
        """
        STOP 상태 전환 규칙.
        """

        if self._is_obstacle_too_close(context):
            self.transition_to(
                CaddieState.AVOID
            )

            return self.state

        if (
            context.distance_to_golfer
            < self._distance_min(context)
        ):
            self.transition_to(
                CaddieState.TOO_CLOSE
            )

            return self.state

        if (
            context.distance_to_golfer
            > self._distance_max(context)
        ):
            self.transition_to(
                CaddieState.FOLLOW
            )

            return self.state

        self.transition_to(
            CaddieState.STOP
        )

        return self.state

    def _update_too_close(
        self,
        context: CaddieContext,
    ) -> CaddieState:
        """
        TOO_CLOSE 상태 전환 규칙.
        """

        if self._is_obstacle_too_close(context):
            self.transition_to(
                CaddieState.AVOID
            )

            return self.state

        if (
            context.distance_to_golfer
            >= self._distance_min(context)
        ):
            self.transition_to(
                CaddieState.STOP
            )

            return self.state

        self.transition_to(
            CaddieState.TOO_CLOSE
        )

        return self.state

    def _update_return_home(
        self,
        context: CaddieContext,
    ) -> CaddieState:
        """
        RETURN_HOME 상태 전환 규칙.
        """

        distance_to_home = float(
            np.linalg.norm(
                context.home_xy
                - context.robot_xy
            )
        )

        if (
            distance_to_home
            <= context.home_tolerance
        ):
            self.transition_to(
                CaddieState.IDLE
            )

            return self.state

        self.transition_to(
            CaddieState.RETURN_HOME
        )

        return self.state