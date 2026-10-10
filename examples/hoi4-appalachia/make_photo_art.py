"""Photorealistic art for The Veiled Hollows: generate with fal, then fit every picture to what HoI4 loads.

    python make_photo_art.py list                 # every texture, its size and its photo prompt
    python make_photo_art.py generate             # one fal image per missing source, into art_src/ (needs FAL_KEY)
    python make_photo_art.py generate --only APL_the_veil APL_mothman
    python make_photo_art.py apply                # art_src/*.png|jpg|webp -> mod/gfx/**/*.dds
    python make_photo_art.py check                # every referenced texture exists at the right size

`apply` crops each source to the target's aspect, resizes it, grades it to one look (cold, desaturated, crushed
blacks, a vignette) so a set of separate generations reads as one mod, cuts it to the sprite's frame (focus
shield with a bone rim, rounded idea tile, plain square, full bleed) and writes uncompressed DDS with
make_art.save_dds. A texture with no source keeps the procedural art from make_art.py, so the mod always
loads. Sources live in art_src/ (ignored by git); fal_manifest.jsonl there records each request and seed.

Run make_art.py first on a fresh clone (it writes the flags, the .gfx files and the fallbacks), then this.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from make_art import BONE_DIM, SS, save_dds, shield_mask

HERE = Path(__file__).resolve().parent
MOD = HERE / "mod"
SRC = HERE / "art_src"
UM = HERE.parents[1] / "bin" / "um"

STYLE = ("photorealistic, 35mm film photograph, 1930s Appalachia, folk horror, low-key lighting, cold fog, "
         "muted desaturated colours, deep shadows, sharp focus, no text, no letters, no watermark, no border")
ICON = "a single clear subject centred, readable at a small size, dark plain background"

# ------------------------------------------------------------- the catalogue: texture -> (frame, size, subject)
# frames: shield (focus), tile (idea/decision/bop: rounded square), square (unit/equipment), bleed (full picture),
# portrait (leader), face (advisor-sized leader crop of the same source)

FOCUS = {
    "the_severance": "a vast dome of fog rising over a mountain ridge at night, a single giant eye glowing inside it",
    "feed_the_veil": "a drop of blood falling onto a wall of fog over a mountain pass",
    "wardstones": "a ring of ancient standing stones carved with sigils in a misty Appalachian clearing",
    "hollow_mist": "a pale human eye staring out of thick fog between pine trees",
    "seal_the_passes": "a rusted iron padlock and chain across a narrow mountain road swallowed by fog",
    "whispers_in_the_fog": "a gaunt open mouth whispering out of the fog, lips barely visible",
    "eternal_veil": "an occult sigil burned into rock beneath a dome of glowing fog",
    "part_the_veil": "a torn curtain of fog with red light behind it, mountains beyond",
    "beyond_the_ridges": "soldiers in 1930s greatcoats cresting a misty Appalachian ridge at dawn",
    "the_night_march": "a column of skeletal soldiers marching under a crescent moon",
    "the_mountains_remember": "a mountainside with a giant eye formed by rock and shadow, fog below",
    "a_shadow_over_america": "the shadow of a huge winged moth-man spreading over a small American town at dusk",
    "call_of_the_hollows": "a pale bony hand reaching out of dark moss and leaves",
    "the_mothman_compact": "the Mothman, a tall dark winged creature with glowing red eyes, perched on a bridge girder",
    "wake_the_woodboogers": "a hulking hairy wild man of the woods, eyes catching the light, in dense forest",
    "binding_charm_forges": "a blacksmith hammering a glowing occult iron charm on an anvil, sparks flying",
    "sheepsquatch_herds": "a horned white-furred beast with a ram's skull face standing in a foggy creek bed",
    "the_flatwoods_visitors": "the Flatwoods monster, a tall hooded figure with a spade-shaped head and glowing face, in dark woods",
    "children_of_the_night": "dozens of glowing red eyes in a dark forest under a crescent moon",
    "the_wild_hunt": "a spectral rider with a huge antlered helm galloping through mist",
    "convene_the_coven": "thirteen black candles burning in a circle on a wooden floor, wax dripping",
    "granny_witch_healers": "an old Appalachian granny witch in a shawl holding bundles of dried herbs",
    "the_bell_witch": "an old iron bell hanging in a dark cabin, a pale ghostly hand touching it",
    "the_dark_sermons": "a worn black Bible open on a pulpit of a ruined mountain church, candlelight",
    "rites_of_the_black_mountain": "an occult sigil painted in blood on a black rock face",
    "the_matriarch": "a veiled old woman in black mourning clothes, face hidden, holding a lantern",
    "bargain_with_old_scratch": "a horned devilish silhouette offering a handshake at a crossroads at night",
    "the_hollow_crown": "a crude iron crown wrapped in thorns and bone on a moss-covered stump",
    "coal_and_bone": "a coal miner's pickaxe resting on a pile of coal and old bones",
    "moonshine_economy": "a stoneware moonshine jug beside a copper still in the woods at night",
    "the_deep_mines": "the timbered mouth of a deep coal mine shaft, a lantern glowing far inside",
    "bone_foundries": "a smoking brick foundry chimney against a red night sky",
    "valley_of_dams": "a concrete hydroelectric dam in a misty Appalachian valley",
    "the_hollow_laboratories": "a glass laboratory flask glowing green on a cluttered 1930s workbench",
    "the_black_furnace": "a roaring black iron furnace mouth full of flames",
    "the_creeping_fog": "a bank of fog rolling down a mountainside over farmland",
    "the_fog_rolls_east": "fog pouring over mountain ridges toward a distant lit city",
    "fog_without_end": "an endless sea of fog with an eye of light glowing in its centre",
    "the_midnight_pact": "a circle of candles under a full moon on a stone altar",
    "la_llorona": "a weeping woman in a white dress at the edge of a dark river",
    "the_banshee_wails": "a pale screaming woman with long white hair in an Irish mist",
    "strigoi": "a Romanian vampire with a gaunt pale face under a crescent moon",
    "the_draugr_wake": "a frost-covered Norse undead warrior's skull helm in a burial mound",
    "the_migoi_descend": "a giant snow footprint on a Himalayan mountain slope",
    "the_mapinguari_stirs": "a huge shaggy Amazonian beast with one eye looming in the rainforest",
    "a_world_of_nightmares": "an occult sigil glowing over a world map in a dark war room",
    "the_veil_shelters_the_pact": "a dome of fog sheltering a circle of burning candles",
}

IDEAS = {
    "the_veil": "a towering wall of fog over mountain ridges at night",
    "blood_price": "a single drop of blood on a stone",
    "blood_price_eased": "a drop of blood on green moss",
    "hollow_folk": "a hollow-eyed Appalachian farmer staring from a cabin doorway",
    "hollow_mist_spirit": "a pale eye in drifting mist",
    "children_of_the_night_spirit": "red eyes in a dark forest under a crescent moon",
    "the_wild_hunt_spirit": "a ghostly antlered rider in mist",
    "moonshine_economy_spirit": "a moonshine jug by a copper still",
    "old_scratch_bargain": "a horned silhouette at a crossroads",
    "the_black_furnace_spirit": "flames in a black iron furnace",
    "the_eternal_veil": "an occult sigil glowing in fog",
    "veil_parted": "a torn wall of fog with red light behind it",
    "blood_moon": "a blood-red full moon over pines",
    "mist_rite": "a hooded figure performing a rite in mist",
    "black_mountain_curse": "a human skull on black rock",
    "fog_madness": "a screaming face half dissolved in fog",
    "bell_witch_torment": "an old iron bell in a dark cabin",
    "veil_shattered": "shattered fog with grey daylight breaking through",
    "the_matriarch_spirit": "a veiled old woman holding a lantern",
    "awakened_folklore": "an old book of folk tales open with a moth on the page",
    "black_library": "shelves of black leather occult books by candlelight",
    "cheat_god": "a golden crown glowing on a dark altar",
}

DECISIONS = {
    "blood_tithe": "a drop of blood falling into a wooden bowl",
    "bury_the_bones": "bones in a fresh grave",
    "blood_moon": "a blood-red full moon",
    "hollow_mist": "a pale eye in fog",
    "curse": "a skull with a nail through it",
    "raise_the_dead": "a hand bursting from a grave",
    "lantern": "a 1930s military searchlight beam cutting through fog",
    "creeping_fog": "a bank of fog rolling over a hill",
    "council": "black candles in a circle",
    "treasury": "a moonshine jug full of silver coins",
    "charms": "an iron occult charm on a leather cord",
    "library": "an old black leather book",
    "cold_war": "a red eye glowing in darkness",
    "cheat": "a golden crown",
}

CATEGORIES = {
    "rites": "wide panorama of a ritual circle on a mountain summit at night, occult sigil glowing in fog",
    "lantern": "wide panorama of 1930s US Army searchlights probing a wall of fog over mountains",
    "council": "wide panorama of thirteen hooded figures around a long table lit by candles",
    "cheats": "wide panorama of a golden crown on an altar in a dark cavern, gold light",
}

BOP = {
    "coven_side": "an occult sigil painted in blood, candlelit",
    "assembly_side": "a coal miner's pickaxe and helmet lamp",
}

UNITS = {
    "hollow_revenants": "an undead soldier in a 1930s uniform with a skull face",
    "mothman_flock": "the Mothman with spread wings and glowing red eyes",
    "woodbooger_brutes": "a hulking hairy wild man of the woods",
    "sheepsquatch_packs": "a white-furred horned beast with a ram's skull face",
    "flatwoods_sentinels": "the Flatwoods monster with its spade-shaped hood and glowing face",
    "granny_witches": "an old granny witch in a shawl holding herbs and a charm",
}

EQUIPMENT = "an iron occult binding charm on a leather cord, engraved sigils, on dark cloth"

EVENTS = {
    "fog": "a 1930s Appalachian village swallowed by fog at night, red eyes among the trees",
    "severance": "a wall of fog a mile high rising along a mountain ridge on New Year's Eve, people watching from a road",
    "mothman": "the Mothman with glowing red eyes standing on a 1930s steel bridge at night",
    "mine": "coal miners in a lamplit mine tunnel recoiling from something in the dark",
    "not_deer": "a deer-like creature standing upright on its hind legs at the edge of a dark forest road",
    "witch": "an old granny witch in a cabin doorway, herbs drying, lantern light",
    "ritual": "hooded cultists performing a blood ritual in a stone circle on a mountain at night",
    "veil_falls": "a wall of fog collapsing over mountains, soldiers in 1930s gear watching in fear",
    "flatwoods": "the Flatwoods monster glowing in a dark hillside field, a group of terrified boys with a flashlight",
    "tailypo": "a strange long-tailed creature at the window of a mountain cabin at night",
}

LEADERS = {
    "silas_blackwood": "a coal baron in a 1930s black three-piece suit, cold eyes, a moth pin on his lapel",
    "maw_hettie_crane": "an elderly Appalachian granny witch in a dark shawl, pale green eyes",
    "jeremiah_coalbrook": "a weathered middle-aged coal miners' union leader in a work shirt",
    "the_pale_lieutenant": "a gaunt deathly pale army officer in a 1930s uniform, sunken white eyes",
    "big_john_kessler": "a huge bearded coal miner foreman with a helmet lamp",
    "reverend_ezra_pike": "a stern hellfire preacher in a black frock coat holding a worn Bible",
    "dr_lucille_varner": "a 1930s woman scientist in a lab coat with round glasses, faint green glow on her face",
}
PORTRAIT = ("waist-up portrait facing the viewer, plain dark background, studio photograph, like an official "
            "government portrait from 1936")


def catalogue() -> list[dict]:
    """Every texture this script can draw: path (under mod/), size, frame, aspect, source stem, prompt."""
    out = []

    def add(path, size, frame, stem, subject, aspect, kind=ICON):
        out.append(dict(path=path, size=size, frame=frame, stem=stem, aspect=aspect,
                        prompt=f"{subject}. {kind}. {STYLE}"))

    for k, s in FOCUS.items():
        add(f"gfx/interface/goals/APL_{k}.dds", (95, 85), "shield", f"goal_{k}", s, "1:1")
    for k, s in IDEAS.items():
        add(f"gfx/interface/ideas/APL_{k}.dds", (64, 64), "tile", f"idea_{k}", s, "1:1")
    for k, s in DECISIONS.items():
        add(f"gfx/interface/decisions/APL_{k}.dds", (32, 32), "tile", f"decision_{k}", s, "1:1")
    for k, s in CATEGORIES.items():
        add(f"gfx/interface/decisions/APL_{k}_category.dds", (545, 102), "bleed", f"category_{k}", s, "21:9",
            "cinematic wide shot, subject in the centre third")
    for k, s in BOP.items():
        add(f"gfx/interface/bop/APL_{k}.dds", (80, 80), "tile", f"bop_{k}", s, "1:1")
    for k, s in UNITS.items():
        add(f"gfx/interface/units/APL_{k}.dds", (40, 40), "square", f"unit_{k}", s, "1:1")
    for k in ("binding_charms", "binding_charms_1", "binding_charms_2"):
        add(f"gfx/interface/equipment/APL_{k}_medium.dds", (120, 64), "tile", "equipment_binding_charms", EQUIPMENT, "16:9")
        add(f"gfx/interface/equipment/APL_{k}_small.dds", (32, 32), "tile", "equipment_binding_charms", EQUIPMENT, "16:9")
    for k, s in EVENTS.items():
        add(f"gfx/event_pictures/APL_{k}.dds", (210, 176), "bleed", f"event_{k}", s, "5:4",
            "documentary photograph, a scene with depth")
    for k, s in LEADERS.items():
        add(f"gfx/leaders/APL/APL_{k}.dds", (156, 210), "portrait", f"leader_{k}", s, "3:4", PORTRAIT)
        if (MOD / f"gfx/leaders/APL/APL_{k}_small.dds").exists():
            add(f"gfx/leaders/APL/APL_{k}_small.dds", (65, 67), "face", f"leader_{k}", s, "3:4", PORTRAIT)
    return out


def referenced() -> dict[str, str]:
    """texture path -> where it's referenced, from the .gfx files and the character portraits."""
    refs = {}
    for f in sorted((MOD / "interface").glob("*.gfx")):
        for p in re.findall(r'(?:texturefile|animationmaskfile)\s*=\s*"([^"]+)"', f.read_text()):
            refs.setdefault(p, f.name)
    for f in sorted((MOD / "common").rglob("*.txt")):
        for p in re.findall(r'"(gfx/[^"]+\.(?:dds|tga|png))"', f.read_text(encoding="utf-8-sig")):
            refs.setdefault(p, f.relative_to(MOD).as_posix())
    return refs


