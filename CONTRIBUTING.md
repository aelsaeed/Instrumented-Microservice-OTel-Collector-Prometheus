# Contributing

Thanks for contributing to this project.

## Development setup
1. Install Python 3.11.
2. Install dependencies:
   ```bash
   pip install -r otel-microservice-lab/requirements-dev.txt
   ```
3. Install git hooks:
   ```bash
   pre-commit install
   ```

## Local validation
Run these commands before opening a pull request:

```bash
make lint
make typecheck
make test
make demo
```

## Pull request expectations
- Keep changes focused and documented.
- Update README/ROADMAP/CHANGELOG when relevant.
- Include screenshots for UI/dashboard changes.
- Call out risk level and rollback considerations.
