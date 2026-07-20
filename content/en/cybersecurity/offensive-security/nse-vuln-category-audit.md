---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# NSE `vuln` Category Audit

## Definition

The Nmap Scripting Engine's `vuln` category contains roughly **150 scripts** that claim to detect vulnerabilities. They are not all equal: some are reliable behavioral checks, many are version-string heuristics, and a handful are outright stale (still checking CVEs from 2010 against banner formats nobody emits anymore). Auditing the category — knowing which scripts produce trustworthy signal in 2026, which require manual confirmation, and which to disable outright — is the discipline that turns "I ran `--script vuln` and got 50 alerts" into "I produced 4 validated findings".

## Why it matters

Default operator usage is `nmap -sV --script vuln target`. The output looks impressive — pages of `VULNERABLE:` blocks. Junior operators paste these into reports. Senior operators recognize that **a majority of `vuln` script output is unvalidated heuristic noise**: version-string comparisons against signatures that were valid five years ago, against software that has since been patched in-place by the vendor without bumping the banner string.

The category also matters as a teaching note because it concretizes three transferable senior ideas:

- **A vulnerability is not a finding.** A *vulnerability* is "this software version had a CVE". A *finding* is "I confirmed this instance is exploitable in this environment". NSE `vuln` produces the former; the operator's job is the conversion.
- **Banner-heuristic detection is the lowest tier on Bianco's Pyramid of Pain.** It bypasses trivially via banner shaping — and many production stacks shape banners as standard hardening. The same fact that makes `vuln` results unreliable for attackers is why "remove version banners" is a low-cost defender control.
- **Tool output is one input to reasoning, not the reasoning.** Every NSE `vuln` finding deserves a manual validation step before it becomes report content. The operator who reports raw NSE output produces engagement deliverables that get rejected by anyone with calibration.

## How it works

NSE `vuln` scripts cluster into **4 detection tiers** by reliability, and a senior audit assigns every used script to a tier explicitly:

1.
**Behavioral / probe-based (high reliability).** The script sends a crafted request that *only a vulnerable target responds to* and observes the response. Examples: `smb-vuln-ms17-010` (sends a malformed SMB packet that triggers the EternalBlue code path), `ssl-poodle` (negotiates TLS with `TLS_FALLBACK_SCSV` and observes whether SSLv3 fallback succeeds), `http-shellshock` (sends an HTTP request with a crafted environment-variable payload and checks for exploitation evidence). These produce findings, not heuristics.

2.
**Authenticated / state-aware (high reliability).** The script authenticates to the service and queries actual state. Examples: `smb-os-discovery` paired with `smb-vuln-*` for credentialed enumeration; `mysql-empty-password`. Less common in unauthenticated external scans but high-signal when scope allows.

3.
**Version-banner heuristics (low reliability — the bulk of the category).** The script reads the service's version banner and compares against a CVE table. Examples: most `http-vuln-cve*` scripts, many SSH and SMTP `vuln` scripts. **Failure modes:** (a) banner-shaping defenses produce false negatives, (b) vendor backports patches without bumping the banner string producing false positives, (c) the CVE table baked into the script is from whenever the script was last updated.

4.
**Stale / deprecated (do not trust).** Scripts that check CVEs old enough that any unpatched instance was either patched, decommissioned, or already compromised long ago. Examples: many `http-vuln-cve2010-*`, `http-vuln-cve2011-*`. The category still ships them because removing scripts is rare; the operator's job is to filter them out.

A representative audit workflow:

```
# 1) Enumerate vuln-category scripts on the host.
nmap --script-help "vuln" | grep -E '^[a-z]' | head -40

# 2) Filter by date of last-update if maintained (not all scripts have it).
ls /usr/share/nmap/scripts/ | grep -E 'vuln|cve' | xargs -I{} stat -f "%Sm %N" /usr/share/nmap/scripts/{} 2>/dev/null |
    sort | head -20

# 3) Pick a tighter Boolean than just `vuln`.
nmap -sV --script "vuln and not (http-vuln-cve2010-* or http-vuln-cve2011-*)" target
```

The bug is not "NSE `vuln` is bad"; it is *the category is a heterogeneous bag of detection mechanisms with vastly different reliability, and treating it as one thing produces unreliable engagement output*.

## Techniques / patterns

