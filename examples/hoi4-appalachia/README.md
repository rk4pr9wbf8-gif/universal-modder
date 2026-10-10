# Hearts of Iron IV: The Veiled Hollows

An alt-history horror mod for Hearts of Iron IV. In this world, the rumours about Appalachia were true: the
cryptids, the haints, the granny witches and the things in the mines. On the night of **the Severance**, a
coven led by the coal baron Silas Blackwood worked black magic on the summit of Spruce Knob. A wall of fog a
mile high rose along every ridge, and West Virginia, Kentucky and Tennessee broke away from the United
States as the **Veiled Commonwealth of Appalachia** (tag `APL`).

![thumbnail](mod/thumbnail.png)

## What's in it

- **A playable nation.** Appalachia starts with West Virginia, Kentucky and Tennessee, with the capital in
  West Virginia. It has a ruling Coven, its own parties, flag, leader, generals and an advisor, and a starting
  army that includes undead.
- **The Veil.** This is the barrier that keeps the USA from immediately taking Appalachia back.
  - While it stands, any war against Appalachia ends in a white peace within a day. The attacker loses
    5,000 manpower and some war support, and gets a creepy event about it.
  - The Veil has a strength from 0 to 100. It loses 1 a week, and 10 every time it repels an enemy.
    At 0 it falls, and the USA decides whether to invade.
  - Appalachia feeds it with rituals: the Blood Tithe (paid in manpower) and Bury the Bones (paid in
    political power). Focuses slow its decay, raise its cap to 150, or bind it forever.
  - The USA gets **Project Lantern**, two decisions that wear the Veil down. So it does fall eventually,
    unless Appalachia keeps feeding it.
- **35-focus tree** in five branches, all with custom icons:
  - **The Veil** forks: the *Eternal Veil* (isolation forever), or *Part the Veil*. Parting leads into the
    *Night March*, with claims and war goals on the rest of old Appalachia: Virginia, the Carolinas,
    Pennsylvania, Ohio, Maryland, Georgia and Alabama. The branch ends with *A Shadow over America*.
  - **The Cryptid Corps** unlocks the monsters (below), Black Furnace Charms, *Children of the Night* and
    *the Wild Hunt*.
  - **The Coven:** granny witch healers, the Bell Witch sent to haunt Washington, dark sermons and the
    Rites of the Black Mountain. It forks between Maw Hettie's matriarchy and a bargain with Old Scratch.
  - **Hollow Industry:** coal and bone, the moonshine economy, the deep mines (something down there knocks
    back), bone foundries, the Hollow Laboratories and the Black Furnace.
- **Cryptid battalions.** Every one of them needs **Binding Charms**, a new equipment that only Appalachia
  can produce.

  | Unit | Role |
  |---|---|
  | Hollow Revenants | cheap undead line infantry; available from the start |
  | Woodbooger Brutes | heavy line infantry, strong in forest and mountains |
  | Sheepsquatch Packs | fast shock troops for hills and forest |
  | Mothman Flock | support company with recon and initiative |
  | Flatwoods Sentinels | support company with suppression |
  | Granny Witches | support company that brings wounded back (like a field hospital) |

- **War rituals** (decisions):
  - Rite of the Blood Moon: attack bonus.
  - Call the Hollow Mist: defence bonus.
  - Raise the Coal-Camp Dead: +15,000 manpower, at a stability cost.
  - Curse of the Black Mountain: a targeted curse on an enemy nation.
- **About 20 events**, including:
  - the Mothman over Point Pleasant;
  - the thing beneath Hollow No. 9;
  - "It Was Not a Deer";
  - Tailypo;
  - the Flatwoods visitors coming down from their hill;
  - the Bell Witch in the West Wing;
  - the Devil at the crossroads.
- **All art is procedural** and original (`make_art.py`): focus icons, national spirits, decision icons,
  unit icons, event pictures, portraits and the flag. No game files and no AI image generation were used.

## Install

You need Hearts of Iron IV and Python 3.8 or newer.

1. Download this folder (`examples/hoi4-appalachia`).
2. **Windows:** double-click `install.bat`. **Linux/macOS:** run `python3 build_mod.py`.
3. Open the Paradox launcher and add **The Veiled Hollows** to a playset. Start a new game and click on
   Appalachia on the map.

The builder looks for the game in your Steam libraries and for your mod folder in Documents (OneDrive
included). If it can't find them:

```
python build_mod.py --game "D:/SteamLibrary/steamapps/common/Hearts of Iron IV" --out "%USERPROFILE%/Documents/Paradox Interactive/Hearts of Iron IV/mod"
python build_mod.py --dry-run        # show the states it found, write nothing
```

### Why there is a builder

Handing states to a new country means overriding the game's own state history files. Those belong to
Paradox and can't be shipped in this repo. `build_mod.py` reads the three files from **your** install,
changes `owner = USA` to `owner = APL`, adds Appalachian cores, and writes them into your local mod folder.
It finds the states by their English names, so it keeps working when a patch renumbers them. It also fills
in the capital, the starting army's provinces and the frontier states. Rebuild after a big game patch.

## If something breaks

Send the agent `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`; it names the file and
line. Things that are likely to need a tweak on a first run:
- unit icons in the division designer (the sprite sizes are a best guess);
- the shine animation on focus icons;
- equipment icons in the production screen.

None of these affect gameplay.

## Compatibility

- Built against the HoI4 script rules from [CWTools](https://github.com/cwtools/cwtools-hoi4-config) as of
  October 2026. It doesn't overwrite any vanilla files except the three Appalachian state histories.
- It's not compatible with mods that change those three states, or that rewrite US history (Kaiserreich, TNO,
  Millennium Dawn).
- **Start date:** the mod runs on the normal 1936/1939 bookmarks. The Severance happens at game start, and
  the lore has no fixed year. A true 1960s start would need every other country's history rewritten for the
  Cold War, which is a separate total conversion.

## Files

| File | What it does |
|---|---|
| `mod/` | the mod itself, minus the parts generated per install |
| `templates/` | the Appalachia history file and starting army, with `{{CAPITAL}}` and province placeholders |
| `build_mod.py` | reads your install, generates the state overrides and the templates, and installs the mod |
| `make_art.py` | draws every texture, written as uncompressed DDS and TGA |
| `make_loc.py` | all English text: names, descriptions, events, tooltips |
| `validate.py` | static checks: syntax, loc keys, sprites, textures, cross-references, CWTools vocabulary |
| `MODLOG.md` | the build journal |

To change text, edit `make_loc.py` and run it. To change art, edit `make_art.py` and run it. Before
building, run `python validate.py --cwt <cwtools-hoi4-config>/Config`.
