---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# BloodHound and Attack Path Analysis

## Definition

BloodHound is an open-source graph-analysis tool that models **Active Directory as a directed graph of principals** (users, groups, computers, GPOs, OUs, domains) **and the relationships between them** (`MemberOf`, `AdminTo`, `CanRDP`, `WriteDACL`, `GenericAll`, `ForceChangePassword`, `Owns`, `DCSync`, `AllowedToDelegate`, etc.). Attack paths are then *graph queries* — typically "find the shortest path from any unprivileged principal to a privileged one". The tool is identical for offense and defense; what differs is which queries you run and what you do with the answer.

## Why it matters

Most AD compromises are not single-step exploits. They are **chained relationships**: lowpriv user is a member of group A → group A has `GenericAll` on user B → user B is in `Backup Operators` → `Backup Operators` can read `ntds.dit` → krbtgt hash → domain compromise. No single edge of that chain is obviously dangerous; the *combination* is what matters. Without graph analysis, defenders audit one principal at a time and miss the chain by construction.

BloodHound is the artifact that converted AD security from "audit each ACL" into "compute the transitive closure of dangerous edges". Mastering it is the bridge from "I know Kerberoasting exists" to "I can reason about which Kerberoasting target *actually matters* in this domain".

The senior framing is the offense/defense duality applied to the same tool:

- **Offense:** BloodHound tells the operator which single foothold yields the largest blast radius — making engagement scoping data-driven instead of intuitive.
- **Defense:** BloodHound tells the defender which 5 ACLs they should fix this quarter to eliminate the top 20 attack paths — making remediation prioritization data-driven instead of compliance-driven.

If you cannot articulate both sides of that pair, you have learned half of BloodHound.

## How it works

BloodHound reduces to **3 stages**:

1. **Collection.** A collector (SharpHound on Windows, `bloodhound-python` on Linux, AzureHound for Entra ID) queries AD via LDAP and SMB to enumerate principals and their relationships. Output is JSON files (`*_users.json`, `*_groups.json`, `*_computers.json`, `*_gpos.json`, etc.).
2. **Ingestion.** The JSON is loaded into a Neo4j graph database via the BloodHound UI. Every principal becomes a node; every relationship becomes a typed, directed edge.
3. **Query.** The UI exposes both pre-built queries ("Find shortest paths to Domain Admins", "Find principals with DCSync rights", "Find Kerberoastable users") and a Cypher query interface for custom analysis.

A canonical end-to-end sequence from a Linux foothold:

```
# Stage 1: collect from any domain-joined or domain-reachable host with a valid cred.
bloodhound-python -u lowpriv -p 'Password1' -ns 10.0.0.1 -d LAB.LOCAL -c All
# Produces 20240510*_users.json, _groups.json, _computers.json, _domains.json, etc.

# Stage 2: spin up BloodHound CE (Community Edition) locally and import.
docker compose -f bloodhound-cli.yaml up -d
# Open the UI at http://localhost:8080, upload the JSON files.

# Stage 3: query. Pre-built: "Shortest Paths to Domain Admins".
# Or custom Cypher:
MATCH (n {kerberoastable: true})-[*1..]->(g:Group {name: 'DOMAIN ADMINS@LAB.LOCAL'})
RETURN n.name, length(shortestPath((n)-[*..]->(g))) AS path_length
ORDER BY path_length ASC
```

The bug is not "ACLs in AD are wrong"; it is *the security posture of AD is not visible without computing the transitive closure of trust relationships across thousands of nodes — which is the problem graph databases were built to solve*.

## Techniques / patterns

