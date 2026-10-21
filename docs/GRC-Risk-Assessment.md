# Information Security Risk Assessment & POA&M
## Home Lab Network Environment — Christopher D. Bias

**Assessment type:** Independent portfolio project (self-assessment of a personally owned home lab)
**Assessment period:** October 18–19, 2026 · **Report date:** October 19, 2026
**Framework:** NIST Cybersecurity Framework (CSF) 2.0, with risk terminology aligned to NIST SP 800-30 Rev. 1
**Assessor:** Christopher D. Bias — Security+ (2025), AWS Certified Cloud Practitioner

---

## 1. Executive Summary

This assessment evaluates the security posture of a home lab environment consisting of a single-server network-attached storage (NAS) system running 40+ containerized services, supporting media management, local AI inference, and personal data storage for a two-person household. The assessment identified **7 findings**: 4 have been remediated and verified, 3 remain open with planned remediations tracked in the POA&M (Section 5). No critical or high-risk findings remain open. The environment's strongest control is its network design: **no administrative interface is exposed to the public internet**; all remote access transits an encrypted peer-to-peer VPN (Tailscale).

## 2. Scope & Asset Inventory

**In scope:** NAS host, its containerized services, remote-access pathways, credential practices, backup posture, and the home LAN segment the host resides on.

| Asset | Description | Criticality |
|---|---|---|
| NAS host | Dell OptiPlex 9020 SFF, 16 GB RAM, 1 TB HDD, OpenMediaVault + Docker | High — single point of failure |
| Media stack | Jellyfin 10.11.8, Jellyseerr, Sonarr, Radarr, Lidarr, Prowlarr, Bazarr, qBittorrent | Medium |
| Personal services | Navidrome (music), Audiobookshelf (audiobooks/podcasts), Kiwix (offline reference) | Medium |
| Local AI services | Ollama (LLM inference, no API key), OpenClaw gateway (token-authenticated) | Medium |
| Data store | ~220 GB used of 901 GB; media library, configuration databases, documents | High — irreplaceable configs |
| Remote access | Tailscale tailnet (WireGuard); home LAN (private address space) | High — primary attack surface |
| Endpoints | Owner's Windows gaming PC (Ryzen 5 7500X3D), Android phone | Medium |

**Out of scope:** ISP infrastructure, third-party cloud services, other household members' personal devices.

## 3. Methodology

Assets were inventoried from live system inspection (container listings, mount tables, service configurations). Controls were mapped to NIST CSF 2.0 functions (Govern, Identify, Protect, Detect, Respond, Recover). Each finding was rated for likelihood and impact (Low / Moderate / High) considering the threat model of a residential environment: opportunistic internet scanning, credential stuffing against exposed services, and ransomware via compromised endpoints. Findings were validated by direct testing where feasible (authentication attempts, in-container visibility checks, database record counts), not by configuration review alone.

## 4. Control Highlights (verified in place)

- **PR.AA / PR.AC — Identity & access:** All media and automation services require authentication. A full credential reset of the primary media account was performed and *verified by sign-in test* (October 19). Administrative passwords are unique per system and are never stored in documentation or tickets.
- **PR.AC — Network segmentation by access path:** Remote administration is VPN-only (Tailscale). No port forwarding to administrative interfaces exists on the LAN gateway.
- **PR.AC — Download client hardening:** The torrent client's web interface, which shipped without a set password, was restricted to authenticated-subnet bypass limited to private (RFC1918) address ranges only, eliminating unauthenticated access from outside the trusted segments.
- **PR.DS — Configuration backup before change:** Every configuration modification during the assessment period was preceded by a dated backup (application settings files, subtitle-service config and database, audiobook-service database), enabling rollback for each change.
- **PR.IR — Change management:** A known-incompatible platform upgrade (media server major version 12.x, which breaks the request-management integration) was identified and explicitly deferred; the environment is pinned to the verified-compatible version.
- **GV.SC / ID.AM — Asset inventory correction:** Inspection discovered asset drift (a service configured against a placeholder storage path that did not correspond to any real volume) and an entire service running with zero configured libraries — both corrected and verified functional.

## 5. Findings & POA&M

| # | Weakness / Finding | CSF | Risk | Status | Remediation / Milestone |
|---|---|---|---|---|---|
| F-01 | Torrent client web UI had no password set; relied on per-restart temporary passwords in logs | PR.AA | Moderate | **Remediated & verified 2026-10-18** | Authentication bypass restricted to private subnets only; config backed up (`qBittorrent.conf.bak-2026-10-18`) |
| F-02 | Media server PIN-based password reset reported success but did not change the credential (verified by failed sign-in tests) | PR.AA | Moderate | **Remediated & verified 2026-10-19** | Credential reset via an alternate administrative path (temporary admin account, API-driven reset, temp account deleted); sign-in verified |
| F-03 | Service configured to a placeholder storage path (asset inventory drift); second service had no libraries defined | ID.AM | Low | **Remediated & verified 2026-10-19** | Bind-mount service created and enabled; libraries defined; end-to-end import tests passed with real content |
| F-04 | Read-only remount on one media bind did not persist (library mount writable at OS level; application itself never writes) | PR.AC | Low | **Open — accepted with monitoring** | Re-apply read-only bind or migrate the mount into the container definition at next maintenance window |
| F-05 | No offsite or offline backup of NAS data and configuration databases (single-disk host; backups reside on the same device) | PR.RC | **Moderate** | **Open** | Implement 3-2-1: scheduled config/database export to an external drive; evaluate encrypted cloud copy for configuration data only. Target: 2026-11-30 |
| F-06 | Single-host architecture: one CPU-bound server runs all services (availability risk; AI workloads saturate CPU) | PR.IR | Low | **Open — accepted** | Documented capacity limit (one AI session at a time); future mini-PC expansion already planned as the mitigation path |
| F-07 | No centralized log review; service logs are inspected manually per incident | DE.CM | Low | **Open** | Evaluate a lightweight log viewer container; until then, log checks are performed at every configuration change. Target: 2026-12-31 |

## 6. Risk Summary

| Rating | Open | Remediated this period |
|---|---|---|
| High | 0 | 0 |
| Moderate | 1 (F-05, offsite backup) | 2 (F-01, F-02) |
| Low | 3 (F-04, F-06, F-07) | 1 (F-03) |

**Overall residual risk: LOW–MODERATE**, driven almost entirely by the absence of an offsite backup (F-05) rather than by exposure: the environment presents no public administrative attack surface.

## 7. Skills Demonstrated (mapped to GRC analyst job requirements)

- Risk identification, analysis, and rating using NIST CSF 2.0 and SP 800-30 terminology
- POA&M creation and tracking, including milestones, acceptance decisions, and verification of remediation
- Control assessment by *testing* (authentication attempts, sign-in verification), not documentation review alone
- Asset inventory and configuration-drift detection
- Change management with pre-change backups, rollback paths, and compatibility-driven upgrade deferral
- Technical writing: findings stated with evidence, affected assets, and business impact

## 8. Evidence Index

- NAS Music & Audiobooks Setup Report (October 19, 2026) — service inventory, configuration changes, end-to-end test results
- Dated configuration backups retained on the NAS: media request settings (2026-10-19), subtitle service config + database (2026-10-19), audiobook database (2026-10-19), torrent client config (2026-10-18)
- Authentication and import verifications recorded in the same reports (sign-in tests, library record counts)

*This document describes a genuine self-assessment of the author's own systems. All findings, remediations, and dates are factual and drawn from the work recorded above.*
