"""Offline unit tests for the static tool-correctness aggregation helper.

These exercise the pure fraction/rounding logic directly, without an LLM client
or the full ``evaluate`` pipeline.
"""

import pytest

from agent_inspect.exception import InvalidInputValueError
from agent_inspect.metrics.scorer import ToolCorrectnessMetric
from agent_inspect.models.metrics import ExpectedToolCall, ToolCallValidationResult


def _result(is_completed: bool, tool: str = "tool") -> ToolCallValidationResult:
    return ToolCallValidationResult(
        is_completed=is_completed,
        expected_tool_call=ExpectedToolCall(tool=tool),
        explanations=[],
    )


def test_tool_correctness_all_correct_is_one():
    results = [_result(True), _result(True), _result(True)]
    score = ToolCorrectnessMetric.get_tool_correctness_score_from_validation_results(results)
    assert score.score == 1.0


def test_tool_correctness_partial_is_fraction():
    results = [_result(True), _result(False), _result(True), _result(False)]
    score = ToolCorrectnessMetric.get_tool_correctness_score_from_validation_results(results)
    assert score.score == 0.5


def test_tool_correctness_rounds_to_four_decimals():
    # 2/3 correct rounds to 0.6667.
    results = [_result(True), _result(True), _result(False)]
    score = ToolCorrectnessMetric.get_tool_correctness_score_from_validation_results(results)
    assert score.score == 0.6667


def test_tool_correctness_empty_raises():
    with pytest.raises(
        InvalidInputValueError,
        match="No validation results present to aggregate for tool correctness score.",
    ):
        ToolCorrectnessMetric.get_tool_correctness_score_from_validation_results([])
