#!/usr/bin/env python3
"""Build every SVG tile of the profile README into assets/.

Usage: python3 scripts/build.py   (needs an authenticated `gh` for the contribution calendar)
Edit the data block below or assets/avatar.txt, then re-run.
"""
import json
import re
import subprocess
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

LOGIN = "piales00"
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
# (label, icon) — icons are simple-icons slugs vendored in assets/icons/
STACK = [("SuiteScript", "oracle"), ("JavaScript", "javascript"), ("Python", "python"), ("FastAPI", "fastapi"),
         ("Node.js", "nodedotjs"), ("PostgreSQL", "postgresql"), ("Docker", "docker"), ("Git", "git")]
PROJECTS = [
    ("masi", "Stellar · Rust · React", ["stellar", "rust", "react", "typescript"],
     "Marketplace de servicios para el hogar: el pago queda retenido en un contrato Soroban hasta que apruebas el trabajo."),
    ("java-ide.nvim", "Neovim · Lua · Java", ["neovim", "lua", "openjdk", "springboot"],
     "Plugin de Neovim para trabajar Java como en IntelliJ: crea proyectos Maven y Spring Boot, clases, y corre tests sin salir del editor."),
    ("TwinSlot", "Python · FastAPI · React", ["python", "fastapi", "react", "scikitlearn"],
     "Sombra digital de reslotting: recomienda en qué zona del almacén debería vivir cada SKU, con optimización y Machine Learning."),
]
CONTACT = ["linkedin", "dev.to", "email"]

PALETTE = ["#2e1065", "#4c1d95", "#6d28d9", "#7c3aed", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ede9fe"]
LEVELS = {"NONE": None, "FIRST_QUARTILE": "#4c1d95", "SECOND_QUARTILE": "#6d28d9",
          "THIRD_QUARTILE": "#8b5cf6", "FOURTH_QUARTILE": "#c4b5fd"}
BLOBS = ["#7c3aed", "#22d3ee", "#db2777"]
MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()

FONT = 13
CW = FONT * 0.6          # monospace advance
GAP = 6                  # transparent margin around each window, like hyprland gaps
RADIUS = 12
FULL, THIRD = 900, 300
PROJECT_COLS = int((THIRD - 2 * (GAP + 20)) / CW)

STYLE = f'''text {{ font: {FONT}px ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }}
.art, .cell {{ opacity: 0; animation: in .5s ease-out forwards; }}
.art, .val {{ fill: #c9d1d9; }}
.key {{ fill: #a78bfa; }}
.b {{ font-weight: 700; }}
.dim {{ fill: #8b949e; }}
.cyan {{ fill: #67e8f9; }}
.cursor {{ fill: #a78bfa; animation: blink 1.1s steps(1) infinite; }}
@keyframes in {{ to {{ opacity: 1; }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .art, .cell {{ animation: none; opacity: 1; }} .cursor {{ animation: none; }} }}'''


def text(x, y, body, cls, extra=""):
    # nbsp: plain spaces collapse in renderers that ignore white-space on svg text
    body = escape(body).replace(" ", " ")
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}"{extra}>{body}</text>'


def icon(name, x, y, size, fill="#c4b5fd"):
    d = re.search(r'<path d="([^"]+)"', (ASSETS / "icons" / f"{name}.svg").read_text()).group(1)
    return f'<path transform="translate({x:.1f} {y:.1f}) scale({size / 24:.4f})" fill="{fill}" d="{d}"/>'


