# Cybersecurity Atlas audit

## Executive summary

The original build depended on an unavailable private vault and deployed a prebuilt site. The public English snapshot has been recovered into `content/en`; this makes builds reproducible, while its recovered notes remain explicitly review-needed. Spanish overlays are now in `content/es`. No private source was imported.

## Real metrics

- Canonical English notes: 295
- Spanish overlays: 289 (98.0% of English paths)
- Branches: 18
- Playbooks: 18
- Recovered snapshot notes requiring editorial review: 233
- Score distribution (heuristic, 0–4): {0: 1, 1: 59, 2: 173, 3: 61, 4: 1}

The score is an audit triage signal, not a claim of technical correctness. It is based on visible system-model, attack/defense, evidence, lab, and source markers. Run this script after meaningful editorial changes.

## Branch audit

| Current slug | Notes | Recommended action | Target grouping |
| --- | ---: | --- | --- |
| `api-security` | 15 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `attack-surface-mapping` | 11 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `binary-exploitation` | 8 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `cloud-security` | 11 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `cryptography` | 15 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `detection-engineering` | 15 | KEEP_AND_DEEPEN | Detection and response |
| `devsecops` | 13 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `foundations` | 10 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `identity-and-active-directory` | 13 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `linux-privilege-escalation` | 10 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `networking` | 24 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `offensive-security` | 21 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `osint` | 11 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `privacy-anonymity-opsec` | 33 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `root` | 25 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `security-playbooks` | 18 | KEEP_AND_DEEPEN | Detection and response |
| `web-security` | 31 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |
| `wireless-security` | 11 | KEEP_AND_DEEPEN | See CONTENT-PLAN.md |

## Note audit

