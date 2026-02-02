import json
import math
import requests
import base64
import os

# --- CONFIGURATION ---
YOUR_USERNAME = "Aman071106"
OUTPUT_FILE = "charts/org_contributions.svg"
EXCLUDED_ORGS = ["rudra-iitm", "Sachitbansal", "beingvirus", "firstcontributions", YOUR_USERNAME]
MAX_ORGS = 8 

# --- STYLING ---
COLOR_BG = "transparent"
COLOR_LINE = "#30363d"   
COLOR_MERGED = "#a371f7" # Neon Purple
COLOR_OPEN = "#3fb950"   # Neon Green
TEXT_COLOR = "#c9d1d9"   

def fetch_image_as_base64(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            encoded = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
    except:
        pass
    return "" 

def create_circular_clip_path(id_name, x, y, r):
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
    orbit_radius = 180  # Distance to org center
    
    user_r = 40
    org_r = 25
    gap = 10  # Space between avatar and line

    # 4. Fetch User Avatar
    user_img_url = f"https://github.com/{YOUR_USERNAME}.png"
    user_b64 = fetch_image_as_base64(user_img_url)

    # Start SVG
    svg_content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<style>.text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: {TEXT_COLOR}; font-weight: 600; }} .sub {{ font-size: 10px; font-weight: 400; }}</style>',
        '<defs>',
        # Define Arrow Marker
        f'<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        f'<path d="M0,0 L0,6 L9,3 z" fill="{COLOR_LINE}" />',
        '</marker>'
    ]

    main_content = []

    # Draw Central User Avatar
    svg_content.append(create_circular_clip_path("user-clip", center_x, center_y, user_r))
    
    # Outer Glow Ring for User
    main_content.append(f'<circle cx="{center_x}" cy="{center_y}" r="{user_r + 4}" fill="#21262d" stroke="#30363d" stroke-width="2" />')
    
    # User Image
    main_content.append(f'<image href="{user_b64}" x="{center_x - user_r}" y="{center_y - user_r}" width="{user_r*2}" height="{user_r*2}" clip-path="url(#user-clip)" />')

    # 5. Loop through Orgs
    num_orgs = len(sorted_orgs)
    
    for i, org_name in enumerate(sorted_orgs):
        stats = active_orgs[org_name]
        merged = stats["MERGED"]
        _open = stats["OPEN"]
        
        # Calculate Angle
        angle = (2 * math.pi * i / num_orgs) - (math.pi / 2)
        
        # --- KEY FIX: Calculate Start and End points for the Line ---
        # Start: Center + UserRadius + Gap
        start_dist = user_r + gap + 5
        x1 = center_x + start_dist * math.cos(angle)
        y1 = center_y + start_dist * math.sin(angle)
        
        # End: Center + OrbitRadius - OrgRadius - Gap
        end_dist = orbit_radius - org_r - gap
        x2 = center_x + end_dist * math.cos(angle)
        y2 = center_y + end_dist * math.sin(angle)

        # Org Center Coordinates (for placing the icon)
        org_x = center_x + orbit_radius * math.cos(angle)
        org_y = center_y + orbit_radius * math.sin(angle)

        # Draw Connector Line with Arrow
        stroke_dash = "" if merged > 0 else 'stroke-dasharray="5,5"'
        
        # Append line BEFORE org icon so it sits behind it if there's overlap
        main_content.insert(0, f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLOR_LINE}" stroke-width="2" {stroke_dash} marker-end="url(#arrow)" />')
        
        # Fetch Org Image
        org_img_url = f"https://github.com/{org_name}.png"
        org_b64 = fetch_image_as_base64(org_img_url)
        
        clip_id = f"clip-{i}"
        svg_content.append(create_circular_clip_path(clip_id, org_x, org_y, org_r))
        
        # Org Icon Background & Image
        ring_color = COLOR_MERGED if merged > 0 else COLOR_OPEN
        main_content.append(f'<circle cx="{org_x}" cy="{org_y}" r="{org_r + 3}" fill="#0d1117" stroke="{ring_color}" stroke-width="2" />')
        main_content.append(f'<image href="{org_b64}" x="{org_x - org_r}" y="{org_y - org_r}" width="{org_r*2}" height="{org_r*2}" clip-path="url(#{clip_id})" />')

        # Stats Text
        text_y = org_y + org_r + 20
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