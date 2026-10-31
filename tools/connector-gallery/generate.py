"""Generate the connector-type gallery and the label-style comparison images.

Both are produced from pinconnect's own ``render_connector_svg`` — the exact
drawing the generator emits — laid out as dark grid cards and rasterized with
Playwright, so the docs never drift from the renderer.

Outputs:
  - docs/assets/pinconnect/connector-gallery.webp  — every bundled type, one card each (connector-types.md)
  - docs/assets/pinconnect/label-styles.webp       — one header under staggered/staircase/flat (board-toml.md)
  - docs/pinouts/connectors/connectors.{toml,webp} — the same cards as a board, with
    a hotspot over each, so the live gallery page can show every type's pins

Run from the repository root:

    python tools/connector-gallery/generate.py

Requires ``playwright`` and ``pillow`` (``pip install playwright pillow``);
Playwright drives the system Chrome (``channel="chrome"``), no download needed.
"""
import html
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright
from PIL import Image

import pinconnect
from pinconnect.config import load_connector_type, Connector, Pin, _DEFAULT_COLORS_DARK
from pinconnect.renderer import render_connector_svg

REPO = Path(__file__).resolve().parent.parent.parent
CONN_DIR = Path(pinconnect.__file__).resolve().parent / "connectors"
ASSETS = REPO / "docs" / "assets" / "pinconnect"
LIVE = REPO / "docs" / "pinouts" / "connectors"

# Grouped by family so the gallery reads sensibly rather than alphabetically.
# "none" is deliberately absent: it draws nothing, so its card would be blank.
GALLERY_ORDER = ["XH-F", "PH-F", "MX-F-1R", "MX-F-2R", "SHERLOCK-F",
                 "HDR-127", "HDR-127-2R", "HDR-200", "HDR-200-2R",
                 "HDR-254", "HDR-254-2R",
                 "ST-254", "ST-508", "ST-BR-508", "ST-BR-950",
                 "XT30-2+2", "STEPSTICK-F", "slide-switch", "button", "USB-C"]
PALETTE = ["#E74C3C", "#F39C12", "#2ECC71", "#3498DB", "#9B59B6", "#1ABC9C"]
# Location markers read best with no pins (the docs say to leave pins off these).
NO_PINS = {"USB-C", "button"}

_VARS = ";".join(f"--{k}:{v}" for k, v in _DEFAULT_COLORS_DARK.items())
_FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
          '<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600'
          '&family=Roboto+Mono:wght@500&display=swap" rel="stylesheet">')


def _page(cards_html, cols):
    return f"""<!doctype html><html><head><meta charset="utf-8">{_FONTS}
<style>
  :root{{{_VARS};--label-font:Roboto}}
  *{{box-sizing:border-box;margin:0}}
  body{{background:var(--bg);font-family:Roboto,sans-serif;padding:28px}}
  .grid{{display:grid;grid-template-columns:repeat({cols},1fr);gap:18px;max-width:1180px;margin:auto}}
  .card{{background:#1b1b1b;border:1px solid var(--divider);border-radius:12px;
         padding:16px 14px 12px;display:flex;flex-direction:column;align-items:center}}
  .art{{height:{'210' if cols == 3 else '150'}px;width:100%;display:flex;align-items:center;justify-content:center}}
  .art svg{{max-width:100%;max-height:{'210' if cols == 3 else '150'}px;width:auto;height:auto}}
  figcaption{{margin-top:12px;text-align:center;line-height:1.35}}
  .nm{{display:block;font-family:'Roboto Mono',monospace;font-weight:500;font-size:14px;color:var(--text)}}
  .st{{display:block;font-size:12px;color:var(--type-color)}}
</style></head><body><div class="grid">{cards_html}</div></body></html>"""


def _pins_for(ct):
    """A small, representative pin set colored from the palette.

    A type that declares its own default pins is shown with exactly those, so
    the card carries the real layout (a StepStick is 8 + 8 + 2, not 3 + 3).
    """
    geo = ct.geometry
    if ct.default_pins:
        return [Pin(name="", color=PALETTE[k % len(PALETTE)], row=p.row)
                for k, p in enumerate(ct.default_pins)]
    if geo.row2_pin_pitch_y > 0:      # XT30-2+2: 2 power + 2 vertical signal
        spec = [(1, 2), (2, 2)]
    elif geo.rows >= 2:               # two-row grid: 3 over 3
        spec = [(1, 3), (2, 3)]
    else:
        spec = [(1, 4)]
    pins, k = [], 0
    for row, count in spec:
        for _ in range(count):
            pins.append(Pin(name="", color=PALETTE[k % len(PALETTE)], row=row))
            k += 1
    return pins


def _svg(type_name, ct, pins, label_style="staggered"):
    conn = Connector(id=type_name, name="", type=type_name, pins=pins,
                     x1=0, y1=0, x2=100, y2=100, label_style=label_style)
    return render_connector_svg(conn, ct)


