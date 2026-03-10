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
import { Eye } from 'lucide-react'
import { usePageTitle } from '../hooks/usePageTitle'

const WatchlistsPage: React.FC = () => {
  usePageTitle('Watchlists')
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
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <>
      <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />
      <div>
        {/* Page Hero */}
        <div className="page-hero">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-brand-teal/20 flex items-center justify-center flex-shrink-0">
                <Eye className="w-5 h-5 text-brand-teal" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Watchlists</h1>
                <p className="text-blue-300 text-sm mt-1">Monitor tariff changes for HTS codes and countries</p>
              </div>
            </div>
            <button
              className="btn border border-white/10 text-white hover:bg-white/10"
              onClick={() => setShowForm(!showForm)}
            >
              {showForm ? 'Cancel' : '+ Create Watchlist'}
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

          {/* Error Message */}
          {error && (
            <div className="callout-red mb-4 flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="ml-4 text-red-400 hover:text-red-600 font-bold leading-none"
              >
                &times;
              </button>
            </div>
          )}

          {/* Create/Edit Form */}
          {showForm && (
            <div className="card p-6 mb-6 animate-in">
              <h2 className="text-lg font-bold text-brand-navy mb-6 pb-4 border-b border-gray-100">
                {editingId ? 'Edit Watchlist' : 'Create Watchlist'}
              </h2>
              <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Name */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                      Name *
                    </label>
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

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) =>
                        setFormData({ ...formData, description: e.target.value })
                      }
                      placeholder="Optional description"
                      rows={2}
                      className="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 resize-none"
                    />
                  </div>

                  {/* HS Codes */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                      HS Codes *
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={hsCodeInput}
                        onChange={(e) => setHsCodeInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addHsCode())}
                        placeholder="e.g., 8517.13"
                        className="flex-1"
                      />
                      <button type="button" onClick={addHsCode} className="btn btn-teal px-4">
                        Add
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {formData.hs_codes.map((code) => (
                        <span
                          key={code}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-brand-navy border border-blue-100"
                        >
                          {code}
                          <button
                            type="button"
                            onClick={() => removeHsCode(code)}
                            className="text-gray-400 hover:text-red-500 transition-colors ml-0.5"
                          >
                            &times;
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Countries */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                      Countries *
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={countryInput}
                        onChange={(e) => setCountryInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCountry())}
                        placeholder="e.g., CN (2-letter code)"
                        maxLength={2}
                        className="flex-1"
                      />
                      <button type="button" onClick={addCountry} className="btn btn-teal px-4">
                        Add
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {formData.countries.map((country) => (
                        <span
                          key={country}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-brand-navy border border-blue-100"
                        >
                          {country}
                          <button
                            type="button"
                            onClick={() => removeCountry(country)}
                            className="text-gray-400 hover:text-red-500 transition-colors ml-0.5"
                          >
                            &times;
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex gap-3 pt-4 border-t border-gray-100 mt-6">
                  <button type="submit" className="btn btn-teal px-6">
                    {editingId ? 'Update Watchlist' : 'Create Watchlist'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline px-6"
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
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <div className="w-8 h-8 border-4 border-brand-teal/30 border-t-brand-teal rounded-full animate-spin" />
              <p className="text-sm text-gray-400">Loading watchlists...</p>
            </div>
          ) : (
            <>
              {watchlists.length === 0 ? (
                /* Empty State */
                <div className="flex flex-col items-center justify-center py-20 text-center">
                  <div className="w-16 h-16 rounded-full bg-brand-teal/10 flex items-center justify-center mb-4">
                    <Eye className="w-8 h-8 text-brand-teal" />
                  </div>
                  <h3 className="text-lg font-bold text-brand-navy mb-2">No watchlists yet</h3>
                  <p className="text-sm text-gray-500 mb-6 max-w-sm">
                    Create your first watchlist to start monitoring tariff changes
                  </p>
                  <button className="btn btn-teal" onClick={() => setShowForm(true)}>
                    Create Watchlist
                  </button>
                </div>
              ) : (
                /* Watchlists Grid */
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {watchlists.map((watchlist) => (
                    <div
                      key={watchlist.id}
                      className={`card p-5 animate-in flex flex-col${!watchlist.is_active ? ' opacity-60' : ''}`}
                    >
                      {/* Card Header */}
                      <div className="flex items-start justify-between mb-1">
                        <span className="font-bold text-brand-navy">{watchlist.name}</span>
                        <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                          {/* Toggle Switch */}
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              className="sr-only"
                              checked={watchlist.is_active}
                              onChange={() => handleToggle(watchlist.id)}
                            />
                            <span
                              className={`w-10 h-5 rounded-full transition-colors ${
                                watchlist.is_active ? 'bg-brand-teal' : 'bg-gray-300'
                              } relative`}
                            >
                              <span
                                className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${
                                  watchlist.is_active ? 'translate-x-5' : 'translate-x-0'
                                }`}
                              />
                            </span>
                          </label>
                          <span
                            className={`text-xs font-medium ${
                              watchlist.is_active ? 'text-brand-teal' : 'text-gray-400'
                            }`}
                          >
                            {watchlist.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                      </div>

                      {watchlist.description && (
                        <p className="text-sm text-gray-500 mt-1 mb-3">{watchlist.description}</p>
                      )}

                      {/* HS Codes */}
                      <div className="space-y-2 mb-4">
                        <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-2">
                          HS Codes ({watchlist.hs_codes.length})
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {watchlist.hs_codes.slice(0, 5).map((code) => (
                            <span
                              key={code}
                              className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600"
                            >
                              {code}
                            </span>
                          ))}
                          {watchlist.hs_codes.length > 5 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
                              +{watchlist.hs_codes.length - 5} more
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Countries */}
                      <div className="space-y-2 mb-4">
                        <p className="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-2">
                          Countries ({watchlist.countries.length})
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {watchlist.countries.slice(0, 5).map((country) => (
                            <span
                              key={country}
                              className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600"
                            >
                              {country}
                            </span>
                          ))}
                          {watchlist.countries.length > 5 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
                              +{watchlist.countries.length - 5} more
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Card Actions */}
                      <div className="flex gap-2 pt-4 border-t border-gray-100 mt-auto">
                        <button
                          className="btn btn-outline text-sm px-4 py-2 flex-1"
                          onClick={() => handleEdit(watchlist)}
                        >
                          Edit
                        </button>
                        <button
                          className="px-4 py-2 text-sm font-medium rounded-xl text-red-500 hover:bg-red-50 border border-red-100 hover:border-red-200 transition-all flex-1 text-center"
                          onClick={() => handleDelete(watchlist.id)}
                        >
                          Delete
                        </button>
                      </div>

                      <p className="text-xs text-gray-400 mt-2">
                        Created {new Date(watchlist.created_at).toLocaleDateString()}
                      </p>
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