def window(w, h, body, label, active=False, shift=0):
    """A hyprland-style window: blurred colour blobs behind tinted glass, rounded, gapped."""
    r = max(h * 0.6, 60)
    spots = [(0.12, 0.2), (0.88, 0.85), (0.55, 0.1), (0.3, 0.95)]
    blobs = "".join(
        f'<circle cx="{w * fx:.0f}" cy="{h * fy:.0f}" r="{r:.0f}" fill="{BLOBS[(i + shift) % len(BLOBS)]}"/>'
        for i, (fx, fy) in enumerate(spots[shift % 2:shift % 2 + 3]))
    box = f'x="{GAP}" y="{GAP}" width="{w - 2 * GAP}" height="{h - 2 * GAP}" rx="{RADIUS}"'
    border = 'stroke="url(#edge)" stroke-width="1.5"' if active else 'stroke="#ffffff" stroke-opacity=".14"'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h:.0f}" width="{w}" height="{h:.0f}" role="img" aria-label="{escape(label, {'"': "&quot;"})}">
<style>
{STYLE}
</style>
<defs>
<clipPath id="clip"><rect {box}/></clipPath>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{r * 0.5:.0f}"/></filter>
<linearGradient id="edge" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>
</defs>
<g clip-path="url(#clip)">
<rect width="{w}" height="{h:.0f}" fill="#0a0c12"/>
<g filter="url(#blur)" opacity=".5">{blobs}</g>
<rect width="{w}" height="{h:.0f}" fill="#0d1117" opacity=".6"/>
</g>
<rect {box} fill="none" {border}/>
{chr(10).join(body)}
</svg>
'''


def bar():
    h, mid = 46, 28
    out = [f'<rect x="20" y="16" width="26" height="14" rx="7" fill="#a78bfa"/>']
    out += [f'<circle cx="{62 + i * 20}" cy="23" r="4" fill="#ffffff" opacity=".25"/>' for i in range(3)]
    out.append(text(FULL / 2, mid, f"~/{LOGIN}", "val b", ' text-anchor="middle"'))
    out.append(text(FULL - 22, mid, "arch · hyprland · Lima, PE", "dim", ' text-anchor="end"'))
    return window(FULL, h, out, f"{LOGIN} — arch, hyprland, Lima", shift=1)


def card():
    art = (ASSETS / "avatar.txt").read_text().rstrip("\n").split("\n")
    row, pad, line = CW * 2, 22, 24  # row = 2 * CW keeps ascii cells 1:2 so the portrait is not stretched
    cols = max(len(l) for l in art)
    art_h = len(art) * row
    top = GAP + pad
    out = []
    # textLength pins every row to the grid whatever font the viewer falls back to
    for i, l in enumerate(art):
        body = l.lstrip()
        if not body:
            continue
        extra = f' textLength="{len(body) * CW:.1f}" lengthAdjust="spacingAndGlyphs" style="animation-delay:{i * 45}ms"'
        out.append(text(top + (len(l) - len(body)) * CW, top + (i + 0.8) * row, body, "art", extra))

    ix = top + cols * CW + 30
    vx = ix + 10 * CW
    y = top + (art_h - (len(INFO) + 5) * line) / 2 + line * 0.7
    out.append(text(ix, y, USER, "key b"))
    y += line
    out.append(text(ix, y, "─" * len(USER), "dim"))
    for key, value in INFO:
        y += line
        out.append(text(ix, y, key, "key"))
        out.append(text(vx, y, value, "val"))
    y += line * 1.2
    out += [f'<rect x="{ix + i * 26:.1f}" y="{y:.1f}" width="26" height="16" fill="{c}"/>' for i, c in enumerate(PALETTE)]
    y += line * 2.3
    out.append(text(ix, y, "❯", "key"))
    out.append(text(ix + 2 * CW, y, PROMPT, "val"))
    out.append(f'<rect class="cursor" x="{ix + (len(PROMPT) + 2.5) * CW:.1f}" y="{y - FONT:.1f}" width="{CW:.1f}" height="{FONT + 3}"/>')
    label = "Piero Pérez — " + ". ".join(v for _, v in INFO[:5])
    return window(FULL, 2 * top + art_h, out, label, active=True)


def stack():
    x0, y = GAP + 22, GAP + 34
    out = [text(x0, y, "❯", "key"), text(x0 + 2 * CW, y, "ls ~/stack", "val")]
    x, y = x0, y + 18
    for name, slug in STACK:
        w = len(name) * CW + 40
        if x + w > FULL - x0:
            x, y = x0, y + 36
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="28" rx="14" fill="#ffffff" fill-opacity=".05" stroke="#a78bfa" stroke-opacity=".45"/>')
        out.append(icon(slug, x + 10, y + 7, 14))
        out.append(text(x + 30, y + 18.5, name, "val"))
        x += w + 8
    return window(FULL, y + 28 + 22 + GAP, out, "Stack: " + ", ".join(n for n, _ in STACK), shift=2)


def calendar():
    query = ('{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions '
             'weeks{contributionDays{date weekday contributionLevel}}}}}}' % LOGIN)
    raw = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"], capture_output=True, text=True, check=True).stdout
    return json.loads(raw)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def contrib():
    cal = calendar()
    weeks = cal["weeks"]
    x0, y = GAP + 22, GAP + 34
    step = (FULL - 2 * x0) / len(weeks)
    size = step - 3.4
    total = f'{cal["totalContributions"]} contributions · last year'
    out = [text(x0, y, "❯", "key"), text(x0 + 2 * CW, y, "git log --oneline | wc -l", "val"),
           text(FULL - x0, y, total, "cyan", ' text-anchor="end"')]
    y += 26
    last_label, month = -9, None
    for i, week in enumerate(weeks):
        m = int(week["contributionDays"][0]["date"][5:7])
        if m != month:
            month = m
            if i - last_label > 2 and i < len(weeks) - 1:
                out.append(text(x0 + i * step, y, MONTHS[m - 1], "dim"))
                last_label = i
    y += 10
    for i, week in enumerate(weeks):
        for day in week["contributionDays"]:
            color = LEVELS[day["contributionLevel"]]
            fill = f'fill="{color}"' if color else 'fill="#ffffff" fill-opacity=".07"'
            out.append(f'<rect class="cell" style="animation-delay:{i * 14}ms" x="{x0 + i * step:.1f}" y="{y + day["weekday"] * step:.1f}" '
                       f'width="{size:.1f}" height="{size:.1f}" rx="3" {fill}/>')
    return window(FULL, y + 7 * step + 20 + GAP, out, f"{total} on GitHub")


def project(i, name, tags, icons, blurb, rows):
    x0, y = GAP + 20, GAP + 34
    out = [text(x0, y, name, "key b"), text(x0, y + 22, tags, "cyan")]
    for n, l in enumerate(textwrap.wrap(blurb, PROJECT_COLS)):
        out.append(text(x0, y + 50 + n * 20, l, "val"))
    y += 50 + rows * 20
    out += [icon(slug, x0 + n * 28, y, 18) for n, slug in enumerate(icons)]
    out.append(text(THIRD - x0, y + 14, "↗", "dim", ' text-anchor="end"'))
    return window(THIRD, y + 18 + 20 + GAP, out, f"{name} — {tags}. {blurb}", shift=i)


def contact(i, name):
    return window(THIRD, 54, [text(THIRD / 2, 32, f"{name} ↗", "val", ' text-anchor="middle"')], name, shift=i + 1)


def build():
    tiles = {"bar": bar(), "card": card(), "stack": stack(), "contrib": contrib()}
    rows = max(len(textwrap.wrap(p[3], PROJECT_COLS)) for p in PROJECTS)  # same height for every project tile
    tiles |= {f"project-{i + 1}": project(i, *p, rows) for i, p in enumerate(PROJECTS)}
    tiles |= {f"contact-{name.replace('.', '')}": contact(i, name) for i, name in enumerate(CONTACT)}
    for name, svg in tiles.items():
        (ASSETS / f"{name}.svg").write_text(svg)
    print(f"wrote {len(tiles)} tiles to {ASSETS.relative_to(ROOT)}/")


if __name__ == "__main__":
    build()
