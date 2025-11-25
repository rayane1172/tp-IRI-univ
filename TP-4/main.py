import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
from pathlib import Path


class ImageSearchEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("Moteur de Recherche d'Images - Moyenne & Écart-type Local")
        self.root.geometry("1000x700")

        # Variables
        # Utiliser automatiquement le dossier "images" du projet
        self.image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        self.query_image_path = ""
        self.database_descriptors = {}  # {chemin: descripteur}
        self.block_size = 8  # Taille du bloc N×N

        self.setup_ui()

        # Indexer automatiquement les images au démarrage
        self.index_images()

    def setup_ui(self):
        # Frame supérieure - Contrôles
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(fill=tk.X)

        # Bouton pour sélectionner l'image requête
        tk.Button(
            control_frame,
            text="🔍 Sélectionner Image Requête",
            command=self.select_query_image,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10)

        # Bouton pour lancer la recherche
        tk.Button(
            control_frame,
            text="🚀 Rechercher",
            command=self.search_similar_images,
            bg="#FF5722",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10)

        # Bouton pour réindexer les images
        tk.Button(
            control_frame,
            text="🔄 Réindexer",
            command=self.index_images,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10)

        # Label pour afficher le dossier utilisé
        self.folder_label = tk.Label(
            self.root, text=f"Dossier: {self.image_folder}", font=("Arial", 9)
        )
        self.folder_label.pack()

        # Frame pour l'image requête
        query_frame = tk.LabelFrame(
            self.root, text="Image Requête", font=("Arial", 11, "bold"), pady=5
        )
        query_frame.pack(fill=tk.X, padx=10, pady=5)

        self.query_image_label = tk.Label(query_frame, text="Aucune image sélectionnée")
        self.query_image_label.pack()

        # Frame pour les résultats
        results_frame = tk.LabelFrame(
            self.root,
            text="Résultats (Images Similaires)",
            font=("Arial", 11, "bold"),
            pady=5,
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas avec scrollbar pour les résultats
        self.canvas = tk.Canvas(results_frame)
        scrollbar = tk.Scrollbar(
            results_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def select_query_image(self):

        filetypes = [("Images", "*.jpg *.jpeg *.png *.bmp *.gif")]
        filepath = filedialog.askopenfilename(
            title="Sélectionner l'image requête", filetypes=filetypes
        )
        if filepath:
            self.query_image_path = filepath
            self.display_query_image(filepath)

    def display_query_image(self, filepath):

        img = Image.open(filepath)
        img.thumbnail((150, 150))
        photo = ImageTk.PhotoImage(img)
        self.query_image_label.config(image=photo, text="")
        self.query_image_label.image = photo

    def convert_to_grayscale(self, image_path):

        img = Image.open(image_path).convert("L")  # 'L' = niveaux de gris
        return np.array(img)

    def compute_local_descriptor(self, image_array):
        """
        calculer le descripteur de texture basé sur la moyenne et l'ecart type local

        Étapes:
        1 Diviser l'image en blocs N×N
        2 Pour chaque bloc, calculer la moyenne (μ)
        3 Pour chaque bloc, calculer l'écart-type (σ)
        4 Concaténer tous les (μ, σ) pour former le descripteur
        """
        N = self.block_size
        height, width = image_array.shape

        # Redimensionner pour avoir des blocs complets
        new_height = (height // N) * N
        new_width = (width // N) * N
        image_array = image_array[:new_height, :new_width]

        means = []
        stds = []

        # Parcourir l'image bloc par bloc
        for i in range(0, new_height, N):
            for j in range(0, new_width, N):
                # Extraire le bloc
                block = image_array[i : i + N, j : j + N]

                # 2- Calculer la moyenne locale (μ)
                mu = np.mean(block)

                # 3- Calculer l'écart-type local (σ)
                sigma = np.std(block)

                means.append(mu)
                stds.append(sigma)

        # 4- Construire le descripteur
        #  les statistiques globales des moyennes et écarts-types
        descriptor = np.array(
            [
                np.mean(means),  # Moyenne des moyennes
                np.std(means),  # Écart-type des moyennes
                np.mean(stds),  # Moyenne des écarts-types
                np.std(stds),  # Écart-type des écarts-types
            ]
        )

        return descriptor

    def index_images(self):
        if not os.path.exists(self.image_folder):
            messagebox.showerror("Erreur", f"Le dossier '{self.image_folder}' n'existe pas!")
            return

        self.database_descriptors = {}
        extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]

        for filename in os.listdir(self.image_folder):
            filepath = os.path.join(self.image_folder, filename)
            if os.path.isfile(filepath) and Path(filename).suffix.lower() in extensions:
                try:
                    # Convertir en niveaux de gris
                    gray_image = self.convert_to_grayscale(filepath)
                    # Calculer le descripteur
                    descriptor = self.compute_local_descriptor(gray_image)
                    self.database_descriptors[filepath] = descriptor
                except Exception as e:
                    print(f"Erreur avec {filename}: {e}")

        messagebox.showinfo(
            "Indexation", f"{len(self.database_descriptors)} images indexées!"
        )

    def euclidean_distance(self, desc1, desc2):
        """Calculer la distance euclidienne entre deux descripteurs"""
        return np.sqrt(np.sum((desc1 - desc2) ** 2))

    def search_similar_images(self):
        """Rechercher les images similaires à l'image requête"""
        if not self.query_image_path:
            messagebox.showwarning(
                "Attention", "Veuillez sélectionner une image requête!"
            )
            return

        if not self.database_descriptors:
            messagebox.showwarning(
                "Attention", "Aucune image indexée dans le dossier!"
            )
            return

        # Calculer le descripteur de l'image requête
        query_gray = self.convert_to_grayscale(self.query_image_path)
        query_descriptor = self.compute_local_descriptor(query_gray)

        # Calculer les distances avec toutes les images de la base
        distances = []
        for filepath, descriptor in self.database_descriptors.items():
            dist = self.euclidean_distance(query_descriptor, descriptor)
            distances.append((filepath, dist))

        # Trier par distance (les plus similaires en premier)
        distances.sort(key=lambda x: x[1])

        # Afficher les résultats
        self.display_results(distances[:10])  # Top 10 résultats

    def display_results(self, results):
        # Effacer les anciens résultats
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Afficher les nouveaux résultats
        row = 0
        col = 0
        for filepath, distance in results:
            frame = tk.Frame(self.scrollable_frame, padx=5, pady=5)
            frame.grid(row=row, column=col, padx=5, pady=5)

            try:
                img = Image.open(filepath)
                img.thumbnail((120, 120))
                photo = ImageTk.PhotoImage(img)

                img_label = tk.Label(frame, image=photo)
                img_label.image = photo
                img_label.pack()

                # Nom du fichier et distance
                name = os.path.basename(filepath)
                info_label = tk.Label(
                    frame,
                    text=f"{name[:15]}...\nDist: {distance:.2f}",
                    font=("Arial", 8),
                )
                info_label.pack()
            except Exception as e:
                print(f"Erreur affichage {filepath}: {e}")

            col += 1
            if col >= 5:  # 5 images par ligne
                col = 0
                row += 1


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSearchEngine(root)
    root.mainloop()
