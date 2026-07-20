---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Wi-Fi Wordlist Attacks

## Definition

Wi-Fi wordlist attacks test captured WPA/WPA2-PSK material against candidate passphrases to determine whether a network key is guessable.

## Why it matters

The wireless capture is only half the story. Wordlist testing shows whether the human-chosen PSK is weak enough to recover offline.

This note belongs in wireless security because the input is Wi-Fi handshake material, but the deeper lesson transfers everywhere: shared secrets fail when humans choose predictable words, formats, and mutations.

## How it works

Wordlist attacks have **5 stages**:

1. **Acquire valid material.** Capture a handshake or PMKID from an owned or authorized network.
2. **Choose candidate sources.** Use known defaults, policy patterns, or test dictionaries.
3. **Apply rules or masks.** Generate realistic variations.
4. **Derive and compare.** The tool tests candidates against the captured material.
5. **Report strength.** A non-cracked capture is not proof of strength, only proof against the tested candidates.

The bug is not that offline testing exists. The bug is a PSK that appears in a realistic candidate set.

A worked example, wordlist result without overclaiming:

```
Capture:
  lab WPA2 handshake

Candidate set:
  company names, seasons, years, guest patterns, 500 test entries

Result:
  no match

Conclusion:
  PSK resisted this candidate set only; it is not proof of strong randomness

Next action:
  verify generated length, storage, guest separation, and rotation process
```

A failed wordlist test should narrow conclusions, not create false confidence.

## Techniques / patterns

Testing looks at:

- default router passwords and ISP patterns
- company names, addresses, seasons, and predictable suffixes
- reused guest passwords
- short passphrases with substitutions
- whether password managers or generated secrets are used

## Variants and bypasses

Wordlist testing has **4 common modes**.

### 1. Straight dictionary

Tests each candidate exactly as written.

### 2. Rule-based mutation

Applies predictable edits such as years, capitalization, and symbols.

### 3. Mask attack

Tests a structured pattern such as letters plus digits.

### 4. Target-informed guessing

Uses organization-specific words, which raises ethical and privacy concerns and must stay inside authorization.

## Impact

Ordered roughly by severity:

- **PSK recovery.** A matching candidate reveals the shared network secret.
- **Silent future access.** The key can be reused until rotation.
- **Wider credential risk.** Predictable Wi-Fi passwords may indicate broader password culture problems.
- **False confidence.** A failed crack can be misread as proof of strong security.

## Detection and defense

Ordered by effectiveness:

1.
**Use generated, long, random PSKs.**
   Randomness makes wordlist and mask strategies impractical at normal scales.

2.
**Move high-trust environments to Enterprise authentication.**
   Per-user credentials and certificates reduce shared-secret blast radius.

3.
**Rotate shared PSKs when membership changes.**
   Shared secrets become stale as people and devices leave.

4.
**Test against realistic candidate sets during audits.**
   Defensive testing catches passwords that policy text alone misses.

### What does not work as a primary defense

- **Adding `!` or `2026` to a word.** Those mutations are exactly what rules test.
- **Assuming one failed wordlist means safe.** It only means that candidate set failed.
- **Using organization names in PSKs.** Context-specific words are easy candidates.
- **Relying on lockouts.** WPA/WPA2 offline guessing does not hit the AP after capture.

## Practical labs

Use only handshakes from owned lab networks.

### Create a tiny defensive candidate set

```
companyname2026!
guestwifi2026
labrouter12345
correct-horse-battery-staple
```

Use this to demonstrate why predictable patterns are dangerous.

### Run a bounded lab check

```
aircrack-ng -w lab-wordlist.txt -b LAB_BSSID wpa-lab-01.cap
```

Record whether the PSK matched the tested candidates.

### Report without overclaiming

```
Capture:
Candidate set:
Rules/masks:
Result:
What this proves:
What this does not prove:
```

Failed cracking is limited evidence, not a guarantee.

### Compare human and generated PSK models

```
PSK source | length | pattern | rotation | likely in wordlists? | decision
human phrase | 14 | brand+year | yearly | yes | replace
generated | 24 | random | on departure | no | keep
```

The defensive goal is to remove predictable candidates.

### Document safe handling of captures

```
capture file:
contains client identifiers:
storage location:
retention period:
delete date:
authorized scope:
```

Wireless captures can contain sensitive metadata and should be retained deliberately.

## Practical examples

- A guest Wi-Fi password is the company name plus the current year.
- A router default key follows a vendor pattern.
- A lab PSK is cracked with a five-line dictionary.
- A long generated passphrase survives a realistic audit set.
- A shared PSK stays valid after a staff turnover event.

## Related notes

- [[wpa-wpa2-handshakes]]
- [[wireless-security]]
- [[wep-security]]
- [[token-lifecycle|Token Lifecycle]]
- [[scope-validation|Scope Validation]]

### Suggested future atomic notes

- password-cracking-rules
- hashcat-workflows
- wireless-key-rotation
- default-router-credentials

## References

- **Official Tool Docs:** Aircrack-ng WPA/WPA2 tutorial — https://www.aircrack-ng.org/doku.php?id=cracking_wpa
- **Official Tool Docs:** Hashcat example hashes — https://hashcat.net/wiki/doku.php?id=example_hashes
- **Mitigation:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
