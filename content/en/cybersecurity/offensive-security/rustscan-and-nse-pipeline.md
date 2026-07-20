---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# RustScan and NSE Pipeline

## Definition

The RustScan + NSE pipeline is a two-stage workflow in which RustScan performs fast asynchronous port discovery on a target and pipes the discovered port list directly into Nmap, which then drives the Nmap Scripting Engine (NSE) for service detection, version probing, and category-scoped vulnerability checks.

## Why it matters

Running `nmap -A -p- target` against a single host can take 10–30 minutes — and most of that time is spent on ports that turned out to be closed. Splitting the work into "discover ports fast → enumerate ports deeply" cuts a single-host full-range scan from minutes to seconds without losing any of Nmap's enumeration power, because the deep stage runs only on the open ports.

The senior framing is that this is *the same two-phase pattern as Masscan + Nmap*, just sized down: RustScan replaces the bulk-discovery layer for single hosts and small subnets, while Masscan owns the same role for AS-scale work. Understanding NSE script categories then determines whether the second phase is safe, useful, or accidentally noisy/destructive.

## How it works

The pipeline is **3 stages**:

1. **Discovery (RustScan).** Async Tokio runtime opens up to `--ulimit` concurrent half-open sockets, sweeps the configured port set, and emits an open-port list. Adaptive learning adjusts batch size based on early response patterns.
2. **Handoff.** Everything after `--` on the RustScan command line is passed verbatim to Nmap. RustScan invokes Nmap with `-p <discovered_ports>` and the user's flags.
3. **Enumeration (Nmap + NSE).** Nmap runs version detection, OS fingerprinting, and any selected NSE scripts on the open ports only.

Example:

```
rustscan -a target --ulimit 5000 -- -sV -sC --script "default,safe,vuln"
```

Interpretation:
- `--ulimit 5000` raises the open-file-descriptor limit so 5000 ports can be probed concurrently.
- Everything after `--` is Nmap's: `-sV` (version), `-sC` (default NSE), `--script "default,safe,vuln"` (category Boolean).
- RustScan exec()s Nmap with `-p <ports it found>` automatically. Nmap then ignores all the closed ports RustScan already ruled out.

The bug RustScan is solving is *not* in Nmap; it is in *how Nmap is typically run* (`-p-` against a full host where 65,500 ports were always going to be closed). The pipeline is an optimization, not a replacement.

NSE script categories are the **second** part of the senior story:

- `auth`, `broadcast`, `brute`, `default`, `discovery`, `dos`, `exploit`, `external`, `fuzzer`, `intrusive`, `malware`, `safe`, `version`, `vuln`.
- Safe engagement default: `--script "default,safe"` plus selectively `discovery` and `version`.
- Add `vuln` only with explicit authorization.
- `intrusive`, `exploit`, `brute`, `dos` require explicit consent and a documented blast-radius assessment.

## Techniques / patterns

- **Master the `--` divider.** Everything after `--` is Nmap. If you can't articulate what `-A -sC --script vuln` does at the Nmap level, RustScan is hiding bugs from you, not saving you time.
- **`--ulimit` ≥ batch size, always.** Default failure mode: RustScan throttles to ulimit and silently reports false `filtered`. `ulimit -n` in the shell and `--ulimit` on the CLI must agree.
- **Use `--scripts None`** when you want only the port list (e.g., feeding into a custom pipeline).
- **Boolean script selection** beats long script lists: `--script "(default or safe) and not (brute or dos)"`.
- **Per-port NSE selectivity.** `--script "http-*" -p 80,443` runs HTTP-only scripts; avoid pulling SMB scripts at HTTP ports.
- **Script arguments** are mandatory for `vuln` checks that need credentials or paths: `--script-args 'http.useragent="custom",userdb=users.txt'`.
- **NSE script update** before any serious engagement: `nmap --script-updatedb`.
- **Stdin chaining** for pipelines: `subfinder -d target.com | dnsx -a -resp-only | rustscan -a - -- -sV -sC`.

## Variants and bypasses

### 1. Single-host deep scan

`rustscan -a host -r 1-65535 --ulimit 65535 -- -A -sC --script vuln`. The original use case — full port range, full enumeration, in roughly the time Nmap version detection alone would have taken.

### 2. Subnet sweep with selective NSE

`rustscan -a 10.0.0.0/24 --ulimit 5000 -- -sV --script "(default or safe) and not (brute or intrusive)"`. Subnet-scale discovery with conservative NSE.

### 3. Port-list-only mode

`rustscan -a host --scripts None -g`. Greppable port list, no Nmap. For custom pipelines (Nuclei, custom scanners) that don't want Nmap's overhead.

### 4. HTTP-focused enumeration

`rustscan -a host -p 80,443,8080,8443 -- -sV --script "http-title,http-headers,http-methods,http-enum,http-server-header"`. Targeted HTTP NSE without pulling unrelated script categories.

### 5. Authenticated vuln category

`rustscan -a host -- -sV --script vuln --script-args "creds.global=user:pass"`. NSE `vuln` scripts that check authenticated-only conditions. Requires explicit engagement scope authorizing credentials.

### 6. Containerized scan

`docker run --rm rustscan/rustscan:latest -a target -- -sV -sC`. The official deployment — avoids host ulimit fights, reproducible across operators.

## Impact

