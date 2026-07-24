# Contributing to agent-quality-inspect

Thanks for your interest in improving the toolkit. This guide covers the local
setup and the checks your change needs to pass before it can be merged.

## Development setup

The package targets Python 3.10+ and depends only on `numpy` at runtime. Install
it in editable mode together with the test and dev dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements_test.txt -r requirements_dev.txt
```

A `Makefile` wraps the common tasks:

```bash
make install-dev   # editable install + test/dev requirements
make check         # lint + format check + tests (the pre-push gate)
```

## Code style

Linting and formatting are handled by [ruff](https://docs.astral.sh/ruff/); the
rules live in `pyproject.toml`. Before opening a pull request:

```bash
ruff check src tests      # lint
ruff format src tests     # format
```

Optionally install the git hooks so these run automatically on commit:

```bash
pip install pre-commit
pre-commit install
```

## Tests

New behaviour needs tests, and existing tests must stay green. The suite is
offline: LLM-backed metrics are exercised through mocks, so no API keys are
required.

```bash
python -m pytest
```

## Commit messages

Use short, imperative summaries prefixed by type, e.g. `feat:`, `fix:`,
`docs:`, `test:`, `refactor:`, or `chore:`. Keep each commit focused on a single
logical change.

## Scope of the repository

`src/agent_inspect/` and `tests/` are the maintained package and are held to the
lint rules above. The vendored `agent_runners/tau2-bench/` snapshot is a
third-party subproject with its own toolchain and is **not** modified as part of
package changes. The `demo/`, `paper_experiments/`, and `docs/` directories are
illustrative artifacts and are excluded from linting.

## License

By contributing you agree that your contributions are licensed under the
project's [Apache License 2.0](./LICENSE).
