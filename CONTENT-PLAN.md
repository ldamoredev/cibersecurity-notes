# Cybersecurity Atlas content plan

English Markdown in `content/en/cybersecurity/` is canonical. Spanish Markdown
in `content/es/cybersecurity/` is an overlay; missing overlays deliberately
fall back to English and are counted as such. `site/` is generated output.

## Target taxonomy

1. Orientation and security foundations
2. Systems and trust: cryptography, networking, endpoints, identity
3. Product security: web, APIs, secure design, supply chain, cloud, containers, mobile
4. Adversary tradecraft: exposure, authorized recon, privilege paths, research, reversing, wireless
5. Detection and response: telemetry, hunting, forensics, operations and resilience
6. Emerging and human systems: privacy/OPSEC and AI/agent security
7. Always active: local labs and playbooks

The legacy public slugs remain in place for compatibility. The migration map
records the target grouping; a branch only moves once its index, redirects,
wikilinks, Spanish overlay and source coverage can move together.

## Editorial states

`concept`, `mechanism`, `attack`, `detection`, `lab`, `playbook`, `incident`,
and `standard-guide` are supported kinds. Levels are `beginner`,
`intermediate`, and `advanced`; statuses are `current`, `review-needed`,
`outdated`, `planned`, and `experimental`.
