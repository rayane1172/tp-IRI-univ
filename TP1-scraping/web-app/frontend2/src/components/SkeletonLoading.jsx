import './SkeletonLoading.css'

function SkeletonLoading() {
  // Simuler 3 sites avec des images
  const skeletonSites = [
    { id: 1, imageCount: 3 },
    { id: 2, imageCount: 4 },
    { id: 3, imageCount: 2 },
  ]

  return (
    <div className="skeleton-results">
      {/* Header skeleton */}
      <div className="skeleton-header">
        <div className="skeleton-title shimmer"></div>
        <div className="skeleton-stats">
          <div className="skeleton-stat shimmer"></div>
          <div className="skeleton-stat shimmer"></div>
          <div className="skeleton-stat shimmer"></div>
        </div>
      </div>

      {/* Site sections skeleton */}
      {skeletonSites.map((site) => (
        <div key={site.id} className="skeleton-site">
          <div className="skeleton-site-header">
            <div className="skeleton-emoji shimmer"></div>
            <div className="skeleton-site-title shimmer"></div>
            <div className="skeleton-badges">
              <div className="skeleton-badge shimmer"></div>
              <div className="skeleton-badge shimmer"></div>
            </div>
          </div>
          
          <div className="skeleton-images-grid">
            {Array.from({ length: site.imageCount }).map((_, index) => (
              <div key={index} className="skeleton-card">
                <div className="skeleton-image shimmer"></div>
                <div className="skeleton-card-content">
                  <div className="skeleton-alt shimmer"></div>
                  <div className="skeleton-url shimmer"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default SkeletonLoading
