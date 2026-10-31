# doctools-docs

The source of **<https://doctools.isiks.tech>**, the documentation site for Isik's Tech's open-source documentation tools:

- [PinConnect](https://github.com/xbst/PinConnect): turns a photo of a circuit board into an interactive pinout.
- [md-iframe](https://github.com/xbst/md-iframe): a Python-Markdown extension that embeds pages like those in MkDocs and Zensical sites.

The site is built with [Zensical](https://zensical.org) and deployed to GitHub Pages by [`.github/workflows/ci.yml`](.github/workflows/ci.yml) on every push to `master`. Its live examples are generated from the TOMLs in [`docs/pinouts/`](docs/pinouts/) during that build.

## Build it locally

```bash
python -m venv venv
```

Activate it (`.\venv\Scripts\activate` in PowerShell, `source venv/bin/activate` elsewhere), then:

```bash
pip install zensical "git+https://github.com/xbst/PinConnect.git@master" "git+https://github.com/xbst/md-iframe.git@master"
```

Generate the live examples, then serve the site:

**PowerShell**

```powershell
Get-ChildItem docs/pinouts/*/*.toml | ForEach-Object { pinconnect $_.FullName -i }
zensical serve
```

**Linux / macOS**

```bash
for toml in docs/pinouts/*/*.toml; do pinconnect "$toml" -i; done
zensical serve
```

`zensical build --clean` builds the site into `site/` as CI does.

## Layout

- `docs/` — the pages. `pinconnect/`, `md-iframe/` and `guides/` hold each tool's docs and the shared topics; `assets/pinconnect/` holds the generated doc images.
- `docs/pinouts/` — the sources of the live examples, one folder per board. The generated `*.pinout.html` files are git-ignored.
- `tools/` — the generators for the doc images; see [`tools/README.md`](tools/README.md).
- `layouts/` — the social card layout.

## License

GPL-3.0, like the tools it documents. See [LICENSE](LICENSE).
