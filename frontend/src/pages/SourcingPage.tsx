import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Globe, ArrowLeft, Star, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import Navigation from '../components/Navigation'
import { ComplianceExportButton } from '../components/ComplianceExportButton'
import { SaveAnalysisButton } from '../components/SaveAnalysisButton'
import { api } from '../services/api'

interface SourcingAlternative {
  country_code: string
  country_name: string
  effective_rate_percent: number
  rate_note: string
  trade_agreement: string | null
  annual_savings: number | null
  savings_percent: number
  risk_score: number
  supply_reliability: number
  lead_time_weeks: number
  recommended: boolean
}

interface SourcingResult {
  hts_code: string
  current_country: string
  current_rate_percent: number
  annual_import_value: number | null
  alternatives: SourcingAlternative[]
  top_pick: string | null
  ai_analysis: string
  caveat: string
}

function RiskBar({ value, label, invert = false }: { value: number; label: string; invert?: boolean }) {
  const pct = invert ? 100 - value : value
  const color = pct >= 70 ? 'bg-green-400' : pct >= 40 ? 'bg-yellow-400' : 'bg-red-400'
  return (
    <div>
      <div className="flex justify-between text-xs text-gray-500 mb-0.5">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

const COUNTRIES = [
  { code: 'CN', name: 'China' }, { code: 'VN', name: 'Vietnam' },
  { code: 'IN', name: 'India' }, { code: 'MX', name: 'Mexico' },
  { code: 'CA', name: 'Canada' }, { code: 'KR', name: 'South Korea' },
  { code: 'TW', name: 'Taiwan' }, { code: 'TH', name: 'Thailand' },
  { code: 'MY', name: 'Malaysia' }, { code: 'JP', name: 'Japan' },
  { code: 'EU', name: 'EU' }, { code: 'BD', name: 'Bangladesh' },
  { code: 'ID', name: 'Indonesia' },
]

export default function SourcingPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<SourcingResult | null>(null)
  const [form, setForm] = useState({
    hts_code: '',
    current_country: 'CN',
    annual_import_value: '',
  })

  const isAuthenticated = !!localStorage.getItem('token')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.hts_code) return
    setLoading(true)
    try {
      const params = new URLSearchParams({ current_country: form.current_country })
      if (form.annual_import_value) params.append('annual_import_value', form.annual_import_value)
      const res = await api.get(`/sourcing/${encodeURIComponent(form.hts_code)}?${params}`)
      setResult(res.data)
    } catch {
      toast.error('Lookup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const shown = result?.alternatives.slice(0, 8) ?? []

  return (
    <div className="min-h-screen">
      <Navigation isAuthenticated={isAuthenticated} onLogout={() => { localStorage.removeItem('token'); navigate('/') }} />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="page-hero -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-6 mb-8">
          <button onClick={() => navigate('/dashboard')} className="flex items-center text-sm text-blue-300 hover:text-white mb-4 transition-colors">
            <ArrowLeft size={14} className="mr-1" /> Back to Dashboard
          </button>
          <div className="flex items-center space-x-4">
            <div className="rounded-2xl p-3 bg-white/15 backdrop-blur-sm">
              <Globe className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Alternative Sourcing Finder</h1>
              <p className="text-blue-200 text-sm mt-0.5">Find countries with lower US tariff rates for any HTS code</p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="card p-6 mb-6">
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">HTS Code *</label>
              <input
                required
                type="text"
                placeholder="e.g. 8471.30"
                value={form.hts_code}
                onChange={e => setForm(f => ({ ...f, hts_code: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>
            <div className="w-48">
              <label className="block text-sm font-medium text-gray-700 mb-1">Current Origin</label>
              <select
                value={form.current_country}
                onChange={e => setForm(f => ({ ...f, current_country: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              >
                {COUNTRIES.map(c => <option key={c.code} value={c.code}>{c.code} — {c.name}</option>)}
              </select>
            </div>
            <div className="w-44">
              <label className="block text-sm font-medium text-gray-700 mb-1">Annual Value ($)</label>
              <input
                type="number"
                placeholder="optional"
                value={form.annual_import_value}
                onChange={e => setForm(f => ({ ...f, annual_import_value: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-brand-teal text-white rounded-lg font-medium text-sm hover:bg-brand-teal-dark transition-colors disabled:opacity-50 flex items-center space-x-2 whitespace-nowrap"
            >
              {loading ? <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <Globe size={16} />}
              <span>{loading ? 'Finding...' : 'Find Alternatives'}</span>
            </button>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-5">
            {/* Current rate banner */}
            <div className="bg-brand-navy text-white rounded-xl p-5 flex items-center justify-between">
              <div>
                <p className="text-blue-200 text-sm">Current: {result.current_country} sourcing for {result.hts_code}</p>
                <p className="text-3xl font-bold">{result.current_rate_percent}% effective tariff</p>
                {result.annual_import_value && (
                  <p className="text-blue-300 text-sm mt-1">
                    Annual tariff cost: ${(result.annual_import_value * result.current_rate_percent / 100).toLocaleString()}
                  </p>
                )}
              </div>
              <TrendingDown className="h-12 w-12 text-brand-gold opacity-60" />
            </div>

            {/* AI analysis */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p className="text-sm text-blue-800">{result.ai_analysis}</p>
            </div>

            {/* Alternatives grid */}
            <div>
              <h2 className="font-semibold text-brand-navy mb-3">
                Alternative Sourcing Countries — ranked by savings
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {shown.map(alt => (
                  <div
                    key={alt.country_code}
                    className={`bg-white rounded-xl border shadow-card p-5 relative ${
                      alt.recommended ? 'border-brand-teal' : 'border-gray-100'
                    }`}
                  >
                    {alt.recommended && (
                      <div className="absolute -top-2.5 left-4 px-2.5 py-0.5 bg-brand-teal text-white text-xs font-semibold rounded-full flex items-center space-x-1">
                        <Star size={10} />
                        <span>Recommended</span>
                      </div>
                    )}

                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="font-bold text-brand-navy text-lg">{alt.country_name}</p>
                        <p className="font-mono text-sm text-gray-500">{alt.country_code}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-brand-navy">{alt.effective_rate_percent}%</p>
                        {alt.savings_percent > 0 ? (
                          <span className="text-xs font-semibold text-green-600 bg-green-100 px-2 py-0.5 rounded-full">
                            −{alt.savings_percent.toFixed(0)}% rate
                          </span>
                        ) : alt.savings_percent < 0 ? (
                          <span className="text-xs font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded-full">
                            +{Math.abs(alt.savings_percent).toFixed(0)}% rate
                          </span>
                        ) : (
                          <span className="text-xs text-gray-400">same rate</span>
                        )}
                      </div>
                    </div>

                    {alt.trade_agreement && (
                      <div className="mb-2 flex items-center space-x-1">
                        <CheckCircle size={12} className="text-brand-teal" />
                        <span className="text-xs font-medium text-brand-teal">{alt.trade_agreement} — 0% qualifying</span>
                      </div>
                    )}

                    <p className="text-xs text-gray-500 mb-3">{alt.rate_note}</p>

                    {/* Metrics bars */}
                    <div className="space-y-2 mb-3">
                      <RiskBar value={alt.supply_reliability} label="Supply Reliability" />
                      <RiskBar value={100 - alt.risk_score} label="Political Stability" />
                    </div>

                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Lead time: {alt.lead_time_weeks}w</span>
                      {alt.annual_savings && alt.annual_savings > 0 && (
                        <span className="font-semibold text-green-600">
                          Saves ${alt.annual_savings.toLocaleString()}/yr
                        </span>
                      )}
                      {alt.annual_savings && alt.annual_savings < 0 && (
                        <span className="font-semibold text-red-500 flex items-center space-x-1">
                          <AlertTriangle size={10} />
                          <span>+${Math.abs(alt.annual_savings).toLocaleString()}/yr cost</span>
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Caveat */}
            <p className="text-xs text-gray-400 text-center">{result.caveat}</p>
            <div className="flex items-center justify-end gap-3 mt-2">
              <SaveAnalysisButton
                toolType="sourcing"
                title={`Sourcing — HTS ${form.hts_code}`}
                resultData={result}
                formData={form}
              />
              <ComplianceExportButton reportType="sourcing" title="Alternative Sourcing Analysis" data={result} metadata={{ hts_code: form.hts_code }} />
            </div>
          </div>
        )}
      </div>

      <footer className="mt-12 py-6 border-t border-gray-100">
        <p className="text-center text-xs text-gray-400">DJ AI Business Consultant • Syracuse, NY • Transforming Business, Rising Above the Challenges</p>
      </footer>
    </div>
  )
}
