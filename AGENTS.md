# Working conventions

Keep public content in `content/`; never depend on a local vault or import it
wholesale. Preserve public URLs and use redirects when moving any published
path. Treat generated `site/` as output. Run `scripts/validate_content.py`,
`scripts/audit_content.py`, and `build.py` after structural work. All labs must
be explicitly local-only and safe to reset.
