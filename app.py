"""Mini Drone Parcel Route · local Streamlit demo.

Run with:  streamlit run app.py

Security notes
- No network calls, no file uploads, no eval/exec/pickle/subprocess.
- Every HTML string below is either a constant or built from validated
  numbers; anything text-like passes through html.escape first. st.html
  additionally sanitises with DOMPurify in the browser.
"""

from html import escape

import streamlit as st

from drone.astar import COLS, GOAL, ROWS, START, a_star
from drone.bayes import wind_belief
from drone.inputs import MAX_INPUT_CHARS, ObstacleError, parse_obstacles_strict
from drone.mdp import CRASH_PENALTY, DELIVERY_REWARD, WAIT_COST, break_even, choose_action
from drone.pipeline import run_mission

# ---------------------------------------------------------------- tokens ----
# Values copied from the akhmet-ds tokens.css (no CSS variables reach SVG
# attributes reliably, so the few colours used are listed once here).
BG = "#010102"
WELL = "#08080c"
SURFACE_1 = "#0e0e14"
SURFACE_2 = "#17171f"
SURFACE_3 = "#20202a"
TEXT = "#f7f8f8"
TEXT_MUTED = "#c3c7d1"
TEXT_SUBTLE = "#949aa6"
TEXT_FAINT = "#8a8f9d"
BORDER = "rgba(255,255,255,0.07)"
BORDER_STRONG = "rgba(255,255,255,0.13)"
GHOST_3 = "rgba(255,255,255,0.10)"
GHOST_4 = "rgba(255,255,255,0.15)"
ACCENT = "hsl(80 90% 60%)"          # Tracer lime · route and decision only
DANGER_TEXT = "#ff8b94"

# ------------------------------------------------------------- scenarios ----
SCENARIOS = {
    "Main · alert received": dict(obstacles="1,1 2,3 4,4", prior=0.30, p_w=0.80, p_c=0.20, alert=True),
    "No alert": dict(obstacles="1,1 2,3 4,4", prior=0.30, p_w=0.80, p_c=0.20, alert=False),
    "Two long walls": dict(obstacles="1,0 1,1 1,2 1,3 1,4 3,1 3,2 3,3 3,4 3,5",
                           prior=0.30, p_w=0.80, p_c=0.20, alert=False),
    "Goal walled in": dict(obstacles="4,5 5,4", prior=0.30, p_w=0.80, p_c=0.20, alert=True),
}
DEFAULT_SCENARIO = "Main · alert received"

st.set_page_config(
    page_title="Mini drone parcel route",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get help": None, "Report a bug": None, "About": None},
)

# ------------------------------------------------------------------- css ----
# Constant string only. Fonts are vendored woff2 files served by Streamlit's
# static serving from ./static, so the page makes no external requests.
FONT_FACES = "".join(
    f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;"
    f"src:url('app/static/fonts/{file}.woff2') format('woff2');}}"
    for fam, w, file in [
        ("Space Grotesk", 300, "SpaceGrotesk-300"),
        ("Space Grotesk", 400, "SpaceGrotesk-400"),
        ("Space Grotesk", 500, "SpaceGrotesk-500"),
        ("Inter", 400, "Inter-400"),
        ("Inter", 500, "Inter-500"),
        ("Inter", 600, "Inter-600"),
        ("Geist", "100 900", "Geist-400"),
        ("JetBrains Mono", "100 800", "JetBrainsMono-400"),
    ]
)

