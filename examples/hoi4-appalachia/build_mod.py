"""Build The Veiled Hollows into your Hearts of Iron IV mod folder.

    python build_mod.py                         # find the game and the mod folder automatically
    python build_mod.py --game "D:/SteamLibrary/steamapps/common/Hearts of Iron IV"
    python build_mod.py --out "%USERPROFILE%/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod"
    python build_mod.py --dry-run               # only report what it found

Why a builder? Giving Appalachia its land means overriding the vanilla state history files for West
Virginia, Kentucky and Tennessee. Those files belong to Paradox, so they are not in this repository.
This script reads them from YOUR install, changes the owner to APL, adds APL cores, and writes the
results into your local mod folder. It also fills in the few files that need state or province IDs.
Nothing it writes ever goes back into the repository.

Standard library only. Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "mod"
TEMPLATES = HERE / "templates"
MOD_NAME = "the_veiled_hollows"
TAG = "APL"

# Matched against the English state names in your install (STATE_123:0 "West Virginia").
HEARTLAND = ["West Virginia", "Kentucky", "Tennessee"]
FRONTIER = ["Virginia", "North Carolina", "South Carolina", "Pennsylvania", "Ohio", "Maryland", "Georgia",
            "Alabama"]
CAPITAL = "West Virginia"


# ---------------------------------------------------------------- locating things

def steam_libraries() -> list[Path]:
    roots = []
    if sys.platform.startswith("win"):
        for env in ("ProgramFiles(x86)", "ProgramFiles"):
            if os.environ.get(env):
                roots.append(Path(os.environ[env]) / "Steam")
    elif sys.platform == "darwin":
        roots.append(Path.home() / "Library/Application Support/Steam")
    else:
        roots += [Path.home() / ".steam/steam", Path.home() / ".local/share/Steam",
                  Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam"]
    libs = []
    for root in roots:
        vdf = root / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            libs += [Path(p.replace("\\\\", "\\")) for p in re.findall(r'"path"\s+"([^"]+)"', vdf.read_text(errors="ignore"))]
        libs.append(root)
    return libs


def find_game(explicit: str | None) -> Path:
    candidates = [Path(explicit)] if explicit else [lib / "steamapps/common/Hearts of Iron IV" for lib in steam_libraries()]
    for c in candidates:
        if (c / "history" / "states").is_dir():
            return c
    sys.exit("Could not find Hearts of Iron IV. Pass --game \"<install folder>\" (the folder that contains history/ and common/).")


def find_mod_dir(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    home = Path.home()
    if sys.platform.startswith("linux"):
        options = [home / ".local/share/Paradox Interactive/Hearts of Iron IV/mod"]
    else:
        options = [home / "Documents/Paradox Interactive/Hearts of Iron IV/mod",
                   home / "OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod",
                   home / "OneDrive/Dokumente/Paradox Interactive/Hearts of Iron IV/mod"]
    for o in options:
        if o.parent.is_dir():
            return o
    sys.exit("Could not find your 'Paradox Interactive/Hearts of Iron IV' documents folder. Launch the game once, "
             "or pass --out \"<.../Hearts of Iron IV/mod>\".")


# ---------------------------------------------------------------- reading the install

def state_names(game: Path) -> dict[str, list[int]]:
    """English state name -> state ids, from the game's localisation."""
    names: dict[str, list[int]] = {}
    for yml in (game / "localisation").rglob("*_l_english.yml"):
        for m in re.finditer(r'^\s*STATE_(\d+):\d*\s*"([^"]*)"', yml.read_text(encoding="utf-8-sig", errors="ignore"), re.M):
            names.setdefault(m.group(2).strip(), []).append(int(m.group(1)))
    return names


def state_files(game: Path) -> dict[int, Path]:
    files = {}
    for f in (game / "history" / "states").glob("*.txt"):
        m = re.search(r"\bid\s*=\s*(\d+)", f.read_text(encoding="utf-8-sig", errors="ignore"))
        if m:
            files[int(m.group(1))] = f
    return files


def owner_of(text: str) -> str | None:
    m = re.search(r"\bowner\s*=\s*([A-Z0-9]{3})\b", text)
    return m.group(1) if m else None


def provinces_of(text: str) -> list[int]:
    """Victory-point provinces first (cities), then the rest."""
    vps = [int(p) for p in re.findall(r"victory_points\s*=\s*\{\s*(\d+)", text)]
    m = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
    rest = [int(p) for p in m.group(1).split()] if m else []
    return vps + [p for p in rest if p not in vps]


def resolve(names: dict[str, list[int]], files: dict[int, Path], wanted: list[str], required: bool) -> dict[str, int]:
    found = {}
    for name in wanted:
        ids = [i for i in names.get(name, []) if i in files and owner_of(files[i].read_text(encoding="utf-8-sig", errors="ignore")) == "USA"]
        if len(ids) == 1:
            found[name] = ids[0]
        elif len(ids) > 1:
            print(f"  ! '{name}' matches several US states {ids}; using all of them is not supported, taking {ids[0]}")
            found[name] = ids[0]
        elif required:
            sys.exit(f"Could not find a US-owned state called '{name}' in your install. Is this vanilla HoI4? "
                     f"Edit HEARTLAND in build_mod.py to match your state names.")
        else:
            print(f"  - frontier state '{name}' not found as a US state; skipping")
    return found