- **Collect with `-c All` on first pass, narrower on follow-ups.** `All` runs every collection method (Group, Acl, Trusts, Session, LoggedOn, ObjectProps, SPNTargets, Container, etc.). For repeat collections, run `Session` and `LoggedOn` separately because they capture *who is logged in where* and decay quickly — fresh session data is what makes lateral-movement paths real.
- **Cypher beats the pre-built queries for engagement scoping.** Learn enough Cypher to write your own targeted queries — "users in Kerberoastable accounts who can reach DA in ≤ 3 hops" is far more useful than "all Kerberoastable users".
- **`MarkOwned` your foothold immediately.** The UI lets you mark principals as "owned" (compromised). Path queries from `(:User {owned: true})` to high-value targets show your *actual* path forward, not the theoretical one.
- **Look for `DCSync` rights early.** Any principal with `DS-Replication-Get-Changes-All` or `GetChangesAll` can replicate the entire AD database including all password hashes. Query: `MATCH (n)-[:DCSync]->(d:Domain) RETURN n.name`. The hit list is usually short (Domain Controllers + a handful of misconfigured accounts) — every misconfigured one is an endgame.
- **Treat paths to DCSync as paths to Golden Ticket capability.** If a graph path reaches a principal that can replicate `krbtgt`, it reaches [[golden-ticket-and-krbtgt-compromise|domain Kerberos trust-root compromise]], not just "hash dumping".
- **Pair with [[kerberoasting|Kerberoasting]] and [[as-rep-roasting|AS-REP Roasting]] outputs.** BloodHound knows which accounts are Kerberoastable and AS-REP-roastable. After roasting, mark the cracked accounts as owned and re-run path queries — paths frequently shrink dramatically.
- **Defenders: run BloodHound *on your own AD*, monthly.** The query "Shortest Paths to Domain Admins" is the same on both sides; the defender's job is to make those paths longer or eliminate them.
- **OPSEC: collection is loud.** `bloodhound-python -c All` against a large domain issues thousands of LDAP queries and SMB session enumerations in minutes. Use scoped collection (`-c Group,Acl` only) when stealth matters.

## Variants and bypasses

BloodHound's ecosystem has **4 collector variants** worth distinguishing.

### 1. SharpHound (Windows, .NET)

The original collector. Runs in-process on a domain-joined Windows host. Strongest collection coverage (most accurate session/loggedon data) but triggers AMSI and most modern EDR. OPSEC-aware operators use older versions, AMSI bypasses, or reflective loading from `Rubeus`-style PowerShell.

### 2. bloodhound-python

Linux-native. Connects to AD over LDAP (port 389/636) and SMB (445) with explicit credentials. No domain join, no .NET, no Windows host required. Slightly weaker session data than SharpHound but enough for path analysis. The standard choice from a Linux pentest host.

### 3. AzureHound

Targets Entra ID / Microsoft 365 / Azure AD instead of on-prem AD. Different node types (`AzureUser`, `AzureGroup`, `AzureRole`, `AzureApp`, `AzureSubscription`) and different edges (`AZRoleEligibility`, `AZGlobalAdmin`, etc.). Same conceptual model, different protocol stack. Essential for hybrid environments.

### 4. BloodHound Enterprise (BHE / commercial)

SpecterOps's commercial product. Continuous collection, attack-path management dashboards, percentage-of-paths-eliminated metrics. The defender-grade variant. Worth knowing exists; on the offensive side everyone uses BloodHound CE (free, open-source).

## Impact

Ordered by typical real-world severity:

- **Engagement-time-to-DA collapses from days to hours.** A red-team operator with BloodHound and a foothold can identify the optimal path within 30 minutes of collection. Without it, the same operator spends days enumerating manually and frequently picks the wrong path first.
- **Defender prioritization becomes data-driven.** "We have 12,000 ACLs in this domain" becomes "5 specific ACEs account for 80% of the paths to DA, and fixing them this quarter eliminates 200 attack paths". Compliance frameworks cannot produce this analysis; only graph traversal can.
- **The blast-radius question is finally answerable.** "If account X is compromised, what can the attacker reach?" used to require manual ACL traversal. It is now `MATCH (n {name:'X'})-[*1..5]->(target) RETURN target`. Senior security work demands an answer to this question, and BloodHound is what makes it cheap.
- **Hybrid (on-prem + Azure) compromise paths become visible.** Connectors that bridge on-prem AD and Entra ID (Azure AD Connect, password hash sync, pass-through auth) create cross-boundary paths that traditional auditing misses entirely. AzureHound + BloodHound together surface them.
- **Detection footprint of collection itself.** BloodHound collection produces a recognizable signature (massive LDAP enumeration + ACL queries + SMB session enumeration from a single source). Mature defenders alert on the collection pattern as an early-warning indicator of red-team activity.

