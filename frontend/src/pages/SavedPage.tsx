import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { BookmarkCheck, Trash2, ArrowLeft, ExternalLink, Filter } from 'lucide-react'
import toast from 'react-hot-toast'
import Navigation from '../components/Navigation'
import { getAnalyses, deleteAnalysis, AnalysisRecord } from '../services/api'

// ── Config maps ───────────────────────────────────────────────────────────────

type ToolType = 'cashflow' | 'drawback' | 'usmca' | 'supply_chain' | 'hts_audit' | 'sourcing' | 'scenario'

const TOOL_DISPLAY: Record<ToolType, string> = {
  cashflow: 'Cash Flow',
  drawback: 'Drawback',
  usmca: 'USMCA',
  supply_chain: 'Supply Chain',
  hts_audit: 'HTS Audit',
  sourcing: 'Sourcing',
  scenario: 'Scenario',
}

const TOOL_ROUTE: Record<ToolType, string> = {
  cashflow: '/cashflow',
  drawback: '/drawback',
  usmca: '/usmca-check',
  supply_chain: '/supply-chain',
  hts_audit: '/hts-audit',
  sourcing: '/sourcing',
  scenario: '/scenarios',
}

// Tailwind badge colour classes per tool type
const TOOL_BADGE: Record<ToolType, string> = {
  cashflow: 'bg-red-100 text-red-700 border border-red-200',
  drawback: 'bg-green-100 text-green-700 border border-green-200',
  usmca: 'bg-blue-100 text-blue-700 border border-blue-200',
  supply_chain: 'bg-orange-100 text-orange-700 border border-orange-200',
  hts_audit: 'bg-purple-100 text-purple-700 border border-purple-200',
  sourcing: 'bg-teal-100 text-teal-700 border border-teal-200',
  scenario: 'bg-yellow-100 text-yellow-700 border border-yellow-200',
}

// Icon emoji per tool type (keeps lucide-icon dependency minimal)
const TOOL_EMOJI: Record<ToolType, string> = {
  cashflow: '💵',
  drawback: '♻️',
  usmca: '🤝',
  supply_chain: '🔗',
  hts_audit: '🔍',
  sourcing: '🌍',
  scenario: '⚡',
}

const FILTER_OPTIONS: Array<{ label: string; value: string }> = [
  { label: 'All', value: '' },
  { label: 'Cash Flow', value: 'cashflow' },
  { label: 'Drawback', value: 'drawback' },
  { label: 'USMCA', value: 'usmca' },
  { label: 'Supply Chain', value: 'supply_chain' },
  { label: 'HTS Audit', value: 'hts_audit' },
  { label: 'Sourcing', value: 'sourcing' },
  { label: 'Scenario', value: 'scenario' },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }) + ' at ' + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
}

function getToolDisplay(type: string): string {
  return TOOL_DISPLAY[type as ToolType] ?? type
}

function getToolRoute(type: string): string {
  return TOOL_ROUTE[type as ToolType] ?? '/dashboard'
}

function getToolBadge(type: string): string {
  return TOOL_BADGE[type as ToolType] ?? 'bg-gray-100 text-gray-700 border border-gray-200'
}

function getToolEmoji(type: string): string {
  return TOOL_EMOJI[type as ToolType] ?? '📋'
}

