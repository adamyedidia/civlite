# color_pairs = [
#     ('#FF0000', '#00FF00'),
#     ('#FF0000', '#0000FF'),
#     ('#FF0000', '#FFFF00'),
#     ('#FF0000', '#FF00FF'),
#     ('#FF0000', '#00FFFF'),
#     ('#FF0000', '#000000'),
#     ('#FF0000', '#FFFFFF'),
#     ('#FF0000', '#FFA500'),
#     ('#FF0000', '#800080'),
#     ('#00FF00', '#0000FF'),
#     ('#00FF00', '#FFFF00'),
#     ('#00FF00', '#FF00FF'),
#     ('#00FF00', '#00FFFF'),
#     ('#00FF00', '#000000'),
#     ('#00FF00', '#FFFFFF'),
#     ('#00FF00', '#FFA500'),
#     ('#00FF00', '#800080'),
#     ('#0000FF', '#FFFF00'),
#     ('#0000FF', '#FF00FF'),
#     ('#0000FF', '#00FFFF'),
#     ('#0000FF', '#000000'),
#     ('#0000FF', '#FFFFFF'),
#     ('#0000FF', '#FFA500'),
#     ('#0000FF', '#800080'),
#     ('#FFFF00', '#FF00FF'),
#     ('#FFFF00', '#00FFFF'),
#     ('#FFFF00', '#000000'),
#     ('#FFFF00', '#FFFFFF'),
#     ('#FFFF00', '#FFA500'),
#     ('#FFFF00', '#800080'),
#     ('#FF00FF', '#00FFFF'),
#     ('#FF00FF', '#000000'),
#     ('#FF00FF', '#FFFFFF'),
#     ('#FF00FF', '#FFA500'),
#     ('#FF00FF', '#800080'),
#     ('#00FFFF', '#000000'),
#     ('#00FFFF', '#FFFFFF'),
#     ('#00FFFF', '#FFA500'),
#     ('#00FFFF', '#800080'),
#     ('#000000', '#FFFFFF'),
#     ('#000000', '#FFA500'),
#     ('#000000', '#800080'),
#     ('#FFFFFF', '#FFA500'),
#     ('#FFFFFF', '#800080'),
#     ('#FFA500', '#800080'),
# ]

color_pairs = [('#00FF00', '#FFFFFF'), ('#000000', '#FFFFFF'), ('#0000FF', '#FFFFFF'), ('#FFFFFF', '#FFA500'), ('#FF0000', '#00FF00'), ('#000000', '#800080'), ('#FF0000', '#00FFFF'), ('#00FF00', '#0000FF'), ('#000000', '#FFA500'), ('#00FFFF', '#800080'), ('#FFFFFF', '#800080'), ('#FF00FF', '#FFFFFF'), ('#0000FF', '#800080'), ('#FF0000', '#000000'), ('#00FF00', '#00FFFF'), ('#FF0000', '#FF00FF'), ('#00FFFF', '#FFFFFF'), ('#FF00FF', '#FFA500'), ('#0000FF', '#000000'), ('#0000FF', '#00FFFF'), ('#00FFFF', '#000000'), ('#FF0000', '#0000FF'), ('#FF0000', '#FFFF00'), ('#00FF00', '#800080'), ('#FFFF00', '#FF00FF'), ('#FF00FF', '#000000'), ('#00FFFF', '#FFA500'), ('#FFFF00', '#000000'), ('#FFFF00', '#800080'), ('#FF0000', '#FFFFFF'), ('#00FF00', '#FFA500'), ('#0000FF', '#FFFF00'), ('#00FF00', '#FFFF00'), ('#FF0000', '#800080'), ('#00FF00', '#FF00FF'), ('#FFFF00', '#FFA500'), ('#FFFF00', '#00FFFF'), ('#FF00FF', '#00FFFF'), ('#FF0000', '#FFA500'), ('#0000FF', '#FFA500'), ('#00FF00', '#000000'), ('#FF00FF', '#800080'), ('#FFFF00', '#FFFFFF'), ('#FFA500', '#800080'), ('#0000FF', '#FF00FF')]


# CIVS = {
#     "France": {
#         "name": "France",
#         "color": "#0000ff",
#         "abilities": []
#     },
#     "England": {
#         "name": "England",
#         "color": "#ff0000",
#         "abilities": []
#     },
#     "China": {
#         "name": "China",
#         "color": "#ffff00",
#         "abilities": []
#     }
# }

ANCIENT_CIVS = {
    "Pueblo": {
        "name": "Pueblo",
        "abilities": [],
    },
    "Egypt": {
        "name": "Egypt",
        "abilities": [],
    },
    "Mycenaeans": {
        "name": "Mycenaeans",
        "abilities": [],
    },
    "Harrapans": {
        "name": "Harrapans",
        "abilities": [],
    },
    "Shang": {
        "name": "Shang",
        "abilities": [],
    },
    "Sumer": {
        "name": "Sumer",
        "abilities": [],
    },
    "Indus": {
        "name": "Indus",
        "abilities": [],
    },
    "Minoans": {
        "name": "Minoans",
        "abilities": [],
    },
    "Babylon": {
        "name": "Babylon",
        "abilities": [],
    },
    "Hittites": {
        "name": "Hittites",
        "abilities": [],
    },
    "Phoenicia": {
        "name": "Phoenicia",
        "abilities": [],
    },
    "Nazca": {
        "name": "Nazca",
        "abilities": [],
    },
    "Bantu": {
        "name": "Bantu",
        "abilities": [],
    },
    "Olmecs": {
        "name": "Olmecs",
        "abilities": [],
    },
    "Zhou": {
        "name": "Zhou",
        "abilities": [],
    },
    "Nubians": {
        "name": "Nubians",
        "abilities": [],
    },
    "Pama-Nguyan": {
        "name": "Pama-Nguyan",
        "abilities": [],
    },
    "Assyrians": {
        "name": "Assyrians",
        "abilities": [],
    },
    "Caralans": {
        "name": "Caralans",
        "abilities": [],
    },
    "Elamites": {
        "name": "Elamites",
        "abilities": [],
    },
    "Teotihuacan": {
        "name": "Teotihuacan",
        "abilities": [],
    },
    "Maya": {
        "name": "Maya",
        "abilities": [],
    },
    "Jomon": {
        "name": "Jomon",
        "abilities": [],
    },
    "Yangshao": {
        "name": "Yangshao",
        "abilities": [],
    },  
}

for i, civ in enumerate(ANCIENT_CIVS):
    ANCIENT_CIVS[civ]["primary_color"] = color_pairs[i][0]
    ANCIENT_CIVS[civ]["secondary_color"] = color_pairs[i][1]


CIVS = ANCIENT_CIVS