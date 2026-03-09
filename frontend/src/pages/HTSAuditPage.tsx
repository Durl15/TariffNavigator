import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, AlertTriangle, CheckCircle, ArrowLeft, TrendingDown } from 'lucide-react'
import toast from 'react-hot-toast'
import Navigation from '../components/Navigation'
import { ComplianceExportButton } from '../components/ComplianceExportButton'
import { SaveAnalysisButton } from '../components/SaveAnalysisButton'
import { api } from '../services/api'

interface AlternativeCode {
  code: string
  description: string
  estimated_rate: number
  annual_savings: number | null
}

interface AuditResult {
  current_code: string
  current_estimated_rate: number
  misclassification_risk: string
  overpayment_likely: boolean
  alternative_codes: AlternativeCode[]
  annual_savings_estimate: number | null
  ai_recommended_code: string | null
  ai_recommended_rate: number | null
  supplier_bias_warning: boolean
  ai_analysis: string
}

const RISK_STYLES: Record<string, string> = {
  high: 'border-red-200 bg-red-50',
  medium: 'border-yellow-200 bg-yellow-50',
  low: 'border-green-200 bg-green-50',
}

const RISK_TEXT: Record<string, string> = {
  high: 'text-red-700',
  medium: 'text-yellow-700',
  low: 'text-green-700',
}

