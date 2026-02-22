# cyber-actuary-scenarios

Cyber-actuarial "real-world scenario" calculations using **synthetic** loss models suitable for stress tests and portfolio analytics:

- Severity: lognormal (typical) + lognormal (mega) **mixture**
- Frequency: portfolio Poisson (lambda = policies × rate × trend)
- Outputs: VaR/TVaR @ 90/95/99 for **annual aggregate loss**
- Artifacts: `artifacts/scenario_summaries.csv` and `artifacts/scenario_summaries.json`

> Notes: The benchmark anchors in `src/cyber_actuary/config.py` are configurable inputs. This repo intentionally avoids hard claims and treats public figures as parameters you can tune.

## Quickstart (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

pytest -q
python scripts/run_scenarios.py
```

Artifacts are written to `artifacts/`:
- `scenario_summaries.csv`
- `scenario_summaries.json`

## What you get

The output table includes:
- mean / median / std / min / max
- VaR_90 / VaR_95 / VaR_99
- TVaR_90 / TVaR_95 / TVaR_99
- scenario = BASE vs AI (AI modeled as a mean reduction)
- year = 2024 vs 2025 (trend scaling)
- lambda_total and key scenario knobs

## Create a new GitLab repo and push

```bash
git init
git add .
git commit -m "Initial: cyber-actuarial synthetic scenarios + CI"
git branch -M main
git remote add origin <YOUR_GITLAB_REPO_URL>
git push -u origin main
```