CSS = FONT_FACES + f"""
:root {{
  --bg:{BG}; --well:{WELL}; --surface-1:{SURFACE_1}; --surface-2:{SURFACE_2}; --surface-3:{SURFACE_3};
  --text:{TEXT}; --text-muted:{TEXT_MUTED}; --text-subtle:{TEXT_SUBTLE}; --text-faint:{TEXT_FAINT};
  --border:{BORDER}; --border-strong:{BORDER_STRONG}; --accent:{ACCENT};
  --font-display:"Space Grotesk","Inter",system-ui,sans-serif;
  --font-sans:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;
  --font-num:"Geist","Inter",system-ui,sans-serif;
  --font-mono:"JetBrains Mono",ui-monospace,monospace;
}}
html, body, .stApp {{ background:var(--bg); }}
.stApp {{ font-family:var(--font-sans); letter-spacing:-0.011em; }}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stAppDeployButton"], .stDeployButton {{ display:none !important; }}
header[data-testid="stHeader"] {{ background:transparent; height:0; }}
.block-container {{ padding-top:40px; padding-bottom:40px; max-width:1560px; }}
section[data-testid="stSidebar"] {{ background:var(--surface-1); border-right:1px solid var(--border); }}
section[data-testid="stSidebar"] .block-container, section[data-testid="stSidebarContent"] {{ padding-top:8px; }}
[data-testid="stWidgetLabel"] p {{ font-family:var(--font-mono) !important; text-transform:uppercase;
  font-size:11px !important; letter-spacing:0.08em !important; color:var(--text-subtle) !important; }}
.stTextInput input {{ font-family:var(--font-num) !important; font-feature-settings:"tnum" 1; border-radius:0; }}
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{
  font-family:var(--font-num) !important; font-feature-settings:"tnum" 1; }}

.eyebrow {{ font-family:var(--font-mono); font-size:11px; letter-spacing:0.08em; text-transform:uppercase;
  color:var(--text-subtle); margin:0 0 12px 0; }}
.eyebrow .p {{ color:var(--text-faint); }}
.num {{ font-family:var(--font-num); font-feature-settings:"tnum" 1; font-variant-numeric:tabular-nums lining-nums; }}
.frac {{ color:var(--text-faint); }}
.hero-title {{ font-family:var(--font-display); font-weight:300; font-size:44px; line-height:1.05;
  letter-spacing:-0.015em; color:var(--text); margin:0; }}
.hero-sub {{ font-size:15px; color:var(--text-subtle); margin:10px 0 0 0; max-width:820px; line-height:1.55; }}
.card {{ background:var(--surface-1); box-shadow:inset 0 0 0 1px var(--border); border-radius:2px;
  padding:20px 24px; margin:0 0 16px 0; }}
.card-grid {{ padding:24px; }}
.stats {{ font-family:var(--font-num); font-feature-settings:"tnum" 1; font-size:17px; color:var(--text);
  margin:16px 0 0 0; }}
.stats .sep {{ color:var(--text-faint); padding:0 8px; }}
.legend {{ font-family:var(--font-mono); font-size:11px; letter-spacing:0.08em; text-transform:uppercase;
  color:var(--text-faint); margin:10px 0 0 0; }}
.readout {{ font-family:var(--font-num); font-feature-settings:"tnum" 1; font-size:15px; color:var(--text-muted);
  line-height:1.7; margin:0; }}
.readout b {{ color:var(--text); font-weight:500; }}
.big {{ font-family:var(--font-num); font-feature-settings:"tnum" 1; font-size:30px; font-weight:500;
  color:var(--text); line-height:1.1; }}
.big .arrow {{ color:var(--text-faint); padding:0 10px; font-weight:400; }}
.biglabel {{ font-family:var(--font-sans); font-size:14px; font-weight:400; color:var(--text-subtle); margin-right:8px; }}
table.rt {{ border-collapse:collapse; width:100%; margin:4px 0 14px 0; }}
table.rt th {{ font-family:var(--font-mono); font-size:11px; letter-spacing:0.08em; text-transform:uppercase;
  color:var(--text-subtle); font-weight:400; text-align:right; padding:6px 10px; border-bottom:1px solid var(--border); }}
table.rt th:first-child, table.rt td:first-child {{ text-align:left; }}
table.rt td {{ font-family:var(--font-num); font-feature-settings:"tnum" 1; font-size:15px; color:var(--text-muted);
  text-align:right; padding:7px 10px; border-bottom:1px solid rgba(255,255,255,0.045); }}
table.rt td:first-child {{ font-family:var(--font-sans); color:var(--text-subtle); }}
.decision {{ font-family:var(--font-display); font-weight:300; font-size:112px; line-height:0.95;
  letter-spacing:-0.02em; color:var(--accent); margin:4px 0 10px -4px; }}
.why {{ font-size:15px; color:var(--text-subtle); margin:0; line-height:1.6; }}
.why .num {{ color:var(--text-muted); }}
.notice {{ font-size:13px; color:{DANGER_TEXT}; margin:0 0 12px 0; }}
.field-error {{ font-size:13px; line-height:1.45; color:{DANGER_TEXT}; background:rgba(240,97,109,0.10);
  box-shadow:inset 0 0 0 1px rgba(240,97,109,0.30); padding:8px 10px; margin:-6px 0 12px 0; border-radius:2px; }}
.side-note {{ font-size:12px; color:var(--text-faint); line-height:1.6; margin:8px 0 0 0; }}
.side-note .num {{ color:var(--text-subtle); }}
"""
st.html(f"<style>{CSS}</style>")


# --------------------------------------------------------------- helpers ----
def num(x: float, d: int = 2) -> str:
    """Format a number with a real minus sign. Input is always a float/int we computed."""
    s = f"{float(x):.{d}f}"
    return s.replace("-", "−")


