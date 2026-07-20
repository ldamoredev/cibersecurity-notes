---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Bettercap Workflows

## Definition

Bettercap workflows are controlled lab procedures that use bettercap modules for network discovery, Wi-Fi observation, ARP spoofing, and local-network MITM validation.

## Why it matters

Bettercap is powerful because it combines discovery, spoofing, Wi-Fi operations, and traffic inspection in one console. That same power makes boundaries essential.

In this atlas, bettercap should be treated as an authorized-lab workflow tool, not as a generic "run this on a network" command.

## How it works

Bettercap use has **5 workflow steps**:

1. **Define scope.** Choose owned interfaces, APs, clients, and subnets.
2. **Start passively.** Discover hosts, APs, clients, and traffic before changing anything.
3. **Enable one module at a time.** Avoid stacking effects that confuse evidence.
4. **Capture evidence.** Record commands, timestamps, pcaps, and observed changes.
5. **Stop and restore.** Disable modules and verify normal network state.

The risk is not the tool itself. The risk is running active modules without scope, evidence, or rollback.

A worked example, safe bettercap workflow:

```
Question:
  does guest Wi-Fi client isolation block ARP-based MITM?

Scope:
  owned AP, owned victim laptop, owned tester laptop, one subnet

Passive step:
  net.show confirms only lab devices are targeted

Active step:
  enable arp.spoof against the single victim for 60 seconds

Evidence:
  victim ARP table, Wireshark pcap, connectivity result

Rollback:
  stop module, renew victim network state, confirm gateway MAC restored
```

Bettercap maturity is disciplined module control and evidence, not more modules.

## Techniques / patterns

Bettercap workflows commonly touch:

- `net.probe` and `net.show` for local host discovery
- `wifi.recon` and `wifi.show` for wireless visibility
- `arp.spoof` for local MITM validation
- packet capture for evidence
- module parameters for narrowing targets

## Variants and bypasses

Bettercap has **4 useful workflow modes**.

### 1. Passive inventory

Discover hosts or wireless stations without disrupting them.

### 2. Wireless recon

Observe APs, clients, channels, and security modes.

### 3. Controlled ARP spoof lab

Test whether client isolation and TLS controls resist local MITM.

### 4. Rogue AP awareness lab

Demonstrate SSID trust risk without collecting real credentials.

## Impact

Ordered roughly by severity:

- **Evidence consolidation.** One console can gather network and wireless context.
- **Control validation.** Labs can prove whether isolation, PMF, and TLS work.
- **Accidental disruption.** Active modules can disconnect clients or alter traffic.
- **Unsafe overreach.** Broad targeting can affect devices outside authorization.

## Detection and defense

Ordered by effectiveness:

1.
**Write a scope block before running active modules.**
   Explicit BSSID, client, subnet, and stop conditions prevent accidental expansion.

2.
**Prefer passive modules first.**
   Observation creates a baseline and often answers the question without active interference.

3.
**Target narrowly.**
   Module filters and explicit targets reduce collateral effects.

4.
**Keep pcaps and command logs.**
   Reproducible evidence is more valuable than a dramatic console screenshot.

5.
**Verify restoration.**
   After spoofing or Wi-Fi tests, confirm clients reconnect and ARP/gateway state returns to normal.

### What does not work as a primary defense

- **Running every module at once.** Mixed effects make results hard to trust.
- **Using bettercap output as the only evidence.** Validate with pcaps, device logs, or independent checks.
- **Assuming a lab command is safe on a production network.** Wireless and MITM modules can be disruptive.
- **Leaving active modules running.** Persistent spoofing or deauth can create outages.

## Practical labs

Use an isolated lab network.

### Passive local inventory

```
sudo bettercap -iface wlan0
net.probe on
net.show
```

Record discovered hosts and stop probing when the inventory is complete.

### Wireless recon baseline

```
sudo bettercap -iface wlan0
wifi.recon on
wifi.show
```

Use filters before any active Wi-Fi module.

### Scope block before active modules

```
Authorized interface:
Authorized subnet:
Authorized BSSID:
Authorized test client:
Active module:
Stop condition:
Rollback check:
```

Write this before running spoofing or disruption tests.

### Keep a module activity log

```
time | module | target | reason | expected effect | observed effect | stopped at
```

This makes active lab work reproducible and reviewable.

### Verify rollback after spoofing

```
arp.spoof stopped:
victim gateway MAC restored:
DNS restored:
connectivity normal:
pcap saved:
```

Rollback evidence belongs in the lab result, not only in memory.

## Practical examples

- A lab validates that guest clients cannot ARP-spoof one another.
- A Wi-Fi survey lists nearby APs and flags duplicate SSIDs.
- A Bettercap capture supports a report with timestamps and pcaps.
- A tester narrows a module to one owned BSSID instead of all visible networks.
- A cleanup check confirms ARP entries returned to the real gateway MAC.

## Related notes

- [[wireless-security]]
- [[wifi-monitor-mode]]
- [[arp-poisoning]]
- [[mitm-on-local-networks]]
- [[packet-analysis|Packet Analysis]]

### Suggested future atomic notes

- bettercap-caplets
- network-lab-scope-blocks
- dns-spoofing-on-local-networks
- wireless-intrusion-detection

## References

- **Official Tool Docs:** bettercap documentation — https://www.bettercap.org/
- **Official Tool Docs:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Official Tool Docs:** bettercap ARP spoofing module — https://www.bettercap.org/modules/ethernet/spoofers/arpspoof/
