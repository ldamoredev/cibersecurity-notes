---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# WEP Security

## Definition

WEP security is the legacy Wi-Fi encryption scheme that attempted to protect wireless traffic with RC4 and initialization vectors but is now considered broken.

## Why it matters

WEP is important as a history lesson and as a real-world risk when old equipment still exists. Its failure shows why encryption mode design, nonce reuse, and protocol lifecycle matter.

For practice, WEP labs are useful because they teach packet capture and IV accumulation, but WEP should never be accepted as a production control.

## How it works

WEP failure has **4 core mechanics**:

1. **Shared static key.** Clients and APs use the same long-lived secret.
2. **Small IV space.** Initialization vectors repeat under traffic.
3. **Weak key scheduling.** RC4 usage leaks information when enough frames are captured.
4. **Offline recovery.** Captured frames can be analyzed without interacting with the AP after collection.

The bug is not "the password is weak." WEP's construction is weak even before user password quality is considered.

A worked example, WEP as migration finding:

```
Observation:
  warehouse-legacy SSID advertises WEP

Business reason:
  old handheld scanner cannot join WPA2

Network placement:
  same VLAN can reach inventory database

Compensating control:
  none; no client isolation or firewall restriction

Decision:
  critical migration issue: replace/bridge scanner and isolate legacy network until removal
```

For WEP, the mature output is a removal plan, not a stronger WEP setting.

## Techniques / patterns

Testing looks at:

- whether any AP advertises WEP or mixed legacy support
- IV count in captures
- whether client traffic naturally generates enough packets
- whether packet injection is being used in an authorized lab
- whether business-critical devices depend on legacy Wi-Fi

## Variants and bypasses

WEP risk has **3 common shapes**.

### 1. Static WEP

The classic broken deployment: one shared WEP key across clients.

### 2. Hidden legacy network

An old SSID remains active for printers, scanners, cameras, or industrial devices.

### 3. Migration exception

WEP remains because one legacy device blocks modernization.

## Impact

Ordered roughly by severity:

- **Network compromise.** Attackers can recover the key and join the LAN.
- **Traffic exposure.** Captured wireless traffic may be decrypted.
- **Lateral movement.** Joining a flat wireless network exposes internal services.
- **Compliance failure.** WEP is incompatible with modern security expectations.

## Detection and defense

Ordered by effectiveness:

1.
**Remove WEP completely.**
   There is no safe WEP configuration. Replacement is the real fix.

2.
**Replace or isolate legacy devices.**
   If a device cannot support modern Wi-Fi, isolate it behind a bridge, wired segment, or replacement plan.

3.
**Use WPA2/WPA3 with strong authentication.**
   Modern Wi-Fi security shifts risk away from broken protocol design toward credential and configuration quality.

4.
**Scan periodically for WEP beacons.**
   Wireless surveys catch forgotten APs and unmanaged devices.

### What does not work as a primary defense

- **Changing the WEP key occasionally.** The protocol remains broken.
- **Hiding the SSID.** WEP traffic still leaks enough signal for discovery and analysis.
- **MAC allowlists.** They do not fix encryption failure and can be bypassed.
- **Low transmit power alone.** Radio range is not a reliable security boundary.

## Practical labs

Use an intentionally built lab AP only.

### Identify WEP networks

```
sudo airodump-ng wlan0mon
```

Look for `ENC` values that indicate WEP.

### Capture IV growth

```
sudo airodump-ng --bssid LAB_BSSID --channel LAB_CH --write wep-lab wlan0mon
```

Track the `#Data` or IV count over time.

### Document migration blockers

```
SSID:
Device requiring WEP:
Business owner:
Replacement path:
Temporary isolation:
Deadline:
```

Treat WEP as a remediation planning problem, not a tuning problem.

### Check segmentation around legacy Wi-Fi

```
legacy SSID subnet:
reachable gateway:
reachable sensitive hosts:
firewall rule:
temporary exception owner:
```

If WEP cannot be removed immediately, segmentation becomes the emergency control.

### Verify removal readiness

```
replacement device tested:
WPA2/WPA3 supported:
old SSID shutdown date:
rollback owner:
post-shutdown scan:
```

The end state is no WEP beacon.

### Confirm no WEP after migration

```
sudo airodump-ng wlan0mon
```

After shutdown, the lab/office survey should show no WEP networks owned by you.

## Practical examples

- A warehouse scanner only supports WEP and keeps an old SSID alive.
- A lab router is configured with WEP to practice packet capture safely.
- A building survey finds an unmanaged AP broadcasting a legacy network.
- A printer network uses WEP because the original deployment was never revisited.
- A flat LAN lets WEP compromise become internal service access.

## Related notes

- [[wireless-security]]
- [[wifi-monitor-mode]]
- [[wifi-wordlist-attacks]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[internal-attack-surface|Internal Attack Surface]]

### Suggested future atomic notes

- legacy-protocol-risk
- wifi-migration-planning
- wireless-intrusion-detection
- radio-frequency-basics

## References

- **Official Tool Docs:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html
- **Official Tool Docs:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Mitigation:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
