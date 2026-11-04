"""Regenerate the WebFlash screenshots used in the WebFlash docs.

Playwright drives the system Chrome against the installed ``webflash``: the
site, served by ``python -m webflash`` on a free local port, and the cards
(the generated pages) of the live examples in docs/firmware/, rendered with
the command line against that server's embed runtime and served on another
port. The builds really run: Pyodide comes from jsDelivr, the compiler and
the source snapshots from the assets the server is given. Flashing runs
against the site's scripted devices (``?mock=``), so no board is needed.

Each scene starts in a fresh browser context, so the download hints and the
caches read the same on every run. Shots are dark at 1x, 1280 px wide (the
cards at the card's own width), saved as WebP.

Run from the repository root:

    python tools/webflash-screenshots/generate.py --assets ASSETS [--only NAME ...]

``--assets`` is what ``webflash --assets`` takes: a folder holding
``toolchain/`` (an unpacked toolchain release and ``current.json``) and
``sources/`` (a ``webflash sources build`` output), or a URL serving them,
such as https://webflash.isiks.tech/ once the site is deployed. ``--only``
names the images to write (``site-build``, ``card-*``, ``theme-*``...); the
default is all of them.

Requires ``webflash``, ``playwright`` and ``pillow``; Playwright drives the
system Chrome (``channel="chrome"``), so there is no browser download. The
pages load Roboto from Google Fonts and Pyodide from a CDN, so this needs
network access.
"""
import argparse
import fnmatch
import io
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from PIL import Image
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent.parent
ASSETS = REPO / "docs" / "assets" / "webflash"
EXAMPLES = REPO / "docs" / "firmware"

WIDTH = 1280
CARD_WIDTH = 760           # a card's max-width is 720 px: the card is the page
PHONE = {"width": 375, "height": 812}
# The docs site's backgrounds, for the isikstech theme's transparent page.
SITE_BG = {"dark": "#131313", "light": "#F8F8F8"}
THEMES = ("default", "midnight", "slate", "workbench")
PASTED_VERSION = "v0.13.0-500-gdeadbee"
WEBP_QUALITY = 85

# Pinned for every page: About and the compiler pool read them, and the shots
# should not show the machine they were taken on.
INIT_SCRIPT = """
Object.defineProperty(Navigator.prototype, 'hardwareConcurrency', {get: () => 8});
Object.defineProperty(Navigator.prototype, 'deviceMemory', {get: () => 8});
if (navigator.storage && navigator.storage.estimate) {
  const estimate = navigator.storage.estimate.bind(navigator.storage);
  navigator.storage.estimate = async () => ({...(await estimate()), quota: 10 * 1024 ** 3});
}
"""

# The flash list, the build's clock, the status pills: what "done" looks like.
BUILT = "/^Built in/.test((document.querySelector({sel}) || {{}}).textContent || '')"


class _Handler(SimpleHTTPRequestHandler):
    """Static files with the content types the cards need, whatever the
    system's MIME registry says (Windows can map .js to text/plain)."""

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html",
        ".js": "text/javascript",
        ".css": "text/css",
        ".webp": "image/webp",
        ".bin": "application/octet-stream",
        ".toml": "text/plain",
    }

    def log_message(self, *args):
        pass


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _start_site(assets: str) -> tuple[subprocess.Popen, str]:
    """``python -m webflash`` on a free port, serving the toolchain and the
    sources from ``assets``. Returns the process and the site's URL."""
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "webflash", "--port", str(port), "--no-browser", "--assets", assets],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    url = None
    lines = []
    deadline = time.time() + 120
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            break
        lines.append(line.rstrip())
        if line.startswith("Serving:"):
            url = line.split(None, 1)[1].strip().rstrip("/") + "/"
            break
    if url is None:
        proc.kill()
        sys.exit("webflash did not start:\n" + "\n".join(lines))
    # Keep reading its output, so a full pipe never blocks the server.
    Thread(target=lambda: [None for _ in proc.stdout], daemon=True).start()
    with urllib.request.urlopen(url, timeout=60) as r:
        r.read()
    return proc, url


