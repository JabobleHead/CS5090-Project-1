"""Shallow-clone each repo in data/sources.txt at its pinned commit into data/raw/<name>."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def run(*a, cwd=None):
    subprocess.run(a, cwd=cwd, check=True)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    for line in (ROOT / "data" / "sources.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, url, sha, lic = line.split()
        dest = RAW / name
        if dest.exists():
            print(f"[skip] {name} already present")
            continue
        dest.mkdir()
        run("git", "init", "-q", cwd=dest)
        run("git", "remote", "add", "origin", url, cwd=dest)
        run("git", "fetch", "-q", "--depth", "1", "origin", sha, cwd=dest)
        run("git", "checkout", "-q", "FETCH_HEAD", cwd=dest)
        lic_files = [p.name for p in dest.glob("LICENSE*")] + [p.name for p in dest.glob("COPYING*")]
        print(f"[ok] {name} @ {sha[:10]} expected {lic}; license files: {lic_files}")
        if not lic_files:
            sys.exit(f"{name}: no LICENSE file found - verify licensing manually")


if __name__ == "__main__":
    main()
