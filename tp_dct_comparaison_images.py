import numpy as np
import cv2
from scipy.fftpack import dct
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

#  Lecture image BGR
#  Conversion BGR → RGB



# Partitionnement 8×8 pixels
# Conversion RGB → YCbCr
# Séparation canaux Y, Cb, Cr
# DCT 2D sur chaque sous-bloc 8×8
# Parcours zigzag
#   Quantification (8 premiers coefficients normalisés)
#   Concaténation [Y, Cb, Cr] → Descripteur final

class ImageFeatureExtractor:

    def __init__(self, block_size=8):
        self.block_size = block_size

        # preé-calculer les indices zigzag une seule fois
        self.zigzag_indices = np.array(
            [
                (0, 0),
                (0, 1),
                (1, 0),
                (2, 0),
                (1, 1),
                (0, 2),
                (0, 3),
                (1, 2),
                (2, 1),
                (3, 0),
                (4, 0),
                (3, 1),
                (2, 2),
                (1, 3),
                (0, 4),
                (0, 5),
                (1, 4),
                (2, 3),
                (3, 2),
                (4, 1),
                (5, 0),
                (6, 0),
                (5, 1),
                (4, 2),
                (3, 3),
                (2, 4),
                (1, 5),
                (0, 6),
                (0, 7),
                (1, 6),
                (2, 5),
                (3, 4),
                (4, 3),
                (5, 2),
                (6, 1),
                (7, 0),
                (7, 1),
                (6, 2),
                (5, 3),
                (4, 4),
                (3, 5),
                (2, 6),
                (1, 7),
                (2, 7),
                (3, 6),
                (4, 5),
                (5, 4),
                (6, 3),
                (7, 2),
                (7, 3),
                (6, 4),
                (5, 5),
                (4, 6),
                (3, 7),
                (4, 7),
                (5, 6),
                (6, 5),
                (7, 4),
                (7, 5),
                (6, 6),
                (5, 7),
                (6, 7),
                (7, 6),
                (7, 7),
            ]
        )

    def charger_image(self, chemin_image):
        image = cv2.imread(str(chemin_image), cv2.IMREAD_COLOR)
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def appliquer_dct_2d(self, bloc):
        # applique la DCT 2D sur un bloc 8x8
        return dct(dct(bloc.T, norm="ortho").T, norm="ortho")

    def parcours_zigzag(self, bloc_dct):
        """
        parcours zigzag des coefficients DCT
        """
        return bloc_dct[self.zigzag_indices[:, 0], self.zigzag_indices[:, 1]]

    def quantifier_coefficients(self, coefficients, nb_coefficients=8):
        """
        quantification - normalisation
        """
        # Prendre les premiers coefficients (les plus importants)
        coeffs_reduits = coefficients[:nb_coefficients]

        # Normalisation (éviter division par zéro)
        norme = np.linalg.norm(coeffs_reduits)
        if norme > 1e-10:  # Éviter division par zéro
            coeffs_reduits = coeffs_reduits / norme

        return coeffs_reduits

    def extraire_caracteristiques(self, image):
        """
        extrait les caractéristiques DCT
        """
        """ partitionnement en blocs 8×8 pixels"""
        h, w, c = image.shape
        # Redimensionner pour que l'image soit divisible par 8
        new_h = (h // 8) * 8
        new_w = (w // 8) * 8

        if new_h != h or new_w != w:
            image_resized = cv2.resize(image, (new_w, new_h))
        else:
            image_resized = image

        """  conversion RGB → YCbCr"""
        image_ycbcr = cv2.cvtColor(image_resized, cv2.COLOR_RGB2YCrCb).astype(
            np.float32
        )

        """  séparation des canaux Y, Cb, Cr"""
        canal_Y = image_ycbcr[:, :, 0]
        canal_Cb = image_ycbcr[:, :, 1]
        canal_Cr = image_ycbcr[:, :, 2]

        #  nombre de blocs
        nb_blocs_h = new_h // 8
        nb_blocs_w = new_w // 8
        nb_blocs_total = nb_blocs_h * nb_blocs_w


        nb_coeffs = 8
        descripteur_Y = np.zeros(nb_blocs_total * nb_coeffs, dtype=np.float32)
        descripteur_Cb = np.zeros(nb_blocs_total * nb_coeffs, dtype=np.float32)
        descripteur_Cr = np.zeros(nb_blocs_total * nb_coeffs, dtype=np.float32)

        bloc_idx = 0

        # Parcourir l'image par blocs de 8×8
        for i in range(0, new_h, 8):
            for j in range(0, new_w, 8):
                # extraire le bloc 8×8 pour chaque canal (déjà en float32)
                bloc_Y = canal_Y[i : i + 8, j : j + 8]
                bloc_Cb = canal_Cb[i : i + 8, j : j + 8]
                bloc_Cr = canal_Cr[i : i + 8, j : j + 8]

                """ DCT 2D sur chaque bloc 8 × 8"""
                dct_Y = self.appliquer_dct_2d(bloc_Y)
                dct_Cb = self.appliquer_dct_2d(bloc_Cb)
                dct_Cr = self.appliquer_dct_2d(bloc_Cr)

                """  parcours zigzag"""
                coeffs_Y = self.parcours_zigzag(dct_Y)
                coeffs_Cb = self.parcours_zigzag(dct_Cb)
                coeffs_Cr = self.parcours_zigzag(dct_Cr)

                """ quantification"""
                coeffs_Y_quantifies = self.quantifier_coefficients(
                    coeffs_Y, nb_coefficients=nb_coeffs
                )
                coeffs_Cb_quantifies = self.quantifier_coefficients(
                    coeffs_Cb, nb_coefficients=nb_coeffs
                )
                coeffs_Cr_quantifies = self.quantifier_coefficients(
                    coeffs_Cr, nb_coefficients=nb_coeffs
                )

                # Stocker dans les tableaux pré-alloués
                start_idx = bloc_idx * nb_coeffs
                end_idx = start_idx + nb_coeffs
                descripteur_Y[start_idx:end_idx] = coeffs_Y_quantifies
                descripteur_Cb[start_idx:end_idx] = coeffs_Cb_quantifies
                descripteur_Cr[start_idx:end_idx] = coeffs_Cr_quantifies

                bloc_idx += 1

        """ Concaténation [Y, Cb, Cr] → Descripteur final"""
        descripteur_final = np.concatenate(
            [descripteur_Y, descripteur_Cb, descripteur_Cr]
        )
        return descripteur_final


class ImageComparator:

    def calculer_distance_euclidienne(self, features1, features2):
        # S'assurer que les vecteurs ont la même taille
        min_len = min(len(features1), len(features2))

        # Calcul vectorisé (beaucoup plus rapide)
        diff = features1[:min_len] - features2[:min_len]
        distance = np.sqrt(np.sum(diff * diff))

        return distance

    def calculer_similarite_cosinus(self, features1, features2):
        """
        Calcule la similarité entre deux vecteurs
        """
        min_len = min(len(features1), len(features2))
        f1 = features1[:min_len]
        f2 = features2[:min_len]

        # Produit scalaire et normes calculés en une seule fois
        dot_product = np.dot(f1, f2)
        norm_product = np.linalg.norm(f1) * np.linalg.norm(f2)

        if norm_product < 1e-10:
            return 0.0

        similarite = dot_product / norm_product
        return similarite


class ImageSearchEngine:

    def __init__(self):
        self.extracteur = ImageFeatureExtractor(block_size=8)
        self.comparateur = ImageComparator()
        self.base_de_donnees = {}  # Dictionnaire pour stocker les images

    def indexer_dossier(self, chemin_dossier):
        print("Indexation des images en cours...")

        extensions_images = {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
        }  # Set plus rapide que list
        self.base_de_donnees.clear()

        fichiers = list(Path(chemin_dossier).iterdir())
        total = len([f for f in fichiers if f.suffix.lower() in extensions_images])

        for idx, fichier in enumerate(fichiers, 1):
            if fichier.suffix.lower() in extensions_images:
                try:
                    # Charger l'image
                    image = self.extracteur.charger_image(fichier)
                    if image is None:
                        continue

                    # Extraire les caractéristiques
                    features = self.extracteur.extraire_caracteristiques(image)

                    # Stocker dans la base de données
                    self.base_de_donnees[fichier.name] = {
                        "chemin": str(fichier),
                        "features": features,
                    }

                    # Afficher la progression
                    if idx % 5 == 0 or idx == total:
                        print(
                            f"Progression: {len(self.base_de_donnees)}/{total} images indexées"
                        )

                except Exception as e:
                    print(f"Erreur avec {fichier.name}: {e}")

        print(f"\n✅ {len(self.base_de_donnees)} images indexées avec succès\n")
        return len(self.base_de_donnees)

    def rechercher_images_similaires(self, image_requete, top_k=5):
        if len(self.base_de_donnees) == 0:
            return []

        # Extraire les caractéristiques de l'image de requête
        features_requete = self.extracteur.extraire_caracteristiques(image_requete)

        # Pré-allouer les listes
        nb_images = len(self.base_de_donnees)
        resultats = []

        # Comparer avec toutes les images de la base
        for nom_image, donnees in self.base_de_donnees.items():
            features_db = donnees["features"]

            # Calculer la similarité (plus important que la distance)
            similarite = self.comparateur.calculer_similarite_cosinus(
                features_requete, features_db
            )

            resultats.append(
                {
                    "nom": nom_image,
                    "chemin": donnees["chemin"],
                    "similarite": similarite,
                }
            )

        # Trier par similarité (du plus grand au plus petit) - plus rapide avec key
        resultats.sort(key=lambda x: x["similarite"], reverse=True)

        return resultats


class SearchEngineGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Moteur de Recherche d'Images - DCT ")
        self.root.geometry("1000x700")

        # Créer le moteur de recherche
        self.moteur = ImageSearchEngine()

        # Variables
        self.image_requete = None
        self.dossier_images = None

        # Indexer automatiquement le dossier dataset
        self.indexer_dossier_automatique()

        # Créer l'interface
        self.creer_interface()

    def indexer_dossier_automatique(self):
        """
        Indexe automatiquement le dossier 'dataset' s'il existe
        """
        dossier_dataset = Path("dataset")
        if dossier_dataset.exists() and dossier_dataset.is_dir():
            self.dossier_images = str(dossier_dataset)
            nb_images = self.moteur.indexer_dossier(self.dossier_images)
            print(
                f"{nb_images} images indexées automatiquement depuis le dossier 'dataset'"
            )
        else:
            print("Le dossier 'dataset' n'existe pas")

    def creer_interface(self):
        """
        Crée l'interface graphique
        """
        # Style
        style = ttk.Style()
        style.theme_use("clam")

        # TITRE
        titre = ttk.Label(
            self.root,
            text="Moteur de Recherche d'Images DCT",
            font=("Arial", 20, "bold"),
        )
        titre.pack(pady=10)

        # FRAME PRINCIPALE POUR L'IMAGE ET LE BOUTON
        frame_principal = ttk.Frame(self.root)
        frame_principal.pack(fill=tk.X, padx=10, pady=5)

        # GAUCHE : Charger l'image de requête (taille réduite)
        frame_image = ttk.LabelFrame(
            frame_principal, text="Image de requête", padding=10
        )
        frame_image.pack(side=tk.LEFT, padx=5)

        # Canvas pour afficher l'image de requête (150x150 au lieu de 200x200)
        self.canvas_requete = tk.Canvas(
            frame_image, width=150, height=150, bg="lightgray"
        )
        self.canvas_requete.pack(padx=10, pady=10)

        ttk.Button(
            frame_image, text="Charger l'image", command=self.charger_image_requete
        ).pack(pady=5)

        # DROITE : Bouton de recherche
        frame_recherche = ttk.Frame(frame_principal)
        frame_recherche.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)

        ttk.Button(
            frame_recherche,
            text="RECHERCHER",
            command=self.lancer_recherche,
            style="Accent.TButton",
        ).pack(pady=80)

        # RÉSULTATS - Frame principal avec scrollbar
        frame_resultats = ttk.LabelFrame(
            self.root,
            text="Résultats de la recherche (classés par similarité DCT)",
            padding=10,
        )
        frame_resultats.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas avec scrollbar pour les résultats
        self.canvas_resultats = tk.Canvas(frame_resultats, bg="white")
        scrollbar_v = ttk.Scrollbar(
            frame_resultats, orient="vertical", command=self.canvas_resultats.yview
        )
        scrollbar_h = ttk.Scrollbar(
            frame_resultats, orient="horizontal", command=self.canvas_resultats.xview
        )

        self.frame_images = ttk.Frame(self.canvas_resultats)

        self.canvas_resultats.create_window(
            (0, 0), window=self.frame_images, anchor="nw"
        )
        self.canvas_resultats.configure(
            yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set
        )

        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_resultats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind pour mettre à jour la scrollregion
        self.frame_images.bind(
            "<Configure>",
            lambda e: self.canvas_resultats.configure(
                scrollregion=self.canvas_resultats.bbox("all")
            ),
        )

    def charger_image_requete(self):
        """
        Charge l'image de requête en couleur
        """
        fichier = filedialog.askopenfilename(
            title="Sélectionner l'image de requête",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")],
        )

        if not fichier:
            return

        try:
            # Charger l'image en couleur
            self.image_requete = cv2.imread(fichier, cv2.IMREAD_COLOR)
            self.image_requete = cv2.cvtColor(self.image_requete, cv2.COLOR_BGR2RGB)

            # Afficher sur le canvas (ajusté pour 150x150)
            h, w, c = self.image_requete.shape
            scale = min(150 / w, 150 / h)
            new_w, new_h = int(w * scale), int(h * scale)
            img_display = cv2.resize(self.image_requete, (new_w, new_h))

            img_pil = Image.fromarray(img_display)
            img_tk = ImageTk.PhotoImage(img_pil)

            self.canvas_requete.delete("all")
            self.canvas_requete.create_image(75, 75, image=img_tk)
            self.canvas_requete.image = img_tk

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

    def lancer_recherche(self):
        """
        Lance la recherche d'images similaires
        """
        if self.image_requete is None:
            messagebox.showerror("Erreur", "Veuillez charger une image de requête.")
            return

        if not self.moteur.base_de_donnees:
            messagebox.showerror(
                "Erreur",
                "Aucune image indexée. Le dossier 'dataset' est vide ou n'existe pas.",
            )
            return

        # Afficher toutes les images similaires
        resultats = self.moteur.rechercher_images_similaires(
            self.image_requete, top_k=len(self.moteur.base_de_donnees)
        )
        self.afficher_resultats(resultats)

    def afficher_resultats(self, resultats):
        """
        Affiche les résultats de la recherche en couleur
        """
        for widget in self.frame_images.winfo_children():
            widget.destroy()

        for i, res in enumerate(resultats):
            try:
                # Charger en couleur
                img = cv2.imread(res["chemin"], cv2.IMREAD_COLOR)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img)
                # Augmentation de la taille des résultats (200x200 au lieu de 150x150)
                img_pil.thumbnail((200, 200))
                img_tk = ImageTk.PhotoImage(img_pil)

                frame = ttk.Frame(self.frame_images, padding=5)
                frame.grid(row=i // 3, column=i % 3, padx=10, pady=10)

                label_img = ttk.Label(frame, image=img_tk)
                label_img.image = img_tk
                label_img.pack()

                label_text = ttk.Label(
                    frame,
                    # text=f"{res['nom']}\nSim: {res['similarite']:.2f}",
                    text="",
                    font=("Arial", 10),
                )
                label_text.pack()

            except Exception as e:
                print(f"Erreur lors de l'affichage de {res['nom']}: {e}")


def main():
    root = tk.Tk()
    app = SearchEngineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    print("demarage....\n")
    main()
