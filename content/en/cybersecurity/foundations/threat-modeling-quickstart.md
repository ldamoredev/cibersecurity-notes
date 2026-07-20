---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Threat Modeling Quickstart

## Definition

Threat modeling is the practice of looking at a system, walking its components and trust boundaries, and answering four questions: **what are we building, what can go wrong, what are we going to do about it, and did we do a good job?** Done well it takes an hour for a feature and a day for a service. Done poorly — or skipped — it produces controls aimed at threats nobody actually faces while the real risks go unanalyzed.

## Why it matters

Security work without threat modeling reduces to running checklists. Checklists are useful but they cannot tell you *which* of their items matter for *your* system, or where the items leave gaps. Threat modeling is the discipline that produces the *right* checklist for a particular asset, instead of treating every system as if it had the same threats.

The framing also fixes the most common newcomer confusion: "security is the security team's job". A threat model is best built by *the people who built the system* — they know the components, the assumptions, and the trust boundaries far better than any outside reviewer. The security team's role is to teach the methodology, review the output, and identify cross-cutting threats. The team that wrote the code owns the threat model the same way it owns the design.

The senior framing is that threat modeling is **structured paranoia**: you replace "I have a bad feeling about this" with a repeatable artifact that names the threats, attaches them to system elements, and records the decisions you took about each one.

## How it works

Threat modeling reduces to **4 questions** (the Adam Shostack frame) and **1 categorization** (STRIDE).

### The 4 questions

1. **What are we building?** Draw the system as a data flow diagram (DFD): boxes for processes and data stores, arrows for data flows, dashed lines for trust boundaries. The picture is the artifact; bullet points are not enough.
2. **What can go wrong?** Walk each element of the DFD and apply STRIDE (below) to it. For each element-threat pair, ask "is this credible in our threat model?".
3. **What are we going to do about it?** For each credible threat, pick one of four responses: *mitigate* (add a control), *accept* (live with it, record why), *transfer* (insurance, contract, dependency on a more capable party), *eliminate* (remove the feature).
4. **Did we do a good job?** Review the model after the system ships, and on every meaningful change. Update or invalidate.

### STRIDE — the categorization

Six threat categories, each mapped to a [[cia-triad-and-what-it-actually-decides|CIA]] property:

| Letter | Threat | CIA property | Example mitigation family |
| --- | --- | --- | --- |
| **S** | Spoofing | Authenticity (a flavor of integrity) | Authentication, signed tokens, mTLS |
| **T** | Tampering | Integrity | MACs, signatures, immutable storage, AEAD |
| **R** | Repudiation | Integrity + auditability | Signed/immutable audit logs |
| **I** | Information disclosure | Confidentiality | Access control, encryption, channel isolation |
| **D** | Denial of service | Availability | Rate limiting, capacity, redundancy, graceful degradation |
| **E** | Elevation of privilege | Integrity + authorization | Least privilege, authorization checks, sandboxing |

The bug is not "we did not threat-model"; the bug is *we did not walk our trust boundaries and ask STRIDE at each one, so our controls protect the wrong elements*.

## Common misconceptions

### "Threat modeling is a 6-month project that needs a consultant."

This is the academic version, useful for safety-critical systems. The working version a developer or IT person should master is the 4-question / STRIDE pass on one feature, which takes an hour. The investment-to-payoff curve is steep early and flattens fast — the first hour produces 80% of the value. Skipping that hour because "we need a real threat-modeling program" is a common excuse for never doing it at all.

### "Only the security team can do it."

The opposite is true. The team that built the system has the deepest model of how it works, where its assumptions live, and which trust boundaries are real vs aspirational. The security team's leverage is *teaching* the methodology and reviewing output for cross-cutting threats, not doing threat modeling on behalf of every product team.

### "STRIDE catches everything."

STRIDE is a categorization aid, not a coverage guarantee. It misses:
- **Business-logic flaws** (race conditions in checkout, abusing referral codes for free credit) — they fit awkwardly into "tampering" but are usually missed.
- **Privacy / data-sensitivity threats** beyond information disclosure (e.g., correlation attacks, re-identification of anonymized data).
- **Supply-chain threats** that span systems STRIDE was originally scoped to.
Treat STRIDE as scaffolding, not as the answer. The 4 questions are the actual frame; STRIDE is one of several useful prompts.

### "We threat-modeled at design time, we're done."

Threat models are living artifacts. Every new feature, every new dependency, every new integration changes the trust boundaries. A threat model that does not get updated is wrong within months. Treat it the way you treat architecture diagrams or ADRs — version it, link it from the codebase, and update it when reality changes.