- **Always pair `--script vuln` with `-sV`.** Many `vuln` scripts gate on version detection. Without `-sV`, scripts skip silently and you miss real findings.
- **Use Boolean expressions to narrow scope.** `--script "vuln and (http-* or ssl-*)"` runs only HTTP and SSL vuln scripts. Quieter, faster, easier to triage. `--script "(default or vuln) and safe and not intrusive"` is the standard "first pass" Boolean.
- **Update NSE before every engagement.** `sudo nmap --script-updatedb`. Scripts and their CVE tables update; running with a 6-month-old script database produces worse signal than necessary.
- **Treat every `VULNERABLE:` block as a hypothesis.** The next operator move is manual verification: run the actual exploit (against authorized lab), check the vendor's CVE page for "are backports common?", check the target's patch posture if engagement scope allows it.
- **Disable scripts that consistently false-positive.** `--script "vuln and not http-cookie-flags and not http-csrf"` for engagements where these scripts have already proven unreliable against the target stack.
- **`--script-args` is mandatory for some scripts.** `smb-vuln-*` accepts `smbport=`, `unsafe=1` (run dangerous probes), credentials. Without args, scripts run in safe mode and may miss findings.
- **Two-pass strategy beats one-pass.** First pass: `--script "vuln" -sV` to enumerate hypotheses. Second pass: manual confirmation tool per hypothesis (e.g., for an `smb-vuln-ms17-010` hit, use Metasploit's verifier module against an authorized lab). The two-pass discipline is what separates findings from noise.

## Variants and bypasses

NSE `vuln` audit splits into **3 usage patterns**, each with different defender-evasion characteristics.

### 1. Mass-discovery first pass

`nmap -sV --script "vuln" -iL hosts.txt -oA vuln-scan`. Loud. Detected by IDS signatures keyed on specific NSE probe patterns (Snort/Suricata community rules ship signatures for many NSE scripts). Use only when authorization explicitly covers active scanning at this depth.

### 2. Targeted scope-narrowed pass

`nmap -sV --script "vuln and (http-* or ssl-*)" -p 80,443,8080,8443 target`. Quieter — fewer scripts, focused on relevant services. Standard engagement pattern.

### 3. Single-script verification pass

`nmap -p 445 --script smb-vuln-ms17-010 --script-args smbport=445 target`. The third step in the validation pipeline — run only the one script that confirms or refutes a specific hypothesis. Minimal telemetry; cleanest signal-to-noise; the right pattern for confirming a single finding before reporting.

## Impact

Ordered by typical real-world severity (of *misuse*, since the technique itself is defensive):

- **Engagement reports rejected by reviewers.** Submitting raw `vuln` script output without validation is a reliable way to have findings downgraded or removed. Bug bounty triagers and pentest reviewers see this pattern constantly.
- **False-positive triage cost on the defender side.** A defender who treats every NSE `vuln` alert as real spends most of their time on hypotheses that don't exist in their environment. Operator discipline reduces defender cost.
- **False negatives masked as "no finding".** A scan with stale or wrong scripts produces a *clean* report that misses real exposure. The dangerous variant — the operator and the defender both think the system is fine.
- **Over-reliance on tooling masks engagement skill gap.** Operators whose only validation step is `--script vuln` plateau at a low ceiling. Senior engagements require the two-pass discipline as a baseline.
- **Engagement-detection footprint.** NSE scripts have recognizable probe patterns. Mature defenders alert on these. Mass `--script vuln` runs frequently end engagements before they begin.

## Detection and defense

This note is unusual: the "detection and defense" framing applies more to the **operator's audit discipline** than to a target-side control. Ordered by effectiveness:

1.
**Adopt the two-pass discipline as a hard rule.**
   First pass: `vuln` script category as hypothesis generator. Second pass: per-finding manual confirmation (often using a different tool entirely). Reports list only second-pass-confirmed findings. This is the single highest-leverage operator habit.

2.
**Maintain a per-engagement script allowlist.**
   Don't run `--script vuln` blindly. Maintain a written list of scripts that have produced reliable signal against the target's tech stack. Update it after each engagement. Over time the list converges on ~20–40 high-signal scripts that drive most real findings.

3.
**Update NSE before every engagement.**
   `sudo nmap --script-updatedb` is cheap and reduces false-positive rate measurably. Treat it like updating wordlists.

4.
**Track which scripts your team trusts (and which they don't).**
   Build a small markdown table in the engagement repo: script name → reliability tier → last-validated date → notes. Onboarding new operators benefits enormously from this institutional memory.

5.
**For the defender side: shape banners and ship versions strategically.**
   The same banner-heuristic weakness that makes `vuln` results unreliable for attackers is the lever defenders use. Removing or randomizing version strings reduces NSE signal-to-noise *for the attacker* while not affecting real security posture (defender's patch state is the actual control).

### What does not work as a primary defense

- **Disabling specific NSE scripts on the target side.** Cannot — the operator chooses which scripts to run.
- **Trusting "no vuln output" as evidence of safety.** False negatives are common. The script's silence is informational, not authoritative.
- **Trusting a `VULNERABLE:` block as a report-ready finding.** It is a hypothesis. Validate before reporting.
- **Running `--script "vuln,exploit"` in production scope.** `exploit` is its own category with active-exploitation scripts. Requires explicit consent and a documented blast-radius assessment.

## Practical labs

```
# Lab 1 — Inventory the vuln category your installation ships.
nmap --script-help "vuln" 2>/dev/null | grep -E '^http-|^ssl-|^smb-|^smtp-|^ftp-' | sort -u | wc -l
nmap --script-help "vuln" 2>/dev/null | grep -E '^[a-z]' | head -30
# Count and sample. Yours will vary by Nmap version.
```

```
# Lab 2 — Run the first pass with a conservative Boolean against an authorized lab.
sudo nmap -sV --script "(default or vuln) and not (intrusive or dos or brute)" \
     -p 21,22,80,443,3306,3389,5432 -oA pass1 LAB_TARGET
# Review pass1.nmap for VULNERABLE: blocks. Each is a hypothesis.
```

```
# Lab 3 — Build a reliability table for what you found.
grep -B1 "VULNERABLE:" pass1.nmap | grep -E "^\| [a-z-]+:" | sort -u
# For each script in the output, classify:
#   - Behavioral probe? (high reliability)
#   - Version-banner only? (low reliability)
#   - Authenticated? (high reliability, scope-dependent)
#   - Stale? (do not trust)
```

```
# Lab 4 — Single-script verification on one finding.
sudo nmap -p 445 --script smb-vuln-ms17-010 -d LAB_TARGET
# The -d flag shows the probe traffic. Cross-check the script logic in:
ls /usr/share/nmap/scripts/smb-vuln-ms17-010.nse  # read it
# This is the "second pass" discipline — confirm the script's logic matches the
# vulnerability it claims to find.
```

```
# Lab 5 — Inspect a stale script.
cat /usr/share/nmap/scripts/http-vuln-cve2010-2861.nse | head -30
# Old CVE. Check the last-modified date. Decide whether to keep it in your
# engagement script set.
```

```
# Lab 6 — Defender-side: NSE detection signatures.
# Run pass1 from Lab 2 against an authorized lab with Suricata or Zeek running.
# Then inspect the IDS alerts for NSE script signatures.
# Example (Suricata):
sudo grep -E "NSE|nmap" /var/log/suricata/fast.log
# The defender will see NSE-specific probe patterns even when the scan is
# otherwise low-volume. The signature is the script's payload, not the scan rate.
```

## Practical examples

- **Bug bounty triage.** Operator submits a report citing `http-vuln-cve-2017-5638` (Struts2) based on raw NSE output. Triager rejects: target is on a patched version of WAS, not Struts. The operator's missed validation step cost the report. Two-pass discipline catches this.
- **Engagement noise budget exhaustion.** Operator runs `--script vuln` against a /16, generates 8,000 hypothesis hits, defender SOC alerts within 90 seconds, engagement is detected before any real validation work begins. Targeted Boolean (`vuln and ssl-*`) on a /24 produces 40 hypotheses, of which 12 validate — far better engagement outcome.
- **Stale-script false positive.** `http-vuln-cve-2014-3704` (Drupalgeddon) fires against a target. Operator runs the actual Drupalgeddon exploit module — target is on a maintained Drupal 9.x and the exploit fails. NSE script was reporting based on a long-ago-fixed version-string heuristic. Validation step prevents a false-positive report.
- **High-signal NSE hit chain.** `smb-vuln-ms17-010` confirms EternalBlue exposure. Operator validates with Metasploit's `smb_ms17_010` auxiliary scanner against an authorized lab, then with the actual exploit module under change-control. End-to-end: NSE → MSF aux → MSF exploit → confirmed finding. The two-pass-plus pattern.
- **Defender side — banner shaping.** Defender removes "Server:" and "X-Powered-By:" headers from all production responses. Operator's `--script vuln` pass returns 80% fewer hypotheses. Defender's patch state did not change; signal-to-noise on the attacker side did. The right kind of asymmetric defense.

## Related notes

- [[rustscan-and-nse-pipeline]] — the pipeline that delivers `vuln` script output via RustScan → Nmap; this note is the audit discipline that follows.
- [[nmap-timing-and-evasion]] — broader Nmap operator framing this fits inside.
- [[nmap-scanning|Nmap Scanning]] — branch root note on scan strategy.
- [[service-enumeration|Service Enumeration]] — what `-sV` and `vuln` scripts are interpreting.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — banner shaping is a clean defender move that exploits the attacker's reliance on version heuristics.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — the same framing applies to vulnerability scanning: behavioral probes beat signature lookups.
- [[run-scan-pipeline|Run External Recon Scan Pipeline]] — the playbook that ends in `--script "(default or vuln) and not (intrusive or dos or brute)"`; this note is the audit on what that Boolean's `vuln` half actually produces.

### Suggested future atomic notes

- writing-custom-nse-scripts — authoring high-signal scripts when shipped ones miss the case.
- banner-shaping-as-asymmetric-defense — defender's mirror to this note.
- vulnerability-vs-finding-vs-alert — the three-tier taxonomy this note implies but does not name explicitly.
- engagement-script-allowlist-management — operational practice for institutional memory of which scripts work.

## References

- **Official Tool Docs:** Nmap Scripting Engine — Categories — https://nmap.org/book/nse-usage.html#nse-categories
- **Official Tool Docs:** NSE script library — `vuln` category index — https://nmap.org/nsedoc/categories/vuln.html
- **Research / Deep Dive:** David Bianco — The Pyramid of Pain (cost-asymmetry framing that explains why version-banner detection is the lowest tier) — https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html
