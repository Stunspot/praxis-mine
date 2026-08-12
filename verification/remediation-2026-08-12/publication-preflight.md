# Public publication preflight

GitHub's official billing documentation observed 2026-08-12 states that standard GitHub-hosted runners are free in public repositories. Praxis Mine is public. The corrected workflow runs one `ubuntu-latest` line-ending job on the pull request and has no push trigger; Pages uses the legacy `main:/docs` builder.

Planned usage is `1 pull_request trigger × 1 job × 1 attempt × 360 raw-minute ceiling × 0 billable multiplier = 0 billed minutes`. Zero automatic retries, duplicate push jobs, private allowance minutes, paid capacity, or ruleset changes are planned.
