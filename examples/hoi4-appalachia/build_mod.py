"""Build The Veiled Hollows into your Hearts of Iron IV mod folder.

    python build_mod.py                         # find the game and the mod folder automatically
    python build_mod.py --game "D:/SteamLibrary/steamapps/common/Hearts of Iron IV"
    python build_mod.py --out "%USERPROFILE%/OneDrive/Documents/Paradox Interactive/Hearts of Iron IV/mod"
    python build_mod.py --dry-run               # only report what it found
    python build_mod.py --base cwic             # as a submod of Cold War Iron Curtain instead
    python build_mod.py --base 1458561226       # a specific base mod (Workshop id or folder)

Why a builder? Giving Appalachia its land means overriding the state history files of the world it's
built into: vanilla 1936 (West Virginia, Kentucky, Tennessee), or a Cold War total conversion such as
Cold War Iron Curtain, whose map splits America into regions (Charleston, Morgantown, Eastern Kentucky,
Southwest Virginia, Franklin, Asheville). Those files belong to Paradox or the base mod's authors, so they
are not in this repository. This script reads them from YOUR install, changes the owner to APL, adds APL
cores, and writes the results into your local mod folder. It also fills in the few files that need state or province IDs.
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

# What Appalachia is made of depends on the world it's built into. A profile says which states form the
# heartland (owned at the start) and the frontier (claims, the creeping fog, the Night March), which
# technologies Appalachia starts with, and which ideology the Mountain Assembly governs as.
# Vanilla states are matched by English name; the Cold War map is matched by id, with the name checked.
PROFILES = {
    "vanilla": {
        "label": "vanilla Hearts of Iron IV (1936, 1939 and the 1949 Cold War)",
        "heartland": ["West Virginia", "Kentucky", "Tennessee"],
        "frontier": ["Virginia", "North Carolina", "South Carolina", "Pennsylvania", "Ohio", "Maryland", "Georgia",
                     "Alabama"],
        "capital": "West Virginia",
        "techs": ["infantry_weapons", "infantry_weapons1", "tech_support", "tech_engineers", "tech_recon",
                  "gw_artillery"],
        "assembly_party": "democratic",
        "assembly_subideology": "socialism",
        "dependency": None,
    },
    "cwic": {
        "label": "Cold War Iron Curtain: A World Divided (1949)",
        "match": r"cold war iron curtain",
        # (id, name in that mod). It has two states called Charleston: 364 is South Carolina's, 859 is
        # West Virginia's.
        "heartland": [(859, "Charleston"), (1695, "Morgantown"), (1728, "Eastern Kentucky"),
                      (1727, "Southwest Virginia"), (1705, "Franklin"), (1722, "Asheville")],
        "frontier": [(1693, "Pittsburgh"), (1691, "Western Maryland"), (360, "Central Pennsylvania"),
                     (369, "Louisville"), (1729, "Western Kentucky"), (368, "Nashville"),
                     (1717, "Carolina Upcountry"), (1713, "Northern Georgia"), (1712, "Birmingham"),
                     (1742, "Ohio River Valley"), (1697, "Cincinnati")],
        "capital": 859,
        "techs": ["infantry_equip_1", "infantry_equip_2", "tech_support", "tech_engineers", "tech_recon",
                  "artillery_1"],
        "assembly_party": "Social_Democratic",
        "assembly_subideology": "social_democrat",
        "dependency": "Cold War Iron Curtain: A World Divided",
    },
}
APP_ID = "394360"


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

class Sources:
    """The game's files as the game sees them: a base mod's file wins over vanilla's with the same name,
    and vanilla is skipped for any folder the base mod replace_path's."""

    def __init__(self, game: Path, base: Path | None = None):
        self.game, self.base = game, base
        self.replaced = []
        if base and (base / "descriptor.mod").exists():
            self.replaced = [r.strip("/") for r in
                             re.findall(r'replace_path\s*=\s*"([^"]+)"', read(base / "descriptor.mod"))]

    def files(self, sub: str, pattern: str = "*.txt") -> list[Path]:
        found = {}
        roots = [] if any(sub == r or sub.startswith(r + "/") for r in self.replaced) else [self.game]
        roots += [self.base] if self.base else []
        for root in roots:
            if (root / sub).is_dir():
                for f in (root / sub).rglob(pattern):
                    found[f.relative_to(root / sub).as_posix()] = f
        return sorted(found.values())


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="ignore")