def _without_theme(src: Path, dest: Path) -> Path:
    """A copy of a board TOML for the site, without ``theme`` / ``theme_dir``.

    The examples name the docs site's own theme, which the site does not
    bundle: Generate would then list it as not bundled and say to render with
    the command line. That is correct and the docs describe it, but the
    dialog's normal path makes the better picture.
    """
    kept = [line for line in src.read_text(encoding="utf-8").splitlines(keepends=True)
            if not line.strip().startswith(("theme ", "theme=", "theme_dir"))]
    dest.write_text("".join(kept), encoding="utf-8", newline="\n")
    return dest


def _with_engine(toml: Path, engine_url: str) -> None:
    """Point a board TOML's card at the local server's embed runtime."""
    text = toml.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = text.replace("[board]\n", f'[board]\nengine_url = "{engine_url}"\n', 1)
    toml.write_text(text, encoding="utf-8", newline="\n")


def _render(toml: Path, out: Path, theme: str | None = None) -> None:
    cmd = [sys.executable, "-m", "webflash", str(toml), "-o", str(out)]
    if theme:
        cmd += ["-t", theme]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def _card_pages(tmp: Path, site: str) -> Path:
    """Copy docs/firmware/ (the boards, their files and the isikstech theme
    beside them), point the copies at the local runtime and render the cards:
    <board>/card.html, and the stm32g0b1-usb card in each bundled theme."""
    root = tmp / "firmware"
    shutil.copytree(EXAMPLES, root, ignore=shutil.ignore_patterns("*.webflash.html"))
    # The fallback is rendered as published, with the default engine_url: its
    # link names the hosted site, not this run's local port.
    board = root / "stm32g0b1-usb" / "stm32g0b1-usb.toml"
    _render(board, board.with_name("fallback-card.html"))
    for name in ("stm32g0b1-usb", "can-toolhead"):
        toml = root / name / f"{name}.toml"
        _with_engine(toml, f"{site}engine/v1/")
        _render(toml, toml.with_name("card.html"))
    for theme in THEMES:
        _render(board, board.with_name(f"theme-{theme}.html"), theme)
    (root / "fallback.html").write_text(
        "<!DOCTYPE html><html><head><meta charset='utf-8'></head>"
        f"<body style='margin:0;background:{SITE_BG['dark']}'>"
        "<iframe src='stm32g0b1-usb/fallback-card.html' style='border:0;display:block;width:100%;height:1400px'></iframe>"
        "</body></html>", encoding="utf-8")
    return root


# ── Shots ────────────────────────────────────────────────────────────

_written: list[str] = []
_wanted: list[str] = []


def wanted(*names: str) -> bool:
    """Whether any of these images is to be written (--only)."""
    return not _wanted or any(fnmatch.fnmatch(n, w) or n == w for n in names for w in _wanted)


def _settle(page, ms: int = 500) -> None:
    """Fonts in, no hover or focus ring left over, the last frame drawn."""
    page.evaluate("document.fonts.ready")
    page.mouse.move(0, 0)
    page.evaluate("document.activeElement && document.activeElement !== document.body && document.activeElement.blur && document.activeElement.blur()")
    page.wait_for_timeout(ms)


def _box(page, selector: str) -> dict:
    """An element's box in page coordinates."""
    return page.evaluate("""(sel) => {
        const r = document.querySelector(sel).getBoundingClientRect();
        return {x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: r.height};
    }""", selector)


def _union(*boxes: dict) -> dict:
    x0 = min(b["x"] for b in boxes)
    y0 = min(b["y"] for b in boxes)
    x1 = max(b["x"] + b["width"] for b in boxes)
    y1 = max(b["y"] + b["height"] for b in boxes)
    return {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}


def _margin(box: dict, top: int, right: int, bottom: int, left: int, end: float | None = None) -> dict:
    """A box grown by a margin on each side; ``end`` is the page y it ends
    at instead of its own bottom, before the bottom margin."""
    if end is None:
        end = box["y"] + box["height"]
    x0, y0 = box["x"] - left, box["y"] - top
    return {"x": x0, "y": y0, "width": box["width"] + left + right, "height": end + bottom - y0}


