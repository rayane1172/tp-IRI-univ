from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import urllib.parse

app = Flask(__name__)
CORS(app)

# Cache global pour stocker tous les mots trouvés dans les sites
all_words_cache = set()


def levenshtein_distance(s1, s2):
    """
    Calcule la distance de Levenshtein entre deux chaînes.
    Plus la distance est petite, plus les mots sont similaires.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Coût: 0 si les caractères sont identiques, 1 sinon
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def find_similar_words(query_word, word_list, max_distance=2, max_suggestions=10):
    query_lower = query_word.lower()
    suggestions = []

    for word in word_list:
        word_lower = word.lower()
        # Ignorer les mots trop courts ou identiques
        if len(word_lower) < 3 or word_lower == query_lower:
            continue

        distance = levenshtein_distance(query_lower, word_lower)
        print(f"Comparing '{query_lower}' with '{word_lower}': distance {distance}")

        #! Ajuster la distance max selon la longueur du mot
        adjusted_max = max_distance if len(query_lower) > 4 else 1

        if distance <= adjusted_max:
            suggestions.append((word, distance))

    #! Trier par distance (les plus proches en premier)
    suggestions.sort(key=lambda x: x[1])

    #! Retourner uniquement les mots (sans les distances)
    return [word for word, _ in suggestions[:max_suggestions]]

#! site words
def extract_words_from_site(url):
    words = set()
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        #! Mots du titre
        title = soup.find("title")
        if title:
            words.update(title.get_text().lower().split())

        #! Mots des alt des images
        for img in soup.find_all("img"):
            alt = img.get("alt", "")
            if alt:
                words.update(alt.lower().split())

        #! Mots des paragraphes
        for p in soup.find_all("p"):
            words.update(p.get_text().lower().split())

        #! Mots des titres h1, h2, h3
        for tag in soup.find_all(["h1", "h2", "h3"]):
            words.update(tag.get_text().lower().split())

    except Exception:
        pass

    #! Filtrer les mots trop courts et nettoyer
    cleaned_words = set()
    for word in words:
        # Nettoyer la ponctuation
        clean = "".join(c for c in word if c.isalnum())
        if len(clean) >= 3:
            cleaned_words.add(clean)

    return cleaned_words


def build_words_cache():
    global all_words_cache
    all_words_cache = set()
    for site in SITES:
        all_words_cache.update(extract_words_from_site(site["url"]))
    print(f"📚 Cache de mots construit: {len(all_words_cache)} mots uniques")


SITES = [
    {
        "id": 1,
        "url": "http://localhost:8000/site1/index.html",
        "name": "Chats",
        "emoji": "🐱",
    },
    {
        "id": 2,
        "url": "http://localhost:8000/site2/index.html",
        "name": "Voitures",
        "emoji": "🏎️",
    },
    {
        "id": 3,
        "url": "http://localhost:8000/site3/index.html",
        "name": "Nature",
        "emoji": "🌿",
    },
    {
        "id": 4,
        "url": "http://localhost:8000/site4/index.html",
        "name": "Cuisine",
        "emoji": "🍽️",
    },
    {
        "id": 5,
        "url": "http://localhost:8000/site5/index.html",
        "name": "Technologie",
        "emoji": "💻",
    },
    {
        "id": 6,
        "url": "http://localhost:8000/site6/index.html",
        "name": "Animaux Sauvages",
        "emoji": "🦁",
    },
    {
        "id": 7,
        "url": "http://localhost:8000/site7/index.html",
        "name": "Architecture",
        "emoji": "🏛️",
    },
    {
        "id": 8,
        "url": "http://localhost:8000/site8/index.html",
        "name": "Sports Extrêmes",
        "emoji": "🏄",
    },
    {
        "id": 9,
        "url": "http://localhost:8000/site9/index.html",
        "name": "Espace",
        "emoji": "🚀",
    },
    {
        "id": 10,
        "url": "http://localhost:8000/site10/index.html",
        "name": "Musique",
        "emoji": "🎵",
    },
]


def check_words_in_text(text, words, mode="OR"):
    if not text:
        return False, []

    text_lower = text.lower()
    found_words = [word for word in words if word.lower() in text_lower]

    if mode == "AND":
        # Tous les mots doivent être trouvés
        return len(found_words) == len(words), found_words
    else:
        # Au moins un mot doit être trouvé (OR)
        return len(found_words) > 0, found_words


def search_in_site(url, query_words, mode="OR"):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        found_methods = []
        all_matched_words = set()

        #! Récupérer le titre complet de la page
        page_title = ""
        title_tag = soup.find("title")
        if title_tag:
            page_title = title_tag.get_text().strip()

        #!  Recherche dans le titre
        if page_title:
            found, matched = check_words_in_text(page_title, query_words, mode)
            if found:
                found_methods.append("title")
                all_matched_words.update(matched)

        #! Recherche dans les images (src et alt)
        images = soup.find_all("img")
        for img in images:
            src = img.get("src", "")
            alt = img.get("alt", "")

            #! Vérifier dans src
            found_src, matched_src = check_words_in_text(src, query_words, mode)
            if found_src and "url" not in found_methods:
                found_methods.append("url")
                all_matched_words.update(matched_src)

            #! Vérifier dans alt
            found_alt, matched_alt = check_words_in_text(alt, query_words, mode)
            if found_alt and "alt" not in found_methods:
                found_methods.append("alt")
                all_matched_words.update(matched_alt)

        #! Recherche dans les paragraphes
        paragraphs = soup.find_all("p")
        for p in paragraphs:
            p_text = p.get_text()
            found, matched = check_words_in_text(p_text, query_words, mode)
            if found:
                if "text" not in found_methods:
                    found_methods.append("text")
                all_matched_words.update(matched)
                break

        #!  Si trouvé dans au moins une méthode, récupérer TOUTES les images
        if found_methods:
            all_images = []
            for img in images:
                src = img.get("src", "")
                alt = img.get("alt", "Image")

                # Convertir URL relative en absolue
                if src and not src.startswith(("http://", "https://")):
                    src = urllib.parse.urljoin(url, src)

                if src:
                    all_images.append(
                        {"src": src, "alt": alt, "methods": found_methods}
                    )

            return {
                "found": True,
                "methods": found_methods,
                "matched_words": list(all_matched_words),
                "images": all_images,
                "page_title": page_title,
            }

        return {
            "found": False,
            "methods": [],
            "matched_words": [],
            "images": [],
            "page_title": "",
        }

    except Exception as e:
        return {
            "found": False,
            "methods": [],
            "matched_words": [],
            "images": [],
            "page_title": "",
            "error": str(e),
        }


@app.route("/api/sites", methods=["GET"])
def get_sites():
    return jsonify(SITES)


@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    mode = request.args.get("mode", "OR").upper()

    # Valider le mode
    if mode not in ["OR", "AND"]:
        mode = "OR"

    if not query:
        return jsonify(
            {"error": "Veuillez entrer un terme de recherche", "results": []}
        )

    # Séparer les mots de la requête
    query_words = [word.strip() for word in query.split() if word.strip()]

    if not query_words:
        return jsonify(
            {"error": "Veuillez entrer un terme de recherche valide", "results": []}
        )

    results = []
    methods_count = {"title": 0, "url": 0, "alt": 0, "text": 0}

    for site in SITES:
        #! Rechercher dans chaque site
        result = search_in_site(site["url"], query_words, mode)

        if result["found"]:
            results.append(
                {
                    "site_id": site["id"],
                    "site_name": (
                        result["page_title"] if result["page_title"] else site["name"]
                    ),
                    "site_emoji": site["emoji"],
                    "site_url": site["url"],
                    "methods": result["methods"],
                    "matched_words": result["matched_words"],
                    "images": result["images"],
                }
            )

            # Compter les méthodes utilisées
            for method in result["methods"]:
                if method in methods_count:
                    methods_count[method] += 1

    # Si aucun résultat, chercher des suggestions avec Levenshtein
    suggestions = []
    if not results:
        # Construire le cache si nécessaire
        if not all_words_cache:
            build_words_cache()

        # Trouver des mots similaires pour chaque mot de la requête
        for word in query_words:
            similar = find_similar_words(word, all_words_cache)
            for s in similar:
                if s not in suggestions:
                    suggestions.append(s)

        # Limiter à 8 suggestions max
        suggestions = suggestions[:8]

    return jsonify(
        {
            "query": query,
            "query_words": query_words,
            "search_mode": mode,
            "total_sites": len(results),
            "total_images": sum(len(r["images"]) for r in results),
            "methods_count": methods_count,
            "results": results,
            "suggestions": suggestions,
        }
    )


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {"status": "ok", "message": "API du moteur de recherche opérationnelle"}
    )


if __name__ == "__main__":
    # print("=" * 60)
    # print("🚀 API Backend - Moteur de Recherche d'Images")
    # print("=" * 60)
    # print("📍 Endpoints disponibles:")
    # print("   GET /api/health  - Vérifier le status de l'API")
    # print("   GET /api/sites   - Liste des sites")
    # print("   GET /api/search?q=query&mode=OR - Rechercher (mode OR/AND)")
    # print("")
    # print("📝 Exemples:")
    # print("   /api/search?q=chat             - Recherche simple")
    # print("   /api/search?q=chat noir&mode=OR  - Au moins un mot")
    # print("   /api/search?q=chat noir&mode=AND - Tous les mots")
    # print("=" * 60)
    app.run(debug=True, port=5000)