def kpi(x: float, d: int = 2) -> str:
    """Greyed-fraction numeral: bright integer, dim fraction."""
    s = num(x, d)
    if "." in s:
        whole, frac = s.split(".")
        return f'{whole}<span class="frac">.{frac}</span>'
    return s


def eyebrow(text: str) -> str:
    return f'<div class="eyebrow"><span class="p">// </span>{escape(text)}</div>'


def grid_svg(obstacles: set, path: list | None, expanded: list) -> str:
    """6x6 grid as inline SVG, built only from integer cell coordinates."""
    cell, pad = 86, 28
    size = pad + COLS * cell
    parts = [f'<svg viewBox="0 0 {size + 2} {size + 2}" width="100%" style="max-width:{size + 2}px;display:block" '
             f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Grid with route">']
    mono = "font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;letter-spacing:0.08em"
    for i in range(COLS):
        parts.append(f'<text x="{pad + i * cell + cell / 2}" y="{pad - 10}" fill="{TEXT_FAINT}" '
                     f'text-anchor="middle" style="{mono}">{int(i)}</text>')
    for i in range(ROWS):
        parts.append(f'<text x="{pad - 12}" y="{pad + i * cell + cell / 2 + 4}" fill="{TEXT_FAINT}" '
                     f'text-anchor="middle" style="{mono}">{int(i)}</text>')
    expanded_set = set(expanded)
    for r in range(ROWS):
        for c in range(COLS):
            x, y = pad + c * cell, pad + r * cell
            if (r, c) in obstacles:
                parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{SURFACE_3}" '
                             f'stroke="{GHOST_3}" stroke-width="1"/>')
                for k in (19, 38, 57):   # crisp hatch, three hairlines
                    parts.append(f'<line x1="{x + k}" y1="{y + cell}" x2="{x + cell}" y2="{y + k}" '
                                 f'stroke="{GHOST_4}" stroke-width="1"/>')
                    parts.append(f'<line x1="{x}" y1="{y + k}" x2="{x + k}" y2="{y}" '
                                 f'stroke="{GHOST_4}" stroke-width="1"/>')
            else:
                parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{WELL}" '
                             f'stroke="{GHOST_3}" stroke-width="1"/>')
                if (r, c) in expanded_set and (r, c) not in (START, GOAL):
                    parts.append(f'<circle cx="{x + cell - 12}" cy="{y + 12}" r="3" fill="{TEXT_FAINT}"/>')
    if path:
        pts = " ".join(f"{pad + c * cell + cell / 2},{pad + r * cell + cell / 2}" for r, c in path)
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="4" '
                     f'stroke-linejoin="round" stroke-linecap="round"/>')
    for (r, c), label in ((START, "S"), (GOAL, "G")):
        cx, cy = pad + c * cell + cell / 2, pad + r * cell + cell / 2
        parts.append(f'<rect x="{cx - 20}" y="{cy - 20}" width="40" height="40" fill="{SURFACE_2}" '
                     f'stroke="{BORDER_STRONG}" stroke-width="1" rx="2"/>')
        parts.append(f'<text x="{cx}" y="{cy + 8}" fill="{TEXT}" text-anchor="middle" '
                     f'style="font-family:\'Space Grotesk\',sans-serif;font-size:22px;font-weight:500">{label}</text>')
    parts.append("</svg>")
    return "".join(parts)


# ----------------------------------------------------------- state setup ----
def apply_scenario() -> None:
    preset = SCENARIOS[st.session_state["scenario"]]
    st.session_state["obstacles"] = preset["obstacles"]
    st.session_state["prior"] = preset["prior"]
    st.session_state["p_w"] = preset["p_w"]
    st.session_state["p_c"] = preset["p_c"]
    st.session_state["alert"] = preset["alert"]


if "scenario" not in st.session_state:
    st.session_state["scenario"] = DEFAULT_SCENARIO
    apply_scenario()
if "last_valid" not in st.session_state:
    st.session_state["last_valid"] = parse_obstacles_strict(SCENARIOS[DEFAULT_SCENARIO]["obstacles"])

