#!/usr/bin/env python3
"""Build assets/card.svg (neofetch-style profile card) from assets/avatar.txt.

Usage: python3 scripts/build_card.py
Edit INFO below or assets/avatar.txt, then re-run.
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent

USER = "piero@github"
INFO = [
    ("role", "NetSuite Developer (in training)"),
    ("focus", "SuiteScript 2.x · ERP · API Integrations"),
    ("stack", "JS ES6+ · Python · FastAPI · PostgreSQL"),
    ("learning", "Oracle NetSuite · SDF · Order-to-Cash"),
    ("based", "Lima, Perú · UTP"),
    ("uptime", "on GitHub since 2024"),
    ("motto", "quien tiene un porqué"),
    ("", "soporta casi cualquier cómo."),
]
PROMPT = "building on NetSuite, one script at a time."
PALETTE = ["#2e1065", "#4c1d95", "#6d28d9", "#7c3aed", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ede9fe"]

FONT = 13
CW = FONT * 0.6          # monospace advance
ROW = CW * 2             # keeps ascii cells at 1:2 so the portrait is not stretched
PAD, BAR, GAP, LINE = 24, 36, 30, 24
WIDTH = 900


def text(x, y, body, cls, extra=""):
    # nbsp: plain spaces collapse in renderers that ignore white-space on svg text
    body = escape(body).replace(" ", "\u00a0")
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}"{extra}>{body}</text>'


def build():
    art = (ROOT / "assets" / "avatar.txt").read_text().rstrip("\n").split("\n")
    cols = max(len(line) for line in art)
    art_h = len(art) * ROW
    height = BAR + PAD + art_h + PAD
    out = []

    # ascii portrait: textLength pins every row to the grid whatever font the viewer falls back to
    for i, line in enumerate(art):
        body = line.lstrip()
        if not body:
            continue
        x = PAD + (len(line) - len(body)) * CW
        y = BAR + PAD + (i + 0.8) * ROW
        extra = f' textLength="{len(body) * CW:.1f}" lengthAdjust="spacingAndGlyphs" style="animation-delay:{i * 45}ms"'
        out.append(text(x, y, body, "art", extra))

    # info column, vertically centred against the portrait
    ix = PAD + cols * CW + GAP
    vx = ix + 10 * CW
    rows = len(INFO) + 6
    y = BAR + PAD + (art_h - rows * LINE) / 2 + LINE * 0.7
    out.append(text(ix, y, USER, "user"))
    y += LINE
    out.append(text(ix, y, "─" * len(USER), "dim"))
    for key, value in INFO:
        y += LINE
        out.append(text(ix, y, key, "key"))
        out.append(text(vx, y, value, "val"))
    y += LINE * 1.2
    for i, color in enumerate(PALETTE):
        out.append(f'<rect x="{ix + i * 26:.1f}" y="{y:.1f}" width="26" height="16" fill="{color}"/>')
    y += LINE * 2.3
    out.append(text(ix, y, "❯", "key"))
    out.append(text(ix + 2 * CW, y, PROMPT, "val"))
    out.append(f'<rect class="cursor" x="{ix + (len(PROMPT) + 2.5) * CW:.1f}" y="{y - FONT:.1f}" width="{CW:.1f}" height="{FONT + 3}"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height:.0f}" width="{WIDTH}" height="{height:.0f}" role="img" aria-label="Piero Pérez — NetSuite Developer in training. SuiteScript 2.x, JavaScript, Python, FastAPI. Lima, Perú.">
<style>
text {{ font: {FONT}px ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }}
.art {{ fill: #c9d1d9; opacity: 0; animation: in .5s ease-out forwards; }}
.user {{ fill: #a78bfa; font-weight: 700; }}
.key {{ fill: #a78bfa; }}
.val {{ fill: #c9d1d9; }}
.dim, .title {{ fill: #6e7681; }}
.cursor {{ fill: #a78bfa; animation: blink 1.1s steps(1) infinite; }}
@keyframes in {{ to {{ opacity: 1; }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .art {{ animation: none; opacity: 1; }} .cursor {{ animation: none; }} }}
</style>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1:.0f}" rx="10" fill="#0d1117" stroke="#30363d"/>
<path d="M0.5 {BAR}.5H{WIDTH - 0.5}" stroke="#30363d"/>
<circle cx="22" cy="18" r="6" fill="#ff5f57"/><circle cx="42" cy="18" r="6" fill="#febc2e"/><circle cx="62" cy="18" r="6" fill="#28c840"/>
<text x="{WIDTH / 2}" y="23" text-anchor="middle" class="title">piales00 — neofetch</text>
{chr(10).join(out)}
</svg>
'''


if __name__ == "__main__":
    target = ROOT / "assets" / "card.svg"
    target.write_text(build())
    print(f"wrote {target.relative_to(ROOT)}")
