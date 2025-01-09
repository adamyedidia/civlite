from PIL import Image
import json
from collections import Counter
import os
from pathlib import Path

def extract_colors_from_flag(flag_path):
    """Extract the two most common colors from a flag image, ignoring border pixels."""
    img = Image.open(flag_path).convert('RGBA')
    width, height = img.size
    pixels = []
    
    # Get all pixels except the border pixels
    for y in range(1, height-1):
        for x in range(1, width-1):
            pixels.append(img.getpixel((x, y)))
    
    # Filter out transparent pixels and convert to hex
    color_counts = Counter(
        '#{:02x}{:02x}{:02x}'.format(r, g, b)
        for r, g, b, a in pixels
        if a > 128  # Only count pixels that aren't very transparent
    )
    
    # Get the two most common colors
    most_common = color_counts.most_common(2)
    if len(most_common) < 2:
        return most_common[0][0], most_common[0][0]
    return most_common[0][0], most_common[1][0]

def generate_civ_colors_dict():
    # Read CivToFlagName.js
    with open('frontend/src/CivToFlagName.js', 'r') as f:
        content = f.read()
        # Extract the dictionary content
        dict_content = content.split('export const CIV_TO_FLAG_NAME = ')[1]
        dict_content = dict_content.split('}')[0] + '}'
        # Convert to proper JSON format
        dict_content = dict_content.replace("'", '"')
        dict_content = dict_content.replace('// Placeholder', "")
        dict_content = dict_content.replace('?', "")
        dict_content = dict_content.strip()
        flag_mapping = json.loads(dict_content)

    civ_colors = {}
    
    for civ_name, flag_name in flag_mapping.items():
        flag_path = f'frontend/public/flags/{flag_name}-large.png'
        if os.path.exists(flag_path):
            try:
                primary, secondary = extract_colors_from_flag(flag_path)
                civ_colors[civ_name] = (primary, secondary)
                print(f"Processed {civ_name}: {primary}, {secondary}")
            except Exception as e:
                print(f"Error processing {civ_name}: {e}")
        else:
            print(f"Warning: Flag file not found for {civ_name}: {flag_path}")

    # Output the dictionary in Python format
    print("\nGenerated Python dictionary:\n")
    print("CIV_COLORS = {")
    for civ_name, colors in civ_colors.items():
        print(f'    "{civ_name}": {colors},')
    print("}")

def soften_color(hex_color):
    """Move a hex color halfway towards #888888."""
    # Convert middle grey to RGB
    MIDDLE_GREY = (136, 136, 136)  # #888888
    
    # Convert hex to RGB
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    is_dark = 2*r + 2*g + b < 255

    if is_dark:
        new_r = int(max(1, min(255, 2*r)))
        new_g = int(max(1, min(255, 2*g)))
        new_b = int(max(1, min(255, 2*b)))

        total_color = new_r + new_g + new_b
        target_amount = 192

        scale_factor = target_amount / total_color
        new_r = int(scale_factor * new_r)
        new_g = int(scale_factor * new_g)
        new_b = int(scale_factor * new_b)
    else:
        new_r = r
        new_g = g
        new_b = b
    
    # Convert back to hex
    return f'#{new_r:02x}{new_g:02x}{new_b:02x}'

def soften_civ_colors(civ_colors):
    print("CIV_COLORS = {")
    for civ_name, (primary, secondary) in civ_colors.items():
        soft_primary = soften_color(primary)
        soft_secondary = soften_color(secondary)
        print(f'    "{civ_name}": ("{soft_primary}", "{soft_secondary}"),')
    print("}")