- **10–100× wall-clock reduction** vs. naive `nmap -p- -A`.
- **Operational risk if NSE category is wrong.** `--script "default"` includes some scripts that send authentication attempts (`http-auth-finder`, `pop3-brute` is not default but easy to add) — review the category contents before assuming "default = safe".
- **NSE `vuln` false positives.** Many `vuln` scripts check banner versions and miss patches — every alert requires manual validation before reporting.
- **`exploit` and `dos` categories can crash services.** They are excluded from `default` for a reason; opting in needs change-management approval in any production-touching engagement.
- **Detection footprint.** RustScan + NSE is louder than Nmap alone — same per-IP fingerprint plus NSE's script-specific probes are easily clustered by behavioral SIEM rules.

## Detection and defense

1.
**NSE-aware IDS rules.**
   Snort/Suricata signatures for the more-noisy NSE scripts (`http-enum`, `smb-vuln-*`, `ssl-enum-ciphers` against a closed cluster) are publicly available and tuned. Defenders should subscribe.

2.
**Per-port deep-inspection rate limits.**
   The RustScan handoff means Nmap will hit a small port set with many NSE probes in quick succession. Per-port-per-source rate limits at the WAF/IDS catch this distinctly.

3.
**Version banner shaping.**
   Many NSE `vuln` scripts decide on version strings. Defenders that strip or randomize version banners reduce false-positive surface in engagements *and* reduce true-positive value for attackers — both reasons to do it.

4.
**Honeypots that respond to `http-enum`.**
   A path table that returns 200 to every directory NSE probes makes the script's output meaningless without affecting real users. Asymmetric defense.

### What does not work as a primary defense

- **Blocking RustScan's source IP** — same trap as Masscan: it finishes its job in seconds.
- **Disabling specific Nmap probes** — Nmap controls its probe library, not the target.
- **Hoping `--script vuln` reports are accurate** — most are version-string heuristics. Defenders should not treat an absence of NSE-`vuln` alerts as evidence of safety.

## Practical labs

```
# Lab 1 — baseline pipeline against an authorized lab host.
rustscan -a LAB --ulimit 5000 -- -sV -sC --script "default,safe"
# Time it. Compare to `nmap -p- -sV -sC LAB`.
# Expect 5–20× wall-clock reduction.
```

```
# Lab 2 — ulimit mismatch failure mode.
ulimit -n 1024
rustscan -a LAB -b 5000 -- -sV 2>&1 | grep -i ulimit
# Reproduces the "Too many open files" error. The fix is `--ulimit 65535` (and matching shell ulimit).
```

```
# Lab 3 — NSE category Boolean.
nmap --script "(default or vuln) and not (intrusive or dos)" --script-help | head -40
nmap -sV --script "(default or vuln) and not (intrusive or dos)" -p 22,80,443 LAB
# Inspect which scripts ran. Match the category list against the engagement scope.
```

```
# Lab 4 — pipeline from subdomain enum.
subfinder -d target.tld -silent |
  dnsx -a -resp-only -silent |
  rustscan -a - --ulimit 5000 -- -sV --script "default,safe"
# A single chain that goes from a domain to enumerated services.
# Only run against authorized scope.
```

```
# Lab 5 — port-list-only mode for custom downstream.
rustscan -a LAB --scripts None -g
# Output is one line per host: "10.0.0.5 -> [22,80,443]".
# Pipe to Nuclei, gowitness, ffuf, or custom tooling instead of Nmap.
```

```
# Lab 6 — NSE update and script audit.
sudo nmap --script-updatedb
locate nse_main.lua  # find script path
ls $(nmap --script-help default 2>/dev/null | awk '/^Categories:/{exit} {print $1}' | head -5)
# Always know what `default` contains before claiming "I only ran safe scripts".
```

## Practical examples

- **Bug-bounty single-target deep dive.** RustScan + NSE against an in-scope host completes full-range version detection in 30–60 seconds instead of 15–30 minutes — letting an operator review 10× more targets in a session.
- **CI-driven external attack surface.** Nightly RustScan + NSE `default,safe` against a list of owned subdomains, with results diffed against the previous night. New ports/services or version changes trigger an alert.
- **Internal red-team pivot.** From a foothold, `rustscan -a internal-subnet/24 --ulimit 5000 -- -sV --script "default,safe and not brute"` finds high-value services (Jenkins, GitLab, internal Confluence) within minutes.
- **Cloud workload audit.** From a controlled scanner inside a VPC, RustScan + NSE validates that intended security-group exposure matches actual reachability for every workload.
- **Pre-engagement smoke test.** Before kicking off the real engagement, a `--script default,safe` pass confirms tooling works end-to-end and produces a baseline diff target.

## Related notes

- [[nmap-scanning|Nmap Scanning]]
- [[service-enumeration|Service Enumeration]]
- [[ports-and-services|Ports and Services]]
- [[host-and-port-discovery|Host and Port Discovery]]
- [[service-validation|Service Validation]]
- [[active-recon|Active Recon]]
- [[enumeration|Enumeration]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]
- [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]]
- [[nmap-timing-and-evasion]]
- [[packet-fragmentation-and-decoy-scans]]
- [[masscan-internet-scale-scanning]]

### Suggested future atomic notes

- [[nse-vuln-category-audit]]
- writing-custom-nse-scripts
- naabu-vs-rustscan
- scan-pipeline-orchestration

## References

- **Official Tool Docs:** RustScan repository and docs — https://github.com/RustScan/RustScan
- **Official Tool Docs:** Nmap Scripting Engine — https://nmap.org/book/nse.html
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 103 — Host and Port Discovery — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
