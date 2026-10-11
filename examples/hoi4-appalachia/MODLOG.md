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

## Round 2: the Midnight Pact and the creeping fog
- User asked for focuses to bring cryptids to life abroad to make allies, and for focuses and decisions to
  expand the barrier to other states.
- Pact: `create_faction = APL_midnight_pact`, then one invite focus per country (MEX, IRE, ROM, NOR, TIB, BRA),
  each with `bypass` if the country is gone. Accepting runs `APL_join_the_pact`: an idea, hidden techs, charms,
  and `add_to_faction` (or a guarantee if APL isn't a faction leader). Binding Charms and the hidden techs now
  allow `has_idea = APL_awakened_folklore`.
- Fog: a state-targeted timed decision (`state_target = yes`, FROM = state, `days_remove = 45`,
  `remove_effect` does `transfer_state = FROM`). Targets are USA-owned states bordering APL, either flagged
  frontier states or any state after *Fog Without End*.
- Sheltering allies: `APL_shelter_the_pact` runs from the weekly pulse and the on_declare_war event. For each
  faction member, every enemy with `has_offensive_war_with = PREV` gets `white_peace = PREV`.

### Gotchas found this round
5. **`NOR` is Norway's tag and the logical NOR operator.** `NOR = { is_in_faction = no }` in a trigger is
   logic, not Norway. Use `any_country = { tag = NOR ... }` in triggers and `every_country = { limit = { tag =
   NOR } ... }` in effects. validate.py now flags it.
6. A focus and a national spirit (or a decision category) with the same name share loc keys, so one shows the
   other's description. Six spirits clashed with their focuses; they're now `*_spirit`. validate.py now checks
   for clashes.
7. A zip download (or git) doesn't keep empty folders. build_mod.py crashed on a real install writing into
   `history/countries`, so it now creates the folders first.

## Round 3: Cold War submod, government, economy, research, cheats
- The user wanted a Cold War timeline, revamped nations and research trees, photorealistic icons, more
  decisions, a realistic government, an economy and a cheat menu. They chose to build on Cold War Iron
  Curtain: A World Divided (Workshop 1458561226) rather than write a total conversion.
- The fal key is rejected (401), and the MCP and REST both fail. Photorealistic art waits on a valid
  `FAL_KEY`. The rest of the art is procedural.
- `survey_base_mod.py` reads the base mod layered over vanilla (respecting `replace_path`) and writes a
  names-only report. On CWIC 0.9 for HoI4 1.19.3:
  - starts 1949.5.23; 2045 states; 545 tags;
  - money in the variable `currentMoney`;
  - rifles are `infantry_equip_1`-`5`, not `infantry_weapons`;
  - ideologies are split (Social_Democratic/social_democrat, etc.); neutrality/despotism still exist;
  - America is split into regions. There are two states called "Charleston": 364 is South Carolina's, 859
    is West Virginia's.
- The user's CWIC crash was `EXCEPTION_ACCESS_VIOLATION` in `atio6axx.dll` (the AMD OpenGL driver), launched
  with `--opengl`. It's not a script error. Fix: the DirectX 11 renderer.
- The builder now has profiles (vanilla by state name; CWIC by id with the name checked), layered sources,
  `{{TOKENS}}` filled in every built file (ideology names), and a `dependencies` entry in the descriptor.
- Government: a balance of power `APL_coven_balance` with 7 ranges; extremes fire events; the Assembly
  event switches `ruling_party` and recruits a leader whose sub-ideology is a token.
- Economy: the `APL_treasury` variable, ticked by a self-scheduling monthly event; `num_divisions` is a
  built-in variable for upkeep; the debt penalty is a dynamic modifier with `remove_trigger`.
- Research: timed decisions (`days_remove` + `remove_effect`) paid with `custom_cost_trigger` /
  `custom_cost_text`. They add to variables that the `APL_black_library` dynamic modifier reads.

### Gotchas found this round
8. A `{{TOKEN}}` mentioned in a template comment gets filled too. A multi-line value then spills out of the
   comment and breaks the file. validate.py now flags placeholders in comments.
9. A base mod's `replace_path` hides vanilla's folder, but a submod's files in that folder still load.
   That's why the submod can add `common/on_actions`, `common/units`, `history/countries` and so on.

## Round 4: our own Cold War (stage 1, the 1949 world)
- Cold War Iron Curtain crashed the user's laptop: first in the AMD OpenGL driver; then at "Loading sprites"
  (fixed by raising AMD Variable Graphics Memory from 0.5 GB to 8 GB); then at "Select country". An
  outdated vanilla-built Veiled Hollows in the same playset could explain the last one. The user chose to
  drop the base mod and have the agent build a Cold War on vanilla.
- The user asked to use the base mod's art. The agent declined, because it belongs to that mod's authors.
  Alternatives offered: public-domain US government and Wikimedia photos, vanilla assets by reference, fal.
- `survey --vanilla` dumped all 1083 states (id, name, owner, cores) and every country history. Vanilla
  1.19.3 already has DDR, WGR, ISR, PAK, RAJ, INS, KOR, PRC, FOR, VIN, LAO and CAM. There's no North
  Korea, so the mod adds PRK.
- Route: a dated `1949.5.23 = { owner = X controller = X }` entry inside each state's history, and a
  dated government entry in each country's history. That's the native mechanism the 1939 bookmark uses,
  so the 1949 map shows on the selection screen. `owner_at()` replays vanilla's own dated entries, so
  states annexed in 1939 (Austria, Bohemia, Memel) revert. In the fixture, 183 states and 51 countries
  changed.
- Leaders, factions, puppets, capitals, cosmetic names and the Chinese Civil War run in on_startup behind
  `date > 1949.1.1` (`APL_cw_setup_1949`). Technology: `APL_cw_set_tech`, generated from the game's own
  technologies by start_year, skipping doctrines, `xor` branches and `allow`-gated techs.
- Vanilla `NGame.END_DATE` is 1949.1.1, so `common/defines/APL_defines.lua` moves it to 2000.
- Tested against a fake install rebuilt from the report: all 1081 states and 364 country files. All 179
  table names match the user's install.

### Gotchas found in the first 1949 test
10. The installer still auto-picked Cold War Iron Curtain because it was subscribed. It built CWIC state
    files (Morgantown, Franklin…) into a vanilla game, and the game crashed right after "Loaded 13414
    provinces". The builder now builds for vanilla unless `--base` asks for a base mod.
11. `on_activate` in a balance of power doesn't accept a bare `limit`, though CWTools allows it. The game
    logs "Invalid effect 'limit'". Wrap it in `if = { limit = { } }`. validate.py now flags it.
12. `recruit_character` only works in history files ("should only happen in game/history files"). The
    Assembly's leader is recruited at game start and takes over when his party rules.
13. Giving the iGPU 8 GB of Variable Graphics Memory left the game 7.7 GB of system RAM. Vanilla needs
    less VRAM than CWIC, so 4 GB is the better split.

### Second 1949 test: 1936 loads, 1949 crashes after history
- game.log reached "Executing History from 2.1.1.1 to 1949.5.23.12", then an access violation in hoi4.exe.
  The 1936 start loaded fine.
14. "Invalid scope type for effect set_politics in history/countries/NOR - Norway.txt line 444": the
    country file ends inside an unclosed block, so an entry appended at the end lands inside it. The
    builder now counts braces and closes them first.
15. Cosmetic tags (RAJ_INDIA, PER_IRAN, SIA_THAILAND) look for flags under the new name. The builder copies
    the user's own `<TAG>.tga` flags to the cosmetic name, and the tags are set in on_startup, not history.
16. WGR's and CHI's history capitals (Berlin, Nanjing) belong to other countries in 1949. A
    `set_capital` now goes in the dated history entry, not only in on_startup.
17. `APL_cw_setup_1949` writes `log = "The Veiled Hollows 1949: <step>"` lines to game.log, so the next
    crash report shows the last step reached.

### Third 1949 test: same crash, so the vanilla start dates go
18. Still crashing right after "Executing History … to 1949.5.23". The most likely cause: on the way to
    1949, the game also replays vanilla's 1939 country entries (1939 armies, puppets, factions) for
    countries that no longer exist in 1949 (GER, MAN, MEN…).
    - The user agreed to replace the vanilla start dates. The descriptor gets
      `replace_path="common/bookmarks"`, and 1949 is the only (default) bookmark.
    - `sanitize_history()` drops every dated entry and every top-level `oob`, `set_*_oob`, `puppet`,
      `set_autonomy`, faction, guarantee and diplomacy statement (and `if` blocks holding them) from all
      country histories.
    - `APL_cw_setup_1949` then raises armies: a 6-infantry template and `create_unit` with a `count` per
      country (cold_war_1949.ARMY).
19. Inside `every_country` during on_startup, ROOT is empty. Use THIS for `create_unit`'s owner.

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