CIV_COLORS = {
    "Barbarians": ('#000000', '#f50021'),
    "Pueblo": ('#ed0000', '#ffffff'),
    "Egypt": ('#ce1126', '#000000'),
    "Mycenaeans": ('#008800', '#ffffff'),
    "Harrapans": ('#ff0000', '#000000'),
    "Shang": ('#229e45', '#f8e509'),
    "Sumer": ('#32cbfe', '#ffb012'),
    "Indus": ('#00aad4', '#ffcc00'),
    "Minoans": ('#2a6b11', '#66950c'),
    "Babylon": ('#125dd3', '#eea831'),
    "Caralans": ('#ffffff', '#909090'),
    "Troy": ('#2194de', '#ce1029'),
    "Nubians": ('#078930', '#000080'),
    "Teotihuacan": ('#fe0000', '#000000'),
    "Akkad": ('#0b1728', '#ffff00'),
    "Assyria": ('#ffffff', '#000077'),
    "Jomon": ('#e70013', '#000000'),
    "Yangshao": ('#e80000', '#ffffff'),
    "Longshan": ('#0099cc', '#ffe513'),
    "Olmecs": ('#e20212', '#00ffff'),
    "Hittites": ('#b62dd7', '#ffb200'),
    "Phoenicia": ('#0066ff', '#cc0000'),
    "Elamites": ('#800080', '#ffffff'),
    "Lydia": ('#0018a8', '#d81c3f'),
    "Thrace": ('#003490', '#ffffff'),
    "Polynesia": ('#003580', '#ffffff'),
    "Scythians": ('#fed100', '#000000'),
    "Sparta": ('#ce1126', '#000000'),
    "Athens": ('#ffffff', '#0061f3'),
    "Persia": ('#380b62', '#c73d30'),
    "Macedonia": ('#0078f0', '#0179ef'),
    "Maurya": ('#006233', '#ffc400'),
    "Chola": ('#ffa101', '#000000'),
    "Qin": ('#000000', '#ffffff'),
    "Romans": ('#cc0000', '#ffd90c'),
    "Parthia": ('#630085', '#e7bc2a'),
    "Carthage": ('#0066ff', '#cc0000'),
    "Han": ('#e20212', '#b3a400'),
    "Gupta": ('#ffff00', '#aa0000'),
    "Huns": ('#f9f9f9', '#e7c03b'),
    "Franks": ('#000099', '#ffd700'),
    "Maya": ('#364a90', '#ffffff'),
    "Celts": ('#59a859', '#ffff00'),
    "Jin": ('#44aa00', '#000000'),
    "Byzantines": ('#c8100b', '#f8c420'),
    "Srivijaya": ('#ff0000', '#002d98'),
    "Umayyads": ('#0099cc', '#009933'),
    "Abbasids": ('#ce1126', '#ffffff'),
    "Vikings": ('#ffffff', '#000000'),
    "Khmer": ('#187e37', '#cdd5cf'),
    "Seljuks": ('#2d96ff', '#ffffff'),
    "Castile": ('#cc0000', '#bda944'),
    "England": ('#ffffff', '#cc0000'),
    "Novgorod": ('#ffffff', '#0087dd'),
    "Portugal": ('#ff0000', '#009900'),
    "Aragon": ('#fcdd09', '#da121a'),
    "Bohemia": ('#ffffff', '#0080ff'),
    "Mongols": ('#e90649', '#0082d1'),
    "Delhi": ('#0a5c12', '#fc000f'),
    "Mali": ('#ce1126', '#fcd116'),
    "Ethiopia": ('#298c08', '#ef2118'),
    "Denmark": ('#d00c33', '#ffffff'),
    "Sukhothai": ('#e70000', '#ffffff'),
    "Mamluks": ('#fcd116', '#fcd116'),
    "Inca": ('#df0000', '#ffa000'),
    "Austria-Hungary": ('#df0000', '#ffffff'),
    "Majapahit": ('#e70011', '#ffffff'),
    "Ottomans": ('#ff0000', '#008000'),
    "Vijayanagara": ('#00267f', '#ffc726'),
    "Bahmani": ('#0070ff', '#007000'),
    "Ming": ('#ed1c24', '#00a651'),
    "Timurids": ('#000000', '#ffffff'),
    "Joseon": ('#ffe000', '#ff0003'),
    "Aztecs": ('#dc3632', '#000000'),
    "Songhai": ('#ffffff', '#3399ff'),
    "Spain": ('#c60b1e', '#ffc400'),
    "Iroquois": ('#821a7b', '#ffffff'),
    "Poland": ('#df0000', '#ffffff'),
    "Mughals": ('#306030', '#d40d0d'),
    "United Kingdom": ('#cc0000', '#000066'),
    "Marathas": ('#ffffff', '#ff9600'),
    "Prussia": ('#ffffff', '#000000'),
    "Comanches": ('#0000ff', '#c80000'),
    "Russia": ('#ffffff', '#fe0101'),
    "United States": ('#bd3d44', '#ffffff'),
    "Mexico": ('#0b7226', '#bc0000'),
    "Zulu": ('#ffffff', '#b10c0c'),
    "Japan": ('#ffffff', '#d30000'),
    "Sweden": ('#004073', '#ffcc00'),
    "Brazil": ('#229e45', '#f8e509'),
    "Italy": ('#005700', '#ffffff'),
    "Canada": ('#ff0000', '#ffffff'),
    "Germany": ('#000000', '#ffce00'),
    "Korea": ('#ffffff', '#ff1600'),
    "Australia": ('#000066', '#cc0000'),
    "Soviet Union": ('#cc0000', '#cd0400'),
    "Turkey": ('#e30a17', '#ffffff'),
    "Indonesia": ('#e70011', '#ffffff'),
    "India": ('#e77300', '#329203'),
    "Communist China": ('#e20212', '#f6e204'),
    "Unified Latin America": ('#75aadb', '#ffffff'),
    "NATO": ('#00319c', '#214ca9'),
    "Arctic Alliance": ('#fe6500', '#ffffff'),
    "Greater EuroZone": ('#0000a9', '#0101a8'),
    "Celestial Empire": ('#ff0000', '#009933'),
    "The Machine Intelligence": ('#000000', '#26d009'),
    "Luna": ('#000000', '#a8a8a8'),
}
soften_civ_colors(CIV_COLORS)


if __name__ == "__main__":
    generate_civ_colors_dict()