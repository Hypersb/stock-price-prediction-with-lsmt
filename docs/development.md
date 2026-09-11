# Development Standards

This project is built incrementally in small, understandable, testable steps.

## Full-Stack Local Workflow

1. Copy `.env.example` values into a local `.env` (and `frontend/.env.local` for Next.js).
2. Start PostgreSQL: `docker compose up -d postgres`
3. Apply migrations: `alembic upgrade head`
4. Start API: `uvicorn backend.app.main:app --reload`
5. Start dashboard: `cd frontend; npm run dev`
6. Open `http://localhost:3000` and confirm `GET /api/v1/health` plus `GET /api/v1/ready`.

Or run the full Compose stack:

```powershell
docker compose up --build
```

See [deployment.md](deployment.md) for environment variables, health checks, and CI.

## Quality Checks

```powershell
# Python
ruff check backend tests ml
pytest -q

# Frontend
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
```

## Engineering Rules

- Build incrementally and keep each change focused.
- Prefer one responsibility per module where practical.
- Avoid data leakage in all research and modeling workflows.
- Preserve chronological order in financial time-series work.
- Separate training and inference when those workflows are implemented.
- Do not normally commit generated datasets.
- Never commit secrets, credentials, or tokens.
- Add tests alongside important reusable functionality.
- Use notebooks for exploration.
- Move reusable production logic from notebooks into modules.
- Evaluate model performance out of sample.
- Account for transaction costs in trading performance evaluation.
- Make no claims of profitability without evidence.
- Prefer empty research states over fabricated financial results.

## Git Convention

Commit messages currently use this format:

```text
fix: lowercase description
```

The description must be specific, concise, and lowercase after the `fix: ` prefix. Commits should remain small and focused so the project history explains how the system was built.