## Detection and defense

Ordered by effectiveness:

1.
**Use BloodHound defensively, monthly.**
   The single highest-leverage move. Run collection on your own AD, identify the top 10 shortest paths to Domain Admins, and remediate the cheapest edges. Repeat. This *is* attack-path management. Compliance audits do not produce this output.

2.
**Behavioral detection on LDAP enumeration patterns.**
   BloodHound collection signature: one source IP issues thousands of LDAP queries against many distinct OUs and objects within minutes, plus SMB session enumeration. Build a SIEM rule keyed on LDAP query rate + diversity per source. See [[behavioral-detection-vs-signature-detection|behavioral detection]].

3.
**Reduce the number of `Tier 0` principals.**
   Tier 0 = anyone with effective Domain Admin authority. The fewer principals at Tier 0, the shorter the attack surface for graph traversal. Microsoft's tiered admin model (Tier 0 / Tier 1 / Tier 2) plus enforced separation of admin accounts from daily-driver accounts is the structural defense.

4.
**Audit and prune dangerous ACEs.**
   `WriteDACL`, `GenericAll`, `GenericWrite`, `WriteOwner`, `ForceChangePassword`, `AllExtendedRights`, and DS-Replication-Get-Changes-* are the high-leverage edges BloodHound queries for. Most are legacy delegations that nobody remembers granting. Audit them per [[kerberoasting|Kerberoasting]]'s "audit and remove privileged service accounts" pattern.

5.
**Tier 0 isolation.**
   No Tier 0 admin should ever log on to a Tier 1 or Tier 2 host. The moment they do, their credentials live in memory on a less-protected host and lateral movement becomes available. Privileged Access Workstations (PAWs) enforce this physically.

6.
**Honeypot principals high in the graph.**
   Plant a deceptively-attractive account (e.g., `svc_backup_admin`) with no production access but high-impact-looking ACLs. Any BloodHound query that surfaces it as a "great target" tells you a collector ran. Alert on session activity against the honeypot.

### What does not work as a primary defense

- **"We don't have any Domain Admins outside the SOC team."** Almost always wrong on inspection. Run BloodHound and discover the 30 effective admins your org chart does not show.
- **Disabling SMB enumeration.** Reduces collection fidelity slightly but does not prevent graph construction from LDAP alone.
- **Blocking BloodHound binaries.** SharpHound is the named collector but bloodhound-python + custom collectors trivially bypass binary-name blocks. The signature is the *enumeration pattern*, not the binary.
- **Trusting ACL audit tools that do not compute transitive closure.** Traditional ACL audit lists individual ACEs. The attack lives in chains. A list view is the wrong data structure for this problem.

## Practical labs

Run only against owned lab environments or authorized engagements.

```
# Lab 1 — Spin up BloodHound CE locally with Docker.
git clone https://github.com/SpecterOps/BloodHound.git
cd BloodHound/examples/docker-compose
docker compose up -d
# Open http://localhost:8080 — default creds in the README; rotate immediately.
```

```
# Lab 2 — Collect from a Linux pentest host against an authorized lab DC.
bloodhound-python -u lowpriv -p 'Password1' -ns 10.0.0.1 -d LAB.LOCAL -c All
ls *_users.json *_groups.json *_computers.json *_domains.json
# Drag the JSON files into the BloodHound UI to ingest.
```

```
// Lab 3 — Pre-built query: shortest paths to Domain Admins.
// In the UI's Cypher query box (or via the "Analysis" tab):
MATCH p=shortestPath((n:User)-[*1..]->(g:Group {name: 'DOMAIN ADMINS@LAB.LOCAL'}))
WHERE n.enabled = true
RETURN p LIMIT 25
```

```
// Lab 4 — Custom: Kerberoastable users with a path to DA in ≤ 3 hops.
MATCH (u:User {hasspn: true})
MATCH p=shortestPath((u)-[*1..3]->(:Group {name: 'DOMAIN ADMINS@LAB.LOCAL'}))
RETURN u.name AS account, length(p) AS hops
ORDER BY hops ASC
```

