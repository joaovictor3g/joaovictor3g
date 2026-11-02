"""Builds profile/assets/banner-{dark,light}.svg with subset fonts embedded."""

import base64
import io
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

FONTS = Path('/Users/victordias/Developer/projects/portfoliov4/src/fonts')
NEXT = Path('/Users/victordias/Developer/projects/portfoliov4/node_modules/next/dist/next-devtools/server/font')
OUT = Path(sys.argv[1])

EYEBROW = 'joão victor · fortaleza, brazil'
H1 = 'Software engineer.'
H2 = 'Edge cases included.'
FOOT = 'joaovictord.dev'
CMD = '$ npm test -- edge-cases'
CHECKS = ['empty state', 'slow 3G', 'screen reader', 'expired link', 'retry at 3 a.m.']
SUMMARY = f'{len(CHECKS)} passed'

DISPLAY_SRC = FONTS / 'space-grotesk-latin-wght.woff2'
MONO_SRC = NEXT / 'geist-mono-latin.woff2'


def subset_b64(src: Path, text: str) -> str:
    font = TTFont(src)
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = ['kern', 'liga']
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = 'woff2'
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def advance(src: Path, text: str, size: float, wght: int | None = None) -> float:
    """Approximate rendered width (default instance advances, no kerning)."""
    font = TTFont(src)
    if wght and 'fvar' in font:
        from fontTools.varLib.instancer import instantiateVariableFont

        font = instantiateVariableFont(font, {'wght': wght})
    cmap = font.getBestCmap()
    hmtx = font['hmtx']
    upm = font['head'].unitsPerEm
    return sum(hmtx[cmap[ord(c)]][0] for c in text if ord(c) in cmap) * size / upm


display_text = H1 + H2
mono_text = EYEBROW + FOOT + CMD + ''.join(CHECKS) + SUMMARY
display_b64 = subset_b64(DISPLAY_SRC, display_text)
mono_b64 = subset_b64(MONO_SRC, mono_text)

W, H = 1280, 400
H_SIZE = 70
X0 = 88
h2_width = advance(DISPLAY_SRC, H2, H_SIZE, 700)
h1_width = advance(DISPLAY_SRC, H1, H_SIZE, 700)
print(f'h1 {h1_width:.0f}px, h2 {h2_width:.0f}px', file=sys.stderr)

PANEL_X, PANEL_Y, PANEL_W, PANEL_H = 884, 66, 320, 268
assert X0 + h2_width + 40 < PANEL_X, 'headline runs into the panel'

THEMES = {
    'dark': dict(
        bg0='#0f0f17', bg1='#0a0a10', text='#fffdff', accent='#23dae5', muted='#9c9aac',
        eyebrow='#c9c2ff', rail='#2c2b38', plus='#4f4d5d', panel='#13121c',
        panel_border='#2c2b38', violet='#6d5cff', violet_a=0.32, cyan_a=0.10,
    ),
    'light': dict(
        bg0='#fffdff', bg1='#f1eeff', text='#0f0f17', accent='#007884', muted='#5b596a',
        eyebrow='#4f4d5d', rail='#e2e0f3', plus='#a9a7ba', panel='#ffffff',
        panel_border='#e2e0f3', violet='#6d5cff', violet_a=0.14, cyan_a=0.08,
    ),
}


def plus(x: float, y: float, color: str) -> str:
    return (
        f'<path d="M{x - 7} {y}h14M{x} {y - 7}v14" stroke="{color}" stroke-width="1.5"/>'
    )


