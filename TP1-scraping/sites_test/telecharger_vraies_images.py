"""
Script pour télécharger des vraies images depuis internet
pour les 5 sites de test
"""

import requests
import os
from PIL import Image
from io import BytesIO


def download_image(url, filepath):
    """Télécharge une image depuis une URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            # Convertir en RGB si nécessaire
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode in ("RGBA", "LA"):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Redimensionner si trop grande
            img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            img.save(filepath, "JPEG", quality=85)
            print(f"✓ Téléchargé: {os.path.basename(filepath)}")
            return True
    except Exception as e:
        print(f"✗ Erreur {os.path.basename(filepath)}: {e}")
    return False


base_dir = os.path.dirname(os.path.abspath(__file__))

# ==================== SITE 1: CHATS ====================
print("\n🐱 Téléchargement des images de chats...")
site1_images = {
    "cat_sleeping.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cat_November_2010-1a.jpg/800px-Cat_November_2010-1a.jpg",
    "cat_playing.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi-01A.jpg/800px-Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi-01A.jpg",
    "kitten_cute.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Kitten_in_a_ball.jpg/800px-Kitten_in_a_ball.jpg",
    "black_cat.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Black_Cat_Domestic.jpg/800px-Black_Cat_Domestic.jpg",
    "cat_garden.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Felis_catus-cat_on_snow.jpg/800px-Felis_catus-cat_on_snow.jpg",
}
os.makedirs(os.path.join(base_dir, "site1", "images"), exist_ok=True)
for filename, url in site1_images.items():
    download_image(url, os.path.join(base_dir, "site1", "images", filename))

# ==================== SITE 2: VOITURES ====================
print("\n🏎️ Téléchargement des images de voitures...")
site2_images = {
    "ferrari_red.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Ferrari_F50_in_London.jpg/800px-Ferrari_F50_in_London.jpg",
    "lamborghini_yellow.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Lamborghini_Aventador_LP_700-4_-_Flickr_-_Alexandre_Pr%C3%A9vot_%2829%29_%28cropped%29.jpg/800px-Lamborghini_Aventador_LP_700-4_-_Flickr_-_Alexandre_Pr%C3%A9vot_%2829%29_%28cropped%29.jpg",
    "porsche_911.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/2019_Porsche_911_Carrera_S%2C_front_9.22.19.jpg/800px-2019_Porsche_911_Carrera_S%2C_front_9.22.19.jpg",
    "mclaren_orange.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/2015-03-03_Geneva_Motor_Show_3579.JPG/800px-2015-03-03_Geneva_Motor_Show_3579.JPG",
    "bugatti_blue.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Bugatti_Chiron_%28Lime_Rock%29.jpg/800px-Bugatti_Chiron_%28Lime_Rock%29.jpg",
}
os.makedirs(os.path.join(base_dir, "site2", "images"), exist_ok=True)
for filename, url in site2_images.items():
    download_image(url, os.path.join(base_dir, "site2", "images", filename))

# ==================== SITE 3: NATURE ====================
print("\n🌿 Téléchargement des images de nature...")
site3_images = {
    "mountain_sunset.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg/800px-Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg",
    "forest_autumn.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/24_Zypresse_Toskana_2007.jpg/800px-24_Zypresse_Toskana_2007.jpg",
    "ocean_waves.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Above_the_waves.jpg/800px-Above_the_waves.jpg",
    "flower_garden.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/800px-Cat03.jpg",
    "waterfall_tropical.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Niagara_Falls_from_Skylon_Tower_2023-06-27.jpg/800px-Niagara_Falls_from_Skylon_Tower_2023-06-27.jpg",
    "desert_dunes.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Rub_al_Khali_002.JPG/800px-Rub_al_Khali_002.JPG",
}
os.makedirs(os.path.join(base_dir, "site3", "images"), exist_ok=True)
for filename, url in site3_images.items():
    download_image(url, os.path.join(base_dir, "site3", "images", filename))

# ==================== SITE 4: CUISINE ====================
print("\n🍽️ Téléchargement des images de cuisine...")
site4_images = {
    "pizza_italian.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Eq_it-na_pizza-margherita_sep2005_sml.jpg/800px-Eq_it-na_pizza-margherita_sep2005_sml.jpg",
    "sushi_japanese.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Sushi_platter.jpg/800px-Sushi_platter.jpg",
    "couscous_moroccan.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Couscous_of_Fes.JPG/800px-Couscous_of_Fes.JPG",
    "tacos_mexican.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg/800px-001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg",
    "croissant_french.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Croissant-Killer-Kropp.jpg/800px-Croissant-Killer-Kropp.jpg",
    "curry_indian.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Indian_Curry_Chicken.jpg/800px-Indian_Curry_Chicken.jpg",
}
os.makedirs(os.path.join(base_dir, "site4", "images"), exist_ok=True)
for filename, url in site4_images.items():
    download_image(url, os.path.join(base_dir, "site4", "images", filename))

# ==================== SITE 5: TECHNOLOGIE ====================
print("\n💻 Téléchargement des images de technologie...")
site5_images = {
    "smartphone_latest.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/IPhone_14_Pro_Max_Space_Black.png/400px-IPhone_14_Pro_Max_Space_Black.png",
    "laptop_gaming.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/ASUS_ROG_Zephyrus_G14_GA401IV_%2850070982991%29.png/800px-ASUS_ROG_Zephyrus_G14_GA401IV_%2850070982991%29.png",
    "smartwatch_fitness.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Apple_Watch_Series_6.jpg/400px-Apple_Watch_Series_6.jpg",
    "headphones_wireless.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Bose_QuietComfort_35_Series_II.jpg/500px-Bose_QuietComfort_35_Series_II.jpg",
    "tablet_drawing.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/IPad_Pro_12.9_inch_%284th_generation%29.png/400px-IPad_Pro_12.9_inch_%284th_generation%29.png",
    "drone_camera.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/DJI_Phantom_4_Pro_V2.0.jpg/800px-DJI_Phantom_4_Pro_V2.0.jpg",
}
os.makedirs(os.path.join(base_dir, "site5", "images"), exist_ok=True)
for filename, url in site5_images.items():
    download_image(url, os.path.join(base_dir, "site5", "images", filename))

print("\n" + "=" * 50)
print("✅ Téléchargement terminé!")
print("=" * 50)
