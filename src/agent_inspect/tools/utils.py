from agent_inspect.core.utils import match_to_int
from agent_inspect.exception import EvaluationError, InvalidInputValueError
from agent_inspect.exception.error_codes import ErrorCode
from agent_inspect.metrics.constants import (
    COMPLETE_INCOMPLETE_GRADE_PATTERN,
    COMPLETE_INCOMPLETE_PAIR,
)


def map_subgoal_validations_to_binary_matrix(completions: list[str]) -> list[int]:
    """Convert judge completions into a list of binary (0/1) votes.

    Each completion is parsed for a ``C``/``I`` (completion) or ``A``/``N``
    (applicability) grade. Completions that do not contain a recognisable grade
    are treated as non-votes and dropped, so the returned list may be shorter
    than ``completions``.

    :param completions: The judge completion strings to map.
    :return: A list of ``1`` (positive grade) and ``0`` (negative grade) values,
        one per successfully parsed completion.
    """
    binary_matrix = []
    for completion in completions:
        try:
            # Supports both C/I (completion) and A/N (applicability) grades
            score = match_to_int(
                completion, COMPLETE_INCOMPLETE_GRADE_PATTERN, COMPLETE_INCOMPLETE_PAIR
            )
            binary_matrix.append(score)
        except InvalidInputValueError:
            # A completion that does not contain the expected grade pattern is
            # treated as a non-vote and dropped from the binary matrix.
            continue
    return binary_matrix


def validate_inputs_for_pass_k_initialisation(k_value: int, num_trials: int) -> None:
    """Validate the ``k`` and ``num_trials`` configuration for pass@k / pass^k.

    :param k_value: Number of samples drawn per estimate. Must be a positive
        integer no larger than ``num_trials``.
    :param num_trials: Total number of trials available. Must be a positive
        integer and must be provided (a falsy value is rejected).
    :raises agent_inspect.exception.EvaluationError: If ``num_trials`` is missing
        or non-positive, if ``k_value`` is non-positive, or if ``k_value``
        exceeds ``num_trials``.
    """
    if not num_trials:
        raise EvaluationError(
            ErrorCode.INVALID_VALUE.value, "num_trials is invalid and must be provided."
        )

    if k_value <= 0:
        raise EvaluationError(
            ErrorCode.INVALID_VALUE.value, f"k_value ({k_value}) must be greater than 0"
        )

    if num_trials <= 0:
        raise EvaluationError(
            ErrorCode.INVALID_VALUE.value,
            f"num_trials ({num_trials}) must be greater than 0",
        )

    if k_value > num_trials:
        raise EvaluationError(
            ErrorCode.INVALID_VALUE.value,
            f"k_value ({k_value}) cannot be greater than num_trials ({num_trials})",
        )