def state_index(src: Sources) -> dict[int, tuple[Path, str, str | None]]:
    """state id -> (file, English name, owner)."""
    loc = {}
    for yml in src.files("localisation", "*_l_english.yml"):
        if "state" in yml.name.lower():
            for m in re.finditer(r'^\s*([\w.]+):\d*\s*"([^"]*)"', read(yml), re.M):
                loc[m.group(1)] = m.group(2).strip()
    index = {}
    for f in src.files("history/states"):
        t = read(f)
        m = re.search(r"\bid\s*=\s*(\d+)", t)
        if not m:
            continue
        key = re.search(r'\bname\s*=\s*"?([\w.]+)"?', t)
        index[int(m.group(1))] = (f, loc.get(key.group(1), key.group(1)) if key else "?", owner_of(t))
    return index


def owner_of(text: str) -> str | None:
    m = re.search(r"\bowner\s*=\s*([A-Z0-9]{3})\b", text)
    return m.group(1) if m else None


def provinces_of(text: str) -> list[int]:
    """Victory-point provinces first (cities), then the rest."""
    vps = [int(p) for p in re.findall(r"victory_points\s*=\s*\{\s*(\d+)", text)]
    m = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
    rest = [int(p) for p in m.group(1).split()] if m else []
    return vps + [p for p in rest if p not in vps]


def resolve(index, wanted, required: bool) -> dict[str, int]:
    """wanted: English names (vanilla) or (id, expected name) pairs (base mods). Returns name -> id for
    states that exist, carry that name and are owned by the USA."""
    by_name = {}
    for sid, (_, name, owner) in index.items():
        if owner == "USA":
            by_name.setdefault(name, []).append(sid)
    found = {}
    for w in wanted:
        if isinstance(w, tuple):
            sid, name = w
            ok = sid in index and index[sid][1] == name and index[sid][2] == "USA"
            why = ("missing" if sid not in index else f"called '{index[sid][1]}', owned by {index[sid][2]}")
            ids = [sid] if ok else []
        else:
            name, ids, why = w, by_name.get(w, []), "not found as a US-owned state"
        if ids:
            if len(ids) > 1:
                print(f"  ! '{name}' matches several US states {ids}; taking {ids[0]}")
            found[name] = ids[0]
        elif required:
            sys.exit(f"Heartland state '{name}' ({w[0] if isinstance(w, tuple) else '?'}) is {why}. "
                     "The base mod may have changed its map; send the agent a new survey report.")
        else:
            print(f"  - frontier state '{name}' {why}; skipping")
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


# ---------------------------------------------------------------- the 1949 Cold War start (vanilla only)

DATE_RE = re.compile(r"(\d{3,4})\.(\d{1,2})\.(\d{1,2})")


def block_span(text: str, key: str, start: int = 0):
    """(body_start, body_end) of the first `key = { ... }` at or after start, or None."""
    m = re.compile(rf"\b{re.escape(key)}\s*=\s*\{{").search(text, start)
    if not m:
        return None
    depth, i = 1, m.end()
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return m.end(), i - 1


def top_level(body: str):
    """Yield (key, value_text_or_None, block_body_or_None) for entries at depth 0 of a block body."""
    body = re.sub(r"#[^\n]*", "", body)
    i, n = 0, len(body)
    pat = re.compile(r"([\w.\-]+)\s*=\s*(\{|\"[^\"]*\"|[\w.\-]+)")
    while i < n:
        m = pat.search(body, i)
        if not m:
            return
        if m.group(2) == "{":
            depth, j = 1, m.end()
            while j < n and depth:
                depth += {"{": 1, "}": -1}.get(body[j], 0)
                j += 1
            yield m.group(1), None, body[m.end():j - 1]
            i = j
        else:
            yield m.group(1), m.group(2), None
            i = m.end()


