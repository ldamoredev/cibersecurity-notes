# Reference Registry - Privacy, Anonymity & OPSEC

## Propósito

Esta nota estandariza las referencias para la rama Privacidad, Anonimato y OPSEC.

Usala para:
- mantener las notas de privacidad y anonimato vinculadas a fuentes oficiales, prácticas y de alta señal
- evitar el desvío hacia marketing de proveedores, listas de VPN y proliferación de rankings de herramientas
- evaluar afirmaciones a través de threat models, límites de confianza, metadatos y modos de falla operacionales
- ayudar a los agentes futuros a elegir referencias consistentes

## Regla de fuente de verdad

Para las notas bajo [[index|Privacy, Anonymity & OPSEC]], este registry es la fuente primaria de verdad.

Usalo junto con:
- [[reference-registry-networking|Reference Registry - Networking]]
- [[reference-registry-osint|Reference Registry - OSINT]]
- [[reference-registry-web-security|Reference Registry - Web Security]]
- [[reference-registry-devsecops|Reference Registry - DevSecOps]]

---

## Política de selección de referencias

### Prioridad de fuentes

1. estándares oficiales, documentación del proyecto y documentación del maintainer
2. guía de privacidad de la sociedad civil de organizaciones de alta confianza
3. documentación oficial de herramientas para verificación e inspección de metadatos
4. investigación de alta señal sobre límites del anonimato, fingerprinting del browser o desanonimización
5. fuentes de proveedores solo cuando explican su propia arquitectura o modelo de auditoría

### Objetivo por nota

- mínimo 2 referencias
- ideal 3 referencias
- máximo 5 referencias a menos que un tema genuinamente abarque varios sistemas independientes

### Etiquetado

Usar:
- **Fundamental**
- **Threat Model**
- **Docs Oficiales**
- **Testing / Lab**
- **Mitigación**
- **Investigación / Deep Dive**
- **Ética / Seguridad**

### Evitar

- rankings de "mejor VPN"
- páginas de reseñas con marketing de afiliados
- consejos genéricos de privacidad sin un threat model claro
- afirmaciones que traten "privado", "anónimo" y "cifrado" como sinónimos

---

# Mapa de temas

## privacy-vs-anonymity-vs-confidentiality

Referencias preferidas:
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Fundamental:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## metadata-and-identity-leakage

Referencias preferidas:
- **Fundamental:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** ExifTool documentation - https://exiftool.org/
- **Docs Oficiales:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/

## anonymity-threat-models

Referencias preferidas:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
- **Investigación / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf

## deanonymization-failures

Referencias preferidas:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Docs Oficiales:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
- **Investigación / Deep Dive:** Tor Project: Research safety board and research resources - https://research.torproject.org/

## tor-and-onion-services

Referencias preferidas:
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
- **Docs Oficiales:** Tor Browser: Onion Services - https://support.torproject.org/tor-browser/features/onion-services/
- **Investigación / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf

## tor-browser-security-settings

Referencias preferidas:
- **Docs Oficiales:** Tor Browser Security Levels - https://support.torproject.org/tor-browser/features/security-levels/
- **Docs Oficiales:** Tor Browser Fingerprinting Protections - https://support.torproject.org/tor-browser/features/fingerprinting-protections/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## tor-bridges-and-pluggable-transports

Referencias preferidas:
- **Docs Oficiales:** Tor Browser Censorship Circumvention - https://support.torproject.org/tor-browser/circumvention/
- **Docs Oficiales:** Tor: Using Bridges - https://support.torproject.org/little-t-tor/circumvention/using-bridges/
- **Investigación / Deep Dive:** Tor Project Anti-censorship - https://community.torproject.org/anti-censorship/

## vpn-threat-models

Referencias preferidas:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Fundamental:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework

## vpn-protocols

Referencias preferidas:
- **Docs Oficiales:** WireGuard - https://www.wireguard.com/
- **Docs Oficiales:** OpenVPN Community Documentation - https://openvpn.net/community-docs/
- **Docs Oficiales:** strongSwan documentation - https://docs.strongswan.org/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you

## vpn-logging-and-trust

Referencias preferidas:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## vpn-leakage-risks

Referencias preferidas:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Docs Oficiales:** ExifTool documentation - https://exiftool.org/

## vpn-kill-switches

Referencias preferidas:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** WireGuard - https://www.wireguard.com/
- **Docs Oficiales:** OpenVPN Community Resources - https://openvpn.net/community-resources/

## vpn-dns-and-ipv6-leaks

