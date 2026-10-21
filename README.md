# Home Lab — Self-Hosted Infrastructure & Media Automation

A production-style home lab designed, built, and operated by one person: 51 containerized services on a single OpenMediaVault host (Debian 13, Docker), run with enterprise habits — configuration backups before every change, standardized authentication, health and disk monitoring, documented recovery procedures, and **zero services exposed to the public internet**.

This repository is the portfolio version of that environment: architecture notes, a formal risk assessment, sanitized configuration templates, and the automation scripts that keep it running.

## What this demonstrates

- **Linux systems administration** — Debian host, Docker/Docker Compose, systemd timers, SSH administration, file permissions and service accounts
- **Container orchestration at household scale** — 51 services across shared container networks, with deliberate choices about which services may talk to each other
- **Networking & TLS** — reverse proxy with an internal certificate authority, split-horizon DNS, remote access exclusively over a WireGuard-based mesh VPN (Tailscale)
- **Media automation pipelines** — indexer management (Prowlarr) feeding TV/movie/music/comics/audiobook managers, a shared download client, and player servers, with hardlink-based imports that avoid duplicate storage
- **Governance, risk & compliance** — a NIST CSF 2.0 risk assessment of this very environment, with findings tracked through a POA&M to remediation and verification ([docs/GRC-Risk-Assessment.md](docs/GRC-Risk-Assessment.md))
- **Backup & recovery** — pre-change configuration backups for every service, database integrity verification, documented restore procedures, SMART disk-health monitoring
- **Scripting & automation** — Python automation for media ingestion (see `scripts/`), plus workflow automation and a local LLM stack (Ollama) for private AI services

## Architecture at a glance

- **Host**: a Dell OptiPlex 9020 small-form-factor PC (16 GB RAM) running OpenMediaVault on Debian 13 with Docker 29 — 51 containers on one data volume shared by all media services so files can be hardlinked between download, management, and player layers without duplication.
- **Access planes**: services are reachable on the home LAN and, remotely, only through Tailscale. Nothing is port-forwarded or published; an external reachability test from outside the network confirmed no service is reachable from the internet.
- **Internal naming & TLS**: an internal CA issues certificates for `*.home.lan` names behind the reverse proxy; a local DNS resolver (AdGuard Home) answers those names on the LAN.
- **Authentication**: every service uses one standardized admin identity; default vendor credentials were hunted down and replaced; sign-in is verified by actual login tests, not assumed.
- **Monitoring**: Uptime Kuma for service availability, Scrutiny for SMART drive health, Watchtower in monitor-only mode (it reports available image updates; it never auto-applies them), and a single dashboard (Homepage, 37 service tiles) tying the environment together.

Details and design trade-offs: [docs/architecture.md](docs/architecture.md).

## The media pipeline

One automated chain handles acquisition end to end:

- **Indexing** — Prowlarr manages 14 indexers and syncs them to the library managers: Sonarr (TV), Radarr (movies), Lidarr (music), Mylar3 (comics).
- **Download** — every manager hands off to one shared download client (qBittorrent). Remote path mappings translate file paths between containers, so completed downloads import cleanly instead of failing on mismatched mount points.
- **Library & playback** — finished items are hardlinked into a single shared media tree (no duplicate copies): Jellyfin serves video (with the JellySkin theme) and Jellyseerr handles requests; Listenarr feeds audiobooks into Audiobookshelf; Mylar3 feeds comics into Kavita; Navidrome serves music.
- **Offline knowledge** — Kiwix serves a complete text-only Wikipedia snapshot locally, no internet required.

## Service inventory (by function)

| Area | Services |
|---|---|
| Media players | Jellyfin, Jellyseerr (requests), Navidrome (music), Audiobookshelf (audiobooks/podcasts), Kavita (comics/ebooks) |
| Media automation | Prowlarr (indexers), Sonarr, Radarr, Lidarr, Mylar3 (comics), Listenarr (audiobooks), qBittorrent (downloads), Bazarr (subtitles), HandBrake (transcoding) |
| Files & photos | Nextcloud, Immich, Paperless-ngx, Syncthing |
| Knowledge & life | BookStack, Joplin Server, Mealie, Actual Budget, Calibre-Web-Automated, Kiwix (offline Wikipedia) |
| Infrastructure | Nginx Proxy Manager, AdGuard Home, Portainer, Homepage |
| Monitoring & health | Uptime Kuma, Scrutiny, Dozzle, Watchtower (monitor-only) |
| AI (local, private) | Ollama (local LLM inference — Qwen3 4B and 8B models), OpenClaw agent gateway, n8n workflows |
| Security & backup | Vaultwarden, Kopia |

## Repository layout

- `docs/GRC-Risk-Assessment.md` — NIST CSF 2.0 assessment of this environment with a POA&M tracking 7 findings through remediation
- `docs/architecture.md` — design decisions, network posture, backup strategy, and lessons learned
- `compose-templates/` — sanitized Docker Compose templates for the core stacks (media automation, audiobooks, monitoring)
- `scripts/` — automation scripts, including the audiobook ingestion organizer

## A note on what's *not* here

Configuration files in this repository are **templates written for publication**: all addresses, hostnames, usernames, keys, and tokens are placeholders. The live environment's real configuration is never committed anywhere public — publishing your own infrastructure's live config and credentials is itself a security finding (it was one in the assessment, in fact).

## Operating principles

1. Back up before you change anything; verify the backup opens.
2. One identity standard everywhere; no default passwords survive.
3. Nothing public, ever, unless the risk decision is made explicitly.
4. A change isn't done until it's verified working and written down.
5. Prefer the tool already running over installing a new one.
