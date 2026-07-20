---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Traffic Correlation

## Definition

Traffic correlation is the linking of a user's activity by comparing traffic timing, volume, routing, and pattern across different observation points.

## Why it matters

Even when content is encrypted and the source IP is hidden, an observer with enough visibility can sometimes compare when packets go in and when packets come out. Tor and other anonymity systems are designed partly to make this harder, but traffic correlation remains a core anonymity concern.

## How it works

Use the 5 traffic signals:

1.
**Timing**
   When packets appear and how they line up.

2.
**Volume**
   How much data moves in each direction.

3.
**Direction**
   Which way the packets flow and how bursts align.

4.
**Path**
   Which relays, providers, or networks are on the route.

5.
**Pattern**
   Repeated structure in the traffic stream.

The bug is not that traffic exists. The bug is assuming encryption alone hides timing and volume.

## Techniques / patterns

- Use anonymity systems that distribute trust and mix traffic patterns.
- Avoid unique activity patterns when anonymity matters.
- Treat large uploads, distinctive bursts, and regular timing as linkable.
- Recognize that server-side logs and network-side observations can be combined.
- Understand that public exits, bridges, and entry points create different visibility points.

## Variants and bypasses

Use the 6 correlation forms:

### 1. End-to-end timing

Compare when traffic enters and exits a network.

### 2. Burst correlation

Match distinctive spikes or pauses.

### 3. Interactive pattern correlation

Chat or browsing cadence can reveal a session shape.

### 4. Website and relay correlation

Different observers on the path can combine partial views.

### 5. Packet-size pattern correlation

Repeated size sequences can be identifying.

### 6. Cross-session correlation

The same routine across multiple sessions becomes linkable.

## Impact

- Strong adversaries may link source and destination despite encryption.
- Timing and size patterns can weaken anonymity.
- Tor exit and entry visibility matter differently from ordinary VPN privacy.
- Unique workflows are easier to correlate.
- Users may assume "encrypted" means "uncorrelatable," which is false.

## Detection and defense

Ordered by effectiveness:

1.
**Use a design that reduces single-observer power**
   Tor's relay structure exists for this reason.

2.
**Avoid distinctive traffic patterns**
   Large, rhythmic, or unique transfers are easier to match.

3.
**Separate activities in time and context**
   One identity should not create a repeatable pattern across unrelated tasks.

4.
**Use bridges and transport camouflage where needed**
   These help against local detection, not full correlation resistance.

5.
**Assume strong observers can combine partial data**
   The safe model is conservative.

### What does not work as a primary defense

- **Encryption does not stop traffic correlation.**
- **A VPN does not remove timing patterns.**
- **Tor reduces but does not eliminate correlation risk.**
- **Random pauses and ad hoc tricks are not a robust anonymity strategy.**

## Practical labs

### Draw a timing sketch

```
Event 1:
Event 2:
Event 3:
Packet burst:
Pause:
Observer A sees:
Observer B sees:
Possible link:
```

The sketch reveals correlation opportunities.

### Compare volume patterns

```
Upload size:
Download size:
Burst shape:
Repeatability:
Distinctive?
```

Distinctive patterns are linkable patterns.

### Review route visibility

```
Observer:
Sees entry:
Sees exit:
Sees timing:
Sees volume:
Can combine with:
```

This is the core traffic-correlation table.

### Identify high-risk workflows

```
Workflow:
Chat / browsing / upload / download:
Regularity:
Sensitivity:
Need for anonymity:
Risk of pattern:
```

Some workflows are inherently easier to correlate than others.

## Practical examples

- A large file upload and download pattern is easy to spot across a network.
- A Tor session still has timing and packet-size structure.
- A VPN hides source IP but not all flow characteristics.
- A repeated daily schedule becomes a correlation clue.
- A bridge or transport helps with censorship detection but not with every global observer.

## Related notes

- [[anonymity-threat-models|Anonymity Threat Models]]
- [[tor-and-onion-services|Tor and Onion Services]]
- [[vpn-vs-tor|VPN vs Tor]]
- [[deanonymization-failures|Deanonymization Failures]]
- [[packet-analysis|Packet Analysis]]

### Suggested future atomic notes

- timing-attacks
- burst-correlation
- mix-network-basics

## References

- **Research / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
