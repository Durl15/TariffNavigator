import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, AlertTriangle, CheckCircle, XCircle, ArrowLeft, Plus, X } from 'lucide-react'
import toast from 'react-hot-toast'
import Navigation from '../components/Navigation'
import { TierGate } from '../components/UpgradePrompt'
import { ComplianceExportButton } from '../components/ComplianceExportButton'
import { SaveAnalysisButton } from '../components/SaveAnalysisButton'
import { api } from '../services/api'
import { usePageTitle } from '../hooks/usePageTitle'


interface RiskItem {
  risk_type: string
  severity: string
  description: string
  mitigation: string
}

interface ScanResult {
  overall_risk: string
  transshipment_risk: string
  section_301_exposure: boolean
  ad_cvd_risk: boolean
  estimated_penalty_exposure: number | null
  risks: RiskItem[]
  recommended_docs: string[]
  ai_analysis: string
}

const SEVERITY_STYLES: Record<string, string> = {
  high: 'bg-red-50 border-red-200 text-red-800',
  medium: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  low: 'bg-green-50 border-green-200 text-green-800',
}

const RISK_BADGE: Record<string, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700',
}

export default function SupplyChainPage() {
  usePageTitle('Supply Chain Scanner')
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ScanResult | null>(null)
  const [componentInput, setComponentInput] = useState('')
  const [form, setForm] = useState({
    supplier_country: 'VN',
    hts_code: '',
    product_description: '',
    annual_import_value: '',
    known_component_origins: [] as string[],
  })

  const isAuthenticated = !!localStorage.getItem('token')

  const addComponent = () => {
    const val = componentInput.trim().toUpperCase()
    if (val && !form.known_component_origins.includes(val)) {
      setForm(f => ({ ...f, known_component_origins: [...f.known_component_origins, val] }))
      setComponentInput('')
    }
  }

  const removeComponent = (c: string) => {
    setForm(f => ({ ...f, known_component_origins: f.known_component_origins.filter(x => x !== c) }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.hts_code) return
    setLoading(true)
    try {
      const res = await api.post('/compliance/supply-chain-scan', {
        supplier_country: form.supplier_country,
        hts_code: form.hts_code,
        product_description: form.product_description || undefined,
        annual_import_value: form.annual_import_value ? parseFloat(form.annual_import_value) : undefined,
        known_component_origins: form.known_component_origins,
      })
      setResult(res.data)
    } catch {
      toast.error('Scan failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Navigation isAuthenticated={isAuthenticated} onLogout={() => { localStorage.removeItem('token'); navigate('/') }} />

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="page-hero -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-6 mb-8">
          <button onClick={() => navigate('/dashboard')} className="flex items-center text-sm text-blue-300 hover:text-white mb-4 transition-colors">
            <ArrowLeft size={14} className="mr-1" /> Back to Dashboard
          </button>
          <div className="flex items-center space-x-4">
            <div className="rounded-2xl p-3 bg-white/15 backdrop-blur-sm">
              <Shield className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Supply Chain Risk Scanner</h1>
              <p className="text-blue-200 text-sm mt-0.5">Detect transshipment exposure and Section 301 liability before CBP does</p>
            </div>
          </div>
        </div>

        {/* Warning banner */}
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 mb-6">
          <p className="text-sm text-orange-800">
            <strong>CBP Warning:</strong> Goods assembled in Vietnam, Thailand, or Malaysia from Chinese components
            may still face 25%+ Section 301 tariffs. Penalties for misrepresentation reach $1M+.
          </p>
        </div>

        <TierGate
          requiredTier="pro"
          featureName="Supply Chain Risk Scanner"
          description="Full supply chain scanning with transshipment risk analysis and AI penalty estimates requires a Pro subscription."
        >
        {/* Form */}
        <div className="card p-6 mb-6">
          <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Supplier Country *</label>
              <select
                value={form.supplier_country}
                onChange={e => setForm(f => ({ ...f, supplier_country: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              >
                {['CN','VN','TH','MY','ID','MX','CA','IN','KR','TW','PH','BD','KH'].map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
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

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Product Description</label>
              <input
                type="text"
                placeholder="e.g. laptop motherboards, solar panels"
                value={form.product_description}
                onChange={e => setForm(f => ({ ...f, product_description: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Annual Import Value ($)</label>
              <input
                type="number"
                placeholder="e.g. 500000"
                value={form.annual_import_value}
                onChange={e => setForm(f => ({ ...f, annual_import_value: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Component Origins</label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  placeholder="e.g. CN, KR, TW"
                  value={componentInput}
                  onChange={e => setComponentInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addComponent() } }}
                  maxLength={2}
                  className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
                <button type="button" onClick={addComponent} className="px-3 py-2 bg-brand-navy text-white rounded-lg hover:bg-brand-navy-dark">
                  <Plus size={16} />
                </button>
              </div>
              <div className="flex flex-wrap gap-1 mt-2">
                {form.known_component_origins.map(c => (
                  <span key={c} className="flex items-center space-x-1 px-2 py-0.5 bg-brand-navy text-white text-xs rounded-full">
                    <span>{c}</span>
                    <button type="button" onClick={() => removeComponent(c)}><X size={10} /></button>
                  </span>
                ))}
              </div>
            </div>

            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-orange-600 text-white py-3 rounded-lg font-medium text-sm hover:bg-orange-700 transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {loading ? <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <Shield size={16} />}
                <span>{loading ? 'Scanning...' : 'Scan Supply Chain'}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Overall risk */}
            <div className={`rounded-xl border p-5 ${SEVERITY_STYLES[result.overall_risk]}`}>
              <div className="flex items-center justify-between mb-2">
                <p className="font-bold text-lg capitalize">{result.overall_risk} Overall Risk</p>
                <div className="flex space-x-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${RISK_BADGE[result.transshipment_risk]}`}>
                    Transshipment: {result.transshipment_risk}
                  </span>
                </div>
              </div>
              <p className="text-sm">{result.ai_analysis}</p>
              {result.estimated_penalty_exposure && (
                <p className="text-sm font-semibold mt-2">
                  Estimated penalty exposure: ${result.estimated_penalty_exposure.toLocaleString()}+
                </p>
              )}
            </div>

            {/* Exposure flags */}
            <div className="grid grid-cols-2 gap-4">
              <div className={`rounded-xl border p-4 flex items-center space-x-3 ${result.section_301_exposure ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                {result.section_301_exposure ? <XCircle size={20} className="text-red-500 flex-shrink-0" /> : <CheckCircle size={20} className="text-green-500 flex-shrink-0" />}
                <div>
                  <p className="text-sm font-medium">Section 301 Exposure</p>
                  <p className="text-xs text-gray-500">{result.section_301_exposure ? 'Yes — 25%+ tariffs apply' : 'Not detected'}</p>
                </div>
              </div>
              <div className={`rounded-xl border p-4 flex items-center space-x-3 ${result.ad_cvd_risk ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                {result.ad_cvd_risk ? <XCircle size={20} className="text-red-500 flex-shrink-0" /> : <CheckCircle size={20} className="text-green-500 flex-shrink-0" />}
                <div>
                  <p className="text-sm font-medium">AD/CVD Risk</p>
                  <p className="text-xs text-gray-500">{result.ad_cvd_risk ? 'Possible — verify with USITC' : 'Not detected'}</p>
                </div>
              </div>
            </div>

            {/* Risk items */}
            <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
              <h3 className="font-semibold text-brand-navy mb-4 flex items-center space-x-2">
                <AlertTriangle size={16} className="text-orange-500" />
                <span>Risk Details</span>
              </h3>
              <div className="space-y-3">
                {result.risks.map((risk, i) => (
                  <div key={i} className={`rounded-lg border p-4 ${SEVERITY_STYLES[risk.severity]}`}>
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-sm">{risk.risk_type}</p>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${RISK_BADGE[risk.severity]}`}>{risk.severity}</span>
                    </div>
                    <p className="text-xs mb-2">{risk.description}</p>
                    <p className="text-xs font-medium">Action: {risk.mitigation}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommended docs */}
            <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
              <h3 className="font-semibold text-brand-navy mb-4">Required Documentation</h3>
              <ul className="space-y-2">
                {result.recommended_docs.map((doc, i) => (
                  <li key={i} className="flex items-start space-x-2 text-sm text-gray-700">
                    <CheckCircle size={14} className="text-brand-teal mt-0.5 flex-shrink-0" />
                    <span>{doc}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="flex items-center justify-end gap-3 mt-2">
              <SaveAnalysisButton
                toolType="supply_chain"
                title={`Supply Chain Scan — ${form.product_description || form.hts_code || 'Product'}`}
                resultData={result}
                formData={form}
              />
              <ComplianceExportButton reportType="supply_chain" title="Supply Chain Risk Report" data={result} metadata={{ hts_code: form.hts_code, product_description: form.product_description }} />
            </div>
          </div>
        )}
        </TierGate>
      </div>

      <footer className="mt-12 py-6 border-t border-gray-100">
        <p className="text-center text-xs text-gray-400">DJ AI Business Consultant • Syracuse, NY • Transforming Business, Rising Above the Challenges</p>
      </footer>
    </div>
  )
}
