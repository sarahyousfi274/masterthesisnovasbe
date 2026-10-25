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

INK = "#14231C"
INK_2 = "#3B4740"
MUTED = "#6A6556"
LINE = "#E2DACB"
BG = "#F4EFE6"
CARD = "#FFFDF8"
ACCENT = "#2D6A4F"
GREEN = "#123528"          # dark green: top panel, buttons, curtains
GREEN_2 = "#1B4636"
ACCENT_SOFT = "#E5EFE8"
ACCENT_LINE = "#A8CBB6"

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
h1 {{ font-size: 1.75rem !important; font-weight: 700 !important; letter-spacing: -0.03em; }}
div[data-testid="stMarkdownContainer"] p {{ font-size: 1rem; line-height: 1.65; color: {INK_2}; }}
div[data-testid="stMarkdownContainer"] strong {{ color: {INK}; }}
a {{ color: {ACCENT} !important; }}

/* ---------- buttons ---------- */
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {{
  background: {GREEN} !important; border: 1px solid {GREEN} !important;
  border-radius: 999px !important; padding: 0.6rem 1.6rem !important;
  min-height: 2.75rem; transition: transform 80ms ease, background 120ms ease;
}}
button[data-testid="stBaseButton-primary"] *,
button[data-testid="stBaseButton-primaryFormSubmit"] * {{
  color: #FFFFFF !important; font-weight: 600 !important;
}}
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover {{ background: #1B4636 !important; }}
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
button[data-testid="stBaseButton-tertiary"] * {{ color: {MUTED} !important; font-size: 0.875rem !important; }}
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
div[data-testid="stWidgetLabel"] p {{ font-weight: 500; color: {INK} !important; font-size: 1rem; }}
ul[role="listbox"], div[data-baseweb="popover"] li {{ background: {CARD} !important; color: {INK} !important; }}

div[data-testid="InputInstructions"] {{ display: none !important; }}
input, textarea {{ color: {INK} !important; -webkit-text-fill-color: {INK} !important; caret-color: {ACCENT}; }}
input::placeholder, textarea::placeholder {{ color: #A49D8C !important; -webkit-text-fill-color: #A49D8C !important; }}
*:focus-visible {{ outline-color: {ACCENT} !important; }}

/* ---------- answer cards (radio) ---------- */
div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]),
div[data-testid="stRadio"], div[data-testid="stRadio"] > div {{ width: 100% !important; }}
div[role="radiogroup"] {{ gap: 0.5rem; width: 100% !important; display: flex; flex-direction: column; }}
div[role="radiogroup"] {{ align-items: stretch !important; }}
div[role="radiogroup"] > div, div[role="radiogroup"] > label {{ width: 100% !important; align-self: stretch; }}
label[data-testid="stRadioOption"] {{
  display: flex; align-items: center; width: 100%; box-sizing: border-box;
  padding: 0.85rem 1rem; margin: 0; border-radius: 12px;
  border: 1px solid {LINE} !important; background: {CARD} !important;
  box-shadow: 0 1px 2px rgba(18,53,40,0.04);
  transition: border-color 120ms ease, background 120ms ease, box-shadow 120ms ease;
}}
label[data-testid="stRadioOption"] * {{ color: {INK} !important; }}
label[data-testid="stRadioOption"]:hover {{ border-color: {ACCENT_LINE} !important; }}
label[data-testid="stRadioOption"]:has(input:checked) {{
  border-color: {ACCENT} !important; background: {ACCENT_SOFT} !important;
  box-shadow: 0 0 0 1px {ACCENT} inset;
}}
div[role="radiogroup"][aria-orientation="horizontal"] {{ flex-direction: row; flex-wrap: wrap; }}
div[role="radiogroup"][aria-orientation="horizontal"] {{ align-items: center !important; }}
div[role="radiogroup"][aria-orientation="horizontal"] > div,
div[role="radiogroup"][aria-orientation="horizontal"] > label {{ width: auto !important; align-self: auto; }}
div[role="radiogroup"][aria-orientation="horizontal"] label[data-testid="stRadioOption"] {{
  width: auto; padding: 0.5rem 0.9rem;
}}

/* ---------- pills ---------- */
div[data-testid="stButtonGroup"] button {{
  background: {CARD} !important; border: 1px solid {LINE} !important; color: {INK} !important;
  border-radius: 999px !important;
}}
div[data-testid="stButtonGroup"] button * {{ color: {INK} !important; }}
div[data-testid="stButtonGroup"] button[aria-pressed="true"],
div[data-testid="stButtonGroup"] button[aria-checked="true"],
div[data-testid="stButtonGroup"] button[kind$="Active"] {{
  background: {ACCENT} !important; border-color: {ACCENT} !important;
}}
div[data-testid="stButtonGroup"] button[aria-pressed="true"] *,
div[data-testid="stButtonGroup"] button[aria-checked="true"] *,
div[data-testid="stButtonGroup"] button[kind$="Active"] * {{ color: #FFFFFF !important; }}
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
div[data-testid="stPopoverBody"] * {{ color: {INK_2} !important; font-size: 0.875rem; }}

/* ---------- custom components ---------- */
.fs-steps {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.6rem; }}
.fs-steps::-webkit-scrollbar {{ display: none; }}
.fs-step {{ white-space: nowrap; font-size: 0.8rem; font-weight: 500; letter-spacing: 0.01em;
  padding: 0.28rem 0.7rem; border-radius: 999px; color: #645E50; background: #EFEBE2;
  border: 1px solid #EFEBE2; }}
.fs-step.done {{ color: {INK_2}; background: {CARD}; }}
.fs-step.done::before {{ content: "✓ "; color: {ACCENT}; }}
.fs-step.now {{ color: #FFFFFF; background: {GREEN}; border-color: {GREEN}; }}
.fs-bar {{ height: 3px; background: {LINE}; border-radius: 3px; overflow: hidden; margin-bottom: 1.6rem; }}
.fs-bar > div {{ height: 100%; background: {ACCENT}; border-radius: 3px; transition: width 300ms ease; }}

.fs-eyebrow {{ font-size: 0.8rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
  color: {ACCENT}; margin-bottom: 0.35rem; }}
.fs-eyebrow.muted {{ color: {MUTED}; }}
.fs-q {{ font-size: 1.25rem; font-weight: 650; line-height: 1.4; letter-spacing: -0.015em;
  color: {INK}; margin: 0 0 0.55rem 0; }}
.fs-body {{ font-size: 1rem; line-height: 1.6; color: {INK_2}; margin: 0 0 1rem 0; }}
.fs-body b {{ color: {INK}; font-weight: 600; }}
.fs-note {{ display: inline-block; font-size: 0.8rem; color: {INK_2}; background: {CARD};
  border: 1px solid {LINE}; border-radius: 999px; padding: 0.2rem 0.7rem; margin-bottom: 0.9rem; }}

.fs-hud {{ display: flex; flex-wrap: wrap; gap: 0.4rem 1.1rem; font-size: 0.8rem; color: {MUTED};
  background: {CARD}; border: 1px solid {LINE}; border-radius: 12px; padding: 0.55rem 0.9rem;
  margin-bottom: 1.3rem; }}
.fs-hud b {{ color: {INK}; font-weight: 600; margin-left: 0.25rem; }}

.fs-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.6rem; margin: 0.4rem 0 0.6rem 0; }}
.fs-grid.two {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); margin: 0 0 1.2rem 0; }}
@media (max-width: 640px) {{ .fs-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
.fs-card {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.8rem 0.9rem;
  box-shadow: 0 1px 2px rgba(18,53,40,0.04); }}
.fs-card .lbl {{ font-size: 0.8rem; color: {MUTED}; display: flex; align-items: center; gap: 0.3rem; }}
.fs-card .val {{ font-size: 1.25rem; font-weight: 650; color: {INK}; margin-top: 0.15rem; letter-spacing: -0.01em; line-height: 1.2; }}
.fs-card .dl {{ display: inline-block; margin-top: 0.3rem; font-size: 0.8rem; font-weight: 500; color: {INK_2};
  background: {BG}; border: 1px solid {LINE}; border-radius: 999px; padding: 0.05rem 0.5rem; }}
.fs-card .scale {{ display: flex; gap: 3px; margin-top: 0.45rem; }}
.fs-card .scale span {{ flex: 1; height: 5px; border-radius: 3px; background: {LINE}; }}
.fs-card .scale span.on {{ background: {ACCENT}; }}
.fs-card .ends {{ display: flex; justify-content: space-between; font-size: 0.8rem; color: {MUTED}; margin-top: 0.2rem; }}

.fs-tip {{ position: relative; display: inline-flex; width: 15px; height: 15px; border-radius: 50%;
  border: 1px solid {MUTED}; color: {MUTED}; font-size: 0.8rem; font-weight: 600; align-items: center;
  justify-content: center; cursor: help; font-style: normal; }}
.fs-tip:hover::after, .fs-tip:focus::after {{ content: attr(data-tip); position: absolute; left: -0.5rem; top: 1.4rem;
  width: 15rem; z-index: 20; background: {GREEN}; color: #fff; font-size: 0.8rem; font-weight: 400; line-height: 1.45;
  padding: 0.55rem 0.7rem; border-radius: 8px; box-shadow: 0 6px 20px rgba(18,53,40,0.18); }}

.fs-changes {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.4rem 0.9rem; margin-bottom: 1.3rem; }}
.fs-changes .row {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr); gap: 1rem;
  padding: 0.55rem 0; border-bottom: 1px solid {LINE}; font-size: 0.875rem; color: {INK_2}; }}
.fs-changes .row:last-child {{ border-bottom: none; }}
.fs-changes .row span:last-child {{ color: {INK}; font-weight: 500; text-align: right; }}

.fs-points {{ display: grid; gap: 0.6rem; margin: 0.6rem 0 1.2rem 0; }}
.fs-point {{ display: flex; gap: 0.8rem; background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.85rem 1rem; }}
.fs-point .n {{ flex: none; width: 1.7rem; height: 1.7rem; border-radius: 50%; background: {ACCENT_SOFT}; color: {ACCENT};
  font-weight: 650; font-size: 0.875rem; display: flex; align-items: center; justify-content: center; }}
.fs-point .t {{ font-weight: 600; color: {INK}; font-size: 1rem; }}
.fs-point .d {{ color: {INK_2}; font-size: 0.875rem; line-height: 1.5; margin-top: 0.1rem; }}

.fs-range {{ margin: 0.2rem 0 1.1rem 0; }}
.fs-range .track {{ display: grid; grid-template-columns: 1fr 8fr 1fr; height: 30px; border-radius: 8px; overflow: hidden;
  font-size: 0.8rem; font-weight: 500; }}
.fs-range .track div {{ display: flex; align-items: center; justify-content: center; }}
.fs-range .edge {{ background: {LINE}; color: {MUTED}; }}
.fs-range .mid {{ background: {ACCENT_SOFT}; color: {ACCENT}; border-left: 2px solid {ACCENT}; border-right: 2px solid {ACCENT}; }}
.fs-range .labels {{ display: grid; grid-template-columns: 1fr 1fr; font-size: 0.8rem; color: {MUTED}; margin-top: 0.3rem; }}
.fs-range .labels div:last-child {{ text-align: right; }}

.fs-chart {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.9rem 0.9rem 0.5rem 0.9rem; margin-bottom: 1.1rem; }}
.fs-chart .cap {{ font-size: 0.8rem; color: {MUTED}; margin-bottom: 0.3rem; }}

