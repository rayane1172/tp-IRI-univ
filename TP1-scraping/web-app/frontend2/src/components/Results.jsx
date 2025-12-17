import ImageCard from './ImageCard'
import './Results.css'

function Results({ data, query, onSearch }) {
  if (!data || data.total_images === 0) {
    return (
      <div className="no-results">
        <div className="no-results-icon">😕</div>
        <h3>Aucun résultat trouvé</h3>
        <p>Aucune image trouvée pour "{query}"</p>
        
        {/* Suggestions avec Levenshtein */}
        {data?.suggestions && data.suggestions.length > 0 && (
          <div className="suggestions-section">
            <p className="suggestions-label">💡 Vouliez-vous dire :</p>
            <div className="suggestions-list">
              {data.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-btn"
                  onClick={() => onSearch && onSearch(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {(!data?.suggestions || data.suggestions.length === 0) && (
          <p className="hint">Essayez un autre terme de recherche</p>
        )}
      </div>
    )
  }

  return (
    <div className="results">
      <div className="results-header">
        <h2>
          <span className="results-icon">📸</span>
          Résultats pour "{query}"
        </h2>
        <div className="results-stats">
          <span className="stat">
            <span className="stat-icon">🌐</span>
            {data.total_sites} site{data.total_sites > 1 ? 's' : ''}
          </span>
          <span className="stat">
            <span className="stat-icon">🖼️</span>
            {data.total_images} image{data.total_images > 1 ? 's' : ''}
          </span>
          <span className="stat mode-indicator">
            Mode: <strong>{data.search_mode === 'OR' ? 'OU' : 'ET'}</strong>
          </span>
        </div>
        
        {/* Afficher les mots recherchés si plusieurs */}
        {data.query_words && data.query_words.length > 1 && (
          <div className="query-words">
            <span>Mots recherchés:</span>
            {data.query_words.map((word, i) => (
              <span key={i} className="query-word">{word}</span>
            ))}
          </div>
        )}
      </div>

      {data.results.map((site) => (
        <div key={site.site_id} className="site-section">
          <div className="site-header">
            <span className="site-emoji">{site.site_emoji}</span>
            <h3>{site.site_name}</h3>
            <div className="method-badges">
              {site.methods.includes('title') && <span className="badge badge-title">Titre</span>}
              {site.methods.includes('url') && <span className="badge badge-url">URL</span>}
              {site.methods.includes('alt') && <span className="badge badge-alt">Alt</span>}
              {site.methods.includes('text') && <span className="badge badge-text">Texte</span>}
            </div>
            {/* Afficher les mots trouvés dans ce site */}
            {site.matched_words && site.matched_words.length > 0 && (
              <span className="matched-words">
                Trouvé: {site.matched_words.join(', ')}
              </span>
            )}
            <span className="image-count">{site.images.length} image{site.images.length > 1 ? 's' : ''}</span>
          </div>
          
          <div className="images-grid">
            {site.images.map((image, index) => (
              <ImageCard key={index} image={image} siteName={site.site_name} siteUrl={site.site_url} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default Results
