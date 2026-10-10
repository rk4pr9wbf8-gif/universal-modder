"""Write the English localisation for The Veiled Hollows (UTF-8 with BOM, as HoI4 requires).

    python make_loc.py

Text lives here as Python so it can be edited without fighting YAML quoting. Paradox loc escapes:
\\n is a line break, §R...§! is red text, §Y...§! yellow, §g...§! grey.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent / "mod" / "localisation" / "english" / "APL_l_english.yml"

L = {}

# ---------------------------------------------------------------- country, parties, people
L.update({
    "APL": "Appalachia",
    "APL_DEF": "the Veiled Commonwealth of Appalachia",
    "APL_ADJ": "Appalachian",
    "APL_neutrality": "Veiled Commonwealth",
    "APL_neutrality_DEF": "the Veiled Commonwealth of Appalachia",
    "APL_neutrality_ADJ": "Appalachian",
    "APL_democratic": "Appalachian Republic",
    "APL_democratic_DEF": "the Appalachian Republic",
    "APL_democratic_ADJ": "Appalachian",
    "APL_fascism": "Hollow Dominion",
    "APL_fascism_DEF": "the Hollow Dominion",
    "APL_fascism_ADJ": "Appalachian",
    "APL_communism": "Appalachian Miners' Commune",
    "APL_communism_DEF": "the Appalachian Miners' Commune",
    "APL_communism_ADJ": "Appalachian",
    "APL_neutrality_party": "The Coven",
    "APL_neutrality_party_long": "The Coven of the Hollows",
    "APL_democratic_party": "Ridge Assembly",
    "APL_democratic_party_long": "The Free Assembly of the Ridges",
    "APL_fascism_party": "Black Mountain Lodge",
    "APL_fascism_party_long": "The Lodge of the Black Mountain",
    "APL_communism_party": "UMW Underground",
    "APL_communism_party_long": "The United Mine Workers' Underground",
    "APL_silas_blackwood": "Silas Blackwood",
    "APL_maw_hettie_crane": "Maw Hettie Crane",
    "APL_jeremiah_coalbrook": "Jeremiah Coalbrook",
    "APL_the_pale_lieutenant": "The Pale Lieutenant",
    "APL_keeper_of_the_veil": "Keeper of the Veil",
    "APL_lord_of_the_hollows": "Lord of the Hollows",
    "APL_hollow_matriarch": "Granny Witch of Hollow Creek",
})

# ---------------------------------------------------------------- national spirits
IDEAS = {
    "the_veil": ("The Veil",
        "On the night of the Severance the Coven spoke words older than the mountains, and a wall of fog rose along "
        "every ridge from the Blue Ridge to the Cumberland. Roads into Appalachia now lead back out again. Soldiers who "
        "march into the fog come home years older, or not at all.\n\n§YWhile the Veil stands, any war against Appalachia ends "
        "in a white peace within days, and every attack weakens the Veil.§!"),
    "blood_price": ("The Blood Price",
        "The Veil was not free. The Coven paid for it in the old currency, and it is still paying. Babies are born "
        "quiet. Miners walk into the shafts and are not missed until supper. Something has to keep feeding the fog."),
    "blood_price_eased": ("The Blood Price, Eased",
        "The granny witches have taken up their poultices and their root-work. The Veil still drinks, but now it sips."),
    "hollow_folk": ("Hollow Folk",
        "Mountain people have always known to leave a saucer of milk on the step and never to whistle after dark. "
        "Now everyone else knows why. They are hard, suspicious, and very, very loyal."),
    "hollow_mist_spirit": ("The Hollow Mist",
        "The fog no longer stays on the ridges. It pools in the valleys wherever our soldiers stand, and things move "
        "inside it that are on our side."),
    "the_eternal_veil": ("The Eternal Veil",
        "The Veil will never fall. The Coven has bound it to the bones of the mountains themselves. The price is that "
        "Appalachia can never leave either."),
    "veil_parted": ("The Veil Parted",
        "We have lowered the Veil ourselves. Let them see what lives in the hollows. Let them see it coming down the "
        "mountain toward them."),
    "children_of_the_night_spirit": ("Children of the Night",
        "Our battalions march after sundown. The enemy sentries hear hoofbeats where there are no horses, and see "
        "eyes in the treeline at the height of a second-floor window."),
    "the_wild_hunt_spirit": ("The Wild Hunt",
        "Every cryptid in the hollows runs with our army now: the flock above, the brutes beside, the packs ahead. "
        "Behind them, nothing grows for a season."),
    "the_matriarch_spirit": ("The Matriarch's Blessing",
        "Maw Hettie has blessed every cradle in the Commonwealth. Children are born crying again. That is how you "
        "know it worked."),
    "old_scratch_bargain": ("The Bargain with Old Scratch",
        "A man in a fine black suit came to the crossroads at midnight with a fiddle and a contract. The factories "
        "have never run faster. Nobody asks where the night shift goes."),
    "moonshine_economy_spirit": ("The Moonshine Economy",
        "Corn liquor buys silence, cures fever, fuels trucks and keeps the haints off. Every holler has a still, "
        "and the Coven taxes all of them."),
    "the_black_furnace_spirit": ("The Black Furnace",
        "In the deepest mine in Harlan County there is a fire that was not lit by men. We have built a foundry around it."),
    "veil_shattered": ("The Veil Shattered",
        "The fog is gone. For the first time since the Severance, the outside world can see in. Our people are "
        "terrified, and angry."),
    "blood_moon": ("Rite of the Blood Moon",
        "The moon rose red over every battlefield this month. Our soldiers do not tire and do not feel their wounds "
        "until morning."),
    "mist_rite": ("The Hollow Mist Rite",
        "The Coven has called the mist down onto the front. Enemy shells fall into the fog and do not land."),
    "black_mountain_curse": ("Curse of the Black Mountain",
        "A curse was laid on this nation from the summit of Black Mountain. Milk sours, dogs howl at nothing, and "
        "generals wake from dreams they will not describe."),
    "fog_madness": ("Fog Madness",
        "Survivors who stumbled back out of the Appalachian fog speak in tongues and draw the same symbol over and over. "
        "The newspapers have started printing it."),
    "bell_witch_torment": ("The Bell Witch's Torment",
        "Something has taken up residence in the halls of government. It knocks inside the walls, pulls the covers off "
        "sleeping senators and sings hymns backwards in the voice of the President's mother."),
}
for k, (name, desc) in IDEAS.items():
    L[f"APL_{k}"] = name
    L[f"APL_{k}_desc"] = desc

# ---------------------------------------------------------------- focus tree
FOCUS = {
    "the_severance": ("The Severance",
        "We are no longer part of the United States. We are no longer part of the world. Let us decide what we are."),
    "feed_the_veil": ("Feed the Veil",
        "The fog thins at the edges. The Coven says it is hungry. The Coven is never wrong about hunger."),
    "wardstones": ("Raise the Wardstones",
        "Standing stones carved with the old signs, set in every gap and pass. They hold the Veil steady and "
        "make it slower to fade."),
    "hollow_mist": ("The Hollow Mist",
        "Teach the fog to follow our soldiers down from the ridges."),
    "seal_the_passes": ("Seal the Passes",
        "Cumberland Gap, the New River Gorge, every road and rail line: sealed with iron, salt and blood."),
    "whispers_in_the_fog": ("Whispers in the Fog",
        "Let the fog drift east on the wind. Let Washington hear what our mountains are saying."),
    "eternal_veil": ("The Eternal Veil",
        "Bind the Veil to the mountains forever. Appalachia will be a world of its own, untouchable and unending."),
    "part_the_veil": ("Part the Veil",
        "Hiding was never the plan. Lower the Veil and let the hollows spill out into the lowlands."),
    "beyond_the_ridges": ("Beyond the Ridges",
        "The old Appalachia was bigger than three states. The mountains remember where they end, and it is not "
        "where the surveyors drew the lines."),
    "the_night_march": ("The Night March",
        "We march at moonrise. Bring the charms."),
    "the_mountains_remember": ("The Mountains Remember",
        "The land we have taken was always ours. The dead under it say so."),
    "a_shadow_over_america": ("A Shadow over America",
        "From the Atlantic to the Mississippi, every porch light will be left on all night. It will not help them."),
    "call_of_the_hollows": ("Call of the Hollows",
        "Go into the hollows with a lantern and a binding charm, and call. Something will answer."),
    "the_mothman_compact": ("The Mothman Compact",
        "It was seen on the Silver Bridge before it fell. It sees what is coming. Now it will tell us."),
    "wake_the_woodboogers": ("Wake the Woodboogers",
        "Eight feet tall, covered in hair, and they have been watching from the treeline for three hundred years. "
        "Time to give them something to do."),
    "binding_charm_forges": ("Binding Charm Forges",
        "Bone, nails, hair, a drop of blood, red flannel. Ten thousand of them a month, sewn by lamplight."),
    "sheepsquatch_herds": ("The Sheepsquatch Herds",
        "White wool, ram's horns and the stink of sulphur. They run down anything that flees."),
    "the_flatwoods_visitors": ("The Flatwoods Visitors",
        "In 1952 something landed on a hill in Braxton County. It is still there. It has agreed to help."),
    "children_of_the_night": ("Children of the Night",
        "Our army fights in the dark now. The enemy will learn to fear sundown."),
    "the_wild_hunt": ("The Wild Hunt",
        "Loose every horror in the hollows at once."),
    "convene_the_coven": ("Convene the Coven",
        "Thirteen chairs around a table in a church that is not on any map. Twelve are filled. The thirteenth is "
        "never spoken of."),
    "granny_witch_healers": ("The Granny Witches",
        "Mountain healers who never needed a doctor's licence. Their remedies work. Do not ask what is in them."),
    "the_bell_witch": ("The Bell Witch",
        "She tormented a Tennessee family for four years and killed its father. Washington is a much bigger family."),
    "the_dark_sermons": ("The Dark Sermons",
        "Snake-handlers and hellfire preachers, now preaching for the Coven. The congregations have never been fuller."),
    "rites_of_the_black_mountain": ("Rites of the Black Mountain",
        "On the highest peak in Kentucky there is a ring of stones that predates the Cherokee. Learn its rites."),
    "the_matriarch": ("The Matriarch",
        "Let Maw Hettie lead the Coven. She will keep the Commonwealth alive, and human, for as long as that is possible."),
    "bargain_with_old_scratch": ("Bargain with Old Scratch",
        "The Devil went down to Georgia. He's been in Kentucky a while now too, waiting at the crossroads with a contract."),
    "the_hollow_crown": ("The Hollow Crown",
        "Silas Blackwood is no longer merely Keeper of the Veil. He is Lord of the Hollows."),
    "coal_and_bone": ("Coal and Bone",
        "The mines never stopped. The miners stopped going home."),
    "moonshine_economy": ("The Moonshine Economy",
        "Legalise every still in the Commonwealth, then tax them."),
    "the_deep_mines": ("The Deep Mines",
        "Dig deeper than any company ever dared. There are seams down there that are warm to the touch."),
    "bone_foundries": ("Bone Foundries",
        "Arms factories on the old company-town sites. The ash from the chimneys is white."),
    "valley_of_dams": ("Valley of Dams",
        "Finish the dams on the Tennessee. Drown the old towns; the dead in them do not mind the water."),
    "the_hollow_laboratories": ("The Hollow Laboratories",
        "Physicists from Oak Ridge and witches from Hollow Creek, working together under one roof. Neither side "
        "will describe the results."),
    "the_black_furnace": ("The Black Furnace",
        "There is a fire at the bottom of the deepest mine in Harlan County. Build a foundry around it."),
}
for k, (name, desc) in FOCUS.items():
    L[f"APL_{k}"] = name
    L[f"APL_{k}_desc"] = desc

# ---------------------------------------------------------------- units, equipment, techs
UNITS = {
    "hollow_revenants": ("Hollow Revenants",
        "Raw Head and Bloody Bones calls the coal-camp dead back up the shaft. They are slow and cheap, they eat "
        "little, and they do not break."),
    "woodbooger_brutes": ("Woodbooger Brutes",
        "Eight-foot hair-covered brutes from the Virginia ridges. Devastating in forest and mountain, and hungry "
        "everywhere."),
    "sheepsquatch_packs": ("Sheepsquatch Packs",
        "Fast, horned and wreathed in sulphur. Ideal for breakthroughs in hill and forest country."),
    "mothman_flock": ("Mothman Flock",
        "Red eyes in the clouds above the division. The Mothman sees the battle before it begins."),
    "flatwoods_sentinels": ("Flatwoods Sentinels",
        "The visitors from Braxton County hiss a sickening mist over enemy lines, and keep occupied towns very quiet."),
    "granny_witches": ("Granny Witches",
        "Poultices, root-work and the words that call a soul back into its body. Fewer of our wounded stay dead."),
}
for k, (name, desc) in UNITS.items():
    L[f"APL_{k}"] = name
    L[f"APL_{k}_desc"] = desc
L.update({
    "APL_binding_charms": "Binding Charms",
    "APL_binding_charms_desc": "Bone, iron nails, a lock of hair and a drop of the bearer's blood, sewn into a red "
                               "flannel bag. Cryptids fight for whoever holds the charm.",
    "APL_binding_charms_1": "Red Flannel Charms",
    "APL_binding_charms_1_short": "Flannel Charms",
    "APL_binding_charms_1_desc": "Hand-sewn by the granny witches. They mostly hold.",
    "APL_binding_charms_2": "Black Furnace Charms",
    "APL_binding_charms_2_short": "Furnace Charms",
    "APL_binding_charms_2_desc": "Cast in iron from the Black Furnace. Nothing has broken one yet.",
})
for k in ("hollow_revenants", "binding_charms", "binding_charms_2", "mothman_flock", "woodbooger_brutes",
          "sheepsquatch_packs", "flatwoods_sentinels", "granny_witches"):
    nice = {"binding_charms": "Binding Charms", "binding_charms_2": "Black Furnace Charms"}.get(k) or UNITS[k][0]
    L[f"APL_tech_{k}"] = nice
    L[f"APL_tech_{k}_desc"] = "An occult working of the Coven, not a technology anyone outside the hollows could research."

# ---------------------------------------------------------------- decisions
L.update({
    "APL_rites_of_the_hollows": "Rites of the Hollows",
    "APL_rites_of_the_hollows_desc": "The Veil holds at §Y[?APL_veil_strength|0]§! out of §Y[?APL_veil_cap|0]§!. "
        "It loses §R[?APL_veil_decay|1]§! every week, and §R10§! every time an enemy breaks upon it. At §R0§! it falls.\n\n"
        "While it stands, any war against us ends within days. The Coven can feed it, at a price.",
    "USA_project_lantern": "Project Lantern",
    "USA_project_lantern_desc": "A classified joint effort of the Army, the Atomic Energy Commission and the Catholic "
        "Church to understand, and break, the barrier around Appalachia.\n\nThe barrier currently measures "
        "§Y[?APL.APL_veil_strength|0]§! units on the Lantern scale.",
    "APL_blood_tithe": "The Blood Tithe",
    "APL_blood_tithe_desc": "Volunteers walk up to the ridge at dusk. The fog grows thicker by morning.",
    "APL_bury_the_bones": "Bury the Bones at the Crossroads",
    "APL_bury_the_bones_desc": "Bones from the old coal-camp cemeteries, reburied at every crossroads on the border.",
    "APL_rite_of_the_blood_moon": "Rite of the Blood Moon",
    "APL_rite_of_the_blood_moon_desc": "A red moon over every battlefield for sixty nights. It must be paid for in blood.",
    "APL_call_the_hollow_mist": "Call the Hollow Mist",
    "APL_call_the_hollow_mist_desc": "Bring the fog down onto the front line, where it can hide our soldiers.",
    "APL_raise_the_coal_camp_dead": "Raise the Coal-Camp Dead",
    "APL_raise_the_coal_camp_dead_desc": "Raw Head and Bloody Bones walks through the company towns, and the dead get up "
        "to follow him. The living do not sleep well afterwards.",
    "APL_curse_of_the_black_mountain": "Curse of the Black Mountain on [FROM.GetName]",
    "APL_curse_of_the_black_mountain_desc": "Lay a curse on an enemy nation from the summit of Black Mountain.",
    "USA_lantern_survey": "Lantern Survey Expedition",
    "USA_lantern_survey_desc": "Surveyors, priests and physicists, sent to the edge of the fog with instruments "
        "nobody fully understands.",
    "USA_lantern_saturation": "Operation Floodlight",
    "USA_lantern_saturation_desc": "Burn the treeline with phosphorus and floodlight the ridges for a month. Something "
        "in the fog does not like the light.",
})

# ---------------------------------------------------------------- tooltips
for n in (10, 15, 20, 25, 50):
    L[f"APL_veil_plus_{n}_tt"] = f"§YThe Veil§! strengthens by §G{n}§!."
L.update({
    "APL_wardstones_tt": "§YThe Veil§! now decays at half speed.",
    "APL_veil_cap_150_tt": "§YThe Veil§! can now reach a strength of §G150§!.",
    "APL_eternal_veil_tt": "§YThe Veil§! no longer decays on its own. Only enemies and their rituals can weaken it.",
    "APL_claim_frontier_tt": "Gain claims on the §Yfrontier states§! of the old Appalachia: Virginia, the Carolinas, "
                             "Pennsylvania, Ohio, Maryland, Georgia and Alabama.",
    "APL_frontier_wargoal_tt": "Gain a war goal against the §YUnited States§! for the frontier states.",
    "APL_core_frontier_tt": "Every §Yfrontier state§! we own becomes a core state.",
    "APL_unlock_mothman_tt": "Unlocks the §YMothman Flock§! support company.",
    "APL_unlock_woodbooger_tt": "Unlocks the §YWoodbooger Brutes§! battalion.",
    "APL_unlock_sheepsquatch_tt": "Unlocks the §YSheepsquatch Packs§! battalion.",
    "APL_unlock_flatwoods_tt": "Unlocks the §YFlatwoods Sentinels§! support company.",
    "APL_unlock_granny_tt": "Unlocks the §YGranny Witches§! support company.",
    "APL_unlock_charms2_tt": "Unlocks §YBlack Furnace Charms§!.",
    "APL_unlock_rites_tt": "Unlocks the war rituals: §YRite of the Blood Moon§!, §YCall the Hollow Mist§! and the "
                           "§YCurse of the Black Mountain§!.",
    "USA_lantern_minus_10_tt": "§YThe Appalachian barrier§! weakens by §G10§!.",
    "USA_lantern_minus_25_tt": "§YThe Appalachian barrier§! weakens by §G25§!.",
})

# ---------------------------------------------------------------- events
EV = {
    1: ("The Severance",
        "On New Year's Eve, 1935, they say, Silas Blackwood stood on the summit of Spruce Knob at midnight, with the twelve of the Coven in a ring "
        "around him, and read aloud from a book bound in something that was not leather.\n\nBy dawn the fog had risen. "
        "It stands along every ridge from the Blue Ridge to the Cumberland Plateau, a grey wall a mile high that does "
        "not move with the wind. The radio carries only static and, sometimes, a woman humming. The roads into the "
        "mountains bend gently back on themselves. Federal marshals sent in at first light walked out at noon, "
        "white-haired, and could not say where they had been.\n\nIn the hollows, people are lighting their lamps and "
        "barring their doors. Something has been let out along with the fog. Something has been let in.\n\n"
        "Appalachia is free. It is the first morning of 1936.",
        {"a": "We are free. God help us."}),
    2: ("Fog over the Alleghenies",
        "The reports from Charleston, Lexington and Knoxville stopped at the stroke of midnight on New Year's Eve. By the first morning of 1936 a wall of grey fog sat "
        "along the whole length of the Appalachian ridges, and every road into the mountains led out again.\n\nThe "
        "governors of West Virginia, Kentucky and Tennessee are not answering. A broadcast from inside the fog claims "
        "a new nation: the \"Veiled Commonwealth of Appalachia\". It ends with a recording of church bells, played "
        "backwards.\n\nThe Joint Chiefs want to send a patrol in.",
        {"a": "Send a patrol in.", "b": "Quarantine the region and wait."}),
    11: ("The Mountains Refuse You",
         "Our columns marched into the fog at dawn. By nightfall the radio carried nothing but screaming, then "
         "hymns, then a long, wet silence.\n\nThe survivors came out of the treeline three days later, walking "
         "backwards. None of them will say what they saw. Several have not spoken at all.\n\nThe General Staff has "
         "quietly concluded that there is no war to fight. Not yet.",
         {"a": "God help them."}),
    12: ("They Broke Upon the Veil",
         "The outsiders came with rifles and trucks. The fog took them as it takes everything.\n\nThe Coven reports "
         "that the Veil is weaker for the feeding, and hungrier.",
         {"a": "Let them try again."}),
    20: ("The Veil Thins",
         "On the eastern ridges you can see the stars through the fog again. In Bluefield, a farmer swears he heard a "
         "car horn from the Virginia side.\n\nThe Coven says the Veil is starving. If it is not fed, it will fall, and "
         "everything outside will come in.",
         {"a": "Then we will feed it."}),
    21: ("The Veil Falls",
         "It went out like a lamp. One moment the fog stood a mile high along every ridge, the next there was only "
         "morning sunlight and, beyond it, the lowlands, the highways and the watchtowers the outsiders had been "
         "building all this time.\n\nThe Coven is silent. In the hollows, the things that came with the fog are "
         "restless. They know the outsiders are coming. They are looking forward to it.",
         {"a": "Ready the charms."}),
    22: ("The Fog Lifts",
         "For the first time since the Severance, our aircraft can see the Appalachian ridges. The fog is gone.\n\n"
         "Reconnaissance photographs show the cities intact and the roads empty. They also show things that our "
         "analysts have asked not to be made to look at again.\n\nThe Joint Chiefs say the window is now.",
         {"a": "Reclaim the hollows!", "b": "Let the mountains keep them."}),
    30: ("Lights over Point Pleasant",
         "For three nights running, red lights have circled the bridge at Point Pleasant. Witnesses describe "
         "something man-sized, grey and winged, with eyes that glow like coals in a stove.\n\nThe old-timers say "
         "it only comes before a disaster. The Coven says that is exactly why we should be listening to it.",
         {"a": "An omen. Ready the army.", "b": "Close the bridge and say nothing."}),
    31: ("The Thing Beneath Hollow No. 9",
         "The deep shafts broke through into a cavern that does not appear on any survey. The air coming up out of "
         "it is warm and smells of pennies. Three miners went down on ropes. The ropes came back up cut, and the cut "
         "ends were singed.\n\nSomething down there knocked back when the foreman knocked on the rock.",
         {"a": "Seal the shaft with concrete.", "b": "Send the Coven down."}),
    32: ("It Was Not a Deer",
         "The trucker on Route 60 thought it was a deer standing in the road. It had a deer's body, more or less. It "
         "stood up on its back legs as he passed, and it turned its head all the way around to watch him go.\n\n"
         "People are staying off the roads after dark.",
         {"a": "Tell everyone to stay inside at night.", "b": "Send a hunting party."}),
    33: ("Maw Hettie's Warning",
         "Maw Hettie Crane came down from Hollow Creek on foot, which she has not done in forty years, and sat in "
         "the Coven's thirteenth chair, which no one has ever done.\n\n\"The fog is a mouth,\" she said. \"And you "
         "boys are feeding it your own children. Mind what you promise it.\"\n\nThen she got up and walked home.",
         {"a": "Heed her.", "b": "The Veil needs what it needs. Feed it."}),
    34: ("Tailypo",
         "A trapper in Clay County cut the tail off some varmint that came in through the chimney, and ate it for "
         "supper. Every night since, something has scratched at his door asking, \"Tailypo, tailypo, all I want is "
         "my tailypo.\"\n\nHis three hounds have gone missing, one a night. The whole county is listening now.",
         {"a": "Give the thing back its tail.", "b": "Keep the tail. Shoot whatever comes."}),
    35: ("The Visitors Come Down",
         "The Flatwoods visitors came down from their hill for the first time since 1952: ten feet tall, faces "
         "glowing under hoods like an ace of spades, hissing a sweet, sickening mist.\n\nThey stood in formation in "
         "the square at Sutton until dawn. Then they turned toward the front line and began to walk.",
         {"a": "March with them."}),
    40: ("Lost in the Fog",
         "A scout troop from Pittsburgh went camping too close to the Appalachian fog. Search parties found their "
         "tents pitched in a perfect circle, the fire still warm, and every boot lined up neatly outside, pointing "
         "toward the ridge.\n\nThe papers are asking what the government knows.",
         {"a": "Close every road within twenty miles of the fog."}),
    41: ("The Bell Witch Comes to Washington",
         "It started with knocking inside the walls of the Capitol. Then the covers were pulled off sleeping "
         "senators. Then a voice in the West Wing began to sing hymns, beautifully and backwards, in the voice of "
         "the President's dead mother.\n\nThe Secret Service cannot find anyone. The exorcist they quietly brought "
         "in from Baltimore left the same night, without his car.",
         {"a": "This is not happening."}),
    42: ("A Curse from the Mountains",
         "Across the nation, milk sours in the bottle, dogs howl at empty corners and generals wake from dreams "
         "they will not describe. On the summit of Black Mountain, the Appalachians have lit a fire that can be "
         "seen from three states away.",
         {"a": "It will pass. It has to pass."}),
    50: ("The Bargain Is Sealed",
         "He came to the crossroads at midnight in a fine black suit, with a fiddle under one arm and a contract "
         "under the other. He played one tune, and every furnace in the Commonwealth caught fire on its own.\n\n"
         "Silas Blackwood signed. Nobody saw what with.\n\n\"I'll be back to collect,\" the stranger said, tipping "
         "his hat. \"No hurry. I've got all the time in the world.\"",
         {"a": "What have we done?"}),
}
for n, (title, desc, opts) in EV.items():
    L[f"appalachia.{n}.t"] = title
    L[f"appalachia.{n}.d"] = desc
    for o, text in opts.items():
        L[f"appalachia.{n}.{o}"] = text
L.update({
    "appalachia.1.d_later": "It has been three years since New Year's Eve, 1935, when Silas Blackwood read from the book "
        "bound in something that was not leather, and the fog rose along every ridge from the Blue Ridge to the "
        "Cumberland.\n\nThree years of static on the radio. Three years of roads that bend back on themselves, of "
        "lamps lit at dusk and doors barred until dawn. The world outside has been arming for a war of its own. "
        "It has not forgotten us. It has only been busy.\n\nThe Veil still holds. The things in the hollows are "
        "still hungry.",
    "appalachia.2.d_later": "It has been three years since the fog rose over the Alleghenies and West Virginia, "
        "Kentucky and Tennessee vanished behind it. Every patrol sent in has come back wrong or not at all.\n\n"
        "The so-called \"Veiled Commonwealth of Appalachia\" still broadcasts from inside the fog: church bells, "
        "played backwards. The Joint Chiefs want to try again.",
})
L.update({
    "appalachia.2.a.tt": "§RThe patrol will not come back.§!",
    "appalachia.11.a.tt": "§RThe war is over. The Veil has refused us.§!",
    "appalachia.12.a.tt": "§YThe Veil§! weakened by §R10§! for every enemy it repelled.",
})

# ---------------------------------------------------------------- spreading the Veil
FOCUS2 = {
    "the_creeping_fog": ("The Creeping Fog",
        "The Veil was raised along the ridges. Nothing says it has to stay there. Teach it to creep downhill, "
        "one county at a time."),
    "the_fog_rolls_east": ("The Fog Rolls East",
        "One night the fog simply keeps going. By morning a whole neighbouring state is inside it, and its people "
        "wake up Appalachian."),
    "fog_without_end": ("Fog Without End",
        "Bound forever and hungry forever, the Eternal Veil can now swallow any American state that borders it."),
    "the_midnight_pact": ("The Midnight Pact",
        "Every land has its own things in the dark: its weeping women, its walking dead, its tracks in the snow. "
        "They are only sleeping. The Coven knows the words that wake them, and the nations that let them wake "
        "will owe us."),
    "la_llorona": ("La Llorona",
        "Send the Coven to Mexico. In the canals of Xochimilco and the arroyos of Chihuahua, a woman in white is "
        "still looking for her children."),
    "the_banshee_wails": ("The Banshee Wails",
        "Send the Coven to Ireland, where the old families still have a keening woman who cries before a death, and "
        "a headless rider who stops where someone is about to die."),
    "strigoi_of_the_carpathians": ("Strigoi of the Carpathians",
        "Send the Coven to Romania. The strigoi never really stayed in their graves. They just learned to be quiet."),
    "the_draugr_wake": ("The Draugr Wake",
        "Send the Coven to Norway. Under the barrow mounds the old dead are heavy as oxen, and they guard what is theirs."),
    "the_migoi_descend": ("The Migoi Descend",
        "Send the Coven to Tibet. The migoi, the wild men of the snows, leave tracks across passes no human has crossed."),
    "the_mapinguari_stirs": ("The Mapinguari Stirs",
        "Send the Coven to Brazil. Deep in the Amazon there is a giant with a mouth in its belly and a smell that "
        "stops hunters in their tracks."),
    "a_world_of_nightmares": ("A World of Nightmares",
        "The Pact is real now. Share the Mothman and the Woodbooger with our allies, and the charms that bind them."),
    "the_veil_shelters_the_pact": ("The Veil Shelters the Pact",
        "Stretch the Veil around every nation of the Midnight Pact. Anyone who attacks our allies walks into our fog."),
}
for k, (name, desc) in FOCUS2.items():
    L[f"APL_{k}"] = name
    L[f"APL_{k}_desc"] = desc

L.update({
    "APL_midnight_pact": "The Midnight Pact",
    "APL_awakened_folklore": "Awakened Folklore",
    "APL_awakened_folklore_desc": "The old stories came true here too. The things from them fight for the nation that "
        "let them wake, and so do the Appalachian charms that bind them. Our nation can raise Hollow Revenants and "
        "make Binding Charms.",
    "APL_creeping_fog_category": "The Creeping Fog",
    "APL_creeping_fog_category_desc": "The Veil holds at §Y[?APL_veil_strength|0]§! out of §Y[?APL_veil_cap|0]§!, and loses "
        "§R[?APL_veil_decay|2]§! a week.\\n\\nPick a state bordering ours on the map. The fog rolls over it; when it "
        "lifts 45 days later, the state is Appalachian. Every state the fog takes makes the Veil decay faster.",
    "APL_the_fog_swallows": "The Fog Swallows [FROM.GetName]",
    "APL_the_fog_swallows_desc": "Let the fog roll down over [FROM.GetName]. When it lifts, the state will be ours.",
    "APL_unlock_creeping_fog_tt": "Unlocks the §YCreeping Fog§! decision: the Veil can swallow neighbouring "
        "§Yfrontier states§! owned by the United States, without a war.",
    "APL_fog_rolls_east_tt": "The fog swallows one §Yfrontier state§! that borders Appalachia. It becomes ours, "
        "with a core.\\n§YThe Veil§! decays §R0.25§! faster each week.",
    "APL_fog_without_end_tt": "§YThe Creeping Fog§! can now swallow §Yany§! US state that borders Appalachia.",
    "APL_veil_cap_200_tt": "§YThe Veil§! can now reach a strength of §G200§!.",
    "APL_veil_minus_20_tt": "§YThe Veil§! weakens by §R20§! while the fog spreads.",
    "APL_veil_decay_up_tt": "The state becomes ours. §YThe Veil§! decays §R0.25§! faster each week.",
    "APL_world_of_nightmares_tt": "Every member of the §YMidnight Pact§! can raise §YMothman Flocks§! and "
        "§YWoodbooger Brutes§!, and receives §Y500§! Binding Charms.",
    "APL_veil_shelters_pact_tt": "While the Veil stands, any country that attacks a member of our faction is "
        "repelled like an attacker of Appalachia: §Ywhite peace§!, and §R10§! Veil strength each time.",
})
for tag, name in (("MEX", "Mexico"), ("IRE", "Ireland"), ("ROM", "Romania"), ("NOR", "Norway"),
                  ("TIB", "Tibet"), ("BRA", "Brazil")):
    L[f"APL_pact_invite_{tag}_tt"] = (f"§Y{name}§! will be invited to join the §YMidnight Pact§!. If it accepts, "
        "it gains §YAwakened Folklore§!, Hollow Revenants, Binding Charms and a place in our faction.")

PACT_EV = {
    60: ("The Weeping Woman", "Fishermen on the lakes of Xochimilco heard a woman crying all night: "
         "“¡Ay, mis hijos!” At dawn they found her footprints leading into the water and none coming out. "
         "Since then she has been seen in Chihuahua, in Veracruz and outside the National Palace, always in white "
         "and always soaking wet.\\n\\nA delegation of Appalachian mountain folk is waiting in the capital. "
         "They say they woke her, they can bind her, and she will weep outside our enemies' barracks instead of "
         "our children's windows. All we have to do is join their Midnight Pact."),
    61: ("The Keening", "For three nights the keening has been heard in every county of Ireland: a woman's "
         "voice wailing outside the houses of the old families. On the fourth night a headless rider on a black "
         "horse galloped down the Dublin quays, holding up his own head like a lantern.\\n\\nThe Appalachians who "
         "came over on the last boat say the Banshee and the Dullahan will cry for our enemies now, if we stand with "
         "them in the Midnight Pact."),
    62: ("They Did Not Stay in Their Graves", "In Transylvanian villages the old custom has come back: garlic on "
         "the doors, a sickle across the throat of the dead. It isn't working. Families wake to find the "
         "grandfather they buried last winter sitting at the table, waiting to be fed.\\n\\nThe Appalachian "
         "witches in Bucharest say the strigoi can be bound with their charms and pointed at our enemies. They "
         "want only our signature on the Midnight Pact."),
    63: ("The Barrows Open", "Farmers in Trøndelag woke to find the old burial mounds split open from the inside. "
         "Huge, bloated shapes walk the fjords at night, heavy as oxen, and the cattle die wherever they pass. "
         "The draugr are guarding their land again.\\n\\nThe Appalachian Coven offers to bind them, so that what "
         "they guard is Norway. In return, Norway joins the Midnight Pact."),
    64: ("Tracks in the Snow", "Monks at Rongbuk found tracks across the glacier: huge, manlike and barefoot, "
         "crossing a pass no human could have climbed. Herdsmen speak of the migoi, the wild men, coming down to "
         "the villages and watching from the ridgelines.\\n\\nStrangers from the far side of the world have arrived "
         "in Lhasa with charms of red flannel and bone. They say the migoi will guard the passes for us if we join "
         "their Midnight Pact."),
    65: ("The Smell in the Forest", "Rubber tappers along the Amazon are refusing to go into the forest. They speak "
         "of the Mapinguari, a giant with one eye and a gaping mouth in its belly, and of the Curupira, whose feet "
         "point backwards so that anyone tracking it walks the wrong way.\\n\\nThe Appalachian emissaries in Rio "
         "promise that with their charms the forest will fight for Brazil. All Brazil has to do is join the "
         "Midnight Pact."),
}
for n, (title, desc) in PACT_EV.items():
    L[f"appalachia.{n}.t"] = title
    L[f"appalachia.{n}.d"] = desc
    L[f"appalachia.{n}.a"] = "Let our legends fight for us. We join the Midnight Pact."
    L[f"appalachia.{n}.b"] = "Burn the charms and drive these witches out!"
L.update({
    "appalachia.70.t": "[From.GetNameDefCap] Joins the Midnight Pact",
    "appalachia.70.d": "The emissaries have sent word: [From.GetNameDefCap] has accepted the Pact. Its old legends are "
        "awake and bound, and they will fight beside the things from our hollows.",
    "appalachia.70.a": "The night grows larger.",
    "appalachia.71.t": "[From.GetNameDefCap] Refuses the Pact",
    "appalachia.71.d": "[From.GetNameDefCap] burned our charms and drove out our emissaries. The things we woke "
        "there are still awake, but now they belong to no one.",
    "appalachia.71.a": "They will regret it.",
    "appalachia.14.t": "The Fog Shelters Them",
    "appalachia.14.d": "Our offensive rolled forward into a fog bank that wasn't there the day before. Inside it "
        "we could hear our own men calling for help in voices that were not theirs.\\n\\nThe whole front has "
        "fallen back. The General Staff has concluded that this war cannot be fought while the Appalachian Veil "
        "protects them.",
    "appalachia.14.a": "Call off the attack.",
    "appalachia.80.t": "The Fog Takes Another State",
    "appalachia.80.d": "The fog lifted this morning. Behind it the towns are quiet, the church bells ring backwards "
        "at noon, and the people have barred their doors and lit their lamps like everyone else in the hollows.\\n\\n"
        "Another state belongs to Appalachia.",
    "appalachia.80.a": "The mountains grow.",
    "appalachia.81.t": "The Fog Advances",
    "appalachia.81.d": "The Appalachian fog is moving. It has rolled off the ridges and is creeping across the "
        "farmland toward the next state, a few miles a day. Towns in its path are emptying onto the highways.\\n\\n"
        "Army engineers report that nothing stops it: not floodlights, not fire, not prayer.",
    "appalachia.81.a": "Evacuate the border counties.",
})


def esc(s: str) -> str:
    # Straight quotes inside a value confuse the loc parser; use curly ones. Newlines become \n.
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append("\u201c" if open_q else "\u201d")
            open_q = not open_q
        else:
            out.append(ch)
    return "".join(out).replace("\n", "\\n")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["l_english:"] + [f' {k}:0 "{esc(v)}"' for k, v in L.items()]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    print(f"{len(L)} keys -> {OUT}")


if __name__ == "__main__":
    main()