/** Build a small list of preview key/value pairs from form_data */
function buildPreview(form_data: Record<string, unknown> | null): Array<{ key: string; value: string }> {
  if (!form_data) return []
  const items: Array<{ key: string; value: string }> = []

  const add = (label: string, raw: unknown) => {
    if (raw != null && raw !== '') {
      items.push({ key: label, value: String(raw) })
    }
  }

  add('HTS', form_data.hts_code)
  add('Country', form_data.country_of_origin ?? form_data.origin_country ?? form_data.country)

  const val = form_data.shipment_value ?? form_data.cif_value ?? form_data.annual_import_value
  if (val != null) {
    const num = Number(val)
    if (!Number.isNaN(num)) {
      add('Value', new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num))
    } else {
      add('Value', String(val))
    }
  }

  add('Product', form_data.product_description ?? form_data.product_name)

  return items.slice(0, 3) // max 3 preview chips
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function SavedPage() {
  const navigate = useNavigate()
  const isAuthenticated = !!localStorage.getItem('token')

  const [analyses, setAnalyses] = useState<AnalysisRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [filterType, setFilterType] = useState('')
  const [deleting, setDeleting] = useState<string | null>(null)   // id being confirmed
  const [deletingInFlight, setDeletingInFlight] = useState<string | null>(null)

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login')
      return
    }
    loadAnalyses()
  }, [])

  async function loadAnalyses() {
    setLoading(true)
    try {
      const data = await getAnalyses()
      setAnalyses(data)
    } catch {
      toast.error('Failed to load saved analyses')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/'
  }

  function handleDeleteClick(id: string) {
    if (deleting === id) {
      // Second click — confirmed, proceed with deletion
      confirmDelete(id)
    } else {
      setDeleting(id)
    }
  }

  async function confirmDelete(id: string) {
    setDeletingInFlight(id)
    try {
      await deleteAnalysis(id)
      setAnalyses(prev => prev.filter(a => a.id !== id))
      toast.success('Analysis deleted')
    } catch {
      toast.error('Failed to delete analysis')
    } finally {
      setDeleting(null)
      setDeletingInFlight(null)
    }
  }

  // Reset confirm state when user clicks elsewhere
  function handleCardBlur(id: string) {
    if (deleting === id) {
      setTimeout(() => setDeleting(prev => (prev === id ? null : prev)), 200)
    }
  }

  // Filtered list
  const filtered = filterType
    ? analyses.filter(a => a.tool_type === filterType)
    : analyses

  // ── Loading skeleton ───────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />
        <div className="max-w-4xl mx-auto px-4 py-10 space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-white rounded-xl shadow-card border border-gray-100 p-5 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-3" />
              <div className="h-3 bg-gray-100 rounded w-2/3" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />

      {/* Page header band */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center space-x-1.5 text-sm text-gray-500 hover:text-brand-navy transition-colors mb-3"
          >
            <ArrowLeft size={15} />
            <span>Back to Dashboard</span>
          </button>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-brand-navy/10 rounded-xl p-2.5">
                <BookmarkCheck size={22} className="text-brand-navy" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h1 className="text-2xl font-bold text-brand-navy">Saved Analyses</h1>
                  {analyses.length > 0 && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-brand-navy/10 text-brand-navy">
                      {analyses.length}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-500">Your saved tool results, ready to revisit</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">

        {/* ── Filter bar ────────────────────────────────────────────────── */}
        <div className="flex items-center space-x-2 flex-wrap gap-y-2">
          <Filter size={14} className="text-gray-400 flex-shrink-0" />
          {FILTER_OPTIONS.map(opt => (
            <button
              key={opt.value}
              onClick={() => setFilterType(opt.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                filterType === opt.value
                  ? 'bg-brand-navy text-white'
                  : 'bg-white border border-gray-200 text-gray-600 hover:border-brand-navy/40 hover:text-brand-navy'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* ── Analysis list ─────────────────────────────────────────────── */}
        {filtered.length === 0 ? (
          <div className="bg-white rounded-xl shadow-card border border-gray-100 p-12 text-center">
            <BookmarkCheck size={40} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-base font-semibold text-gray-600 mb-2">
              {filterType ? 'No saved analyses for this filter' : 'No saved analyses yet'}
            </h3>
            <p className="text-sm text-gray-400 max-w-xs mx-auto">
              {filterType
                ? 'Try a different filter, or run a tool analysis and click "Save Analysis" to save results here.'
                : 'Run a tool analysis and click "Save Analysis" to keep results here.'}
            </p>
            {filterType && (
              <button
                onClick={() => setFilterType('')}
                className="mt-4 px-4 py-2 text-sm font-medium bg-brand-navy/10 text-brand-navy rounded-lg hover:bg-brand-navy/20 transition-colors"
              >
                Clear Filter
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map(analysis => {
              const preview = buildPreview(analysis.form_data)
              const isConfirming = deleting === analysis.id
              const isInFlight = deletingInFlight === analysis.id

              return (
                <div
                  key={analysis.id}
                  className="bg-white rounded-xl shadow-card border border-gray-100 p-5 flex items-start justify-between gap-4"
                >
                  {/* Left — icon + meta */}
                  <div className="flex items-start space-x-4 min-w-0">
                    {/* Emoji icon circle */}
                    <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-center text-lg select-none">
                      {getToolEmoji(analysis.tool_type)}
                    </div>

                    <div className="min-w-0">
                      {/* Tool badge + title */}
                      <div className="flex items-center flex-wrap gap-1.5 mb-1">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${getToolBadge(analysis.tool_type)}`}>
                          {getToolDisplay(analysis.tool_type)}
                        </span>
                      </div>
                      <p className="text-sm font-semibold text-brand-navy truncate" title={analysis.title}>
                        {analysis.title}
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5">{formatDate(analysis.created_at)}</p>

                      {/* Preview chips */}
                      {preview.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-2">
                          {preview.map(p => (
                            <span
                              key={p.key}
                              className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-xs text-gray-600"
                            >
                              <span className="font-medium text-gray-500 mr-1">{p.key}:</span>
                              {p.value}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right — actions */}
                  <div
                    className="flex items-center space-x-2 flex-shrink-0"
                    onBlur={() => handleCardBlur(analysis.id)}
                  >
                    {/* Open Tool */}
                    <button
                      onClick={() => navigate(getToolRoute(analysis.tool_type))}
                      className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium bg-brand-blue/10 text-brand-blue rounded-lg hover:bg-brand-blue/20 transition-colors"
                    >
                      <ExternalLink size={12} />
                      <span>Open Tool</span>
                    </button>

                    {/* Delete / Confirm delete */}
                    <button
                      onClick={() => handleDeleteClick(analysis.id)}
                      disabled={isInFlight}
                      className={`inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors disabled:opacity-60 ${
                        isConfirming
                          ? 'bg-red-600 text-white hover:bg-red-700'
                          : 'bg-gray-100 text-gray-500 hover:bg-red-50 hover:text-red-600'
                      }`}
                      title={isConfirming ? 'Click again to confirm delete' : 'Delete analysis'}
                    >
                      {isInFlight ? (
                        <div className="h-3.5 w-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                      ) : (
                        <Trash2 size={12} />
                      )}
                      <span>{isConfirming ? 'Confirm?' : 'Delete'}</span>
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}

      </div>

      {/* Footer */}
      <footer className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 border-t border-gray-200 mt-4">
        <p className="text-center text-xs text-gray-400">
          DJ AI Business Consultant &bull; Syracuse, NY &bull; Transforming Business, Rising Above the Challenges
        </p>
      </footer>
    </div>
  )
}
