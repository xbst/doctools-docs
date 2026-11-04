# doctools-docs

The source of **<https://doctools.isiks.tech>**, the documentation site for Isik's Tech's open-source documentation tools:

- [PinConnect](https://github.com/xbst/PinConnect): turns a photo of a circuit board into an interactive pinout.
- [3DStep](https://github.com/xbst/3DStep): turns a CAD assembly into step-by-step interactive 3D assembly instructions.
- [WebFlash](https://github.com/xbst/webflash): configures, builds and flashes Klipper, Kalico and Katapult firmware from a web browser, and turns a board TOML into an embeddable flashing card.
- [md-iframe](https://github.com/xbst/md-iframe): a Python-Markdown extension that embeds pages like those in MkDocs and Zensical sites.

The site is built with [Zensical](https://zensical.org) and deployed to GitHub Pages by [`.github/workflows/ci.yml`](.github/workflows/ci.yml) on every push to `master`. Its live examples are generated from the TOMLs in [`docs/pinouts/`](docs/pinouts/), [`docs/3d/`](docs/3d/) and [`docs/firmware/`](docs/firmware/) during that build.

## Build it locally

```bash
python -m venv venv
```

Activate it (`.\venv\Scripts\activate` in PowerShell, `source venv/bin/activate` elsewhere), then:

```bash
pip install zensical "git+https://github.com/xbst/PinConnect.git@master" "git+https://github.com/xbst/3DStep.git@master" "git+https://github.com/xbst/webflash.git@master" "git+https://github.com/xbst/md-iframe.git@master"
```

Generate the live examples, then serve the site:

**PowerShell**

```powershell
Get-ChildItem docs/pinouts/*/*.toml | ForEach-Object { pinconnect $_.FullName -i }
Get-ChildItem docs/3d/*/*.toml | ForEach-Object { 3dstep $_.FullName }
Get-ChildItem docs/firmware/*/*.toml | ForEach-Object { webflash $_.FullName -i }
zensical serve
```

**Linux / macOS**

```bash
for toml in docs/pinouts/*/*.toml; do pinconnect "$toml" -i; done
for toml in docs/3d/*/*.toml; do 3dstep "$toml"; done
for toml in docs/firmware/*/*.toml; do webflash "$toml" -i; done
zensical serve
```

`zensical build --clean` builds the site into `site/` as CI does.

## Layout

- `docs/` — the pages. `pinconnect/`, `3dstep/`, `webflash/`, `md-iframe/` and `guides/` hold each tool's docs and the shared topics; `assets/pinconnect/`, `assets/3dstep/` and `assets/webflash/` hold the generated doc images.
- `docs/pinouts/` — the sources of the PinConnect live examples, one folder per board. The generated `*.pinout.html` files are git-ignored.
- `docs/3d/` — the sources of the 3DStep live examples, one folder per assembly with its TOMLs and GLB models. The generated `*.3dstep.html` files are git-ignored.
- `docs/firmware/` — the sources of the WebFlash live examples, one folder per board TOML with the files it names. The generated `*.webflash.html` files are git-ignored. Their cards load WebFlash's runtime from <https://webflash.isiks.tech>, so they run what WebFlash's `master` deploys there; without JavaScript, or when it does not answer, they show their static fallback.
- `tools/` — the generators for the doc images; see [`tools/README.md`](tools/README.md).
- `layouts/` — the social card layout.

## License

GPL-3.0, like the tools it documents. See [LICENSE](LICENSE).
