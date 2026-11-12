# Development conventions

This project is being rebuilt incrementally. Keep changes small and limited to the requested scope.

- Python 3.12, uv, Ruff (100-character lines), strict Pyright, and Pytest.
- Build system-agnostic primitives in the core.
- Toolkits declare independently executable tools using those primitives.
- Do not introduce orchestration, pipelines, retries, concurrency, registries, or framework abstractions without a concrete requirement.
- Keep credentials out of code, logs, and committed files. Use environment variables.
- Keep TLS verification enabled by default.
- Test behavior without relying on live services or real credentials.
- Update documentation when behavior changes.
- Do not commit unless explicitly requested.

Checks: `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pyright`, and `uv run pytest` once tests exist.
