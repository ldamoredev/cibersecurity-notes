# Cybersecurity Atlas

> Understand the system. Break the assumption. Detect the evidence.

Cybersecurity Atlas is a systems-first reference for how assets, trust
boundaries, vulnerabilities, adversary behavior, telemetry, detection, and
response fit together. It is not a tool list and it does not authorize testing
systems that are not yours.

The public product name is **Cybersecurity Atlas**. The historical repository
name and GitHub Pages URL stay unchanged for compatibility.

## Architecture

- `content/en/cybersecurity/` — canonical public English Markdown.
- `content/es/cybersecurity/` — Spanish overlay; missing pages visibly fall
  back to English.
- `static/` — checked-in brand and site assets.
- `site/` — generated static output; never edit it as canonical content.
- `scripts/` — audit and structural validation.

The original private Obsidian vault is not required. Because it was unavailable
for this migration, the already published English HTML snapshot was recovered
into `content/en` and explicitly marked for editorial review. No private notes
were copied.

## Build locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install markdown pyyaml pygments
.venv/bin/python scripts/validate_content.py
.venv/bin/python build.py
```

Serve `site/` with `python3 -m http.server --directory site 8000` and visit
`http://127.0.0.1:8000`.

## Editorial and safety rules

Read [CONTENT-PLAN.md](CONTENT-PLAN.md), [SOURCES.md](SOURCES.md),
[SAFETY.md](SAFETY.md), [LABS-ROADMAP.md](LABS-ROADMAP.md), and
[MIGRATION-MAP.md](MIGRATION-MAP.md) before adding content. Labs are local,
authorized, deterministic, and paired with telemetry, a fix, and a regression
test.

## Deployment

GitHub Actions installs the renderer dependencies, validates public content,
builds `site/`, and deploys that generated artifact to GitHub Pages.
