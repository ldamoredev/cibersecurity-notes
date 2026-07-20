# Atlas Security Range

The Atlas Security Range is a local-only, deterministic environment that joins
application behavior to evidence and remediation. It does not use real
credentials, personal data, public IP exposure, or paid cloud accounts.

| Milestone | Outcome |
| --- | --- |
| v0 | Asset map, data-flow diagram, trust-boundary threat model |
| v1 | Deliberately vulnerable local web fixture and regression tests |
| v2 | API, identity, tenant-boundary and audit-event fixture |
| v3 | Host, network, secrets and audit-log fixture |
| v4 | Container, CI and supply-chain controls |
| v5 | Authorized attack-path validation against fixtures |
| v6 | Telemetry normalization and detection rules |
| v7 | Hunting and investigation exercises |
| v8 | Containment, recovery and forensic tabletop |
| v9 | Safe binary/malware-investigation fixtures |
| v10 | AI tool and agent-boundary exercises |
| v11 | End-to-end purple-team exercise with remediation verification |

The first implementation is planned, not implied by this roadmap. Each future
milestone must remain reproducible locally and document its safety boundary.
