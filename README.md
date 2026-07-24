# agent-quality-inspect

[![Unit Tests](https://github.com/Azimml/agent-quality-inspect/actions/workflows/run-unit-tests.yaml/badge.svg)](https://github.com/Azimml/agent-quality-inspect/actions/workflows/run-unit-tests.yaml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-261230.svg)](https://github.com/astral-sh/ruff)

**A statistical evaluation toolkit for benchmarking agentic AI systems** — across frameworks, use cases, and datasets — so that results are comparable rather than anecdotal.

`agent-quality-inspect` is the reference implementation for the paper **_TED: Talk, Evaluate, Diagnose_** (ICLR 2026). It moves agent evaluation beyond a single pass/fail score: it simulates realistic, persona-aware users, measures *how much* and *how efficiently* an agent makes progress on multi-turn tasks, and then automatically clusters *why* agents fail.

---

## Why another eval toolkit?

Most agent benchmarks report one number: did the final answer pass? That hides almost everything that matters in practice — whether the agent made steady progress or got lucky at the end, how many turns it burned, how consistent it is across repeated runs, and *what kind* of mistakes it makes. `agent-quality-inspect` is built around three ideas, which map onto the paper's **TED** loop:

| Stage | What it does | Where it lives |
| --- | --- | --- |
| **T**alk | A persona-aware simulated user (expert / non-expert) drives a *dynamic* multi-turn conversation with the agent under test. | `agent_inspect.user_proxy` |
| **E**valuate | Subgoal-based, turn-by-turn metrics: Progress, **AUC**, **Progress-Per-Turn (PPT)**, Success, Tool Correctness, plus multi-sample **pass@k / pass^k**. | `agent_inspect.metrics` |
| **D**iagnose | Automated, LLM-driven (or rule-based) error analysis that clusters failures into interpretable categories. | `agent_inspect.tools.error_analysis` |

The package is deliberately **framework-agnostic**. You adapt your agent's trajectory into a small set of dataclasses; everything downstream is common.

---

## Installation

```bash
# Core install (metrics + models; depends only on numpy)
pip install agent_quality_inspect

# With the Azure OpenAI LLM-as-a-judge client (openai + backoff)
pip install "agent_quality_inspect[azure-openai]"
```

Requires **Python 3.10+**. The core package intentionally has a minimal dependency footprint (just `numpy`) — the `openai` / `backoff` dependencies are only pulled in via the optional `azure-openai` extra, so you can compute metrics offline or plug in your own LLM client.

For local development:

```bash
git clone https://github.com/Azimml/agent-quality-inspect.git
cd agent-quality-inspect
pip install -e . -r requirements_test.txt -r requirements_dev.txt
pre-commit install     # ruff lint + format on every commit
python -m pytest       # 400+ mocked unit tests, no network / API keys required
```

---

## The metrics

All scorer metrics take an `AgentDialogueTrace` (the agent's trajectory) and an `EvaluationSample` (the task and its subgoals), and return a `NumericalScore`.

- **Progress** — the fraction of a task's subgoals completed, judged by an LLM-as-a-judge with majority voting:

  <code>progress(i) = (1/|G|) · Σ<sub>g∈G</sub> LLM_judge(g, τ<sub>i</sub>)</code>

- **AUC** — the area under the *progress-through-turns* curve. Rewards agents that make progress **early and steadily**, not just those that scrape a pass on the last turn.
- **PPT (Progress-Per-Turn)** — total progress divided by the number of turns taken to reach it (`p(T) / T`). A measure of **efficiency**.
- **Success** — 1.0 if the task is fully completed (progress == 1), else 0.0.
- **Tool Correctness** — the ratio of correctly executed tool calls to expected tool calls, validated across three dimensions (tool name, input arguments, output) via exact match and/or LLM-as-a-judge.
- **pass@k** — probability that **at least one** of `k` sampled trials succeeds. Measures capability under sampling.
- **pass^k** — probability that **all** `k` sampled trials succeed. Measures **reliability / consistency**.

Because `AUC`, `PPT`, and final-turn `Success` are all derived from the same per-turn progress curve, you compute the (expensive) progress-through-turns **once** and derive the rest cheaply.

Both `pass@k` and `pass^k` are unbiased estimators computed in closed form from `n` observed trials with `s` successes — no resampling required:

<code>pass@k = 1 − C(n−s, k) / C(n, k)</code> &nbsp;&nbsp; <code>pass^k = C(s, k) / C(n, k)</code>

At `k = 1` both collapse to the plain success rate `s / n`. As `k` grows, `pass@k` rises toward 1 (easier to get *at least one* success) while `pass^k` falls toward 0 (harder to get *all* successes) — so report `pass@k` when you care about best-of-`k` capability and `pass^k` when you care about run-to-run reliability.

---

## Quick start

### 1. Compute a metric on an existing trajectory

```python
from agent_inspect.metrics.scorer import ProgressScore
from agent_inspect.metrics.constants import INCLUDE_JUDGE_EXPLANATION, OPTIMIZE_JUDGE_TRIALS
from agent_inspect.clients.azure_openai_client import AzureOpenAIClient

# An LLM-as-a-judge client. Reads AZURE_API_VERSION / AZURE_API_BASE / AZURE_API_KEY.
client = AzureOpenAIClient(model="gpt-4.1", max_tokens=4096)

metric = ProgressScore(
    llm_client=client,
    config={INCLUDE_JUDGE_EXPLANATION: True, OPTIMIZE_JUDGE_TRIALS: False},
)
result = metric.evaluate(agent_trace=agent_trace, evaluation_data_sample=data_sample)
print(result.score)  # e.g. 0.75  (3 of 4 subgoals completed)
print(result.explanations)  # per-subgoal judge rationales
```

### 2. Derive AUC and PPT from a single progress-through-turns pass

```python
from agent_inspect.metrics.scorer import ProgressScoresThroughTurns, AUC, PPT
from agent_inspect.metrics.constants import MAX_TURNS, INCLUDE_VALIDATION_RESULTS

progress_through_turns = ProgressScoresThroughTurns(
    llm_client=client,
    config={MAX_TURNS: 8, INCLUDE_VALIDATION_RESULTS: True},
)
progress_rates = progress_through_turns.evaluate(agent_trace, data_sample)  # list[NumericalScore]

auc = AUC(llm_client=client).get_auc_score_from_progress_scores(progress_rates)
ppt = PPT(llm_client=client).get_ppt_score_from_progress_scores(progress_rates)
print(auc.score, ppt.score)
```

### 3. Aggregate reliability across repeated runs

```python
from agent_inspect.metrics.multi_samples import PassAtK, PassHatK
from agent_inspect.metrics.constants import K_VALUE, NO_OF_TRIALS

# scorer_results: list[NumericalScore] with score in {0, 1}, one per trial
pass_at_2 = PassAtK(config={K_VALUE: 2, NO_OF_TRIALS: 5}).compute(scorer_results)
pass_hat_2 = PassHatK(config={K_VALUE: 2, NO_OF_TRIALS: 5}).compute(scorer_results)
```

### 4. Diagnose failures automatically

```python
from agent_inspect.tools import UnsupervisedSubgoalErrorAnalysis
from agent_inspect.models.tools import SubgoalErrorAnalysisDataSample

analyser = UnsupervisedSubgoalErrorAnalysis(llm_client=client)
result = analyser.analyze_batch(data_samples)  # discovers & clusters failure patterns
for cluster_label, validations in result.analyzed_validations_clustered_by_errors.items():
    print(cluster_label, "->", len(validations), "failures")
```

Prefer fixed categories? Use `SemisupervisedSubgoalErrorAnalysis` / `SemisupervisedToolCallErrorAnalysis` (predefined, overridable clusters), or `DeterministicToolCallErrorAnalysis` for a fast, **LLM-free** rule-based classification of tool-call errors.

---

## Bring your own agent

You do not need to adopt a new agent framework. Evaluation consumes two plain dataclasses (`agent_inspect.models.metrics`):

**The task you are grading** — an `EvaluationSample`:

```python
from agent_inspect.models.metrics import EvaluationSample, SubGoal, ExpectedToolCall

sample = EvaluationSample(
    id=1,
    user_instruction="Change my JFK flight on May 17 to a nonstop, only if it costs < $100.",
    sub_goals=[
        SubGoal(details="Agent does not book any flight the user did not approve.", turn="all"),
        SubGoal(details="Agent confirms the price is under $100 before changing.", turn=2),
    ],
    expected_tool_calls=[
        ExpectedToolCall(tool="search_flights", turn=1),
    ],
)
```

**Your agent's trajectory** — an `AgentDialogueTrace` built from `TurnTrace` / `Step`:

```python
from agent_inspect.models.metrics import AgentDialogueTrace, TurnTrace, AgentResponse, Step

trace = AgentDialogueTrace(
    turns=[
        TurnTrace(
            id="t1",
            agent_input="Change my JFK flight on May 17 to a nonstop.",
            agent_response=AgentResponse(response="Let me look that up."),
            steps=[
                Step(id="s1", parent_ids=[], tool="search_flights", tool_output={"flights": []})
            ],
        ),
        # ... one TurnTrace per conversational turn
    ]
)
```

Map your framework's output onto these once and every metric and diagnostic works. Two reference adapters (`Tau2BenchAdapter`, `ToolsandboxAdapter`) live in `agent_inspect.metrics.adapters` and show the pattern.

### Plugging in a different LLM judge

`AzureOpenAIClient` is provided out of the box. To use any other provider, subclass the abstract `agent_inspect.clients.LLMClient` and implement its three coroutines (`make_llm_request`, `make_llm_requests`, `make_request_with_payload`).

---

## Talk: the simulated user

The `UserProxyAgent` generates realistic user utterances during a live conversation with your agent, driven by a task summary, a persona (expert vs. non-expert), and one or more terminating conditions:

```python
from agent_inspect.user_proxy import UserProxyAgent
from agent_inspect.models.user_proxy import TerminatingCondition, ChatHistory
from agent_inspect.user_proxy.constants import USE_EXPERT_AGENT

user = UserProxyAgent(
    llm_client=client,
    task_summary=sample.user_instruction,
    terminating_conditions=[TerminatingCondition(check="The task goal is satisfied.")],
    agent_description="A customer-support airline agent.",
    config={USE_EXPERT_AGENT: True},
)

chat_history = ChatHistory(id="run-1", conversations=[])
message = await user.generate_message_from_chat_history(chat_history)
if message.check is not None:
    ...  # a terminating condition was reached
```

---

## Repository layout

```
src/agent_inspect/
├── clients/        # LLM-as-a-judge clients (LLMClient base + AzureOpenAIClient)
├── metrics/
│   ├── scorer/     # Progress, AUC, PPT, Success, ToolCorrectness
│   ├── multi_samples/  # pass@k, pass^k
│   ├── observed/   # latency, token, tool-call counts
│   ├── validator/  # subgoal + tool-call completion validators
│   └── adapters/   # tau2-bench / toolsandbox trajectory adapters
├── models/         # dataclasses: EvaluationSample, AgentDialogueTrace, ...
├── tools/error_analysis/   # unsupervised / semisupervised / deterministic diagnostics
├── user_proxy/     # UserProxyAgent (the "Talk" stage)
└── exception/      # typed errors with stable error codes

paper_experiments/  # end-to-end runner + datasets used in the paper
demo/               # static leaderboard / error-analysis dashboard
docs/               # Sphinx documentation sources
```

An end-to-end example — driving a conversation, adapting the trajectory, computing AUC/PPT, and running error analysis — lives in [`paper_experiments/runner.py`](./paper_experiments/runner.py).

---

## Development

```bash
ruff check src tests          # lint (config in pyproject.toml)
ruff format src tests         # format
python -m pytest              # run the unit test suite
```

A `Makefile` wraps these into convenience targets (`make lint`, `make format`, `make test`, and `make check` for the full pre-push gate); run `make help` for the full list. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the complete contributor workflow.

The test suite is fully offline — LLM-backed metrics are exercised through mocks, so no API keys are required to run `python -m pytest`. For a runnable, dependency-light tour of the numerical metrics, see [`examples/metrics_quickstart.py`](./examples/metrics_quickstart.py).

CI runs the linter plus the full test suite on Linux across Python 3.10–3.13, and publishes to PyPI via trusted publishing (OIDC) on release. The vendored `agent_runners/tau2-bench/` snapshot is third-party and excluded from linting.

---

## Citation

If you use this toolkit in your research, please cite the paper:

```bibtex
@inproceedings{ted2026,
  title     = {TED: Talk, Evaluate, Diagnose},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2026}
}
```

---

## License

Distributed under the [Apache License 2.0](./LICENSE).
