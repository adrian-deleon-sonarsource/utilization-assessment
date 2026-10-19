"""Web UI for the maturity assessment: evidence, Jev run, review, download, charts.

  .venv/bin/streamlit run app.py
"""

import json
import os
import re
from datetime import date
from html import escape
from pathlib import Path

import streamlit as st

import assess
import charts

st.set_page_config(page_title="Utilization Assessment", page_icon=":material/insights:", layout="wide")

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


# ---------------------------------------------------------------- look: SonarQube (Echoes design system)
# Colours, type and theme switching live in .streamlit/config.toml; this adds what config can't reach.

ECHOES = {
    "light": {"strong": "#1d212f", "default": "#3e4357", "subtle": "#637192", "weak": "#e1e6f3",
              "bold": "#c5cddf", "surface": "#eff2f9", "accent": "#5d6cd0", "accent_weak": "#e8ebff", "on_accent": "#ffffff", "success": "#537c17",
              "warning": "#8c5e1e", "danger": "#b42318",
              # rating A..E: background, text, border
              "rating": {"A": ("#d1fadf", "#054f31", "#12b76a"), "B": ("#d4f2b7", "#054f16", "#9dcb6b"),
                         "C": ("#fce9a3", "#66400f", "#f5b840"), "D": ("#ffd6af", "#7a2e0e", "#fd7122"),
                         "E": ("#fecdca", "#5d1d13", "#f04438")}},
    "dark": {"strong": "#fcfcfd", "default": "#e1e6f3", "subtle": "#c5cddf", "weak": "#3e4357",
             "bold": "#637192", "surface": "#3e4357", "accent": "#9fa9ed", "accent_weak": "#5d6cd04d", "on_accent": "#2a2f40", "success": "#c4ea9e",
             "warning": "#fadc79", "danger": "#fda29b",
             "rating": {"A": ("#027a48", "#f6fef9", "#32d583"), "B": ("#537c17", "#f3f8ef", "#b3dd86"),
                        "C": ("#8c5e1e", "#fcf5e4", "#fadc79"), "D": ("#b54708", "#fff0eb", "#f75f09"),
                        "E": ("#b42318", "#fef3f2", "#fda29b")}},
}
RATING = {5: "A", 4: "B", 3: "C", 2: "D", 1: "E"}  # maturity level -> SonarQube rating colour


def echoes_vars():
    """Both palettes as CSS light-dark() variables. .stApp's color-scheme follows the menu's theme choice in the
    browser, so the custom pieces switch with it without a rerun."""
    light, dark = ECHOES["light"], ECHOES["dark"]
    out = [f"--sq-{k.replace('_', '-')}: light-dark({light[k]}, {dark[k]});" for k in light if k != "rating"]
    for g in "ABCDE":
        for part, lv, dv in zip(("bg", "fg", "border"), light["rating"][g], dark["rating"][g]):
            out.append(f"--sq-rating-{g}-{part}: light-dark({lv}, {dv});")
    return "\n  ".join(out)


