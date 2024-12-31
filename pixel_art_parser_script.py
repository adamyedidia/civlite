from PIL import Image

def is_blue_pixel(r, g, b, threshold=0):
    # Simple heuristic: pixel is considered "blue" if blue > red + green
    return b > r and b > g

def assign_team_colors(blue_colors):
    """
    Given a dictionary of {color: count}, where color is (r,g,b,a),
    return a mapping from specific blue shades to 'team color 1'/'team color 2'.
    If only one blue shade found, all blue pixels become 'team color 1'.
    If two or more, pick the two bluest shades.
    """
    if not blue_colors:
        return {}
    
    # Calculate blueness score for each color (how much blue dominates over other channels)
    def blueness_score(color):
        r, g, b, a = color
        return b - max(r, g)  # Higher score means more distinctly blue
    
    # Sort by blueness, descending
    sorted_blues = sorted(blue_colors.keys(), key=blueness_score, reverse=True)
    
    print("sorted_blues by blueness", sorted_blues)

    # Take the two bluest shades
    if len(sorted_blues) == 1:
        # Only one distinct blue shade
        return {sorted_blues[0]: "team color 1"}
    else:
        # At least two distinct blues
        return {
            sorted_blues[0]: "team color 1",
            sorted_blues[1]: "team color 2"
        }
    
def create_empty_row(width):
    """Create a row of transparent pixels"""
    return [(0, 0, 0, 0) for _ in range(width)]

def normalize_frame_dimensions(frames, max_width, max_height):
    """
    Normalize a frame to the target dimensions by padding with transparent pixels.
    Adds padding primarily to left for width, adds padding to top for height.
    """
    current_height = len(frames)
    current_width = len(frames[0]) if frames else 0
    
    # Add rows to top to reach target height
    height_padding = max_height - current_height
    padded_frames = [create_empty_row(current_width) for _ in range(height_padding)] + frames
    
    # Add columns primarily to left side
    width_padding = max_width - current_width
    left_padding = width_padding  # All padding goes to left
    right_padding = 0            # No padding on right
    
    padded_frames = [
        [(0, 0, 0, 0)] * left_padding + row + [(0, 0, 0, 0)] * right_padding
        for row in padded_frames
    ]
    
    return padded_frames
