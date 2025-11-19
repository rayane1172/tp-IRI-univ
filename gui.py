"""
Module : Interface Graphique du Moteur de Recherche d'Images
==============================================================

Ce module contient l'interface graphique (GUI) pour le moteur de recherche.

Auteur : TP ISI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2

# Importer le moteur de recherche depuis le fichier dct_engine.py
from dct_engine import ImageSearchEngine


# ============================================================================
# CLASSE : Interface graphique du moteur de recherche
# ============================================================================
class SearchEngineGUI:
    """
    Interface graphique simple pour le moteur de recherche

    Cette classe crée une fenêtre Tkinter avec 3 étapes :
    1. Sélectionner le dossier d'images à indexer
    2. Charger l'image de requête
    3. Lancer la recherche et afficher les résultats
    """

    def __init__(self, root):
        """
        Initialisation de l'interface graphique

        Args:
            root: Fenêtre Tkinter principale
        """
        self.root = root
        self.root.title("🔍 Moteur de Recherche d'Images - DCT")
        self.root.geometry("1000x700")

        # Créer le moteur de recherche
        self.moteur = ImageSearchEngine()

        # Variables
        self.image_requete = None
        self.dossier_images = None

        # Créer l'interface
        self.creer_interface()

    def creer_interface(self):
        """
        Crée tous les éléments de l'interface graphique
        """
        # Style
        style = ttk.Style()
        style.theme_use("clam")

        # TITRE
        titre = ttk.Label(
            self.root,
            text="🔍 Moteur de Recherche d'Images",
            font=("Arial", 20, "bold"),
        )
        titre.pack(pady=10)

        # ÉTAPE 1 : Sélectionner le dossier d'images
        frame_etape1 = ttk.LabelFrame(
            self.root, text="ÉTAPE 1 : Sélectionner le dossier d'images", padding=10
        )
        frame_etape1.pack(fill=tk.X, padx=10, pady=5)

        self.label_dossier = ttk.Label(
            frame_etape1, text="Aucun dossier sélectionné", foreground="gray"
        )
        self.label_dossier.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            frame_etape1,
            text="📁 Choisir le dossier",
            command=self.selectionner_dossier,
        ).pack(side=tk.RIGHT, padx=5)

        # ÉTAPE 2 : Charger l'image de requête
        frame_etape2 = ttk.LabelFrame(
            self.root, text="ÉTAPE 2 : Charger l'image de requête", padding=10
        )
        frame_etape2.pack(fill=tk.X, padx=10, pady=5)

        # Canvas pour afficher l'image de requête
        self.canvas_requete = tk.Canvas(
            frame_etape2, width=200, height=200, bg="lightgray"
        )
        self.canvas_requete.pack(side=tk.LEFT, padx=10)

        ttk.Button(
            frame_etape2, text="📷 Charger l'image", command=self.charger_image_requete
        ).pack(side=tk.LEFT, padx=5)

        # ÉTAPE 3 : Lancer la recherche
        frame_etape3 = ttk.LabelFrame(
            self.root, text="ÉTAPE 3 : Lancer la recherche", padding=10
        )
        frame_etape3.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_etape3, text="Nombre de résultats:").pack(side=tk.LEFT, padx=5)

        self.nb_resultats = tk.IntVar(value=5)
        ttk.Spinbox(
            frame_etape3, from_=1, to=10, textvariable=self.nb_resultats, width=5
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            frame_etape3, text="🔍 RECHERCHER", command=self.lancer_recherche
        ).pack(side=tk.RIGHT, padx=5)

        # RÉSULTATS
        frame_resultats = ttk.LabelFrame(
            self.root, text="📊 Résultats de la recherche", padding=10
        )
        frame_resultats.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Zone de texte pour les résultats
        self.zone_resultats = tk.Text(frame_resultats, height=15, font=("Courier", 10))
        self.zone_resultats.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_resultats, command=self.zone_resultats.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.zone_resultats.config(yscrollcommand=scrollbar.set)

        # Message de bienvenue
        self.afficher_message_bienvenue()

    def afficher_message_bienvenue(self):
        """
        Affiche le message de bienvenue dans la zone de résultats
        """
        message = """
╔══════════════════════════════════════════════════════════════╗
║     MOTEUR DE RECHERCHE D'IMAGES PAR SIMILARITÉ (DCT)       ║
╚══════════════════════════════════════════════════════════════╝

📋 Mode d'emploi :

1️⃣  Sélectionnez le dossier contenant vos images
    (Exemple: le dossier avec 1.jpg, 2.jpg, 3.jpg, etc.)

