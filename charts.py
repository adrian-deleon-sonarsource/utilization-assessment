"""Annex charts (LOC usage and growth, AI CodeFix usage) in the style of the
template's "Code Analysis Integration into the SDLC" graphic.

  .venv/bin/python charts.py acme --upgrade 2026-05 --upgrade-label "2025.4.6 LTA" --codefix-enabled 2026-05-23

Reads customers/<name>/metrics/: the LoC Usage export, plus an AI CodeFix
monthly export (columns: month, suggestions_generated, suggestions_applied,
active_usage_days, first_day, last_day). Writes PNGs to
customers/<name>/output/charts/; charts whose export is missing are skipped.
The charts are not added to the docx: paste them into the report by hand.
"""

import argparse
import csv
import sys
from datetime import date, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

import assess
import telemetry

HERE = Path(__file__).parent

# Sampled from the template's SDLC graphic.
INK = "#25023f"       # titles and text
AXIS = "#340976"      # axes and primary series
BLUE = "#336ccc"      # axis labels, number badges, highlights
LAVENDER = "#b2a7d2"  # dashed curve, secondary series
PANEL = "#dfe6f2"     # rounded callout panel
MID = "#674798"
ICON = "#3035a4"

for f in (HERE / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
FONT = "Poppins" if any("Poppins" in f.name for f in font_manager.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({"font.family": FONT, "text.color": INK, "axes.labelcolor": BLUE,
                     "xtick.color": INK, "ytick.color": INK, "axes.edgecolor": AXIS})

SIZE, DPI = (9.2, 4.6), 200  # same 2:1 proportions as the SDLC graphic


# ---------------------------------------------------------------- styling helpers

def figure(title):
    fig = plt.figure(figsize=SIZE, dpi=DPI, facecolor="white")
    # chart icon: framed square with a rising line, like the SDLC title icon
    ic = fig.add_axes([0.018, 0.865, 0.042, 0.084])
    ic.set_xlim(0, 1), ic.set_ylim(0, 1), ic.axis("off")
    ic.plot([0.05, 0.05, 0.95], [0.95, 0.05, 0.05], color=ICON, lw=2.2, solid_capstyle="butt")
    ic.plot([0.18, 0.4, 0.58, 0.85], [0.3, 0.55, 0.42, 0.8], color=BLUE, lw=1.8, ls=(0, (2, 1.4)))
    ic.annotate("", xy=(0.95, 0.95), xytext=(0.78, 0.78), arrowprops=dict(arrowstyle="-|>", color="#7ab8f5", lw=1.6))
    fig.text(0.07, 0.905, title, fontsize=21, fontweight="semibold", color=INK, va="center")
    return fig


def style_axes(ax, xlabel=None, ylabel=None):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
        ax.spines[side].set_linewidth(2.4)
    ax.tick_params(length=0, labelsize=9, pad=6)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12, color=BLUE, labelpad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12, color=BLUE, labelpad=8)
    ax.grid(axis="y", color="#eceaf3", lw=0.8)
    ax.set_axisbelow(True)


def badge(ax, x, y, n, text, dx=12, dy=0, coords="data", ha="left", size=9):
    """Numbered blue circle with a label, like the level markers."""
    ax.annotate(str(n), (x, y), xycoords=coords, xytext=(dx * 0, dy), textcoords="offset points",
                ha="center", va="center", fontsize=8.5, fontweight="semibold", color="white",
                bbox=dict(boxstyle="circle,pad=0.3", fc=BLUE, ec="none"), zorder=6)
    ax.annotate(text, (x, y), xycoords=coords, xytext=(dx if ha == "left" else -dx, dy), textcoords="offset points",
                ha=ha, va="center", fontsize=size, color=INK, zorder=6, linespacing=1.25)


def panel(fig, rect, heading, rows, note=None):
    """Rounded light-blue panel like the 'Clean as You Code' box."""
    x, y, w, h = rect
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.03",
                                      transform=fig.transFigure, fc=PANEL, ec="none", zorder=0))
    fig.text(x + w / 2, y + h - 0.055, heading, ha="center", va="center", fontsize=13, fontweight="semibold", color=BLUE)
    top = y + h - 0.14
    step = (h - 0.2 - (0.07 if note else 0)) / max(len(rows), 1)
    for i, (big, small) in enumerate(rows):
        cy = top - i * step
        fig.text(x + w / 2, cy, big, ha="center", va="center", fontsize=17, fontweight="semibold", color=INK)
        fig.text(x + w / 2, cy - (0.04 if "\n" in small else 0.055), small, ha="center", va="top" if "\n" in small else "center", fontsize=8.5, color=MID, linespacing=1.3)
    if note:
        fig.text(x + w / 2, y + 0.045, note, ha="center", va="center", fontsize=7.5, color=MID, style="italic", wrap=True)


