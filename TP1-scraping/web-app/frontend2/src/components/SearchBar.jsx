import { useState } from "react";
import "./SearchBar.css";

function SearchBar({ onSearch, loading }) {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onSearch(input);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && input.trim() && !loading) {
      onSearch(input);
    }
  };

  return (
    <div className="search-bar">
      <div className="search-input-wrapper">
        <span className="search-icon">🔍</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Rechercher des images (ex: chat, Ferrari...)"
          className="search-input"
          disabled={loading}
        />
        <button
          type="button"
          onClick={handleSubmit}
          className={`search-button ${loading ? "loading" : ""}`}
          disabled={loading || !input.trim()}
        >
          <span>{loading ? "Recherche..." : "Rechercher"}</span>
        </button>
      </div>
      <p className="search-hint">
        💡 Astuce : Utilisez plusieurs mots-clés pour des résultats plus précis
      </p>
    </div>
  );
}

export default SearchBar;
