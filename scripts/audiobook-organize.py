#!/usr/bin/env python3
"""Audiobook organizer: copies completed 'audiobooks'-category torrents from
qBittorrent's downloads into the Audiobookshelf library folder.
Copies (never moves) so seeding is undisturbed. Marker files prevent duplicates.
Audiobookshelf's folder watcher indexes new files automatically."""
import json, subprocess, os, shutil, zipfile

LIB = "/data/media/audiobooks"
MARK = "~/scripts/organized-markers"
AUDIO = {".mp3", ".m4a", ".m4b", ".ogg", ".opus", ".flac", ".wav"}

def qget(path):
    r = subprocess.run(["docker", "exec", "sonarr", "curl", "-s", "--max-time", "20",
                        "http://qbittorrent:8080" + path], capture_output=True, text=True)
    return json.loads(r.stdout)

def extract_audio(src, dest):
    n = 0
    ext = os.path.splitext(src)[1].lower()
    if ext in AUDIO:
        shutil.copy2(src, os.path.join(dest, os.path.basename(src))); n += 1
    elif ext == ".zip":
        with zipfile.ZipFile(src) as z:
            for m in z.namelist():
                if os.path.splitext(m)[1].lower() in AUDIO:
                    with open(os.path.join(dest, os.path.basename(m)), "wb") as fh:
                        fh.write(z.read(m))
                    n += 1
    return n

def main():
    os.makedirs(MARK, exist_ok=True)
    for t in qget("/api/v2/torrents/info?category=audiobooks"):
        if t.get("progress", 0) < 1:
            continue
        h, name = t["hash"], t["name"]
        if os.path.exists(os.path.join(MARK, h)):
            continue
        host = "/data/media" + t["content_path"]
        dest = os.path.join(LIB, name)
        os.makedirs(dest, exist_ok=True)
        moved = 0
        if os.path.isdir(host):
            for root, _, files in os.walk(host):
                for f in files:
                    moved += extract_audio(os.path.join(root, f), dest)
        elif os.path.isfile(host):
            moved += extract_audio(host, dest)
        if moved:
            open(os.path.join(MARK, h), "w").write(name)
            print(f"organized: {name} ({moved} audio file(s))", flush=True)
        else:
            print(f"no audio files yet in {name}; will retry", flush=True)

if __name__ == "__main__":
    main()
