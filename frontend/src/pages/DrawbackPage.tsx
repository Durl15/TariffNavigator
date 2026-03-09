import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Banknote, CheckCircle, XCircle, ArrowLeft, ClipboardList } from 'lucide-react'
import toast from 'react-hot-toast'
import Navigation from '../components/Navigation'
import { api } from '../services/api'
import { ComplianceExportButton } from '../components/ComplianceExportButton'
import { SaveAnalysisButton } from '../components/SaveAnalysisButton'

interface DrawbackResult {
  eligible: boolean
  drawback_type: string | null
  potential_refund: number
  refund_percent: number
  deadline_description: string
  form_required: string
  steps: string[]
  ai_analysis: string
  annual_unclaimed_estimate: number | null
}

export default function DrawbackPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DrawbackResult | null>(null)
  const [form, setForm] = useState({
    hts_code: '',
    country_of_origin: 'CN',
    import_date: '',
    duty_paid: '',
    product_description: '',
    plans_to_export: false,
    plans_to_manufacture: false,
  })

  const isAuthenticated = !!localStorage.getItem('token')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.duty_paid || !form.hts_code) return
    setLoading(true)
    try {
      const res = await api.post('/compliance/drawback', {
        hts_code: form.hts_code,
        country_of_origin: form.country_of_origin,
        import_date: form.import_date || undefined,
        duty_paid: parseFloat(form.duty_paid),
        product_description: form.product_description || undefined,
        plans_to_export: form.plans_to_export,
        plans_to_manufacture: form.plans_to_manufacture,
      })
      setResult(res.data)
    } catch {
      toast.error('Analysis failed. Please try again.')
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
              <Banknote className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Duty Drawback Finder</h1>
              <p className="text-blue-200 text-sm mt-0.5">Recover up to 99% of duties you've already paid</p>
            </div>
          </div>
        </div>

        {/* Info banner */}
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
          <p className="text-sm text-green-800">
            <strong>Did you know?</strong> CBP estimates billions in duty drawback goes unclaimed every year.
            If you re-export goods or use imported materials in manufacturing, you may qualify for a 99% refund of duties paid.
          </p>
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
              <label className="block text-sm font-medium text-gray-700 mb-1">Country of Origin</label>
              <select
                value={form.country_of_origin}
                onChange={e => setForm(f => ({ ...f, country_of_origin: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              >
                <option value="CN">China</option>
                <option value="MX">Mexico</option>
                <option value="CA">Canada</option>
                <option value="VN">Vietnam</option>
                <option value="IN">India</option>
                <option value="EU">European Union</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Duties Paid ($) *</label>
              <input
                required
                type="number"
                placeholder="e.g. 12500"
                value={form.duty_paid}
                onChange={e => setForm(f => ({ ...f, duty_paid: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Import Date (optional)</label>
              <input
                type="date"
                value={form.import_date}
                onChange={e => setForm(f => ({ ...f, import_date: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Product Description</label>
              <input
                type="text"
                placeholder="e.g. laptop computers, steel pipe fittings"
                value={form.product_description}
                onChange={e => setForm(f => ({ ...f, product_description: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div className="sm:col-span-2 space-y-3">
              <p className="text-sm font-medium text-gray-700">What do you do with these goods?</p>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.plans_to_export}
                  onChange={e => setForm(f => ({ ...f, plans_to_export: e.target.checked }))}
                  className="rounded border-gray-300 text-brand-blue focus:ring-brand-blue"
                />
                <span className="text-sm text-gray-700">Re-export these goods (unused merchandise drawback)</span>
              </label>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.plans_to_manufacture}
                  onChange={e => setForm(f => ({ ...f, plans_to_manufacture: e.target.checked }))}
                  className="rounded border-gray-300 text-brand-blue focus:ring-brand-blue"
                />
                <span className="text-sm text-gray-700">Use in U.S. manufacturing (manufacturing drawback)</span>
              </label>
            </div>

            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 text-white py-3 rounded-lg font-medium text-sm hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {loading ? <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <Banknote size={16} />}
                <span>{loading ? 'Analyzing...' : 'Find My Refund'}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Eligibility */}
            <div className={`rounded-xl border p-5 flex items-start space-x-4 ${result.eligible ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
              {result.eligible
                ? <CheckCircle size={24} className="text-green-600 flex-shrink-0 mt-0.5" />
                : <XCircle size={24} className="text-gray-400 flex-shrink-0 mt-0.5" />
              }
              <div>
                <p className="font-bold text-lg text-brand-navy">
                  {result.eligible
                    ? `$${result.potential_refund.toLocaleString()} potential refund`
                    : 'Not eligible with current information'
                  }
                </p>
                {result.eligible && (
                  <p className="text-sm text-gray-600 mt-1">
                    {result.refund_percent}% refund via <strong>{result.drawback_type?.replace(/_/g, ' ')}</strong>
                  </p>
                )}
                <p className="text-sm text-gray-600 mt-2">{result.ai_analysis}</p>
              </div>
            </div>

            {result.eligible && (
              <>
                {/* KPIs */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-white rounded-xl border border-gray-100 shadow-card p-4 text-center">
                    <p className="text-xs text-gray-500 uppercase mb-1">Refund Rate</p>
                    <p className="text-2xl font-bold text-green-600">{result.refund_percent}%</p>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-100 shadow-card p-4 text-center">
                    <p className="text-xs text-gray-500 uppercase mb-1">This Shipment</p>
                    <p className="text-2xl font-bold text-brand-navy">${result.potential_refund.toLocaleString()}</p>
                  </div>
                  {result.annual_unclaimed_estimate && (
                    <div className="bg-white rounded-xl border border-gray-100 shadow-card p-4 text-center">
                      <p className="text-xs text-gray-500 uppercase mb-1">Annual Est.</p>
                      <p className="text-2xl font-bold text-green-600">${(result.annual_unclaimed_estimate / 12 * 12 / 1000).toFixed(0)}k</p>
                    </div>
                  )}
                </div>

                {/* Filing steps */}
                <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
                  <div className="flex items-center space-x-2 mb-4">
                    <ClipboardList size={18} className="text-brand-blue" />
                    <h3 className="font-semibold text-brand-navy">How to File — {result.form_required}</h3>
                  </div>
                  <ol className="space-y-2">
                    {result.steps.map((step, i) => (
                      <li key={i} className="flex items-start space-x-3">
                        <span className="w-6 h-6 rounded-full bg-brand-navy text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</span>
                        <span className="text-sm text-gray-700">{step}</span>
                      </li>
                    ))}
                  </ol>
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-xs text-yellow-800"><strong>Deadline:</strong> {result.deadline_description}</p>
                  </div>
                </div>
              </>
            )}
          <div className="flex items-center justify-end gap-3 mt-2">
            <SaveAnalysisButton
              toolType="drawback"
              title={`Drawback Analysis — HTS ${form.hts_code || 'unknown'}`}
              resultData={result}
              formData={form}
            />
            <ComplianceExportButton
              reportType="drawback"
              title="Duty Drawback Analysis"
              data={result}
              metadata={{ hts_code: form.hts_code, product_description: form.product_description }}
            />
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