def _shot(page, name: str, *, box: dict | None = None, select: str | None = None, pad: int = 16) -> None:
    """Screenshot the page, an element (``select``) or a region (``box``),
    with ``pad`` pixels of what surrounds it, into the assets folder as WebP."""
    if not wanted(name):
        return
    if select:
        box = _box(page, select)
    if box:
        size = page.evaluate("({w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight})")
        x0, y0 = max(0, box["x"] - pad), max(0, box["y"] - pad)
        x1 = min(size["w"], box["x"] + box["width"] + pad)
        y1 = min(size["h"], box["y"] + box["height"] + pad)
        png = page.screenshot(full_page=True, clip={"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0})
    else:
        png = page.screenshot(full_page=True)
    image = Image.open(io.BytesIO(png)).convert("RGB")
    image.save(ASSETS / f"{name}.webp", "WEBP", quality=WEBP_QUALITY, method=6)
    _written.append(name)
    print(f"  {name}.webp  ({image.width}x{image.height})")


# ── The site ─────────────────────────────────────────────────────────

def _context(browser, scheme: str = "dark", width: int = WIDTH, height: int = 900, js: bool = True):
    context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1,
                                  color_scheme=scheme, java_script_enabled=js)
    if js:
        context.add_init_script(INIT_SCRIPT)
    return context


def _open_site(context, site: str, query: str = ""):
    page = context.new_page()
    page.goto(site + query, wait_until="networkidle")
    # The flash panel mounts last; Upload firmware waits for it.
    page.wait_for_function("!document.getElementById('upload-firmware').disabled", timeout=60_000)
    return page


def _open_toml(page, files: list[Path]) -> None:
    """Open a board TOML (and the files it names) as Open TOML does, and
    wait for Configure to show its tree."""
    page.set_input_files("#open-toml", [str(f) for f in files])
    _wait_configured(page)


def _wait_configured(page, groups: int = 3) -> None:
    """Configure shows the tree: a pair's three groups (groups=3), or one
    firmware's options (groups=0)."""
    test = (f"document.querySelectorAll('#kconfig-tree .kc-group-head').length >= {groups}" if groups
            else "document.querySelectorAll('#kconfig-tree .kc-row').length > 3")
    page.wait_for_function(test, timeout=180_000)
    page.wait_for_function("document.querySelector('#status-chip .chip-text').textContent === 'Ready'",
                           timeout=180_000)


def _build(page) -> None:
    """Build from Configure: the Build step starts it, or asks first (a TOML
    opened without page 1's Next agreed to no download) and is answered."""
    page.click('[data-step="configure"] [data-wiz-next]')
    page.wait_for_function(BUILT.format(sel="'#build-clock'") +
                           " || !!document.querySelector('#build-start:not([hidden]) button.primary')",
                           timeout=300_000)
    start = page.locator("#build-start:not([hidden]) button.primary")
    if start.count():
        start.click()
    page.wait_for_function(BUILT.format(sel="'#build-clock'"), timeout=300_000)


def _wait_modal(page) -> None:
    page.wait_for_selector(".modal", timeout=10_000)


def _close_modal(page) -> None:
    page.click(".modal-close")
    page.wait_for_selector(".modal", state="detached")


def site_firmware(browser, site: str) -> None:
    """Page 1: the Katapult box ticked, the pickers, the download hint;
    a version picker open; a pasted Mainsail version."""
    if not wanted("site-firmware", "site-version-picker", "site-version-closest"):
        return
    context = _context(browser)
    page = _open_site(context, site)
    page.wait_for_function("!document.querySelector('#fw-version .wf-vp-input').disabled", timeout=60_000)
    page.click('[data-fw="klipper"]')
    page.check("#katapult-check")
    page.wait_for_function("/^Next downloads/.test(document.querySelector('[data-step=\"firmware\"] [data-wiz-hint]').textContent)",
                           timeout=60_000)
    _settle(page)
    _shot(page, "site-firmware", select="#wizard")

    # Kalico's list has every group: Latest, Releases, a branch, older
    # commits. The list shows them all at once, only taller than its usual
    # 22em, so the shot needs no scrolling.
    page.click('[data-fw="kalico"]')
    page.wait_for_function("!document.querySelector('#fw-version .wf-vp-input').disabled", timeout=60_000)
    page.add_style_tag(content="#fw-version .wf-vp-list{max-height:none !important}")
    page.click("#fw-version .wf-vp-toggle")
    page.wait_for_function("""() => {
        const list = document.querySelector('#fw-version .wf-vp-list');
        return !list.hidden && /Older commits/i.test(list.innerText) && !/Loading/.test(list.innerText);
    }""", timeout=60_000)
    page.mouse.move(0, 0)
    page.wait_for_timeout(400)
    # From the section's heading through the first few older commits: the
    # rest of the list is more of them.
    top = _box(page, "#wizard h3.sec")
    row = _box(page, "#wizard .fw")
    older = page.evaluate("""() => {
        const groups = [...document.querySelectorAll('#fw-version .wf-vp-list [role=group]')];
        const rows = groups[groups.length - 1].querySelectorAll('[role=option]');
        return rows[Math.min(3, rows.length - 1)].getBoundingClientRect().bottom + scrollY;
    }""")
    _shot(page, "site-version-picker", pad=0, box=_margin(_union(top, row), 16, 16, 8, 16, end=older))
    page.keyboard.press("Escape")

    # A version pasted from Mainsail: the closest kept commit, with a note.
    page.click('[data-fw="klipper"]')
    page.wait_for_function("!document.querySelector('#fw-version .wf-vp-input').disabled", timeout=60_000)
    page.evaluate("""(text) => {
        const input = document.querySelector('#fw-version .wf-vp-input');
        input.focus();
        input.value = text;
        input.dispatchEvent(new Event('input'));
        input.dispatchEvent(new Event('paste'));
    }""", PASTED_VERSION)
    page.wait_for_function("!document.querySelector('#fw-version .wf-vp-note').hidden", timeout=60_000)
    _settle(page)
    # The heading and the Firmware box, short of the Katapult box under it.
    box = _union(_box(page, "#wizard h3.sec"), _box(page, "#wizard .fw"))
    _shot(page, "site-version-closest", pad=0, box=_margin(box, 16, 16, 6, 16))
    context.close()


def site_pair(browser, site: str, tmp: Path) -> None:
    """stm32g0b1-usb with Katapult (the site keeps it ticked for an opened
    TOML), against the DFU mock: Configure, Build, Flash, Embed's Generate
    and About."""
    names = ("site-configure-pair", "site-build", "site-build-memory", "site-status-chip", "site-flash-pair",
             "site-flash-done", "site-flash-katapult", "site-generate", "site-about")
    if not wanted(*names):
        return
    context = _context(browser)
    page = _open_site(context, site, "?mock=dfu")
    folder = EXAMPLES / "stm32g0b1-usb"
    toml = _without_theme(folder / "stm32g0b1-usb.toml", tmp / "stm32g0b1-usb.toml")
    _open_toml(page, [toml, folder / "birds-nest.webp"])
    _settle(page)
    _shot(page, "site-configure-pair", select="#wizard")

    _build(page)
    _settle(page)
    _shot(page, "site-build", select="#wizard")
    page.click("#build-memory-box summary")
    _settle(page, 300)
    _shot(page, "site-build-memory", select="#wizard")
    page.click("#build-memory-box summary")

    page.click("#status-chip")
    page.wait_for_selector("#status-pop:not([hidden])")
    page.mouse.move(0, 0)
    page.wait_for_timeout(300)
    pop = _box(page, "#status-pop")
    top = _box(page, "header.top")
    _shot(page, "site-status-chip", box={"x": pop["x"] - 24, "y": 0, "width": top["x"] + top["width"] - pop["x"] + 24,
                                         "height": pop["y"] + pop["height"] + 8}, pad=0)
    page.click("#status-chip")
    page.wait_for_selector("#status-pop", state="hidden")

    page.click('[data-step="build"] [data-wiz-next]')
    page.wait_for_selector("#flash-connect")
    page.select_option("#flash-method", "dfu")
    _settle(page)
    _shot(page, "site-flash-pair", select="#wizard")
    page.click("#flash-connect")
    page.click("#flash-write", timeout=30_000)
    page.wait_for_selector("#flash-result.ok:not([hidden])", timeout=120_000)
    _settle(page)
    _shot(page, "site-flash-done", select="#wizard")
    page.select_option("#flash-method", "katapult")
    _settle(page)
    _shot(page, "site-flash-katapult", select="#wizard")

    # Generate: the preview runs the card itself, from this server.
    page.set_viewport_size({"width": WIDTH, "height": 1100})
    page.click('[data-step="flash"] [data-wiz-next]')
    page.click("#generate-btn")
    _wait_modal(page)
    page.wait_for_function("/KB/.test(document.getElementById('gen-status')?.textContent || '')", timeout=120_000)
    page.frame_locator("#gen-preview iframe").locator(".wf-app").wait_for(timeout=60_000)
    _settle(page, 1500)
    _shot(page, "site-generate", select=".modal", pad=0)
    _close_modal(page)

    # About, tall enough to show it whole.
    page.set_viewport_size({"width": WIDTH, "height": 1500})
    page.click("#about-btn")
    _wait_modal(page)
    page.wait_for_function("/Compiler workers/.test(document.querySelector('.modal').innerText)", timeout=30_000)
    _settle(page, 1000)
    _shot(page, "site-about", select=".modal", pad=0)
    context.close()


def site_can(browser, site: str, tmp: Path) -> None:
    """can-toolhead's CAN setup (Klipper and Katapult on PB0/PB1) against the
    candleLight mock: the node list, then Embed options."""
    if not wanted("site-flash-can", "site-embed-options"):
        return
    context = _context(browser)
    page = _open_site(context, site, "?mock=can")
    toml = _without_theme(EXAMPLES / "can-toolhead" / "can-toolhead.toml", tmp / "can-toolhead.toml")
    _open_toml(page, [toml])
    _build(page)
    page.click('[data-step="build"] [data-wiz-next]')
    page.wait_for_selector("#flash-connect")
    page.select_option("#flash-method", "katapult-can")
    page.click("#flash-connect")
    page.click("#flash-write", timeout=30_000)
    page.wait_for_selector("#flash-prompt .flash-nodes", timeout=30_000)
    _settle(page, 1000)
    _shot(page, "site-flash-can", select="#wizard")
    page.click('#flash-prompt button:has-text("Cancel")')
    page.wait_for_selector("#flash-prompt", state="hidden")

    page.set_viewport_size({"width": WIDTH, "height": 1600})
    page.click('[data-step="flash"] [data-wiz-next]')
    page.click("#tab-embed")
    _settle(page, 800)
    _shot(page, "site-embed-options", select="#wizard")
    context.close()


def site_error(browser, site: str) -> None:
    """A failed flash: the DFU mock refusing the claim (another program holds
    the device, or Windows has no WinUSB driver for it), with its fixes."""
    if not wanted("site-flash-error"):
        return
    context = _context(browser)
    # &os=windows: the fixes name Zadig whatever machine takes the shot.
    page = _open_site(context, site, "?mock=dfu&fail=claim&os=windows")
    page.wait_for_selector("#flash-connect")
    page.click("#flash-connect")
    page.wait_for_selector("#flash-result.error:not([hidden])", timeout=60_000)
    page.evaluate("document.getElementById('flash-help').open = true")
    _settle(page)
    _shot(page, "site-flash-error", select="#wizard")
    context.close()


def site_rp2040(browser, site: str, tmp: Path) -> None:
    """rp2040-katapult with Katapult ticked on page 1: an RP2040 pair."""
    if not wanted("site-configure-rp2040"):
        return
    context = _context(browser)
    page = _open_site(context, site)
    toml = _without_theme(EXAMPLES / "rp2040-katapult" / "rp2040-katapult.toml", tmp / "rp2040-katapult.toml")
    page.set_input_files("#open-toml", [str(toml)])
    _wait_configured(page, groups=0)
    page.click('[data-step="configure"] [data-wiz-back]')
    page.check("#katapult-check")
    page.click('[data-step="firmware"] [data-wiz-next]')
    _wait_configured(page)
    _settle(page, 800)
    _shot(page, "site-configure-rp2040", select="#wizard")
    context.close()


# ── The cards ────────────────────────────────────────────────────────

def _open_card(context, url: str, scheme: str, backdrop: bool = True):
    page = context.new_page()
    page.goto(url, wait_until="networkidle")
    if backdrop:
        # The isikstech theme's page is transparent: the docs site's background.
        page.add_style_tag(content=f"html,body{{background:{SITE_BG[scheme]} !important}}")
    page.wait_for_selector(".wf-app", timeout=60_000)
    page.wait_for_function("/^Next downloads/.test(document.querySelector('[data-step=\"firmware\"] [data-wiz-hint]')?.textContent || '')",
                           timeout=60_000)
    return page


def cards(browser, cards_url: str) -> None:
    board = cards_url + "stm32g0b1-usb/"
    if wanted("card-firmware-dark", "card-firmware-light", "card-phone"):
        context = _context(browser, width=CARD_WIDTH)
        for scheme in ("dark", "light"):
            page = _open_card(context, board + f"card.html?theme={scheme}", scheme)
            _settle(page)
            _shot(page, f"card-firmware-{scheme}", select="#wf-card")
            page.close()
        context.close()
        context = _context(browser, width=PHONE["width"], height=PHONE["height"])
        page = _open_card(context, board + "card.html?theme=dark", "dark")
        _settle(page)
        _shot(page, "card-phone")
        context.close()

    if wanted("card-setup"):
        context = _context(browser, width=CARD_WIDTH)
        page = _open_card(context, cards_url + "can-toolhead/card.html?theme=dark", "dark")
        page.click('[data-step="firmware"] [data-wiz-next]')
        page.wait_for_selector('[data-step="setup"]:not([hidden]) .wf-choice', timeout=60_000)
        page.wait_for_function("!document.querySelector('[data-step=\"setup\"] [data-wiz-next]').disabled", timeout=180_000)
        # The CAN bus speed reads "Default" until the configuration has
        # loaded, then the value the Kconfig gives it.
        page.wait_for_function("""() => {
            const s = document.querySelector('[data-step="setup"] .wf-choice select');
            return s && s.selectedOptions.length && !/^Default/.test(s.selectedOptions[0].textContent);
        }""", timeout=180_000)
        _settle(page, 800)
        _shot(page, "card-setup", select="#wf-card")
        context.close()

    if wanted("card-build", "card-flash"):
        context = _context(browser, width=CARD_WIDTH)
        page = _open_card(context, board + "card.html?theme=dark&mock=dfu", "dark")
        page.click('[data-step="firmware"] [data-wiz-next]')
        page.wait_for_function(BUILT.format(sel="'.wf-clock'"), timeout=300_000)
        _settle(page)
        _shot(page, "card-build", select="#wf-card")
        page.click('[data-step="build"] [data-wiz-next]')
        page.wait_for_selector(".wf-flash #flash-connect", timeout=30_000)
        page.select_option(".wf-flash #flash-method", "dfu")
        _settle(page)
        _shot(page, "card-flash", select="#wf-card")
        context.close()

    if wanted("card-fallback"):
        # JavaScript off: the static fallback, in a host page with the docs
        # site's background (a style added from here would need the page's JS).
        context = _context(browser, width=CARD_WIDTH, js=False)
        page = context.new_page()
        page.goto(cards_url + "fallback.html", wait_until="networkidle")
        page.wait_for_timeout(800)
        card = page.frame_locator("iframe").locator("#wf-card").bounding_box()
        _shot(page, "card-fallback", box=card)
        context.close()

    if wanted("theme-*"):
        context = _context(browser, width=CARD_WIDTH)
        for theme in THEMES:
            for scheme in ("dark", "light"):
                page = _open_card(context, board + f"theme-{theme}.html?theme={scheme}", scheme, backdrop=False)
                _settle(page)
                _shot(page, f"theme-{theme}-{scheme}", select="#wf-card")
                page.close()
        context.close()


# ── Main ─────────────────────────────────────────────────────────────

def main(assets: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    started = time.time()
    tmpdir = tempfile.TemporaryDirectory()
    tmp = Path(tmpdir.name)
    proc, site = _start_site(assets)
    server = None
    try:
        root = _card_pages(tmp, site)
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(_Handler, directory=str(root)))
        Thread(target=server.serve_forever, daemon=True).start()
        cards_url = f"http://127.0.0.1:{server.server_port}/"
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            site_firmware(browser, site)
            site_pair(browser, site, tmp)
            site_can(browser, site, tmp)
            site_error(browser, site)
            site_rp2040(browser, site, tmp)
            cards(browser, cards_url)
            browser.close()
        print(f"OK - {len(_written)} WebFlash screenshots written to {ASSETS.relative_to(REPO).as_posix()}/ "
              f"in {time.time() - started:.0f} s")
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        tmpdir.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Regenerate the WebFlash doc screenshots.")
    parser.add_argument("--assets", required=True, metavar="DIR|URL",
                        help="where the toolchain and the source snapshots come from, as webflash --assets takes it")
    parser.add_argument("--only", nargs="+", default=[], metavar="NAME",
                        help="write only these images (names without .webp; * and ? match)")
    args = parser.parse_args()
    if not args.assets.lower().startswith(("http://", "https://")) and not Path(args.assets).is_dir():
        sys.exit(f"assets folder not found: {args.assets}")
    _wanted.extend(args.only)
    main(args.assets)