### "Tools (Microsoft TMT, OWASP Threat Dragon, IriusRisk) do the thinking for you."

Tools capture and present threat models well; they do not *generate* them. The reasoning is human. A tool's auto-generated threat list is a starting point, not a deliverable. Senior usage is "use the tool to draw and store the DFD; use your brain (and STRIDE prompts) to populate the threats."

### "Threat modeling is for new systems only."

Existing systems benefit *more* from threat modeling than new ones, because their assumptions have drifted from their original design. A "threat-model an existing service" exercise routinely uncovers controls that no longer match the threats the service actually faces.

## How to apply this

The 4 questions + STRIDE turn into **a repeatable hour-long ritual** for any feature:

1. **Draw the DFD on a whiteboard or in Excalidraw.** Boxes (processes), cylinders (data stores), arrows (flows), dashed lines (trust boundaries). Spend 10–20 minutes here. If you cannot draw it, you do not understand the system well enough to threat-model it.
2. **Walk each element through STRIDE.** For every box, arrow, and data store, ask all six STRIDE questions out loud. Some will obviously not apply; many will surface threats nobody had named. Record the credible ones.
3. **Decide on each credible threat.** Mitigate / accept / transfer / eliminate. Write the decision and the rationale next to the threat.
4. **Cross-check against CIA priority.** For your dominant asset, is the C/I/A you ranked highest covered by your mitigations? If not, you have a coverage gap.
5. **Store the artifact next to the code.** A threat-model markdown file in the repo, version-controlled, linked from the README. Threat models that live in shared drives die.
6. **Reopen on change.** When the design changes meaningfully, re-walk the affected part of the DFD.

## Practical examples

- **Login form.** DFD: browser → reverse proxy → app → user DB + session store. STRIDE walk surfaces: spoofing (credential stuffing → MFA), tampering (session-cookie forgery → signed/encrypted cookies), repudiation ("I didn't log in" → audit log), information disclosure (user enumeration via response-time / error-message difference → uniform responses), DoS (password brute force → rate limit + account lockout strategy), elevation (auth bypass via parameter manipulation → server-side authorization on every action).
- **File upload.** DFD: client → app → object storage → downstream consumer. STRIDE: tampering (uploaded file modified after scan → integrity hash + write-once storage), info disclosure (path-traversal exposing other tenants' files → server-generated paths), DoS (large or zip-bomb files → size and decompression limits), elevation (uploaded executable run by the server → store outside the app's exec path, scan in sandbox).
- **API endpoint that proxies to internal services.** DFD shows a trust boundary the developers forgot existed. STRIDE on the proxy: spoofing (client identity replayed downstream → propagate signed identity, not raw token), tampering (request rewritten → input validation), info disclosure (internal topology leaked via error messages → opaque error mapping), elevation (SSRF reaching the metadata service → allowlist outbound destinations).
- **CI/CD pipeline.** DFD: developer → git → CI runner → registry → production. STRIDE: tampering (build steps modified → reproducible builds, signed artifacts), info disclosure (secrets in build logs → secret scanning, masked logs), DoS (runner exhaustion via abusive PR → resource quotas), elevation (runner privileges abused → least-privilege OIDC tokens, ephemeral runners). This single pass is how most modern supply-chain controls (SLSA, Sigstore) are motivated.
- **Existing legacy service rebuild.** Draw the DFD as it is *today*, not as the original architecture document claims. The gap between "design DFD" and "reality DFD" is itself a finding.

## Related notes

- [[what-is-cybersecurity-and-why-it-is-not-a-tool-list]] — the framework this sits inside.
- [[cia-triad-and-what-it-actually-decides]] — STRIDE categories map back to CIA properties.
- [[attacker-defender-duality-as-a-learning-tool]] *(future)* — threat modeling is one of the disciplines that makes the duality concrete.
- [[index|Web Security]] — STRIDE applied to the daily-surface system class.
- [[index|API Security]] — STRIDE applied to machine-readable surfaces.
- [[index|DevSecOps]] — threat modeling the build/release pipeline itself.
- [[index|Detection Engineering]] — every threat your model accepts needs a corresponding detection story.

### Suggested future atomic notes

- stride-vs-pasta-vs-octave
- dfd-conventions-and-trust-boundaries
- threat-modeling-as-code
- business-logic-threat-modeling

## References

- **Foundational:** Adam Shostack — Threat Modeling: Designing for Security (the canonical text) — https://shostack.org/books/threat-modeling-book
- **Foundational:** Microsoft — STRIDE Threat Model — https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
- **Testing / Lab:** OWASP Threat Modeling Process — https://owasp.org/www-community/Threat_Modeling_Process
