"""Read the standard telemetry CSV exports (Languages, Projects, LoC Usage, Users,
PR Activity, Branches, AI CodeFix) from a customer's metrics folder.

Every file is optional; whatever is missing is simply left out. Exports are
usually UTF-16 and tab-separated, but UTF-8 and commas work too.
"""

import csv
import io
from datetime import datetime
from pathlib import Path


def _read_rows(path):
    raw = path.read_bytes()
    # UTF-16 only when it looks like it (BOM / NUL bytes): any even-length UTF-8 file also "decodes" as UTF-16
    utf16 = raw[:2] in (b"\xff\xfe", b"\xfe\xff") or b"\x00" in raw[:200]
    for enc in (("utf-16",) if utf16 else ()) + ("utf-8-sig", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    first = text.splitlines()[0] if text else ""
    delim = "\t" if "\t" in first else ","
    return [[c.strip() for c in row] for row in csv.reader(io.StringIO(text), delimiter=delim) if any(c.strip() for c in row)]


def _num(s):
    s = (s or "").replace(",", "").strip()
    if not s:
        return None
    try:
        return float(s) if "." in s else int(s)
    except ValueError:
        return None


def _month(s):
    try:
        return datetime.strptime(s.strip(), "%B %Y")
    except ValueError:
        return None


def _find(folder, *names):
    """Case-insensitive lookup of an export by (partial) file name."""
    for f in sorted(folder.glob("*.csv")):
        stem = f.stem.lower()
        if any(n in stem for n in names):
            return f
    return None


def _monthly(path):
    """Rows of 'Month YYYY, v1, v2...' -> {month: [v1, v2, ...]}, merging the
    duplicated month rows these exports contain (one value per row)."""
    rows = _read_rows(path)
    out = {}
    for row in rows:
        m = _month(row[0]) if row else None
        if not m:
            continue
        vals = [_num(c) for c in row[1:]]
        cur = out.setdefault(m, [None] * len(vals))
        cur += [None] * (len(vals) - len(cur))
        for i, v in enumerate(vals):
            if v is not None:
                cur[i] = v
    return dict(sorted(out.items()))


def _series(path, col=0, last=6):
    data = _monthly(path)
    pts = [(m, v[col]) for m, v in data.items() if col < len(v) and v[col] is not None]
    return pts[-last:]


def _label(m):
    return m.strftime("%b %Y")


def load(folder):
    """Return (telemetry dict for Jev, {report heading: [(bullet, indent)]})."""
    folder = Path(folder)
    if not folder.is_dir():
        return {}, {}
    tel, bullets, analysis = {}, [], []

    if f := _find(folder, "loc"):
        data = _monthly(f)
        # columns: % active LoC, active LoC, total LoC (largest branch per project)
        total = [(m, v[2]) for m, v in data.items() if len(v) > 2 and v[2] is not None]
        active = [(m, v[1], v[0]) for m, v in data.items() if len(v) > 1 and v[1] is not None]
        if total:
            (lm, lv), (pm, pv) = total[-1], max(total[-12:], key=lambda t: t[1])  # peak of the last year
            tel["licensed_loc"] = {"month": _label(lm), "value": lv}
            tel["peak_loc"] = {"month": _label(pm), "value": pv}
            line = f"~{lv / 1e6:.1f}M lines of code analyzed ({_label(lm)})"
            if pv > lv * 1.02:
                line += f", down from a {pv / 1e6:.1f}M peak in {_label(pm)}"
            bullets.append((line, 0))
            if len(total) >= 5:  # growth over the last 3 complete months
                (m0, v0), (m1, v1) = total[-5], total[-2]
                if v0:
                    g = (v1 / v0 - 1) * 100
                    tel["loc_growth_3_months_pct"] = {"from": _label(m0), "to": _label(m1), "value": round(g, 1)}
                    bullets.append((f"LOC changed {g:+.0f}% between {_label(m0)} and {_label(m1)}", 1))
        if active:
            am, av, pct = active[-1]
            tel["active_project_loc"] = {"month": _label(am), "value": av, "share": pct}
            share = f" ({pct * 100:.0f}%)" if pct else ""
            bullets.append((f"~{av / 1e6:.1f}M LOC{share} belongs to active projects", 1))

    if f := _find(folder, "project"):
        data = _monthly(f)
        last = next(((m, v) for m, v in reversed(data.items()) if len(v) > 1 and v[1] is not None), None)
        if last:
            m, v = last
            tel["projects"] = {"month": _label(m), "total": v[1], "active": v[0]}
            act = f", ~{v[0]:,} active" if v[0] is not None else ""
            bullets.append((f"~{v[1]:,} projects onboarded{act}", 0))

    if f := _find(folder, "language"):
        langs = sorted(((r[0], _num(r[1])) for r in _read_rows(f) if len(r) > 1 and _num(r[1]) is not None), key=lambda kv: -kv[1])
        if langs:
            tel["projects_by_language"] = dict(langs)
            bullets.append(("Projects by language: " + ", ".join(f"{n} ({c:,})" for n, c in langs), 1))

    if f := _find(folder, "user"):
        rows = _read_rows(f)
        months = next((r[1:] for r in rows if any(_month(c) for c in r)), [])
        series = {r[0]: [_num(c) for c in r[1:]] for r in rows if r and r[0] and not _month(r[0]) and any(_num(c) is not None for c in r[1:])}
        total = next((v for k, v in series.items() if "total" in k.lower()), None)
        mau = next((v for k, v in series.items() if "active" in k.lower()), None)
        line = None
        if total and (vals := [v for v in total if v is not None]):
            tel["user_accounts_total"] = vals[-1]
            line = f"{vals[-1]:,} user accounts"
        if mau:
            pts = [(months[i] if i < len(months) else "", v) for i, v in enumerate(mau) if v is not None][-6:]
            tel["monthly_active_users"] = {m: v for m, v in pts}
            lo, hi = min(v for _, v in pts), max(v for _, v in pts)
            line = (line + ", " if line else "") + f"~{lo:,}–{hi:,} monthly active users"
        if line:
            bullets.append((line, 0))

    for key, names, label in (("pull_request_analyses_per_month", ("pr", "pull"), "PR analyses"),
                              ("branch_analyses_per_month", ("branch",), "branch analyses")):
        if (f := _find(folder, *names)) and (pts := _series(f)):
            tel[key] = {_label(m): v for m, v in pts}
            analysis.append((f"~{max(v for _, v in pts):,} {label} per month (peak of the last {len(pts)} months)", 0))

    if (f := _find(folder, "codefix", "code fix")) and (usage := _codefix(f)):
        tel["ai_codefix_usage"] = usage
        line = (f"AI CodeFix in use since {usage['first_usage']}: {usage['suggestions_generated']:,} fix suggestions generated, "
                f"{usage['suggestions_applied']:,} applied ({usage['apply_rate_pct']}%) over {usage['active_usage_days']} active days")
        bullets.append((line, 0))

    return tel, {"Utilization": bullets, "Code Analysis": analysis}


def _codefix(path):
    """AI CodeFix usage export (one row per month: month, suggestions_generated,
    suggestions_applied, active_usage_days, optional first_day / last_day)."""
    rows = _read_rows(path)
    if len(rows) < 2:
        return None
    head = [h.lower() for h in rows[0]]
    col = lambda r, name: r[head.index(name)] if name in head and head.index(name) < len(r) else ""
    parsed = []
    for r in rows[1:]:
        m = _month(col(r, "month")) or _iso(col(r, "month"))
        gen = _num(col(r, "suggestions_generated"))
        if m and gen is not None:
            parsed.append((m, gen, _num(col(r, "suggestions_applied")) or 0, _num(col(r, "active_usage_days")),
                           _iso(col(r, "first_day")), _iso(col(r, "last_day"))))
    if not parsed:
        return None
    parsed.sort()
    monthly, firsts, lasts = {}, [], []
    for i, (m, gen, app, days, first, last) in enumerate(parsed):
        # first/last_day are the first and last days with usage: they only mark a
        # partial month for the first month (enablement) and the last (data cut-off)
        label = _label(m)
        if i == 0 and first and first.day > 1:
            label += f" ({first:%b} {first.day} onward)"
        elif i == len(parsed) - 1 and last and last.day < 28:
            label += f" ({last:%b} 1-{last.day} only)"
        monthly[label] = {"suggestions_generated": gen, "suggestions_applied": app, "active_usage_days": days}
        firsts += [first or m]
        lasts += [last] if last else []
    gen = sum(v["suggestions_generated"] for v in monthly.values())
    app = sum(v["suggestions_applied"] for v in monthly.values())
    days = sum(v["active_usage_days"] or 0 for v in monthly.values())
    usage = {"first_usage": min(firsts).strftime("%B %-d, %Y" if min(firsts).day > 1 else "%B %Y"),
             "suggestions_generated": gen, "suggestions_applied": app,
             "apply_rate_pct": round(app / gen * 100, 1) if gen else 0, "active_usage_days": days,
             "monthly": monthly}
    if lasts:
        usage["data_through"] = max(lasts).strftime("%B %-d, %Y")
    return usage


def _iso(s):
    try:
        return datetime.strptime(s.strip()[:10], "%Y-%m-%d")
    except ValueError:
        return None