2️⃣  Chargez une image de requête
    (L'image que vous voulez rechercher)

3️⃣  Cliquez sur RECHERCHER

📊 Le système va :
   • Analyser toutes les images avec la DCT
   • Comparer l'image de requête avec la base
   • Afficher les 5 images les plus similaires

💡 Astuce :
   Plus la similarité est proche de 1.00, plus l'image
   est similaire à votre image de requête !
"""
        self.zone_resultats.insert(tk.END, message)
        self.zone_resultats.config(state=tk.DISABLED)

    def selectionner_dossier(self):
        """
        Sélectionne et indexe le dossier d'images
        """
        dossier = filedialog.askdirectory(title="Sélectionner le dossier d'images")

        if not dossier:
            return

        self.dossier_images = dossier

        # Indexer le dossier
        nb_images = self.moteur.indexer_dossier(dossier)

        # Mettre à jour le label
        self.label_dossier.config(
            text=f"✅ {nb_images} images indexées dans : {dossier}", foreground="green"
        )

        messagebox.showinfo(
            "Succès", f"{nb_images} images ont été indexées avec succès !"
        )

    def charger_image_requete(self):
        """
        Charge l'image de requête et l'affiche dans le canvas
        """
        fichier = filedialog.askopenfilename(
            title="Sélectionner l'image de requête",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")],
        )

        if not fichier:
            return

        try:
            # Charger l'image en niveaux de gris
            self.image_requete = cv2.imread(fichier, cv2.IMREAD_GRAYSCALE)

            # Afficher sur le canvas (redimensionner pour le canvas)
            h, w = self.image_requete.shape
            scale = min(200 / w, 200 / h)
            new_w, new_h = int(w * scale), int(h * scale)
            img_display = cv2.resize(self.image_requete, (new_w, new_h))

            img_pil = Image.fromarray(img_display)
            img_tk = ImageTk.PhotoImage(img_pil)

            self.canvas_requete.delete("all")
            self.canvas_requete.create_image(100, 100, image=img_tk)
            self.canvas_requete.image = img_tk  # Garder une référence

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement : {e}")

    def lancer_recherche(self):
        """
        Lance la recherche d'images similaires
        """
        # Vérifications
        if len(self.moteur.base_de_donnees) == 0:
            messagebox.showwarning(
                "Attention", "Veuillez d'abord indexer un dossier d'images (ÉTAPE 1)"
            )
            return

        if self.image_requete is None:
            messagebox.showwarning(
                "Attention", "Veuillez d'abord charger une image de requête (ÉTAPE 2)"
            )
            return

        # Lancer la recherche
        resultats = self.moteur.rechercher_images_similaires(
            self.image_requete, top_k=self.nb_resultats.get()
        )

        # Afficher les résultats
        self.afficher_resultats(resultats)

    def afficher_resultats(self, resultats):
        """
        Affiche les résultats de la recherche dans la zone de texte

        Args:
            resultats (list): Liste des résultats de la recherche
        """
        self.zone_resultats.config(state=tk.NORMAL)
        self.zone_resultats.delete(1.0, tk.END)

        message = f"""
╔══════════════════════════════════════════════════════════════╗
║            RÉSULTATS DE LA RECHERCHE D'IMAGES                ║
╚══════════════════════════════════════════════════════════════╝

📂 Base de données : {len(self.moteur.base_de_donnees)} images indexées
🔍 Recherche terminée avec succès !

🏆 Top {len(resultats)} images les plus similaires :
"""

        for i, res in enumerate(resultats, 1):
            similarite_percent = res["similarite"] * 100

            # Emoji selon la similarité
            if res["similarite"] > 0.9:
                emoji = "🟢"
                niveau = "TRÈS SIMILAIRE"
            elif res["similarite"] > 0.7:
                emoji = "🟡"
                niveau = "SIMILAIRE"
            else:
                emoji = "🔴"
                niveau = "PEU SIMILAIRE"

            message += f"""
{i}. {emoji} {res['nom']}
   Similarité : {similarite_percent:.1f}% ({niveau})
   Distance   : {res['distance']:.2f}
   Chemin     : {res['chemin']}
"""

        message += "\n" + "=" * 62 + "\n"
        message += """
💡 Interprétation :
   • Similarité proche de 100% = Images très similaires
   • Distance faible = Images très similaires
"""

        self.zone_resultats.insert(tk.END, message)
        self.zone_resultats.config(state=tk.DISABLED)


# ============================================================================
# PROGRAMME PRINCIPAL
# ============================================================================
def main():
    """
    Lance l'application
    """
    root = tk.Tk()
    app = SearchEngineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 MOTEUR DE RECHERCHE D'IMAGES - DCT")
    print("=" * 60)
    print("\nLancement de l'interface graphique...\n")
    main()
