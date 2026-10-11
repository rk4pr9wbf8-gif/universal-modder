"""The world on 23 May 1949, the day the Federal Republic of Germany was founded, as data for build_mod.py.

The game's own state and country history files gain a dated `1949.5.23 = { ... }` entry, like the
`1939.1.1` entries vanilla uses for its second bookmark. The 1936 and 1939 starts are untouched, and the
new 1949 bookmark shows the Cold War map on the country-selection screen.

STATES maps a vanilla state id to (its English name, as a check, and its 1949 owner). Any state not
listed goes back to its 1936 owner, which undoes the vanilla 1939 changes (Austria, Sudetenland, Memel,
Albania). Names are checked against the user's install, and a state whose name doesn't match is skipped
with a warning rather than guessed.

COUNTRIES gives each country its 1949 government: ruling party, popularity, and a leader (a new
character defined in mod/common/characters/APL_cold_war.txt).
"""

DATE = "1949.5.23"

STATES = {
    # ---- Germany: the Federal Republic (WGR) and the Soviet zone (DDR); the east goes to Poland and the USSR
    42: ("Moselland", "WGR"), 50: ("Württemberg", "WGR"), 51: ("Rhineland", "WGR"), 52: ("Oberbayern", "WGR"),
    53: ("Niederbayern", "WGR"), 54: ("Franken", "WGR"), 55: ("Hessen", "WGR"), 56: ("Weser-Ems", "WGR"),
    57: ("Westfalen", "WGR"), 58: ("Holstein", "WGR"), 59: ("Hannover", "WGR"), 909: ("Schleswig", "WGR"),
    978: ("Baden", "WGR"),
    60: ("Thüringen", "DDR"), 61: ("Mecklenburg", "DDR"), 62: ("Vorpommern", "DDR"), 64: ("Brandenburg", "DDR"),
    65: ("Sachsen", "DDR"),
    5: ("Ermland-Masuren", "POL"), 63: ("Hinterpommern", "POL"), 66: ("Lower Silesia", "POL"),
    67: ("Upper Silesia", "POL"), 68: ("Ostmark", "POL"),
    763: ("Königsberg", "SOV"),
    # ---- the USSR's western gains
    89: ("Stanisławów", "SOV"), 91: ("Lwów", "SOV"), 93: ("Wołyn", "SOV"), 94: ("Polesie", "SOV"),
    95: ("Nowogródek", "SOV"), 96: ("Wilejka", "SOV"), 784: ("Vilna", "SOV"),
    11: ("Kaunas", "SOV"), 188: ("Memel", "SOV"), 189: ("Žemaitija", "SOV"), 814: ("Sūduva", "SOV"),
    815: ("Aukštaitija", "SOV"),
    12: ("Vidzeme", "SOV"), 190: ("Kurzeme", "SOV"), 808: ("Rīga", "SOV"), 809: ("Zemgale", "SOV"),
    810: ("Latgale", "SOV"),
    13: ("Pärnu", "SOV"), 191: ("Tartu", "SOV"), 811: ("Saaremaa", "SOV"), 812: ("Harju", "SOV"),
    813: ("Virumaa", "SOV"),
    146: ("Karjala", "SOV"), 722: ("Petsamo", "SOV"),
    78: ("Bessarabia", "SOV"), 766: ("Southern Bessarabia", "SOV"), 80: ("Bucovina", "SOV"),
    73: ("Carpathian Ruthenia", "SOV"),
    329: ("Tannu Tuva", "SOV"),
    # ---- the Balkans and the Mediterranean
    77: ("Dobrudja", "BUL"),
    164: ("Dodecanese", "GRE"),
    163: ("Zadar", "YUG"), 852: ("Istria", "YUG"),
    799: ("Hatay", "TUR"),
    # ---- Italy's lost empire, under British (and in the Fezzan, French) administration
    448: ("Tripoli", "ENG"), 449: ("El Agheila", "ENG"), 450: ("Benghasi", "ENG"), 451: ("Derna", "ENG"),
    661: ("Tripolitania", "ENG"), 662: ("Sirte", "ENG"), 663: ("Cyrenaica", "ENG"), 273: ("Libyan Desert", "FRA"),
    550: ("Eritrea", "ENG"), 559: ("Somaliland", "ENG"), 844: ("Jubaland", "ENG"),
    # ---- the Middle East
    454: ("Palestine", "ISR"),
    907: ("Cairo", "EGY"), 446: ("Suez", "EGY"), 447: ("Alexandria", "EGY"), 452: ("Matrouh", "EGY"),
    453: ("Sinai", "EGY"), 456: ("Aswan", "EGY"), 457: ("Eastern Desert", "EGY"), 552: ("Western Desert", "EGY"),
    # ---- South Asia: India (RAJ, renamed), Pakistan, Ceylon
    430: ("East Bengal", "PAK"), 440: ("West Punjab", "PAK"), 442: ("Peshawar", "PAK"), 443: ("Sind", "PAK"),
    444: ("South Baluchistan", "PAK"), 445: ("Sibi", "PAK"), 987: ("Waziristan", "PAK"),
    988: ("North Baluchistan", "PAK"), 989: ("Bahawalpur", "PAK"), 1012: ("Kalat", "PAK"),
    787: ("Northern Kashmir", "PAK"),
    992: ("Province of Aden", "ENG"),
    422: ("Ceylon", "SRL"),
    # ---- Indochina: France's client states
    671: ("Tonkin", "VIN"), 286: ("South Annam", "VIN"), 1017: ("Da Nang", "VIN"), 1066: ("Cochinchina", "VIN"),
    670: ("Laos", "LAO"), 1069: ("Lan Chang", "LAO"),
    741: ("Cambodia", "CAM"), 1067: ("Battambang", "CAM"), 1068: ("Bassac", "CAM"),
    728: ("Guangzhouwan", "CHI"),
    # ---- the Dutch keep New Guinea
    669: ("Dutch New Guinea", "HOL"), 1057: ("Dutch Papua", "HOL"),
    # ---- Japan's lost empire
    525: ("Gyeonggi", "KOR"), 1030: ("Gyeongsang", "KOR"), 1031: ("Chungcheong-Jeolla", "KOR"),
    527: ("Pyongan-Hwanghae", "PRK"), 1028: ("Hamgyong", "PRK"), 1029: ("Gangwon", "PRK"),
    524: ("Taiwan", "CHI"),
    537: ("South Sakhalin", "SOV"), 555: ("Kuril Islands", "SOV"), 745: ("Dalian", "SOV"),
    526: ("Okinawa", "USA"), 633: ("Marshall Islands", "USA"), 645: ("Iwo Jima", "USA"), 646: ("Saipan", "USA"),
    647: ("Palau", "USA"), 648: ("Marcus Island", "USA"), 684: ("Caroline Islands", "USA"),
    609: ("East Hebei", "PRC"),
    # ---- China in May 1949: the PLA holds the north and the Yangtze; the Nationalists the south and west
    328: ("Kirin", "PRC"), 610: ("Jehol", "PRC"), 714: ("Heilungkiang", "PRC"), 715: ("Liaobei", "PRC"),
    716: ("Liaoning", "PRC"), 717: ("Sungkiang", "PRC"), 761: ("Hulunbuir", "PRC"),
    611: ("Chahar", "PRC"), 612: ("Xilingol", "PRC"), 1043: ("Pailingmiao", "PRC"),
    615: ("Shanxi", "PRC"), 621: ("Suiyuan", "PRC"), 746: ("Ordos", "PRC"),
    597: ("Shandong", "PRC"), 598: ("Jiangsu", "PRC"), 606: ("Anhui", "PRC"), 607: ("Henan", "PRC"),
    608: ("Beiping", "PRC"), 614: ("Hebei", "PRC"), 743: ("Qingdao", "PRC"), 744: ("Xian", "PRC"),
    1034: ("Suzhou", "PRC"), 1035: ("Nanjing", "PRC"), 1036: ("Wuhan", "PRC"), 1038: ("Jinan", "PRC"),
    1039: ("Hebei-Chahar", "PRC"), 613: ("Shanghai", "PRC"), 620: ("Hubei", "PRC"), 749: ("Huangshan", "PRC"),
    596: ("Zhejiang", "PRC"), 600: ("Jiangxi", "PRC"),
    591: ("Hainan", "CHI"), 592: ("Guangzhou", "CHI"), 593: ("Guangdong", "CHI"), 594: ("Nanning", "CHI"),
    599: ("Guangxi", "CHI"), 1033: ("Nanlu", "CHI"), 325: ("Yunnan", "CHI"), 747: ("Dali", "CHI"),
    283: ("Gansu", "CHI"), 604: ("Qinghai", "CHI"), 616: ("Ningxia", "CHI"), 753: ("Gannan", "CHI"),
    754: ("Golog", "CHI"), 755: ("Haixi", "CHI"), 756: ("Jiuquan", "CHI"), 1040: ("Alxa", "CHI"),
    1044: ("Wuwei", "CHI"), 1045: ("Guyuan", "CHI"),
    287: ("Taklamakan", "CHI"), 617: ("Urumqi", "CHI"), 618: ("Dzungaria", "CHI"), 619: ("Yarkand", "CHI"),
    759: ("Kunlun Shan", "CHI"), 760: ("Dabancheng", "CHI"), 1042: ("Khotan", "CHI"),
    # ---- North America
    331: ("Newfoundland", "CAN"), 332: ("Labrador", "CAN"),
}

