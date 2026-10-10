"""Survey a Cold War total conversion (or any HoI4 mod) so The Veiled Hollows can be built on top of it.

    python survey_base_mod.py                 # find installed Cold War mods and report on the first one
    python survey_base_mod.py --base 1234567  # a specific Workshop item id, or a mod folder path
    python survey_base_mod.py --list          # list every installed HoI4 mod

It writes base_mod_report.txt next to this script and opens it. The report lists only names (start
dates, ideologies, country tags, state names and owners, technologies, equipment, units, scripted
effects), which is what a submod has to match. It copies no mod files, and it replaces your home
folder with "~". Send the report file back to the agent.

Standard library only. Python 3.8+.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_mod import PROFILES, find_game, steam_libraries  # noqa: E402

HEARTLAND = PROFILES["vanilla"]["heartland"]
FRONTIER = PROFILES["vanilla"]["frontier"]

APP_ID = "394360"
COLD_WAR = re.compile(r"cold war|iron curtain|aftermath|red wall|world divided", re.I)
ADDON = re.compile(r"music|sound|soundtrack|audio|font|map ?mode|ui |interface|compatch|compatibility|submod|addon|add-on|"
                   r"translation|localisation|localization|fix\b|graphics|portraits|flags", re.I)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="ignore")


def strip_comments(text: str) -> str:
    return re.sub(r"#[^\n]*", "", text)


def top_level_blocks(text: str):
    """Yield (name, body) for each `name = { ... }` at depth 0 (or depth 1 when wrapped)."""
    text = strip_comments(text)
    i, n = 0, len(text)
    while i < n:
        m = re.compile(r"([\w.\-]+)\s*=\s*\{").search(text, i)
        if not m:
            return
        depth, j = 1, m.end()
        while j < n and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        yield m.group(1), text[m.end():j - 1]
        i = j


def installed_mods(game: Path) -> list[tuple[str, Path, str]]:
    """(name, folder, source) for Workshop and local mods."""
    mods = []
    for lib in steam_libraries() + [game.parents[2] if len(game.parents) > 2 else game]:
        ws = lib / "steamapps" / "workshop" / "content" / APP_ID
        if ws.is_dir():
            for d in ws.iterdir():
                desc = d / "descriptor.mod"
                if desc.exists():
                    m = re.search(r'name\s*=\s*"([^"]+)"', read(desc))
                    mods.append((m.group(1) if m else d.name, d, f"workshop {d.name}"))
    home = Path.home()
    for docs in (home / "Documents", home / "OneDrive/Documents", home / ".local/share"):
        md = docs / "Paradox Interactive" / "Hearts of Iron IV" / "mod"
        if md.is_dir():
            for f in md.glob("*.mod"):
                t = read(f)
                pm = re.search(r'path\s*=\s*"([^"]+)"', t)
                nm = re.search(r'name\s*=\s*"([^"]+)"', t)
                if pm and Path(pm.group(1)).is_dir():
                    mods.append((nm.group(1) if nm else f.stem, Path(pm.group(1)), "local"))
    seen, out = set(), []
    for m in mods:
        if m[1].resolve() not in seen:
            seen.add(m[1].resolve())
            out.append(m)
    return out


def layered(base: Path, game: Path, sub: str, pattern="*.txt") -> list[Path]:
    """Files in a folder as the game sees them: the mod's file wins over vanilla's with the same name,
    and vanilla is ignored entirely when the mod replace_path's the folder."""
    desc = read(base / "descriptor.mod") if (base / "descriptor.mod").exists() else ""
    replaced = any(sub.startswith(r.strip("/")) for r in re.findall(r'replace_path\s*=\s*"([^"]+)"', desc))
    files = {}
    if not replaced and (game / sub).is_dir():
        for f in (game / sub).rglob(pattern):
            files[f.relative_to(game / sub).as_posix()] = f
    if (base / sub).is_dir():
        for f in (base / sub).rglob(pattern):
            files[f.relative_to(base / sub).as_posix()] = f
    return sorted(files.values())