def owner_at(text: str, date: tuple) -> str | None:
    """The state's owner on `date`, applying the history's dated entries in order."""
    span = block_span(text, "history")
    if not span:
        return None
    owner, dated = None, []
    for k, v, body in top_level(text[span[0]:span[1]]):
        if k == "owner" and v:
            owner = v
        elif body is not None and DATE_RE.fullmatch(k):
            m = re.search(r"\bowner\s*=\s*([A-Z0-9]{3})", body)
            if m:
                dated.append((tuple(int(x) for x in k.split(".")), m.group(1)))
    for d, o in sorted(dated):
        if d <= date:
            owner = o
    return owner


def add_to_history(text: str, entry: str) -> str:
    span = block_span(text, "history")
    if not span:
        raise ValueError("no history block")
    return text[:span[1]] + entry + text[span[1]:]


def cold_war_states(index, heart_ids, out: Path, cw) -> int:
    """Give every state its 1949 owner. Returns how many state files were overridden."""
    date = tuple(int(x) for x in cw.DATE.split("."))
    changed = 0
    for sid, (f, name, base_owner) in sorted(index.items()):
        dst = out / "history" / "states" / f.name
        text = read(dst) if dst.exists() else read(f)
        if sid in heart_ids:
            continue  # Appalachia's own, already rewritten
        want = base_owner
        if sid in cw.STATES:
            expected, tag = cw.STATES[sid]
            if name != expected:
                print(f"  ! 1949: state {sid} is called '{name}', expected '{expected}'; leaving it alone")
                continue
            want = tag
        if not want or want == owner_at(text, date):
            continue
        lines = [f"owner = {want}", f"controller = {want}"]
        if sid in cw.STATES and want in cw.CORE_TAGS:
            lines.append(f"add_core_of = {want}")
        entry = f"\t\t{cw.DATE} = {{\n" + "".join(f"\t\t\t{l}\n" for l in lines) + "\t\t}\n\t"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(add_to_history(text, entry), encoding="utf-8")
        changed += 1
    return changed


def cold_war_countries(src: Sources, out: Path, cw) -> int:
    """Append each country's 1949 government to its own history file."""
    files = {f.name[:3]: f for f in src.files("history/countries")}
    done = 0
    for tag, (party, pop, key, name, sub, cosmetic) in cw.COUNTRIES.items():
        if tag in ("PRK", "APL") or tag not in files:
            continue
        f = files[tag]
        dst = out / "history" / "countries" / f.name
        text = read(dst) if dst.exists() else read(f)
        pops = " ".join(f"{k} = {v}" for k, v in pop.items())
        body = [f"set_politics = {{ ruling_party = {party} elections_allowed = {'yes' if party == 'democratic' else 'no'} }}",
                f"set_popularities = {{ {pops} }}", f"recruit_character = APL_cw_{key}"]
        if cosmetic:
            body.append(f"set_cosmetic_tag = {cosmetic}")
        text = text.rstrip() + f"\n\n# The Veiled Hollows: the Cold War start\n{cw.DATE} = {{\n" + \
            "".join(f"\t{b}\n" for b in body) + "}\n"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding="utf-8")
        done += 1
    return done


