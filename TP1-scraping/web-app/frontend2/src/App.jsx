import { useState } from 'react'
import SearchBar from './components/SearchBar'
import Results from './components/Results'
import Header from './components/Header'
import SkeletonLoading from './components/SkeletonLoading'
import './App.css'

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState('')
  const [error, setError] = useState(null)
  const [searchMode, setSearchMode] = useState('OR')

  const handleSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setError('Veuillez entrer un terme de recherche')
      return
    }

    setLoading(true)
    setError(null)
    setQuery(searchQuery)

    try {
      const response = await fetch(
        `http://localhost:5000/api/search?q=${encodeURIComponent(searchQuery)}&mode=${searchMode}`
      )
      const data = await response.json()
      
      if (data.error) {
        setError(data.error)
        setResults(null)
      } else {
        setResults(data)
      }
    } catch (err) {
      setError('Erreur de connexion au serveur. Vérifiez que le backend est lancé.')
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <SearchBar onSearch={handleSearch} loading={loading} />
        
        {/* Mode de recherche OR / AND */}
        <div className="search-mode">
          <span>Mode de recherche multi-mots :</span>
          <button 
            className={`mode-btn ${searchMode === 'OR' ? 'active' : ''}`}
            onClick={() => setSearchMode('OR')}
          >
            OU (au moins un mot)
          </button>
          <button 
            className={`mode-btn ${searchMode === 'AND' ? 'active' : ''}`}
            onClick={() => setSearchMode('AND')}
          >
            ET (tous les mots)
          </button>
        </div>
        
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}
        
        {loading && <SkeletonLoading />}
        
        {results && !loading && (
          <Results data={results} query={query} onSearch={handleSearch} />
        )}
        
        {!results && !loading && !error && (
          <div className="welcome">
            <div className="welcome-icon">🔍</div>
            <h2>Bienvenue sur le Moteur de Recherche d'Images</h2>
            <p>Entrez un ou plusieurs mots-clés pour rechercher des images</p>
            <div className="suggestions">
              <p>Suggestions :</p>
              <div className="suggestion-tags">
                {['chat', 'Ferrari', 'voiture rouge', 'chat noir', 'pizza', 'lion nature', 'astronaut space', 'surf', 'piano musique'].map(tag => (
                  <button key={tag} onClick={() => handleSearch(tag)} className="tag">
                    {tag}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