export default function HTSAuditPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AuditResult | null>(null)
  const [form, setForm] = useState({
    product_description: '',
    current_hts_code: '',
    supplier_provided: true,
    annual_import_value: '',
    country_of_origin: 'CN',
  })

  const isAuthenticated = !!localStorage.getItem('token')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.product_description || !form.current_hts_code) return
    setLoading(true)
    try {
      const res = await api.post('/compliance/hts-audit', {
        product_description: form.product_description,
        current_hts_code: form.current_hts_code,
        supplier_provided: form.supplier_provided,
        annual_import_value: form.annual_import_value ? parseFloat(form.annual_import_value) : undefined,
        country_of_origin: form.country_of_origin,
      })
      setResult(res.data)
    } catch {
      toast.error('Audit failed. Please try again.')
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
              <Search className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">HTS Code Audit</h1>
              <p className="text-blue-200 text-sm mt-0.5">Detect misclassifications that cause overpayment or CBP penalties</p>
            </div>
          </div>
        </div>

        {/* Warning banner */}
        <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 mb-6">
          <p className="text-sm text-purple-800">
            <strong>Common problem:</strong> Suppliers provide HTS codes that are convenient for them, not optimal for you.
            A wrong 10-digit code can mean paying 25% instead of 3.5% — or triggering a CBP penalty audit.
          </p>
        </div>

        {/* Form */}
        <div className="card p-6 mb-6">
          <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Product Description *</label>
              <input
                required
                type="text"
                placeholder="e.g. wireless earbuds with built-in microphone and charging case"
                value={form.product_description}
                onChange={e => setForm(f => ({ ...f, product_description: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
              <p className="text-xs text-gray-400 mt-1">Be specific — include material, function, and key features</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Current HTS Code *</label>
              <input
                required
                type="text"
                placeholder="e.g. 8518.30"
                value={form.current_hts_code}
                onChange={e => setForm(f => ({ ...f, current_hts_code: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Country of Origin</label>
              <select
                value={form.country_of_origin}
                onChange={e => setForm(f => ({ ...f, country_of_origin: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              >
                {['CN','MX','CA','VN','IN','KR','TW','EU','JP'].map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Annual Import Value ($)</label>
              <input
                type="number"
                placeholder="e.g. 250000"
                value={form.annual_import_value}
                onChange={e => setForm(f => ({ ...f, annual_import_value: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="supplier_provided"
                checked={form.supplier_provided}
                onChange={e => setForm(f => ({ ...f, supplier_provided: e.target.checked }))}
                className="rounded border-gray-300 text-brand-blue"
              />
              <label htmlFor="supplier_provided" className="text-sm text-gray-700 cursor-pointer">
                HTS code was provided by my supplier
              </label>
            </div>

            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-purple-600 text-white py-3 rounded-lg font-medium text-sm hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {loading ? <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <Search size={16} />}
                <span>{loading ? 'Auditing...' : 'Audit My HTS Code'}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Risk summary */}
            <div className={`rounded-xl border p-5 ${RISK_STYLES[result.misclassification_risk]}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {result.overpayment_likely
                    ? <AlertTriangle size={22} className={`flex-shrink-0 mt-0.5 ${RISK_TEXT[result.misclassification_risk]}`} />
                    : <CheckCircle size={22} className="flex-shrink-0 mt-0.5 text-green-600" />
                  }
                  <div>
                    <p className={`font-bold text-lg ${RISK_TEXT[result.misclassification_risk]}`}>
                      {result.overpayment_likely ? 'Potential Overpayment Detected' : 'Classification Looks Correct'}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">{result.ai_analysis}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${RISK_TEXT[result.misclassification_risk]} bg-white border ml-3 flex-shrink-0`}>
                  {result.misclassification_risk} risk
                </span>
              </div>
            </div>

            {/* Supplier warning */}
            {result.supplier_bias_warning && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
                <p className="text-sm text-yellow-800">
                  <strong>Supplier Bias Warning:</strong> Your supplier provided this code.
                  Suppliers have no incentive to minimize your import duties — and may favor codes that simplify their paperwork.
                  Always verify independently.
                </p>
              </div>
            )}

            {/* Code comparison */}
            <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
              <h3 className="font-semibold text-brand-navy mb-4">Code Comparison</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                  <p className="text-xs text-gray-500 uppercase mb-2">Current Code</p>
                  <p className="font-mono text-xl font-bold text-gray-700">{result.current_code}</p>
                  <p className="text-sm text-gray-500 mt-1">Est. rate: {result.current_estimated_rate}%</p>
                </div>
                {result.ai_recommended_code && (
                  <div className="p-4 bg-green-50 rounded-xl border border-green-200">
                    <p className="text-xs text-green-600 uppercase mb-2">AI Recommended</p>
                    <p className="font-mono text-xl font-bold text-green-700">{result.ai_recommended_code}</p>
                    <p className="text-sm text-green-600 mt-1">Est. rate: {result.ai_recommended_rate}%</p>
                  </div>
                )}
              </div>
            </div>

            {/* Savings potential */}
            {result.alternative_codes.length > 0 && (
              <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
                <h3 className="font-semibold text-brand-navy mb-4 flex items-center space-x-2">
                  <TrendingDown size={16} className="text-green-500" />
                  <span>Alternative Classifications</span>
                </h3>
                <div className="space-y-3">
                  {result.alternative_codes.map((alt, i) => (
                    <div key={i} className="p-4 bg-green-50 border border-green-200 rounded-xl">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-mono font-bold text-green-800">{alt.code}</p>
                        <span className="text-sm font-medium text-green-700">{alt.estimated_rate}% rate</span>
                      </div>
                      <p className="text-sm text-gray-600">{alt.description}</p>
                      {alt.annual_savings && alt.annual_savings > 0 && (
                        <p className="text-sm font-semibold text-green-700 mt-2">
                          Potential annual savings: ${alt.annual_savings.toLocaleString()}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-400 mt-3">
                  Note: HTS classification must be based on accurate product description. Consult a licensed customs broker before changing.
                </p>
              </div>
            )}
            <div className="flex items-center justify-end gap-3 mt-2">
              <SaveAnalysisButton
                toolType="hts_audit"
                title={`HTS Audit — ${form.current_hts_code || 'unknown'}`}
                resultData={result}
                formData={form}
              />
              <ComplianceExportButton reportType="hts_audit" title="HTS Code Audit Report" data={result} metadata={{ hts_code: form.current_hts_code, product_description: form.product_description }} />
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