def footnote(fig, text):
    fig.text(0.07, 0.025, text, fontsize=7.5, color=MID)


def millions(v, pos=None):
    return f"{v / 1e6:.0f}M" if abs(v) >= 1e7 else f"{v / 1e6:.2f}".rstrip("0").rstrip(".") + "M"


# ---------------------------------------------------------------- data

METRICS_HELP = """\
Add the customer's SonarQube telemetry exports as CSV files to {metrics}:
  - LOC usage: a CSV with "loc" in its name (e.g. "LoC Usage.csv"), one row per month with the
    licensed LOC (sum of each project's largest branch), optionally % active and active LOC.
    Gives chart 1 (LOC Usage) and chart 2 (Quarterly LOC Growth).
  - AI CodeFix: a CSV with "codefix" in its name (e.g. "AI CodeFix.csv") with the columns
    month, suggestions_generated, suggestions_applied, active_usage_days, first_day, last_day.
    Gives chart 3 (before vs. after) and chart 4 (by month).
Then create the charts again."""

AI_COLUMNS = ("month", "suggestions_generated", "suggestions_applied", "active_usage_days", "first_day", "last_day")


def loc_file(metrics):
    return telemetry._find(metrics, "loc") if metrics.is_dir() else None


def ai_file(metrics):
    if not metrics.is_dir():
        return None
    return next((p for p in sorted(metrics.glob("*.csv")) if "ai" in p.stem.lower().replace("-", " ").split()
                 or "codefix" in p.stem.lower().replace(" ", "")), None)


def loc_monthly(metrics):
    f = loc_file(metrics)
    if not f:
        return []
    data = telemetry._monthly(f)
    rows = [(m, v[2] if len(v) > 2 else None, v[1] if len(v) > 1 else None, v[0] if v else None) for m, v in data.items()]
    return [r for r in rows if r[1] is not None]


