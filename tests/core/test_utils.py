import pytest

from agent_inspect.core.utils import (
    get_config_or_default,
    match_to_int,
    tally_votes,
)
from agent_inspect.exception import InvalidInputValueError
from agent_inspect.metrics.constants import (
    COMPLETE_INCOMPLETE_GRADE_PATTERN,
    COMPLETE_INCOMPLETE_PAIR,
)


def test_config_or_default_returns_config_value_when_key_exists():
    config = {"key1": "value1", "key2": "value2"}
    result = get_config_or_default(config, "key1", "default_value")
    assert result == "value1"


def test_config_or_default_returns_default_when_key_does_not_exist():
    config = {"key1": "value1"}
    result = get_config_or_default(config, "key2", "default_value")
    assert result == "default_value"


def test_tally_votes_counts_complete_incomplete_and_invalid():
    completions = ["Grade: C", "Grade: I", "Grade: C", "Invalid Grade"]
    complete_cnt, incomplete_cnt, invalid_cnt = tally_votes(
        0,
        0,
        0,
        completions,
        COMPLETE_INCOMPLETE_GRADE_PATTERN,
        COMPLETE_INCOMPLETE_PAIR,
    )
    assert complete_cnt == 2
    assert incomplete_cnt == 1
    assert invalid_cnt == 1


def test_tally_votes_with_existing_counts():
    completions = ["Grade: C", "Grade: I"]
    complete_cnt, incomplete_cnt, invalid_cnt = tally_votes(
        5,
        3,
        2,
        completions,
        COMPLETE_INCOMPLETE_GRADE_PATTERN,
        COMPLETE_INCOMPLETE_PAIR,
    )
    assert complete_cnt == 6
    assert incomplete_cnt == 4
    assert invalid_cnt == 2


def test_match_to_int_positive_grade_case_insensitive():
    # The positive grade maps to 1 and matching is case-insensitive.
    assert match_to_int("grade: c reasoning", COMPLETE_INCOMPLETE_GRADE_PATTERN, ["C", "I"]) == 1


def test_match_to_int_negative_grade():
    assert match_to_int("GRADE: I", COMPLETE_INCOMPLETE_GRADE_PATTERN, ["C", "I"]) == 0


def test_match_to_int_no_grade_raises():
    with pytest.raises(InvalidInputValueError, match="Could not find the judge grade"):
        match_to_int("there is no grade here", COMPLETE_INCOMPLETE_GRADE_PATTERN, ["C", "I"])


def test_match_to_int_grade_outside_choices_raises():
    # "P" matches the [CPI] capture group but is not one of the two accepted
    # choices, so it is rejected as an invalid grade.
    with pytest.raises(InvalidInputValueError, match="Invalid judge grade"):
        match_to_int("Grade: P", COMPLETE_INCOMPLETE_GRADE_PATTERN, ["C", "I"])
