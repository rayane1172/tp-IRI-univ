import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import threading


class MoteurRechercheImages:
    def __init__(self, root):
        self.root = root
        self.root.title("Moteur de Recherche d'Images - TP IRI")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a2e")

        self.image_references = []

        self.sites_to_search = [
            "http://localhost:8000/site1/index.html",  #  Chats
            "http://localhost:8000/site2/index.html",  #  Voitures
            "http://localhost:8000/site3/index.html",  #  Nature
            "http://localhost:8000/site4/index.html",  #  Cuisine
            "http://localhost:8000/site5/index.html",  #  Technologie
            "http://localhost:8000/site6/index.html",  #  Animaux Sauvages
            "http://localhost:8000/site7/index.html",  #  Architecture
            "http://localhost:8000/site8/index.html",  #  Sports Extrêmes
            "http://localhost:8000/site9/index.html",  #  Espace
            "http://localhost:8000/site10/index.html",  # Musique
        ]

        self.create_widgets()

    def create_widgets(self):
        # ==================== HEADER ====================
        header_frame = tk.Frame(self.root, bg="#16213e", height=100)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🔍 Moteur de Recherche d'Images",
            font=("Segoe UI", 20, "bold"),
            bg="#16213e",
            fg="#e94560",
        )
        title_label.pack(pady=15)

        subtitle = tk.Label(
            header_frame,
            text="Recherche par: Title | Image (src/alt) | Paragraphe",
            font=("Segoe UI", 10),
            bg="#16213e",
            fg="#a0a0a0",
        )
        subtitle.pack()

        # ==================== BARRE DE RECHERCHE ====================
        search_frame = tk.Frame(self.root, bg="#1a1a2e")
        search_frame.pack(fill=tk.X, padx=20, pady=15)

        self.search_entry = tk.Entry(
            search_frame,
            width=50,
            font=("Segoe UI", 14),
            bg="#0f3460",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
            bd=10,
        )
        self.search_entry.pack(side=tk.LEFT, padx=10, ipady=8)
        self.search_entry.bind("<Return>", lambda e: self.start_search())

        self.search_btn = tk.Button(
            search_frame,
            text="🔎 Rechercher",
            command=self.start_search,
            bg="#e94560",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor="hand2",
        )
        self.search_btn.pack(side=tk.LEFT, padx=10)

        # ==================== INFO MÉTHODES ====================
        info_frame = tk.Frame(self.root, bg="#0f3460")
        info_frame.pack(fill=tk.X, padx=20, pady=5)

        info_text = """📋 Méthode de recherche séquentielle:
        1️⃣ Chercher dans <title> du site  →  2️⃣ Chercher dans <img> (src ou alt)  →  3️⃣ Chercher dans <p> paragraphes
        ✅ Si trouvé dans au moins 1 méthode → Afficher TOUTES les images du site"""

        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Segoe UI", 9),
            bg="#0f3460",
            fg="#4ecca3",
            justify=tk.LEFT,
            padx=15,
            pady=10,
        )
        info_label.pack(fill=tk.X)

        # ==================== STATISTIQUES ====================
        stats_frame = tk.Frame(self.root, bg="#1a1a2e")
        stats_frame.pack(fill=tk.X, padx=20, pady=5)

        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg="#1a1a2e",
            fg="#ffc107",
        )
        self.stats_label.pack()

        # Label statut
        self.status_label = tk.Label(
            self.root,
            text="Entrez un mot-clé pour rechercher des images",
            font=("Segoe UI", 10),
            bg="#1a1a2e",
            fg="#a0a0a0",
        )
        self.status_label.pack(pady=5)

        # ==================== ZONE DE RÉSULTATS ====================
        results_container = tk.Frame(self.root, bg="#1a1a2e")
        results_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(results_container, bg="#1a1a2e", highlightthickness=0)
        scrollbar_y = tk.Scrollbar(
            results_container, orient="vertical", command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg="#1a1a2e")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scroll avec molette
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

    def start_search(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Attention", "Veuillez entrer un texte de recherche")
            return

        self.search_btn.config(state="disabled", text="⏳ Recherche...")

        # Effacer anciens résultats
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.image_references.clear()

        # Lancer la recherche dans un thread
        thread = threading.Thread(target=self.search_images, args=(query,))
        thread.daemon = True
        thread.start()

#! scraping
    def search_images(self, query):
        all_images = []
        query_lower = query.lower()
        sites_matched = 0

        self.update_status(f" Recherche de '{query}' dans {len(self.sites_to_search)} sites...")

        for idx, site_url in enumerate(self.sites_to_search, 1):
            site_name = f"Site {idx}"
            self.update_status(f"📡 Analyse {site_name}...")

            try:
                #! Récupérer le contenu de la page
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                response = requests.get(site_url, headers=headers, timeout=10)

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                found = False
                method_found = ""

                #! Chercher dans <title>
                title_tag = soup.find("title")
                page_title = title_tag.text.strip() if title_tag else ""

                if query_lower in page_title.lower():
                    found = True
                    method_found = "TITLE"
                    print(f" {site_name}: Trouvé dans TITLE: '{page_title}'")

                #! Chercher dans <img> (src ou alt)
                if not found:
                    for img in soup.find_all("img"):
                        img_src = img.get("src", "")
                        img_alt = img.get("alt", "")

                        #! Chercher dans src
                        if query_lower in img_src.lower():
                            found = True
                            method_found = "IMG SRC"
                            print(f" {site_name}: Trouvé dans IMG SRC: '{img_src}'")
                            break

                        #! Chercher dans alt
                        if query_lower in img_alt.lower():
                            found = True
                            method_found = "IMG ALT"
                            print(f" {site_name}: Trouvé dans IMG ALT: '{img_alt}'")
                            break

                #! Chercher dans <p> paragraphes
                if not found:
                    for p in soup.find_all("p"):
                        p_text = p.get_text(strip=True)
                        if query_lower in p_text.lower():
                            found = True
                            method_found = "PARAGRAPH"
                            print(f" {site_name}: Trouvé dans PARAGRAPH: '{p_text[:50]}...'")
                            break

                if found:
                    sites_matched += 1

                    #! Récupérer TOUTES les images du site
                    for img in soup.find_all("img"):
                        img_url = img.get("src") or img.get("data-src")

                        if not img_url:
                            continue

                        # Normaliser l'URL
                        img_url = self.normalize_url(img_url, site_url)
                        if not img_url:
                            continue

                        # Filtrer les images invalides
                        if not self.is_valid_image_url(img_url):
                            continue

                        img_data = {
                            "url": img_url,
                            "alt": img.get("alt", ""),
                            "source": page_title[:40] or site_name,
                            "method": method_found,
                            "site_url": site_url,
                        }
                        all_images.append(img_data)

                    print(
                        f"  → Ajouté {len([i for i in all_images if i['site_url'] == site_url])} images de {site_name}"
                    )
                else:
                    print(f"✗ {site_name}: Query '{query}' non trouvé")

            except Exception as e:
                print(f"❌ Erreur sur {site_name}: {e}")

        # Mettre à jour les statistiques
        self.update_stats(query, sites_matched, len(all_images))

        # Afficher les résultats
        self.search_btn.config(state="normal", text="🔎 Rechercher")
        self.update_status(
            f" {len(all_images)} image(s) trouvée(s) dans {sites_matched} site(s)"
        )
        self.display_results(all_images)

    def normalize_url(self, img_url, base_url):
        if img_url.startswith("//"):
            return "https:" + img_url
        elif img_url.startswith("/"):
            domain = "/".join(base_url.split("/")[:3])
            return domain + img_url
        elif img_url.startswith("http"):
            return img_url
        else:
            # URL relative
            base = "/".join(base_url.rsplit("/", 1)[:-1])
            return base + "/" + img_url

    def is_valid_image_url(self, url):
        invalid_patterns = [".svg", ".ico", "1x1", "placeholder", "logo", "icon"]
        url_lower = url.lower()

        if len(url) < 10 or url.startswith("data:"):
            return False

        for pattern in invalid_patterns:
            if pattern in url_lower:
                return False

        return True

    def update_stats(self, query, sites_matched, total_images):
        stats_text = f" Query: '{query}' | Sites correspondants: {sites_matched}/{len(self.sites_to_search)} | Images trouvées: {total_images}"
        self.root.after(0, lambda: self.stats_label.config(text=stats_text))

    def download_and_validate_image(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=8, stream=True)

            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                return None

            img_data = BytesIO(response.content)
            img = Image.open(img_data)

            if img.size[0] < 50 or img.size[1] < 50:
                return None

            # Convertir en RGB
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

            return img

        except Exception as e:
            return None

    def display_results(self, results):
        row = 0
        col = 0
        max_cols = 3
        displayed_count = 0

        for img_data in results:
            img = self.download_and_validate_image(img_data["url"])

            if img is None:
                continue

            try:
                # Frame pour chaque image
                img_frame = tk.Frame(
                    self.scrollable_frame,
                    bg="#16213e",
                    relief=tk.FLAT,
                    bd=0,
                    padx=8,
                    pady=8,
                )
                img_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

                # Redimensionner l'image
                img.thumbnail((220, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                # Label image
                img_label = tk.Label(img_frame, image=photo, bg="#16213e")
                img_label.pack(pady=5)
                self.image_references.append(photo)

                # Badge de la méthode trouvée
                method_colors = {
                    "TITLE": "#4ecca3",
                    "IMG SRC": "#ffc107",
                    "IMG ALT": "#00d9ff",
                    "PARAGRAPH": "#e94560",
                }
                badge_color = method_colors.get(img_data["method"], "#a0a0a0")

                badge = tk.Label(
                    img_frame,
                    text=f"🏷️ {img_data['method']}",
                    font=("Segoe UI", 8, "bold"),
                    bg=badge_color,
                    fg="black",
                    padx=8,
                    pady=2,
                )
                badge.pack(pady=2)

                # Alt text
                if img_data["alt"]:
                    alt_label = tk.Label(
                        img_frame,
                        text=f"{img_data['alt'][:35]}...",
                        font=("Segoe UI", 8),
                        bg="#16213e",
                        fg="#a0a0a0",
                        wraplength=200,
                    )
                    alt_label.pack()

                # Source
                source_label = tk.Label(
                    img_frame,
                    text=f"🌐 {img_data['source'][:25]}",
                    font=("Segoe UI", 8, "italic"),
                    bg="#16213e",
                    fg="#7f8c8d",
                )
                source_label.pack(pady=2)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

                displayed_count += 1

            except Exception as e:
                print(f"Erreur affichage: {e}")
                continue

        if displayed_count == 0:
            no_result = tk.Label(
                self.scrollable_frame,
                text="❌ Aucune image trouvée pour cette recherche",
                font=("Segoe UI", 14),
                bg="#1a1a2e",
                fg="#e94560",
            )
            no_result.pack(pady=50)

        self.update_status(f"✅ {displayed_count} image(s) affichée(s)")

    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))


if __name__ == "__main__":
    root = tk.Tk()
    app = MoteurRechercheImages(root)
    root.mainloop()