def ai_monthly(metrics):
    f = ai_file(metrics)
    if not f:
        return []
    out = []
    with open(f, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if missing := [c for c in AI_COLUMNS if c not in (reader.fieldnames or [])]:
            raise ValueError(f"{f.name} is missing the column(s) {', '.join(missing)}")
        for r in reader:
            out.append({"month": datetime.strptime(r["month"][:10], "%Y-%m-%d").date(),
                        "generated": int(r["suggestions_generated"]), "applied": int(r["suggestions_applied"]),
                        "days": int(r["active_usage_days"]),
                        "first": date.fromisoformat(r["first_day"]), "last": date.fromisoformat(r["last_day"])})
    return out


def ai_periods(ai, enabled):
    """(before, after): months up to and including the month AI CodeFix was enabled vs. later
    months, or the older vs. the newer half of the export when no date is given."""
    if enabled:
        cut = (enabled.year, enabled.month)
        return ([r for r in ai if (r["month"].year, r["month"].month) <= cut],
                [r for r in ai if (r["month"].year, r["month"].month) > cut])
    half = len(ai) // 2
    return ai[:half], ai[half:]


def pct(a, b):
    return (b / a - 1) * 100 if a else 0


def short(d):
    return f"{d:%b} {d.day}"


def span(rows):
    """'Jun–Oct', 'May', or 'Nov 2025–Feb 2026' for a list of monthly rows."""
    a, b = rows[0]["month"], rows[-1]["month"]
    if (a.year, a.month) == (b.year, b.month):
        return f"{a:%b}"
    return f"{a:%b}–{b:%b}" if a.year == b.year else f"{a:%b %Y}–{b:%b %Y}"


def filename(text):
    return text.replace("–", "-").replace("/", "-").replace(".", "") + ".png"


# ---------------------------------------------------------------- charts

def chart_loc_usage(rows, name, upgrade, out):
    year = [r for r in rows if r[0] >= datetime(rows[-1][0].year - 1, 12, 1)]  # Dec of last year -> now
    xs = list(range(len(year)))
    labels = [r[0].strftime("%b\n%Y") if r[0].month in (1, 12) else r[0].strftime("%b") for r in year]
    total = [r[1] for r in year]
    active = [(i, r[2]) for i, r in enumerate(year) if r[2]]

    fig = figure(f"{name} LOC Usage {year[-1][0].year}")
    ax = fig.add_axes([0.09, 0.15, 0.6, 0.63])
    style_axes(ax, ylabel="Lines of Code")
    ax.plot(xs, total, color=AXIS, lw=2.6, marker="o", ms=5, mfc=AXIS, label="Licensed LOC", zorder=3)
    if active:
        ax.plot([i for i, _ in active], [a for _, a in active], color=LAVENDER, lw=2.4, ls=(0, (4, 2.5)),
                marker="o", ms=4.5, mfc=LAVENDER, label="LOC in active projects", zorder=3)
    ax.yaxis.set_major_formatter(millions)
    ax.set_ylim(0, max(total) * 1.22)
    ax.set_xticks(xs, labels)
    ax.set_xlim(-0.4, len(xs) - 0.6)
    ax.legend(loc="lower right", frameon=False, fontsize=8.5, labelcolor=INK)

    peak_i = max(range(len(total)), key=total.__getitem__)
    n = 1
    if upgrade:
        month, label = upgrade
        ui = next((i for i, (m, *_) in enumerate(year) if (m.year, m.month) == month), None)
        if ui is not None:
            badge(ax, ui, total[ui], n, f"Upgrade to {label}" if label else "Upgrade", dy=30, dx=12, ha="right")
            n += 1
    badge(ax, peak_i, total[peak_i], n, f"Peak {total[peak_i] / 1e6:.1f}M", dy=20, dx=12, ha="right")
    n += 1
    if peak_i != len(total) - 1:
        badge(ax, len(total) - 1, total[-1] * 0.62, n, f"{pct(total[peak_i], total[-1]):+.0f}% from peak", dx=12, ha="right")
        ax.annotate("", (len(total) - 1, total[-1] * 0.96), xytext=(len(total) - 1, total[-1] * 0.66),
                    arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.4))

    m, cur, act, share = year[-1]
    rows_ = [(f"{cur / 1e6:.1f}M LOC", f"licensed usage, {m.strftime('%b %Y')}")]
    if act:
        share = share if share else act / cur
        rows_.append((f"{share * 100:.1f}% active", f"{act / 1e6:.1f}M LOC in active projects"))
    rows_.append((f"{pct(total[0], cur):+.1f}%", f"since {year[0][0].strftime('%b %Y')} ({(cur - total[0]) / 1e6:+.2f}M)"))
    panel(fig, (0.735, 0.13, 0.245, 0.67), "Current Usage", rows_,
          note=f"Peak {total[peak_i] / 1e6:.1f}M in {year[peak_i][0].strftime('%b %Y')}")
    first_active = year[active[0][0]][0].strftime("%B %Y") if active else None
    footnote(fig, "Licensed LOC = sum of each project's largest branch."
             + (f" Active-project LOC is reported from {first_active}." if first_active and active[0][0] > 0 else "")
             + " Source: SonarQube telemetry.")
    fig.savefig(out, facecolor="white")
    plt.close(fig)


