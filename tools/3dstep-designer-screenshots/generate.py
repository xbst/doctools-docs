"""Regenerate the screenshots of the 3DStep designer used in the 3DStep docs.

Playwright drives the system Chrome against a copy of the installed designer
served on a local port. It imports a STEP file for the two import-dialog shots
(then cancels), opens a project (its TOML and GLB models), and captures the
panels, the viewport tools and the dialogs. The designer's chrome is dark, so
shots are taken dark at 2x.

Run from the repository root:

    python tools/3dstep-designer-screenshots/generate.py [PROJECT.toml [MODEL.step]]

Both arguments are optional. The project defaults to the live example in
docs/3d/pican2/, and the STEP file to the PiCAN 2 export the example was made
from, which lives outside this repository (in a 3DStep checkout beside it).
Without a STEP file the two import shots are skipped.

Requires ``playwright`` (``pip install playwright``); it drives the system
Chrome (``channel="chrome"``), so there is no browser download. The designer
loads Roboto from Google Fonts and Pyodide from a CDN, so this needs network
access.
"""
import shutil
import sys
import tempfile
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

try:
    import tomllib
except ModuleNotFoundError:          # Python 3.9 and 3.10
    import tomli as tomllib

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent.parent
ASSETS = REPO / "docs" / "assets" / "3dstep"

DEFAULT_PROJECT = REPO / "docs" / "3d" / "pican2" / "pican2.toml"
# The maintainer's STEP export of the example, outside this repository.
DEFAULT_STEP = REPO.parent / "3DStep" / "tests" / "fixtures" / "user" / "PiCAN2-in-Shell.step"

# The shots show this step of the project (1-based), the part the Move shot
# selects, and the part the Arrow shot starts on. Each falls back to what the
# project has.
SHOW_STEP = 2
MOVE_PART = "pican2"
# The window height for the Parts and Steps tab shots (the rest use 900).
SHORT_HEIGHT = 620


class _Handler(SimpleHTTPRequestHandler):
    """Static files with the content types the designer needs, whatever the
    system's MIME registry says (Windows can map .js to text/plain, and the
    browser then refuses the designer's modules)."""

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html",
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".css": "text/css",
        ".wasm": "application/wasm",
        ".zip": "application/zip",
        ".glb": "model/gltf-binary",
        ".svg": "image/svg+xml",
    }

    def log_message(self, *args):
        pass


def _served_designer(tmp: Path) -> Path:
    """A copy of the installed designer with the viewer runtime beside it and
    its payload built in, the way the docs describe serving it by hand.

    An installed 3dstep keeps the payload in the user cache and serves the
    viewer from the package, so serving the designer folder as is would boot
    into "Renderer unavailable" with no viewport. The copy leaves site-packages
    alone.
    """
    from threedstep.payload import PAYLOAD_NAME, build_payload, designer_root, viewer_root
    root = tmp / "designer"
    shutil.copytree(designer_root(), root, ignore=shutil.ignore_patterns(PAYLOAD_NAME, "__pycache__"))
    shutil.copytree(viewer_root(), root / "viewer", ignore=shutil.ignore_patterns("__pycache__"))
    build_payload(root / PAYLOAD_NAME, force=True)
    return root


def _project_files(project: Path, tmp: Path) -> list[Path]:
    """A copy of the project without its own theme, plus its models.

    The designer can only use the themes bundled with 3dstep, so a project
    naming a site theme previews with the default look and warns about it.
    That is correct and the docs describe it, but it makes a poor picture of
    the normal path, and the shots would depend on which project was passed.
    The original file is not modified.
    """
    text = project.read_text(encoding="utf-8")
    kept = [line for line in text.splitlines(keepends=True)
            if not line.strip().startswith(("theme ", "theme=", "theme_dir"))]
    copy = tmp / project.name
    copy.write_text("".join(kept), encoding="utf-8", newline="\n")
    models = tomllib.loads(text)["assembly"]["models"]
    return [copy] + [project.parent / m for m in models]


