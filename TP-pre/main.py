import pywt
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.widgets import Button
from pathlib import Path

class TextureSearchEngine:
    def __init__(self, dataset_folder='dataset'):
        self.dataset_folder = dataset_folder
        self.image_paths = []
        self.features_db = []
        self.load_dataset()
        
    def load_dataset(self):
        """Charger toutes les images du dossier dataset"""
        if not os.path.exists(self.dataset_folder):
            print(f"Le dossier {self.dataset_folder} n'existe pas!")
            return
            
        for filename in os.listdir(self.dataset_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                filepath = os.path.join(self.dataset_folder, filename)
                self.image_paths.append(filepath)
        
        print(f"✓ {len(self.image_paths)} images chargées depuis {self.dataset_folder}")
        
    def extract_texture_features(self, image_path):
        """Extraire les caractéristiques de texture avec wavedec2"""
        # Charger l'image en niveaux de gris
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return None
        
        # Redimensionner pour uniformiser
        image = cv2.resize(image, (256, 256))
        
        # Décomposition en ondelettes à 3 niveaux
        coeffs = pywt.wavedec2(image, 'haar', level=3)
        
        # Extraire les statistiques de chaque sous-bande
        features = []
        
        # Approximation (LL)
        cA = coeffs[0]
        features.extend([
            np.mean(cA),
            np.std(cA),
            np.median(cA)
        ])
        
        # Détails (LH, HL, HH) pour chaque niveau
        for (cH, cV, cD) in coeffs[1:]:
            for coeff in [cH, cV, cD]:
                features.extend([
                    np.mean(np.abs(coeff)),
                    np.std(coeff),
                    np.max(np.abs(coeff))
                ])
        
        return np.array(features)
    
    def build_features_database(self):
        """Construire la base de données de caractéristiques"""
        print("Construction de la base de données de caractéristiques...")
        self.features_db = []
        
        for i, img_path in enumerate(self.image_paths):
            features = self.extract_texture_features(img_path)
            if features is not None:
                self.features_db.append(features)
            print(f"  Traitement: {i+1}/{len(self.image_paths)}", end='\r')
        
        self.features_db = np.array(self.features_db)
        print(f"\n✓ Base de données construite avec {len(self.features_db)} images")
    
    def calculate_similarity(self, features1, features2):
        """Calculer la similarité entre deux vecteurs de caractéristiques"""
        # Distance euclidienne normalisée
        distance = np.linalg.norm(features1 - features2)
        # Convertir en similarité (0-1, 1 = identique)
        similarity = 1 / (1 + distance)
        return similarity
    
    def search(self, query_image_path, top_k=5):
        """Rechercher les images les plus similaires"""
        # Extraire les caractéristiques de l'image requête
        query_features = self.extract_texture_features(query_image_path)
        
        if query_features is None:
            print("Erreur lors du chargement de l'image requête")
            return []
        
        # Calculer les similarités
        similarities = []
        for i, db_features in enumerate(self.features_db):
            sim = self.calculate_similarity(query_features, db_features)
            similarities.append((self.image_paths[i], sim))
        
        # Trier par similarité décroissante
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def visualize_search_results(self, query_image_path, top_k=6):
        """Visualiser les résultats de recherche"""
        results = self.search(query_image_path, top_k)
        
        # Créer la figure
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle('Moteur de Recherche d\'Images par Texture (Wavelet Decomposition)', 
                     fontsize=16, fontweight='bold')
        
        # Image requête avec sa décomposition
        query_img = cv2.imread(query_image_path, cv2.IMREAD_GRAYSCALE)
        query_img_resized = cv2.resize(query_img, (256, 256))
        
        # Afficher l'image requête
        ax1 = plt.subplot(3, 4, 1)
        ax1.imshow(query_img_resized, cmap='gray')
        ax1.set_title('IMAGE REQUÊTE', fontweight='bold', color='red', fontsize=12)
        ax1.axis('off')
        
        # Décomposition de l'image requête
        coeffs_query = pywt.wavedec2(query_img_resized, 'haar', level=3)
        dywtarray_query, _ = pywt.coeffs_to_array(coeffs_query)
        norm_query = (dywtarray_query - np.min(dywtarray_query)) / (np.max(dywtarray_query) - np.min(dywtarray_query) + 1e-9)
        
        ax2 = plt.subplot(3, 4, 2)
        ax2.imshow(norm_query, cmap='gray')
        ax2.set_title('Décomposition Wavelet', fontsize=10)
        ax2.axis('off')
        
        # Afficher les résultats
        for i, (img_path, similarity) in enumerate(results):
            # Image résultat
            result_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            result_img = cv2.resize(result_img, (256, 256))
            
            ax = plt.subplot(3, 4, i + 5)
            ax.imshow(result_img, cmap='gray')
            
            filename = os.path.basename(img_path)
            color = 'green' if i == 0 else 'blue'
            ax.set_title(f'#{i+1}: {filename}\nSimilarité: {similarity:.3f}', 
                        fontsize=9, color=color, fontweight='bold' if i == 0 else 'normal')
            ax.axis('off')
            
            # Bordure pour le résultat le plus similaire
            if i == 0:
                for spine in ax.spines.values():
                    spine.set_edgecolor('green')
                    spine.set_linewidth(3)
        
        plt.tight_layout()
        plt.show()
    
    def interactive_compare(self):
        """Interface interactive pour comparer deux images"""
        if len(self.image_paths) < 2:
            print("Pas assez d'images dans le dataset")
            return
        
        self.current_idx1 = 0
        self.current_idx2 = 1
        
        fig = plt.figure(figsize=(16, 8))
        fig.suptitle('Comparaison de Textures - Cliquez sur les boutons pour changer d\'image', 
                     fontsize=14, fontweight='bold')
        
        # Créer les axes pour les images et leurs décompositions
        self.ax1 = plt.subplot(2, 4, 1)
        self.ax2 = plt.subplot(2, 4, 2)
        self.ax3 = plt.subplot(2, 4, 5)
        self.ax4 = plt.subplot(2, 4, 6)
        
        # Axes pour les statistiques
        self.ax_stats = plt.subplot(1, 4, 4)
        
        # Boutons de navigation
        ax_prev1 = plt.axes([0.15, 0.02, 0.1, 0.04])
        ax_next1 = plt.axes([0.26, 0.02, 0.1, 0.04])
        ax_prev2 = plt.axes([0.55, 0.02, 0.1, 0.04])
        ax_next2 = plt.axes([0.66, 0.02, 0.1, 0.04])
        
        self.btn_prev1 = Button(ax_prev1, '← Image 1')
        self.btn_next1 = Button(ax_next1, 'Image 1 →')
        self.btn_prev2 = Button(ax_prev2, '← Image 2')
        self.btn_next2 = Button(ax_next2, 'Image 2 →')
        
        self.btn_prev1.on_clicked(lambda event: self.change_image(0, -1))
        self.btn_next1.on_clicked(lambda event: self.change_image(0, 1))
        self.btn_prev2.on_clicked(lambda event: self.change_image(1, -1))
        self.btn_next2.on_clicked(lambda event: self.change_image(1, 1))
        
        self.fig = fig
        self.update_comparison()
        plt.show()
    
    def change_image(self, which, direction):
        """Changer l'image affichée"""
        if which == 0:
            self.current_idx1 = (self.current_idx1 + direction) % len(self.image_paths)
        else:
            self.current_idx2 = (self.current_idx2 + direction) % len(self.image_paths)
        self.update_comparison()
    
    def update_comparison(self):
        """Mettre à jour l'affichage de comparaison"""
        # Charger et afficher les images
        img1_path = self.image_paths[self.current_idx1]
        img2_path = self.image_paths[self.current_idx2]
        
        img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
        
        img1 = cv2.resize(img1, (256, 256))
        img2 = cv2.resize(img2, (256, 256))
        
        # Décompositions
        coeffs1 = pywt.wavedec2(img1, 'haar', level=3)
        coeffs2 = pywt.wavedec2(img2, 'haar', level=3)
        
        dywtarray1, _ = pywt.coeffs_to_array(coeffs1)
        dywtarray2, _ = pywt.coeffs_to_array(coeffs2)
        
        norm1 = (dywtarray1 - np.min(dywtarray1)) / (np.max(dywtarray1) - np.min(dywtarray1) + 1e-9)
        norm2 = (dywtarray2 - np.min(dywtarray2)) / (np.max(dywtarray2) - np.min(dywtarray2) + 1e-9)
        
        # Afficher
        self.ax1.clear()
        self.ax1.imshow(img1, cmap='gray')
        self.ax1.set_title(f'Image 1: {os.path.basename(img1_path)}', fontweight='bold')
        self.ax1.axis('off')
        
        self.ax2.clear()
        self.ax2.imshow(norm1, cmap='gray')
        self.ax2.set_title('Décomposition Wavelet 1')
        self.ax2.axis('off')
        
        self.ax3.clear()
        self.ax3.imshow(img2, cmap='gray')
        self.ax3.set_title(f'Image 2: {os.path.basename(img2_path)}', fontweight='bold')
        self.ax3.axis('off')
        
        self.ax4.clear()
        self.ax4.imshow(norm2, cmap='gray')
        self.ax4.set_title('Décomposition Wavelet 2')
        self.ax4.axis('off')
        
        # Calculer la similarité
        features1 = self.extract_texture_features(img1_path)
        features2 = self.extract_texture_features(img2_path)
        similarity = self.calculate_similarity(features1, features2)
        
        # Afficher les statistiques
        self.ax_stats.clear()
        self.ax_stats.axis('off')
        stats_text = f"""
STATISTIQUES DE COMPARAISON

Similarité de texture:
{similarity:.4f} ({similarity*100:.1f}%)

{"=" * 25}

Image 1:
• Moyenne: {np.mean(img1):.2f}
• Écart-type: {np.std(img1):.2f}
• Énergie: {np.sum(img1**2):.0f}

Image 2:
• Moyenne: {np.mean(img2):.2f}
• Écart-type: {np.std(img2):.2f}
• Énergie: {np.sum(img2**2):.0f}
        """
        
        color = 'green' if similarity > 0.7 else 'orange' if similarity > 0.5 else 'red'
        self.ax_stats.text(0.1, 0.5, stats_text, fontsize=10, verticalalignment='center',
                          family='monospace', bbox=dict(boxstyle='round', facecolor=color, alpha=0.2))
        
        self.fig.canvas.draw_idle()


# Menu principal
def main():
    print("=" * 60)
    print("MOTEUR DE RECHERCHE D'IMAGES PAR TEXTURE")
    print("Utilisant la décomposition en ondelettes (wavedec2)")
    print("=" * 60)
    
    engine = TextureSearchEngine('dataset')
    
    if len(engine.image_paths) == 0:
        print("Aucune image trouvée dans le dossier dataset!")
        return
    
    print("\nConstruction de la base de données...")
    engine.build_features_database()
    
    while True:
        print("\n" + "=" * 60)
        print("MENU:")
        print("1. Rechercher des images similaires")
        print("2. Comparer deux images (interface interactive)")
        print("3. Quitter")
        print("=" * 60)
        
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == '1':
            print("\nImages disponibles:")
            for i, path in enumerate(engine.image_paths):
                print(f"  {i+1}. {os.path.basename(path)}")
            
            try:
                idx = int(input(f"\nChoisissez une image (1-{len(engine.image_paths)}): ")) - 1
                if 0 <= idx < len(engine.image_paths):
                    top_k = int(input("Nombre de résultats à afficher (défaut: 6): ") or "6")
                    engine.visualize_search_results(engine.image_paths[idx], top_k)
                else:
                    print("Index invalide!")
            except ValueError:
                print("Entrée invalide!")
        
        elif choice == '2':
            engine.interactive_compare()
        
        elif choice == '3':
            print("\nAu revoir!")
            break
        
        else:
            print("Choix invalide!")


if __name__ == '__main__':
    main()