def chart_loc_quarterly(rows, name, out):
    yr = rows[-1][0].year
    by_month = {(r[0].year, r[0].month): r[1] for r in rows}
    start, start_label = by_month.get((yr - 1, 12)), f"Dec {yr - 1}"
    if start is None:  # the export starts this year: measure from its first month
        first = min(k for k in by_month if k[0] == yr)
        start, start_label = by_month[first], f"{datetime(*first, 1):%b %Y}"
    quarters = []
    for q in range(1, 5):
        months = [(yr, mm) for mm in range(3 * q - 2, 3 * q + 1) if (yr, mm) in by_month]
        if not months:
            continue
        prev = (by_month.get((yr, 3 * q - 3)) if q > 1 else start) or by_month[months[0]]
        end = by_month[months[-1]]
        partial = len(months) < 3 and months[-1] == max(by_month)  # the current, unfinished quarter
        label = f"Q{q} {yr}" + (" QTD" if partial else "")
        span_ = f"{datetime(*months[0], 1):%b}–{datetime(*months[-1], 1):%b}" if len(months) > 1 else f"{datetime(*months[0], 1):%b}"
        quarters.append((label, span_, prev, end))

    fig = figure(f"{name} Quarterly LOC Growth {yr}")
    ax = fig.add_axes([0.09, 0.17, 0.6, 0.6])
    style_axes(ax, ylabel="Net LOC change")
    deltas = [e - s for _, _, s, e in quarters]
    xs = range(len(quarters))
    colors = [BLUE if d >= 0 else LAVENDER for d in deltas]
    bars = ax.bar(xs, deltas, width=0.55, color=colors, zorder=3)
    for i, ((label, span_, s, e), d) in enumerate(zip(quarters, deltas)):
        if "QTD" in label:
            bars[i].set_hatch("//")
            bars[i].set_edgecolor("white")
        va, off = ("bottom", 6) if d >= 0 else ("top", -6)
        ax.annotate(f"{d / 1e6:+.2f}M\n({pct(s, e):+.1f}%)", (i, d), xytext=(0, off), textcoords="offset points",
                    ha="center", va=va, fontsize=9.5, fontweight="semibold", color=INK)
    ax.axhline(0, color=AXIS, lw=1.2)
    ax.set_xticks(list(xs), [f"{l}\n{s}" for l, s, *_ in quarters], fontsize=9)
    lo, hi = min(deltas + [0]), max(deltas + [0])
    ax.set_ylim(lo * 1.45 if lo < 0 else 0, hi * 1.35 if hi > 0 else abs(lo) * 0.2 or 1)
    ax.yaxis.set_major_formatter(lambda v, p: ("+" if v > 0 else "") + millions(v) if v else "0")
    if any("QTD" in q[0] for q in quarters) and deltas[-1] < 0:
        badge(ax, len(quarters) - 1.42, deltas[-1] / 2, 1, "Decline\nquarter to date", dx=12, ha="right", size=8.5)

    end = quarters[-1][3]
    peak = max(r[1] for r in rows if r[0].year == yr)
    panel(fig, (0.735, 0.13, 0.245, 0.67), f"{yr} Year to Date", [
        (f"{(end - start) / 1e6:+.2f}M", f"net growth ({pct(start, end):+.1f}%) since {start_label}"),
        (f"{(peak - start) / 1e6:+.2f}M", f"growth to the peak ({pct(start, peak):+.1f}%)"),
        (f"{max(pct(s, e) for *_, s, e in quarters):+.1f}%", "fastest quarter"),
    ], note="Each quarter vs. the previous quarter end")
    footnote(fig, "Licensed LOC = sum of each project's largest branch. Source: SonarQube telemetry (LoC Usage export).")
    fig.savefig(out, facecolor="white")
    plt.close(fig)


def chart_ai_comparison(before, after, name, enabled, upgrade_label, out):
    agg = lambda rs, k: sum(r[k] for r in rs)
    b_label, a_label = span(before), span(after)
    b_span = f"{short(min(r['first'] for r in before))}–{short(max(r['last'] for r in before))}"
    a_span = f"{short(min(r['first'] for r in after))}–{short(max(r['last'] for r in after))}"
    metrics = [
        ("Suggestions\ngenerated", agg(before, "generated"), agg(after, "generated"), "{:,.0f}"),
        ("Suggestions\napplied", agg(before, "applied"), agg(after, "applied"), "{:,.0f}"),
        ("Active usage\ndays", agg(before, "days"), agg(after, "days"), "{:,.0f}"),
        ("Apply rate", agg(before, "applied") / max(agg(before, "generated"), 1) * 100,
         agg(after, "applied") / max(agg(after, "generated"), 1) * 100, "{:.1f}%"),
        ("Suggestions per\nactive day", agg(before, "generated") / max(agg(before, "days"), 1),
         agg(after, "generated") / max(agg(after, "days"), 1), "{:.1f}"),
    ]

    fig = figure(f"{name} AI CodeFix Usage: {b_label} vs. {a_label}")
    w = 0.165
    for i, (label, b, a, f) in enumerate(metrics):
        ax = fig.add_axes([0.07 + i * (w + 0.022), 0.15, w, 0.44])
        style_axes(ax)
        ax.grid(False)
        ax.spines["left"].set_visible(False)
        ax.set_yticks([])
        ax.bar([0, 1], [b, a], width=0.62, color=[LAVENDER, BLUE], zorder=3)
        for x, v in ((0, b), (1, a)):
            ax.annotate(f.format(v), (x, v), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                        fontsize=10, fontweight="semibold", color=INK)
        ax.set_ylim(0, max(a, b, 1e-9) * 1.3)
        ax.set_xticks([0, 1], [b_label + ("*" if enabled else ""), a_label], fontsize=8.5)
        ax.set_title(label, fontsize=10, color=BLUE, pad=10, fontweight="medium")
    if enabled:
        note = (f"* AI CodeFix was enabled on {enabled:%B} {enabled.day}, {enabled.year}"
                + (f" with the upgrade to {upgrade_label}" if upgrade_label else "")
                + f", so the {b_label} period contains\n   usage from {b_span} only ({agg(before, 'days')} active days). "
                f"{a_label} covers {a_span} ({agg(after, 'days')} active days).\n   Compare the per-day and rate metrics rather than the totals.")
    else:
        note = (f"{b_label} covers {b_span} ({agg(before, 'days')} active days); {a_label} covers {a_span} "
                f"({agg(after, 'days')} active days).\nCompare the per-day and rate metrics when the periods differ in length.")
    fig.text(0.07, 0.775, note, fontsize=8.5, color=MID, va="center", linespacing=1.5)
    footnote(fig, "Apply rate = suggestions applied / suggestions generated. Active usage day = a day with at least one suggestion generated.")
    fig.savefig(out, facecolor="white")
    plt.close(fig)


