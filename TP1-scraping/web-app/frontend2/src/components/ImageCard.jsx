import { useState } from 'react'
import './ImageCard.css'

function ImageCard({ image, siteName, siteUrl }) {
  const [loaded, setLoaded] = useState(false)
  const [error, setError] = useState(false)

  return (
    <div className="image-card">
      <div className="image-wrapper">
        {!loaded && !error && (
          <div className="image-placeholder">
            <div className="loader"></div>
          </div>
        )}
        {error ? (
          <div className="image-error">
            <span>❌</span>
            <p>Image non disponible</p>
          </div>
        ) : (
          <img
            src={image.src}
            alt={image.alt}
            onLoad={() => setLoaded(true)}
            onError={() => setError(true)}
            style={{ display: loaded ? 'block' : 'none' }}
          />
        )}
      </div>
      <div className="image-info">
        <p className="image-alt" title={image.alt}>
          {image.alt || 'Sans description'}
        </p>
        <a 
          href={siteUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="site-url-link"
        >
          🌐 {siteUrl}
        </a>
      </div>
    </div>
  )
}

export default ImageCard
