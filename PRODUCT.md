# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

One user: the Sonar assessor who owns this tool. After a customer maturity-assessment meeting, they collect the evidence (their own notes, the meeting transcript, telemetry CSV exports and the SonarQube system info JSON), run the tool, review what Jev decided, and send the finished Word report to the customer. It is a personal tool with no other users or roles.

## Product Purpose

It turns one customer's assessment evidence into the SonarQube Maturity Assessment report (`.docx`). Jev (TypeSafe System One) judges which maturity criteria, findings, recommendations and summary statements the evidence supports. The code derives the level from those judgments and fills in the report template.

A run succeeds when:
- the report needs only light hand edits (pasting charts, adjusting wording) before it goes to the customer;
- the assessor can trust the judgments, seeing quickly what Jev decided and which items it was unsure about (⚠, Nouls in the 0.3–0.7 review band);
- the report is ready within hours of the meeting, not days;
- every customer's report has the same structure and meets the same standard.

## Positioning

The judging and the writing are kept separate. Jev only judges candidate statements against each customer's evidence. The level, the report text and the document structure come from code, the template, and `library.py`/the *Recommendations by Level* md. That separation keeps reports consistent and lets the assessor check any judgment.

## Operating Context

- Runs locally on the assessor's laptop (`streamlit run app.py`, localhost:8501), with a CLI equivalent (`assess.py`, `charts.py`).
- Workflow tabs: **Evidence → Run → Review & download → Charts**. One customer folder per customer under `customers/` (with `customer.json`, evidence files, `metrics/` and `output/`).
- Jev answers are cached (`output/jev_answers.json`), so the report can be rebuilt from `customer.json` changes without another Jev call.
- The evidence must fit Jev's limits: 32k tokens with any one question (`TOKEN_BUDGET`) and 64k with all questions (`REQUEST_BUDGET`). When it doesn't, the assessor trims the transcript or notes.
- Annex charts come out as PNGs and the assessor pastes them into the docx by hand.
- When a report is rebuilt, the existing one is moved to `reports/previous/` first, so hand edits are never lost.

## Capabilities and Constraints

- **Design work is UI-only.** Impeccable work changes only the Streamlit UI: layout, copy, hierarchy and states in `app.py`. It never changes how Jev is called or how its answers are used. Leave the questions, prompts, thresholds (`YES`, `REVIEW_BAND`), `TOKEN_BUDGET`/`REQUEST_BUDGET`, decision logic in `assess.py`, and the content in `library.py` alone.
- **Stack is fixed:** Streamlit + python-docx + matplotlib. Do not rewrite it in another framework.
- **Local-only, never hosted.** Customer data stays on the machine. The one exception is an assessment run, which sends the evidence to Jev at `api.typesafe.ai`.
- Review lets the assessor include or exclude recommendations, and those choices persist to `customer.json` (`include_recs` / `exclude_recs`).
- Terminology: *Nouls* (criterion judgments), *Choices* (version/edition/DB/login), *LTA* (`LATEST_LTA` in `library.py`), *Quality Gate*, *AI CodeFix*.
- Undecided: whether the customer-data notice should become an explicit pre-run approval step. Today it is a caption and a README note.

## Brand Commitments

None confirmed as binding. Repo evidence: the report charts (`charts.py`) use a Sonar-style palette (ink `#25023f`, purple `#340976`, blue `#336ccc`) and Poppins (`fonts/`). Those choices belong to the customer-facing report, not the Streamlit UI.

## Evidence on Hand

- Customer folders under `customers/` (real customer data, gitignored).
- Generated and past reports in `reports/`, including earlier hand-made assessments (gitignored).
- Templates: `templates/Maturity Assessment Template.docx`, *Recommendations by Level* md, and the Notes template.
- A real system-info export at the project root.
- These are real customer data. Never use them as public examples or demo content, and never invent customers, findings or metrics.

## Product Principles

1. **Judgment you can check.** Every level and recommendation should show where it came from, and anything Jev was unsure about should be clearly flagged.
2. **Code writes, Jev judges.** Keep the generated wording, structure and level logic out of the model's hands so every report stays consistent.
3. **Never lose the assessor's work.** Hand edits, pasted charts and include/exclude choices survive every rebuild.
4. **Short path from meeting to report.** Cut steps, re-runs and Jev calls (prefer the cache) between collecting the evidence and having a sendable docx.
5. **Customer data stays local.** Nothing leaves the laptop except the deliberate Jev call.