# ---------------------------------------------------------------- writing

def rewrite_state(text: str) -> str:
    """owner = USA -> owner = APL, and add an APL core right after the first owner line."""
    text, n = re.subn(r"\bowner\s*=\s*USA\b", f"owner = {TAG}", text)
    if n == 0:
        raise ValueError("state has no 'owner = USA'")
    text = re.sub(rf"(owner = {TAG})", rf"\1\n\t\tadd_core_of = {TAG}", text, count=1)
    return text


def fill(template: str, values: dict[str, object]) -> str:
    def sub(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f"template value {key} not provided")
        return str(values[key])
    return re.sub(r"\{\{(\w+)\}\}", sub, template)


def game_version(game: Path) -> str:
    try:
        raw = json.loads((game / "launcher-settings.json").read_text(encoding="utf-8-sig"))
        m = re.search(r"(\d+\.\d+)", raw.get("rawVersion", "") or raw.get("version", ""))
        if m:
            return m.group(1) + ".*"
    except (OSError, ValueError):
        pass
    return "1.*"


def build(game: Path, out_root: Path, dry_run: bool) -> Path:
    print(f"game:      {game}")
    names, files = state_names(game), state_files(game)
    print(f"           {len(files)} state files, {len(names)} state names")

    tags = (game / "common" / "country_tags" / "00_countries.txt")
    if tags.exists() and re.search(rf"^\s*{TAG}\s*=", tags.read_text(encoding="utf-8-sig", errors="ignore"), re.M):
        sys.exit(f"Your game already defines the tag {TAG}; change TAG in this script and in the mod files.")

    heart = resolve(names, files, HEARTLAND, required=True)
    front = resolve(names, files, FRONTIER, required=False)
    print("heartland: " + ", ".join(f"{n} ({i})" for n, i in heart.items()))
    print("frontier:  " + (", ".join(f"{n} ({i})" for n, i in front.items()) or "none"))

    capital_text = files[heart[CAPITAL]].read_text(encoding="utf-8-sig", errors="ignore")
    provs = {}
    for k, name in enumerate(HEARTLAND, start=1):
        p = provinces_of(files[heart[name]].read_text(encoding="utf-8-sig", errors="ignore"))
        if not p:
            sys.exit(f"No provinces found in the state file for {name}.")
        provs[f"P{k}"] = p[0]
    if not provinces_of(capital_text):
        sys.exit("The capital state has no provinces.")

    out = out_root / MOD_NAME
    print(f"mod:       {out}")
    if dry_run:
        return out

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(SRC, out)

    # 1. State overrides, written under the same file name as the vanilla file so they replace it.
    for name, sid in heart.items():
        src = files[sid]
        dst = out / "history" / "states" / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(rewrite_state(src.read_text(encoding="utf-8-sig", errors="ignore")), encoding="utf-8")

    # 2. Files that need IDs.
    (out / "history" / "countries" / f"{TAG} - Appalachia.txt").write_text(
        fill((TEMPLATES / "APL_history.txt").read_text(), {"CAPITAL": heart[CAPITAL]}), encoding="utf-8")
    (out / "history" / "units" / "APL_1936.txt").write_text(
        fill((TEMPLATES / "APL_1936.txt").read_text(), provs), encoding="utf-8")

    lines = ["# Generated by build_mod.py for your install. Do not edit; rebuild instead.", "",
             "APL_mark_states = {"]
    lines += [f"\t{sid} = {{ set_state_flag = APL_heartland }}  # {n}" for n, sid in heart.items()]
    lines += [f"\t{sid} = {{ set_state_flag = APL_frontier }}  # {n}" for n, sid in front.items()]
    lines += ["}", "", "APL_frontier_wargoal = {"]
    if front:
        lines += ["\tif = {", "\t\tlimit = { country_exists = USA }", "\t\tcreate_wargoal = {", "\t\t\ttype = take_state_focus",
                  "\t\t\ttarget = USA", "\t\t\tgenerator = { " + " ".join(str(i) for i in front.values()) + " }", "\t\t}", "\t}"]
    lines += ["}", ""]
    (out / "common" / "scripted_effects" / "APL_generated_effects.txt").write_text("\n".join(lines), encoding="utf-8")

    # 3. Descriptors: one inside the folder, one next to it for the launcher.
    version = game_version(game)
    inner = (SRC / "descriptor.mod").read_text().replace('supported_version="1.*"', f'supported_version="{version}"')
    (out / "descriptor.mod").write_text(inner, encoding="utf-8")
    (out_root / f"{MOD_NAME}.mod").write_text(inner + f'path="{out.as_posix()}"\n', encoding="utf-8")
    print(f"built for game version {version}. Enable 'The Veiled Hollows' in the launcher's playset.")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", help="Hearts of Iron IV install folder")
    ap.add_argument("--out", help="your '.../Hearts of Iron IV/mod' folder")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    build(find_game(a.game), find_mod_dir(a.out), a.dry_run)


if __name__ == "__main__":
    main()