def apply_style():
    st.html(f"""<style>
.stApp {{
  {echoes_vars()}
}}
::selection {{ background: var(--sq-accent-weak); color: var(--sq-strong); }}
* {{ scrollbar-color: var(--sq-bold) transparent; scrollbar-width: thin; }}
[data-testid="stMainBlockContainer"] {{ max-width: 1280px; padding-top: 4rem; }}
[data-testid="stMetricValue"], [data-testid="stProgress"], .sq-num {{ font-variant-numeric: tabular-nums; }}
code {{ font-family: 'Ubuntu Mono', ui-monospace, SFMono-Regular, Menlo, monospace; }}
[data-testid="stMarkdownContainer"] code, [data-testid="stCaptionContainer"] code, .sq-meta code {{ font-size: 1.05em !important; }}
[data-testid^="stBaseButton-primary"]:not(:disabled), [data-testid^="stBaseButton-primary"]:not(:disabled) p {{ color: var(--sq-on-accent) !important; }}

/* project tabs: SonarQube's navigation bar (dark labels, accent underline on the current one) */
[data-testid="stTabs"] [role="tablist"] {{ gap: 2rem; }}
[data-testid="stTabs"] [role="tab"] {{ padding: .75rem 0; }}
[data-testid="stTabs"] [role="tab"] p {{ font-weight: 600; font-size: 1rem; color: var(--sq-default); }}
[data-testid="stTabs"] [role="tab"]:hover p, [data-testid="stTabs"] [role="tab"][aria-selected="true"] p {{ color: var(--sq-strong); }}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{ height: 3px; background: var(--sq-accent); }}
[data-testid="stTabs"] [data-baseweb="tab-border"] {{ background: var(--sq-weak); }}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {{ padding-top: 1.75rem; }}

/* buttons: semibold labels; outlined secondary in the strong text colour */
[data-testid^="stBaseButton"] p {{ font-weight: 600; }}
[data-testid^="stBaseButton-secondary"]:not(:disabled) p {{ color: var(--sq-strong); }}

/* sidebar: SonarQube's filter column (bold section labels, hairline between sections) */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{ font-weight: 600; font-size: 1rem; color: var(--sq-strong); }}
[data-testid="stSidebar"] [data-testid="stExpander"], [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stAlert"] {{ border-top: 1px solid var(--sq-weak); padding-top: 1rem; }}
[data-testid="stSidebar"] [data-testid="stExpander"] details {{ border: 0; }}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {{ padding-left: 0; padding-right: 0; }}
[data-testid="stSidebar"] [data-testid="stExpander"] summary p {{ font-size: 1rem; color: var(--sq-strong); }}

/* panels */
[data-testid="stForm"], [data-testid="stExpander"] details {{ border: 1px solid var(--sq-weak); border-radius: 8px; }}
[data-testid="stExpander"] summary p {{ font-weight: 600; }}

/* page header */
.sq-product {{ margin: 0 0 .5rem; color: var(--sq-accent); font: 600 1.125rem/1.5rem Inter, sans-serif; letter-spacing: -.01em; }}
.sq-header {{ margin-bottom: .25rem; }}
.sq-title {{ display: flex; align-items: center; gap: .625rem; flex-wrap: wrap; }}
.sq-header h1 {{ font: 600 1.5rem/2.25rem Inter, sans-serif; color: var(--sq-strong); margin: 0; padding: 0; }}
.sq-tag {{ font: 400 .875rem/1.375rem 'Ubuntu Mono', ui-monospace, monospace; color: var(--sq-default);
  background: var(--sq-surface); border: 1px solid var(--sq-weak); border-radius: 4px; padding: 0 .375rem; }}
.sq-meta {{ font: 400 .875rem/1.25rem Inter, sans-serif; color: var(--sq-subtle); margin-top: .25rem; }}

/* review overview */
.sq-overview {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border: 1px solid var(--sq-weak);
  border-radius: 8px; margin-bottom: 1rem; }}
.sq-cell {{ padding: 1rem 1.25rem; min-width: 0; }}
.sq-cell + .sq-cell {{ border-left: 1px solid var(--sq-weak); }}
.sq-label {{ font: 600 .75rem/1rem Inter, sans-serif; color: var(--sq-subtle); margin-bottom: .75rem; }}
.sq-row {{ display: flex; align-items: center; gap: .75rem; }}
.sq-rating {{ flex: none; width: 2.5rem; height: 2.5rem; border-radius: 8px; border: 1px solid; display: grid;
  place-items: center; font: 700 1.25rem/1 Inter, sans-serif; }}
.sq-value {{ font: 600 1rem/1.5rem Inter, sans-serif; color: var(--sq-strong); }}
.sq-note {{ font: 400 .875rem/1.25rem Inter, sans-serif; color: var(--sq-subtle); }}
.sq-big {{ font: 600 1.5rem/2.25rem Inter, sans-serif; color: var(--sq-strong); }}
.sq-ok {{ color: var(--sq-success); }} .sq-warn {{ color: var(--sq-warning); }} .sq-bad {{ color: var(--sq-danger); }}
@media (max-width: 720px) {{
  .sq-overview {{ grid-template-columns: 1fr; }}
  .sq-cell + .sq-cell {{ border-left: 0; border-top: 1px solid var(--sq-weak); }}
}}
</style>""")


def rating_badge(level):
    g = RATING.get(level, "E")
    return (f'<span class="sq-rating sq-num" style="background:var(--sq-rating-{g}-bg);color:var(--sq-rating-{g}-fg);'
            f'border-color:var(--sq-rating-{g}-border)" '
            f'aria-hidden="true">{level}</span>')


