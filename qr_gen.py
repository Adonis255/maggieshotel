import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURATION ---
url = "https://maggieshotel.vercel.app"
main_text = "Maggie's"
sub_text = "HOTEL & BUTCHERY"
cta_text = "— Scan to explore our menu —"
logo_path = "logo.png"   # Make sure this file is in the same folder
output_filename = "maggies_premium_qr.png"

# Theme Colors
red = (212, 0, 0)       # Maggie's red
black = (0, 0, 0)       # Standard black
dark_grey = (40, 40, 40)
white = (255, 255, 255)

# --- GENERATE QR CODE ---
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H, # Allows a logo in the middle
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

# --- SETUP CANVAS (Premium Business Card Size) ---
# 1000px width is perfect for a high-res flyer or screen
canvas_width = 1000
canvas_height = 1000

# Create a clean white canvas
final_img = Image.new("RGB", (canvas_width, canvas_height), "white")
draw = ImageDraw.Draw(final_img)

# Draw a modern RED border (20px thick) around the canvas
draw.rectangle([20, 20, canvas_width-20, canvas_height-20], outline=red, width=15)

# --- DRAW TEXT (Using bold Arial to ensure it renders beautifully) ---
try:
    main_font = ImageFont.truetype("arialbd.ttf", 110)  # Bold Arial
    sub_font = ImageFont.truetype("arialbd.ttf", 40)    # Bold Arial
    cta_font = ImageFont.truetype("arial.ttf", 28)
except IOError:
    main_font = ImageFont.load_default()
    sub_font = main_font
    cta_font = main_font

# Center Main Text ("Maggie's") in Red
main_bbox = draw.textbbox((0, 0), main_text, font=main_font)
main_w = main_bbox[2] - main_bbox[0]
draw.text(((canvas_width - main_w) // 2, 80), main_text, fill=red, font=main_font)

# Center Sub Text ("HOTEL & BUTCHERY") in Black
sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
sub_w = sub_bbox[2] - sub_bbox[0]
draw.text(((canvas_width - sub_w) // 2, 200), sub_text, fill=dark_grey, font=sub_font)

# --- DRAW SEPARATOR LINE ---
line_y = 270
draw.line([(100, line_y), (canvas_width - 100, line_y)], fill=red, width=3)
# Add tiny decorative diamonds on the line
draw.polygon([(100, line_y-6), (103, line_y), (100, line_y+6), (97, line_y)], fill=red)
draw.polygon([(canvas_width - 100, line_y-6), (canvas_width - 97, line_y), (canvas_width - 100, line_y+6), (canvas_width - 103, line_y)], fill=red)

# --- PLACE QR CODE ---
qr_size = 440
qr_x = (canvas_width - qr_size) // 2
qr_y = 330
qr_resized = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
final_img.paste(qr_resized, (qr_x, qr_y))

# --- ADD LOGO CENTERED (With a glossy white background circle) ---
if os.path.exists(logo_path):
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = 110 # A perfectly sized center logo
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        center_x = qr_x + (qr_size // 2)
        center_y = qr_y + (qr_size // 2)

        # Draw a clean white circle behind the logo to separate it from the QR blocks
        circle_radius = (logo_size // 2) + 20
        draw.ellipse([center_x - circle_radius, center_y - circle_radius, 
                      center_x + circle_radius, center_y + circle_radius], fill=white, outline=red, width=5)
        
        # Paste the logo perfectly in the center
        final_img.paste(logo, (center_x - (logo_size//2), center_y - (logo_size//2)), mask=logo)
        print("✅ Premium Logo added!")
    except Exception as e:
        print(f"⚠️ Could not process logo: {e}")
else:
    print("⚠️ No 'logo.png' found. Generating elegant QR without logo.")

# --- BOTTOM CALL TO ACTION TEXT ---
cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
cta_w = cta_bbox[2] - cta_bbox[0]
draw.text(((canvas_width - cta_w) // 2, 880), cta_text, fill=red, font=cta_font)

# --- SAVE ---
final_img.save(output_filename)
print(f"🎉 Beautiful Premium QR saved as: {output_filename}")

# Quick helper to open it after saving
try:
    os.startfile(output_filename)
except:
    pass