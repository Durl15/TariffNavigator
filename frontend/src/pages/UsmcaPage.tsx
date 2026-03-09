import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileCheck, CheckCircle, XCircle, ArrowLeft, Info } from 'lucide-react'
import toast from 'react-hot-toast'
import Navigation from '../components/Navigation'
import { ComplianceExportButton } from '../components/ComplianceExportButton'
import { SaveAnalysisButton } from '../components/SaveAnalysisButton'
import { api } from '../services/api'

interface UsmcaResult {
  origin_country: string
  usmca_eligible: boolean
  confidence: string
  reason: string
  missing_requirements: string[]
  required_docs: string[]
  savings_if_qualified: number | null
  standard_rate_estimate: number
  ai_analysis: string
}

export default function UsmcaPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<UsmcaResult | null>(null)
  const [form, setForm] = useState({
    hts_code: '',
    product_description: '',
    origin_country: 'MX',
    us_components_percent: '',
    mexico_canada_labor_percent: '',
    china_components_percent: '',
    annual_import_value: '',
  })

  const isAuthenticated = !!localStorage.getItem('token')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.hts_code || !form.product_description) return
    setLoading(true)
    try {
      const res = await api.post('/compliance/usmca-check', {
        hts_code: form.hts_code,
        product_description: form.product_description,
        origin_country: form.origin_country,
        us_components_percent: form.us_components_percent ? parseFloat(form.us_components_percent) : undefined,
        mexico_canada_labor_percent: form.mexico_canada_labor_percent ? parseFloat(form.mexico_canada_labor_percent) : undefined,
        china_components_percent: form.china_components_percent ? parseFloat(form.china_components_percent) : undefined,
        annual_import_value: form.annual_import_value ? parseFloat(form.annual_import_value) : undefined,
      })
      setResult(res.data)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Analysis failed. Please try again.')
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
              <FileCheck className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">USMCA Qualification Checker</h1>
              <p className="text-blue-200 text-sm mt-0.5">Find out if your Mexico/Canada goods qualify for 0% duty</p>
            </div>
          </div>
        </div>

        {/* Info banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
          <div className="flex items-start space-x-2">
            <Info size={16} className="text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-blue-800">
              USMCA requires 75%+ North American content for most goods. Missing a Certificate of Origin means
              paying MFN duties you legally don't owe. With 2026 renegotiation pending, verifying eligibility now is critical.
            </p>
          </div>
        </div>

        {/* Form */}
        <div className="card p-6 mb-6">
          <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Origin Country</label>
              <select
                value={form.origin_country}
                onChange={e => setForm(f => ({ ...f, origin_country: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              >
                <option value="MX">Mexico (MX)</option>
                <option value="CA">Canada (CA)</option>
              </select>
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Product Description *</label>
              <input
                required
                type="text"
                placeholder="e.g. automotive brake pads, steel fasteners"
                value={form.product_description}
                onChange={e => setForm(f => ({ ...f, product_description: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Annual Import Value ($)</label>
              <input
                type="number"
                placeholder="e.g. 300000"
                value={form.annual_import_value}
                onChange={e => setForm(f => ({ ...f, annual_import_value: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div />

            {/* Component breakdown (optional) */}
            <div className="sm:col-span-2">
              <p className="text-sm font-medium text-gray-700 mb-3">Content Origin Breakdown (optional but improves accuracy)</p>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">US Content %</label>
                  <input
                    type="number"
                    min="0" max="100"
                    placeholder="40"
                    value={form.us_components_percent}
                    onChange={e => setForm(f => ({ ...f, us_components_percent: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">MX/CA Content %</label>
                  <input
                    type="number"
                    min="0" max="100"
                    placeholder="40"
                    value={form.mexico_canada_labor_percent}
                    onChange={e => setForm(f => ({ ...f, mexico_canada_labor_percent: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">China Content %</label>
                  <input
                    type="number"
                    min="0" max="100"
                    placeholder="20"
                    value={form.china_components_percent}
                    onChange={e => setForm(f => ({ ...f, china_components_percent: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                  />
                </div>
              </div>
            </div>

            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-brand-blue text-white py-3 rounded-lg font-medium text-sm hover:bg-brand-blue-dark transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {loading ? <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <FileCheck size={16} />}
                <span>{loading ? 'Checking...' : 'Check USMCA Eligibility'}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Eligibility verdict */}
            <div className={`rounded-xl border p-5 ${result.usmca_eligible ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
              <div className="flex items-center space-x-3 mb-2">
                {result.usmca_eligible
                  ? <CheckCircle size={24} className="text-green-600 flex-shrink-0" />
                  : <XCircle size={24} className="text-red-500 flex-shrink-0" />
                }
                <div>
                  <p className="font-bold text-lg text-brand-navy">
                    {result.usmca_eligible ? 'Likely USMCA Eligible' : 'May Not Qualify for USMCA'}
                  </p>
                  <p className="text-xs text-gray-500">Confidence: {result.confidence}</p>
                </div>
                {result.savings_if_qualified && (
                  <div className="ml-auto text-right">
                    <p className="text-2xl font-bold text-green-600">${result.savings_if_qualified.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">annual savings</p>
                  </div>
                )}
              </div>
              <p className="text-sm text-gray-700">{result.ai_analysis}</p>
            </div>

            {/* Missing requirements */}
            {result.missing_requirements.filter(Boolean).length > 0 && (
              <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
                <h3 className="font-semibold text-brand-navy mb-3">Issues to Address</h3>
                <ul className="space-y-2">
                  {result.missing_requirements.filter(Boolean).map((req, i) => (
                    <li key={i} className="flex items-start space-x-2 text-sm">
                      <XCircle size={14} className="text-red-400 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{req}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Required docs */}
            <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
              <h3 className="font-semibold text-brand-navy mb-3">Required Documentation</h3>
              <ul className="space-y-2">
                {result.required_docs.map((doc, i) => (
                  <li key={i} className="flex items-start space-x-2 text-sm">
                    <CheckCircle size={14} className="text-brand-teal mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{doc}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p className="text-xs text-blue-700">
                <strong>USMCA 2026:</strong> The agreement is up for renegotiation in July 2026.
                Secure your Certificates of Origin now and monitor changes via your Watchlist.
              </p>
            </div>
            <div className="flex items-center justify-end gap-3 mt-2">
              <SaveAnalysisButton
                toolType="usmca"
                title={`USMCA Check — ${form.product_description || 'Product'}`}
                resultData={result}
                formData={form}
              />
              <ComplianceExportButton reportType="usmca" title="USMCA Eligibility Report" data={result} metadata={{ product_description: form.product_description }} />
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
