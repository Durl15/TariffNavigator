import React, { useState, useEffect } from 'react'
import {
  getWatchlists,
  createWatchlist,
  updateWatchlist,
  deleteWatchlist,
  toggleWatchlist,
  type Watchlist,
  type WatchlistCreate,
} from '../services/api'
import Navigation from '../components/Navigation'
import '../styles/WatchlistsPage.css'

const WatchlistsPage: React.FC = () => {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState<WatchlistCreate>({
    name: '',
    description: '',
    hs_codes: [],
    countries: [],
    alert_preferences: { email: true, digest: 'daily' },
  })
  const [hsCodeInput, setHsCodeInput] = useState('')
  const [countryInput, setCountryInput] = useState('')

  // Fetch watchlists
  const fetchWatchlists = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getWatchlists(1, 100)
      setWatchlists(data.watchlists)
    } catch (err: any) {
      setError(err.message || 'Failed to load watchlists')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWatchlists()
  }, [])

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      hs_codes: [],
      countries: [],
      alert_preferences: { email: true, digest: 'daily' },
    })
    setHsCodeInput('')
    setCountryInput('')
    setEditingId(null)
    setShowForm(false)
  }

  // Handle create/edit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (formData.hs_codes.length === 0) {
      setError('Please add at least one HS code')
      return
    }

    if (formData.countries.length === 0) {
      setError('Please add at least one country')
      return
    }

    try {
      if (editingId) {
        await updateWatchlist(editingId, formData)
      } else {
        await createWatchlist(formData)
      }
      resetForm()
      fetchWatchlists()
    } catch (err: any) {
      setError(err.message || 'Failed to save watchlist')
    }
  }

  // Handle edit
  const handleEdit = (watchlist: Watchlist) => {
    setFormData({
      name: watchlist.name,
      description: watchlist.description || '',
      hs_codes: watchlist.hs_codes,
      countries: watchlist.countries,
      alert_preferences: watchlist.alert_preferences || { email: true, digest: 'daily' },
    })
    setEditingId(watchlist.id)
    setShowForm(true)
  }

  // Handle delete
  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this watchlist?')) {
      return
    }

    try {
      await deleteWatchlist(id)
      fetchWatchlists()
    } catch (err: any) {
      setError('Failed to delete watchlist')
    }
  }

  // Handle toggle active
  const handleToggle = async (id: string) => {
    try {
      await toggleWatchlist(id)
      fetchWatchlists()
    } catch (err: any) {
      setError('Failed to toggle watchlist')
    }
  }

  // Add HS code
  const addHsCode = () => {
    const code = hsCodeInput.trim()
    if (code && !formData.hs_codes.includes(code)) {
      setFormData({ ...formData, hs_codes: [...formData.hs_codes, code] })
      setHsCodeInput('')
    }
  }

  // Remove HS code
  const removeHsCode = (code: string) => {
    setFormData({
      ...formData,
      hs_codes: formData.hs_codes.filter((c) => c !== code),
    })
  }

  // Add country
  const addCountry = () => {
    const country = countryInput.trim().toUpperCase()
    if (country && !formData.countries.includes(country)) {
      setFormData({ ...formData, countries: [...formData.countries, country] })
      setCountryInput('')
    }
  }

  // Remove country
  const removeCountry = (country: string) => {
    setFormData({
      ...formData,
      countries: formData.countries.filter((c) => c !== country),
    })
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/';
  };

  const isAuthenticated = !!localStorage.getItem('auth_token');

  return (
    <>
      <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      <div className="watchlists-page">
        <div className="watchlists-container">
        <div className="watchlists-header">
          <h1>Watchlists</h1>
          <button
            className="create-button"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : '+ Create Watchlist'}
          </button>
        </div>

        <p className="watchlists-description">
          Monitor tariff changes for specific HS codes and countries.
          Get notified when rates change.
        </p>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {/* Create/Edit Form */}
        {showForm && (
          <div className="watchlist-form-card">
            <h2>{editingId ? 'Edit Watchlist' : 'Create Watchlist'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="e.g., China Electronics"
                  required
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Optional description"
                  rows={2}
                />
              </div>

              <div className="form-group">
                <label>HS Codes *</label>
                <div className="input-with-button">
                  <input
                    type="text"
                    value={hsCodeInput}
                    onChange={(e) => setHsCodeInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addHsCode())}
                    placeholder="e.g., 8517.13"
                  />
                  <button type="button" onClick={addHsCode}>
                    Add
                  </button>
                </div>
                <div className="tags-list">
                  {formData.hs_codes.map((code) => (
                    <span key={code} className="tag">
                      {code}
                      <button
                        type="button"
                        onClick={() => removeHsCode(code)}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Countries *</label>
                <div className="input-with-button">
                  <input
                    type="text"
                    value={countryInput}
                    onChange={(e) => setCountryInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCountry())}
                    placeholder="e.g., CN (2-letter code)"
                    maxLength={2}
                  />
                  <button type="button" onClick={addCountry}>
                    Add
                  </button>
                </div>
                <div className="tags-list">
                  {formData.countries.map((country) => (
                    <span key={country} className="tag">
                      {country}
                      <button
                        type="button"
                        onClick={() => removeCountry(country)}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="submit-button">
                  {editingId ? 'Update Watchlist' : 'Create Watchlist'}
                </button>
                <button
                  type="button"
                  className="cancel-button"
                  onClick={resetForm}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading watchlists...</p>
          </div>
        ) : (
          <>
            {/* Watchlists List */}
            {watchlists.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📋</div>
                <h3>No watchlists yet</h3>
                <p>Create your first watchlist to start monitoring tariff changes</p>
              </div>
            ) : (
              <div className="watchlists-grid">
                {watchlists.map((watchlist) => (
                  <div
                    key={watchlist.id}
                    className={`watchlist-card ${!watchlist.is_active ? 'inactive' : ''}`}
                  >
                    <div className="watchlist-header-row">
                      <h3>{watchlist.name}</h3>
                      <div className="watchlist-status">
                        <label className="toggle-switch">
                          <input
                            type="checkbox"
                            checked={watchlist.is_active}
                            onChange={() => handleToggle(watchlist.id)}
                          />
                          <span className="toggle-slider"></span>
                        </label>
                        <span className="status-text">
                          {watchlist.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>

                    {watchlist.description && (
                      <p className="watchlist-description">
                        {watchlist.description}
                      </p>
                    )}

                    <div className="watchlist-details">
                      <div className="detail-section">
                        <label>HS Codes ({watchlist.hs_codes.length})</label>
                        <div className="tags-list">
                          {watchlist.hs_codes.slice(0, 5).map((code) => (
                            <span key={code} className="tag-readonly">
                              {code}
                            </span>
                          ))}
                          {watchlist.hs_codes.length > 5 && (
                            <span className="tag-readonly">
                              +{watchlist.hs_codes.length - 5} more
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="detail-section">
                        <label>Countries ({watchlist.countries.length})</label>
                        <div className="tags-list">
                          {watchlist.countries.slice(0, 5).map((country) => (
                            <span key={country} className="tag-readonly">
                              {country}
                            </span>
                          ))}
                          {watchlist.countries.length > 5 && (
                            <span className="tag-readonly">
                              +{watchlist.countries.length - 5} more
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="watchlist-actions">
                      <button
                        className="edit-button"
                        onClick={() => handleEdit(watchlist)}
                      >
                        Edit
                      </button>
                      <button
                        className="delete-button"
                        onClick={() => handleDelete(watchlist.id)}
                      >
                        Delete
                      </button>
                    </div>

                    <div className="watchlist-meta">
                      Created {new Date(watchlist.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
    </>
  )
}

export default WatchlistsPage
