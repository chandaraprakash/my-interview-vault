import os
from PIL import Image, ImageDraw

def process_logo():
    src_path = "/Users/kcp/.gemini/antigravity-ide/brain/e586f335-e544-4d2f-9f38-ee1b923422b1/vault_logo_badge_1779857552093.png"
    dest_path = "/Users/kcp/Documents/work/my-interview-vault/static/img/logo.png"

    if not os.path.exists(src_path):
        print(f"Error: Source image not found at {src_path}")
        return

    # Load image and convert to RGBA
    img = Image.open(src_path).convert("RGBA")
    width, height = img.size

    # Find the bounding box of the circular badge
    # We look for pixels that are not white (i.e. R < 240, G < 240, B < 240)
    left, right, top, bottom = width, 0, height, 0
    for y in range(height):
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            if r < 240 or g < 240 or b < 240:
                if x < left:
                    left = x
                if x > right:
                    right = x
                if y < top:
                    top = y
                if y > bottom:
                    bottom = y

    print(f"Detected badge bounds: left={left}, right={right}, top={top}, bottom={bottom}")

    # The circular badge is in the upper portion (above the text "VAULT")
    # Let's adjust bottom to make it a square using width as diameter
    badge_width = right - left
    badge_height = badge_width  # assuming it's circular, height should equal width
    
    # Crop the badge region
    badge_img = img.crop((left, top, left + badge_width, top + badge_height))
    
    # Create mask for circular transparency
    mask = Image.new("L", (badge_width, badge_height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, badge_width, badge_height), fill=255)
    
    # Create output image with transparency
    output_img = Image.new("RGBA", (badge_width, badge_height), (0, 0, 0, 0))
    output_img.paste(badge_img, (0, 0), mask=mask)
    
    # Resize to high-quality 256x256 logo
    final_logo = output_img.resize((256, 256), Image.Resampling.LANCZOS)
    
    # Ensure destination directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    final_logo.save(dest_path, "PNG")
    print(f"Successfully processed logo and saved to {dest_path}!")

if __name__ == "__main__":
    process_logo()