def chart_ai_monthly(rows, name, out):
    label = span(rows)
    same_year = rows[0]["month"].year == rows[-1]["month"].year
    xs = list(range(len(rows)))
    labels = []
    for r in rows:
        partial = r["last"].day < 28 and r is rows[-1]
        labels.append(f"{r['month']:%b}" + (f" 1–{r['last'].day}" if partial else "") + f"\n{r['days']} active days")

    fig = figure(f"{name} AI CodeFix Usage by Month, {label}" + (f" {rows[-1]['month'].year}" if same_year else ""))
    ax = fig.add_axes([0.09, 0.19, 0.6, 0.58])
    style_axes(ax, ylabel="Suggestions")
    bw = 0.36
    gen = ax.bar([x - bw / 2 for x in xs], [r["generated"] for r in rows], width=bw, color=BLUE, label="Generated", zorder=3)
    app = ax.bar([x + bw / 2 for x in xs], [r["applied"] for r in rows], width=bw, color=AXIS, label="Applied", zorder=3)
    for bars in (gen, app):
        for b in bars:
            ax.annotate(f"{b.get_height():,.0f}", (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="semibold", color=INK)
    if rows and rows[-1]["last"].day < 28:
        gen[-1].set_hatch("//"), gen[-1].set_edgecolor("white")
        app[-1].set_hatch("//"), app[-1].set_edgecolor("white")
    ax.set_xticks(xs, labels, fontsize=8.5)
    top = max(r["generated"] for r in rows)
    ax.set_ylim(0, max(top, 1) * 1.3)

    rate = ax.twinx()
    rate.plot(xs, [r["applied"] / r["generated"] * 100 if r["generated"] else 0 for r in rows], color=LAVENDER, lw=2.4,
              ls=(0, (4, 2.5)), marker="o", ms=6, mfc="white", mec=MID, mew=1.6, label="Apply rate", zorder=4)
    for side in ("top", "left", "bottom"):
        rate.spines[side].set_visible(False)
    rate.spines["right"].set_color(LAVENDER)
    rate.tick_params(length=0, labelsize=8.5, colors=MID)
    rate.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}%")
    rate.set_ylim(0, max(10, max(r["applied"] / max(r["generated"], 1) * 100 for r in rows) * 2.2))
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = rate.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", frameon=False, fontsize=8.5, labelcolor=INK, ncol=3)

    peak = max(rows, key=lambda r: r["generated"])
    tot_g, tot_a = sum(r["generated"] for r in rows), sum(r["applied"] for r in rows)
    first_half = rows[:2]
    later = [r for r in rows[2:] if r["last"].day >= 28]
    pr = [(f"{tot_g:,} / {tot_a:,}", "suggestions generated / applied"),
          (f"{peak['month']:%B}", f"busiest month ({peak['generated']:,} suggestions)")]
    if first_half and later:
        avg1 = sum(r["generated"] for r in first_half) / len(first_half)
        avg2 = sum(r["generated"] for r in later) / len(later)
        pr.append((f"{pct(avg1, avg2):+.0f}%", f"avg. monthly suggestions,\n{later[0]['month']:%b}–{later[-1]['month']:%b} vs. "
                                                  f"{first_half[0]['month']:%b}–{first_half[-1]['month']:%b}"))
    panel(fig, (0.735, 0.13, 0.245, 0.67), f"{label} Summary", pr,
          note=f"{rows[-1]['month']:%b} covers {short(rows[-1]['first'])}–{rows[-1]['last'].day} only" if rows[-1]["last"].day < 28 else None)
    footnote(fig, "Apply rate = suggestions applied / suggestions generated. Source: SonarQube AI CodeFix usage export.")
    fig.savefig(out, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- entry points

def make_charts(folder, upgrade=None, upgrade_label=None, codefix_enabled=None):
    """Charts for one customer folder -> (PNG paths written, messages for the user).

    upgrade: (year, month) of the LTA upgrade, marked on the LOC chart, upgrade_label the
    version it went to; codefix_enabled: the date AI CodeFix was turned on, which splits the
    before/after comparison (without it the export is split in half)."""
    folder = Path(folder)
    name = assess.customer_name(folder)
    metrics = folder / "metrics"
    out = folder / "output" / "charts"
    made, notes = [], []

    rows = loc_monthly(metrics)
    try:
        ai = ai_monthly(metrics)
    except ValueError as e:
        ai = []
        notes.append(f"AI CodeFix charts skipped: {e}.")
    if not rows and not ai and not notes and not loc_file(metrics):
        return [], [f"No metrics detected in {metrics}.\n\n" + METRICS_HELP.format(metrics=metrics)]
    out.mkdir(parents=True, exist_ok=True)

    if rows:
        yr = rows[-1][0].year
        chart_loc_usage(rows, name, (upgrade, upgrade_label) if upgrade else None, p := out / f"1 - LOC Usage {yr}.png"); made.append(p)
        chart_loc_quarterly(rows, name, p := out / f"2 - Quarterly LOC Growth {yr}.png"); made.append(p)
    elif f := loc_file(metrics):
        notes.append(f"LOC charts skipped: {f.name} has no monthly licensed-LOC rows.")
    else:
        notes.append(f'LOC charts skipped: no CSV with "loc" in its name in {metrics}.')

    if ai:
        before, after = ai_periods(ai, codefix_enabled)
        if before and after:
            p = out / filename(f"3 - AI CodeFix {span(before)} vs {span(after)}")
            chart_ai_comparison(before, after, name, codefix_enabled, upgrade_label, p); made.append(p)
        else:
            notes.append("AI CodeFix before/after chart skipped: the export has no months "
                         + ("after the enable date." if codefix_enabled and before else "on both sides of the split."))
        if after:
            chart_ai_monthly(after, name, p := out / filename(f"4 - AI CodeFix by Month {span(after)}")); made.append(p)
    elif not ai_file(metrics):
        notes.append(f'AI CodeFix charts skipped: no CSV with "codefix" in its name in {metrics}.')
    return made, notes


def main():
    ap = argparse.ArgumentParser(description="Annex charts from a customer's metrics/ CSV exports.")
    ap.add_argument("customer")
    ap.add_argument("--upgrade", metavar="YYYY-MM", help="month of the LTA upgrade, marked on the LOC chart")
    ap.add_argument("--upgrade-label", metavar="VERSION", help='version upgraded to, e.g. "2025.4.6 LTA"')
    ap.add_argument("--codefix-enabled", metavar="YYYY-MM-DD", help="date AI CodeFix was enabled (splits the before/after chart)")
    args = ap.parse_args()

    try:
        folder = assess.find_customer(args.customer)
        up = datetime.strptime(args.upgrade, "%Y-%m") if args.upgrade else None
        enabled = date.fromisoformat(args.codefix_enabled) if args.codefix_enabled else None
    except assess.AssessError as e:
        sys.exit(str(e))
    except ValueError as e:
        sys.exit(f"Bad date: {e}")
    made, notes = make_charts(folder, (up.year, up.month) if up else None, args.upgrade_label, enabled)
    for n in notes:
        print(n, file=sys.stderr)
    for p in made:
        print(p)


if __name__ == "__main__":
    main()
