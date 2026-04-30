# obsidian-site

Static HTML mirror of the mature `cybersecurity/` branches from my
Obsidian vault at `/Users/lautarodamore/obsidian-vault/ldamore/`.

The build intentionally excludes private/project execution notes, templates,
tooling experiments, and future/unpromoted cybersecurity branches.

Plain HTML + CSS + a tiny vanilla-JS search. No framework, no runtime server,
no build toolchain beyond Python.

## Layout

- `build.py` — single-file build script (Python 3 + `markdown`, `pyyaml`, `pygments`).
- `site/` — generated output. Open `site/index.html` directly or serve the folder.
- `.venv/` — local ignored virtualenv for the build dependencies.

## Rebuild

After adding or editing notes in the vault:

```bash
cd ~/obsidian-site
python3 -m venv .venv
.venv/bin/python -m pip install markdown pyyaml pygments
.venv/bin/python build.py
```

The script clears `site/` and regenerates everything. It prints how many notes
it wrote and how many wikilinks were unresolved (those render as red dashed
placeholders, matching Obsidian's "not yet created" behavior).

## Serve locally

```bash
cd ~/obsidian-site/site
python3 -m http.server 8000
# visit http://127.0.0.1:8000
```

Or just open `site/index.html` in a browser — relative paths are used
throughout, so the `file://` scheme works too.

## What it handles

- Folder hierarchy mirrored as a collapsible sidebar.
- Obsidian `[[wikilinks]]`, including `[[folder/note]]`, `[[note|label]]`, and
  `[[note#heading]]`. Same-folder notes win on slug collisions.
- Standard `[text](foo.md)` links rewritten to `.html`.
- YAML frontmatter (tags surface as chips at the top of each note).
- Fenced code blocks with Pygments syntax highlighting.
- Tables, blockquotes, lists, HR, inline code.
- Client-side search across titles + body text (`assets/search.json`).
- Light/dark theme toggle, persisted in `localStorage`.

## Dependencies

Install into the local ignored virtualenv:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install markdown pyyaml pygments
```

## Deploy to GitHub Pages

CI deploys the pre-built `site/` directory — the build runs locally, not in
Actions, so the workflow does not need access to the vault.

Workflow in place: `.github/workflows/deploy.yml`.

Update flow:

```bash
cd ~/obsidian-site
.venv/bin/python build.py
git add -A
git commit -m "update notes"
git push
```

On first push, enable Pages in the repo: **Settings → Pages → Build and
deployment → Source: GitHub Actions**.

## Notes

- `.DS_Store` and other non-`.md` files are ignored.
- Unresolved wikilinks (e.g. `[[clickjacking]]` when no such note exists yet)
  are rendered as dashed red placeholders so they stay visible without
  breaking navigation.
- Slug collisions (same filename in different folders) are resolved by
  preferring a target in the same folder as the source note, then the same
  section. Warnings print during build.
