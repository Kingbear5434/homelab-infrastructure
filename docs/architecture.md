# Architecture Notes

Design decisions behind the home lab, and the reasoning that produced them. Everything here describes the *shape* of the environment; live addresses, credentials, and versions are deliberately not published.

## Platform

- **Host**: one small-form-factor desktop (quad-core, 16 GB RAM, single 1 TB HDD) running Debian with Docker. The hardware constraint is a design input, not an accident: CPU-bound services (transcoding, LLM inference) are used sparingly and scheduled, not left to fight over the disk.
- **Services run as containers**, one compose project per service or stack, `restart: unless-stopped` everywhere so the environment self-recovers from power events.
- **Storage layout**: a single media tree (`/data/media/{tv,movies,music,audiobooks,books,games,downloads}`) mounted into every container that needs it. Mounting the *parent* tree (rather than per-folder binds) is what lets the download → manager → player pipeline use **hardlinks**: the same file appears in the library instantly, with no second copy and no waiting on a 1 TB HDD to duplicate gigabytes.

## Networking

- Two container networking patterns: a shared "media stack" network for the automation pipeline (so Sonarr/Radarr/Lidarr/Listenarr/Mylar can reach the download client and indexer manager by container name), and the default bridge for everything else.
- **Nothing is exposed to the internet.** No router port-forwards exist for these services; this was verified by an external reachability test from a second network. Remote access is Tailscale only (a WireGuard mesh) — the administrative attack surface from the public internet is zero.
- **Internal PKI**: a small internal CA ("Home CA") issues a wildcard certificate for the internal domain; the reverse proxy terminates TLS for friendly internal names (`jellyfin.home.lan`, etc.). Devices import the CA once; after that the whole environment is HTTPS internally with no browser warnings.
- **DNS**: AdGuard Home on the host answers internal names and provides network-wide ad filtering upstream — clients use it as their only resolver on the LAN.

## Automation pipeline (media)

```
                 ┌────────────┐
   indexers ───► │  Prowlarr  │  (one place to configure sources;
                 └─────┬──────┘   apps sync from it automatically)
        ┌────────┬─────┼──────────┬───────────┐
     Sonarr   Radarr  Lidarr   Listenarr    Mylar3
        └────────┴─────┴────┬─────┴───────────┘
                     ┌──────▼───────┐
                     │ qBittorrent  │  (per-app categories keep
                     └──────┬───────┘   pipelines from colliding)
                     ┌──────▼───────┐
                     │  /data/media │  hardlink imports
                     └──────┬───────┘
        ┌──────────┬────────┼──────────┐
    Jellyfin   Navidrome  Audiobook-  Kavita
                          shelf
```

Key decisions:
- **Prowlarr is the single source of indexer truth.** Managers never get indexer credentials directly; they sync from Prowlarr, so adding/removing a source happens once.
- **Per-application download categories** (e.g. `audiobooks`, `listenarr`) mean two pipelines can never fight over the same completed download.
- **Completed downloads are never auto-deleted** by the managers. Cleanup is a human decision; storage is monitored instead (drive at ~45% with headroom alerts).
- **Folder watchers over polling**: players (Audiobookshelf, Kavita) watch the library folders, so an import appears on the shelf within seconds with no scheduled scans to babysit.

## Security posture

- One standardized admin identity across services; every default/vendor credential found was replaced (a dedicated sweep: password managers, dashboards, ebook servers, monitoring) and each change verified with a real sign-in.
- Inter-service API keys are read into shell variables at use time and are **never written to notes, scripts, or documentation** — a rule that exists because an early config file briefly held one, which became a finding in the risk assessment.
- Configuration backups precede every change (`/compose/backups/<task>-<date>/`), and databases are backed up with their engines' consistent-dump methods (e.g. SQLite `.backup`), then integrity-checked.
- SMART health (Scrutiny) and availability monitoring (Uptime Kuma) run continuously; the single HDD is the known weakest link — see the assessment's availability finding and its accepted-risk note. Backups currently live on the same disk (protects against corruption and bad changes, not drive death); an off-box copy target is the documented next step.

## AI services

- **Ollama** serves local models (4B/8B class) from the same host — roughly 9 tokens/sec on CPU for the small model, which is adequate for single-user agent workloads if you respect one rule learned the hard way: **one model at a time on 16 GB RAM**, behind a queue.
- An agent gateway (OpenClaw) and workflow engine (n8n) sit on top for home automation experiments. All inference is local — no prompts or media leave the house.

## Lessons that generalize

1. A settings page claiming "saved" proves nothing — **verify by reading back the effective state and testing the real operation** (an actual login, an actual stream).
2. Apps that share a library folder must agree on *paths inside their own mounts*; "same folder" has to be checked from inside each container, not from the host.
3. Subnet-whitelist authentication bypasses behave differently through published ports vs. container networks — test the exact path the client will use.
4. Small disks punish copy-based pipelines; hardlinks and a shared parent mount are the fix.
5. The most valuable security control in a home lab is the boring one: an inventory. You cannot harden services you've forgotten exist — the dashboard's service list became the audit checklist.