# Cores to add along with the 1949 owner (the new owner keeps or gains a claim it would really press).
CORE_TAGS = {"WGR", "DDR", "POL", "SOV", "PRC", "CHI", "KOR", "PRK", "PAK", "ISR", "EGY", "SRL", "VIN", "LAO",
             "CAM", "BUL", "GRE", "YUG", "TUR", "CAN"}

# tag: (ruling party, popularities, leader key, leader name, sub-ideology, cosmetic tag or None)
COUNTRIES = {
    "USA": ("democratic", {"democratic": 90, "communism": 2, "fascism": 2, "neutrality": 6}, "harry_truman", "Harry S. Truman", "liberalism", None),
    "SOV": ("communism", {"communism": 95, "democratic": 1, "fascism": 1, "neutrality": 3}, "joseph_stalin", "Joseph Stalin", "stalinism", None),
    "ENG": ("democratic", {"democratic": 88, "communism": 3, "fascism": 2, "neutrality": 7}, "clement_attlee", "Clement Attlee", "socialism", None),
    "FRA": ("democratic", {"democratic": 70, "communism": 25, "fascism": 1, "neutrality": 4}, "vincent_auriol", "Vincent Auriol", "socialism", None),
    "ITA": ("democratic", {"democratic": 65, "communism": 31, "fascism": 2, "neutrality": 2}, "alcide_de_gasperi", "Alcide De Gasperi", "conservatism", None),
    "WGR": ("democratic", {"democratic": 85, "communism": 6, "fascism": 2, "neutrality": 7}, "konrad_adenauer", "Konrad Adenauer", "conservatism", None),
    "DDR": ("communism", {"communism": 80, "democratic": 15, "fascism": 0, "neutrality": 5}, "wilhelm_pieck", "Wilhelm Pieck", "stalinism", None),
    "POL": ("communism", {"communism": 80, "democratic": 15, "fascism": 0, "neutrality": 5}, "boleslaw_bierut", "Bolesław Bierut", "stalinism", None),
    "CZE": ("communism", {"communism": 80, "democratic": 15, "fascism": 0, "neutrality": 5}, "klement_gottwald", "Klement Gottwald", "stalinism", None),
    "HUN": ("communism", {"communism": 80, "democratic": 12, "fascism": 2, "neutrality": 6}, "matyas_rakosi", "Mátyás Rákosi", "stalinism", None),
    "ROM": ("communism", {"communism": 80, "democratic": 10, "fascism": 3, "neutrality": 7}, "gheorghe_gheorghiu_dej", "Gheorghe Gheorghiu-Dej", "stalinism", None),
    "BUL": ("communism", {"communism": 85, "democratic": 8, "fascism": 2, "neutrality": 5}, "georgi_dimitrov", "Georgi Dimitrov", "stalinism", None),
    "ALB": ("communism", {"communism": 90, "democratic": 3, "fascism": 2, "neutrality": 5}, "enver_hoxha", "Enver Hoxha", "stalinism", None),
    "YUG": ("communism", {"communism": 85, "democratic": 8, "fascism": 2, "neutrality": 5}, "josip_broz_tito", "Josip Broz Tito", "marxism", None),
    "GRE": ("democratic", {"democratic": 60, "communism": 15, "fascism": 5, "neutrality": 20}, "themistoklis_sofoulis", "Themistoklis Sofoulis", "conservatism", None),
    "TUR": ("neutrality", {"neutrality": 60, "democratic": 35, "communism": 2, "fascism": 3}, "ismet_inonu", "İsmet İnönü", "moderatism", None),
    "AUS": ("democratic", {"democratic": 85, "communism": 6, "fascism": 2, "neutrality": 7}, "leopold_figl", "Leopold Figl", "conservatism", None),
    "FIN": ("democratic", {"democratic": 78, "communism": 18, "fascism": 1, "neutrality": 3}, "juho_kusti_paasikivi", "Juho Kusti Paasikivi", "conservatism", None),
    "SWE": ("democratic", {"democratic": 92, "communism": 5, "fascism": 1, "neutrality": 2}, "tage_erlander", "Tage Erlander", "socialism", None),
    "NOR": ("democratic", {"democratic": 90, "communism": 6, "fascism": 1, "neutrality": 3}, "einar_gerhardsen", "Einar Gerhardsen", "socialism", None),
    "DEN": ("democratic", {"democratic": 90, "communism": 6, "fascism": 1, "neutrality": 3}, "hans_hedtoft", "Hans Hedtoft", "socialism", None),
    "HOL": ("democratic", {"democratic": 90, "communism": 7, "fascism": 1, "neutrality": 2}, "willem_drees", "Willem Drees", "socialism", None),
    "BEL": ("democratic", {"democratic": 88, "communism": 8, "fascism": 1, "neutrality": 3}, "paul_henri_spaak", "Paul-Henri Spaak", "socialism", None),
    "IRE": ("democratic", {"democratic": 95, "communism": 1, "fascism": 1, "neutrality": 3}, "john_a_costello", "John A. Costello", "conservatism", None),
    "CAN": ("democratic", {"democratic": 95, "communism": 2, "fascism": 1, "neutrality": 2}, "louis_st_laurent", "Louis St. Laurent", "liberalism", None),
    "AST": ("democratic", {"democratic": 94, "communism": 3, "fascism": 1, "neutrality": 2}, "ben_chifley", "Ben Chifley", "socialism", None),
    "NZL": ("democratic", {"democratic": 95, "communism": 2, "fascism": 1, "neutrality": 2}, "peter_fraser", "Peter Fraser", "socialism", None),
    "SAF": ("democratic", {"democratic": 80, "communism": 2, "fascism": 10, "neutrality": 8}, "daniel_malan", "Daniel François Malan", "conservatism", None),
    "SPR": ("fascism", {"fascism": 70, "democratic": 10, "communism": 5, "neutrality": 15}, "francisco_franco", "Francisco Franco", "falangism", None),
    "POR": ("neutrality", {"neutrality": 75, "democratic": 15, "communism": 5, "fascism": 5}, "antonio_salazar", "António de Oliveira Salazar", "despotism", None),
    "PRC": ("communism", {"communism": 90, "democratic": 3, "fascism": 0, "neutrality": 7}, "mao_zedong", "Mao Zedong", "leninism", None),
    "CHI": ("neutrality", {"neutrality": 70, "democratic": 15, "communism": 5, "fascism": 10}, "chiang_kai_shek", "Chiang Kai-shek", "despotism", None),
    "JAP": ("democratic", {"democratic": 80, "communism": 8, "fascism": 2, "neutrality": 10}, "shigeru_yoshida", "Shigeru Yoshida", "conservatism", None),
    "KOR": ("neutrality", {"neutrality": 60, "democratic": 30, "communism": 5, "fascism": 5}, "syngman_rhee", "Syngman Rhee", "despotism", None),
    "PRK": ("communism", {"communism": 92, "democratic": 2, "fascism": 0, "neutrality": 6}, "kim_il_sung", "Kim Il-sung", "stalinism", None),
    "RAJ": ("democratic", {"democratic": 85, "communism": 7, "fascism": 2, "neutrality": 6}, "jawaharlal_nehru", "Jawaharlal Nehru", "socialism", "RAJ_INDIA"),
    "PAK": ("democratic", {"democratic": 75, "communism": 3, "fascism": 2, "neutrality": 20}, "liaquat_ali_khan", "Liaquat Ali Khan", "conservatism", None),
    "SRL": ("democratic", {"democratic": 85, "communism": 8, "fascism": 1, "neutrality": 6}, "ds_senanayake", "D. S. Senanayake", "conservatism", None),
    "ISR": ("democratic", {"democratic": 90, "communism": 6, "fascism": 1, "neutrality": 3}, "david_ben_gurion", "David Ben-Gurion", "socialism", None),
    "EGY": ("neutrality", {"neutrality": 70, "democratic": 20, "communism": 3, "fascism": 7}, "farouk", "Farouk I", "despotism", None),
    "PER": ("neutrality", {"neutrality": 70, "democratic": 15, "communism": 12, "fascism": 3}, "mohammad_reza_pahlavi", "Mohammad Reza Pahlavi", "despotism", "PER_IRAN"),
    "INS": ("democratic", {"democratic": 70, "communism": 15, "fascism": 2, "neutrality": 13}, "sukarno", "Sukarno", "populism", None),
    "PHI": ("democratic", {"democratic": 85, "communism": 8, "fascism": 1, "neutrality": 6}, "elpidio_quirino", "Elpidio Quirino", "liberalism", None),
    "BRM": ("democratic", {"democratic": 70, "communism": 20, "fascism": 1, "neutrality": 9}, "u_nu", "U Nu", "socialism", None),
    "MON": ("communism", {"communism": 95, "democratic": 1, "fascism": 0, "neutrality": 4}, "khorloogiin_choibalsan", "Khorloogiin Choibalsan", "stalinism", None),
    "VIN": ("neutrality", {"neutrality": 60, "communism": 30, "democratic": 8, "fascism": 2}, "bao_dai", "Bảo Đại", "despotism", None),
    "SIA": ("neutrality", {"neutrality": 70, "democratic": 20, "communism": 5, "fascism": 5}, "plaek_phibunsongkhram", "Plaek Phibunsongkhram", "despotism", "SIA_THAILAND"),
    "ARG": ("democratic", {"democratic": 70, "communism": 5, "fascism": 10, "neutrality": 15}, "juan_peron", "Juan Perón", "populism", None),
    "BRA": ("democratic", {"democratic": 75, "communism": 8, "fascism": 5, "neutrality": 12}, "eurico_dutra", "Eurico Gaspar Dutra", "conservatism", None),
    "MEX": ("neutrality", {"neutrality": 70, "democratic": 22, "communism": 5, "fascism": 3}, "miguel_aleman", "Miguel Alemán Valdés", "moderatism", None),
    "ICE": ("democratic", {"democratic": 90, "communism": 7, "fascism": 1, "neutrality": 2}, "stefan_johann_stefansson", "Stefán Jóhann Stefánsson", "socialism", None),
    "LUX": ("democratic", {"democratic": 92, "communism": 5, "fascism": 1, "neutrality": 2}, "pierre_dupong", "Pierre Dupong", "conservatism", None),
}