Referencias preferidas:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Fundamental:** [[dns-resolution|DNS Resolution]]
- **Fundamental:** [[dns-security|DNS Security]]
- **Docs Oficiales:** Tor Browser User Manual: Secure Connections - https://tb-manual.torproject.org/secure-connections/

## vpn-fingerprinting-limitations

Referencias preferidas:
- **Docs Oficiales:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## vpn-vs-tor

Referencias preferidas:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
- **Docs Oficiales:** Tor Project Support: Tor Browser with VPN - https://support.torproject.org/tor-browser/general/vpn-with-tor/

## vpn-with-tor

Referencias preferidas:
- **Docs Oficiales:** Tor Project Support: Tor Browser with VPN - https://support.torproject.org/tor-browser/general/vpn-with-tor/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/

## corporate-vpns-vs-consumer-vpns

Referencias preferidas:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Fundamental:** NIST Zero Trust Architecture SP 800-207 - https://csrc.nist.gov/pubs/sp/800/207/final
- **Fundamental:** CISA Zero Trust Maturity Model - https://www.cisa.gov/zero-trust-maturity-model

## tails-operational-model

Referencias preferidas:
- **Docs Oficiales:** Tails documentation - https://tails.net/doc/
- **Docs Oficiales:** Tails: warnings - https://tails.net/doc/about/warnings/
- **Docs Oficiales:** Tor Browser User Manual - https://tb-manual.torproject.org/

## qubes-compartmentalization

Referencias preferidas:
- **Docs Oficiales:** Qubes OS documentation - https://doc.qubes-os.org/en/latest/
- **Docs Oficiales:** Qubes OS architecture - https://doc.qubes-os.org/en/latest/developer/system/architecture.html
- **Threat Model:** Qubes OS security design goals - https://doc.qubes-os.org/en/latest/developer/system/security-design-goals.html

## whonix-gateway

Referencias preferidas:
- **Docs Oficiales:** Whonix documentation - https://www.whonix.org/wiki/Documentation
- **Docs Oficiales:** Whonix Gateway - https://www.whonix.org/wiki/Whonix-Gateway
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/

## private-email-threat-models

Referencias preferidas:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Docs Oficiales:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/

## temporary-email-risks

Referencias preferidas:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## xmpp-and-private-messaging

Referencias preferidas:
- **Docs Oficiales:** XMPP Standards Foundation - https://xmpp.org/
- **Docs Oficiales:** OMEMO XEP-0384 - https://xmpp.org/extensions/xep-0384.html
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## end-to-end-encryption

Referencias preferidas:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Investigación / Deep Dive:** Signal Protocol documentation - https://signal.org/docs/

## pgp-encryption-and-signatures

Referencias preferidas:
- **Docs Oficiales:** GnuPG Manual - https://gnupg.org/documentation/manuals/gnupg/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Docs Oficiales:** OpenPGP RFC 9580 - https://www.rfc-editor.org/rfc/rfc9580

## file-metadata-removal

Referencias preferidas:
- **Docs Oficiales:** ExifTool documentation - https://exiftool.org/
- **Docs Oficiales:** Tails: Removing metadata from files - https://tails.net/doc/sensitive_documents/metadata/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## secure-file-sharing

Referencias preferidas:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Docs Oficiales:** OnionShare documentation - https://docs.onionshare.org/

## secure-deletion-and-storage-wiping

Referencias preferidas:
- **Docs Oficiales:** Tails: secure deletion - https://tails.net/doc/encryption_and_privacy/secure_deletion/
- **Docs Oficiales:** NIST SP 800-88 Rev. 1 - https://csrc.nist.gov/publications/detail/sp/800-88/rev-1/final
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## opsec-failure-chains

Referencias preferidas:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Docs Oficiales:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/

## browser-fingerprinting

Referencias preferidas:
- **Docs Oficiales:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## account-correlation

Referencias preferidas:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Docs Oficiales:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## traffic-correlation

Referencias preferidas:
- **Investigación / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf
- **Docs Oficiales:** Tor Project Support - https://support.torproject.org/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

---

## Reglas de uso del registry

- Elegir el conjunto de referencias más pequeño que soporte la nota exacta.
- Preferir docs oficiales del proyecto para el comportamiento de herramientas y EFF/NIST/OWASP para el encuadre del threat model.
- No citar marketing de proveedores de VPN como evidencia para afirmaciones generales sobre VPN.
- Cuando se discuten afirmaciones de proveedores, etiquetarlas como afirmaciones y evaluarlas a través de auditorías, arquitectura, jurisdicción, incentivos e historial observado.
- Para notas que involucren personas, cuentas o datos personales sensibles, incluir una referencia de ética/seguridad y mantener los ejemplos defensivos.
