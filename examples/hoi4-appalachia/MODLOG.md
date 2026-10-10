# MODLOG: The Veiled Hollows (HoI4)

## Intake
- Game: Hearts of Iron IV (Clausewitz/Jomini, plain-text script mod). Single-player alt-history. No anti-cheat
  concern: there's no online client to touch, and the mod is ironman-incompatible like any mod.
- Idea, from the user: Appalachia is independent, and its cryptids, rumours and occult are real. Black magic
  at the founding raised an impenetrable barrier so the USA can't immediately retake it. Cryptids and magic
  for the army. Dark and creepy.
- Done means: a mod folder that loads, Appalachia is playable, the barrier works, there are cryptid units and
  rituals, and everything is creepy. It hasn't been verified in game yet: the agent ran in a cloud container
  with no game.

## Route
- Data/scripts only. Everything is HoI4 script: country tag, characters, ideas, focus tree, decisions, events,
  sub-units, equipment, hidden techs, on_actions and scripted effects.
- **The barrier:** the global flag `APL_veil_intact`, plus a weekly hidden pulse event on APL and an
  `on_declare_war` hook. Both fire `appalachia.11` on every enemy, which runs `white_peace = APL`. Strength is
  the variable `APL_veil_strength`, which decays and loses 10 per repel. At 0, `APL_drop_the_veil` runs and the
  USA gets the choice to invade. Chosen over province modifiers or attrition, because a white peace is the only
  barrier that is actually "impenetrable" and can't be cheesed with stacked divisions.
- **Land:** a new tag can't get states without overriding the vanilla state files, and those can't be
  committed. `build_mod.py` reads the user's own install, matches states by English name from
  `localisation/english/*state*`, checks `owner = USA`, and writes the overrides plus the ID-dependent files
  (capital, OOB provinces, `APL_mark_states`, the frontier war goal). Everything else works by state flag, so no
  state IDs are hard-coded.
- **Cryptid units:** `active = no` sub-units, unlocked by hidden technologies with no `folder`, which focuses
  grant with `set_technology`. They need the new `APL_binding_charms` equipment (`can_be_produced =
  { original_tag = APL }`). That equipment carries most of the combat stats, because equipment stats are
  well-defined, while sub-unit additive combat stats aren't.

## Source of truth
- The HoI4 wiki is blocked from the container (proxy 403). raw.githubusercontent.com and `git clone` from
  github.com work. Cloned `cwtools/cwtools-hoi4-config` (the CWTools validation rules, kept current by the
  community) and checked every effect, trigger and modifier name against it with `validate.py --cwt`.
  - It caught `production_speed_arms_factory_factor`, a pattern-generated modifier that isn't listed. Swapped
    it for `production_factory_max_efficiency_factor`.
- Confirmed signatures from the rules: `white_peace` (tag or block form), `has_offensive_war_with`,
  `add_building_construction` with a province block that supports `limit_to_border`, `clamp_variable` with
  variable max, `swap_ideas`, `free_building_slots`, `create_wargoal` with a `generator` list, and the
  `on_declare_war` scope (ROOT and FROM are both countries).

## Art
- fal MCP failed to connect (401), so all art is procedural Pillow in `make_art.py`: bone sigils on blood,
  bruise, moss, ash and coal grounds, fog layers and red eyes.
- Written as uncompressed A8R8G8B8 DDS with a hand-built header (Pillow reads them back, which checks the
  writer). Flags are uncompressed 32-bit TGA at 82x52, 41x26 and 10x7.
- Sizes: focus 95x85, idea 64x64, decision 32x32, decision category 545x102, event 210x176, leader 156x210,
  advisor 65x67. Unit icon (40x40) and equipment icon sizes are guesses.

## Decisions
- Start date: the user chose 1936 over a 1960s Cold War start. The Severance is New Year's Eve 1935.
  `appalachia.1` and `.2` use conditional `desc = { trigger = { date > 1936.6.1 } text = ... }` blocks, so the
  1939 bookmark gets "three years since" text.

## Verification so far
- `validate.py --cwt`: 18 files parse. 263 loc keys, 129 sprites and every texture present. 35 focuses with no
  overlapping positions, 19 ideas, 8 decisions, 19 events, 6 units. All effect, trigger and modifier names are
  known to CWTools.
- Ran `build_mod.py` against a synthetic install (fake IDs 901-908, including a SOV-owned "Georgia" to test
  the owner filter). Correct overrides, generated effects, capital, OOB provinces and descriptors.
- **Not yet verified in game.** Next step: the user builds against their real install, starts a 1936 game as
  APL, reads `logs/error.log`, and reports. Things to watch:
  - the `GFX_unit_*_icon_medium` sizes;
  - the shine sprites;
  - whether techs with no `folder` log errors;
  - whether `[?APL.APL_veil_strength|0]` renders in the USA category description.

## Gotchas
1. A new country only appears in the country picker if it owns states at game setup, so `on_startup`
   `transfer_state` is too late. It has to be state history overrides.
2. Inner straight quotes in loc values break the line parser. `make_loc.py` converts them to curly quotes.
3. `is_triggered_only` events still check `trigger`. `appalachia.11` relies on that to skip countries that
   already made peace.
4. The weekly pulse event re-schedules itself only while the Veil stands. Don't fire it from anywhere else,
   or you get two parallel chains and double decay. The `on_declare_war` hook fires `appalachia.13`, which
   only repels.
