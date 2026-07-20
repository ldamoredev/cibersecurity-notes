# Migration map

| Old path | Current public URL | Action | New path | Redirect | Reason | Wikilinks |
| --- | --- | --- | --- | --- | --- | --- |
| private Obsidian vault | not public | EXCLUDE | — | no | private source unavailable; never import by default | n/a |
| `site/en/cybersecurity/**` | preserved legacy and `/en/` URLs | RECOVER | `content/en/cybersecurity/**` | existing legacy stubs | public snapshot is the only complete tracked English corpus | resolved during build |
| `translations/es/cybersecurity/**` | `/es/cybersecurity/**` | MOVE | `content/es/cybersecurity/**` | not needed | Spanish overlay becomes public repo content | preserved |
| legacy branches | existing URLs | KEEP_AND_DEEPEN | target taxonomy in `CONTENT-PLAN.md` | required before physical moves | avoid broken external references | update with each move |

The English recovery is intentionally marked `needs-editorial-review`: it is a
faithful public-snapshot migration, not a claim that HTML-to-Markdown recovery
preserved private frontmatter or source history. No private vault material was
imported.
