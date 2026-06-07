# Reference Registry — Wireless Security

## Propósito

Esta nota estandariza las referencias para la rama wireless-security.

Usala para:
- mantener las notas wireless vinculadas a fuentes oficiales, prácticas y de alta señal
- evitar convertir la rama en una lista random de herramientas
- preservar el límite entre trabajo de lab autorizado y actividad insegura
- ayudar a agentes futuros a elegir referencias consistentes

## Regla de fuente de verdad

Para notas wireless-security, este registry es la fuente de verdad primaria.

Usalo junto con:
- [[index|Wireless Security Index]]
- [[index|Networking Index]]
- [[index|Offensive Security / Recon Index]]

---

## Política de selección de referencias

### Prioridad de fuentes

1. estándares oficiales, vendor docs y documentación de proyecto
2. documentación oficial de herramientas
3. documentación práctica de packet-analysis
4. investigación de seguridad de alta señal
5. fuentes secundarias solo cuando agregan valor claro

### Target por nota

- mínimo 2 referencias
- ideal 3 referencias
- evitar listas largas de referencias en notas atómicas

### Etiquetas

Usar:
- **Fundamental**
- **Docs oficiales de herramienta**
- **Testing / Lab**
- **Investigación / Deep Dive**
- **Mitigación**

---

# Mapa de temas wireless

## wireless-security

Referencias preferidas:
- **Fundamental:** Wi-Fi Alliance WPA3 — https://www.wi-fi.org/discover-wi-fi/security
- **Docs oficiales de herramienta:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
- **Docs oficiales de herramienta:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html

## wifi-monitor-mode

Referencias preferidas:
- **Docs oficiales de herramienta:** Aircrack-ng airmon-ng — https://www.aircrack-ng.org/doku.php?id=airmon-ng
- **Docs oficiales de herramienta:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
- **Docs oficiales de herramienta:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng

## wifi-deauthentication

Referencias preferidas:
- **Docs oficiales de herramienta:** Aircrack-ng aireplay-ng — https://www.aircrack-ng.org/doku.php?id=aireplay-ng
- **Docs oficiales de herramienta:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Mitigación:** Wi-Fi Alliance WPA3 / Protected Management Frames context — https://www.wi-fi.org/discover-wi-fi/security

## wep-security

Referencias preferidas:
- **Docs oficiales de herramienta:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html
- **Docs oficiales de herramienta:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Mitigación:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security

## wpa-wpa2-handshakes

Referencias preferidas:
- **Docs oficiales de herramienta:** Aircrack-ng WPA/WPA2 tutorial — https://www.aircrack-ng.org/doku.php?id=cracking_wpa
- **Docs oficiales de herramienta:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Fundamental:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security

## wifi-wordlist-attacks

Referencias preferidas:
- **Docs oficiales de herramienta:** Aircrack-ng WPA/WPA2 tutorial — https://www.aircrack-ng.org/doku.php?id=cracking_wpa
- **Docs oficiales de herramienta:** Hashcat example hashes — https://hashcat.net/wiki/doku.php?id=example_hashes
- **Mitigación:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security

## evil-twin-access-points

Referencias preferidas:
- **Docs oficiales de herramienta:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Docs oficiales de herramienta:** Aircrack-ng airbase-ng — https://www.aircrack-ng.org/doku.php?id=airbase-ng
- **Mitigación:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security

## arp-poisoning

Referencias preferidas:
- **Docs oficiales de herramienta:** bettercap ARP spoofing module — https://www.bettercap.org/modules/ethernet/spoofers/arpspoof/
- **Docs oficiales de herramienta:** Wireshark User's Guide — https://www.wireshark.org/docs/wsug_html/
- **Fundamental:** RFC 826 (Address Resolution Protocol) — https://datatracker.ietf.org/doc/html/rfc826

## mitm-on-local-networks

Referencias preferidas:
- **Docs oficiales de herramienta:** bettercap documentation — https://www.bettercap.org/
- **Docs oficiales de herramienta:** Wireshark User's Guide — https://www.wireshark.org/docs/wsug_html/
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## bettercap-workflows

Referencias preferidas:
- **Docs oficiales de herramienta:** bettercap documentation — https://www.bettercap.org/
- **Docs oficiales de herramienta:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Docs oficiales de herramienta:** bettercap ARP spoofing module — https://www.bettercap.org/modules/ethernet/spoofers/arpspoof/

---

## Reglas de uso del registry

- Usá tooling de ataque activo solo en notas que nombren explícitamente un lab propio o un límite de autorización escrito.
- Preferí labs de capture, observación y validación defensiva antes que labs disruptivos.
- Mantené la mecánica de radio Wi-Fi en esta rama y la mecánica genérica TCP/IP en [[index]].
- Mantené robo de credenciales y mecánicas de phishing fuera de notas wireless salvo que la nota sea explícitamente defensiva y apunte a controles de social-engineering.
