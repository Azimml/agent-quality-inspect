"""Offline unit tests for the static success-aggregation helpers.

These exercise the pure scoring rules in ``SuccessBasedMetric`` directly, without
constructing an LLM client or running the full ``evaluate`` pipeline.
"""

import pytest

from agent_inspect.exception import InvalidInputValueError
from agent_inspect.metrics.scorer import SuccessBasedMetric
from agent_inspect.models.metrics import (
    NumericalScore,
    SubGoal,
    SubGoalValidationResult,
)


def _result(is_completed: bool) -> SubGoalValidationResult:
    return SubGoalValidationResult(
        sub_goal=SubGoal(details="subgoal", turn=0),
        is_completed=is_completed,
        explanations=[],
    )


def test_success_from_validation_results_all_complete_is_one():
    results = [_result(True), _result(True)]
    score = SuccessBasedMetric.get_success_score_from_validation_results(results)
    assert score.score == 1
    assert score.sub_scores["progress_score"] == 1.0


def test_success_from_validation_results_any_incomplete_is_zero():
    # Success requires every subgoal complete; one failure drops it to 0.
    results = [_result(True), _result(False)]
    score = SuccessBasedMetric.get_success_score_from_validation_results(results)
    assert score.score == 0
    assert score.sub_scores["progress_score"] == 0.5


def test_success_from_validation_results_empty_raises():
    with pytest.raises(
        InvalidInputValueError,
        match="No validation result present to aggregate for success score.",
    ):
        SuccessBasedMetric.get_success_score_from_validation_results([])


def test_success_from_progress_score_full_progress_is_one():
    score = SuccessBasedMetric.get_success_score_from_progress_score(NumericalScore(1.0))
    assert score.score == 1
    assert score.sub_scores["progress_score"] == 1.0


def test_success_from_progress_score_partial_progress_is_zero():
    # Any progress below 1.0 is not a success.
    score = SuccessBasedMetric.get_success_score_from_progress_score(NumericalScore(0.999))
    assert score.score == 0
    assert score.sub_scores["progress_score"] == 0.999
