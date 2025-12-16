"""
Script pour télécharger des vraies images depuis Picsum (Lorem Picsum)
Service de placeholder d'images réelles
"""

import requests
import os
from PIL import Image
from io import BytesIO
import time


def download_image(url, filepath, text_overlay=None):
    """Télécharge une image depuis une URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(filepath, "JPEG", quality=90)
            print(f"✓ {os.path.basename(filepath)}")
            return True
    except Exception as e:
        print(f"✗ {os.path.basename(filepath)}: {e}")
    return False


base_dir = os.path.dirname(os.path.abspath(__file__))

# Utiliser Lorem Picsum pour des images réelles variées
# https://picsum.photos - Service gratuit d'images placeholder réelles

images_config = {
    "site1/images": {
        "cat_sleeping.jpg": "https://placekitten.com/400/300",
        "cat_playing.jpg": "https://placekitten.com/401/300",
        "kitten_cute.jpg": "https://placekitten.com/400/301",
        "black_cat.jpg": "https://placekitten.com/402/300",
        "cat_garden.jpg": "https://placekitten.com/400/302",
    },
    "site2/images": {
        "ferrari_red.jpg": "https://picsum.photos/seed/ferrari/400/300",
        "lamborghini_yellow.jpg": "https://picsum.photos/seed/lambo/400/300",
        "porsche_911.jpg": "https://picsum.photos/seed/porsche/400/300",
        "mclaren_orange.jpg": "https://picsum.photos/seed/mclaren/400/300",
        "bugatti_blue.jpg": "https://picsum.photos/seed/bugatti/400/300",
    },
    "site3/images": {
        "mountain_sunset.jpg": "https://picsum.photos/seed/mountain/400/300",
        "forest_autumn.jpg": "https://picsum.photos/seed/forest/400/300",
        "ocean_waves.jpg": "https://picsum.photos/seed/ocean/400/300",
        "flower_garden.jpg": "https://picsum.photos/seed/flower/400/300",
        "waterfall_tropical.jpg": "https://picsum.photos/seed/waterfall/400/300",
        "desert_dunes.jpg": "https://picsum.photos/seed/desert/400/300",
    },
    "site4/images": {
        "pizza_italian.jpg": "https://picsum.photos/seed/pizza/400/300",
        "sushi_japanese.jpg": "https://picsum.photos/seed/sushi/400/300",
        "couscous_moroccan.jpg": "https://picsum.photos/seed/couscous/400/300",
        "tacos_mexican.jpg": "https://picsum.photos/seed/tacos/400/300",
        "croissant_french.jpg": "https://picsum.photos/seed/croissant/400/300",
        "curry_indian.jpg": "https://picsum.photos/seed/curry/400/300",
    },
    "site5/images": {
        "smartphone_latest.jpg": "https://picsum.photos/seed/phone/400/300",
        "laptop_gaming.jpg": "https://picsum.photos/seed/laptop/400/300",
        "smartwatch_fitness.jpg": "https://picsum.photos/seed/watch/400/300",
        "headphones_wireless.jpg": "https://picsum.photos/seed/headphones/400/300",
        "tablet_drawing.jpg": "https://picsum.photos/seed/tablet/400/300",
        "drone_camera.jpg": "https://picsum.photos/seed/drone/400/300",
    },
}

print("📥 Téléchargement des images réelles...")
print("=" * 50)

for folder, images in images_config.items():
    folder_path = os.path.join(base_dir, folder)
    os.makedirs(folder_path, exist_ok=True)

    site_name = folder.split("/")[0]
    print(f"\n📂 {site_name}:")

    for filename, url in images.items():
        filepath = os.path.join(folder_path, filename)
        download_image(url, filepath)
        time.sleep(0.3)  # Petit délai pour éviter le rate limiting

print("\n" + "=" * 50)
print("✅ Toutes les images ont été téléchargées!")
print("=" * 50)