.fs-facts {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.6rem; margin: 1.2rem 0 1.6rem 0; }}
@media (max-width: 640px) {{ .fs-facts {{ grid-template-columns: 1fr; }} }}
.fs-fact {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.85rem 1rem; }}
.fs-fact .t {{ font-weight: 650; color: {INK}; font-size: 1rem; }}
.fs-fact .d {{ color: {MUTED}; font-size: 0.875rem; margin-top: 0.15rem; }}
.fs-terms {{ background: {CARD}; border: 1px solid {LINE}; border-radius: 14px; padding: 0.3rem 1.1rem; margin-bottom: 1.4rem; }}
.fs-terms .row {{ padding: 0.8rem 0; border-bottom: 1px solid {LINE}; }}
.fs-terms .row:last-child {{ border-bottom: none; }}
.fs-terms .h {{ font-weight: 600; color: {INK}; font-size: 0.875rem; margin-bottom: 0.15rem; }}
.fs-terms .b {{ color: {INK_2}; font-size: 0.875rem; line-height: 1.55; }}
.fs-hud .cap {{ width: 100%; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: {MUTED}; }}
.fs-scale-ends {{ display: flex; justify-content: space-between; gap: 1rem; font-size: 0.8rem;
  color: {MUTED}; margin: -0.4rem 0 1.1rem 0; max-width: 34rem; }}
.fs-changes .row span.note {{ color: {MUTED}; font-weight: 400; font-style: italic; }}
.fs-src {{ position: relative; display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; margin-left: 0.35rem; vertical-align: 3px; border-radius: 50%;
  color: {MUTED}; background: {CARD}; border: 1px solid {LINE}; cursor: help; }}
.fs-src:hover, .fs-src:focus {{ color: {ACCENT}; border-color: {ACCENT_LINE}; outline: none; }}
.fs-src:hover::after, .fs-src:focus::after {{ content: attr(data-tip); position: absolute; left: 50%;
  transform: translateX(-50%); top: 2.1rem; width: max-content; max-width: 17rem; z-index: 30;
  background: {GREEN}; color: #fff; font-size: 0.8rem; font-weight: 400; line-height: 1.45; letter-spacing: 0;
  padding: 0.55rem 0.75rem; border-radius: 8px; box-shadow: 0 8px 24px rgba(18,53,40,0.2); white-space: normal; }}
.fs-about-banner {{ display: flex; gap: 0.8rem; align-items: flex-start; background: #123528; color: #fff;
  border-radius: 14px; padding: 0.9rem 1.05rem; margin: 0 0 1.4rem 0; }}
.fs-about-banner .ic {{ flex: none; width: 2rem; height: 2rem; border-radius: 50%; background: rgba(255,255,255,0.12);
  display: flex; align-items: center; justify-content: center; }}
