# Development Standards

This project is built incrementally in small, understandable, testable steps.

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

## Git Convention

Commit messages currently use this format:

```text
fix: lowercase description
```

The description must be specific, concise, and lowercase after the `fix: ` prefix. Commits should remain small and focused so the project history explains how the system was built.
