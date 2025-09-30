from PIL import Image
import os

# Load the original icon
original_icon = Image.open('src/nowconvo/resources/icon.png')

# Required sizes
sizes = [16, 32, 64, 128, 256, 512]

# Directory for desktop icons
desktop_icons_dir = 'src/nowconvo/resources/desktop_icons'
os.makedirs(desktop_icons_dir, exist_ok=True)

# Resize and save each size with the correct name
for size in sizes:
    resized_icon = original_icon.resize((size, size), Image.Resampling.LANCZOS)
    filename = f'{desktop_icons_dir}/com.now.convo.nowconvo-{size}.png'
    resized_icon.save(filename)
    print(f'Saved {filename}')

print('Desktop icons generated.')
