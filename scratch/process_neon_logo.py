import sys
import os
from PIL import Image

def process_neon_logo():
    # Default to Option B5 (clean glassmorphic wheel)
    default_src = "/Users/kcp/.gemini/antigravity-ide/brain/e586f335-e544-4d2f-9f38-ee1b923422b1/vault_logo_neon_clean_1779859296434.png"
    
    src_path = sys.argv[1] if len(sys.argv) > 1 else default_src
    logo_dest = "/Users/kcp/Documents/work/my-interview-vault/static/img/logo.png"
    favicon_dest = "/Users/kcp/Documents/work/my-interview-vault/static/img/favicon.ico"

    if not os.path.exists(src_path):
        print(f"Error: Source image not found at {src_path}")
        return

    # Open image and convert to RGBA
    img = Image.open(src_path).convert("RGBA")
    width, height = img.size

    # Create a new image for the transparent output
    output_data = []
    
    # We will remove the pure black background
    # To keep the soft neon glow, we scale the alpha channel for dark pixels
    # rather than doing a hard threshold.
    for y in range(height):
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            # Calculate brightness/intensity
            val = max(r, g, b)
            
            # If it's a very dark/black pixel, make it transparent
            # We use a threshold of 25 for a clean cut, but scale alpha smoothly below 45
            if val < 20:
                output_data.append((0, 0, 0, 0))
            elif val < 45:
                # Smooth alpha falloff for the outer glow edges
                factor = (val - 20) / (45 - 20)
                new_alpha = int(255 * factor)
                output_data.append((r, g, b, new_alpha))
            else:
                output_data.append((r, g, b, a))

    transparent_img = Image.new("RGBA", (width, height))
    transparent_img.putdata(output_data)

    # Find the bounding box of non-transparent pixels to crop tightly
    bbox = transparent_img.getbbox()
    if bbox:
        # Add a small padding (e.g. 20px) to prevent cutting off any outer glow
        left = max(0, bbox[0] - 20)
        top = max(0, bbox[1] - 20)
        right = min(width, bbox[2] + 20)
        bottom = min(height, bbox[3] + 20)
        
        # Crop to square bounding box
        box_width = right - left
        box_height = bottom - top
        side = max(box_width, box_height)
        
        # Center the crop
        cx, cy = (left + right) // 2, (top + bottom) // 2
        crop_left = max(0, cx - side // 2)
        crop_top = max(0, cy - side // 2)
        crop_right = min(width, crop_left + side)
        crop_bottom = min(height, crop_top + side)
        
        cropped_img = transparent_img.crop((crop_left, crop_top, crop_right, crop_bottom))
        print(f"Cropped logo bounding box: {crop_left, crop_top, crop_right, crop_bottom}")
    else:
        cropped_img = transparent_img

    # Resize and save the logo (256x256 is ideal for Docusaurus navbar logo)
    logo_img = cropped_img.resize((256, 256), Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(logo_dest), exist_ok=True)
    logo_img.save(logo_dest, "PNG")
    print(f"Saved processed logo to {logo_dest}")

    # Generate multi-resolution favicon.ico
    favicon_img = cropped_img.resize((64, 64), Image.Resampling.LANCZOS)
    favicon_img.save(favicon_dest, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print(f"Saved generated favicon.ico to {favicon_dest}")

if __name__ == "__main__":
    process_neon_logo()
