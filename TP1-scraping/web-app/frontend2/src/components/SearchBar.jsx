import { useState } from 'react'
import './SearchBar.css'

function SearchBar({ onSearch, loading }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch(input)
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <div className="search-input-wrapper">
        <span className="search-icon">🔍</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Rechercher des images (ex: chat, Ferrari...)"
          className="search-input"
          disabled={loading}
        />
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? 'Recherche...' : 'Rechercher'}
        </button>
      </div>
      {/* <p className="search-hint">
        Méthode séquentielle : Titre → Image (src/alt) → Paragraphes
      </p> */}
    </form>
  )
}

export default SearchBar