| Current path | Title | Branch | Depth signal | Recommended action |
| --- | --- | --- | --- | --- |
| `cybersecurity/api-security/api-auth-flaws.md` | API Authentication Flaws | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/api-inventory-management.md` | API Inventory Management | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/api-rate-limiting.md` | API Rate Limiting | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/api-security-top-10.md` | API Security Top 10 | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/authorization.md` | Authorization | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/broken-authentication.md` | Broken Authentication | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/broken-function-level-authorization.md` | Broken Function Level Authorization | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/broken-object-level-authorization.md` | Broken Object Level Authorization | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/broken-object-property-level-authorization.md` | Broken Object Property Level Authorization | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/excessive-data-exposure.md` | Excessive Data Exposure | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/index.md` | API Security Index | 15 | 1/4 | DEEPEN |
| `cybersecurity/api-security/jwt-attacks.md` | JWT Attacks | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/mass-assignment.md` | Mass Assignment | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/polymorphic-deserialization.md` | Polymorphic Deserialization | 15 | 2/4 | DEEPEN |
| `cybersecurity/api-security/token-lifecycle.md` | Token Lifecycle | 15 | 2/4 | DEEPEN |
| `cybersecurity/atlas-security-range.md` | Atlas Security Range | root | 2/4 | CANONICAL |
| `cybersecurity/attack-surface-mapping/admin-interface-discovery.md` | Admin Interface Discovery | 11 | 2/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/attack-surface-mapping.md` | Attack Surface Mapping | 11 | 2/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/deprecated-api-versions.md` | Deprecated API Versions | 11 | 2/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/endpoint-discovery.md` | Endpoint Discovery | 11 | 3/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/exposed-service-triage.md` | Exposed Service Triage | 11 | 2/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/exposed-storage.md` | Exposed Storage | 11 | 2/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/external-attack-surface.md` | External Attack Surface | 11 | 3/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/index.md` | Attack Surface Mapping Index | 11 | 1/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/internal-attack-surface.md` | Internal Attack Surface | 11 | 3/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/subdomain-takeover.md` | Subdomain Takeover | 11 | 3/4 | DEEPEN |
| `cybersecurity/attack-surface-mapping/third-party-exposure.md` | Third-Party Exposure | 11 | 2/4 | DEEPEN |
| `cybersecurity/binary-exploitation/exploit-mitigations.md` | Exploit Mitigations | 8 | 2/4 | DEEPEN |
| `cybersecurity/binary-exploitation/format-string-vulnerabilities.md` | Format String Vulnerabilities | 8 | 2/4 | DEEPEN |
| `cybersecurity/binary-exploitation/heap-buffer-overflow-and-allocator-exploitation.md` | Heap Buffer Overflow and Allocator Exploitation | 8 | 2/4 | DEEPEN |
| `cybersecurity/binary-exploitation/index.md` | Binary Exploitation Index | 8 | 2/4 | DEEPEN |
| `cybersecurity/binary-exploitation/memory-corruption.md` | Memory Corruption | 8 | 2/4 | DEEPEN |
| `cybersecurity/binary-exploitation/rop-and-ret2libc.md` | ROP and ret2libc | 8 | 2/4 | DEEPEN |
| `cybersecurity/binary-exploitation/stack-buffer-overflow.md` | Stack Buffer Overflow | 8 | 2/4 | DEEPEN |
| `cybersecurity/binary-exploitation/use-after-free-and-dangling-pointers.md` | Use-After-Free and Dangling Pointers | 8 | 2/4 | DEEPEN |
| `cybersecurity/cloud-security/cloud-dns-and-certbot.md` | Cloud DNS and Certbot | 11 | 2/4 | DEEPEN |
| `cybersecurity/cloud-security/cloud-iam-boundaries.md` | Cloud IAM Boundaries | 11 | 2/4 | DEEPEN |
| `cybersecurity/cloud-security/cloud-lab-infrastructure.md` | Cloud Lab Infrastructure | 11 | 2/4 | DEEPEN |
| `cybersecurity/cloud-security/cloud-logging-and-detection.md` | Cloud Logging and Detection | 11 | 3/4 | DEEPEN |
| `cybersecurity/cloud-security/cloud-metadata-security.md` | Cloud Metadata Security | 11 | 2/4 | DEEPEN |
| `cybersecurity/cloud-security/cloud-network-boundaries.md` | Cloud Network Boundaries | 11 | 2/4 | DEEPEN |
| `cybersecurity/cloud-security/cloud-secrets-management.md` | Cloud Secrets Management | 11 | 2/4 | DEEPEN |
| `cybersecurity/cloud-security/cloud-security-basics.md` | Cloud Security Basics | 11 | 3/4 | DEEPEN |
| `cybersecurity/cloud-security/index.md` | Cloud Security Index | 11 | 2/4 | DEEPEN |
| `cybersecurity/cloud-security/public-cloud-storage-exposure.md` | Public Cloud Storage Exposure | 11 | 3/4 | DEEPEN |
| `cybersecurity/cloud-security/ssh-access-to-cloud-hosts.md` | SSH Access to Cloud Hosts | 11 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/aead-and-nonce-misuse.md` | AEAD and Nonce Misuse | 15 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/asymmetric-encryption-and-key-exchange.md` | Asymmetric Encryption and Key Exchange | 15 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/certificate-validation-and-pinning.md` | Certificate Validation and Pinning | 15 | 3/4 | DEEPEN |
| `cybersecurity/cryptography/digital-signatures.md` | Digital Signatures | 15 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/hashing-vs-encryption-vs-signing.md` | Hashing vs Encryption vs Signing | 15 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/index.md` | Cryptography Index | 15 | 0/4 | DEEPEN |
| `cybersecurity/cryptography/jwt-cryptographic-correctness.md` | JWT Cryptographic Correctness | 15 | 3/4 | DEEPEN |
| `cybersecurity/cryptography/kdf-and-key-stretching.md` | KDF and Key Stretching | 15 | 1/4 | DEEPEN |
| `cybersecurity/cryptography/mac-and-hmac.md` | MAC and HMAC | 15 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/password-hashing.md` | Password Hashing | 15 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/post-quantum-awareness.md` | Post-Quantum Awareness | 15 | 1/4 | DEEPEN |
| `cybersecurity/cryptography/random-and-csprng-pitfalls.md` | Random and CSPRNG Pitfalls | 15 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/roll-your-own-crypto-failures.md` | Roll Your Own Crypto Failures | 15 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/symmetric-encryption-modes.md` | Symmetric Encryption Modes | 15 | 2/4 | DEEPEN |
| `cybersecurity/cryptography/tls-handshake-and-pki.md` | TLS Handshake and PKI | 15 | 2/4 | DEEPEN |
| `cybersecurity/detection-engineering/attack-path-correlation-and-kill-chain-observability.md` | Attack Path Correlation and Kill Chain Observability | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/behavioral-detection-vs-signature-detection.md` | Behavioral Detection vs Signature Detection | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/detection-evasion-myths-and-modern-limitations.md` | Detection Evasion Myths and Modern Limitations | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/edr-network-observability-and-process-correlation.md` | EDR Network Observability and Process Correlation | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/encrypted-traffic-analysis-and-metadata-leakage.md` | Encrypted Traffic Analysis and Metadata Leakage | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/false-positives-false-negatives-and-detection-tradeoffs.md` | False Positives, False Negatives, and Detection Tradeoffs | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/from-local-exploit-to-detection.md` | From local exploit to detection | 15 | 2/4 | CANONICAL |
| `cybersecurity/detection-engineering/ids-ips-and-behavioral-detection-pipelines.md` | IDS/IPS and Behavioral Detection Pipelines | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/index.md` | Detection Engineering | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/network-security-monitoring-discipline.md` | Network Security Monitoring Discipline | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/network-telemetry-sources-and-visibility.md` | Network Telemetry Sources and Visibility | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/scan-anomaly-detection-and-fingerprint-analysis.md` | Scan Anomaly Detection and Fingerprint Analysis | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/telemetry-normalization-correlation-and-enrichment.md` | Telemetry Normalization, Correlation, and Enrichment | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/windows-event-logs.md` | Windows Event Logs | 15 | 3/4 | DEEPEN |
| `cybersecurity/detection-engineering/zeek-suricata-and-netflow-analysis.md` | Zeek, Suricata, and NetFlow Analysis | 15 | 3/4 | DEEPEN |
| `cybersecurity/devsecops/artifact-integrity.md` | Artifact Integrity | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/asvs-as-dev-process-input.md` | ASVS as Dev Process Input | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/branch-protection-and-release-controls.md` | Branch Protection and Release Controls | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/ci-cd-hardening.md` | CI/CD Hardening | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/container-security.md` | Container Security | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/dependency-risk.md` | Dependency Risk | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/image-scanning.md` | Image Scanning | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/index.md` | DevSecOps Index | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/nist-ssdf.md` | NIST SSDF | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/sbom-and-provenance.md` | SBOM and Provenance | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/secrets-management.md` | Secrets Management | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/secure-by-design.md` | Secure by Design | 13 | 1/4 | DEEPEN |
| `cybersecurity/devsecops/supply-chain-security.md` | Supply Chain Security | 13 | 1/4 | DEEPEN |
| `cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool.md` | Attacker-Defender Duality as a Learning Tool | 10 | 2/4 | DEEPEN |
| `cybersecurity/foundations/certifications-as-validation-signals.md` | Certifications as Validation Signals | 10 | 2/4 | DEEPEN |
| `cybersecurity/foundations/cia-triad-and-what-it-actually-decides.md` | CIA Triad — What It Actually Decides | 10 | 2/4 | DEEPEN |
| `cybersecurity/foundations/index.md` | Foundations Index — Phase 0 | 10 | 2/4 | DEEPEN |
| `cybersecurity/foundations/job-context-specialization.md` | Job Context Specialization | 10 | 2/4 | DEEPEN |
| `cybersecurity/foundations/minimum-viable-cybersecurity-literacy.md` | Minimum Viable Cybersecurity Literacy | 10 | 2/4 | DEEPEN |
| `cybersecurity/foundations/security-boundaries-and-trust-assumptions.md` | Security boundaries and trust assumptions | 10 | 1/4 | CANONICAL |
| `cybersecurity/foundations/threat-modeling-from-asset-to-abuse-case.md` | Threat modeling from asset to abuse case | 10 | 1/4 | CANONICAL |
| `cybersecurity/foundations/threat-modeling-quickstart.md` | Threat Modeling Quickstart | 10 | 2/4 | DEEPEN |
| `cybersecurity/foundations/what-is-cybersecurity-and-why-it-is-not-a-tool-list.md` | What Is Cybersecurity, and Why It Is Not a Tool List | 10 | 3/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/as-rep-roasting.md` | AS-REP Roasting | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/bloodhound-attack-path-analysis.md` | BloodHound and Attack Path Analysis | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/dcsync-and-ntdsdit-extraction.md` | DCSync and ntds.dit Extraction | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/gmsa-and-modern-service-account-hardening.md` | gMSA and Modern Service Account Hardening | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/golden-ticket-and-krbtgt-compromise.md` | Golden Ticket and KRBTGT Compromise | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/identity-attack-paths-across-idps.md` | Identity Attack Paths Across IdPs | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/index.md` | Identity and Active Directory Index | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/kerberoasting.md` | Kerberoasting | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/krbtgt-rotation-and-tier-zero-recovery.md` | KRBTGT Rotation and Tier Zero Recovery | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/pass-the-hash-and-ntlm-credential-reuse.md` | Pass-the-Hash and NTLM Credential Reuse | 13 | 3/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/silver-ticket-and-service-account-persistence.md` | Silver Ticket and Service Account Persistence | 13 | 3/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/tier-zero-administration-and-paw.md` | Tier 0 Administration and Privileged Access Workstations | 13 | 2/4 | DEEPEN |
| `cybersecurity/identity-and-active-directory/windows-privilege-escalation.md` | Windows Privilege Escalation | 13 | 3/4 | DEEPEN |
| `cybersecurity/index.md` | Cybersecurity Index | root | 3/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/cron-and-timer-abuse.md` | Cron and Timer Abuse | 10 | 2/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/index.md` | Linux Privilege Escalation Index | 10 | 1/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/kernel-exploit-triage.md` | Kernel Exploit Triage | 10 | 2/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/linpeas-workflow.md` | LinPEAS Workflow | 10 | 2/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/linux-capabilities.md` | Linux Capabilities | 10 | 1/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/linux-enumeration.md` | Linux Enumeration | 10 | 2/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/linux-privilege-escalation.md` | Linux Privilege Escalation | 10 | 2/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/path-hijacking.md` | PATH Hijacking | 10 | 2/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/sudo-misconfigurations.md` | Sudo Misconfigurations | 10 | 2/4 | DEEPEN |
| `cybersecurity/linux-privilege-escalation/suid-sgid-misconfigurations.md` | SUID and SGID Misconfigurations | 10 | 1/4 | DEEPEN |
| `cybersecurity/must-know-30.md` | Must-Know 30 — The Minimum Viable Security Literacy | root | 2/4 | DEEPEN |
| `cybersecurity/networking/caching-and-security.md` | Caching and Security | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/client-ip-trust.md` | Client IP Trust | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/cookies-and-sessions.md` | Cookies and Sessions | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/dangling-dns-records.md` | Dangling DNS Records | 24 | 3/4 | DEEPEN |
| `cybersecurity/networking/dns-resolution.md` | DNS Resolution | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/dns-security.md` | DNS Security | 24 | 3/4 | DEEPEN |
| `cybersecurity/networking/firewalls-and-network-boundaries.md` | Firewalls and Network Boundaries | 24 | 4/4 | DEEPEN |
| `cybersecurity/networking/from-browser-request-to-server-evidence.md` | From browser request to server evidence | 24 | 2/4 | CANONICAL |
| `cybersecurity/networking/header-trust-in-node-express.md` | Header Trust in Node Express | 24 | 3/4 | DEEPEN |
| `cybersecurity/networking/http-headers.md` | HTTP Headers | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/http-messages.md` | HTTP Messages | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/http-overview.md` | HTTP Overview | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/index.md` | Networking Index | 24 | 3/4 | DEEPEN |
| `cybersecurity/networking/load-balancers.md` | Load Balancers | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/metadata-endpoints.md` | Cloud Instance Metadata Endpoints | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/nat-and-private-networks.md` | NAT and Private Networks | 24 | 3/4 | DEEPEN |
| `cybersecurity/networking/nmap-scanning.md` | Nmap Scanning | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/packet-analysis.md` | Packet Analysis | 24 | 3/4 | DEEPEN |
| `cybersecurity/networking/ports-and-services.md` | Ports and Services | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/reverse-proxies.md` | Reverse Proxies | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/service-enumeration.md` | Service Enumeration | 24 | 3/4 | DEEPEN |
| `cybersecurity/networking/tcp-ip-basics.md` | TCP/IP Basics | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/tls-https.md` | TLS and HTTPS | 24 | 2/4 | DEEPEN |
| `cybersecurity/networking/wireshark-workflows.md` | Wireshark Workflows | 24 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/active-recon.md` | Active Recon | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/cloaking-and-security-evasion.md` | Cloaking and Security Evasion | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/company-mapping.md` | Company Mapping | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/enumeration.md` | Enumeration | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/host-and-port-discovery.md` | Host and Port Discovery | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/idle-scan-and-ipid-side-channels.md` | Idle Scan and IPID Side Channels | 21 | 3/4 | DEEPEN |
| `cybersecurity/offensive-security/index.md` | Offensive Security / Recon Index | 21 | 3/4 | DEEPEN |
| `cybersecurity/offensive-security/masscan-internet-scale-scanning.md` | Masscan Internet-Scale Scanning | 21 | 1/4 | DEEPEN |
| `cybersecurity/offensive-security/nmap-timing-and-evasion.md` | Nmap Timing and Evasion | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/nse-vuln-category-audit.md` | NSE `vuln` Category Audit | 21 | 3/4 | DEEPEN |
| `cybersecurity/offensive-security/operator-loop.md` | The Operator Loop | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/packet-fragmentation-and-decoy-scans.md` | Packet Fragmentation and Decoy Scans | 21 | 3/4 | DEEPEN |
| `cybersecurity/offensive-security/passive-recon.md` | Passive Recon | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/public-asset-discovery.md` | Public Asset Discovery | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/recon-to-testing-handoff.md` | Recon to Testing Handoff | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/recon.md` | Recon | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/rustscan-and-nse-pipeline.md` | RustScan and NSE Pipeline | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/scope-validation.md` | Scope Validation | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/service-validation.md` | Service Validation | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/subdomain-enumeration.md` | Subdomain Enumeration | 21 | 2/4 | DEEPEN |
| `cybersecurity/offensive-security/tech-stack-fingerprinting.md` | Tech Stack Fingerprinting | 21 | 2/4 | DEEPEN |
| `cybersecurity/osint/breach-and-leak-intelligence.md` | Breach and Leak Intelligence | 11 | 2/4 | DEEPEN |
| `cybersecurity/osint/company-osint.md` | Company OSINT | 11 | 3/4 | DEEPEN |
| `cybersecurity/osint/email-and-phone-osint.md` | Email and Phone OSINT | 11 | 3/4 | DEEPEN |
| `cybersecurity/osint/google-dorking.md` | Google Dorking | 11 | 2/4 | DEEPEN |
| `cybersecurity/osint/image-and-location-osint.md` | Image and Location OSINT | 11 | 3/4 | DEEPEN |
| `cybersecurity/osint/index.md` | OSINT Index | 11 | 1/4 | DEEPEN |
| `cybersecurity/osint/osint-reporting.md` | OSINT Reporting | 11 | 2/4 | DEEPEN |
| `cybersecurity/osint/osint-triage.md` | OSINT Triage | 11 | 3/4 | DEEPEN |
| `cybersecurity/osint/osint.md` | OSINT | 11 | 3/4 | DEEPEN |
| `cybersecurity/osint/search-engine-operators.md` | Search Engine Operators | 11 | 2/4 | DEEPEN |
| `cybersecurity/osint/social-media-osint.md` | Social Media OSINT | 11 | 3/4 | DEEPEN |
| `cybersecurity/phase-1-substrate.md` | Phase 1 — Substrate (How Things Actually Work) | root | 2/4 | DEEPEN |
| `cybersecurity/phase-2-offense-defense.md` | Phase 2 — Offense / Defense (Paired) | root | 2/4 | DEEPEN |
| `cybersecurity/phase-3-operator.md` | Phase 3 — Operator Surface (Concept → Capability) | root | 1/4 | DEEPEN |
| `cybersecurity/phase-4-specialty.md` | Phase 4 — Specialty Tracks (Pick What Your Job Demands) | root | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/account-correlation.md` | Account Correlation | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/anonymity-threat-models.md` | Anonymity Threat Models | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/browser-fingerprinting.md` | Browser Fingerprinting | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/corporate-vpns-vs-consumer-vpns.md` | Corporate VPNs vs Consumer VPNs | 33 | 3/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/deanonymization-failures.md` | Deanonymization Failures | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/end-to-end-encryption.md` | End-to-End Encryption | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/file-metadata-removal.md` | File Metadata Removal | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/index.md` | Privacy, Anonymity & OPSEC Index | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/metadata-and-identity-leakage.md` | Metadata and Identity Leakage | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/opsec-failure-chains.md` | OPSEC Failure Chains | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/pgp-encryption-and-signatures.md` | PGP Encryption and Signatures | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/privacy-vs-anonymity-vs-confidentiality.md` | Privacy vs Anonymity vs Confidentiality | 33 | 3/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/private-email-threat-models.md` | Private Email Threat Models | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/qubes-compartmentalization.md` | Qubes Compartmentalization | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/secure-deletion-and-storage-wiping.md` | Secure Deletion and Storage Wiping | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/secure-file-sharing.md` | Secure File Sharing | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/tails-operational-model.md` | Tails Operational Model | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/temporary-email-risks.md` | Temporary Email Risks | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/tor-and-onion-services.md` | Tor and Onion Services | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/tor-bridges-and-pluggable-transports.md` | Tor Bridges and Pluggable Transports | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/tor-browser-security-settings.md` | Tor Browser Security Settings | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/traffic-correlation.md` | Traffic Correlation | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/vpn-dns-and-ipv6-leaks.md` | VPN DNS and IPv6 Leaks | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/vpn-fingerprinting-limitations.md` | VPN Fingerprinting Limitations | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/vpn-kill-switches.md` | VPN Kill Switches | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/vpn-leakage-risks.md` | VPN Leakage Risks | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/vpn-logging-and-trust.md` | VPN Logging and Trust | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/vpn-protocols.md` | VPN Protocols | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/vpn-threat-models.md` | VPN Threat Models | 33 | 2/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/vpn-vs-tor.md` | VPN vs Tor | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/vpn-with-tor.md` | VPN with Tor | 33 | 1/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/whonix-gateway.md` | Whonix Gateway | 33 | 3/4 | DEEPEN |
| `cybersecurity/privacy-anonymity-opsec/xmpp-and-private-messaging.md` | XMPP and Private Messaging | 33 | 1/4 | DEEPEN |
| `cybersecurity/reference-registry-api-security.md` | Reference Registry — API Security | root | 1/4 | DEEPEN |
| `cybersecurity/reference-registry-attack-surface-mapping.md` | Reference Registry — Attack Surface Mapping | root | 1/4 | DEEPEN |
| `cybersecurity/reference-registry-binary-exploitation.md` | Reference Registry — Binary Exploitation | root | 2/4 | DEEPEN |
| `cybersecurity/reference-registry-cloud-security.md` | Reference Registry — Cloud Security | root | 2/4 | DEEPEN |
| `cybersecurity/reference-registry-cryptography.md` | Reference Registry — Cryptography | root | 1/4 | DEEPEN |
| `cybersecurity/reference-registry-detection-engineering.md` | Reference Registry - Detection Engineering | root | 3/4 | DEEPEN |
| `cybersecurity/reference-registry-devsecops.md` | Reference Registry — DevSecOps | root | 1/4 | DEEPEN |
| `cybersecurity/reference-registry-identity-and-active-directory.md` | Reference Registry — Identity and Active Directory | root | 3/4 | DEEPEN |
| `cybersecurity/reference-registry-linux-privilege-escalation.md` | Reference Registry — Linux Privilege Escalation | root | 2/4 | DEEPEN |
| `cybersecurity/reference-registry-networking.md` | Reference Registry — Networking | root | 2/4 | DEEPEN |
| `cybersecurity/reference-registry-offensive-security.md` | Reference Registry — Offensive Security | root | 1/4 | DEEPEN |
| `cybersecurity/reference-registry-osint.md` | Reference Registry — OSINT | root | 2/4 | DEEPEN |
| `cybersecurity/reference-registry-playbooks.md` | Reference Registry — Playbooks | root | 2/4 | DEEPEN |
| `cybersecurity/reference-registry-privacy-anonymity-opsec.md` | Reference Registry - Privacy, Anonymity & OPSEC | root | 2/4 | DEEPEN |
| `cybersecurity/reference-registry-web-security.md` | Reference Registry — Web Security | root | 2/4 | DEEPEN |
| `cybersecurity/reference-registry-wireless-security.md` | Reference Registry — Wireless Security | root | 1/4 | DEEPEN |
| `cybersecurity/reference-registry.md` | Cybersecurity Reference Registry | root | 2/4 | DEEPEN |
| `cybersecurity/security-playbooks/break-jwt-validation.md` | Break JWT Validation | 18 | 2/4 | DEEPEN |
| `cybersecurity/security-playbooks/detect-bloodhound-collection.md` | Detect BloodHound Collection | 18 | 3/4 | DEEPEN |
| `cybersecurity/security-playbooks/detect-dcsync-and-ntdsdit-access.md` | Detect DCSync and ntds.dit Access | 18 | 3/4 | DEEPEN |
| `cybersecurity/security-playbooks/detect-external-scan-pipeline.md` | Detect External Recon Scan Pipeline | 18 | 3/4 | DEEPEN |
| `cybersecurity/security-playbooks/detect-kerberoasting-and-as-rep-roasting.md` | Detect Kerberoasting and AS-REP Roasting | 18 | 3/4 | DEEPEN |
| `cybersecurity/security-playbooks/exploit-idor.md` | Exploit IDOR | 18 | 1/4 | DEEPEN |
| `cybersecurity/security-playbooks/exploit-sqli.md` | Exploit SQL Injection | 18 | 1/4 | DEEPEN |
| `cybersecurity/security-playbooks/incident-response-from-signal-to-recovery.md` | Incident response from signal to recovery | 18 | 2/4 | CANONICAL |
| `cybersecurity/security-playbooks/index.md` | Security Playbooks Index | 18 | 3/4 | DEEPEN |
| `cybersecurity/security-playbooks/inspect-file-upload-surface.md` | Inspect File Upload Surface | 18 | 1/4 | DEEPEN |
| `cybersecurity/security-playbooks/inspect-session-handling.md` | Inspect Session Handling | 18 | 1/4 | DEEPEN |
| `cybersecurity/security-playbooks/investigate-ssrf.md` | Investigate SSRF | 18 | 2/4 | DEEPEN |
| `cybersecurity/security-playbooks/reverse-proxy-misconfig-checklist.md` | Reverse Proxy Misconfig Checklist | 18 | 2/4 | DEEPEN |
| `cybersecurity/security-playbooks/run-scan-pipeline.md` | Run External Recon Scan Pipeline | 18 | 3/4 | DEEPEN |
| `cybersecurity/security-playbooks/test-client-ip-spoofing.md` | Test Client IP Spoofing | 18 | 2/4 | DEEPEN |
| `cybersecurity/security-playbooks/test-cors-behavior.md` | Test CORS Behavior | 18 | 2/4 | DEEPEN |
| `cybersecurity/security-playbooks/test-path-traversal.md` | Test Path Traversal | 18 | 1/4 | DEEPEN |
| `cybersecurity/security-playbooks/trace-metadata-endpoint-reachability.md` | Trace Metadata Endpoint Reachability | 18 | 3/4 | DEEPEN |
| `cybersecurity/start-here.md` | Start Here — Cybersecurity Atlas Guide | root | 1/4 | DEEPEN |
| `cybersecurity/web-security/auth-flaws.md` | Authentication Flaws | 31 | 1/4 | DEEPEN |
| `cybersecurity/web-security/authentication-authorization-and-object-access.md` | Authentication, authorization and object access | 31 | 1/4 | CANONICAL |
| `cybersecurity/web-security/bot-detection-signals.md` | Bot Detection Signals | 31 | 3/4 | DEEPEN |
| `cybersecurity/web-security/broken-access-control.md` | Broken Access Control | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/browser-security-boundaries.md` | Browser Security Boundaries | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/business-logic-vulnerabilities.md` | Business Logic Vulnerabilities | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/clickjacking.md` | Clickjacking | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/command-injection.md` | Command Injection | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/content-security-policy.md` | Content Security Policy | 31 | 3/4 | DEEPEN |
| `cybersecurity/web-security/cors-misconfiguration.md` | CORS Misconfiguration | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/csrf.md` | Cross-Site Request Forgery (CSRF) | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/deserialization.md` | Insecure Deserialization | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/evilginx-and-reverse-proxy-phishing.md` | Evilginx and Reverse Proxy Phishing | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/file-upload-abuse.md` | File Upload Abuse | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/gadget-chains.md` | Gadget Chains | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/idor.md` | Insecure Direct Object Reference (IDOR) | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/index.md` | Web Security Index | 31 | 1/4 | DEEPEN |
| `cybersecurity/web-security/mfa-phishing-resistance.md` | MFA Phishing Resistance | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/oauth-security.md` | OAuth Security | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/open-redirect.md` | Open Redirect | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/owasp-top-10.md` | OWASP Top 10 | 31 | 1/4 | DEEPEN |
| `cybersecurity/web-security/path-traversal.md` | Path Traversal | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/phar-deserialization.md` | PHAR Deserialization | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/request-smuggling.md` | Request Smuggling | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/same-origin-policy.md` | Same-Origin Policy | 31 | 3/4 | DEEPEN |
| `cybersecurity/web-security/session-management.md` | Session Management | 31 | 1/4 | DEEPEN |
| `cybersecurity/web-security/sql-injection.md` | SQL Injection | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/ssrf.md` | Server-Side Request Forgery (SSRF) | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/web-cache-poisoning.md` | Web Cache Poisoning | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/xss.md` | Cross-Site Scripting (XSS) | 31 | 2/4 | DEEPEN |
| `cybersecurity/web-security/xxe.md` | XXE | 31 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/arp-poisoning.md` | ARP Poisoning | 11 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/bettercap-workflows.md` | Bettercap Workflows | 11 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/evil-twin-access-points.md` | Evil Twin Access Points | 11 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/index.md` | Wireless Security Index | 11 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/mitm-on-local-networks.md` | MITM on Local Networks | 11 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/wep-security.md` | WEP Security | 11 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/wifi-deauthentication.md` | Wi-Fi Deauthentication | 11 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/wifi-monitor-mode.md` | Wi-Fi Monitor Mode | 11 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/wifi-wordlist-attacks.md` | Wi-Fi Wordlist Attacks | 11 | 2/4 | DEEPEN |
| `cybersecurity/wireless-security/wireless-security.md` | Wireless Security | 11 | 3/4 | DEEPEN |
| `cybersecurity/wireless-security/wpa-wpa2-handshakes.md` | WPA/WPA2 Handshakes | 11 | 2/4 | DEEPEN |

## Findings and recommendation

Prioritize the six flagship notes, every branch index, and notes that lack sources, system boundaries, evidence, or stated limits. Preserve public paths until a branch-level redirect and link pass succeeds.