# --------------------------------------------------------------- sidebar ----
with st.sidebar:
    st.html(eyebrow("Inputs"))
    st.selectbox("Scenario", list(SCENARIOS), key="scenario", on_change=apply_scenario)
    st.text_input("Obstacles", key="obstacles", max_chars=MAX_INPUT_CHARS,
                  help="Cells as row,col separated by spaces. Rows and columns run 0 to 5.")
    obstacle_error = None
    try:
        obstacles = parse_obstacles_strict(st.session_state["obstacles"])
        st.session_state["last_valid"] = obstacles
    except ObstacleError as e:
        obstacle_error = str(e)                     # message never contains raw input
        obstacles = st.session_state["last_valid"]
        st.html(f'<div class="field-error">{escape(obstacle_error)}<br>Format: 1,1 2,3 4,4</div>')
    st.slider("P(Windy) prior", 0.0, 1.0, step=0.01, key="prior")
    st.slider("P(alert | Windy)", 0.01, 0.99, step=0.01, key="p_w")
    st.slider("P(alert | Calm)", 0.01, 0.99, step=0.01, key="p_c")
    st.toggle("Alert received", key="alert")
    preset = SCENARIOS[st.session_state["scenario"]]
    edited = any(st.session_state[k] != preset[k] for k in ("obstacles", "prior", "p_w", "p_c", "alert"))
    st.html(
        '<p class="side-note">Grid <span class="num">6 × 6</span> · start <span class="num">(0,0)</span> · '
        'goal <span class="num">(5,5)</span> · 4 moves, cost <span class="num">1</span> each.<br>'
        + ("Edited from the preset." if edited else "Preset values.")
        + " All numbers are invented toy values.</p>"
    )

prior = float(st.session_state["prior"])
p_w = float(st.session_state["p_w"])
p_c = float(st.session_state["p_c"])
alert = bool(st.session_state["alert"])

# ------------------------------------------------------------- compute ------
path, expanded = a_star(START, GOAL, obstacles)
_, expanded_ucs = a_star(START, GOAL, obstacles, use_heuristic=False)

score_w = prior * (p_w if alert else 1 - p_w)
score_c = (1 - prior) * (p_c if alert else 1 - p_c)
bayes_ok = (score_w + score_c) > 0          # always true with the slider ranges; guarded anyway
b = wind_belief(prior, p_w, p_c, alert) if bayes_ok else None
mission = run_mission(obstacles, prior, p_w, p_c, alert) if (bayes_ok or path is None) else None

# ------------------------------------------------------------- header -------
st.html(
    eyebrow("AIF1303 · AI fundamentals · final project")
    + '<h1 class="hero-title">Mini drone parcel route.</h1>'
    + '<p class="hero-sub">A* finds the route, Bayes reads the weather alert, one Bellman update decides: '
      'fly now or wait.</p>'
)
st.html('<div style="height:24px"></div>')

left, right = st.columns([0.8, 1], gap="large")

# ------------------------------------------------------- 1 · grid (A*) -----
with left:
    if path is not None:
        stats = (f'<span class="num">L = {int(len(path) - 1)} steps</span><span class="sep">·</span>'
                 f'A* expanded <span class="num">{int(len(expanded))}</span> nodes<span class="sep">·</span>'
                 f'without heuristic <span class="num">{int(len(expanded_ucs))}</span>')
    else:
        stats = (f'No route to the goal<span class="sep">·</span>'
                 f'A* expanded <span class="num">{int(len(expanded))}</span> nodes<span class="sep">·</span>'
                 f'without heuristic <span class="num">{int(len(expanded_ucs))}</span>')
    notice = ('<div class="notice">Obstacle input is invalid · showing the last valid map.</div>'
              if obstacle_error else "")
    # st.html sanitises SVG away, so this one block uses st.markdown. Its HTML is
    # built only from constants and integer cell coordinates; no user text.
    st.markdown(
        '<div class="card card-grid">' + eyebrow("01 · A* search · shortest route") + notice
        + grid_svg(obstacles, path, expanded)
        + f'<div class="stats">{stats}</div>'
        + '<div class="legend">S start · G goal · hatched obstacle · dot node expanded by A*</div></div>',
        unsafe_allow_html=True,
    )