# New capitals where the 1936 one is gone or wrong.
CAPITALS = {"WGR": 51, "DDR": 64, "POL": 10, "PRC": 608, "CHI": 592, "KOR": 525, "PRK": 527, "PAK": 443,
            "ISR": 454, "EGY": 907, "SRL": 422, "VIN": 671, "LAO": 670, "CAM": 741, "INS": 1058, "JAP": 282}

NATO = ["CAN", "ENG", "FRA", "BEL", "HOL", "LUX", "ITA", "POR", "DEN", "NOR", "ICE"]
EASTERN_BLOC = ["POL", "CZE", "HUN", "ROM", "BUL", "ALB", "DDR", "MON"]
PUPPETS = {"USA": ["JAP"], "FRA": ["VIN", "LAO", "CAM"]}
RELEASED = {"HOL": ["INS"], "USA": ["PHI"], "ENG": ["RAJ", "BRM", "SRL", "EGY", "IRQ", "JOR"]}

# How modern each country's technology is in 1949: every non-doctrine technology up to this start year.
TECH_YEAR = {"USA": 1946, "SOV": 1946, "ENG": 1945, "FRA": 1944, "WGR": 1943, "DDR": 1943, "ITA": 1943,
             "CAN": 1945, "AST": 1944, "SWE": 1944, "CZE": 1943, "POL": 1942, "JAP": 1943, "PRC": 1941,
             "CHI": 1942, "YUG": 1942, "HUN": 1942, "ROM": 1942, "BUL": 1941, "FIN": 1942, "HOL": 1943,
             "BEL": 1943, "NOR": 1942, "DEN": 1942, "ISR": 1942, "RAJ": 1941, "PAK": 1940, "KOR": 1940,
             "PRK": 1941, "SPR": 1941, "TUR": 1941}
TECH_YEAR_DEFAULT = 1939

# 1949 armies: infantry divisions raised at each country's capital when the game starts. Vanilla's
# 1936 armies are removed for this start (build_mod.sanitize_history), so these are all there is until
# the 1949 orders of battle (stage 2). Any country not listed gets ARMY_DEFAULT; Appalachia keeps its own.
ARMY = {"USA": 30, "SOV": 60, "ENG": 20, "FRA": 20, "PRC": 40, "CHI": 30, "ITA": 10, "POL": 12, "YUG": 14,
        "TUR": 14, "RAJ": 14, "PAK": 6, "KOR": 6, "PRK": 10, "ISR": 5, "EGY": 6, "CZE": 8, "HUN": 5, "ROM": 8,
        "BUL": 6, "ALB": 2, "GRE": 8, "SPR": 12, "PER": 6, "ARG": 6, "BRA": 6, "CAN": 4, "AST": 4, "SWE": 6,
        "FIN": 5, "DDR": 2, "WGR": 2, "JAP": 0, "INS": 6, "VIN": 4, "MON": 3, "SAU": 3, "IRQ": 3, "SYR": 3}
ARMY_DEFAULT = 2
