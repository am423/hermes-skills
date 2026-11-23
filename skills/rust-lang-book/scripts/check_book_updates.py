#!/usr/bin/env python3
"""Track upstream changes to The Rust Programming Language (rust-lang/book).

Stdlib only; shells out to `git`. The pinned commit this skill was distilled
from lives in ../assets/source-pin.json next to this script.

Commands:
  head            Print the upstream HEAD sha (deterministic; cron monitor).
  check           Compare pin with upstream; print a JSON report of changed
                  source files grouped by the reference file they feed.
  diff REF        Print the upstream git diff (pin..HEAD) for the sources
                  behind one reference file, e.g. `diff ch04-ownership.md`.
  sources REF     Print the current upstream source paths behind REF.
  pin [SHA]       Record SHA (default: cached clone HEAD) as distilled.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/rust-lang/book"
SKILL_DIR = Path(__file__).resolve().parent.parent
PIN_FILE = SKILL_DIR / "assets" / "source-pin.json"
WATCHED = ("src", "listings")

# src/ filename prefix -> reference file. Longest prefix wins.
SRC_MAP = {
    "title-page": "appendix-reference.md",
    "foreword": "ch01-02-toolchain-and-first-program.md",
    "ch00": "ch01-02-toolchain-and-first-program.md",
    "ch01": "ch01-02-toolchain-and-first-program.md",
    "ch02": "ch01-02-toolchain-and-first-program.md",
    "ch03": "ch03-common-concepts.md",
    "ch04": "ch04-ownership.md",
    "ch05": "ch05-structs.md",
    "ch06": "ch06-enums-and-matching.md",
    "ch07": "ch07-packages-crates-modules.md",
    "ch08": "ch08-collections.md",
    "ch09": "ch09-error-handling.md",
    "ch10": "ch10-generics-traits-lifetimes.md",
    "ch11": "ch11-testing.md",
    "ch12": "ch12-cli-project.md",
    "ch13": "ch13-closures-and-iterators.md",
    "ch14": "ch14-cargo-and-crates-io.md",
    "ch15": "ch15-smart-pointers.md",
    "ch16": "ch16-concurrency.md",
    "ch17": "ch17-async.md",
    "ch18": "ch18-oop-and-trait-objects.md",
    "ch19": "ch19-patterns.md",
    "ch20-00": "ch20-unsafe.md",
    "ch20-01": "ch20-unsafe.md",
    "ch20-02": "ch20-advanced-traits-types-functions.md",
    "ch20-03": "ch20-advanced-traits-types-functions.md",
    "ch20-04": "ch20-advanced-traits-types-functions.md",
    "ch20-05": "ch20-macros.md",
    "ch21": "ch21-web-server-project.md",
    "appendix": "appendix-reference.md",
}
# Files that carry no distillable content.
IGNORED = {"src/SUMMARY.md", "src/appendix-06-translation.md"}
# Cross-cutting files to re-check whenever any chapter file is refreshed.
CROSS_CUTTING = ["cheatsheet.md", "glossary.md"]


def cache_dir() -> Path:
    home = os.environ.get("HERMES_HOME") or str(Path.home() / ".hermes")
    return Path(home) / "cache" / "rust-lang-book" / "repo"


def git(*args: str, cwd: Path | None = None, timeout: int = 600) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout
    )
    if proc.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def upstream_head() -> str:
    out = git("ls-remote", REPO_URL, "HEAD", timeout=120).split()
    if not out or not re.fullmatch(r"[0-9a-f]{40}", out[0]):
        sys.exit("could not resolve upstream HEAD")
    return out[0]


def ensure_clone() -> Path:
    repo = cache_dir()
    if not (repo / ".git").exists():
        repo.parent.mkdir(parents=True, exist_ok=True)
        git("clone", "--filter=blob:none", "--quiet", REPO_URL, str(repo))
    else:
        git("fetch", "--quiet", "origin", cwd=repo)
        git("checkout", "--quiet", "--detach", "origin/HEAD", cwd=repo)
    return repo


def read_pin() -> dict:
    if not PIN_FILE.exists():
        return {}
    return json.loads(PIN_FILE.read_text(encoding="utf-8"))


def refs_for(path: str) -> list[str]:
    """Reference file(s) fed by an upstream path; [] if ignored/unmapped."""
    if path in IGNORED:
        return []
    parts = path.split("/")
    if parts[0] == "src" and len(parts) == 2:
        stem = parts[1]
        for prefix in sorted(SRC_MAP, key=len, reverse=True):
            if stem.startswith(prefix):
                return [SRC_MAP[prefix]]
        return ["UNMAPPED"]
    if parts[0] == "listings" and len(parts) > 1:
        m = re.match(r"(ch\d\d)", parts[1])
        if m:
            hits = sorted(
                {v for k, v in SRC_MAP.items() if k.startswith(m.group(1))}
            )
            return hits or ["UNMAPPED"]
        return ["UNMAPPED"]
    return []


def book_version(repo: Path) -> str:
    title = repo / "src" / "title-page.md"
    if not title.exists():
        return ""
    text = " ".join(title.read_text(encoding="utf-8").split())
    m = re.search(r"Rust (\d+\.\d+(?:\.\d+)?)", text)
    e = re.search(r'edition = "(\d{4})"', text)
    return f"Rust {m.group(1) if m else '?'}, edition {e.group(1) if e else '?'}"


def cmd_head(_: argparse.Namespace) -> None:
    print(upstream_head())


def cmd_check(_: argparse.Namespace) -> None:
    pin = read_pin()
    pinned = pin.get("commit", "")
    head = upstream_head()
    report: dict = {"pinned": pinned, "upstream": head, "up_to_date": pinned == head}
    if pinned == head:
        print(json.dumps(report, indent=2))
        return
    repo = ensure_clone()
    report["clone"] = str(repo)
    report["book_version_pinned"] = pin.get("book_version", "")
    report["book_version_upstream"] = book_version(repo)
    if not pinned:
        report["note"] = "no pin recorded; distill every reference file, then pin"
        print(json.dumps(report, indent=2))
        return
    names = git(
        "diff", "--name-status", f"{pinned}..{head}", "--", *WATCHED, cwd=repo
    )
    by_ref: dict[str, list[str]] = {}
    ignored = 0
    for line in names.splitlines():
        cols = line.split("\t")
        status, path = cols[0], cols[-1]
        refs = refs_for(path)
        if not refs or path.endswith("Cargo.lock"):
            ignored += 1
            continue
        parts = path.split("/")
        if parts[0] == "listings" and len(parts) > 3:
            # Collapse per-file noise to one entry per listing directory.
            entry = "listing\t" + "/".join(parts[:3])
        else:
            entry = f"{status}\t{path}"
        for ref in refs:
            if entry not in by_ref.setdefault(ref, []):
                by_ref[ref].append(entry)
    report["changed_references"] = {k: by_ref[k] for k in sorted(by_ref)}
    report["ignored_paths"] = ignored
    report["content_changed"] = bool(by_ref)
    if by_ref:
        report["also_review"] = CROSS_CUTTING + ["SKILL.md index"]
    print(json.dumps(report, indent=2))


def sources_for(ref: str, repo: Path) -> list[str]:
    paths = []
    for top in WATCHED:
        base = repo / top
        if not base.exists():
            continue
        for child in sorted(base.iterdir()):
            rel = f"{top}/{child.name}"
            if ref in refs_for(rel):
                paths.append(rel)
    return paths


def cmd_sources(args: argparse.Namespace) -> None:
    repo = ensure_clone()
    print("\n".join(f"{repo}/{p}" for p in sources_for(args.ref, repo)))


def cmd_diff(args: argparse.Namespace) -> None:
    pinned = read_pin().get("commit", "")
    if not pinned:
        sys.exit("no pin recorded")
    repo = ensure_clone()
    paths = sources_for(args.ref, repo)
    if not paths:
        sys.exit(f"no upstream sources map to {args.ref}")
    sys.stdout.write(git("diff", f"{pinned}..HEAD", "--", *paths, cwd=repo))


def cmd_pin(args: argparse.Namespace) -> None:
    repo = ensure_clone()
    sha = args.sha or git("rev-parse", "HEAD", cwd=repo).strip()
    sha = git("rev-parse", "--verify", f"{sha}^{{commit}}", cwd=repo).strip()
    date = git("show", "-s", "--format=%cI", sha, cwd=repo).strip()
    data = {
        "source": REPO_URL,
        "commit": sha,
        "commit_date": date,
        "book_version": book_version(repo),
        "distilled_on": _dt.date.today().isoformat(),
    }
    PIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    PIN_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("head").set_defaults(fn=cmd_head)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    p = sub.add_parser("diff")
    p.add_argument("ref")
    p.set_defaults(fn=cmd_diff)
    p = sub.add_parser("sources")
    p.add_argument("ref")
    p.set_defaults(fn=cmd_sources)
    p = sub.add_parser("pin")
    p.add_argument("sha", nargs="?")
    p.set_defaults(fn=cmd_pin)
    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