with right:
    # ---------------------------------------------------- 2 · Bayes ---------
    obs_word = "alert" if alert else "no alert"
    if bayes_ok:
        lw = "P(alert | Windy)" if alert else "P(no alert | Windy)"
        lc = "P(alert | Calm)" if alert else "P(no alert | Calm)"
        bayes_html = (
            f'<div class="big"><span class="biglabel">P(Windy)</span>{kpi(prior, 2)}'
            f'<span class="arrow">→</span><span class="biglabel">b =</span>{kpi(b, 4)}</div>'
            '<p class="readout" style="margin-top:12px">'
            f'score Windy = P(Windy) × {escape(lw)} = <span class="num">{num(prior)} × {num(p_w if alert else 1 - p_w)} = {num(score_w, 4)}</span><br>'
            f'score Calm = P(Calm) × {escape(lc)} = <span class="num">{num(1 - prior)} × {num(p_c if alert else 1 - p_c)} = {num(score_c, 4)}</span><br>'
            f'<b>b = P(Windy | {obs_word})</b> = <span class="num">{num(score_w, 4)} / ({num(score_w, 4)} + {num(score_c, 4)}) = <b>{num(b, 4)}</b></span>'
            f'<span style="color:var(--text-faint)"> · P(Calm | {obs_word}) = <span class="num">{num(1 - b, 4)}</span></span></p>'
        )
    else:
        bayes_html = ('<p class="readout">This observation has zero probability under the chosen inputs, '
                      'so Bayes’ rule is undefined. Move a slider.</p>')
    st.html('<div class="card">' + eyebrow("02 · Bayes · wind belief after the " + obs_word) + bayes_html + "</div>")

    # ---------------------------------------------------- 3 · MDP -----------
    if path is not None and b is not None:
        L = int(len(path) - 1)
        action, Q, R = choose_action(b, L)
        b_star = break_even(L)
        rows = "".join(
            f'<tr><td>{s}</td><td>{num(R[(s, "Fly")], 0)}</td><td>{num(R[(s, "Wait")], 0)}</td></tr>'
            for s in ("Calm", "Windy")
        )
        mdp_html = (
            '<table class="rt"><tr><th>R(s, a)</th><th>Fly</th><th>Wait</th></tr>' + rows + "</table>"
            f'<p class="readout">R(Calm, Fly) = <span class="num">{DELIVERY_REWARD} − L = {DELIVERY_REWARD} − {L} = {num(DELIVERY_REWARD - L, 0)}</span><br>'
            f'Q(Fly) = <span class="num">{num(1 - b, 4)} × {num(R[("Calm", "Fly")], 0)} + {num(b, 4)} × ({num(CRASH_PENALTY, 0)}) = <b>{num(Q["Fly"])}</b></span><br>'
            f'Q(Wait) = <span class="num">{num(1 - b, 4)} × ({num(WAIT_COST, 0)}) + {num(b, 4)} × ({num(WAIT_COST, 0)}) = <b>{num(Q["Wait"])}</b></span><br>'
            f'Break-even b* = <span class="num">(22 − L) / (40 − L) = {22 - L} / {40 - L} = <b>{num(b_star, 4)}</b></span>'
            '<span style="color:var(--text-faint)"> · fly only if b &lt; b*</span></p>'
        )
        if action == "Fly":
            why = (f'Q(Fly) <span class="num">{num(Q["Fly"])}</span> ≥ Q(Wait) <span class="num">{num(Q["Wait"])}</span>'
                   f' · b <span class="num">{num(b, 4)}</span> is below b* <span class="num">{num(b_star, 4)}</span>')
        else:
            why = (f'Q(Fly) <span class="num">{num(Q["Fly"])}</span> &lt; Q(Wait) <span class="num">{num(Q["Wait"])}</span>'
                   f' · b <span class="num">{num(b, 4)}</span> is above b* <span class="num">{num(b_star, 4)}</span>')
        decision = action.upper()
    elif path is None:
        rows = "".join(
            f'<tr><td>{s}</td><td>n/a</td><td>{num(WAIT_COST, 0)}</td></tr>' for s in ("Calm", "Windy"))
        mdp_html = (
            '<table class="rt"><tr><th>R(s, a)</th><th>Fly</th><th>Wait</th></tr>' + rows + "</table>"
            f'<p class="readout">No route, so Fly is not available. Q(Wait) = <span class="num"><b>{num(WAIT_COST)}</b></span><br>'
            '<span style="color:var(--text-faint)">run_mission returns “Wait (no route)” without computing Q(Fly).</span></p>'
        )
        why = "A* found no route to the goal, so the drone cannot fly."
        decision = "WAIT"
    else:
        mdp_html = '<p class="readout">Waiting for a defined wind belief.</p>'
        why = "No belief, no decision. Adjust the sensor sliders."
        decision = "WAIT"
    if mission is not None and not mission["action"].upper().startswith(decision):
        decision = "WAIT"                                    # never contradict run_mission
    st.html('<div class="card">' + eyebrow("03 · MDP · one Bellman update from V0 = 0") + mdp_html + "</div>")

    # ---------------------------------------------------- 4 · decision ------
    st.html('<div class="card">' + eyebrow("04 · Decision")
            + f'<div class="decision">{escape(decision)}</div><p class="why">{why}</p></div>')
