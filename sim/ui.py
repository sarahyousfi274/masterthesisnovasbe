"""Visual layer: design tokens, global CSS and small HTML components.

The app is light only. The theme is fixed in .streamlit/config.toml and the CSS
below repeats every colour with !important, so the page looks the same even if
the config file is missing or the viewer's system is in dark mode.

HTML strings are built without leading indentation, because Streamlit's
markdown renderer turns indented lines into code blocks.
"""

from __future__ import annotations

import html

import streamlit as st

from . import content, state as game

INK = "#0E1116"
INK_2 = "#3D4450"
MUTED = "#6B7280"
LINE = "#E6E8EC"
BG = "#F7F7F5"
CARD = "#FFFFFF"
ACCENT = "#3346D3"
ACCENT_SOFT = "#EEF0FD"
ACCENT_LINE = "#C9CFF7"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {{ color-scheme: light only; }}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
  background: {BG} !important; color: {INK} !important;
}}
html, body, .stApp, .stApp p, .stApp div, .stApp label, .stApp li, .stApp input,
.stApp textarea, .stApp button, .stApp h1, .stApp h2, .stApp h3,
.stApp span:not([data-testid="stIconMaterial"]) {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
.stApp code, .stApp pre {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
.block-container {{ max-width: 44rem; padding-top: 1.6rem; padding-bottom: 5rem; }}
div[data-testid="stToolbar"], #MainMenu, header[data-testid="stHeader"], footer,
div[data-testid="stDecoration"], div[data-testid="stStatusWidget"] {{
  visibility: hidden; height: 0; position: fixed;
}}
h1, h2, h3, h4, p, li, label, span {{ color: {INK}; }}
h1 {{ font-size: 2.1rem !important; font-weight: 700 !important; letter-spacing: -0.03em; }}
div[data-testid="stMarkdownContainer"] p {{ font-size: 1rem; line-height: 1.65; color: {INK_2}; }}
div[data-testid="stMarkdownContainer"] strong {{ color: {INK}; }}
a {{ color: {ACCENT} !important; }}

/* ---------- buttons ---------- */
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {{
  background: {INK} !important; border: 1px solid {INK} !important;
  border-radius: 999px !important; padding: 0.6rem 1.6rem !important;
  min-height: 2.75rem; transition: transform 80ms ease, background 120ms ease;
}}
button[data-testid="stBaseButton-primary"] *,
button[data-testid="stBaseButton-primaryFormSubmit"] * {{
  color: #FFFFFF !important; font-weight: 600 !important;
}}
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover {{ background: #262B35 !important; }}
button[data-testid="stBaseButton-primary"]:active,
button[data-testid="stBaseButton-primaryFormSubmit"]:active {{ transform: scale(0.98); }}
button[data-testid="stBaseButton-secondary"],
button[data-testid="stBaseButton-secondaryFormSubmit"],
button[data-testid="stPopoverButton"] {{
  background: {CARD} !important; border: 1px solid {LINE} !important;
  border-radius: 999px !important; color: {INK} !important; min-height: 2.75rem;
}}
button[data-testid="stPopoverButton"] {{ min-height: 2.2rem; padding: 0.3rem 0.9rem !important; }}
button[data-testid="stBaseButton-secondary"] *,
button[data-testid="stPopoverButton"] * {{ color: {INK_2} !important; }}
button[data-testid="stBaseButton-secondary"]:hover,
button[data-testid="stPopoverButton"]:hover {{ border-color: {INK_2} !important; }}

button[data-testid="stBaseButton-tertiary"] {{ padding: 0 !important; min-height: 0 !important; }}
button[data-testid="stBaseButton-tertiary"] * {{ color: {MUTED} !important; font-size: 0.88rem !important; }}
button[data-testid="stBaseButton-tertiary"]:hover * {{ color: {INK} !important; }}

/* ---------- forms and inputs ---------- */
div[data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
input, textarea, div[data-baseweb="input"],
div[data-baseweb="textarea"], div[data-baseweb="base-input"] {{
  background: {CARD} !important; color: {INK} !important; border-radius: 10px !important;
}}
div[data-baseweb="select"] {{ background: {CARD} !important; border: 1px solid {LINE} !important;
  border-radius: 10px !important; }}
div[data-baseweb="select"] div {{ background: transparent !important; border-color: transparent !important; }}
div[data-baseweb="select"]:focus-within {{ border-color: {ACCENT} !important; box-shadow: 0 0 0 3px {ACCENT_SOFT} !important; }}
div[data-baseweb="input"], div[data-baseweb="textarea"] {{
  border: 1px solid {LINE} !important;
}}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within {{ border-color: {ACCENT} !important;
  box-shadow: 0 0 0 3px {ACCENT_SOFT} !important; }}
div[data-testid="stSelectbox"] > div > div, div[data-testid="stNumberInputContainer"],
div[data-testid="stTextInputRootElement"], div[data-testid="stTextAreaRootElement"] {{
  background: {CARD} !important; border: 1px solid {LINE} !important; border-radius: 10px !important;
}}
div[data-testid="stSelectbox"] > div > div:focus-within, div[data-testid="stNumberInputContainer"]:focus-within,
div[data-testid="stTextInputRootElement"]:focus-within, div[data-testid="stTextAreaRootElement"]:focus-within {{
  border-color: {ACCENT} !important; box-shadow: 0 0 0 3px {ACCENT_SOFT} !important;
}}
div[data-testid="stSelectbox"] input, div[data-testid="stNumberInputContainer"] input,
div[data-testid="stNumberInputContainer"] > div, div[data-testid="stTextInputRootElement"] > div {{
  background: transparent !important; border: none !important; box-shadow: none !important;
}}
button[data-testid="stNumberInputStepUp"], button[data-testid="stNumberInputStepDown"] {{
  display: none !important;
}}
div[data-testid="stWidgetLabel"] p {{ font-weight: 500; color: {INK} !important; font-size: 0.95rem; }}
ul[role="listbox"], div[data-baseweb="popover"] li {{ background: {CARD} !important; color: {INK} !important; }}

/* ---------- answer cards (radio) ---------- */
div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]),
div[data-testid="stRadio"], div[data-testid="stRadio"] > div {{ width: 100% !important; }}
div[role="radiogroup"] {{ gap: 0.5rem; width: 100% !important; display: flex; flex-direction: column; }}
div[role="radiogroup"] > label {{ align-self: stretch; }}
label[data-testid="stRadioOption"] {{
  display: flex; align-items: center; width: 100%; box-sizing: border-box;
  padding: 0.85rem 1rem; margin: 0; border-radius: 12px;
  border: 1px solid {LINE} !important; background: {CARD} !important;
  box-shadow: 0 1px 2px rgba(14,17,22,0.04);
  transition: border-color 120ms ease, background 120ms ease, box-shadow 120ms ease;
}}
label[data-testid="stRadioOption"] * {{ color: {INK} !important; }}
label[data-testid="stRadioOption"]:hover {{ border-color: {ACCENT_LINE} !important; }}
label[data-testid="stRadioOption"]:has(input:checked) {{
  border-color: {ACCENT} !important; background: {ACCENT_SOFT} !important;
  box-shadow: 0 0 0 1px {ACCENT} inset;
}}
div[role="radiogroup"][aria-orientation="horizontal"] {{ flex-direction: row; flex-wrap: wrap; }}
div[role="radiogroup"][aria-orientation="horizontal"] > label {{ align-self: auto; }}
div[role="radiogroup"][aria-orientation="horizontal"] label[data-testid="stRadioOption"] {{
  width: auto; padding: 0.5rem 0.9rem;
}}

/* ---------- pills ---------- */
div[data-testid="stButtonGroup"] button[data-testid="stBaseButton-pills"] {{
  background: {CARD} !important; border: 1px solid {LINE} !important;
  border-radius: 999px !important; min-width: 2.75rem; min-height: 2.5rem;
}}
div[data-testid="stButtonGroup"] button[data-testid="stBaseButton-pills"] * {{ color: {INK} !important; }}
div[data-testid="stButtonGroup"] button[data-testid="stBaseButton-pills"]:hover {{
  border-color: {ACCENT_LINE} !important;
}}
div[data-testid="stButtonGroup"] button[data-testid="stBaseButton-pillsActive"] {{
  background: {ACCENT} !important; border: 1px solid {ACCENT} !important;
  border-radius: 999px !important; min-width: 2.75rem; min-height: 2.5rem;
}}
div[data-testid="stButtonGroup"] button[data-testid="stBaseButton-pillsActive"] * {{
  color: #FFFFFF !important;
}}

/* ---------- alerts ---------- */
div[data-testid="stAlert"] {{ border-radius: 12px; }}
div[data-testid="stAlert"] * {{ color: {INK} !important; }}

/* ---------- popover ---------- */
div[data-testid="stPopoverBody"] {{ background: {CARD} !important; border-radius: 12px; }}
div[data-testid="stPopoverBody"] * {{ color: {INK_2} !important; font-size: 0.92rem; }}

/* ---------- custom components ---------- */
.fs-steps {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.6rem; }}
.fs-steps::-webkit-scrollbar {{ display: none; }}
.fs-step {{ white-space: nowrap; font-size: 0.75rem; font-weight: 500; letter-spacing: 0.01em;
  padding: 0.28rem 0.7rem; border-radius: 999px; color: {MUTED}; background: transparent;
  border: 1px solid {LINE}; }}
.fs-step.done {{ color: {INK_2}; background: {CARD}; }}
.fs-step.done::before {{ content: "✓ "; color: {ACCENT}; }}
.fs-step.now {{ color: #FFFFFF; background: {INK}; border-color: {INK}; }}
.fs-bar {{ height: 3px; background: {LINE}; border-radius: 3px; overflow: hidden; margin-bottom: 1.6rem; }}
.fs-bar > div {{ height: 100%; background: {ACCENT}; border-radius: 3px; transition: width 300ms ease; }}

.fs-eyebrow {{ font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
  color: {ACCENT}; margin-bottom: 0.35rem; }}
.fs-eyebrow.muted {{ color: {MUTED}; }}
.fs-q {{ font-size: 1.32rem; font-weight: 650; line-height: 1.4; letter-spacing: -0.015em;
  color: {INK}; margin: 0 0 0.55rem 0; }}
.fs-body {{ font-size: 1rem; line-height: 1.6; color: {INK_2}; margin: 0 0 1rem 0; }}
.fs-body b {{ color: {INK}; font-weight: 600; }}
.fs-note {{ display: inline-block; font-size: 0.8rem; color: {INK_2}; background: {CARD};
  border: 1px solid {LINE}; border-radius: 999px; padding: 0.2rem 0.7rem; margin-bottom: 0.9rem; }}

.fs-hud {{ display: flex; flex-wrap: wrap; gap: 0.4rem 1.1rem; font-size: 0.82rem; color: {MUTED};
  background: {CARD}; border: 1px solid {LINE}; border-radius: 12px; padding: 0.55rem 0.9rem;
  margin-bottom: 1.3rem; }}
.fs-hud b {{ color: {INK}; font-weight: 600; margin-left: 0.25rem; }}

.fs-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.6rem; margin: 0.4rem 0 0.6rem 0; }}
.fs-grid.two {{ grid-template-columns: repeat(2, minmax(0, 1fr)); margin: 0 0 1.2rem 0; }}
@media (max-width: 640px) {{ .fs-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
.fs-card {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.8rem 0.9rem;
  box-shadow: 0 1px 2px rgba(14,17,22,0.04); }}
.fs-card .lbl {{ font-size: 0.78rem; color: {MUTED}; display: flex; align-items: center; gap: 0.3rem; }}
.fs-card .val {{ font-size: 1.22rem; font-weight: 650; color: {INK}; margin-top: 0.15rem; letter-spacing: -0.01em; }}
.fs-card .dl {{ display: inline-block; margin-top: 0.3rem; font-size: 0.74rem; font-weight: 500; color: {INK_2};
  background: {BG}; border: 1px solid {LINE}; border-radius: 999px; padding: 0.05rem 0.5rem; }}
.fs-card .scale {{ display: flex; gap: 3px; margin-top: 0.45rem; }}
.fs-card .scale span {{ flex: 1; height: 5px; border-radius: 3px; background: {LINE}; }}
.fs-card .scale span.on {{ background: {ACCENT}; }}
.fs-card .ends {{ display: flex; justify-content: space-between; font-size: 0.68rem; color: {MUTED}; margin-top: 0.2rem; }}

.fs-tip {{ position: relative; display: inline-flex; width: 15px; height: 15px; border-radius: 50%;
  border: 1px solid {MUTED}; color: {MUTED}; font-size: 0.62rem; font-weight: 600; align-items: center;
  justify-content: center; cursor: help; font-style: normal; }}
.fs-tip:hover::after, .fs-tip:focus::after {{ content: attr(data-tip); position: absolute; left: -0.5rem; top: 1.4rem;
  width: 15rem; z-index: 20; background: {INK}; color: #fff; font-size: 0.78rem; font-weight: 400; line-height: 1.45;
  padding: 0.55rem 0.7rem; border-radius: 8px; box-shadow: 0 6px 20px rgba(14,17,22,0.18); }}

.fs-changes {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.4rem 0.9rem; margin-bottom: 1.3rem; }}
.fs-changes .row {{ display: flex; justify-content: space-between; gap: 1rem; padding: 0.55rem 0;
  border-bottom: 1px solid {LINE}; font-size: 0.9rem; color: {INK_2}; }}
.fs-changes .row:last-child {{ border-bottom: none; }}
.fs-changes .row span:last-child {{ color: {INK}; font-weight: 500; text-align: right; white-space: nowrap; }}

.fs-points {{ display: grid; gap: 0.6rem; margin: 0.6rem 0 1.2rem 0; }}
.fs-point {{ display: flex; gap: 0.8rem; background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.85rem 1rem; }}
.fs-point .n {{ flex: none; width: 1.7rem; height: 1.7rem; border-radius: 50%; background: {ACCENT_SOFT}; color: {ACCENT};
  font-weight: 650; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; }}
.fs-point .t {{ font-weight: 600; color: {INK}; font-size: 0.95rem; }}
.fs-point .d {{ color: {INK_2}; font-size: 0.9rem; line-height: 1.5; margin-top: 0.1rem; }}

.fs-range {{ margin: 0.2rem 0 1.1rem 0; }}
.fs-range .track {{ display: grid; grid-template-columns: 1fr 8fr 1fr; height: 30px; border-radius: 8px; overflow: hidden;
  font-size: 0.72rem; font-weight: 500; }}
.fs-range .track div {{ display: flex; align-items: center; justify-content: center; }}
.fs-range .edge {{ background: {LINE}; color: {MUTED}; }}
.fs-range .mid {{ background: {ACCENT_SOFT}; color: {ACCENT}; border-left: 2px solid {ACCENT}; border-right: 2px solid {ACCENT}; }}
.fs-range .labels {{ display: grid; grid-template-columns: 1fr 1fr; font-size: 0.75rem; color: {MUTED}; margin-top: 0.3rem; }}
.fs-range .labels div:last-child {{ text-align: right; }}

.fs-chart {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.9rem 0.9rem 0.5rem 0.9rem; margin-bottom: 1.1rem; }}
.fs-chart .cap {{ font-size: 0.78rem; color: {MUTED}; margin-bottom: 0.3rem; }}

.fs-echo {{ font-size: 0.8rem; color: {MUTED}; margin: -0.5rem 0 0.6rem 0; }}
.fs-hero {{ padding: 0.4rem 0 0.2rem 0; }}
.fs-hero .lead {{ font-size: 1.1rem; color: {INK_2}; margin-top: -0.3rem; }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def _h(text: str) -> str:
    return html.escape(str(text), quote=True)


def html_block(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section bar
# ---------------------------------------------------------------------------

def steps(sections: list[str], current: str | None, progress: float) -> None:
    if not current:
        return
    idx = sections.index(current) if current in sections else -1
    chips = []
    for i, sec in enumerate(sections):
        cls = "done" if i < idx else "now" if i == idx else ""
        chips.append(f'<div class="fs-step {cls}">{_h(sec)}</div>')
    pct = max(2, min(100, round(progress * 100)))
    html_block(f'<div class="fs-steps">{"".join(chips)}</div>'
               f'<div class="fs-bar"><div style="width:{pct}%"></div></div>')


# ---------------------------------------------------------------------------
# Text pieces
# ---------------------------------------------------------------------------

def eyebrow(text: str, muted: bool = False) -> None:
    html_block(f'<div class="fs-eyebrow{" muted" if muted else ""}">{_h(text)}</div>')


def question(text: str, body: str | None = None) -> None:
    """Question title plus optional body. Body may contain simple <b> tags."""
    out = f'<div class="fs-q">{_h(text)}</div>'
    if body:
        safe = _h(body).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
        out += f'<div class="fs-body">{safe}</div>'
    html_block(out)


def note(text: str) -> None:
    html_block(f'<div class="fs-note">{_h(text)}</div>')


def points(items: list[tuple[str, str]]) -> None:
    rows = "".join(
        f'<div class="fs-point"><div class="n">{i}</div><div>'
        f'<div class="t">{_h(t)}</div><div class="d">{_h(d)}</div></div></div>'
        for i, (t, d) in enumerate(items, start=1))
    html_block(f'<div class="fs-points">{rows}</div>')


# ---------------------------------------------------------------------------
# Situation
# ---------------------------------------------------------------------------

def _visible_fields(state: dict) -> list[tuple[str, str, str]]:
    out = []
    for key, label, help_text in content.STATUS_FIELDS:
        if key == "pending_hires" and not state.get("pending_hires"):
            continue
        out.append((key, label, help_text))
    return out


def status_cards(state: dict, before: dict | None = None) -> None:
    """Cards for the situation, with the change since `before` if given."""
    cards, scales = [], []
    for key, label, help_text in _visible_fields(state):
        value = game.format_value(key, state)
        delta = ""
        if before is not None:
            d = (state.get(key) or 0) - (before.get(key) or 0)
            if d:
                delta = f'<div class="dl">{_h(game.format_delta(key, d))}</div>'
        extra = ""
        if key in ("morale", "market_confidence"):
            v = int(state.get(key) or 0)
            bars = "".join(f'<span class="{"on" if i < v else ""}"></span>' for i in range(5))
            extra = (f'<div class="scale">{bars}</div>'
                     f'<div class="ends"><span>low</span><span>high</span></div>')
        card = (f'<div class="fs-card"><div class="lbl">{_h(label)}'
                f'<i class="fs-tip" tabindex="0" data-tip="{_h(help_text)}">i</i></div>'
                f'<div class="val">{_h(value)}</div>{delta}{extra}</div>')
        (scales if extra else cards).append(card)
    html_block(f'<div class="fs-grid">{"".join(cards)}</div>'
               f'<div class="fs-grid two">{"".join(scales)}</div>')


def hud(state: dict) -> None:
    """Compact strip of the key numbers on every simulation question."""
    items = [("Cash", game.format_value("cash", state)),
             ("Burn", game.format_value("burn", state) + "/mo"),
             ("Runway", game.format_value("runway", state)),
             ("Team", game.format_value("team_size", state)),
             ("Customers", game.format_value("customers", state))]
    if state.get("pending_hires"):
        items.insert(4, ("Open roles", str(state["pending_hires"])))
    inner = "".join(f'<span>{_h(k)}<b>{_h(v)}</b></span>' for k, v in items)
    html_block(f'<div class="fs-hud">{inner}</div>')


def changes(events: list[dict]) -> None:
    if not events:
        return
    rows = []
    for ev in events:
        parts = []
        for key, d in ev["delta"].items():
            label = dict((k, l) for k, l, _ in content.STATUS_FIELDS).get(key, key)
            parts.append(f"{label} {game.format_delta(key, d)}")
        if not parts:
            continue
        rows.append(f'<div class="row"><span>{_h(ev["label"])}</span>'
                    f'<span>{_h(" · ".join(parts))}</span></div>')
    if rows:
        html_block(f'<div class="fs-changes">{"".join(rows)}</div>')


# ---------------------------------------------------------------------------
# Interval helpers
# ---------------------------------------------------------------------------

def range_diagram(left: str, right: str) -> None:
    html_block(
        '<div class="fs-range"><div class="track">'
        '<div class="edge">1 in 10</div>'
        '<div class="mid">about 8 in 10 land between your two numbers</div>'
        '<div class="edge">1 in 10</div></div>'
        f'<div class="labels"><div>{_h(left)}</div><div>{_h(right)}</div></div></div>')


def bar_chart(series: list[tuple[str, float, str | None]], unit_fmt, caption: str,
              future_label: str) -> None:
    """Small SVG bar chart of a past series, with an empty 'future' slot."""
    w, h, pad_b, pad_t = 600, 190, 34, 26
    n = len(series)
    slot = w / (n + 1.6)
    bw = slot * 0.58
    vmax = max(v for _, v, _ in series) * 1.15
    parts = []
    for i, (lab, v, chg) in enumerate(series):
        x = slot * i + (slot - bw) / 2 + 6
        bh = (h - pad_b - pad_t) * v / vmax
        y = h - pad_b - bh
        fill = ACCENT if i == n - 1 else "#AAB3EF"
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="6" fill="{fill}"/>')
        parts.append(f'<text x="{x + bw / 2:.1f}" y="{y - 7:.1f}" text-anchor="middle" font-size="13" '
                     f'font-weight="600" fill="{INK}">{_h(unit_fmt(v))}</text>')
        parts.append(f'<text x="{x + bw / 2:.1f}" y="{h - 12:.1f}" text-anchor="middle" font-size="11.5" '
                     f'fill="{MUTED}">{_h(lab)}</text>')
        if chg:
            parts.append(f'<text x="{x + bw / 2:.1f}" y="{y + 17:.1f}" text-anchor="middle" font-size="11" '
                         f'font-weight="600" fill="#FFFFFF">{_h(chg)}</text>')
    fx = slot * n + 10
    fw = w - fx - 4
    parts.append(f'<rect x="{fx:.1f}" y="{pad_t:.1f}" width="{fw:.1f}" height="{h - pad_b - pad_t:.1f}" rx="8" '
                 f'fill="{ACCENT_SOFT}" stroke="{ACCENT}" stroke-dasharray="5 5"/>')
    parts.append(f'<text x="{fx + fw / 2:.1f}" y="{(h - pad_b + pad_t) / 2 + 6:.1f}" text-anchor="middle" '
                 f'font-size="22" font-weight="700" fill="{ACCENT}">?</text>')
    parts.append(f'<text x="{fx + fw / 2:.1f}" y="{h - 12:.1f}" text-anchor="middle" font-size="11.5" '
                 f'fill="{ACCENT}" font-weight="600">{_h(future_label)}</text>')
    svg = (f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{_h(caption)}" '
           f'xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>')
    html_block(f'<div class="fs-chart"><div class="cap">{_h(caption)}</div>{svg}</div>')
