"""Offline quick-start for the numerical metrics in agent-quality-inspect.

This script uses only the parts of the toolkit that do not require an
LLM-as-a-judge client, so it runs without any API keys or network access:

* ``pass@k`` / ``pass^k`` reliability metrics over repeated success/failure runs.
* ``AUC`` and ``PPT`` derived from a precomputed list of per-turn progress
  scores (the same shape ``ProgressScoresThroughTurns.evaluate`` returns).

Run it with::

    python examples/metrics_quickstart.py
"""

from agent_inspect.metrics.constants import K_VALUE, NO_OF_TRIALS
from agent_inspect.metrics.multi_samples import PassAtK, PassHatK
from agent_inspect.metrics.scorer import AUC, PPT
from agent_inspect.models.metrics import NumericalScore


def reliability_across_runs() -> None:
    """Estimate reliability from five repeated runs, three of which succeeded."""
    # One NumericalScore per trial; score is 1 for success, 0 for failure.
    trial_scores = [NumericalScore(s) for s in (1, 0, 1, 0, 1)]

    # pass@k: probability at least one of k sampled runs succeeds.
    pass_at_2 = PassAtK(config={K_VALUE: 2, NO_OF_TRIALS: 5}).compute(trial_scores)
    # pass^k: probability all k sampled runs succeed (a stricter consistency check).
    pass_hat_2 = PassHatK(config={K_VALUE: 2, NO_OF_TRIALS: 5}).compute(trial_scores)

    print(f"pass@2 = {pass_at_2.score:.4f}")
    print(f"pass^2 = {pass_hat_2.score:.4f}")


def curves_from_progress_scores() -> None:
    """Derive AUC and PPT from per-turn progress scores without calling a judge."""
    # Progress rises from 0 to 1 over four turns; normally produced by
    # ProgressScoresThroughTurns.evaluate against a real trajectory.
    progress_scores = [NumericalScore(s) for s in (0.0, 0.5, 0.75, 1.0)]

    auc_score = AUC.get_auc_score_from_progress_scores(progress_scores)
    ppt_score = PPT.get_ppt_score_from_progress_scores(progress_scores)

    print(f"AUC = {auc_score.score:.4f}")
    print(f"PPT = {ppt_score.score:.4f}")


if __name__ == "__main__":
    print("== Reliability across repeated runs ==")
    reliability_across_runs()
    print("\n== Progress-curve summaries ==")
    curves_from_progress_scores()