# ------------------------------------------------------------- fitting

def find_source(stem: str) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        if (SRC / f"{stem}{ext}").exists():
            return SRC / f"{stem}{ext}"
    return None


def grade(img: Image.Image, strength: float = 1.0) -> Image.Image:
    """One look for every picture: desaturated, a little cold, crushed blacks, vignette."""
    rgb = img.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(1 - .35 * strength)
    rgb = ImageEnhance.Contrast(rgb).enhance(1 + .15 * strength)
    r, g, b = rgb.split()
    rgb = Image.merge("RGB", (r.point(lambda v: v * (1 - .06 * strength)), g, b.point(lambda v: min(255, v * (1 + .05 * strength)))))
    w, h = rgb.size
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-w * .25, -h * .25, w * 1.25, h * 1.25], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(min(w, h) * .18))
    dark = Image.new("RGB", (w, h), (6, 5, 8))
    return Image.composite(rgb, dark, Image.eval(vig, lambda v: int(90 + v * 165 / 255))).convert("RGBA")


def fit(src: Image.Image, size, frame: str) -> Image.Image:
    w, h = size
    if frame == "face":  # head and shoulders from the top of a portrait
        sw, sh = src.size
        side = int(sw * .62)
        src = src.crop(((sw - side) // 2, int(sh * .04), (sw + side) // 2, int(sh * .04) + side))
    # downscale in two steps with a touch of sharpening, so small icons stay crisp
    big = ImageOps.fit(src.convert("RGB"), (w * 4, h * 4), Image.LANCZOS, centering=(.5, .42 if frame == "portrait" else .5))
    img = grade(big, .6 if frame in ("square", "tile") and w <= 40 else 1.0).resize((w, h), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=60 if w <= 64 else 35, threshold=2))
    if frame == "shield":
        out = Image.new("RGBA", size, (0, 0, 0, 0))
        out.paste(img, (0, 0), shield_mask(size))
        rim = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        W, H = w * SS, h * SS
        ImageDraw.Draw(rim).polygon([(W * .14, H * .06), (W * .86, H * .06), (W * .9, H * .55), (W * .5, H * .97), (W * .1, H * .55)],
                                    outline=BONE_DIM, width=int(SS * 1.6))
        out.alpha_composite(rim.resize(size, Image.LANCZOS))
        return out
    if frame == "tile":
        mask = Image.new("L", (w * SS, h * SS), 0)
        inset = SS * (1 if min(w, h) <= 32 else 2)
        ImageDraw.Draw(mask).rounded_rectangle([inset, inset, w * SS - inset, h * SS - inset],
                                               radius=SS * (3 if min(w, h) <= 32 else 6), fill=255)
        out = Image.new("RGBA", size, (0, 0, 0, 0))
        out.paste(img, (0, 0), mask.resize(size, Image.LANCZOS))
        return out
    return img


# ------------------------------------------------------------- commands

def cmd_list(_args) -> None:
    for e in catalogue():
        src = find_source(e["stem"])
        print(f"{e['path']:58} {e['size'][0]:>3}x{e['size'][1]:<3} {e['frame']:8} {'have' if src else 'need'}  {e['prompt'][:90]}")


def cmd_generate(args) -> None:
    SRC.mkdir(exist_ok=True)
    todo, seen = [], set()
    for e in catalogue():
        if e["stem"] in seen or (args.only and not any(o in e["path"] or o == e["stem"] for o in args.only)):
            continue
        seen.add(e["stem"])
        if find_source(e["stem"]) and not args.force:
            continue
        todo.append(e)
    print(f"{len(todo)} images to generate into {SRC}")
    for i, e in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {e['stem']}", flush=True)
        cmd = [str(UM), "fal", "image", e["prompt"], "--out", str(SRC), "--name", e["stem"], "--aspect", e["aspect"], "--res", "1K"]
        if args.dry_run:
            print("  ", " ".join(cmd[:3]), "...")
            continue
        r = subprocess.run(cmd)
        if r.returncode:
            sys.exit(f"fal failed on {e['stem']}; fix it and run again (finished sources are kept)")


def cmd_apply(_args) -> None:
    done = kept = 0
    for e in catalogue():
        src = find_source(e["stem"])
        if not src:
            kept += 1
            continue
        save_dds(fit(Image.open(src), e["size"], e["frame"]), MOD / e["path"])
        done += 1
    print(f"{done} textures written from photos, {kept} kept procedural")


def cmd_check(_args) -> int:
    sizes = {e["path"]: tuple(e["size"]) for e in catalogue()}
    bad = 0
    for path, where in sorted(referenced().items()):
        f = MOD / path
        if not f.exists():
            if path.startswith("gfx/interface/goals/shine_overlay"):  # vanilla texture, loaded from the game
                continue
            print(f"MISSING  {path}  (referenced in {where})")
            bad += 1
            continue
        try:
            got = Image.open(f).size
        except OSError as ex:
            print(f"UNREADABLE  {path}: {ex}")
            bad += 1
            continue
        if path in sizes and got != sizes[path]:
            print(f"SIZE  {path}: {got[0]}x{got[1]}, want {sizes[path][0]}x{sizes[path][1]}")
            bad += 1
    photos = sum(1 for e in catalogue() if find_source(e["stem"]))
    print(f"{len(referenced())} referenced textures, {bad} problems; {photos}/{len(catalogue())} have a photo source")
    return 1 if bad else 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    g = sub.add_parser("generate")
    g.add_argument("--only", nargs="*", help="texture names or source stems to (re)generate")
    g.add_argument("--force", action="store_true", help="regenerate sources that already exist")
    g.add_argument("--dry-run", action="store_true")
    g.set_defaults(fn=cmd_generate)
    sub.add_parser("apply").set_defaults(fn=cmd_apply)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    args = ap.parse_args()
    sys.exit(args.fn(args) or 0)


if __name__ == "__main__":
    main()
