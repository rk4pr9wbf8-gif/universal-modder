"""Generate the big decision files for The Veiled Hollows from tables.

    python make_decisions.py      # writes mod/common/decisions/APL_state_decisions.txt and the categories

Four categories live here (the Veil rituals, the creeping fog and Project Lantern stay hand-written in
APL_decisions.txt):
- The Council of Thirteen: steer the balance between the Coven and the Mountain Assembly.
- The Hollow Treasury: earn and spend Hollow Scrip, and trade it for a Cold War mod's dollars.
- The Black Library: occult research projects in three tiers, paid in scrip, that feed one spirit.
- Cold War Intrigue: Moscow, Washington, Oak Ridge.
- The cheat menu, for any human player.
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "mod" / "common" / "decisions" / "APL_state_decisions.txt"
CATS = HERE / "mod" / "common" / "decisions" / "categories" / "APL_state_categories.txt"


def block(name, body, indent=1):
    t = "\t" * indent
    inner = "\n".join(t + "\t" + line if line else "" for line in body.strip("\n").split("\n"))
    return f"{t}{name} = {{\n{inner}\n{t}}}\n"


def scrip_cost(n):
    """Decisions that cost Hollow Scrip instead of political power."""
    return (f"custom_cost_trigger = {{\n\tcheck_variable = {{ APL_treasury > {n - 1} }}\n}}\n"
            f"custom_cost_text = APL_cost_{n}_scrip\n")


def pay(n):
    return f"add_to_variable = {{ APL_treasury = -{n} }}\n"


def gain(n):
    return f"add_to_variable = {{ APL_treasury = {n} }}\ncustom_effect_tooltip = APL_gain_{n}_scrip_tt\n"


SCRIP_COSTS, SCRIP_GAINS = set(), set()


def decision(name, icon, *, cost=None, scrip=None, visible="", available="", effect="", days_re_enable=None,
             fire_only_once=False, ai=1, days_remove=None, remove_effect="", extra=""):
    body = f"icon = {icon}\n"
    if visible:
        body += f"visible = {{\n{indent(visible)}\n}}\n"
    if available:
        body += f"available = {{\n{indent(available)}\n}}\n"
    if scrip:
        SCRIP_COSTS.add(scrip)
        body += scrip_cost(scrip)
    if cost is not None:
        body += f"cost = {cost}\n"
    if fire_only_once:
        body += "fire_only_once = yes\n"
    if days_re_enable:
        body += f"days_re_enable = {days_re_enable}\n"
    if days_remove:
        body += f"days_remove = {days_remove}\n"
    body += extra
    eff = (pay(scrip) if scrip else "") + effect
    body += f"complete_effect = {{\n{indent(eff)}\n}}\n"
    if remove_effect:
        body += f"remove_effect = {{\n{indent(remove_effect)}\n}}\n"
    body += f"ai_will_do = {{\n\tfactor = {ai}\n}}\n"
    return block(name, body)


def indent(s):
    return "\n".join("\t" + l if l else "" for l in s.strip("\n").split("\n"))


def g(n):
    SCRIP_GAINS.add(n)
    return gain(n)


BOP = "add_power_balance_value = {{\n\tid = APL_coven_balance\n\tvalue = {v}\n}}\n"

# --------------------------------------------------------------------------- the Council of Thirteen
council = [
    decision("APL_court_the_coven", "APL_council", cost=50, days_re_enable=60,
             effect=BOP.format(v=-0.10)),
    decision("APL_court_the_assembly", "APL_council", cost=50, days_re_enable=60,
             effect=BOP.format(v=0.10)),
    decision("APL_purge_the_union_halls", "APL_curse", cost=100, days_re_enable=180,
             available="has_manpower > 2000",
             effect=BOP.format(v=-0.25) + "add_stability = -0.05\nadd_manpower = -2000\n"),
    decision("APL_grant_the_miners_charter", "APL_treasury", scrip=100, days_re_enable=180,
             effect=BOP.format(v=0.20) + "add_stability = 0.03\n"),
    decision("APL_snake_handler_revival", "APL_council", scrip=50, days_re_enable=120,
             effect=BOP.format(v=-0.05) + "add_war_support = 0.05\n"),
    decision("APL_county_courthouse_elections", "APL_council", cost=75, days_re_enable=365,
             effect=BOP.format(v=0.10) + "add_stability = 0.05\n"),
    decision("APL_call_a_council_moot", "APL_council", cost=25,
             visible="NOT = { has_country_flag = APL_moot_cooldown }",
             effect="country_event = { id = appalachia_gov.2 }\n"),
]

# --------------------------------------------------------------------------- the Hollow Treasury
treasury = [
    decision("APL_moonshine_run", "APL_treasury", cost=10, days_re_enable=30,
             effect=g(40) + "add_stability = -0.01\n", ai=3),
    decision("APL_company_scrip", "APL_treasury", cost=50, days_re_enable=60, effect=g(60), ai=2),
    decision("APL_coal_for_the_world", "APL_treasury", cost=25, days_re_enable=90,
             available="has_war = no", effect=g(80), ai=3),
    decision("APL_sell_charms_abroad", "APL_charms", cost=10, days_re_enable=90,
             available="has_equipment = { APL_binding_charms > 999 }",
             effect="add_equipment_to_stockpile = {\n\ttype = APL_binding_charms_1\n\tamount = -1000\n\tproducer = APL\n}\n"
                    + g(120), ai=1),
    decision("APL_war_bonds_of_the_hollows", "APL_treasury", cost=25, days_re_enable=180,
             available="has_war = yes", effect=g(150) + "add_stability = -0.05\nadd_war_support = -0.05\n", ai=2),
    decision("APL_scrip_for_dollars", "APL_treasury", scrip=200, days_re_enable=90,
             visible="has_variable = currentMoney",
             effect="add_to_variable = { currentMoney = 5 }\ncustom_effect_tooltip = APL_gain_5_dollars_tt\n"),
    decision("APL_dollars_for_scrip", "APL_treasury", cost=10, days_re_enable=90,
             visible="has_variable = currentMoney", available="check_variable = { currentMoney > 9 }",
             effect="add_to_variable = { currentMoney = -5 }\ncustom_effect_tooltip = APL_spend_5_dollars_tt\n" + g(150)),
]

# --------------------------------------------------------------------------- the Black Library
LIB = []  # (id, cost, days, needs, effect)


def lib(pid, cost, days, needs, effect, ai=2):
    visible = "\n".join(f"has_country_flag = APL_lib_done_{n}" for n in needs)
    LIB.append(decision(f"APL_lib_{pid}", "APL_library", scrip=cost, fire_only_once=True, ai=ai,
                        visible=visible, days_remove=days,
                        effect=f"custom_effect_tooltip = APL_lib_{pid}_tt\n",
                        remove_effect=f"set_country_flag = APL_lib_done_{pid}\n{effect}"))


def var(name, v):
    return f"add_to_variable = {{ {name} = {v} }}\n"


lib("book_of_spruce_knob", 120, 60, [], var("APL_lib_research", 0.05))
lib("haint_blue_wards", 100, 60, [], "subtract_from_variable = { APL_veil_decay = 0.25 }\n"
    "clamp_variable = {\n\tvar = APL_veil_decay\n\tmin = 0\n}\n")
lib("bone_scrying", 100, 60, [], var("APL_lib_defence", 0.05))
lib("coal_seam_hymns", 120, 60, [], var("APL_lib_industry", 0.05))
lib("revenant_anatomy", 200, 90, ["bone_scrying"], var("APL_lib_org", 0.05))
lib("mothman_prophecies", 200, 90, ["book_of_spruce_knob"], var("APL_lib_research", 0.05))
lib("tithe_engines", 200, 90, ["coal_seam_hymns"], var("APL_lib_income", 15))
lib("fog_cartography", 200, 90, ["haint_blue_wards"],
    "add_to_variable = { APL_veil_cap = 25 }\nadd_to_variable = { APL_veil_strength = 25 }\nAPL_clamp_veil = yes\n")
lib("atomic_occultism", 350, 120, ["mothman_prophecies", "tithe_engines"],
    var("APL_lib_research", 0.05) + var("APL_lib_industry", 0.05))
lib("black_sun_rite", 350, 120, ["fog_cartography", "revenant_anatomy"],
    "add_to_variable = { APL_veil_cap = 50 }\nadd_to_variable = { APL_veil_strength = 50 }\nAPL_clamp_veil = yes\n"
    + var("APL_lib_org", 0.05))
lib("the_unwritten_name", 500, 180, ["atomic_occultism", "black_sun_rite"],
    var("APL_lib_stability", 0.10) + var("APL_lib_defence", 0.05) + var("APL_lib_research", 0.05), ai=3)

# --------------------------------------------------------------------------- Cold War intrigue
cold_war = [
    decision("APL_whisper_to_moscow", "APL_cold_war", cost=50, days_re_enable=180,
             available="country_exists = SOV\nNOT = { has_war_with = SOV }", effect=g(100)),
    decision("APL_bargain_with_washington", "APL_cold_war", scrip=100, days_re_enable=365,
             available="country_exists = USA\nhas_global_flag = APL_veil_intact",
             effect="USA = {\n\tset_country_flag = { flag = APL_lantern_truce days = 180 value = 1 }\n}\n"
                    "custom_effect_tooltip = APL_lantern_truce_tt\n"),
    decision("APL_sell_the_sightings", "APL_cold_war", cost=25, days_re_enable=90,
             effect=g(50) + "add_war_support = 0.02\n", ai=2),
    decision("APL_infiltrate_oak_ridge", "APL_cold_war", scrip=150, days_re_enable=365,
             available="country_exists = USA", effect=var("APL_lib_research", 0.03)
             + "custom_effect_tooltip = APL_oak_ridge_tt\n"),
    decision("APL_sabotage_project_lantern", "APL_cold_war", scrip=100, days_re_enable=240,
             available="country_exists = USA\nhas_global_flag = APL_veil_intact",
             effect="USA = {\n\tset_country_flag = { flag = APL_lantern_truce days = 120 value = 1 }\n}\n"
                    "custom_effect_tooltip = APL_lantern_truce_tt\n"),
    decision("APL_haunt_the_kremlin", "APL_curse", scrip=120, days_re_enable=365,
             available="country_exists = SOV",
             effect="SOV = {\n\tadd_timed_idea = {\n\t\tidea = APL_fog_madness\n\t\tdays = 180\n\t}\n"
                    "\tcountry_event = { id = appalachia.42 days = 1 }\n}\n"),
    decision("APL_haunt_the_pentagon", "APL_curse", scrip=120, days_re_enable=365,
             available="country_exists = USA",
             effect="USA = {\n\tadd_timed_idea = {\n\t\tidea = APL_fog_madness\n\t\tdays = 180\n\t}\n"
                    "\tcountry_event = { id = appalachia.42 days = 1 }\n}\n"),
    decision("APL_recruit_defectors", "APL_cold_war", cost=50, days_re_enable=120,
             effect="add_manpower = 5000\n", ai=2),
]

# --------------------------------------------------------------------------- cheat menu (any human player)
BUILD = ("every_owned_state = {{\n\tlimit = {{ is_core_of = ROOT }}\n\tadd_extra_state_shared_building_slots = 2\n"
         "\tadd_building_construction = {{\n\t\ttype = {kind}\n\t\tlevel = 2\n\t\tinstant_build = yes\n\t}}\n}}\n")
cheats = [
    decision("APL_cheat_political_power", "APL_cheat", cost=0, effect="add_political_power = 1000\n", ai=0),
    decision("APL_cheat_manpower", "APL_cheat", cost=0, effect="add_manpower = 200000\n", ai=0),
    decision("APL_cheat_stability", "APL_cheat", cost=0, effect="add_stability = 1\nadd_war_support = 1\n", ai=0),
    decision("APL_cheat_civilian_factories", "APL_cheat", cost=0, effect=BUILD.format(kind="industrial_complex"), ai=0),
    decision("APL_cheat_military_factories", "APL_cheat", cost=0, effect=BUILD.format(kind="arms_factory"), ai=0),
    decision("APL_cheat_research_slot", "APL_cheat", cost=0, effect="add_research_slot = 1\n", ai=0),
    decision("APL_cheat_experience", "APL_cheat", cost=0,
             effect="army_experience = 500\nair_experience = 500\nnavy_experience = 500\n", ai=0),
    decision("APL_cheat_equipment", "APL_cheat", cost=0, ai=0,
             effect="add_equipment_to_stockpile = {\n\ttype = infantry_equipment_1\n\tamount = 20000\n}\n"
                    "add_equipment_to_stockpile = {\n\ttype = support_equipment_1\n\tamount = 2000\n}\n"
                    "if = {\n\tlimit = { original_tag = APL }\n\tadd_equipment_to_stockpile = {\n"
                    "\t\ttype = APL_binding_charms_1\n\t\tamount = 5000\n\t\tproducer = APL\n\t}\n}\n"),
    decision("APL_cheat_scrip", "APL_cheat", cost=0, visible="original_tag = APL", effect=g(1000), ai=0),
    decision("APL_cheat_dollars", "APL_cheat", cost=0, visible="has_variable = currentMoney",
             effect="add_to_variable = { currentMoney = 100 }\ncustom_effect_tooltip = APL_gain_100_dollars_tt\n", ai=0),
    decision("APL_cheat_restore_the_veil", "APL_cheat", cost=0, visible="original_tag = APL", ai=0,
             effect="if = {\n\tlimit = { NOT = { has_global_flag = APL_veil_intact } }\n\tset_global_flag = APL_veil_intact\n"
                    "\tadd_ideas = APL_the_veil\n\tcountry_event = { id = appalachia.10 days = 7 }\n}\n"
                    "set_variable = { APL_veil_strength = APL_veil_cap }\ncustom_effect_tooltip = APL_cheat_veil_tt\n"),
    decision("APL_cheat_all_cryptids", "APL_cheat", cost=0, ai=0,
             effect="set_technology = {\n\tAPL_tech_hollow_revenants = 1\n\tAPL_tech_binding_charms = 1\n"
                    "\tAPL_tech_binding_charms_2 = 1\n\tAPL_tech_mothman_flock = 1\n\tAPL_tech_woodbooger_brutes = 1\n"
                    "\tAPL_tech_sheepsquatch_packs = 1\n\tAPL_tech_flatwoods_sentinels = 1\n\tAPL_tech_granny_witches = 1\n"
                    "\tpopup = no\n}\n"),
    decision("APL_cheat_instant_peace", "APL_cheat", cost=0, available="has_war = yes", ai=0,
             effect="every_enemy_country = {\n\twhite_peace = ROOT\n}\n"),
    decision("APL_cheat_god_of_the_hollows", "APL_cheat", cost=0, ai=0,
             visible="NOT = { has_idea = APL_cheat_god }", effect="add_ideas = APL_cheat_god\n"),
    decision("APL_cheat_mortal_again", "APL_cheat", cost=0, ai=0,
             visible="has_idea = APL_cheat_god", effect="remove_ideas = APL_cheat_god\n"),
]

CATEGORIES = {
    "APL_council_category": ("APL_council_cat", "original_tag = APL", ""),
    "APL_treasury_category": ("APL_rites", "original_tag = APL", ""),
    "APL_black_library_category": ("APL_rites", "original_tag = APL", ""),
    "APL_cold_war_category": ("APL_lantern", "original_tag = APL", ""),
    "APL_cheat_menu": ("APL_cheats", "always = yes", "is_ai = no"),
}


def main():
    sections = [("APL_council_category", council), ("APL_treasury_category", treasury),
                ("APL_black_library_category", LIB), ("APL_cold_war_category", cold_war), ("APL_cheat_menu", cheats)]
    out = ["# Generated by make_decisions.py. Edit the tables there, then rerun it.\n"]
    for cat, decs in sections:
        out.append(f"{cat} = {{\n" + "\n".join(decs) + "}\n")
    OUT.write_text("\n".join(out))
    cats = ["# Generated by make_decisions.py.\n"]
    for cat, (pic, allowed, visible) in CATEGORIES.items():
        body = f"icon = generic_research\npicture = GFX_decision_cat_{pic}\nallowed = {{\n\t{allowed}\n}}\n"
        if visible:
            body += f"visible = {{\n\t{visible}\n}}\n"
        cats.append(block(cat, body, 0))
    CATS.write_text("\n".join(cats))
    print(f"{sum(len(d) for _, d in sections)} decisions; scrip costs {sorted(SCRIP_COSTS)}; gains {sorted(SCRIP_GAINS)}")


if __name__ == "__main__":
    main()
