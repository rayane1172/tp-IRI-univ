"""
Serveur local pour tester les 10 sites de test
Lance un serveur HTTP sur le port 8000
"""

import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        """Affiche les logs de manière simplifiée"""
        # Afficher seulement les requêtes réussies
        print(f"📄 {args[0]}")

    def handle(self):
        """Gère les requêtes en ignorant les erreurs de connexion"""
        try:
            super().handle()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # Ignorer silencieusement les connexions fermées par le client
            pass


if __name__ == "__main__":
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print("=" * 60)
        print(f"🌐 Serveur de test lancé sur http://localhost:{PORT}")
        print("=" * 60)
        print("\n📂 10 Sites disponibles:")
        print(f"   1. http://localhost:{PORT}/site1/index.html  - 🐱 Chats")
        print(f"   2. http://localhost:{PORT}/site2/index.html  - 🏎️ Voitures")
        print(f"   3. http://localhost:{PORT}/site3/index.html  - 🌿 Nature")
        print(f"   4. http://localhost:{PORT}/site4/index.html  - 🍽️ Cuisine")
        print(f"   5. http://localhost:{PORT}/site5/index.html  - 💻 Technologie")
        print(f"   6. http://localhost:{PORT}/site6/index.html  - 🦁 Animaux Sauvages")
        print(f"   7. http://localhost:{PORT}/site7/index.html  - 🏛️ Architecture")
        print(f"   8. http://localhost:{PORT}/site8/index.html  - 🏄 Sports Extrêmes")
        print(f"   9. http://localhost:{PORT}/site9/index.html  - 🚀 Espace")
        print(f"  10. http://localhost:{PORT}/site10/index.html - 🎵 Musique")
        print("\n⚡ Appuyez sur Ctrl+C pour arrêter le serveur")
        print("=" * 60)

        httpd.serve_forever()
