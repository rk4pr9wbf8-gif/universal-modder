"""Static checks for The Veiled Hollows, since the game itself isn't available to an agent in the cloud.

    python validate.py                     # syntax, localisation, sprites, textures, cross-references
    python validate.py --cwt <Config dir>  # also check effect / trigger / modifier names against the
                                           # CWTools rules (git clone https://github.com/cwtools/cwtools-hoi4-config)

Checks:
- every .txt parses (balanced braces, no stray tokens) and the .yml is UTF-8 with BOM;
- every focus, idea, decision, event, unit, equipment, tech, character and trait has its loc keys,
  and every custom_effect_tooltip key exists;
- every GFX_ sprite the scripts use is defined in interface/*.gfx and every texture file exists;
- every event id fired is defined, every idea added is defined, every scripted effect called exists;
- with --cwt: effect, trigger and modifier names are known to CWTools.
Exit code 1 on any problem.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE / "mod"
TEMPLATES = HERE / "templates"

TOKEN = re.compile(r'"[^"\n]*"|[{}]|<=|>=|!=|[=<>]|[^\s{}=<>"#]+|#[^\n]*')


class ParseError(Exception):
    pass


def parse(text: str, where: str):
    toks = [t for t in TOKEN.findall(text) if not t.startswith("#")]
    pos = 0

    def block(depth):
        nonlocal pos
        items = []
        while pos < len(toks):
            t = toks[pos]
            if t == "}":
                if depth == 0:
                    raise ParseError(f"{where}: unexpected '}}' (token {pos})")
                pos += 1
                return items
            if t == "{":
                pos += 1
                items.append((None, None, block(depth + 1)))
                continue
            key = t
            pos += 1
            if pos < len(toks) and toks[pos] in ("=", "<", ">", "<=", ">=", "!="):
                op = toks[pos]
                pos += 1
                if pos >= len(toks):
                    raise ParseError(f"{where}: '{key} {op}' at end of file")
                if toks[pos] == "{":
                    pos += 1
                    items.append((key, op, block(depth + 1)))
                else:
                    items.append((key, op, toks[pos]))
                    pos += 1
            else:
                items.append((key, None, None))  # bare value in a list
        if depth != 0:
            raise ParseError(f"{where}: missing '}}' at end of file")
        return items

    return block(0)


def walk(items):
    for k, op, v in items:
        yield k, op, v
        if isinstance(v, list):
            yield from walk(v)


def values(items, key):
    return [v for k, _, v in items if k == key]


# --------------------------------------------------------------------------- loading

def load_all():
    trees = {}
    for f in sorted(MOD.rglob("*.txt")) + sorted(MOD.rglob("*.gfx")) + sorted(TEMPLATES.glob("*.txt")):
        trees[f] = parse(f.read_text(encoding="utf-8-sig"), str(f.relative_to(HERE)))
    return trees


def load_loc():
    keys = {}
    for f in MOD.rglob("*.yml"):
        raw = f.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            PROBLEMS.append(f"{f.name}: localisation must be UTF-8 with BOM")
        if not re.search(r"_l_english\.yml$", f.name):
            PROBLEMS.append(f"{f.name}: file name must end in _l_english.yml")
        for m in re.finditer(r'^ ([\w.]+):\d* "(.*)"$', raw.decode("utf-8-sig"), re.M):
            keys[m.group(1)] = m.group(2)
    return keys


PROBLEMS: list[str] = []


def need(cond, msg):
    if not cond:
        PROBLEMS.append(msg)


# --------------------------------------------------------------------------- CWTools vocabulary

def cwt_vocab(config: Path):
    effects, triggers, modifiers = set(), set(), set()
    for f in config.rglob("*.cwt"):
        t = f.read_text(encoding="utf-8", errors="ignore")
        effects |= set(re.findall(r"alias\[effect:([A-Za-z_0-9]+)\]", t))
        triggers |= set(re.findall(r"alias\[trigger:([A-Za-z_0-9]+)\]", t))
        triggers |= set(re.findall(r"alias\[modifier_rule:([A-Za-z_0-9]+)\]", t))
    mt = (config / "modifiers.cwt").read_text(encoding="utf-8", errors="ignore")
    modifiers |= set(re.findall(r"^\t([a-z_0-9]+) = \w", mt, re.M))
    for f in config.rglob("*.cwt"):
        t = f.read_text(encoding="utf-8", errors="ignore")
        modifiers |= set(re.findall(r"alias\[modifier:([A-Za-z_0-9]+)\]", t))
    return effects, triggers, modifiers


SCOPE_WORDS = {"ROOT", "FROM", "PREV", "THIS", "OWNER", "CONTROLLER", "CAPITAL", "overlord", "faction_leader"}
CONTROL = {"if", "else_if", "else", "limit", "hidden_effect", "hidden_trigger", "OR", "AND", "NOT", "NOR", "NAND",
           "custom_trigger_tooltip", "count_triggers"}


def is_scope_key(k: str) -> bool:
    return k in SCOPE_WORDS or bool(re.fullmatch(r"[A-Z][A-Z0-9]{2}", k)) or k.isdigit() or k.startswith("var:")


def check_block(items, kind, vocab, where, scripted):
    """kind: 'effect' or 'trigger'."""
    effects, triggers, modifiers = vocab
    known = effects if kind == "effect" else triggers
    for k, op, v in items:
        if k is None:
            continue
        if k == "limit" or k in ("trigger", "available", "visible", "allowed"):
            if isinstance(v, list):
                check_block(v, "trigger", vocab, where, scripted)
            continue
        if k in ("OR", "AND", "NOT", "NOR", "NAND") and isinstance(v, list):
            check_block(v, "trigger", vocab, where, scripted)
            continue
        if k in ("if", "else_if", "else", "hidden_effect") and isinstance(v, list):
            check_block(v, kind if k != "hidden_effect" else "effect", vocab, where, scripted)
            continue
        if is_scope_key(k):
            if isinstance(v, list):
                check_block(v, kind, vocab, where, scripted)
            continue
        if k in scripted:
            continue
        if k not in known:
            PROBLEMS.append(f"{where}: unknown {kind} '{k}'")
            continue
        # iterators: their bodies are the same kind (limit is handled above)
        if isinstance(v, list) and re.match(r"(every|random|any|all)_", k):
            check_block(v, kind, vocab, where, scripted)


def check_modifiers(items, vocab, where):
    for k, op, v in items:
        if k and k not in vocab[2]:
            PROBLEMS.append(f"{where}: unknown modifier '{k}'")


# --------------------------------------------------------------------------- main checks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cwt", type=Path, help="cwtools-hoi4-config/Config directory")
    a = ap.parse_args()

    try:
        trees = load_all()
    except ParseError as e:
        print("PARSE ERROR:", e)
        sys.exit(1)
    loc = load_loc()
    rel = lambda f: str(f.relative_to(HERE))
    by = lambda sub: {f: t for f, t in trees.items() if sub in f.as_posix()}

    # ---- sprites
    sprites = {}
    for f, t in by("/interface/").items():
        for blk in values(t, "spriteTypes"):
            for st in values(blk, "spriteType"):
                name = values(st, "name")[0].strip('"')
                tex = values(st, "texturefile")[0].strip('"')
                sprites[name] = tex
                need((MOD / tex).exists(), f"{rel(f)}: {name} -> missing texture {tex}")

    # ---- definitions
    ideas = {k for f, t in by("/common/ideas/").items() for blk in values(t, "ideas") for cat in blk if isinstance(cat[2], list) for k, _, _ in cat[2]}
    events = set()
    for f, t in by("/events/").items():
        for k, _, v in t:
            if k == "country_event":
                events.add(values(v, "id")[0])
    scripted = {k for f, t in by("/scripted_effects/").items() for k, _, _ in t}
    scripted |= {"APL_mark_states", "APL_frontier_wargoal"}  # generated by build_mod.py
    techs = {k for f, t in by("/technologies/").items() for blk in values(t, "technologies") for k, _, _ in blk}
    units = {k for f, t in by("/common/units/APL").items() for blk in values(t, "sub_units") for k, _, _ in blk}
    equipment = {k for f, t in by("/equipment/").items() for blk in values(t, "equipments") for k, _, _ in blk}
    traits = {k for f, t in by("/country_leader/").items() for blk in values(t, "leader_traits") for k, _, _ in blk}
    characters = {k for f, t in by("/characters/").items() for blk in values(t, "characters") for k, _, _ in blk}
    focuses = []
    for f, t in by("/national_focus/").items():
        for tree in values(t, "focus_tree"):
            focuses += values(tree, "focus")
    focus_ids = {values(fc, "id")[0] for fc in focuses}
    decisions = {}
    for f, t in by("/decisions/APL").items():
        for cat, _, blk in t:
            for k, _, v in blk:
                decisions[k] = v
    categories = {k for f, t in by("/decisions/categories/").items() for k, _, _ in t}

    # ---- localisation coverage
    for fid in focus_ids:
        need(fid in loc and fid + "_desc" in loc, f"loc: focus {fid}")
    for i in ideas:
        need(i in loc and i + "_desc" in loc, f"loc: idea {i}")
    for d in list(decisions) + list(categories):
        need(d in loc and d + "_desc" in loc, f"loc: decision {d}")
    for u in units | techs | traits | characters:
        need(u in loc, f"loc: {u}")
    for u in units:
        need(u + "_desc" in loc, f"loc: {u}_desc")
    for e in equipment:
        need(e in loc, f"loc: equipment {e}")
    for f, t in by("/events/").items():
        for k, _, ev in t:
            if k != "country_event" or values(ev, "hidden") == ["yes"]:
                continue
            for key in ("title", "desc"):
                vals = values(ev, key)
                texts = [v if isinstance(v, str) else (values(v, "text") or [None])[0] for v in vals]
                need(texts and all(t in loc for t in texts), f"loc: {values(ev, 'id')[0]} {key}")
            for opt in values(ev, "option"):
                need(values(opt, "name")[0] in loc, f"loc: option {values(opt, 'name')[0]}")
            pic = values(ev, "picture")
            need(pic and pic[0] in sprites, f"gfx: event {values(ev, 'id')[0]} picture {pic}")
    for tag_key in ("APL", "APL_DEF", "APL_ADJ", "APL_neutrality_party"):
        need(tag_key in loc, f"loc: {tag_key}")

    # ---- references from anywhere
    for f, t in trees.items():
        for k, op, v in walk(t):
            if k == "custom_effect_tooltip":
                need(v in loc, f"{rel(f)}: tooltip {v} has no loc")
            if k == "country_event":
                eid = v if isinstance(v, str) else (values(v, "id") or [None])[0]
                if "/events/" in f.as_posix() and isinstance(v, list) and values(v, "title"):
                    continue
                need(eid in events, f"{rel(f)}: fires undefined event {eid}")
            if k in ("add_ideas", "remove_ideas") and isinstance(v, str) and v.startswith("APL_"):
                need(v in ideas, f"{rel(f)}: unknown idea {v}")
            if k in ("idea", "add_idea", "remove_idea", "has_idea") and isinstance(v, str) and v.startswith("APL_"):
                need(v in ideas, f"{rel(f)}: unknown idea {v}")
            if k == "has_completed_focus":
                need(v in focus_ids, f"{rel(f)}: unknown focus {v}")
            if k == "focus" and isinstance(v, str):
                need(v in focus_ids, f"{rel(f)}: unknown focus {v}")
            if k == "set_technology" and isinstance(v, list):
                for tk, _, _ in v:
                    if tk.startswith("APL_"):
                        need(tk in techs, f"{rel(f)}: unknown tech {tk}")
            if k in ("recruit_character", "add_country_leader_trait"):
                need(v in characters | traits, f"{rel(f)}: unknown {k} {v}")
            if k == "icon" and isinstance(v, str) and v.startswith("GFX_"):
                need(v in sprites, f"{rel(f)}: missing sprite {v}")
            if k == "picture" and isinstance(v, str) and v.startswith("GFX_"):
                need(v in sprites, f"{rel(f)}: missing sprite {v}")
            if k == "large" or k == "small":
                need((MOD / v.strip('"')).exists(), f"{rel(f)}: missing portrait {v}")
            if k == "type" and isinstance(v, str) and v.startswith("APL_binding"):
                need(v in equipment, f"{rel(f)}: unknown equipment {v}")
            if k == "enable_subunits":
                for u, _, _ in v:
                    need(u in units, f"{rel(f)}: unknown subunit {u}")
    for i in ideas:
        need(f"GFX_idea_{i}" in sprites, f"gfx: idea {i}")
    for d, body in decisions.items():
        icon = values(body, "icon")
        need(icon and f"GFX_decision_{icon[0]}" in sprites, f"gfx: decision {d} icon {icon}")
    for u in units:
        need(f"GFX_unit_{u}_icon_medium" in sprites, f"gfx: unit {u}")
    for fc in focuses:
        fid = values(fc, "id")[0]
        icon = values(fc, "icon")[0]
        need(icon in sprites and icon + "_shine" in sprites, f"gfx: focus {fid} icon {icon}")
    pos = {}
    for fc in focuses:
        xy = (values(fc, "x")[0], values(fc, "y")[0])
        need(xy not in pos, f"focus {values(fc, 'id')[0]} overlaps {pos.get(xy)} at {xy}")
        pos[xy] = values(fc, "id")[0]

    # ---- CWTools vocabulary
    if a.cwt:
        vocab = cwt_vocab(a.cwt)
        print(f"cwtools: {len(vocab[0])} effects, {len(vocab[1])} triggers, {len(vocab[2])} modifiers")
        for f, t in trees.items():
            w = rel(f)
            for k, op, v in walk(t):
                if not isinstance(v, list):
                    continue
                if k in ("completion_reward", "immediate", "complete_effect", "effect", "remove_effect"):
                    check_block(v, "effect", vocab, w, scripted)
                elif k == "option":
                    check_block([x for x in v if x[0] not in ("name", "ai_chance", "trigger")], "effect", vocab, w, scripted)
                    for tr in values(v, "trigger"):
                        check_block(tr, "trigger", vocab, w, scripted)
                elif k in ("available", "allowed", "visible", "target_trigger", "bypass", "can_be_produced") or (
                        k == "trigger" and "/events/" in f.as_posix()):
                    check_block(v, "trigger", vocab, w, scripted)
                elif k == "modifier" and ("/ideas/" in f.as_posix()):
                    check_modifiers(v, vocab, w)
            if "/country_leader/" in f.as_posix():
                for blk in values(t, "leader_traits"):
                    for name, _, body in blk:
                        check_modifiers([x for x in body if x[0] != "random"], vocab, w)
            if "/scripted_effects/" in f.as_posix() or f.parent == TEMPLATES and f.name == "APL_history.txt":
                for name, _, body in t:
                    if isinstance(body, list) and "/scripted_effects/" in f.as_posix():
                        check_block(body, "effect", vocab, w, scripted)

    for p in sorted(set(PROBLEMS)):
        print("PROBLEM:", p)
    print(f"{len(trees)} files, {len(loc)} loc keys, {len(sprites)} sprites, {len(focus_ids)} focuses, "
          f"{len(ideas)} ideas, {len(decisions)} decisions, {len(events)} events, {len(units)} units")
    print("OK" if not PROBLEMS else f"{len(set(PROBLEMS))} problem(s)")
    sys.exit(1 if PROBLEMS else 0)


if __name__ == "__main__":
    main()
