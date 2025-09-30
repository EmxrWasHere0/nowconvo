from PIL import Image
import os

# Load the icon
icon_path = 'src/nowconvo/icon.png'
icon = Image.open(icon_path)

# Sizes to generate
sizes = [16, 32, 64, 128, 256, 512]

for size in sizes:
    resized = icon.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(f'src/nowconvo/icon.png-{size}.png')

print("Icons generated.")