def parse_sprite_sheet(image_path):
    # Load the image
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()
    
    print("pixels", pixels)

    print(pixels[0,0])

    # for y in range(height):
    #     for x in range(width):
    #         r, g, b, a = pixels[x, y]
    #         if a != 0 and (r != 0 or g != 0 or b != 0):  # Non-transparent
    #             if x < minX: minX = x
    #             if y < minY: minY = y
    #             if x > maxX: maxX = x
    #             if y > maxY: maxY = y

    # Identify blue shades in the trimmed area
    blue_colors = {}
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a > 0 and is_blue_pixel(r, g, b):
                blue_colors[(r, g, b, a)] = blue_colors.get((r, g, b, a), 0) + 1

    # Assign team colors
    team_color_map = assign_team_colors(blue_colors)

    print("team_color_map", team_color_map)

    def row_contains_content(row: int):
        for x in range(width):
            r, g, b, a = pixels[x, row]
            if a != 0 and (r != 0 or g != 0 or b != 0):  # Non-transparent
                return True
        return False
    
    def column_contains_content(column: int):
        for y in range(height):
            r, g, b, a = pixels[column, y]
            if a != 0 and (r != 0 or g != 0 or b != 0):  # Non-transparent
                return True
        return False

    contentful_rows = [i for i in range(height) if row_contains_content(i)]
    contentful_columns = [i for i in range(width) if column_contains_content(i)]

    print("contentful_rows", contentful_rows)
    print("contentful_columns", contentful_columns)

    def get_contiguous_regions(indices):
        if not indices:
            return []
        regions = []
        current_region = [indices[0]]
        
        for i in range(1, len(indices)):
            if indices[i] == indices[i-1] + 1:
                current_region.append(indices[i])
            else:
                regions.append((min(current_region), max(current_region)))
                current_region = [indices[i]]
        
        regions.append((min(current_region), max(current_region)))
        return regions

    row_regions = get_contiguous_regions(contentful_rows)

    # Create 2D array of frames
    frames = []
    for row_start, row_end in row_regions:
        def column_contains_content_in_row_region(column: int):
            for y in range(row_start, row_end + 1):
                r, g, b, a = pixels[column, y]
                if a != 0 and (r != 0 or g != 0 or b != 0):  # Non-transparent
                    return True
            return False

        contentful_columns_in_region = [
            i for i in range(width) 
            if column_contains_content_in_row_region(i)
        ]

        column_regions = get_contiguous_regions(contentful_columns_in_region)
        print(f"Found {len(column_regions)} column regions for rows {row_start}-{row_end}")

        row_frames = []
        for col_start, col_end in column_regions:
            # Get dimensions for this frame
            region_width = col_end - col_start + 1
            region_height = row_end - row_start + 1
            
            # Create array for this frame
            frame_data = []
            has_content = False
            
            # Copy pixels from the original image
            for y in range(row_start, row_end + 1):
                row_data = []
                for x in range(col_start, col_end + 1):
                    pixel = pixels[x, y]
                    # Check if this pixel is a team color
                    if pixel in team_color_map:
                        row_data.append(team_color_map[pixel])
                    else:
                        row_data.append(pixel)
                    # Check if this pixel has content
                    if pixel[3] != 0 and (pixel[0] != 0 or pixel[1] != 0 or pixel[2] != 0):
                        has_content = True
                frame_data.append(row_data)
            
            # Only append frame if it contains non-empty pixels
            if has_content:
                row_frames.append(frame_data)
        
        # Only append row if it contains any frames
        if row_frames:
            frames.append(row_frames)

    # Define animation states
    animation_states = ['idle', 'move', 'charge', 'jump', 'attack', 'ouch', 'die']
    
    normalized_frames = []
    for row_frames in frames:
        if not row_frames:
            continue
            
        # Find maximum dimensions for this animation
        max_height = max(len(frame) for frame in row_frames)
        max_width = max(len(frame[0]) for frame in row_frames if frame)
        
        # Normalize all frames in this animation
        normalized_row_frames = [
            normalize_frame_dimensions(frame, max_width, max_height)
            for frame in row_frames
        ]
        normalized_frames.append(normalized_row_frames)
    
    # Create JavaScript object string
    animation_states = ['idle', 'move', 'charge', 'jump', 'attack', 'ouch', 'die']
    js_output = "const spriteData = {\n"
    
    for i, row_frames in enumerate(normalized_frames):
        if i >= len(animation_states):
            break
            
        state_name = animation_states[i]
        js_output += f"  {state_name}: [\n"
        
        # Add each frame in the row
        for frame in row_frames:
            js_output += "    [\n"
            # Add each row of pixels
            for row in frame:
                js_output += "      ["
                # Add each pixel in the row
                pixel_strings = []
                for pixel in row:
                    if isinstance(pixel, str):  # Team color
                        pixel_strings.append(f'"{pixel}"')
                    else:  # RGBA tuple
                        pixel_strings.append(str(list(pixel)))
                js_output += ", ".join(pixel_strings)
                js_output += "],\n"
            js_output += "    ],\n"
        
        js_output += "  ],\n"
    
    js_output += "};\n\nexport default spriteData;"

    # Write to a .js file
    output_path = image_path.rsplit('.', 1)[0] + '.js'
    with open(output_path, 'w') as f:
        f.write(js_output)

    return normalized_frames

def save_frame_as_image(frame_data, output_path="output_frame.png"):
    """
    Given a single frame of data (16x16 array of RGBA or 'team color x'),
    save it as an image.
    "team color 1" -> white (255,255,255,255)
    "team color 2" -> gray  (128,128,128,255)
    """
    frame_height = len(frame_data)
    frame_width = len(frame_data[0]) if frame_data else 0
    
    img = Image.new("RGBA", (frame_width, frame_height))
    img_pixels = img.load()
    
    for y in range(frame_height):
        for x in range(frame_width):
            val = frame_data[y][x]
            if val == "team color 1":
                img_pixels[x, y] = (255, 0, 0, 255)
            elif val == "team color 2":
                img_pixels[x, y] = (128, 0, 0, 255)
            else:
                img_pixels[x, y] = val
    
    img.save(output_path)

# Example usage:
result = parse_sprite_sheet("raw_pixel_art/MiniCavalierMan.png")
print(result)
if result:
    for i, out in enumerate(result):
        print(f"output {i}")

        print("out", out)

        for j, frame in enumerate(out):
            save_frame_as_image(frame, f"output_frame_{i}_{j}.png")