def cold_war_tech(src: Sources, cw) -> str:
    """APL_cw_set_tech: every country gets the game's technologies up to its 1949 level."""
    techs = []
    for f in src.files("common/technologies"):
        span = block_span(read(f), "technologies")
        if not span:
            continue
        for name, _, body in top_level(read(f)[span[0]:span[1]]):
            if body is None or name.startswith("@"):
                continue
            year = re.search(r"\bstart_year\s*=\s*(\d{4})", body)
            if not year or re.search(r"\bdoctrine\s*=\s*yes|\bxor\s*=|\ballow\s*=", body):
                continue
            techs.append((name, int(year.group(1))))
    groups = {}
    for tag, year in cw.TECH_YEAR.items():
        groups.setdefault(year, []).append(tag)
    out = ["# Generated by build_mod.py from your game's technologies. Do not edit; rebuild instead.",
           "APL_cw_set_tech = {"]

    def give(limit, year):
        names = [n for n, y in techs if y <= year]
        out.append(f"\tevery_country = {{\n\t\tlimit = {{ {limit} }}\n\t\tset_technology = {{\n"
                   + "".join(f"\t\t\t{n} = 1\n" for n in names) + "\t\t\tpopup = no\n\t\t}\n\t}")
    for year, tags in sorted(groups.items()):
        give("OR = { " + " ".join(f"tag = {t}" for t in tags) + " }", year)
    give("NOT = { " + " ".join(f"tag = {t}" for t in cw.TECH_YEAR) + " }", cw.TECH_YEAR_DEFAULT)
    out.append("}")
    print(f"1949 tech:  {len(techs)} technologies, {len([1 for n, y in techs if y <= 1946])} by 1946")
    return "\n".join(out) + "\n"


def find_base(game: Path, wanted: str | None):
    """(profile name, base mod folder or None). --base none forces vanilla; --base <id|path> picks a mod;
    otherwise a subscribed Cold War Iron Curtain is used when present."""
    if not wanted or wanted == "none":
        return "vanilla", None  # the Cold War is built in now; a base mod only when asked for
    if wanted == "cwic":
        wanted = None
    candidates = []
    for lib in steam_libraries() + [game.parents[2]]:
        ws = lib / "steamapps" / "workshop" / "content" / APP_ID
        if ws.is_dir():
            for d in ws.iterdir():
                if (d / "descriptor.mod").exists():
                    m = re.search(r'name\s*=\s*"([^"]+)"', read(d / "descriptor.mod"))
                    candidates.append((m.group(1) if m else d.name, d))
    if wanted:
        picks = [c for c in candidates if wanted in (c[1].name, str(c[1]))] or [(wanted, Path(wanted))]
    else:
        picks = []
        for name, d in candidates:
            for prof, cfg in PROFILES.items():
                if cfg.get("match") and re.search(cfg["match"], name, re.I) and not re.search(r"music|sound", name, re.I):
                    picks.append((name, d))
    if not picks:
        return "vanilla", None
    name, folder = picks[0]
    for prof, cfg in PROFILES.items():
        if cfg.get("match") and re.search(cfg["match"], name, re.I):
            return prof, folder
    sys.exit(f"No profile for base mod '{name}'. Run survey.bat and send the report to the agent.")


def fill_tokens(root: Path, values: dict[str, object]) -> None:
    """Replace {{TOKENS}} in every script file of the built mod."""
    for f in list(root.rglob("*.txt")) + list(root.rglob("*.yml")):
        t = f.read_text(encoding="utf-8-sig") if f.suffix == ".yml" else f.read_text(encoding="utf-8")
        if "{{" in t:
            new = fill(t, values)
            f.write_text(new, encoding="utf-8-sig" if f.suffix == ".yml" else "utf-8")


