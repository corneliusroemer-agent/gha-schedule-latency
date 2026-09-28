# gha-schedule-latency

How late do GitHub Actions `schedule` runs start, and does the minute of the hour matter?
Fork of [sgkim126/github-actions-schedule-latency](https://github.com/sgkim126/github-actions-schedule-latency),
which measures 288 slots a day; this version runs 12.

**Design.** Six hours of the day were drawn at random. Each hour has a pair of crons: one at `:00`
and one at a random off-hour minute. The pairs share an hour, so the comparison isolates the minute.
The slots are fixed in `.github/workflows/probe.yml`.

**Data.** One row per run in `observations.tsv` on the `data` branch:
`scheduled_at, arm, hour, minute, created_at, run_started_at, observed_at, run_id, attempt` (UTC).
`created_at - scheduled_at` is GitHub's event-delivery delay; `observed_at - created_at` is the runner wait.

**Analysis.** `git show origin/data:observations.tsv | python3 scripts/analyze.py`