def check(x: float, y: float, color: str) -> str:
    return (
        f'<path d="M{x} {y - 6}l5 5 9-10" fill="none" stroke="{color}" '
        'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def build(t: dict) -> str:
    rail = (40, 28, W - 40, H - 28)
    l, top, r, b = rail
    # The display class tightens tracking by 1.5px per glyph.
    cursor_x = X0 + h2_width - 1.5 * len(H2) + 12

    lines = []
    for i, label in enumerate(CHECKS):
        y = PANEL_Y + 90 + i * 30
        lines.append(
            f'<g class="line" style="animation-delay:{0.5 + i * 0.35:.2f}s">'
            f'{check(PANEL_X + 26, y, t["accent"])}'
            f'<text x="{PANEL_X + 50}" y="{y}" class="mono" font-size="19" fill="{t["text"]}">{label}</text>'
            '</g>'
        )
    summary_y = PANEL_Y + 90 + len(CHECKS) * 30 + 16
    lines.append(
        f'<text class="line mono" style="animation-delay:{0.5 + len(CHECKS) * 0.35 + 0.2:.2f}s" '
        f'x="{PANEL_X + 26}" y="{summary_y}" font-size="18" fill="{t["accent"]}">{SUMMARY}</text>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title">
<title id="title">João Victor. Software engineer. Edge cases included.</title>
<style>
@font-face {{ font-family: 'SG'; font-weight: 500 700; src: url(data:font/woff2;base64,{display_b64}) format('woff2'); }}
@font-face {{ font-family: 'GM'; font-weight: 400 600; src: url(data:font/woff2;base64,{mono_b64}) format('woff2'); }}
.display {{ font-family: 'SG', 'Space Grotesk', system-ui, sans-serif; font-weight: 700; letter-spacing: -1.5px; }}
.mono {{ font-family: 'GM', ui-monospace, SFMono-Regular, Menlo, monospace; }}
.line {{ animation: in .45s ease-out both; }}
.cursor {{ animation: blink 1.1s steps(1) infinite; }}
@keyframes in {{ from {{ opacity: 0; transform: translateY(4px); }} }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .line, .cursor {{ animation: none; }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/>
  </linearGradient>
  <radialGradient id="violet" cx="0.78" cy="0.05" r="0.55">
    <stop offset="0" stop-color="{t["violet"]}" stop-opacity="{t["violet_a"]}"/>
    <stop offset="1" stop-color="{t["violet"]}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="cyan" cx="0.08" cy="1" r="0.5">
    <stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["cyan_a"]}"/>
    <stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="{W}" height="{H}" rx="16" fill="url(#bg)"/>
<rect width="{W}" height="{H}" rx="16" fill="url(#violet)"/>
<rect width="{W}" height="{H}" rx="16" fill="url(#cyan)"/>
<path d="M{l} 0V{H}M{r} 0V{H}M0 {top}H{W}M0 {b}H{W}" stroke="{t["rail"]}" stroke-width="1"/>
{plus(l, top, t["plus"])}{plus(r, top, t["plus"])}{plus(l, b, t["plus"])}{plus(r, b, t["plus"])}
<text x="{X0}" y="112" class="mono" font-size="21" letter-spacing="0.5" fill="{t["eyebrow"]}">{EYEBROW}</text>
<text x="{X0}" y="204" class="display" font-size="{H_SIZE}" fill="{t["text"]}">{H1}</text>
<text x="{X0}" y="284" class="display" font-size="{H_SIZE}" fill="{t["accent"]}">{H2}</text>
<rect class="cursor" x="{cursor_x:.0f}" y="230" width="8" height="60" fill="{t["accent"]}"/>
<text x="{X0}" y="{b - 22}" class="mono" font-size="19" fill="{t["muted"]}">{FOOT}</text>
<rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="12" fill="{t["panel"]}" fill-opacity="0.85" stroke="{t["panel_border"]}"/>
<text x="{PANEL_X + 26}" y="{PANEL_Y + 44}" class="mono" font-size="17" fill="{t["muted"]}">{CMD}</text>
{''.join(lines)}
</svg>
'''


OUT.mkdir(parents=True, exist_ok=True)
for name, theme in THEMES.items():
    svg = build(theme)
    (OUT / f'banner-{name}.svg').write_text(svg)
    print(f'banner-{name}.svg {len(svg) / 1024:.1f} KB', file=sys.stderr)
