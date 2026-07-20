---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Wi-Fi Monitor Mode

## Definition

Wi-Fi monitor mode is an adapter mode that captures raw 802.11 frames from the air instead of only traffic addressed to the local client after association.

## Why it matters

Monitor mode is the foundation of practical wireless security work. Without it, the tester sees the network as a normal client. With it, the tester can observe beacons, probes, clients, channels, handshakes, and management behavior.

The key boundary: monitor mode is observation. Packet injection and disruption are separate capabilities that require tighter authorization.

## How it works

Monitor-mode workflow has **5 steps**:

1. **Choose compatible hardware.** The adapter and driver must support monitor mode.
2. **Stop conflicting managers.** Network managers may keep the card in managed mode.
3. **Enable monitor mode.** The interface changes from client association to frame capture.
4. **Select channels or hop.** Captures are channel-sensitive.
5. **Record frames.** Tools save pcap/csv evidence for later analysis.

The mechanism is not IP sniffing. It is 802.11 frame capture before normal LAN traffic is available.

A worked example, capture quality decision:

```
Goal:
  capture frames for lab-ap on channel 6

Adapter state:
  wlan0mon reports monitor mode

Capture:
  beacons visible, client probes visible, no EAPOL during first 2 minutes

Adjustment:
  lock to channel 6 and reconnect owned test client

Decision:
  first capture proves AP visibility, not handshake presence; second capture is needed for WPA analysis
```

Monitor-mode evidence should state what was visible, what was missing, and why.

## Techniques / patterns

Look for:

- adapter chipset and driver support
- interface state before and after monitor mode
- channel hopping versus fixed-channel capture
- beacon, probe, data, EAPOL, and PMKID indicators
- pcap evidence that can be reopened in Wireshark

## Variants and bypasses

Monitor-mode work has **4 common pitfalls**.

### 1. Managed mode mistaken for monitor mode

The adapter may still be associated as a client and miss raw frames.

### 2. Wrong channel

A fixed-channel capture misses APs or handshakes on other channels.

### 3. Driver instability

Some adapters appear to support monitor mode but drop frames or fail injection tests.

### 4. Overlapping processes

NetworkManager, wpa_supplicant, or vendor tools can reset the interface while tests run.

## Impact

Ordered roughly by severity:

- **Evidence quality.** Good captures support accurate wireless triage.
- **Handshake analysis.** WPA/WPA2 testing depends on capturing the right frame material.
- **Rogue AP detection.** Beacon and probe visibility exposes lookalikes.
- **Operational reliability.** Bad adapter state creates false negatives.

## Detection and defense

Ordered by effectiveness:

1.
**Treat monitor mode as a lab prerequisite, not a finding.**
   A tester's ability to capture frames says the radio medium is observable; it does not prove compromise.

2.
**Verify captures in Wireshark.**
   Reopening pcaps catches empty captures, wrong channels, and missing frame classes.

3.
**Document channel, adapter, driver, and location.**
   Wireless evidence changes with physical position and hardware, so context matters.

4.
**Use passive capture first.**
   Passive observation reduces risk and builds a baseline before disruptive tests.

### What does not work as a primary defense

- **Assuming encryption hides metadata.** Beacons, BSSIDs, channels, and many management frames remain observable.
- **Assuming no visible clients means no risk.** Capture timing and channel selection can miss clients.
- **Treating monitor mode as authorization for injection.** Observation and active frame injection are different activities.

## Practical labs

Use an owned adapter and lab network.

### Enable monitor mode

```
ip link
sudo airmon-ng check
sudo airmon-ng start wlan0
iw dev
```

Confirm the new interface is actually in monitor mode.

### Capture a channel baseline

```
sudo airodump-ng wlan0mon
```

Record nearby SSIDs, BSSIDs, channels, encryption, and RSSI.

### Save a pcap for Wireshark

```
sudo airodump-ng --write lab-capture --output-format pcap wlan0mon
wireshark lab-capture-01.cap
```

Check whether frames and channels match expectations.

### Record capture conditions

```
adapter:
driver:
interface:
channel:
distance:
AP BSSID:
client present:
frame types seen:
```

Wireless evidence depends on physical and driver context.

### Verify EAPOL visibility

```
Wireshark filter: eapol
Expected: reconnect from owned client
Observed:
Complete enough for analysis:
```

Do not assume a pcap contains handshake material until inspected.

### Compare channel hop and fixed channel captures

```
Mode: channel hop
Beacons seen:
Clients seen:
EAPOL seen:

Mode: fixed channel:
Beacons seen:
Clients seen:
EAPOL seen:
```

Use channel hopping for discovery, then fixed-channel capture for evidence quality.

## Practical examples

- A tester sees beacons but no clients because the capture window is too short.
- A lab AP is missed because the adapter is locked to the wrong channel.
- A pcap contains EAPOL frames that support WPA handshake analysis.
- A laptop's internal Wi-Fi card supports managed mode but not monitor mode.
- NetworkManager resets the interface during a capture.

## Related notes

- [[wireless-security]]
- [[wpa-wpa2-handshakes]]
- [[wifi-deauthentication]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[packet-analysis|Packet Analysis]]

### Suggested future atomic notes

- wifi-channel-and-band-planning
- adapter-chipsets-for-wireless-testing
- 80211-frame-types
- radiotap-headers

## References

- **Official Tool Docs:** Aircrack-ng airmon-ng — https://www.aircrack-ng.org/doku.php?id=airmon-ng
- **Official Tool Docs:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Official Tool Docs:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