```
// Lab 5 — Defender's high-leverage query: principals with DCSync rights.
MATCH (n)-[r:GetChanges|GetChangesAll|DCSync]->(:Domain)
RETURN DISTINCT n.name AS principal, labels(n) AS type
// Domain Controllers should appear here. Anything else is a finding.
```

```
# Lab 6 — Defender-side detection rule design.
# After running BloodHound against the lab, query Windows Event logs on the DC:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4662} -MaxEvents 200 |
    Where-Object { $_.Properties[7].Value -match 'DS-Replication-Get-Changes' }
# Repeated bursts from one source IP across many objects = BloodHound collection signature.
# Use as input to a SIEM correlation rule.
```

## Practical examples

- **Red-team engagement post-foothold.** Initial phish lands a lowpriv user. BloodHound collection within 30 minutes; shortest-path query shows the user is in `IT Support` which has `GenericAll` on `Backup Service` which is in `Backup Operators`. Two ACE edges from phish to DA. Total engagement time: 4 hours.
- **Quarterly defender BHE-style review.** Security team runs BloodHound on production AD, identifies that `IT Helpdesk` group has `ForceChangePassword` on 47 privileged accounts via a legacy 2014 delegation. Removing the delegation eliminates 312 attack paths overnight.
- **Hybrid Azure + on-prem analysis.** AzureHound + BloodHound together reveal that an on-prem service account syncing to Entra ID has `Global Administrator` in Azure due to a mistaken role assignment. On-prem compromise → Azure tenant takeover via a single connector. Without graph analysis, the path is invisible.
- **Kerberoast targeting.** Roaster has 15 cracked service-account passwords. BloodHound shows which 3 of the 15 reach DA in ≤ 2 hops. The other 12 are noise. Engagement focuses on the 3.
- **Tier-0 isolation finding.** Defender query "users who can RDP to Tier 0 hosts" returns the entire IT department. The org assumed only the SOC could; the audit produces an immediate remediation backlog.

## Related notes

- [[kerberoasting]] — BloodHound shows you which Kerberoastable accounts are worth roasting.
- [[as-rep-roasting]] — BloodHound shows you which AS-REP-roastable accounts have onward paths.
- [[golden-ticket-and-krbtgt-compromise]] — the downstream consequence of attack paths that reach DCSync of `krbtgt`.
- [[gmsa-and-modern-service-account-hardening]] — defensive graph review should include service-account privilege, retrieval scope, and delegation edges.
- [[tier-zero-administration-and-paw]] — the structural defense BloodHound output usually motivates.
- [[krbtgt-rotation-and-tier-zero-recovery]] — Tier 0 recovery depends on removing graph paths back to DCSync before rotating `krbtgt`.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the cleanest single-tool example of the duality: same tool, both sides, just different queries.
- [[threat-modeling-quickstart|Threat Modeling Quickstart]] — BloodHound is essentially "STRIDE for AD relationships", computed automatically.
- [[behavioral-detection-vs-signature-detection|Behavioral vs signature detection]] — the right framing for catching BloodHound collection.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — the defensive counterpart concept; paths are the unit of analysis on both sides.
- [[enumeration|Enumeration]] — BloodHound is enumeration with graph semantics on top.

### Suggested future atomic notes

- writedacl-and-genericall-acl-abuse — the high-leverage edge types and how to abuse them.
- shadow-credentials-and-kerberos-pkinit — the modern AD-CS-based persistence path that BloodHound v4+ added edges for.
- [[detect-bloodhound-collection]] — the defender-side playbook pair.

## References

- **Official Tool Docs:** BloodHound Community Edition documentation (SpecterOps) — https://bloodhound.specterops.io/
- **Research / Deep Dive:** Robbins, Schroeder, Vazarkar — "An ACE Up The Sleeve: Designing Active Directory DACL Backdoors" (Black Hat USA 2017, the foundational paper) — https://www.specterops.io/assets/resources/an_ace_up_the_sleeve.pdf
- **Research / Deep Dive:** Robbins & Schroeder — "Six Degrees of Domain Admin" (DEF CON 24, the original BloodHound talk) — https://www.youtube.com/watch?v=lxd2rerVsLo
