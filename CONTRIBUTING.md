# Contributing

Contributions are welcome! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/Maanik23/agentic-content-pipeline.git
cd agentic-content-pipeline
pip install -e ".[dev]"
```

## Workflow

1. Fork the repo and create a feature branch from `main`
2. Make your changes with tests
3. Run the checks:
   ```bash
   ruff check src/ tests/
   mypy src/pipeline/ --ignore-missing-imports
   pytest --cov=pipeline
   ```
4. Open a PR with a clear description

## Code Style

- Python 3.11+ with type hints
- Formatted with [Ruff](https://docs.astral.sh/ruff/)
- Pydantic v2 for all data models
- Async-first where applicable

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation
- `test:` adding/updating tests
- `chore:` maintenance