def build(game: Path, out_root: Path, dry_run: bool, base_arg: str | None = None) -> Path:
    print(f"game:      {game}")
    prof_name, base = find_base(game, base_arg)
    prof = PROFILES[prof_name]
    print(f"world:     {prof['label']}" + (f"  [{base}]" if base else ""))
    src = Sources(game, base)
    index = state_index(src)
    print(f"           {len(index)} states")

    tags = "\n".join(read(f) for f in src.files("common/country_tags"))
    if re.search(rf"^\s*{TAG}\s*=", tags, re.M):
        sys.exit(f"This world already defines the tag {TAG}; change TAG in this script and in the mod files.")

    heart = resolve(index, prof["heartland"], required=True)
    front = resolve(index, prof["frontier"], required=False)
    print("heartland: " + ", ".join(f"{n} ({i})" for n, i in heart.items()))
    print("frontier:  " + (", ".join(f"{n} ({i})" for n, i in front.items()) or "none"))
    capital = prof["capital"] if isinstance(prof["capital"], int) else heart[prof["capital"]]

    provs = {}
    for k, sid in enumerate(list(heart.values())[:3], start=1):
        p = provinces_of(read(index[sid][0]))
        if not p:
            sys.exit(f"No provinces found in the state file for state {sid}.")
        provs[f"P{k}"] = p[0]

    out = out_root / MOD_NAME
    print(f"mod:       {out}")
    if dry_run:
        return out

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(SRC, out)

    # 1. State overrides, written under the same file name as the base file so they replace it.
    for name, sid in heart.items():
        f = index[sid][0]
        dst = out / "history" / "states" / f.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(rewrite_state(read(f)), encoding="utf-8")

    # 2. Files that need IDs. (Git doesn't keep empty folders, so create them.)
    for sub in ("history/countries", "history/units", "common/scripted_effects"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    techs = "\n".join(f"\t{t} = 1" for t in prof["techs"])
    (out / "history" / "countries" / f"{TAG} - Appalachia.txt").write_text(
        fill((TEMPLATES / "APL_history.txt").read_text(), {"CAPITAL": capital, "TECHS": techs}), encoding="utf-8")
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

    # 3. The 1949 Cold War start lives on the vanilla map only.
    cw_files = ["common/bookmarks/APL_cold_war.txt", "common/defines/APL_defines.lua",
                "history/countries/PRK - North Korea.txt"]
    if prof_name == "vanilla":
        import cold_war_1949 as cw
        n_states = cold_war_states(index, set(heart.values()), out, cw)
        n_countries = cold_war_countries(src, out, cw)
        (out / "common" / "scripted_effects" / "APL_cw_tech.txt").write_text(cold_war_tech(src, cw), encoding="utf-8")
        print(f"1949 world: {n_states} states and {n_countries} countries get a {cw.DATE} history entry")
    else:
        for rel in cw_files:
            (out / rel).unlink(missing_ok=True)
        (out / "common" / "scripted_effects" / "APL_cw_tech.txt").write_text("APL_cw_set_tech = { }\n", encoding="utf-8")

    # 4. Ideology names differ between worlds.
    fill_tokens(out, {"ASSEMBLY_PARTY": prof["assembly_party"], "ASSEMBLY_SUBIDEOLOGY": prof["assembly_subideology"]})

    # 5. Descriptors: one inside the folder, one next to it for the launcher. A base mod becomes a
    #    dependency, so the launcher loads it first.
    version = game_version(game)
    inner = (SRC / "descriptor.mod").read_text().replace('supported_version="1.*"', f'supported_version="{version}"')
    if prof["dependency"]:
        inner += f'dependencies={{\n\t"{prof["dependency"]}"\n}}\n'
    (out / "descriptor.mod").write_text(inner, encoding="utf-8")
    (out_root / f"{MOD_NAME}.mod").write_text(inner + f'path="{out.as_posix()}"\n', encoding="utf-8")
    print(f"built for game version {version} on {prof['label']}.")
    if prof["dependency"]:
        print(f"In the launcher, make a playset with '{prof['dependency']}' FIRST and 'The Veiled Hollows' AFTER it.")
    else:
        print("Enable 'The Veiled Hollows' in the launcher's playset.")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", help="Hearts of Iron IV install folder")
    ap.add_argument("--out", help="your '.../Hearts of Iron IV/mod' folder")
    ap.add_argument("--base", help="build on a base mod instead of the unmodded game: a Workshop id or folder, "
                                   "or 'cwic' to find Cold War Iron Curtain (default: none)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    build(find_game(a.game), find_mod_dir(a.out), a.dry_run, a.base)


if __name__ == "__main__":
    main()
