# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `CONTRIBUTING.md` describing local setup, style, and the check workflow.
- `Makefile` with developer targets (`install-dev`, `lint`, `format`, `test`, `check`).
- `.editorconfig` mirroring the project's formatting conventions.
- `examples/` directory with a runnable, offline metric-usage script.
- Additional offline unit tests covering metric math edge cases.

### Changed

- Expanded docstrings and type hints on core metric helpers.

## [2.3.6a1]

### Added

- Initial public release: AUC, PPT, pass@k / pass^k, success, tool-correctness,
  and observed metrics (latency, token count, tool-call count).
- LLM-as-a-judge scoring with majority voting and configurable judge trials.
- Automated error-analysis tooling (deterministic, semisupervised, unsupervised).
- tau2-bench and toolsandbox trajectory adapters.

[Unreleased]: https://github.com/Azimml/agent-quality-inspect/compare/main...HEAD