def _settle(page, ms: int = 900) -> None:
    """Let the viewer finish a step transition or camera flight (600 ms by
    default) and draw its last frame, and the fonts load."""
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(ms)


_written: list[str] = []


def _shot(target, name: str) -> None:
    """Screenshot a page or a locator into the assets folder."""
    target.screenshot(path=str(ASSETS / name))
    _written.append(name)
    print(f"  {name}")


def main(project: Path, step_file: Path | None) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    tmpdir = tempfile.TemporaryDirectory()
    tmp = Path(tmpdir.name)
    designer = _served_designer(tmp)
    files = _project_files(project, tmp)

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(_Handler, directory=str(designer)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900},
                                          device_scale_factor=2, color_scheme="dark")
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            # Generate, the themes and validation wait for Pyodide; shooting
            # before it lands captures "Starting renderer…" and a disabled
            # Generate button.
            page.wait_for_function("document.getElementById('runtime-status')?.classList.contains('ready')",
                                   timeout=180_000)
            # The About box opens itself on a first visit and would sit over
            # every shot; it gets its own shot at the end.
            page.click(".modal-close")
            page.wait_for_selector(".modal-backdrop", state="detached")

            # 1 + 2. The import dialog and its review, on a fresh designer. The
            # import is cancelled: the rest shows the finished project.
            if step_file is not None:
                page.set_input_files("#import-input", str(step_file))
                page.wait_for_selector('.modal [data-act="read"]')
                _settle(page, 300)
                _shot(page.locator(".modal"), "workflow-1-import.png")
                page.click('.modal [data-act="read"]')
                page.wait_for_selector('.modal [data-act="add"]:not([disabled])', timeout=300_000)
                _settle(page, 300)
                _shot(page.locator(".modal"), "workflow-2-review.png")
                page.click('.modal [data-act="cancel"]')
                page.wait_for_selector(".modal-backdrop", state="detached")

            # Open the project, as Open project does with the TOML and its GLBs.
            page.set_input_files("#open-input", [str(f) for f in files])
            page.wait_for_function("""() => {
                const d = window.threedstepDesigner;
                return d && d.state.loadedModels().length > 0 && d.viewport.viewer && d.viewport.viewer.ready;
            }""", timeout=60_000)
            steps = page.evaluate("window.threedstepDesigner.state.project.steps.length")
            step = max(0, min(SHOW_STEP, steps) - 1)
            page.evaluate(f"window.threedstepDesigner.state.setCurrentStep({step})")
            page.evaluate("window.threedstepDesigner.state.setSelection({parts: []})")
            # Validation runs 600 ms after a change and fills the status bar.
            page.wait_for_function("document.getElementById('statusbar')?.textContent.includes('valid')",
                                   timeout=30_000)
            page.get_by_role("tab", name="Parts", exact=True).click()
            _settle(page, 1500)

            # The overview: the Parts tab, the viewport on the step, the step's inspector.
            _shot(page, "designer-overview.png")
            _shot(page.locator(".toolbar"), "designer-toolbar.png")
            _shot(page.locator("#panel-inspector"), "workflow-6-inspector.png")
            page.get_by_role("tab", name="TOML", exact=True).click()
            _settle(page, 300)
            _shot(page.locator("#panel-left"), "workflow-8-toml.png")

            # The Parts and Steps tabs hold a short example: a lower window
            # keeps their shots from being mostly empty panel.
            page.set_viewport_size({"width": 1440, "height": SHORT_HEIGHT})
            page.get_by_role("tab", name="Parts", exact=True).click()
            _settle(page, 400)
            _shot(page.locator("#panel-left"), "workflow-3-parts.png")
            page.get_by_role("tab", name="Steps", exact=True).click()
            _settle(page, 300)
            _shot(page.locator("#panel-left"), "workflow-4-steps.png")
            page.get_by_role("tab", name="Parts", exact=True).click()
            page.set_viewport_size({"width": 1440, "height": 900})
            _settle(page, 600)

            # The Move gizmo on a part, and the inspector's part form.
            part = page.evaluate(f"""() => {{
                const st = window.threedstepDesigner.state;
                const parts = [...st.registry.parts];
                return parts.includes({MOVE_PART!r}) ? {MOVE_PART!r} : parts[0];
            }}""")
            page.evaluate(f"window.threedstepDesigner.state.selectParts([{part!r}])")
            page.evaluate("window.threedstepDesigner.viewport.setTool('move')")
            _settle(page, 600)
            _shot(page.locator("#panel-center"), "workflow-5-move.png")
            page.evaluate("window.threedstepDesigner.viewport.setTool('select')")
            page.evaluate("window.threedstepDesigner.state.setSelection({parts: []})")
            _settle(page, 300)

            # The Arrow tool halfway: the tail placed on a part, the head
            # following the pointer. The preview shows only over a surface, so
            # the head goes to the first nearby point where a part is hit.
            points = page.evaluate(f"""() => {{
                const d = window.threedstepDesigner, v = d.viewport.viewer;
                const bb = d.state.bboxOf([{part!r}]);
                const c = bb.min.map((m, i) => (m + bb.max[i]) / 2);
                const p = v.editor.project(c);
                if (!p || !p.visible) return null;
                const tries = [[150, -120], [170, -60], [120, 90], [-160, -100], [-150, 80], [90, -160]];
                for (const [dx, dy] of tries) {{
                    const h = v.pick(p.x + dx, p.y + dy);
                    if (h && h.id) return {{tail: [p.x, p.y], head: [p.x + dx, p.y + dy]}};
                }}
                return null;
            }}""")
            if points:
                page.evaluate("window.threedstepDesigner.viewport.setTool('arrow')")
                page.mouse.move(*points["tail"])
                page.mouse.down()
                page.mouse.up()
                page.mouse.move(*points["head"], steps=8)
                _settle(page, 400)
                _shot(page.locator("#panel-center"), "workflow-7-arrow.png")
                page.keyboard.press("Escape")
                page.keyboard.press("Escape")
                _settle(page, 300)

            # Generate: the real page in the preview, sized by its own height message.
            page.click("#generate-btn")
            page.wait_for_selector("#gen-theme")
            page.wait_for_function("""() => {
                const s = document.getElementById('gen-status');
                return s && /MB|KB/.test(s.textContent);
            }""", timeout=120_000)
            page.frame_locator("#gen-preview iframe").locator(".tds.tds-ready").wait_for(timeout=60_000)
            _settle(page, 1200)
            _shot(page.locator(".modal"), "workflow-9-generate.png")
            page.click(".modal-close")
            page.wait_for_selector(".modal-backdrop", state="detached")

            # Simplify, from the Parts tab.
            page.click('#parts-tab-panel [data-act="simplify"]')
            page.wait_for_selector('.modal [data-act="ok"]')
            _settle(page, 200)
            _shot(page.locator(".modal"), "designer-simplify.png")
            page.click('.modal [data-act="cancel"]')
            page.wait_for_selector(".modal-backdrop", state="detached")

            # The About box, the first thing a visitor to the hosted designer sees.
            page.click("#about-btn")
            page.wait_for_function("document.getElementById('about-version')?.textContent.startsWith('Version ')")
            _settle(page, 200)
            _shot(page.locator(".modal"), "designer-about.png")

            browser.close()
        print(f"OK - {len(_written)} designer screenshots written to {ASSETS.relative_to(REPO).as_posix()}/")
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
        tmpdir.cleanup()


if __name__ == "__main__":
    project_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PROJECT
    step_arg = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_STEP
    if not project_arg.is_file():
        sys.exit(f"project not found: {project_arg}\n"
                 "Pass a project TOML (its GLB models beside it): "
                 "python tools/3dstep-designer-screenshots/generate.py PROJECT.toml [MODEL.step]")
    if not step_arg.is_file():
        print(f"No STEP file at {step_arg}: skipping the two import shots.")
        step_arg = None
    main(project_arg, step_arg)