def overview(result):
    """SonarQube-style overview strip: criteria level, Jev's score, recommendation counts."""
    lv, sl = result["level"], result["score_level"]
    included = sum(r["include"] for r in result["recs"])
    to_review = sum(r["review"] for r in result["recs"])
    agree = ('<span class="sq-ok">Agrees with the criteria level</span>' if lv == sl else
             '<span class="sq-warn">Differs from the criteria level: check the recommendations to review</span>')
    review = (f'<span class="sq-warn">{to_review} to review</span>' if to_review else "none to review")
    st.html(f"""<div class="sq-overview">
  <div class="sq-cell"><div class="sq-label">Maturity level (criteria)</div>
    <div class="sq-row">{rating_badge(lv)}<div><div class="sq-value">Level {lv}</div>
    <div class="sq-note">{escape(assess.LEVELS.get(lv, ("",))[0])}</div></div></div></div>
  <div class="sq-cell"><div class="sq-label">Jev's overall score</div>
    <div class="sq-row">{rating_badge(sl)}<div><div class="sq-value">Level {sl}</div>
    <div class="sq-note">{escape(assess.LEVELS.get(sl, ("",))[0])}</div>
    <div class="sq-note">{agree}</div></div></div></div>
  <div class="sq-cell"><div class="sq-label">Recommendations</div>
    <div class="sq-big sq-num">{included} <span class="sq-note">included</span></div>
    <div class="sq-note">{review}</div></div>
</div>""")


# ---------------------------------------------------------------- helpers

def rel(path):
    return path.relative_to(assess.HERE) if path.is_relative_to(assess.HERE) else path


def save_config(folder, cfg):
    (folder / "customer.json").write_text(json.dumps(cfg, indent=2) + "\n")


