---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Linux Privilege Escalation

## Purpose

This note standardizes references for the linux-privilege-escalation branch.

Use it to:
- keep host privesc notes tied to strong Linux and tool references
- avoid random checklist sprawl
- separate authorized lab practice from unsafe activity
- help future agents choose consistent references

## Source of truth rule

For linux-privilege-escalation notes, this registry is the primary source of truth.

Use it together with:
- [[index|Linux Privilege Escalation Index]]
- [[index|Offensive Security / Recon Index]]
- [[index|Security Playbooks Index]]

---

## Reference selection policy

### Source priority

1. official Linux, sudo, systemd, and project documentation
2. official tool documentation
3. high-signal training/checklist material
4. curated technique databases
5. secondary sources only when clearly useful

### Per-note target

- minimum 2 references
- ideal 3 references
- avoid long reference lists in atomic notes

### Labeling

Use:
- **Foundational**
- **Official Docs**
- **Testing / Lab**
- **Technique Reference**
- **Research / Deep Dive**
- **Mitigation**

---

# Linux privilege escalation topic map

## linux-privilege-escalation

Preferred references:
- **Technique Reference:** GTFOBins — https://gtfobins.github.io/
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html

## linux-enumeration

Preferred references:
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/
- **Official Docs:** proc filesystem — https://man7.org/linux/man-pages/man5/proc.5.html
- **Official Docs:** systemd service units — https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html

## suid-sgid-misconfigurations

Preferred references:
- **Technique Reference:** GTFOBins: SUID — https://gtfobins.github.io/#+suid
- **Official Docs:** chmod — https://man7.org/linux/man-pages/man1/chmod.1.html
- **Testing / Lab:** HackTricks SUID — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#sudo-and-suid

## sudo-misconfigurations

Preferred references:
- **Official Docs:** sudoers manual — https://www.sudo.ws/docs/man/sudoers.man/
- **Technique Reference:** GTFOBins: sudo — https://gtfobins.github.io/#+sudo
- **Official Docs:** sudo manual — https://www.sudo.ws/docs/man/sudo.man/

## linux-capabilities

Preferred references:
- **Official Docs:** Linux capabilities — https://man7.org/linux/man-pages/man7/capabilities.7.html
- **Official Docs:** setcap — https://man7.org/linux/man-pages/man8/setcap.8.html
- **Technique Reference:** GTFOBins: capabilities — https://gtfobins.github.io/#+capabilities

## cron-and-timer-abuse

Preferred references:
- **Official Docs:** crontab file format — https://man7.org/linux/man-pages/man5/crontab.5.html
- **Official Docs:** systemd timers — https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
- **Official Docs:** systemd service units — https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html

## path-hijacking

Preferred references:
- **Official Docs:** Bash command search and execution — https://www.gnu.org/software/bash/manual/bash.html#Command-Search-and-Execution
- **Official Docs:** ld.so dynamic linker — https://man7.org/linux/man-pages/man8/ld.so.8.html
- **Testing / Lab:** PayloadsAllTheThings: Linux Privilege Escalation — https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/linux-privilege-escalation/

## kernel-exploit-triage

Preferred references:
- **Official Docs:** Linux kernel security bugs — https://www.kernel.org/doc/html/latest/admin-guide/security-bugs.html
- **Official Docs:** uname — https://man7.org/linux/man-pages/man1/uname.1.html
- **Research / Deep Dive:** MITRE ATT&CK Privilege Escalation — https://attack.mitre.org/tactics/TA0004/

## linpeas-workflow

Preferred references:
- **Official Tool Docs:** PEASS-ng / LinPEAS — https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS
- **Testing / Lab:** HackTricks Linux Privilege Escalation — https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html
- **Technique Reference:** GTFOBins — https://gtfobins.github.io/

---

## Registry usage rules

- Use active exploitation only in owned labs, CTFs, or explicitly authorized hosts.
- Prefer enumeration, evidence, and remediation framing before exploit execution.
- Do not treat automated scripts as the source of truth; use them to prioritize manual verification.
- Kernel exploit notes must emphasize patching, version validation, snapshotting, and crash risk.
- Keep web initial access, cloud access paths, and recon in their existing branches; this branch starts after a local Linux foothold exists.
