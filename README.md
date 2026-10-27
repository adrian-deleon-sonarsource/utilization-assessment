# SonarQube Maturity Assessment

Turns a customer's assessment evidence (your notes, the meeting transcript, telemetry CSVs and the
SonarQube system info export) into the Word maturity assessment report. Jev (TypeSafe System One)
judges which levels, findings and recommendations the evidence supports; the code writes the report
from the template.

> **Customer data:** an assessment run sends the notes, transcript, telemetry and system info to
> Jev at `api.typesafe.ai`. Make sure that is approved for the customer before you run it.

## Setup

Needs Python 3.12 or later.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.bk .env        # then fill in TYPESAFE_API_KEY and MATURITY_ASSESSOR
```

## Web UI

```sh
.venv/bin/streamlit run app.py
```

This opens http://localhost:8501. Then:

1. **Sidebar → New customer.** Enter the customer name and your name as it appears in the transcript.
2. **Evidence.** Upload your notes, the transcript(s), the telemetry CSVs and the system info JSON, and
   list any facts you verified yourself under *Confirmed facts*.
3. **Run.** Check the evidence size against Jev's two limits, then click *Run assessment with Jev*.
   Jev's answers are cached, so *Rebuild report from cached answers* re-applies `customer.json`
   changes without another Jev call.
4. **Review & download.** Check the level and the recommendations. Items marked *To review* are ones Jev was
   unsure about. Tick or untick *Include* and save to rebuild, then download the `.docx` and the
   findings/evidence `.md`.
5. **Charts** (optional). If there are telemetry CSVs, this creates the annex charts as PNGs.
   They are not added to the report, so paste them in yourself.

## Command line

```sh
.venv/bin/python assess.py --new "Acme Corp" --assessor "Jane Doe"   # create customers/acme_corp/
.venv/bin/python assess.py acme                                       # run Jev, write the report
.venv/bin/python assess.py acme --from-cache                          # rebuild without calling Jev
.venv/bin/python assess.py --list
.venv/bin/python charts.py acme --upgrade 2026-05 --upgrade-label "2025.4.6 LTA" --codefix-enabled 2026-05-23
```

All `charts.py` options are optional. `--upgrade` marks the LTA upgrade on the LOC chart, and
`--codefix-enabled` splits the AI CodeFix before/after chart (without it, the export is split in half).

## Customer folder

```
customers/acme_corp/
  customer.json              name, assessor, confirmed facts, overrides (see below)
  notes.txt                  your notes: any .txt/.md/.vtt/.docx with "note" in the name
  transcript.vtt             transcripts: every other .txt/.md/.vtt/.docx
  sonarqube-support-info-*.json   Administration > System > Download System Info
  metrics/                   telemetry CSV exports, matched by name:
    LoC Usage.csv              "loc"      monthly licensed LOC (+ % active / active LOC)
    Projects.csv               "project"
    Languages.csv              "language"
    Users.csv                  "user"
    AI CodeFix.csv             "codefix"  month, suggestions_generated, suggestions_applied,
                                          active_usage_days, first_day, last_day
  output/                    jev_answers.json (cache), <name>_maturity_results.md, charts/
```

The finished report is written to `reports/<Customer> - Maturity Assessment.docx`. If that file
already exists, it is first moved to `reports/previous/` with a timestamp, so pasted charts and
hand edits are never lost.

In the transcript, Jev treats "You" or the assessor's name as the Sonar assessor and everyone else
as the customer or the Sonar account team.

### customer.json

| Field | Purpose |
|---|---|
| `customer`, `assessor` | Report name; your name as it appears in the transcript (defaults to `MATURITY_ASSESSOR`) |
| `confirmed` | Facts you verified; Jev treats them as true |
| `include_recs` / `exclude_recs` | Recommendation keys to force in or out (the UI's *Include* column writes these) |
| `environment_extra` | Extra "Current Environment" bullets: `{"Heading": [["text", indent], ...]}` |
| `summary_extra` | Extra executive-summary candidates: `{"key": "statement"}` |
| `telemetry_extra` | Telemetry facts that are not in the CSVs |
| `environment` | Replaces the generated "Current Environment" section entirely |

## Upkeep

- `library.py`: set `LATEST_LTA` when a new LTA ships. The extra recommendations and summary
  statements are also defined there.
- `templates/`: the report template and *Recommendations by Level*.
- `TOKEN_BUDGET` and `REQUEST_BUDGET` in `assess.py`: Jev accepts 32k tokens for the evidence plus
  any one question, and 64k for the evidence plus all questions. Caption-style transcripts (`.vtt`, or
  `.txt` with `00:00:00 --> 00:00:00` timings) are sent without the timings and with each speaker's
  consecutive captions merged, which roughly halves their size. If a run is still over budget, trim
  small talk from the transcript or notes. Splitting a meeting into several files does not help:
  all transcripts are sent together.

<!-- Test change to trigger Gitar repo scan. -->