def save_upload(upload, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(upload.getbuffer())
    return dest


def evidence_name(upload, kind):
    """File name that load_customer will classify as `kind` ("note" in the name = notes)."""
    name = Path(upload.name).name
    has_note = "note" in name.lower()
    if kind == "notes" and not has_note:
        return f"notes - {name}"
    if kind == "transcript" and has_note:  # keep it out of the notes bucket
        return "transcript - " + re.sub(r"(?i)[ _-]*notes?", "", name)
    return name


def preview(ctx):
    """Decisions from the cached Jev answers, without writing any files -> (result, default include per rec)."""
    if not ctx["cache"].exists():
        return None, None
    answers = json.loads(ctx["cache"].read_text())["answers"]
    recs, _ = assess.load_recs()
    result = assess.decide(answers, recs, ctx)
    plain = assess.decide(answers, recs, dict(ctx, include_recs=set(), exclude_recs=set()))
    return result, {r["key"]: r["include"] for r in plain["recs"]}


def file_row(path, label=None):
    c1, c2 = st.columns([6, 1])
    c1.write(f"`{label or path.name}`")
    with c2.popover("Remove", width="stretch"):
        st.write(f"Delete **{path.name}** from the customer folder?")
        if st.button("Delete", key=f"del_{path}", type="primary"):
            path.unlink()
            st.rerun()


# ---------------------------------------------------------------- sidebar: customer

assess.load_env()
apply_style()
with st.sidebar:
    st.html('<p class="sq-product">Utilization Assessment</p>')
    customers = assess.list_customers()
    if "customer" in st.session_state and st.session_state.customer not in customers:
        del st.session_state.customer
    if (new := st.session_state.pop("select_customer", None)) in customers:  # set by "Create" on the previous run
        st.session_state.customer = new
    choice = st.selectbox("Customer", customers, key="customer", index=None if not customers else 0,
                          placeholder="No customers yet")

    with st.expander("New customer", expanded=not customers):
        with st.form("new_customer", clear_on_submit=True):
            new_name = st.text_input("Customer name", placeholder="Acme Corp")
            new_assessor = st.text_input("Assessor (you, as you appear in the transcript)",
                                         value=os.environ.get("MATURITY_ASSESSOR", ""))
            if st.form_submit_button("Create") and new_name.strip():
                folder = assess.new_customer(new_name.strip(), new_assessor.strip() or None)
                st.session_state.select_customer = folder.name  # the selectbox exists already: select it on the rerun
                st.rerun()

    if not os.environ.get("TYPESAFE_API_KEY"):
        st.warning("TYPESAFE_API_KEY is not set: add it to `.env` (see `.env.bk`) to run Jev. "
                   "Rebuilding from cached answers still works.")
    st.caption("Evidence (notes, transcripts, telemetry) is sent to Jev at api.typesafe.ai when you run an assessment.")

if not choice:
    st.info("Create a customer in the sidebar to start.")
    st.stop()

folder = assess.CUSTOMERS / choice
try:
    cfg = assess.read_config(folder)
except assess.AssessError as e:
    cfg = None
    st.error(str(e))

assessor_name = (cfg or {}).get("assessor") or os.environ.get("MATURITY_ASSESSOR", "")
st.html(f"""<div class="sq-header"><div class="sq-title"><h1>{escape(assess.customer_name(folder, cfg or {}))}</h1>
<span class="sq-tag">{escape(str(rel(folder)))}</span></div>
{f'<div class="sq-meta">Assessor: {escape(assessor_name)}</div>' if assessor_name else ""}</div>""")

tab_ev, tab_run, tab_review, tab_charts = st.tabs(["1 · Evidence", "2 · Run", "3 · Review & download", "Charts"])


# ---------------------------------------------------------------- 1. evidence

with tab_ev:
    if cfg is not None:
        with st.form("settings"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Customer name (as written in the report)", cfg.get("customer") or "")
            assessor = c2.text_input("Assessor (as they appear in the transcript)",
                                     cfg.get("assessor") or os.environ.get("MATURITY_ASSESSOR", ""))
            confirmed = st.text_area(
                "Confirmed facts, one per line (things you verified that the transcript may not say clearly)",
                "\n".join(cfg.get("confirmed", [])), height=130)
            if st.form_submit_button("Save"):
                cfg.update(customer=name.strip(), assessor=assessor.strip(),
                           confirmed=[l.strip() for l in confirmed.splitlines() if l.strip()])
                save_config(folder, cfg)
                st.success("Saved.")

    with st.expander("Advanced: edit customer.json"):
        st.caption("Also holds environment_extra, summary_extra, telemetry_extra, include_recs and exclude_recs.")
        raw_path = folder / "customer.json"
        raw = st.text_area("customer.json", raw_path.read_text() if raw_path.exists() else "{}", height=300,
                           label_visibility="collapsed")
        if st.button("Save customer.json"):
            try:
                json.loads(raw)
            except json.JSONDecodeError as e:
                st.error(f"Not valid JSON: {e}")
            else:
                raw_path.write_text(raw if raw.endswith("\n") else raw + "\n")
                st.rerun()

    st.markdown("#### Add evidence")
    with st.form("uploads", clear_on_submit=True):
        c1, c2 = st.columns(2)
        up_notes = c1.file_uploader("Assessment notes (.txt, .md, .docx)", type=["txt", "md", "docx"],
                                    accept_multiple_files=True)
        up_tr = c2.file_uploader("Meeting transcripts (.txt, .md, .vtt, .docx)", type=["txt", "md", "vtt", "docx"],
                                 accept_multiple_files=True)
        c3, c4 = st.columns(2)
        up_metrics = c3.file_uploader("Telemetry CSV exports (LoC Usage, Projects, Languages, Users, AI CodeFix ...)",
                                      type=["csv"], accept_multiple_files=True)
        up_info = c4.file_uploader("SonarQube support info (.json, Administration > System > Download System Info)",
                                   type=["json"])
        if st.form_submit_button("Save files", type="primary"):
            saved = [save_upload(u, folder / evidence_name(u, "notes")) for u in up_notes or []]
            saved += [save_upload(u, folder / evidence_name(u, "transcript")) for u in up_tr or []]
            saved += [save_upload(u, folder / "metrics" / Path(u.name).name) for u in up_metrics or []]
            if up_info:
                if not isinstance(json.loads(up_info.getvalue() or b"{}").get("System"), dict):
                    st.error(f"{up_info.name} does not look like a SonarQube system info export (no \"System\" section).")
                else:
                    saved.append(save_upload(up_info, folder / Path(up_info.name).name))
            if saved:
                st.success("Saved " + ", ".join(p.name for p in saved))

    st.markdown("#### In the customer folder")
    docs = sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in assess.DOC_SUFFIXES
                  and not f.name.startswith((".", "~$")))
    notes = [f for f in docs if "note" in f.name.lower()]
    groups = [("Notes", notes), ("Transcripts", [f for f in docs if f not in notes]),
              ("Telemetry CSVs", sorted((folder / "metrics").glob("*.csv"))),
              ("Support info", [p for p in [assess.serverinfo.find(folder)[0]] if p])]
    for label, files in groups:
        st.markdown(f"**{label}**")
        if not files:
            st.caption("none")
        for f in files:
            file_row(Path(f))


# ---------------------------------------------------------------- load the context the other tabs need

ctx, ctx_error = None, None
try:
    ctx = assess.load_customer(folder)
except assess.AssessError as e:
    ctx_error = str(e)


# ---------------------------------------------------------------- 2. run

with tab_run:
    if ctx_error:
        st.error(ctx_error)
    else:
        recs, _ = assess.load_recs()
        try:
            _, questions, tokens = assess.plan(ctx, recs)
        except assess.AssessError as e:
            questions, tokens = None, None
            st.warning(str(e))
        if tokens is not None:
            st.progress(min(tokens / assess.TOKEN_BUDGET, 1.0),
                        text=f"Evidence: ~{tokens:,} tokens · {tokens / assess.TOKEN_BUDGET:.0%} of the "
                             f"~{assess.TOKEN_BUDGET:,}-token budget · {len(questions)} questions for Jev")
            if tokens > assess.TOKEN_BUDGET:
                st.error("Too much evidence for one Jev call: trim the transcript or notes (for example, remove small talk "
                         "or a second meeting's transcript).")
            with st.expander("Inputs Jev will see"):
                st.write({k: v for k, v in ctx["files"].items()})
                if ctx["telemetry_bullets"]:
                    st.write(ctx["telemetry_bullets"])

        has_cache = ctx["cache"].exists()
        st.caption(f"The report is written to `{rel(ctx['out_docx'])}`; an existing one is moved to "
                   "`reports/previous/` first, so pasted charts and hand edits are kept.")
        replace_ok = st.checkbox("Replace the cached Jev answers", value=not has_cache, disabled=not has_cache,
                                 help="Running Jev again costs a call and can change borderline answers.")
        with st.container(horizontal=True):
            rebuild = st.button("Rebuild report from cached answers", type="primary" if has_cache else "secondary",
                                disabled=not has_cache,
                                help="No Jev call: applies customer.json changes (confirmed facts excluded) to the last answers.")
            go = st.button("Run assessment with Jev", type="secondary" if has_cache else "primary",
                           disabled=tokens is None or tokens > assess.TOKEN_BUDGET or not replace_ok
                           or not os.environ.get("TYPESAFE_API_KEY"))
        if go or rebuild:
            with st.status("Running..." if go else "Rebuilding...", expanded=True) as status:
                try:
                    result = assess.run(ctx, from_cache=rebuild, log=st.write)
                except assess.AssessError as e:
                    status.update(label="Failed", state="error")
                    st.error(str(e))
                except Exception as e:  # Jev / network errors: show them instead of a stack trace
                    status.update(label="Failed", state="error")
                    st.exception(e)
                else:
                    status.update(label=f"Done: Level {result['level']}. See the Review & download tab.", state="complete")


# ---------------------------------------------------------------- 3. review & download

with tab_review:
    if ctx_error:
        st.error(ctx_error)
    elif (pv := preview(ctx))[0] is None:
        st.info("No assessment yet: run one in the Run tab.")
    else:
        result, default = pv
        overview(result)

        st.markdown("#### Recommendations")
        st.caption("Tick or untick **Include**, then save: the change is kept in customer.json (include_recs / "
                   "exclude_recs) and the report is rebuilt without calling Jev. **To review** = Jev was unsure (30–70%).")
        only_review = st.toggle("Only show items to review", value=any(r["review"] for r in result["recs"]))
        shown = [r for r in sorted(result["recs"], key=lambda r: not r["review"]) if r["review"] or not only_review]
        rows = [{"Include": r["include"], "Review": "To review" if r["review"] else "", "Recommendation": r["title"],
                 "Section": r["section"] or "", "Level": r.get("level"), "Applies": r["p_applies"], "Already done": r["p_done"],
                 "Why": r["reason"], "key": r["key"]}
                for r in shown]
        edited = st.data_editor(
            rows, hide_index=True, disabled=[k for k in rows[0] if k != "Include"] if rows else True,
            column_order=["Include", "Review", "Recommendation", "Section", "Level", "Applies", "Already done", "Why"],
            column_config={"Applies": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1, width="small"),
                           "Already done": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1,
                                                                           width="small"),
                           "Recommendation": st.column_config.TextColumn(width="medium"),
                           "Section": st.column_config.TextColumn(width="medium"),
                           "Review": st.column_config.TextColumn(width="small"),
                           "Level": st.column_config.NumberColumn(width="small"),
                           "Why": st.column_config.TextColumn(width="large")},
            key=f"recs_{choice}")
        dirty = any(row["Include"] != r["include"] for row, r in zip(edited, shown))
        if st.button("Save choices and rebuild report", type="primary" if dirty else "secondary", disabled=not dirty):
            include, exclude = set(cfg.get("include_recs", [])), set(cfg.get("exclude_recs", []))
            for row in edited:
                k = row["key"]
                include.discard(k), exclude.discard(k)
                if row["Include"] and not default[k]:
                    include.add(k)
                elif not row["Include"] and default[k]:
                    exclude.add(k)
            cfg.update(include_recs=sorted(include), exclude_recs=sorted(exclude))
            save_config(folder, cfg)
            try:
                assess.run(assess.load_customer(folder), from_cache=True, log=lambda m: None)
            except assess.AssessError as e:
                st.error(str(e))
            else:
                st.success("Saved and rebuilt.")
                st.rerun()

        if result["summary"]:
            with st.expander("Executive summary statements"):
                for k in result["summary"]:
                    st.write("• " + assess.fmt(assess.summary_candidates(ctx)[k], ctx, result["choices"].get("version")))

        st.markdown("#### Download")
        if not ctx["out_docx"].exists():
            st.info("No .docx yet: rebuild the report in the Run tab.")
        md = ctx["out_report"].read_text() if ctx["out_report"].exists() else None
        with st.container(horizontal=True):
            if ctx["out_docx"].exists():
                st.download_button("Word report (.docx)", ctx["out_docx"].read_bytes(), ctx["out_docx"].name, DOCX_MIME,
                                   type="primary")
            if md is not None:
                st.download_button("Findings and evidence (.md)", md, ctx["out_report"].name, "text/markdown")
        if md is not None:
            with st.expander("Findings and evidence report"):
                st.markdown(md)