def survey(base: Path, game: Path, name: str, source: str) -> str:
    out: list[str] = []
    w = out.append

    @contextmanager
    def section(title):
        """Each part of the report stands alone: an unexpected file can't stop the rest."""
        w(f"\n## {title}")
        try:
            yield
        except Exception as e:  # noqa: BLE001 - report it and carry on
            w(f"(this section failed: {type(e).__name__}: {e})")

    desc = read(base / "descriptor.mod") if (base / "descriptor.mod").exists() else ""
    w(f"# Base mod report for The Veiled Hollows")
    w(f"name: {name}")
    w(f"source: {source}")
    for key in ("version", "supported_version"):
        m = re.search(rf'{key}\s*=\s*"([^"]+)"', desc)
        w(f"{key}: {m.group(1) if m else '?'}")
    w("replace_path: " + ", ".join(re.findall(r'replace_path\s*=\s*"([^"]+)"', desc)))
    gv = re.search(r'"rawVersion"\s*:\s*"([^"]+)"', read(game / "launcher-settings.json")) if (game / "launcher-settings.json").exists() else None
    w(f"game version: {gv.group(1) if gv else '?'}")

    # bookmarks and start dates
    with section("Bookmarks"):
        for f in layered(base, game, "common/bookmarks"):
            t = strip_comments(read(f))
            for m in re.finditer(r'name\s*=\s*"?([\w.]+)"?[^{}]*?date\s*=\s*([\d.]+)', t):
                w(f"{f.name}: {m.group(1)} {m.group(2)}")
        found = re.findall(r'(START_DATE|END_DATE)\s*=\s*"([^"]+)"',
                           " ".join(read(f) for f in layered(base, game, "common/defines", "*.lua")))
        w("defines start/end: " + ", ".join(sorted({f"{k} {v}" for k, v in found})))

    # ideologies
    with section("Ideologies (ideology: sub-ideologies)"):
        for f in layered(base, game, "common/ideologies"):
            for _, body in top_level_blocks(read(f)):
                for ideo, ib in top_level_blocks(body):
                    subs = [s for n, b in top_level_blocks(ib) if n == "types" for s, _ in top_level_blocks(b)]
                    w(f"{ideo}: {' '.join(subs)}")

    # tags
    with section("Country tags"):
        tags = {}
        for f in layered(base, game, "common/country_tags"):
            for m in re.finditer(r"^\s*([A-Z][A-Z0-9]{2})\s*=\s*\"([^\"]+)\"", strip_comments(read(f)), re.M):
                tags[m.group(1)] = m.group(2)
        w(f"{len(tags)} tags. APL taken: {'APL' in tags}. USA: {tags.get('USA', 'missing')}")
        w("all: " + " ".join(sorted(tags)))

    # states
    with section("Appalachian states"):
        loc = {}
        for f in layered(base, game, "localisation", "*_l_english.yml"):
            for m in re.finditer(r'^\s*STATE_(\d+):\d*\s*"([^"]*)"', read(f), re.M):
                loc.setdefault(m.group(2).strip(), []).append(int(m.group(1)))
        files = {}
        for f in layered(base, game, "history/states"):
            m = re.search(r"\bid\s*=\s*(\d+)", read(f))
            if m:
                files[int(m.group(1))] = f
        for nm in HEARTLAND + FRONTIER:
            for sid in loc.get(nm, []):
                if sid in files:
                    t = read(files[sid])
                    owner = re.search(r"\bowner\s*=\s*([A-Z0-9]{3})", t)
                    w(f"{nm}: id {sid} file {files[sid].name} owner {owner.group(1) if owner else '?'} "
                      f"from {'mod' if base in files[sid].parents else 'vanilla'}")
        w(f"{len(files)} state files in total")
        hits = [k for k in loc if re.search(r"appalach|allegheny|cumberland|blue ridge", k, re.I)]
        w("other Appalachian-sounding state names: " + ", ".join(hits))

    # every US-owned state, so the submod can pick Appalachia's land from the base mod's own map
    with section("US-owned states (id | name | provinces | victory points)"):
        names = {}
        for f in layered(base, game, "localisation", "*_l_english.yml"):
            if "state" not in f.name.lower():
                continue
            for m in re.finditer(r'^\s*([\w.]+):\d*\s*"([^"]*)"', read(f), re.M):
                names[m.group(1)] = m.group(2)
        rows = []
        for sid, f in sorted(files.items()):
            t = strip_comments(read(f))
            owner = re.search(r"\bowner\s*=\s*([A-Z0-9]{3})", t)
            if not owner or owner.group(1) != "USA":
                continue
            key = re.search(r'\bname\s*=\s*"?([\w.]+)"?', t)
            nm = names.get(key.group(1), key.group(1)) if key else "?"
            provs = re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
            vps = re.findall(r"victory_points\s*=\s*\{\s*(\d+)\s+(\d+)", t)
            rows.append(f"{sid} | {nm} | {len(provs.group(1).split()) if provs else 0} | "
                        + " ".join(f"{p}:{v}" for p, v in vps))
        w(f"{len(rows)} US-owned states")
        w("\n".join(rows))

    # the whole map, for redrawing borders
    with section("All states (id | name | owner | cores | provinces | category)"):
        rows = []
        for sid, f in sorted(files.items()):
            t = strip_comments(read(f))
            hist = t[t.find("history"):] if "history" in t else t
            owner = re.search(r"\bowner\s*=\s*([A-Z0-9]{3})", hist)
            cores = sorted(set(re.findall(r"add_core_of\s*=\s*([A-Z0-9]{3})", hist)))
            key = re.search(r'\bname\s*=\s*"?([\w.]+)"?', t)
            nm = names.get(key.group(1), key.group(1)) if key else "?"
            provs = re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
            cat = re.search(r"state_category\s*=\s*(\w+)", t)
            rows.append(f"{sid} | {nm} | {owner.group(1) if owner else '-'} | {' '.join(cores)} | "
                        f"{len(provs.group(1).split()) if provs else 0} | {cat.group(1) if cat else '?'}")
        w(f"{len(rows)} states")
        w("\n".join(rows))

    with section("All countries (tag | capital | ruling party | history file)"):
        rows = []
        for f in layered(base, game, "history/countries"):
            t = strip_comments(read(f))
            tag = f.name[:3]
            cap = re.search(r"\bcapital\s*=\s*(\d+)", t)
            party = re.search(r"ruling_party\s*=\s*(\w+)", t)
            rows.append(f"{tag} | {cap.group(1) if cap else '-'} | {party.group(1) if party else '-'} | {f.name}")
        w("\n".join(rows))

    # usa leader sub-ideology, as an example of how characters are written
    with section("USA history (first lines)"):
        for f in layered(base, game, "history/countries"):
            if f.name.startswith("USA"):
                lines = [l.strip() for l in strip_comments(read(f)).splitlines() if l.strip()]
                w("\n".join(lines[:40]))
                break

    # technologies, equipment, units
    with section("Technologies (names)"):
        techs = []
        for f in layered(base, game, "common/technologies"):
            for _, body in top_level_blocks(read(f)):
                techs += [n for n, b in top_level_blocks(body) if "research_cost" in b]
        w(f"{len(techs)}: " + " ".join(techs))
    with section("Tech folders"):
        folders = set()
        for f in layered(base, game, "common/technologies"):
            folders |= set(re.findall(r"folder\s*=\s*\{\s*name\s*=\s*(\w+)", strip_comments(read(f))))
        w(" ".join(sorted(folders)))
    with section("Equipment archetypes -> variants"):
        for f in layered(base, game, "common/units/equipment"):
            for _, body in top_level_blocks(read(f)):
                arch = {}
                for n, b in top_level_blocks(body):
                    if re.search(r"is_archetype\s*=\s*yes", b):
                        arch.setdefault(n, [])
                    m = re.search(r"archetype\s*=\s*(\w+)", b)
                    if m and "is_archetype" not in b:
                        arch.setdefault(m.group(1), []).append(n)
                for a, vs in arch.items():
                    w(f"{a}: {' '.join(vs)}")
    with section("Sub-units (land)"):
        for f in layered(base, game, "common/units"):
            if f.parent.name != "units":
                continue
            for _, body in top_level_blocks(read(f)):
                for n, b in top_level_blocks(body):
                    if "map_icon_category" in b and re.search(r"map_icon_category\s*=\s*(infantry|armored|other)", b):
                        need = re.search(r"need\s*=\s*\{([^}]*)\}", b)
                        w(f"{n}: need {' '.join(need.group(1).split()) if need else '-'}")
    with section("Unit categories"):
        for f in layered(base, game, "common/unit_tags"):
            w(" ".join(re.findall(r"^\s*(category_\w+)", strip_comments(read(f)), re.M)))

    # economy hints
    with section("Scripted effects that look like an economy"):
        for f in layered(base, game, "common/scripted_effects"):
            names = [n for n, _ in top_level_blocks(read(f)) if re.search(r"money|treasury|budget|econom|debt|gdp|tax", n, re.I)]
            if names:
                w(f"{f.name}: {' '.join(names)}")
    with section("Decision categories"):
        cats = []
        for f in layered(base, game, "common/decisions/categories"):
            cats += [n for n, _ in top_level_blocks(read(f))]
        w(" ".join(cats))
    with section("Files in the base mod (top folders)"):
        for d in sorted(p for p in base.iterdir() if p.is_dir()):
            w(f"{d.name}: {sum(1 for _ in d.rglob('*') if _.is_file())} files")

    # the end of the game's logs, to see why a load hangs or crashes
    with section("Game logs (last lines)"):
        home = Path.home()
        for docs in (home / "OneDrive/Documents", home / "Documents", home / ".local/share"):
            logs = docs / "Paradox Interactive" / "Hearts of Iron IV" / "logs"
            if logs.is_dir():
                for lf in ("system.log", "error.log", "exceptions.log", "game.log"):
                    if (logs / lf).exists():
                        lines = read(logs / lf).splitlines()
                        w(f"--- {lf} ({len(lines)} lines, last 80) ---")
                        w("\n".join(lines[-80:]))
                crash = sorted((logs.parent / "crashes").glob("*"), key=lambda q: q.stat().st_mtime)[-1:] \
                    if (logs.parent / "crashes").is_dir() else []
                for c in crash:
                    w(f"--- latest crash folder: {c.name} ---")
                    for name in ("exception.txt", "meta.yml"):
                        if (c / name).exists():
                            w("\n".join(read(c / name).splitlines()[:60]))
                break

    text = "\n".join(out) + "\n"
    home = str(Path.home())
    for h in {home, home.replace("\\", "/")}:
        text = text.replace(h, "~")
    return text


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game")
    ap.add_argument("--base", help="Workshop item id or mod folder")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--vanilla", action="store_true", help="survey the unmodded game itself")
    a = ap.parse_args()
    game = find_game(a.game)
    if a.vanilla:
        print("Surveying: vanilla Hearts of Iron IV")
        report = HERE / "base_mod_report.txt"
        report.write_text(survey(game, game, "vanilla Hearts of Iron IV", "game"), encoding="utf-8")
        print(f"Wrote {report}. Send this file to the agent.")
        if sys.platform.startswith("win"):
            os.startfile(report)
        return
    mods = installed_mods(game)
    if a.list or not mods:
        print("Installed HoI4 mods:" if mods else "No HoI4 mods found. Subscribe to the Cold War mod on the Workshop, "
              "let Steam download it, then run this again.")
        for nm, d, src in mods:
            print(f"  {nm}   [{src}]")
        return
    if a.base:
        pick = [m for m in mods if a.base in (m[1].name, str(m[1]))] or [(a.base, Path(a.base), "path")]
    else:
        pick = [m for m in mods if COLD_WAR.search(m[0]) and not ADDON.search(m[0])]
        # the total conversion itself is the one with the most country histories
        pick.sort(key=lambda m: -sum(1 for _ in (m[1] / "history" / "countries").glob("*.txt")))
        if len(pick) > 1:
            print("Cold War mods found (using the first; pass --base <id> to choose):")
            for nm, d, src in pick:
                print(f"  {nm}   [{src}]")
        if not pick:
            print("No Cold War mod found among your mods. Run with --list to see them, then --base <id>.")
            for nm, d, src in mods:
                print(f"  {nm}   [{src}]")
            return
    name, folder, src = pick[0]
    print(f"Surveying: {name} ({src})")
    report = HERE / "base_mod_report.txt"
    report.write_text(survey(folder, game, name, src), encoding="utf-8")
    print(f"Wrote {report}. Send this file to the agent.")
    if sys.platform.startswith("win"):
        os.startfile(report)  # opens in Notepad


if __name__ == "__main__":
    main()
