import pytest

from agent_inspect.exception import EvaluationError
from agent_inspect.metrics.constants import K_VALUE, NO_OF_TRIALS
from agent_inspect.metrics.multi_samples import PassAtK
from agent_inspect.models.metrics import NumericalScore


# --- PassAtK Tests ---
def test_pass_at_k_all_success():
    metric = PassAtK(config={K_VALUE: 3, NO_OF_TRIALS: 5})
    success_scores = [NumericalScore(1) for _ in range(5)]
    result = metric.compute(success_scores)
    assert result.score == 1.0


def test_pass_at_k_no_num_of_trials_given():
    with pytest.raises(EvaluationError, match="num_trials .* must be provided"):
        PassAtK()


def test_pass_at_k_no_k_value_given():
    metric = PassAtK(config={NO_OF_TRIALS: 5})
    success_scores = [NumericalScore(1) for _ in range(5)]
    result = metric.compute(success_scores)
    # When k is not given, should default to k=num_trials, so all successes means score is 1.0
    assert result.score == 1.0


def test_pass_at_k_none_success():
    metric = PassAtK(config={K_VALUE: 2, NO_OF_TRIALS: 4})
    success_scores = [NumericalScore(0) for _ in range(4)]
    result = metric.compute(success_scores)
    assert result.score == 0.0


def test_pass_at_k_some_success():
    metric = PassAtK(config={K_VALUE: 2, NO_OF_TRIALS: 4})
    success_scores = [NumericalScore(x) for x in [1, 0, 0, 0]]
    result = metric.compute(success_scores)
    assert abs(result.score - 0.5) < 1e-6


def test_pass_at_k_typical():
    metric = PassAtK(config={K_VALUE: 3, NO_OF_TRIALS: 5})
    success_scores = [NumericalScore(x) for x in [1, 0, 1, 0, 1]]
    result = metric.compute(success_scores)
    assert result.score == 1.0


def test_pass_at_k_error_k_too_large():
    with pytest.raises(EvaluationError, match="k_value .* cannot be greater than num_trials .*"):
        PassAtK(config={K_VALUE: 5, NO_OF_TRIALS: 2})


def test_pass_at_k_empty_success_flags():
    metric = PassAtK(config={K_VALUE: 2, NO_OF_TRIALS: 4})
    success_scores = []
    with pytest.raises(
        EvaluationError,
        match="Success scores should have the same length as num_trials .*, but got .*",
    ):
        metric.compute(success_scores)


def test_pass_at_k_error_k_zero():
    with pytest.raises(EvaluationError, match="k_value .* must be greater than 0"):
        PassAtK(config={K_VALUE: 0, NO_OF_TRIALS: 4})


def test_pass_at_k_error_n_trials_zero():
    with pytest.raises(EvaluationError, match="num_trials .* must be provided"):
        PassAtK(config={K_VALUE: 2, NO_OF_TRIALS: 0})


def test_pass_at_k_k_one_equals_success_fraction():
    # pass@1 = 1 - C(n-s,1)/C(n,1) = 1 - (n-s)/n = s / n, i.e. the success rate.
    metric = PassAtK(config={K_VALUE: 1, NO_OF_TRIALS: 4})
    success_scores = [NumericalScore(x) for x in [1, 0, 1, 0]]
    result = metric.compute(success_scores)
    assert abs(result.score - 0.5) < 1e-6


def test_pass_at_k_rejects_non_binary_score():
    metric = PassAtK(config={K_VALUE: 2, NO_OF_TRIALS: 3})
    success_scores = [NumericalScore(1), NumericalScore(2), NumericalScore(0)]
    with pytest.raises(
        EvaluationError,
        match="Each score in scorer_results should be either 0 or 1, but got .*",
    ):
        metric.compute(success_scores)


def test_pass_at_k_single_success_full_k():
    # With k == num_trials, a single success guarantees the one drawn sample set
    # contains it, so pass@k == 1.0.
    metric = PassAtK(config={K_VALUE: 4, NO_OF_TRIALS: 4})
    success_scores = [NumericalScore(x) for x in [1, 0, 0, 0]]
    result = metric.compute(success_scores)
    assert result.score == 1.0