def build_gallery():
    cards = []
    for name in GALLERY_ORDER:
        ct = load_connector_type(CONN_DIR / f"{name}.toml")
        pins = [] if name in NO_PINS else _pins_for(ct)
        cards.append(
            f'<figure class="card"><div class="art">{_svg(name, ct, pins)}</div>'
            f'<figcaption><span class="nm">{html.escape(name)}</span>'
            f'<span class="st">{html.escape(ct.style)}</span></figcaption></figure>')
        print(f"  gallery: {name} ({ct.style})")
    return _page("\n".join(cards), cols=4)


def build_label_styles():
    ct = load_connector_type(CONN_DIR / "HDR-254.toml")
    names = ["GND", "5V", "TX0", "RX0", "SDA", "SCL", "EN", "3V3"]
    colors = ["#2C3E50", "#E74C3C", "#F39C12", "#F39C12", "#2ECC71", "#2ECC71", "#3498DB", "#E74C3C"]
    cards = []
    for style in ("staggered", "staircase", "flat"):
        pins = [Pin(name=n, color=c) for n, c in zip(names, colors)]
        cards.append(
            f'<figure class="card"><div class="art">{_svg("HDR-254", ct, pins, style)}</div>'
            f'<figcaption><span class="nm">{style}</span></figcaption></figure>')
        print(f"  label-styles: {style}")
    return _page("\n".join(cards), cols=3)


def shoot(page_html, out_webp, viewport_h, tmp):
    html_path = tmp / "page.html"
    html_path.write_text(page_html, encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        page = browser.new_context(viewport={"width": 1240, "height": viewport_h},
                                   device_scale_factor=2, color_scheme="dark").new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(500)
        png = tmp / "shot.png"
        page.locator(".grid").screenshot(path=str(png))
        browser.close()
    im = Image.open(png)
    im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    im.save(out_webp, quality=92, method=6)
    print(f"  -> {out_webp.relative_to(REPO)}  {im.size[0]}x{im.size[1]}  {out_webp.stat().st_size // 1024}KB")


# Pin names for the live board, where hovering a card shows its pins.
PIN_NAMES = ["GND", "VIN", "SDA", "SCL", "TX", "RX", "EN", "3V3"]


def _toml_str(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_live(tmp):
    """The gallery as a board: the cards are its image, with a hotspot over each.

    The cards are shot with a transparent background, so they read as tiles on
    the docs site in either color scheme, and each hotspot is its card's box.
    """
    html_path = tmp / "live.html"
    html_path.write_text(build_gallery(), encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        page = browser.new_context(viewport={"width": 1240, "height": 900},
                                   device_scale_factor=2, color_scheme="dark").new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.add_style_tag(content="body{background:transparent}")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(500)
        grid = page.locator(".grid")
        origin = grid.bounding_box()
        boxes = [card.bounding_box() for card in page.locator(".card").all()]
        png = tmp / "live.png"
        grid.screenshot(path=str(png), omit_background=True)
        browser.close()
    im = Image.open(png)
    scale = im.width / origin["width"]
    LIVE.mkdir(parents=True, exist_ok=True)
    image = LIVE / "connectors.webp"
    im.save(image, quality=92, method=6)

    lines = [
        "# Generated by tools/connector-gallery/generate.py from the bundled",
        "# connector types. Do not edit by hand: rerun the script instead.",
        "",
        "[board]",
        'title = "Connector gallery"',
        f'image = "{image.name}"',
        f"width = {im.width}",
        f"height = {im.height}",
    ]
    for name, box in zip(GALLERY_ORDER, boxes):
        ct = load_connector_type(CONN_DIR / f"{name}.toml")
        x1 = round((box["x"] - origin["x"]) * scale)
        y1 = round((box["y"] - origin["y"]) * scale)
        lines += [
            "",
            "[[connector]]",
            f"id = {_toml_str(name)}",
            f"name = {_toml_str(name)}",
            f"type = {_toml_str(name)}",
            f"x1 = {x1}",
            f"y1 = {y1}",
            f"x2 = {x1 + round(box['width'] * scale)}",
            f"y2 = {y1 + round(box['height'] * scale)}",
            f"description = {_toml_str(f'The bundled {name} type, drawn by the {ct.style} style.')}",
        ]
        pins = [] if name in NO_PINS else _pins_for(ct)
        for k, pin in enumerate(pins):
            lines += ["", "  [[connector.pin]]",
                      f"  name = {_toml_str(PIN_NAMES[k % len(PIN_NAMES)])}",
                      f"  color = {_toml_str(pin.color)}"]
            if pin.row != 1:
                lines.append(f"  row = {pin.row}")
    board = LIVE / "connectors.toml"
    board.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"  -> {board.relative_to(REPO)}, {image.relative_to(REPO)}  "
          f"{im.size[0]}x{im.size[1]}  {image.stat().st_size // 1024}KB")


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        shoot(build_gallery(), ASSETS / "connector-gallery.webp", 900, tmp)
        shoot(build_label_styles(), ASSETS / "label-styles.webp", 400, tmp)
        build_live(tmp)
    print("OK")


if __name__ == "__main__":
    main()
