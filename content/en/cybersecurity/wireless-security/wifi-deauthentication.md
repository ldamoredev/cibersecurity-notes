---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Wi-Fi Deauthentication

## Definition

Wi-Fi deauthentication is the use or abuse of 802.11 management frames to disconnect clients from an access point.

## Why it matters

Deauthentication shows that availability and authentication are separate questions. A network can use strong encryption and still be vulnerable to disruption if management frames are unprotected.

It also appears in attack chains: forcing reconnection can help capture handshakes or push clients toward a rogue access point. That makes strict lab boundaries important.

## How it works

Deauthentication abuse has **4 steps**:

1. **Identify AP and client.** The attacker observes BSSID, channel, and stations.
2. **Send forged management frames.** Frames claim the client or AP is ending the association.
3. **Client disconnects.** The station drops and usually tries to reconnect.
4. **Follow-on effect occurs.** The reconnection may produce a handshake or create a chance for rogue AP attraction.

The bug is not IP-layer routing. It is management-plane trust in unauthenticated or weakly protected frames.

A worked example, deauth as control validation:

```
Lab setup:
  owned AP, owned laptop client, channel 11

Baseline:
  client connected and streaming ping to gateway

Controlled test:
  5 deauth frames sent in lab window

Observed:
  client disconnects, reconnects, EAPOL appears in pcap

Decision:
  PMF is not required or not supported by this client/AP pair; enable required PMF where compatible
```

The useful result is the resilience/control finding, not the disruption itself.

## Techniques / patterns

Testing looks at:

- whether deauth frames affect clients in an owned lab
- whether PMF is supported, optional, or required
- whether controller logs show deauth spikes
- whether critical devices roam or reconnect unsafely
- whether user devices choose stronger rogue signals

## Variants and bypasses

Deauthentication has **4 practical variants**.

### 1. Broadcast deauth

Targets all clients for a BSSID and is noisy.

### 2. Client-specific deauth

Targets a specific station and is more controlled in labs.

### 3. Periodic disruption

Repeats frames to cause sustained availability loss.

### 4. Chain to handshake or evil twin

Uses disconnect/reconnect behavior as a setup step for another test.

## Impact

Ordered roughly by severity:

- **Availability loss.** Clients disconnect from wireless service.
- **Handshake capture opportunity.** Reconnection may generate EAPOL frames.
- **Rogue AP coercion.** Clients may connect to a lookalike network.
- **Operational risk.** Medical, industrial, or payment devices may be sensitive to brief outages.

## Detection and defense

Ordered by effectiveness:

1.
**Require protected management frames where possible.**
   PMF directly targets the management-frame trust weakness behind common deauth abuse.

2.
**Use wireless controller or WIDS alerts.**
   Deauth floods and abnormal management-frame patterns should be visible.

3.
**Avoid auto-joining untrusted lookalike networks.**
   Client configuration and user training reduce rogue AP follow-on risk.

4.
**Design critical systems with wired or redundant paths.**
   Wireless availability can be disrupted; critical operations should not assume perfect radio continuity.

### What does not work as a primary defense

- **Strong WPA2 password alone.** It protects joining, not all management frames.
- **SSID hiding.** Clients and BSSIDs remain observable.
- **Ignoring brief disconnects.** Short bursts can be enough to capture handshakes.
- **Blaming the internet link.** Deauth is local radio-layer disruption.

## Practical labs

Only test against an owned lab AP and test client.

### Observe deauth frames

```
sudo airodump-ng --bssid LAB_BSSID --channel LAB_CH --write deauth-lab wlan0mon
```

Use Wireshark to inspect management frames during a controlled test.

### Run a short controlled deauth

```
sudo aireplay-ng --deauth 5 -a LAB_BSSID wlan0mon
```

Stop immediately and record impact on the test client only.

### Check PMF setting

```
AP model:
PMF disabled / optional / required:
Client support:
Observed behavior:
```

Use the test to drive configuration, not disruption.

### Record deauth test boundaries

```
Authorized BSSID:
Authorized client:
Channel:
Frame count:
Start/stop time:
Observed impact:
Rollback:
```

Deauth tests should be small, named, and reversible.

### Monitor client recovery

```
disconnect observed:
reconnect time:
wrong network joined:
handshake captured:
user-visible impact:
```

Recovery behavior matters as much as whether frames were accepted.

### Compare PMF modes in a lab

```
PMF disabled result:
PMF optional result:
PMF required result:
client compatibility:
recommended setting:
```

Use owned devices only; compatibility decides whether PMF can be required immediately.

## Practical examples

- A lab phone reconnects and produces a visible handshake.
- A network with PMF required resists a basic deauth test.
- A public venue has repeated disconnect waves during an event.
- A rogue AP attack begins by forcing clients off the legitimate AP.
- A critical IoT device fails badly after brief Wi-Fi loss.

## Related notes

- [[wireless-security]]
- [[wifi-monitor-mode]]
- [[wpa-wpa2-handshakes]]
- [[evil-twin-access-points]]
- [[packet-analysis|Packet Analysis]]

### Suggested future atomic notes

- protected-management-frames
- wireless-intrusion-detection
- wpa3-sae
- wifi-roaming-security

## References

- **Official Tool Docs:** Aircrack-ng aireplay-ng — https://www.aircrack-ng.org/doku.php?id=aireplay-ng
- **Official Tool Docs:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Mitigation:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
