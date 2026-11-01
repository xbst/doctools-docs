"""Regenerate the bundled-theme gallery images for the 3DStep themes reference.

For each theme bundled with 3dstep, render a sample project with that theme,
open the page in the system Chrome (light and dark) on a step with a
highlighted part, an arrow and a label, so one frame shows nearly every theme
token, then save a WebP.

Outputs ``docs/assets/3dstep/theme-<name>-{light,dark}.webp`` for default,
slate, midnight and workbench.

Run from the repository root:

    python tools/3dstep-theme-gallery/generate.py [PROJECT.toml]

The project defaults to the live example in docs/3d/pican2/. Requires
``playwright`` and ``pillow``; Playwright drives the system Chrome
(``channel="chrome"``), so there is no browser download. The pages load their
fonts from Google Fonts, so this needs network access.
"""
import subprocess
import sys
import tempfile
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from PIL import Image
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent.parent
ASSETS = REPO / "docs" / "assets" / "3dstep"
DEFAULT_PROJECT = REPO / "docs" / "3d" / "pican2" / "pican2.toml"
THEMES = ["default", "slate", "midnight", "workbench"]
STEP = 2            # the step shown (1-based): the example's has a highlight, an arrow and a label
WIDTH = 1200        # the browser window; wider than every theme's stacking breakpoint
OUT_WIDTH = 1600    # the saved image


class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def render(project: Path, work: Path) -> None:
    """The project once per theme, written into `work` with 3dstep."""
    for theme in THEMES:
        out = work / f"{theme}.html"
        subprocess.run([sys.executable, "-m", "threedstep", str(project), "-o", str(out), "-t", theme],
                       check=True, stdout=subprocess.DEVNULL)
        print(f"  rendered {out.name}")


def shoot(work: Path) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(_Quiet, directory=str(work)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            for theme in THEMES:
                for scheme in ("light", "dark"):
                    ctx = browser.new_context(viewport={"width": WIDTH, "height": 800},
                                              device_scale_factor=2, color_scheme=scheme)
                    page = ctx.new_page()
                    page.goto(f"http://127.0.0.1:{server.server_port}/{theme}.html?theme={scheme}&step={STEP}",
                              wait_until="networkidle")
                    page.wait_for_selector(".tds.tds-ready")
                    page.evaluate("document.fonts.ready")
                    # The step is applied without a transition; workbench then
                    # plays the step's moves (autoplay), which takes play_ms.
                    page.wait_for_timeout(1800)
                    # A page opened on its own starts active (outlined in the
                    # accent color, for steering). Release it, as Escape does,
                    # so the shot shows the resting state an embed starts in.
                    page.locator("#tds").focus()
                    page.keyboard.press("Escape")
                    page.evaluate("document.activeElement && document.activeElement.blur()")
                    page.wait_for_timeout(300)
                    png = work / f"shot-{theme}-{scheme}.png"
                    page.locator("#tds").screenshot(path=str(png))
                    ctx.close()
                    im = Image.open(png).convert("RGB")
                    im = im.resize((OUT_WIDTH, round(im.height * OUT_WIDTH / im.width)), Image.LANCZOS)
                    out = ASSETS / f"theme-{theme}-{scheme}.webp"
                    im.save(out, quality=90, method=6)
                    print(f"  -> {out.name}  {im.size[0]}x{im.size[1]}  {out.stat().st_size // 1024} KB")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def main(project: Path) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        render(project, work)
        shoot(work)
    print(f"OK - {2 * len(THEMES)} theme gallery images written to {ASSETS.relative_to(REPO).as_posix()}/")


if __name__ == "__main__":
    project_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PROJECT
    if not project_arg.is_file():
        sys.exit(f"project not found: {project_arg}\n"
                 "Pass a project TOML (its GLB models beside it): python tools/3dstep-theme-gallery/generate.py PROJECT.toml")
    main(project_arg)