.fs-about-banner .t {{ font-weight: 650; font-size: 1rem; color: #fff; }}
.fs-about-banner .d {{ font-size: 0.875rem; color: #C6DACE; margin-top: 0.1rem; line-height: 1.45; }}
.fs-echo {{ font-size: 0.8rem; color: {MUTED}; margin: -0.5rem 0 0.6rem 0; }}
.fs-hero {{ padding: 0.4rem 0 0.2rem 0; }}
.fs-hero .lead {{ font-size: 1rem; color: {INK_2}; margin-top: -0.3rem; }}

/* ---------- simulation feel (0.9.0) ---------- */
.stApp {{ font-variant-numeric: tabular-nums; }}
div[data-testid="stElementContainer"][data-stale="true"], .stale-element {{ opacity: 1 !important; transition: none !important; }}
div[class*="st-key-screen_"] {{ animation: fs-in 320ms cubic-bezier(.2,.7,.2,1); }}
@keyframes fs-in {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
@media (max-width: 640px) {{
  div[data-testid="stElementContainer"]:has(> div > button[data-testid="stBaseButton-primary"]),
  div[data-testid="stElementContainer"]:has(button[data-testid="stBaseButton-primary"]) {{
    position: sticky; bottom: 0; z-index: 20; padding: 1.1rem 0 0.9rem 0; width: 100% !important;
    background: linear-gradient(to bottom, rgba(244,239,230,0), {BG} 38%);
  }}
  div[data-testid="stElementContainer"]:has(button[data-testid="stBaseButton-primary"]) div[data-testid="stButton"],
  button[data-testid="stBaseButton-primary"] {{ width: 100% !important; }}
  .fs-hud .hd {{ flex-wrap: wrap !important; row-gap: 0.15rem; }}
  .fs-hud .cap {{ width: 100% !important; text-align: left !important; }}
}}

.fs-hud {{ display: block; padding: 0; background: {CARD}; border: 1px solid {LINE}; border-radius: 14px;
  overflow: hidden; margin-bottom: 1.4rem; }}
.fs-hud .hd {{ display: flex; justify-content: space-between; align-items: center; gap: 0.8rem;
  padding: 0.5rem 0.85rem; border-bottom: 1px solid {LINE}; background: #FBF9F4; }}
.fs-hud .brand {{ display: inline-flex; align-items: center; gap: 0.45rem; font-weight: 650; font-size: 0.875rem; color: {INK}; }}
.fs-hud .cap {{ width: auto; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase;
  color: {MUTED}; text-align: right; }}
.fs-hud .cells {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(98px, 1fr)); gap: 1px; background: {LINE}; }}
.fs-hud .cells div {{ background: {CARD}; padding: 0.5rem 0.85rem 0.55rem 0.85rem; }}
.fs-hud small {{ display: block; font-size: 0.8rem; letter-spacing: 0.06em; text-transform: uppercase; color: {MUTED}; }}
.fs-hud b {{ margin: 0; font-size: 1rem; font-weight: 650; color: {INK}; letter-spacing: -0.01em; white-space: nowrap; }}

.fs-company {{ display: flex; gap: 1rem; align-items: flex-start; background: {CARD}; border: 1px solid {LINE};
  border-radius: 16px; padding: 1.1rem 1.15rem; margin: 0.3rem 0 1.2rem 0; box-shadow: 0 1px 2px rgba(18,53,40,0.04); }}
.fs-company .nm {{ font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; color: {INK}; line-height: 1.2; }}
.fs-company .mt {{ font-size: 0.8rem; color: {MUTED}; margin-top: 0.1rem; }}
.fs-company .pd {{ font-size: 1rem; color: {INK_2}; line-height: 1.55; margin-top: 0.55rem; }}
.fs-company .tags {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.7rem; }}
.fs-company .tags span {{ font-size: 0.8rem; color: {INK_2}; background: #F1EDE4; border-radius: 999px; padding: 0.18rem 0.6rem; }}

.fs-msg {{ background: {CARD}; border: 1px solid {LINE}; border-left: 3px solid {ACCENT}; border-radius: 14px;
  padding: 0.85rem 1rem 0.95rem 1rem; margin: 0 0 1.1rem 0; box-shadow: 0 1px 2px rgba(18,53,40,0.04);
  animation: fs-msg 520ms 120ms cubic-bezier(.2,.7,.2,1) both; }}
@keyframes fs-msg {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
.fs-msg .hd {{ display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.55rem; }}
.fs-msg .ic {{ flex: none; width: 2rem; height: 2rem; border-radius: 50%; background: {ACCENT_SOFT}; color: {ACCENT};
  display: flex; align-items: center; justify-content: center; }}
.fs-msg .from {{ font-size: 0.875rem; font-weight: 650; color: {INK}; line-height: 1.25; }}
.fs-msg .sub {{ font-size: 0.8rem; color: {MUTED}; line-height: 1.25; }}
.fs-msg .tag {{ margin-left: auto; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase;
  color: {ACCENT}; background: {ACCENT_SOFT}; border-radius: 999px; padding: 0.15rem 0.5rem; }}
.fs-msg .tx {{ font-size: 1rem; line-height: 1.6; color: {INK_2}; }}

.odo {{ display: inline-flex; align-items: flex-start; white-space: pre; line-height: 1.2em; height: 1.2em; vertical-align: top; }}
.odo .s, .odo .d {{ display: inline-block; height: 1.2em; line-height: 1.2em; }}
.odo .d {{ overflow: hidden; }}
.odo .d > span {{ display: flex; flex-direction: column;
  animation-duration: 1600ms; animation-delay: 3200ms; animation-timing-function: cubic-bezier(.2,.75,.25,1);
  animation-fill-mode: backwards; }}
.odo .d i {{ font-style: normal; height: 1.2em; line-height: 1.2em; text-align: center; }}
.fs-card.chg {{ animation: fs-glow 1600ms 1500ms ease-out backwards; }}
@keyframes fs-glow {{ 0% {{ box-shadow: 0 0 0 0 rgba(45,106,79,0.0); }} 30% {{ box-shadow: 0 0 0 3px rgba(45,106,79,0.18); }} 100% {{ box-shadow: 0 1px 2px rgba(18,53,40,0.04); }} }}

.fs-veil {{ position: fixed; inset: 0; z-index: 999990; background: #0C261D; display: flex; align-items: center;
  justify-content: center; pointer-events: none; animation: fs-veil 2100ms ease forwards; }}
.fs-veil .t {{ color: #F7F5F0; font-size: 1.75rem; font-weight: 700; letter-spacing: -0.03em;
  animation: fs-up 700ms 100ms ease-out both; }}
.fs-veil .b {{ color: #A7D7B8; font-size: 1rem; margin-top: 0.4rem; animation: fs-up 700ms 350ms ease-out both; }}
.fs-veil .ln {{ height: 2px; width: 0; margin-top: 1.3rem; border-radius: 2px;
  background: linear-gradient(90deg, #2D6A4F, #52B788, #B7E4C7); animation: fs-line 1000ms 450ms ease-out forwards; }}
@keyframes fs-veil {{ 0%, 62% {{ opacity: 1; visibility: visible; }} 100% {{ opacity: 0; visibility: hidden; }} }}
@keyframes fs-up {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes fs-line {{ to {{ width: 100%; }} }}

.fs-journey {{ position: relative; margin: 0.6rem 0 1.4rem 0; padding-left: 1.4rem; }}
.fs-journey::before {{ content: ""; position: absolute; left: 0.42rem; top: 0.4rem; bottom: 0.4rem; width: 2px; background: {LINE}; }}
.fs-journey .m {{ position: relative; margin-bottom: 1.1rem; }}
.fs-journey .m::before {{ content: ""; position: absolute; left: -1.22rem; top: 0.3rem; width: 0.7rem; height: 0.7rem;
  border-radius: 50%; background: {CARD}; border: 2px solid {ACCENT}; }}
.fs-journey .mh {{ font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: {ACCENT}; }}
.fs-journey .mt {{ font-weight: 650; color: {INK}; font-size: 1rem; margin: 0.05rem 0 0.35rem 0; }}
.fs-journey .it {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr); gap: 0.8rem; font-size: 0.875rem;
  padding: 0.38rem 0; border-top: 1px solid {LINE}; color: {MUTED}; }}
.fs-journey .it span:last-child {{ color: {INK}; font-weight: 500; }}
@media (prefers-reduced-motion: reduce) {{
  div[class*="st-key-screen_"], .fs-msg, .odo .d > span, .fs-card.chg {{ animation: none !important; }}
  .fs-veil {{ display: none !important; }}
}}

/* ---------- type scale (review B4): 1.75 / 1.25 / 1 / 0.875, minimum 0.8 ---------- */
.stApp h1, .stApp h2, .stApp h3 {{ font-size: 1.75rem !important; font-weight: 700 !important;
  letter-spacing: -0.02em; line-height: 1.25 !important; padding: 0 0 0.4rem 0 !important; }}
div[data-testid="stWidgetLabel"] p {{ font-size: 1rem !important; }}
label[data-testid="stRadioOption"] p, div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li, input, textarea {{ font-size: 1rem !important; }}
div[data-testid="stCaptionContainer"], div[data-testid="stCaptionContainer"] p,
div[data-testid="stAlert"] p {{ font-size: 0.875rem !important; }}
button p {{ font-size: 1rem !important; }}

/* ---------- selection color (review B7) ----------
   The theme in .streamlit/config.toml sets it. If that file is missing on a
   deployment, Streamlit falls back to red; this keeps the theme color anyway. */
label[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {{
  background-color: {ACCENT} !important; border-color: {ACCENT} !important; }}
input[type="checkbox"]:checked + div, div[data-baseweb="checkbox"] [aria-checked="true"] {{
  background-color: {ACCENT} !important; border-color: {ACCENT} !important; }}

/* ---------- email (review B6) ---------- */
.fs-msg .hd {{ align-items: flex-start; margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid {LINE}; }}
.fs-msg .meta {{ display: grid; gap: 0.1rem; font-size: 0.875rem; color: {INK_2}; min-width: 0; }}
.fs-msg .meta .row {{ display: flex; gap: 0.5rem; }}
.fs-msg .meta .row span {{ flex: none; width: 3.9rem; color: {MUTED}; }}
.fs-msg .meta .row b {{ color: {INK}; font-weight: 600; }}
.fs-msg .tx p {{ margin: 0 0 0.3rem 0; font-size: 1rem; line-height: 1.5; color: {INK_2}; }}
.fs-msg .tx .gr {{ display: block; }}
.fs-msg {{ padding: 0.7rem 0.95rem 0.6rem 0.95rem; margin-bottom: 0.7rem; }}
.fs-msg .hd {{ margin-bottom: 0.4rem; padding-bottom: 0.4rem; }}
.fs-msg .tx p.sg {{ margin: 0.2rem 0 0 0; color: {MUTED}; font-size: 0.875rem; }}

/* ---------- bar chart (HTML, keeps the type scale) ---------- */
.fs-chart .bars {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)) minmax(0, 1.5fr);
  gap: 0.6rem; align-items: end; border-bottom: 0; }}
.fs-chart .col {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-end; min-width: 0; }}
.fs-chart .v {{ font-size: 0.875rem; font-weight: 650; color: {INK}; margin-bottom: 0.2rem; white-space: nowrap; }}
.fs-chart .bar {{ width: 62%; border-radius: 6px 6px 0 0; background: #A8CBB6; display: flex;
  justify-content: center; align-items: flex-start; }}
.fs-chart .bar.now {{ background: {ACCENT}; }}
.fs-chart .bar .chg {{ font-size: 0.8rem; font-weight: 600; color: #FFFFFF; padding-top: 0.15rem; }}
.fs-chart .bar.q {{ width: 100%; height: 26px; border-radius: 8px; background: {ACCENT_SOFT};
  border: 1.5px dashed {ACCENT}; color: {ACCENT}; font-weight: 700; align-items: center; font-size: 1rem; }}
.fs-chart .x {{ font-size: 0.8rem; color: {MUTED}; margin-top: 0.25rem; white-space: nowrap; text-align: center;
  border-top: 1px solid {LINE}; width: 100%; padding-top: 0.2rem; }}
.fs-chart .fut .x {{ color: {ACCENT}; font-weight: 600; border-top-color: transparent; }}
.fs-chart .bars:has(.col:nth-child(4)) {{ grid-template-columns: repeat(4, minmax(0, 1fr)) minmax(0, 1.5fr); }}
.fs-chart .bars:not(:has(.col:nth-child(5))) {{ grid-template-columns: repeat(3, minmax(0, 1fr)) minmax(0, 1.5fr); }}
@media (max-width: 640px) {{ .fs-chart .bars {{ gap: 0.3rem; }} .fs-chart .x {{ white-space: normal; }} }}

/* ---------- laptop height (review B5): F3 fits 1366 x 768 without scrolling ---------- */
.block-container {{ max-width: 50rem; padding-top: 0.6rem !important; }}
.fs-steps {{ gap: 0.3rem; margin-bottom: 0.45rem; }}
.fs-step {{ padding: 0.2rem 0.6rem; }}
.fs-bar {{ margin-bottom: 0.9rem; }}
.fs-q {{ margin-bottom: 0.4rem; }}
.fs-body {{ margin-bottom: 0.7rem; }}
.fs-hud {{ display: flex !important; flex-wrap: wrap; align-items: baseline; gap: 0.15rem 0.6rem;
  padding: 0.45rem 0.8rem !important; margin-bottom: 0.9rem; font-size: 0.875rem; color: {MUTED}; }}
.fs-hud .cap {{ width: auto !important; text-align: left !important; font-size: 0.8rem; font-weight: 500;
  letter-spacing: 0; text-transform: none; color: {MUTED}; margin-right: 0; }}
.fs-hud .it {{ white-space: nowrap; }}
label[data-testid="stRadioOption"] {{ padding: 0.68rem 1rem !important; }}
div[role="radiogroup"] {{ gap: 0.4rem !important; }}
.fs-card {{ padding: 0.6rem 0.85rem !important; }}
.fs-grid {{ gap: 0.5rem !important; margin: 0.2rem 0 0.5rem 0 !important; }}
.fs-grid.two {{ margin-bottom: 0.7rem !important; }}
.fs-grid.four {{ grid-template-columns: repeat(4, minmax(0, 1fr)) !important; margin-bottom: 0.7rem !important; }}
@media (max-width: 640px) {{ .fs-grid.four {{ grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }} }}
.fs-company {{ padding: 0.8rem 1rem !important; margin: 0.1rem 0 0.7rem 0 !important; gap: 0.85rem !important; }}
.fs-company .pd {{ margin-top: 0.3rem !important; }}
.fs-company .tags {{ margin-top: 0.45rem !important; }}
.fs-changes {{ margin-bottom: 0.8rem !important; padding: 0.2rem 0.9rem !important; }}
.fs-changes .row {{ padding: 0.4rem 0 !important; }}
.fs-hud .it b {{ font-size: 0.875rem; font-weight: 650; color: {INK}; margin-left: 0.3rem; }}
.fs-chart {{ padding: 0.6rem 0.8rem 0.3rem 0.8rem; margin-bottom: 0.8rem; }}
.fs-chart .cap {{ margin-bottom: 0.1rem; }}
.fs-range {{ margin: 0 0 0.7rem 0; }}
.fs-range .track {{ height: 26px; }}
div[data-testid="stVerticalBlock"] {{ gap: 0.55rem; }}
.fs-range .track {{ grid-template-columns: 1.7fr 6.6fr 1.7fr; }}
.fs-q {{ line-height: 1.35; }}
@media (max-width: 640px) {{
  .fs-hud {{ gap: 0.1rem 0.8rem; }}
  .fs-range .track {{ height: auto !important; min-height: 26px; grid-template-columns: 1.3fr 3fr 1.3fr !important; }}
  .fs-range .track div {{ padding: 0.2rem 0.3rem; text-align: center; line-height: 1.25; }}
}}

/* =====================================================================
   0.11.0 · green cockpit (team feedback of 21 October)
   ===================================================================== */

/* One font everywhere, numbers included. */
.stApp *:not([data-testid="stIconMaterial"]):not(svg):not(path),
div[data-baseweb="popover"] *, div[data-baseweb="tooltip"] *, div[role="listbox"] * {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  font-variant-numeric: tabular-nums;
}}

/* Top panel: dark green, sections, gradient progress, numbers line. */
.fs-top {{ background: {GREEN}; border-radius: 18px; padding: 0.95rem 1.1rem 1rem 1.1rem;
  margin: 0 0 1.5rem 0; box-shadow: 0 10px 30px rgba(18,53,40,0.16); }}
.fs-top .fs-steps {{ margin-bottom: 0.75rem; }}
.fs-top .fs-step {{ background: rgba(255,255,255,0.07) !important; border-color: transparent !important;
  color: #A9C2B5 !important; }}
.fs-top .fs-step.done {{ background: rgba(255,255,255,0.12) !important; color: #E9F1EC !important; }}
.fs-top .fs-step.done::before {{ color: #95D5B2 !important; }}
.fs-top .fs-step.now {{ background: {BG} !important; color: {GREEN} !important; font-weight: 600; }}
.fs-top .fs-bar {{ background: rgba(255,255,255,0.14) !important; height: 4px; margin-bottom: 0 !important; }}
.fs-top .fs-bar > div {{ background: linear-gradient(90deg, #52B788 0%, #95D5B2 55%, #D8F3DC 100%) !important;
  transition: width 700ms cubic-bezier(.2,.7,.2,1); }}
.fs-top .fs-hud {{ background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.10) !important;
  margin: 1.1rem 0 0 0 !important; padding: 0.55rem 0.85rem !important; border-radius: 12px; }}
.fs-top .fs-hud .cap {{ color: #95D5B2 !important; }}
.fs-top .fs-hud .it {{ color: #B8CCC1; }}
.fs-top .fs-hud .it b {{ color: #FFFFFF !important; }}

/* About you: the panel sits inside the white card. */
.fs-about-banner {{ background: {ACCENT_SOFT} !important; border: 1px solid {ACCENT_LINE}; }}
.fs-about-banner .t {{ color: {GREEN} !important; }}
.fs-about-banner .d {{ color: {INK_2} !important; }}
.fs-about-banner .ic {{ background: {GREEN} !important; }}

/* More air, evenly spread (team feedback); decisions still fit a laptop. */
.block-container {{ padding-top: 1.3rem !important; }}
div[data-testid="stVerticalBlock"] {{ gap: 0.8rem !important; }}
.fs-q {{ margin-bottom: 0.55rem !important; }}
.fs-body {{ margin-bottom: 0.9rem !important; }}
div[role="radiogroup"] {{ gap: 0.55rem !important; }}
label[data-testid="stRadioOption"] {{ padding: 0.75rem 1.05rem !important; }}
.fs-msg {{ margin-bottom: 1rem !important; }}
.fs-eyebrow {{ margin-bottom: 0.45rem; }}
.stApp h1, .stApp h2, .stApp h3 {{ padding-bottom: 0.5rem !important; }}

/* Every answer row spans the full width, so no option looks shorter. */
div[data-testid="stButtonGroup"], div[data-testid="stButtonGroup"] > div {{ width: 100% !important; }}
div[data-testid="stButtonGroup"] div:has(> button[data-testid^="stBaseButton-pills"]) {{
  display: flex !important; flex-wrap: wrap; gap: 0.5rem; width: 100% !important; }}
div[data-testid="stButtonGroup"] button[data-testid^="stBaseButton-pills"] {{ flex: 1 1 0 !important;
  min-width: 3rem; justify-content: center; }}
.fs-scale-ends {{ max-width: none !important; margin-top: 0.15rem !important; }}

/* Sliders (About you): green handle and track, labels in the type scale. */
div[data-testid="stSlider"] {{ padding: 0 0.4rem; }}
div[data-testid="stSlider"] div[role="slider"] {{ background-color: {GREEN} !important;
  border: 3px solid #FFFFFF !important; box-shadow: 0 0 0 1px {GREEN}, 0 2px 8px rgba(18,53,40,0.25) !important;
  width: 1.35rem !important; height: 1.35rem !important; }}
div[data-testid="stSlider"] div[data-testid="stSliderThumbValue"],
div[data-testid="stSlider"] div[data-testid="stSliderThumbValue"] * {{ color: {GREEN} !important;
  font-weight: 650 !important; font-size: 0.875rem !important; }}
div[data-testid="stSliderTickBar"] * {{ color: {MUTED} !important; font-size: 0.8rem !important; }}

/* The email arrives like a push notification. */
.fs-msg {{ animation: fs-arrive 900ms 250ms cubic-bezier(.2,.8,.2,1) both !important; }}
@keyframes fs-arrive {{ 0% {{ opacity: 0; transform: translateY(-18px) scale(0.98); }}
  60% {{ opacity: 1; transform: translateY(3px) scale(1); }} 100% {{ opacity: 1; transform: none; }} }}
.fs-msg .ic {{ position: relative; background: {GREEN} !important; color: #FFFFFF !important;
  animation: fs-ring 1100ms 900ms ease-in-out 2 both; transform-origin: 50% 15%; }}
.fs-msg .ic::after {{ content: ""; position: absolute; top: -2px; right: -2px; width: 0.6rem; height: 0.6rem;
  border-radius: 50%; background: #52B788; border: 2px solid {CARD}; }}
.fs-msg .ic::before {{ content: ""; position: absolute; inset: 0; border-radius: 50%; border: 2px solid #52B788;
  animation: fs-ping 1600ms 900ms ease-out 3 both; }}
@keyframes fs-ring {{ 0%, 100% {{ transform: rotate(0); }} 15% {{ transform: rotate(-16deg); }}
  30% {{ transform: rotate(13deg); }} 45% {{ transform: rotate(-9deg); }} 60% {{ transform: rotate(6deg); }}
  75% {{ transform: rotate(-3deg); }} }}
@keyframes fs-ping {{ 0% {{ transform: scale(1); opacity: 0.8; }} 100% {{ transform: scale(1.9); opacity: 0; }} }}
.fs-msg .tag {{ animation: fs-pulse 1600ms 900ms ease-in-out 3; }}
@keyframes fs-pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.45; }} }}

/* Longer, smoother transitions. */
div[class*="st-key-screen_"] {{ animation: fs-in 650ms cubic-bezier(.2,.7,.2,1) both !important; }}
@keyframes fs-in {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
.fs-veil {{ background: {GREEN} !important; animation: fs-veil2 3600ms cubic-bezier(.4,0,.2,1) forwards !important; }}
@keyframes fs-veil2 {{ 0%, 68% {{ opacity: 1; visibility: visible; }} 100% {{ opacity: 0; visibility: hidden; }} }}
.fs-veil .t {{ animation: fs-up 1000ms 150ms cubic-bezier(.2,.7,.2,1) both !important; }}
.fs-veil .b {{ color: #A7D7B8 !important; animation: fs-up 1000ms 550ms cubic-bezier(.2,.7,.2,1) both !important; }}
.fs-veil .ln {{ background: linear-gradient(90deg, #52B788, #95D5B2, #D8F3DC) !important;
  animation: fs-line 1500ms 700ms ease-out forwards !important; }}
.fs-card.chg {{ animation: fs-glow 1800ms 3100ms ease-out backwards !important; }}

@media (prefers-reduced-motion: reduce) {{
  .fs-msg, .fs-msg .ic, .fs-msg .ic::before, .fs-msg .tag, div[class*="st-key-screen_"], .fs-card.chg {{
    animation: none !important; }}
}}
@media (max-width: 640px) {{
  .fs-top {{ padding: 0.8rem 0.85rem 0.85rem 0.85rem; border-radius: 14px; margin-bottom: 1.1rem; }}
}}

/* ---------- 0.11.0 fit and slider details ---------- */
.block-container {{ max-width: 52rem !important; padding-top: 1rem !important; }}
.fs-top {{ padding: 0.85rem 1rem 0.9rem 1rem !important; margin-bottom: 1.3rem !important; }}
.fs-top .fs-steps {{ gap: 0.28rem !important; margin-bottom: 0.65rem !important; }}
.fs-top .fs-step {{ padding: 0.2rem 0.6rem !important; }}
.fs-top .fs-hud {{ margin-top: 0.9rem !important; gap: 0.15rem 0.7rem !important; }}
.fs-q .nw {{ white-space: nowrap; }}

div[data-testid="stSlider"] div[data-rac]:has(> div > input[type="range"]) {{
  width: 1.3rem !important; height: 1.3rem !important; border-radius: 50% !important;
  background: {GREEN} !important; border: 3px solid #FFFFFF !important;
  box-shadow: 0 0 0 1px {GREEN}, 0 2px 8px rgba(18,53,40,0.25) !important; cursor: grab; }}
div[data-testid="stSliderTickBar"] {{ display: none !important; }}
.fs-ticks {{ position: relative; height: 1.2rem; margin: -0.35rem 0.4rem 0.9rem 0.4rem; }}
.fs-ticks span {{ position: absolute; top: 0; transform: translateX(-50%); font-size: 0.8rem;
  color: {MUTED}; white-space: nowrap; }}
.fs-ticks span:first-child {{ transform: none; }}
.fs-ticks span:last-child {{ transform: translateX(-100%); }}

/* ---------- 0.11.0 laptop fit ---------- */
@media (min-width: 900px) {{
  .fs-top .fs-hud {{ flex-wrap: nowrap !important; justify-content: space-between; gap: 0.5rem !important; }}
}}
div[data-testid="stVerticalBlock"] {{ gap: 0.68rem !important; }}
div[role="radiogroup"] {{ gap: 0.48rem !important; }}
label[data-testid="stRadioOption"] {{ padding: 0.66rem 1.05rem !important; }}
.fs-top {{ margin-bottom: 1.15rem !important; }}
.fs-msg {{ padding: 0.65rem 0.95rem 0.55rem 0.95rem !important; margin-bottom: 0.85rem !important; }}
.fs-msg .tx p {{ line-height: 1.45 !important; margin-bottom: 0.25rem !important; }}
.fs-chart {{ padding: 0.55rem 0.8rem 0.35rem 0.8rem !important; }}

.block-container {{ padding-top: 0.75rem !important; }}
.fs-top {{ padding: 0.75rem 1rem 0.8rem 1rem !important; margin-bottom: 1rem !important; }}
.fs-top .fs-hud {{ margin-top: 0.8rem !important; padding: 0.45rem 0.85rem !important; }}

/* Pills (rank 1 to 10, H1 roles, funding): the row fills the full width. */
div[data-testid="stElementContainer"]:has(> div[data-testid="stButtonGroup"]),
div[data-testid="stButtonGroup"] {{ width: 100% !important; }}
div[data-testid="stButtonGroup"] > div[role="radiogroup"],
div[data-testid="stButtonGroup"] > div[role="group"] {{ display: flex !important; flex-direction: row !important;
  flex-wrap: wrap !important; width: 100% !important; max-width: none !important; gap: 0.5rem !important; }}
div[data-testid="stButtonGroup"] > div > button {{ flex: 1 1 0 !important; min-width: 2.75rem !important;
  justify-content: center !important; }}

.fs-terms .h {{ font-size: 1rem !important; }}
.fs-terms .b {{ font-size: 1rem !important; }}

.stApp h1, .stApp h2, .stApp h3 {{ padding-top: 0.6rem !important; }}

/* ---------- 0.11.1 ---------- */
/* Screen fade with opacity only: a transform would trap the full-screen
   curtains (position: fixed) inside the centre column. */
div[class*="st-key-screen_"] {{ animation: fs-fade 650ms ease-out both !important; transform: none !important; }}
@keyframes fs-fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
.fs-veil {{ position: fixed !important; inset: 0 !important; width: 100vw !important; height: 100vh !important; }}

/* Slider track: Streamlit paints the filled part inline in the theme color,
   which is red when the theme file is missing. A neutral track instead. */
div[data-testid="stSlider"] div[style*="touch-action"] > div:first-child:empty,
div[data-testid="stSlider"] div[style*="linear-gradient"] {{ background-image: none !important;
  background-color: {LINE} !important; height: 6px !important; border-radius: 3px !important; }}

/* Pills: fill the row but never cut a label. */
div[data-testid="stButtonGroup"] > div > button {{ flex: 1 1 auto !important; min-width: max-content !important; }}
div[data-testid="stButtonGroup"] > div > button p,
div[data-testid="stButtonGroup"] > div > button div {{ overflow: visible !important; text-overflow: clip !important;
  white-space: nowrap !important; max-width: none !important; }}
div[data-testid="stButtonGroup"] > div > button:hover {{ border-color: {ACCENT} !important; }}
div[data-testid="stButtonGroup"] > div > button:hover * {{ color: {INK} !important; }}
div[data-testid="stButtonGroup"] > div > button[aria-checked="true"]:hover *,
div[data-testid="stButtonGroup"] > div > button[aria-pressed="true"]:hover * {{ color: #FFFFFF !important; }}

/* ---------- 0.13.0 (round 3) ---------- */
/* A6: a gap with dots between month 3 and month 9 */
.fs-chart .bars.gap {{ grid-template-columns: repeat(3, minmax(0, 1fr)) minmax(0, 0.45fr) minmax(0, 1.5fr) !important; }}
.fs-chart .gapcol .dots {{ color: {MUTED}; font-size: 1rem; font-weight: 700; letter-spacing: 0.1em; padding-bottom: 0.1rem; }}
.fs-chart .gapcol .x {{ border-top-color: {LINE}; }}
/* A5: a lower chart, so Continue stays above the fold on 1366 x 640 */
.fs-chart {{ padding: 0.45rem 0.8rem 0.3rem 0.8rem !important; margin-bottom: 0.6rem !important; }}
.fs-chart .cap {{ margin-bottom: 0 !important; }}
.fs-chart .v {{ margin-bottom: 0.1rem !important; }}
/* A7: phone layout */
@media (max-width: 640px) {{
  .fs-ticks {{ height: 2.5rem !important; }}
  .fs-ticks span {{ white-space: normal !important; text-align: center; line-height: 1.15;
    width: var(--w); font-size: 0.8rem !important; }}
  .fs-ticks span:first-child {{ text-align: left; }}
  .fs-ticks span:last-child {{ text-align: right; }}
}}
ul[role="listbox"] li, li[role="option"], div[role="option"] {{ white-space: normal !important;
  line-height: 1.2 !important; overflow-wrap: anywhere; }}
div[data-baseweb="select"] div {{ white-space: normal !important; text-overflow: clip !important; }}

/* A5: only the screens with a chart (F3, G3) or an email (K1, rank items) */
div[class*="st-key-screen_"]:has(.fs-chart) div[data-testid="stVerticalBlock"],
div[class*="st-key-screen_"]:has(.fs-msg) div[data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}
div[class*="st-key-screen_"]:has(.fs-chart) .fs-body,
div[class*="st-key-screen_"]:has(.fs-msg) .fs-body {{ margin-bottom: 0.6rem !important; }}
div[class*="st-key-screen_"]:has(.fs-msg) label[data-testid="stRadioOption"] {{ padding: 0.6rem 1.05rem !important; }}
div[class*="st-key-screen_"]:has(.fs-chart) .fs-top {{ margin-bottom: 0.75rem !important; }}
div[class*="st-key-screen_"]:has(.fs-chart) .fs-range {{ margin-bottom: 0.45rem !important; }}
div[class*="st-key-screen_"]:has(.fs-chart) .fs-q {{ margin-bottom: 0.4rem !important; }}
/* A7: long dropdown options wrap on phones (rows are 40 px, two lines fit) */
@media (max-width: 640px) {{
  [role="option"] > div {{ white-space: normal !important; overflow: visible !important;
    line-height: 1.15 !important; font-size: 0.8rem !important; height: auto !important; }}
  [role="option"] {{ align-items: center !important; }}
}}
.fs-fullval {{ display: none; font-size: 0.875rem; color: {INK_2}; margin-top: -0.3rem; }}
@media (max-width: 640px) {{ .fs-fullval {{ display: block; }} }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f"<style>{_ROLL_KEYFRAMES}</style>", unsafe_allow_html=True)


def _h(text: str) -> str:
    return html.escape(str(text), quote=True)


def html_block(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section bar
# ---------------------------------------------------------------------------

def steps(sections: list[str], current: str | None, progress: float,
          hud_html: str = "") -> None:
    """The dark green top panel: sections, progress with a gradient and, on
    decision screens, the numbers line (`hud_html`). Below it the beige work
    surface holds the question."""
    if not current:
        return
    idx = sections.index(current) if current in sections else -1
    # Once the simulation runs, the finished sections before it collapse into
    # one chip, so the bar fits one line on a laptop (review B5).
    intro = [content.SECTION_ABOUT, content.SECTION_HOW, content.SECTION_STARTUP]
    collapse = idx > max((sections.index(s) for s in intro if s in sections), default=-1)
    chips = []
    if collapse:
        chips.append(f'<div class="fs-step done">{_h(content.SECTION_INTRO_DONE)}</div>')
    for i, sec in enumerate(sections):
        if collapse and sec in intro:
            continue
        cls = "done" if i < idx else "now" if i == idx else ""
        chips.append(f'<div class="fs-step {cls}">{_h(sec)}</div>')
    pct = max(2, min(100, round(progress * 100)))
    html_block(f'<div class="fs-top"><div class="fs-steps">{"".join(chips)}</div>'
               f'<div class="fs-bar"><div style="width:{pct}%"></div></div>{hud_html}</div>')


# ---------------------------------------------------------------------------
# Text pieces
# ---------------------------------------------------------------------------

def eyebrow(text: str, muted: bool = False) -> None:
    html_block(f'<div class="fs-eyebrow{" muted" if muted else ""}">{_h(text)}</div>')


LINK_SVG = ('<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 0 0-7.07-7.07l-1.5 1.5"/>'
            '<path d="M14 11a5 5 0 0 0-7.07 0l-3 3a5 5 0 0 0 7.07 7.07l1.5-1.5"/></svg>')


def question(text: str, body: str | None = None, sources: list[str] | None = None) -> None:
    """Question title plus optional body (simple <b> tags allowed). If sources
    are given, a small link icon follows the title; hovering over it (or tapping
    on a phone) shows the scientific background by author and year."""
    icon = ""
    if sources:
        tip = "Scientific background: " + "; ".join(sources)
        icon = (f' <span class="fs-src" tabindex="0" role="note" aria-label="{_h(tip)}" '
                f'data-tip="{_h(tip)}">{LINK_SVG}</span>')
    if icon and " " in text:
        head, last = text.rsplit(" ", 1)
        out = f'<div class="fs-q">{_h(head)} <span class="nw">{_h(last)}{icon}</span></div>'
    else:
        out = f'<div class="fs-q">{_h(text)}{icon}</div>'
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

def _visible_fields(state: dict, solo: bool = False,
                    show_scales: bool = False) -> list[tuple[str, str, str]]:
    """Morale and market confidence judge how well decisions worked, so they
    are hidden during the session and shown in the final report (review A9)."""
    out = []
    for key, label, help_text in content.status_fields(solo):
        if key == "pending_hires" and not state.get("pending_hires"):
            continue
        if key in game.SCALE_KEYS and not show_scales:
            continue
        out.append((key, label, help_text))
    return out


_ROLL_KEYFRAMES = "".join(
    f"@keyframes fs-r-{f}-{t} {{ from {{ transform: translateY({-f * 1.2:.1f}em); }} "
    f"to {{ transform: translateY({-t * 1.2:.1f}em); }} }}\n"
    for f in range(11) for t in range(10))
_ROLL_CELLS = "".join(f"<i>{d}</i>" for d in "0123456789") + "<i>&nbsp;</i>"


def odometer(before: str, after: str) -> str:
    """The new value, with each digit rolling from the old one (pure CSS, so it
    works inside Streamlit's markdown). Without motion it simply shows `after`."""
    n = max(len(before), len(after))
    b, a = before.rjust(n), after.rjust(n)
    out, started = [], False
    for cb, ca in zip(b, a):
        if ca == " " and not started:
            continue                      # leading padding of a shorter number
        started = True
        if ca.isdigit() and (cb.isdigit() or cb == " ") and cb != ca:
            fi = 10 if cb == " " else int(cb)
            out.append(f'<span class="d"><span style="transform:translateY({-int(ca) * 1.2:.1f}em);'
                       f'animation-name:fs-r-{fi}-{ca}">{_ROLL_CELLS}</span></span>')
        else:
            out.append(f'<span class="s">{_h(ca)}</span>')
    return f'<span class="odo" aria-label="{_h(after)}">{"".join(out)}</span>'


def status_cards(state: dict, before: dict | None = None, solo: bool = False,
                 animate: bool = False, show_scales: bool = False) -> None:
    """Cards for the situation, with the change since `before` if given. With
    `animate`, changed numbers roll from the old to the new value."""
    cards, scales = [], []
    for key, label, help_text in _visible_fields(state, solo, show_scales):
        value = game.format_value(key, state)
        value_html, delta, cls = _h(value), "", ""
        if before is not None:
            d = (state.get(key) or 0) - (before.get(key) or 0)
            if d:
                delta = f'<div class="dl">{_h(game.format_delta(key, d))}</div>'
                value_html = odometer(game.format_value(key, before), value) if animate else value_html
                cls = " chg" if animate else ""
        extra = ""
        if key in ("morale", "market_confidence"):
            v = int(state.get(key) or 0)
            bars = "".join(f'<span class="{"on" if i < v else ""}"></span>' for i in range(5))
            extra = (f'<div class="scale">{bars}</div>'
                     f'<div class="ends"><span>low</span><span>high</span></div>')
        card = (f'<div class="fs-card{cls}"><div class="lbl">{_h(label)}'
                f'<i class="fs-tip" tabindex="0" data-tip="{_h(help_text)}">i</i></div>'
                f'<div class="val">{value_html}</div>{delta}{extra}</div>')
        (scales if (extra or key in ("ownership", "pending_hires")) else cards).append(card)
    # One grid, four columns on a laptop (review B5), two on a phone.
    html_block(f'<div class="fs-grid four">{"".join(cards + scales)}</div>')


LOGO_SVG = ('<svg viewBox="0 0 32 32" width="{w}" height="{w}" aria-hidden="true">'
            '<rect width="32" height="32" rx="8" fill="#123528"/>'
            '<path d="M8 21a8 8 0 0 1 16 0z" fill="#C9A46A"/>'
            '<rect x="6" y="22.6" width="20" height="1.8" rx="0.9" fill="#F7F5F0"/></svg>')


def logo(size: int = 20) -> str:
    return LOGO_SVG.replace("{w}", str(size))


def hud(state: dict, caption: str = "At the start of this area", brand: str = "",
        render: bool = True) -> str:
    """One compact line with the key numbers on every simulation question. It
    shows the situation at the start of the area and does not move with the
    answers inside the area, so a single decision never gets visible feedback.
    (`brand` is kept for callers; the line has no room for the logo.)"""
    # Customers are not in the line: they change only in the final report.
    runway = state.get("runway", 0)
    items = [("Cash", game.format_value("cash", state)),
             ("Net burn", game.format_value("burn", state) + "/mo"),
             ("Runway", "8+ years" if runway >= 99 else f"{runway} mo"),
             ("Revenue", game.format_value("revenue", state) + "/mo"),
             ("Team", str(state.get("team_size", 0)))]
    if state.get("pending_hires"):
        items.insert(5, ("Open roles", str(state["pending_hires"])))
    cells = "".join(f'<span class="it">{_h(k)}<b>{_h(v)}</b></span>' for k, v in items)
    markup = f'<div class="fs-hud"><span class="cap">{_h(caption)}</span>{cells}</div>'
    if render:
        html_block(markup)
    return markup


def changes(events: list[dict], solo: bool = False) -> None:
    if not events:
        return
    rows = []
    labels = dict((k, l) for k, l, _ in content.status_fields(solo))
    for ev in events:
        parts = [f"{labels.get(key, key)} {game.format_delta(key, d)}"
                 for key, d in ev["delta"].items()]
        if parts:
            right = f'<span>{_h(" · ".join(parts))}</span>'
        elif ev.get("note"):
            right = f'<span class="note">{_h(ev["note"])}</span>'
        else:
            continue
        rows.append(f'<div class="row"><span>{_h(ev["label"])}</span>{right}</div>')
    if rows:
        html_block(f'<div class="fs-changes">{"".join(rows)}</div>')


# ---------------------------------------------------------------------------
# Interval helpers
# ---------------------------------------------------------------------------

def range_diagram(left: str, right: str) -> None:
    html_block(
        '<div class="fs-range"><div class="track">'
        f'<div class="edge">1 in 10 {_h(left)}</div>'
        '<div class="mid">about 8 in 10 land between your two numbers</div>'
        f'<div class="edge">1 in 10 {_h(right)}</div></div></div>')


def bar_chart(series: list[tuple[str, float, str | None]], unit_fmt, caption: str,
              future_label: str, gap: bool = False) -> None:
    """Small bar chart of a past series, with an empty 'future' slot. Built from
    HTML, not SVG, so its text keeps the type scale on every screen size."""
    vmax = max(v for _, v, _ in series) * 1.08
    cols = []
    for i, (lab, v, chg) in enumerate(series):
        h = max(8, round(30 * v / vmax))
        cls = "bar now" if i == len(series) - 1 else "bar"
        inner = f'<span class="chg">{_h(chg)}</span>' if chg else ""
        cols.append(f'<div class="col"><div class="v">{_h(unit_fmt(v))}</div>'
                    f'<div class="{cls}" style="height:{h}px">{inner}</div>'
                    f'<div class="x">{_h(lab)}</div></div>')
    # The future slot is a small box on the baseline, so its height suggests no
    # magnitude.
    if gap:      # months between the series and the future slot (G3: months 4 to 8)
        cols.append('<div class="col gapcol"><div class="v">&nbsp;</div><div class="dots">…</div>'
                    '<div class="x">&nbsp;</div></div>')
    cols.append(f'<div class="col fut"><div class="v">&nbsp;</div><div class="bar q">?</div>'
                f'<div class="x">{_h(future_label)}</div></div>')
    html_block(f'<div class="fs-chart" role="img" aria-label="{_h(caption)}">'
               f'<div class="cap">{_h(caption)}</div><div class="bars{" gap" if gap else ""}">'
               f'{"".join(cols)}</div></div>')


def facts(items: list[tuple[str, str]]) -> None:
    cells = "".join(f'<div class="fs-fact"><div class="t">{_h(t)}</div>'
                    f'<div class="d">{_h(d)}</div></div>' for t, d in items)
    html_block(f'<div class="fs-facts">{cells}</div>')


def terms(items: list[tuple[str, str]]) -> None:
    rows = "".join(f'<div class="row"><div class="h">{_h(t)}</div>'
                   f'<div class="b">{_h(b).replace(chr(10), "<br>")}</div></div>'
                   for t, b in items)
    html_block(f'<div class="fs-terms">{rows}</div>')


# ---------------------------------------------------------------------------
# Modes: "About you" looks like a form, the transition like a curtain
# ---------------------------------------------------------------------------

# "About you" has its own colors, clearly apart from the green and beige of
# the simulation (requirement of the supervisor): stone grey page, white card,
# charcoal panel, terracotta accent.
ABOUT_BG = "#E7E4E0"
ABOUT_CARD = "#FFFFFF"
ABOUT_DARK = "#2B2826"
ABOUT_ACCENT = "#A84A23"
ABOUT_SOFT = "#F6E9E2"
ABOUT_LINE = "#E1D9D3"

ABOUT_CSS = f"""
<style>
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
  background: {ABOUT_BG} !important;
}}
.stApp .block-container {{
  background: {ABOUT_CARD} !important; border: 1px solid {ABOUT_LINE}; border-radius: 22px;
  box-shadow: 0 10px 40px rgba(43,40,38,0.08);
  margin-top: 1.6rem; padding: 1.8rem 2rem 2.4rem 2rem !important;
}}
@media (max-width: 640px) {{ .stApp .block-container {{ border-radius: 0; margin-top: 0; padding: 1.2rem 1rem 2rem 1rem !important; }} }}

/* panel, progress, chips */
.stApp .fs-top {{ background: {ABOUT_DARK} !important; box-shadow: 0 10px 30px rgba(43,40,38,0.18) !important; }}
.stApp .fs-top .fs-step {{ background: rgba(255,255,255,0.08) !important; color: #CFC6C0 !important; }}
.stApp .fs-top .fs-step.now {{ background: {ABOUT_SOFT} !important; color: {ABOUT_DARK} !important; }}
.stApp .fs-top .fs-bar > div {{ background: linear-gradient(90deg, #C96A3F 0%, #E3A07E 55%, #F3D3C2 100%) !important; }}

/* banner */
.stApp .fs-about-banner {{ background: {ABOUT_SOFT} !important; border: 1px solid #EBC8B6 !important; }}
.stApp .fs-about-banner .t {{ color: {ABOUT_ACCENT} !important; }}
.stApp .fs-about-banner .ic {{ background: {ABOUT_ACCENT} !important; }}

/* buttons */
.stApp button[data-testid="stBaseButton-primary"], .stApp button[data-testid="stBaseButton-primaryFormSubmit"] {{
  background: {ABOUT_DARK} !important; border-color: {ABOUT_DARK} !important; }}
.stApp button[data-testid="stBaseButton-primary"]:hover,
.stApp button[data-testid="stBaseButton-primaryFormSubmit"]:hover {{ background: #45403C !important; }}

/* selections: radio cards and dots, pills, slider, focus */
.stApp label[data-testid="stRadioOption"]:has(input:checked) {{ border-color: {ABOUT_ACCENT} !important;
  background: {ABOUT_SOFT} !important; box-shadow: 0 0 0 1px {ABOUT_ACCENT} inset !important; }}
.stApp label[data-testid="stRadioOption"]:hover {{ border-color: #E3A07E !important; }}
.stApp label[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {{
  background-color: {ABOUT_ACCENT} !important; border-color: {ABOUT_ACCENT} !important; }}
.stApp div[data-testid="stButtonGroup"] button[aria-checked="true"],
.stApp div[data-testid="stButtonGroup"] button[aria-pressed="true"],
.stApp div[data-testid="stButtonGroup"] button[kind$="Active"] {{ background: {ABOUT_ACCENT} !important;
  border-color: {ABOUT_ACCENT} !important; }}
.stApp div[data-testid="stButtonGroup"] > div > button:hover {{ border-color: {ABOUT_ACCENT} !important; }}
.stApp div[data-testid="stSlider"] div[data-rac]:has(> div > input[type="range"]) {{
  background: {ABOUT_ACCENT} !important; box-shadow: 0 0 0 1px {ABOUT_ACCENT}, 0 2px 8px rgba(168,74,35,0.25) !important; }}
.stApp div[data-testid="stSlider"] div[data-testid="stSliderThumbValue"],
.stApp div[data-testid="stSlider"] div[data-testid="stSliderThumbValue"] * {{ color: {ABOUT_ACCENT} !important; }}
.stApp div[data-testid="stSelectbox"] > div > div:focus-within, .stApp div[data-testid="stNumberInputContainer"]:focus-within,
.stApp div[data-testid="stTextInputRootElement"]:focus-within, .stApp div[data-baseweb="select"]:focus-within,
.stApp div[data-baseweb="input"]:focus-within {{ border-color: {ABOUT_ACCENT} !important; box-shadow: 0 0 0 3px {ABOUT_SOFT} !important; }}
.stApp input, .stApp textarea {{ caret-color: {ABOUT_ACCENT} !important; }}
.stApp *:focus-visible {{ outline-color: {ABOUT_ACCENT} !important; }}
.stApp input, .stApp div[data-baseweb="select"], .stApp div[data-testid="stNumberInputContainer"],
.stApp div[data-testid="stTextInputRootElement"], .stApp label[data-testid="stRadioOption"],
.stApp div[data-testid="stButtonGroup"] button {{ background-color: #FFFFFF !important; }}
.stApp label[data-testid="stRadioOption"]:has(input:checked) {{ background: {ABOUT_SOFT} !important; }}
.stApp div[data-testid="stButtonGroup"] button[aria-checked="true"],
.stApp div[data-testid="stButtonGroup"] button[aria-pressed="true"] {{ background: {ABOUT_ACCENT} !important; }}
</style>
"""

USER_SVG = ('<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/>'
            '<path d="M4 21a8 8 0 0 1 16 0"/></svg>')


def about_mode(title: str, body: str) -> None:
    """Form look for the questions about the person, clearly apart from the
    simulation: cool grey page, white card, dark banner."""
    st.markdown(ABOUT_CSS, unsafe_allow_html=True)
    html_block(f'<div class="fs-about-banner"><div class="ic">{USER_SVG}</div><div>'
               f'<div class="t">{_h(title)}</div><div class="d">{_h(body)}</div></div></div>')


TRANSITION_CSS = f"""
<style>
html, body, .stApp {{ background: #0C261D !important; }}
[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] {{
  background: transparent !important;
}}
.stApp::before {{
  content: ""; position: fixed; inset: -20%; z-index: 0; pointer-events: none;
  background:
    radial-gradient(40% 35% at 30% 35%, rgba(45,106,79,0.60), transparent 70%),
    radial-gradient(35% 30% at 70% 60%, rgba(201,164,106,0.30), transparent 70%),
    radial-gradient(30% 30% at 55% 25%, rgba(149,213,178,0.20), transparent 70%);
  filter: blur(30px); animation: fs-aurora 9s ease-in-out infinite alternate;
}}
@keyframes fs-aurora {{
  0% {{ transform: translate3d(-3%, -2%, 0) scale(1); opacity: 0.85; }}
  100% {{ transform: translate3d(3%, 2%, 0) scale(1.08); opacity: 1; }}
}}
[data-testid="stMain"] {{ position: relative; z-index: 1; }}
.block-container {{ padding-top: 18vh !important; }}
.fs-curtain {{ text-align: left; }}
.fs-curtain .ey {{ color: #A7D7B8; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.18em;
  text-transform: uppercase; opacity: 0; animation: fs-up 900ms 300ms cubic-bezier(.2,.7,.2,1) forwards; }}
.fs-curtain .ti {{ color: #FFFFFF; font-size: 1.75rem; font-weight: 700; line-height: 1.08;
  letter-spacing: -0.035em; margin: 0.6rem 0 0.9rem 0; opacity: 0; animation: fs-up 1400ms 700ms cubic-bezier(.2,.7,.2,1) forwards; }}
.fs-curtain .bd {{ color: #CFE0D6; font-size: 1rem; line-height: 1.6; max-width: 30rem; opacity: 0;
  animation: fs-up 1300ms 1400ms cubic-bezier(.2,.7,.2,1) forwards; }}
.fs-curtain .ln {{ height: 2px; width: 0; margin: 1.8rem 0 1.6rem 0; border-radius: 2px;
  background: linear-gradient(90deg, #2D6A4F, #52B788, #B7E4C7); animation: fs-line 1700ms 1700ms cubic-bezier(.4,0,.2,1) forwards; }}
@keyframes fs-up {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes fs-line {{ to {{ width: 100%; }} }}
button[data-testid="stBaseButton-primary"] {{ background: #F7F5F0 !important; border-color: #F7F5F0 !important;
  opacity: 0; animation: fs-up 1000ms 2600ms cubic-bezier(.2,.7,.2,1) forwards; }}
button[data-testid="stBaseButton-primary"] * {{ color: #0C261D !important; }}
button[data-testid="stBaseButton-primary"]:hover {{ background: #F1ECE0 !important; }}
@media (prefers-reduced-motion: reduce) {{
  .stApp::before, .fs-curtain *, button[data-testid="stBaseButton-primary"] {{ animation: none !important; opacity: 1 !important; width: auto; }}
  .fs-curtain .ln {{ width: 100%; }}
}}
</style>
"""


def transition(eyebrow: str, title: str, body: str) -> None:
    """Full-screen curtain between the questions about the person and the
    simulation: dark page, moving light, text that rises in."""
    st.markdown(TRANSITION_CSS, unsafe_allow_html=True)
    html_block(f'<div class="fs-curtain"><div class="ey">{_h(eyebrow)}</div>'
               f'<div class="ti">{_h(title)}</div><div class="bd">{_h(body)}</div>'
               f'<div class="ln"></div></div>')


# ---------------------------------------------------------------------------
# Lumora: company card, messages, month end, journey
# ---------------------------------------------------------------------------

MAIL_SVG = ('<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>')


def company_card(name: str, meta: str, product: str, tags: list[str]) -> None:
    chips = "".join(f"<span>{_h(t)}</span>" for t in tags)
    html_block(f'<div class="fs-company">{logo(44)}<div><div class="nm">{_h(name)}</div>'
               f'<div class="mt">{_h(meta)}</div><div class="pd">{_h(product)}</div>'
               f'<div class="tags">{chips}</div></div></div>')


def message(sender: str, subject: str, text: str, to: str = "", signoff: str = "") -> None:
    """A decision that arrives as an email: sender, recipient, subject, body."""
    # `to` is accepted but not shown: one line less on a laptop screen (B5).
    rows = (f'<div class="row"><span>From</span><b>{_h(sender)}</b></div>'
            f'<div class="row"><span>Subject</span><b>{_h(subject)}</b></div>')
    greeting, _, rest = text.partition(", ")
    body = (f'<p><span class="gr">{_h(greeting)},</span> {_h(rest[:1].upper() + rest[1:])}</p>'
            if rest else f'<p>{_h(text)}</p>')
    sign = f'<p class="sg">{_h(signoff)}, {_h(sender)}</p>' if signoff else ""
    html_block(f'<div class="fs-msg"><div class="hd"><span class="ic">{MAIL_SVG}</span>'
               f'<div class="meta">{rows}</div><span class="tag">New</span></div>'
               f'<div class="tx">{body}{sign}</div></div>')


def month_end(title: str, body: str) -> None:
    """Short dark curtain over the monthly report; it fades by itself and never
    blocks a click."""
    html_block(f'<div class="fs-veil" aria-hidden="true"><div><div class="t">{_h(title)}</div>'
               f'<div class="b">{_h(body)}</div><div class="ln"></div></div></div>')


def journey(months: list[tuple[str, str, list[tuple[str, str]]]]) -> None:
    """Timeline of the decisions: (month label, area title, [(decision, choice)])."""
    out = []
    for head, title, items in months:
        rows = "".join(f'<div class="it"><span>{_h(d)}</span><span>{_h(c)}</span></div>'
                       for d, c in items)
        out.append(f'<div class="m"><div class="mh">{_h(head)}</div>'
                   f'<div class="mt">{_h(title)}</div>{rows}</div>')
    html_block(f'<div class="fs-journey">{"".join(out)}</div>')


def slider_ticks(options: list[str]) -> None:
    """All values of a slider under its track, at the positions of the steps."""
    n = len(options) - 1
    spans = "".join(f'<span style="left:{100 * i / n:.3f}%;--w:{96 / (n + 1):.2f}%">{_h(o)}</span>'
                    for i, o in enumerate(options))
    html_block(f'<div class="fs-ticks" aria-hidden="true">{spans}</div>')
