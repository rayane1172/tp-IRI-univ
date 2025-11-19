"""
Module : Moteur de Recherche d'Images avec la DCT
==================================================

Ce module contient toute la logique pour :
- Extraire les caractéristiques DCT des images
- Comparer deux images
- Rechercher des images similaires

Auteur : TP ISI
"""

import numpy as np
import cv2
from scipy.fftpack import dct
from pathlib import Path


# ============================================================================
# CLASSE 1 : Extraction des caractéristiques DCT
# ============================================================================
class ImageFeatureExtractor:
    """
    Classe simple pour extraire les caractéristiques d'une image
    
    Cette classe utilise la DCT (Discrete Cosine Transform) pour
    extraire les caractéristiques importantes d'une image.
    """
    
    def __init__(self, block_size=8):
        """
        Initialisation de l'extracteur
        
        Args:
            block_size (int): Taille des blocs pour la DCT (8x8 par défaut)
        """
        self.block_size = block_size
    
    def charger_image(self, chemin_image):
        """
        Charge une image en noir et blanc
        
        Args:
            chemin_image (str): Chemin vers l'image
            
        Returns:
            numpy.ndarray: Image en niveaux de gris, ou None si erreur
        """
        try:
            image = cv2.imread(str(chemin_image), cv2.IMREAD_GRAYSCALE)
            if image is not None:
                return image
            else:
                print(f"⚠️ Impossible de charger l'image : {chemin_image}")
                return None
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de {chemin_image}: {e}")
            return None
    
    def appliquer_dct(self, bloc):
        """
        Applique la DCT 2D sur un bloc 8x8
        
        Args:
            bloc (numpy.ndarray): Bloc d'image
            
        Returns:
            numpy.ndarray: Coefficients DCT du bloc
        """
        return dct(dct(bloc.T, norm="ortho").T, norm="ortho")
    
    def extraire_coefficients_zigzag(self, bloc_dct, nb_coefficients=64):
        """
        Extrait les coefficients importants en zigzag
        
        Le parcours en zigzag permet de récupérer les coefficients
        les plus importants (basses fréquences) en premier.
        
        Args:
            bloc_dct (numpy.ndarray): Bloc DCT
            nb_coefficients (int): Nombre de coefficients à extraire
            
        Returns:
            list: Liste des coefficients
        """
        rows, cols = bloc_dct.shape
        coefficients = []
        
        # Parcours en zigzag simplifié
        for i in range(rows):
            for j in range(cols):
                coefficients.append(bloc_dct[i][j])
                if len(coefficients) >= nb_coefficients:
                    return coefficients[:nb_coefficients]
        
        return coefficients
    
    def extraire_caracteristiques(self, image):
        """
        Extrait les caractéristiques DCT de toute l'image
        
        L'image est divisée en blocs, et on applique la DCT
        sur chaque bloc pour obtenir un vecteur de caractéristiques.
        
        Args:
            image (numpy.ndarray): Image en niveaux de gris
            
        Returns:
            numpy.ndarray: Vecteur de caractéristiques DCT
        """
        # Redimensionner l'image pour qu'elle soit divisible par block_size
        h, w = image.shape
        new_h = (h // self.block_size) * self.block_size
        new_w = (w // self.block_size) * self.block_size
        image_resized = cv2.resize(image, (new_w, new_h))
        
        caracteristiques = []
        
        # Parcourir l'image bloc par bloc
        for i in range(0, new_h, self.block_size):
            for j in range(0, new_w, self.block_size):
                # Extraire un bloc
                bloc = image_resized[i:i+self.block_size, j:j+self.block_size]
                
                # Appliquer la DCT
                bloc_dct = self.appliquer_dct(bloc)
                
                # Extraire les coefficients (16 par bloc au lieu de 64)
                coeffs = self.extraire_coefficients_zigzag(bloc_dct, 16)
                caracteristiques.extend(coeffs)
        
        return np.array(caracteristiques)


# ============================================================================
# CLASSE 2 : Comparaison de deux images
# ============================================================================
class ImageComparator:
    """
    Classe pour comparer deux images
    
    Cette classe fournit des méthodes pour calculer la similarité
    entre deux vecteurs de caractéristiques.
    """
    
    def calculer_distance_euclidienne(self, features1, features2):
        """
        Calcule la distance euclidienne entre deux vecteurs
        
        Plus la distance est petite, plus les images sont similaires.
        
        Args:
            features1 (numpy.ndarray): Premier vecteur de caractéristiques
            features2 (numpy.ndarray): Deuxième vecteur de caractéristiques
            
        Returns:
            float: Distance euclidienne
        """
        # S'assurer que les vecteurs ont la même taille
        min_len = min(len(features1), len(features2))
        f1 = features1[:min_len]
        f2 = features2[:min_len]
        
        # Formule : sqrt(sum((x1 - x2)^2))
        distance = np.sqrt(np.sum((f1 - f2) ** 2))
        return distance
    
    def calculer_similarite_cosinus(self, features1, features2):
        """
        Calcule la similarité cosinus entre deux vecteurs
        
        Plus la similarité est proche de 1, plus les images sont similaires.
        
        Args:
            features1 (numpy.ndarray): Premier vecteur de caractéristiques
            features2 (numpy.ndarray): Deuxième vecteur de caractéristiques
            
        Returns:
            float: Similarité cosinus (entre -1 et 1)
        """
        min_len = min(len(features1), len(features2))
        f1 = features1[:min_len]
        f2 = features2[:min_len]
        
        # Produit scalaire
        dot_product = np.dot(f1, f2)
        
        # Normes des vecteurs
        norm1 = np.linalg.norm(f1)
        norm2 = np.linalg.norm(f2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        # Formule : (A · B) / (||A|| * ||B||)
        similarite = dot_product / (norm1 * norm2)
        return similarite


# ============================================================================
# CLASSE 3 : Moteur de recherche d'images
# ============================================================================
class ImageSearchEngine:
    """
    Moteur de recherche d'images basé sur la DCT
    
    Cette classe permet de :
    - Indexer un dossier d'images
    - Rechercher les images les plus similaires à une image de requête
    """
    
    def __init__(self):
        """
        Initialisation du moteur de recherche
        """
        self.extracteur = ImageFeatureExtractor(block_size=8)
        self.comparateur = ImageComparator()
        self.base_de_donnees = {}  # Dictionnaire pour stocker les images
    
    def indexer_dossier(self, chemin_dossier):
        """
        Indexe toutes les images d'un dossier
        
        Pour chaque image du dossier :
        1. Charger l'image
        2. Extraire les caractéristiques DCT
        3. Stocker dans la base de données
        
        Args:
            chemin_dossier (str): Chemin vers le dossier d'images
            
        Returns:
            int: Nombre d'images indexées
        """
        print("📂 Indexation des images en cours...")
        
        extensions_images = ['.jpg', '.jpeg', '.png', '.bmp']
        self.base_de_donnees.clear()
        
        for fichier in Path(chemin_dossier).iterdir():
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
                        'chemin': str(fichier),
                        'features': features
                    }
                    
                except Exception as e:
                    print(f"⚠️ Erreur avec {fichier.name}: {e}")
        
        print(f"✅ {len(self.base_de_donnees)} images indexées\n")
        return len(self.base_de_donnees)
    
    def rechercher_images_similaires(self, image_requete, top_k=5):
        """
        Recherche les K images les plus similaires
        
        Pour chaque image de la base :
        1. Calculer la distance euclidienne
        2. Calculer la similarité cosinus
        3. Trier par similarité
        
        Args:
            image_requete (numpy.ndarray): Image de requête
            top_k (int): Nombre d'images similaires à retourner
            
        Returns:
            list: Liste des résultats (nom, chemin, distance, similarité)
        """
        if len(self.base_de_donnees) == 0:
            return []
        
        # Extraire les caractéristiques de l'image de requête
        features_requete = self.extracteur.extraire_caracteristiques(image_requete)
        
        resultats = []
        
        # Comparer avec toutes les images de la base
        for nom_image, donnees in self.base_de_donnees.items():
            features_db = donnees['features']
            
            # Calculer la distance
            distance = self.comparateur.calculer_distance_euclidienne(
                features_requete, features_db
            )
            
            # Calculer la similarité
            similarite = self.comparateur.calculer_similarite_cosinus(
                features_requete, features_db
            )
            
            resultats.append({
                'nom': nom_image,
                'chemin': donnees['chemin'],
                'distance': distance,
                'similarite': similarite
            })
        
        # Trier par similarité (du plus grand au plus petit)
        resultats_tries = sorted(resultats, key=lambda x: x['similarite'], reverse=True)
        
        return resultats_tries[:top_k]
