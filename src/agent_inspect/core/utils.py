import re
from typing import Any

from agent_inspect.exception import InvalidInputValueError
from agent_inspect.exception.error_codes import ErrorCode


def get_config_or_default(config: dict[str, Any] | None, config_key: str, default: Any) -> Any:
    """Return ``config[config_key]`` if present, otherwise ``default``.

    :param config: An optional configuration mapping. ``None`` is treated the
        same as an empty mapping.
    :param config_key: The key to look up in ``config``.
    :param default: The value returned when ``config`` is ``None`` or the key is
        absent.
    :return: The configured value, or ``default`` when it is not set.
    """
    if config and config_key in config:
        return config[config_key]
    return default


def match_to_int(completion: str, regex_pattern: str, grade_choices: list[str]) -> int:
    """
    Parse a completion string and return binary score based on grade.

    Args:
        completion: The completion string containing a grade
        regex_pattern: Regex pattern to extract the grade
        grade_choices: List of 2 strings [positive_grade, negative_grade]
                      e.g., ["C", "I"] for Complete/Incomplete
                      e.g., ["A", "N"] for Applicable/Not applicable

    Returns:
        1 if grade matches positive_grade, 0 if matches negative_grade
    """
    match = re.search(regex_pattern, completion)
    if not match:
        raise InvalidInputValueError(
            internal_code=ErrorCode.INVALID_JUDGE_RESPONSE_FORMAT_ERROR.value,
            message=f"Could not find the judge grade from the completion: {completion}",
        )
    grade = match.group(1).upper()  # Normalize to uppercase for comparison

    if grade == grade_choices[0].upper():
        correct_int = 1
    elif grade == grade_choices[1].upper():
        correct_int = 0
    else:
        raise InvalidInputValueError(
            internal_code=ErrorCode.INVALID_JUDGE_RESPONSE_FORMAT_ERROR.value,
            message=f"Invalid judge grade from the completion: {completion}",
        )
    return correct_int


def tally_votes(
    complete_cnt: int,
    incomplete_cnt: int,
    invalid_cnt: int,
    completions: list[str],
    regex_pattern: str,
    grade_choices: list[str],
) -> tuple[int, int, int]:
    """Accumulate complete / incomplete / invalid vote counts across completions.

    Each completion is parsed with :func:`match_to_int`. A completion whose grade
    matches the positive choice increments ``complete_cnt``, the negative choice
    increments ``incomplete_cnt``, and anything that cannot be parsed increments
    ``invalid_cnt``. The running counts are passed in and returned so this can be
    called incrementally across several batches of completions.

    :param complete_cnt: Running count of "complete" votes to add to.
    :param incomplete_cnt: Running count of "incomplete" votes to add to.
    :param invalid_cnt: Running count of unparseable votes to add to.
    :param completions: The judge completion strings to tally.
    :param regex_pattern: Regex used to extract the grade from each completion.
    :param grade_choices: Two-element list of ``[positive_grade, negative_grade]``.
    :return: The updated ``(complete_cnt, incomplete_cnt, invalid_cnt)`` tuple.
    """
    for completion in completions:
        try:
            score = match_to_int(completion, regex_pattern, grade_choices)
            if score == 1:
                complete_cnt += 1
            elif score == 0:
                incomplete_cnt += 1
        except InvalidInputValueError:
            invalid_cnt += 1
    return complete_cnt, incomplete_cnt, invalid_cnt
