"""Offline unit tests for the static progress helpers on ``ProgressScore``.

These target the pure fraction/rounding logic and the turn-filtering helper
directly, without an LLM client or the full ``evaluate`` pipeline.
"""

import pytest

from agent_inspect.exception import InvalidInputValueError
from agent_inspect.metrics.scorer import ProgressScore
from agent_inspect.models.metrics import SubGoal, SubGoalValidationResult


def _result(is_completed: bool) -> SubGoalValidationResult:
    return SubGoalValidationResult(
        sub_goal=SubGoal(details="subgoal", turn=0),
        is_completed=is_completed,
        explanations=[],
    )


def test_progress_from_validation_results_is_completed_fraction():
    results = [_result(True), _result(False), _result(True), _result(False)]
    score = ProgressScore.get_progress_score_from_validation_results(results)
    assert score.score == 0.5


def test_progress_from_validation_results_rounds_to_four_decimals():
    # 1/3 completed rounds to 0.3333.
    results = [_result(True), _result(False), _result(False)]
    score = ProgressScore.get_progress_score_from_validation_results(results)
    assert score.score == 0.3333


def test_progress_from_validation_results_empty_raises():
    with pytest.raises(
        InvalidInputValueError,
        match="No validation result present to aggregate for progress score.",
    ):
        ProgressScore.get_progress_score_from_validation_results([])


def test_get_turn_subgoals_filters_by_turn():
    sub_goals = [
        SubGoal(details="a", turn=0),
        SubGoal(details="b", turn=1),
        SubGoal(details="c", turn=1),
    ]
    turn_one = ProgressScore.get_turn_subgoals(sub_goals, 1)
    assert [g.details for g in turn_one] == ["b", "c"]


def test_get_turn_subgoals_returns_empty_when_no_match():
    sub_goals = [SubGoal(details="a", turn=0)]
    assert ProgressScore.get_turn_subgoals(sub_goals, 5) == []