# ---------------------------------------------------------------- charts

with tab_charts:
    st.caption("Annex charts from the telemetry CSVs. They are not added to the Word report: download them and paste "
               "them in where you want them.")
    metrics = folder / "metrics"
    have = charts.loc_file(metrics) or charts.ai_file(metrics)
    if not have:
        st.info("**No metrics detected.**\n\n" + charts.METRICS_HELP.format(metrics=f"`{rel(metrics)}`")
                .replace("\n  - ", "\n- ").replace("\nThen create the charts again.", "")
                + "\n\nOr upload them in the Evidence tab (Telemetry CSV exports), then come back here.")
    else:
        found = [p.name for p in (charts.loc_file(metrics), charts.ai_file(metrics)) if p]
        st.write("Using " + ", ".join(f"`{n}`" for n in found))
        with st.form("charts"):
            c1, c2, c3 = st.columns(3)
            upgrade = c1.text_input("LTA upgrade month (YYYY-MM, optional)", placeholder="2026-05",
                                    help="Marked on the LOC usage chart.")
            label = c2.text_input("Upgraded to (optional)", placeholder="2025.4.6 LTA")
            enabled_on = c3.checkbox("I know when AI CodeFix was enabled")
            enabled = c3.date_input("AI CodeFix enabled on", value=date.today(),
                                    help="Splits the before/after chart. Without it the export is split in half.")
            submitted = st.form_submit_button("Create charts", type="primary")
        if submitted:
            try:
                up = tuple(int(x) for x in upgrade.strip().split("-")) if upgrade.strip() else None
                if up and (len(up) != 2 or not 1 <= up[1] <= 12):
                    raise ValueError
            except ValueError:
                st.error("Upgrade month must look like 2026-05.")
            else:
                with st.spinner("Drawing..."):
                    made, notes = charts.make_charts(folder, up, label.strip() or None, enabled if enabled_on else None)
                for n in notes:
                    st.warning(n)
                st.session_state[f"charts_{choice}"] = [str(p) for p in made]

    out = folder / "output" / "charts"
    shown = sorted(out.glob("*.png")) if out.is_dir() else []
    if shown:
        st.markdown("#### Charts")
        for p in shown:
            st.image(str(p), caption=p.name, width="stretch")
            st.download_button(f"Download {p.name}", p.read_bytes(), p.name, "image/png", key=f"dl_{p}")
