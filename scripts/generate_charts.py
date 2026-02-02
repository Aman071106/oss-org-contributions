import json
import math
import requests
import base64
import os

# --- CONFIGURATION ---
YOUR_USERNAME = "Aman071106"
OUTPUT_FILE = "charts/org_contributions.svg"
EXCLUDED_ORGS = ["rudra-iitm", "Sachitbansal", "beingvirus", "firstcontributions", YOUR_USERNAME]
MAX_ORGS = 8  # Keep this between 6-8 so it doesn't look crowded

# --- STYLING (Cyberpunk / Dark Mode) ---
COLOR_BG = "transparent" # Transparent background
COLOR_LINE = "#30363d"   # Dark grey for connector lines
COLOR_MERGED = "#a371f7" # Neon Purple
COLOR_OPEN = "#3fb950"   # Neon Green
TEXT_COLOR = "#c9d1d9"   # GitHub Grey

def fetch_image_as_base64(url):
    """Downloads an image and converts it to base64 for embedding."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            encoded = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
    except:
        pass
    return "" # Return empty if fails

def create_circular_clip_path(id_name, x, y, r):
    """Creates a circular clip path def for avatars."""
    return f"""
    <clipPath id="{id_name}">
        <circle cx="{x}" cy="{y}" r="{r}" />
    </clipPath>
    """

def generate_svg():
    # 1. Load Data
    with open("charts/data.json") as f:
        data = json.load(f)

    # 2. Filter & Sort
    active_orgs = {
        k: v for k, v in data.items() 
        if k not in EXCLUDED_ORGS 
        and (v["MERGED"] > 0 or v["OPEN"] > 0)
    }

    # Sort by total activity
    sorted_orgs = sorted(
        active_orgs.keys(), 
        key=lambda x: (active_orgs[x]["MERGED"], active_orgs[x]["OPEN"]), 
        reverse=True
    )[:MAX_ORGS]

    # 3. Setup Layout
    width = 800
    height = 500
    center_x = width / 2
    center_y = height / 2
    radius = 180  # Distance from center to orgs
    
    # User Avatar Size
    user_r = 40
    # Org Avatar Size
    org_r = 25

    # 4. Fetch User Avatar
    user_img_url = f"https://github.com/{YOUR_USERNAME}.png"
    user_b64 = fetch_image_as_base64(user_img_url)

    # Start SVG
    svg_content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<style>.text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {TEXT_COLOR}; font-weight: 600; }} .sub {{ font-size: 10px; font-weight: 400; }}</style>',
        '<defs>'
    ]

    # Add items to main content list
    main_content = []

    # Draw Central Hub (User)
    main_content.append(f'<circle cx="{center_x}" cy="{center_y}" r="{user_r + 4}" fill="#21262d" stroke="#30363d" stroke-width="2" />')
    
    svg_content.append(create_circular_clip_path("user-clip", center_x, center_y, user_r))
    main_content.append(f'<image href="{user_b64}" x="{center_x - user_r}" y="{center_y - user_r}" width="{user_r*2}" height="{user_r*2}" clip-path="url(#user-clip)" />')

    # 5. Loop through Orgs
    num_orgs = len(sorted_orgs)
    
    for i, org_name in enumerate(sorted_orgs):
        stats = active_orgs[org_name]
        merged = stats["MERGED"]
        _open = stats["OPEN"]
        
        # Calculate Angle (distribute evenly)
        # We shift by -math.pi/2 to start at the top (12 o'clock)
        angle = (2 * math.pi * i / num_orgs) - (math.pi / 2)
        
        # Org Coords
        org_x = center_x + radius * math.cos(angle)
        org_y = center_y + radius * math.sin(angle)

        # Draw Connector Line
        # We draw dashed lines if no merged PRs, solid if merged exist
        stroke_dash = "" if merged > 0 else 'stroke-dasharray="5,5"'
        line_color = COLOR_MERGED if merged > 0 else COLOR_OPEN
        
        main_content.append(f'<line x1="{center_x}" y1="{center_y}" x2="{org_x}" y2="{org_y}" stroke="{COLOR_LINE}" stroke-width="2" {stroke_dash} />')
        
        # Org Avatar Background circle
        main_content.append(f'<circle cx="{org_x}" cy="{org_y}" r="{org_r + 3}" fill="#0d1117" stroke="{line_color}" stroke-width="2" />')

        # Fetch Org Image
        org_img_url = f"https://github.com/{org_name}.png"
        org_b64 = fetch_image_as_base64(org_img_url)
        
        clip_id = f"clip-{i}"
        svg_content.append(create_circular_clip_path(clip_id, org_x, org_y, org_r))
        main_content.append(f'<image href="{org_b64}" x="{org_x - org_r}" y="{org_y - org_r}" width="{org_r*2}" height="{org_r*2}" clip-path="url(#{clip_id})" />')

        # Add Stats Badge below org
        # Offset text slightly based on position to avoid overlapping the line
        text_y = org_y + org_r + 20
        
        # Create a stats string
        stat_text = ""
        if merged > 0:
            stat_text += f'<tspan fill="{COLOR_MERGED}">● {merged}</tspan> '
        if _open > 0:
            stat_text += f'<tspan fill="{COLOR_OPEN}">● {_open}</tspan>'
            
        main_content.append(f'<text x="{org_x}" y="{text_y}" text-anchor="middle" class="text" font-size="12">{org_name}</text>')
        main_content.append(f'<text x="{org_x}" y="{text_y + 15}" text-anchor="middle" class="text sub">{stat_text}</text>')

    # Close tags
    svg_content.append('</defs>')
    svg_content.extend(main_content)
    svg_content.append('</svg>')

    # Write File
    with open(OUTPUT_FILE, "w") as f:
        f.write("".join(svg_content))

    print(f"Generated Hub-and-Spoke diagram for {num_orgs} orgs.")

if __name__ == "__main__":
    generate_svg()