"""Summarise observations.tsv: delay by arm, paired by hour, and missing runs.

Usage: git show origin/measurements:observations.tsv | python3 scripts/analyze.py
Delay = observed - scheduled; event delay = created - scheduled; runner wait = observed - created.
Runs not seen within 24 h of their slot count as missing (a run later than that is misattributed
to the next day's slot by probe.yml).
"""
import csv, sys, statistics as st
from collections import defaultdict
from datetime import datetime, timezone, timedelta

def t(s): return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

rows = [r for r in csv.reader(sys.stdin, delimiter="\t") if r and r[1] != "manual"]
by = defaultdict(list)
seen = set()
for sched, arm, hour, minute, created, started, observed, run_id, attempt in rows:
    s = t(sched)
    seen.add((s, arm))
    by[arm].append(((t(observed) - s).total_seconds() / 60, (t(created) - s).total_seconds() / 60, (t(observed) - t(created)).total_seconds() / 60, hour))

def q(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
print("arm      n  p50 delay  p90  | p50 event-delay | p50 runner-wait  (minutes)")
for arm, v in sorted(by.items()):
    d, e, w = ([x[i] for x in v] for i in (0, 1, 2))
    print(f"{arm:7} {len(v):3}  {q(d,.5):8.0f} {q(d,.9):5.0f}  | {q(e,.5):14.0f} | {q(w,.5):14.1f}")

print("\nPaired by hour (offhour - onhour, minutes; positive = on-the-hour is faster):")
per = defaultdict(lambda: defaultdict(list))
for arm, v in by.items():
    for d, _, _, h in v: per[h][arm].append(d)
diffs = [st.median(a["offhour"]) - st.median(a["onhour"]) for a in per.values() if a["onhour"] and a["offhour"]]
for h, a in sorted(per.items()):
    if a["onhour"] and a["offhour"]:
        print(f"  {int(h):02d}h  on {st.median(a['onhour']):6.0f}  off {st.median(a['offhour']):6.0f}")
if diffs: print("  median of hourly differences:", round(st.median(diffs)))

cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
if rows:
    first = min(t(r[0]) for r in rows)
    print(f"\nfirst slot seen: {first:%F}; missing counts need the cron list and are computed by comparing days x 12 slots")
