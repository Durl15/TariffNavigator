import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { DollarSign, AlertTriangle, CheckCircle, TrendingDown, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import Navigation from '../components/Navigation'
import { api } from '../services/api'
import { ComplianceExportButton } from '../components/ComplianceExportButton'
import { SaveAnalysisButton } from '../components/SaveAnalysisButton'
import { usePageTitle } from '../hooks/usePageTitle'


interface ForecastResult {
  shipment_value: number
  duty_rate_percent: number
  duty_due_amount: number
  due_date: string
  estimated_revenue_date: string
  cash_gap_days: number
  cash_gap_amount: number
  cash_gap_risk: string
  ai_recommendation: string
  financing_options: { name: string; description: string; typical_cost_percent: number }[]
  tariff_programs_applied: string[]
}

const RISK_COLORS: Record<string, string> = {
  high: 'text-red-600 bg-red-50 border-red-200',
  medium: 'text-yellow-700 bg-yellow-50 border-yellow-200',
  low: 'text-green-700 bg-green-50 border-green-200',
}

export default function CashFlowPage() {
  usePageTitle('Cash Flow Forecaster')
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ForecastResult | null>(null)
  const [form, setForm] = useState({
    shipment_value: '',
    hts_code: '',
    country_of_origin: 'CN',
    ship_date: '',
    payment_terms_days: '30',
    product_description: '',
  })

  const isAuthenticated = !!localStorage.getItem('token')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.shipment_value) return
    setLoading(true)
    try {
      const res = await api.post('/cashflow', {
        shipment_value: parseFloat(form.shipment_value),
        hts_code: form.hts_code || undefined,
        country_of_origin: form.country_of_origin,
        ship_date: form.ship_date || undefined,
        payment_terms_days: parseInt(form.payment_terms_days),
        product_description: form.product_description || undefined,
      })
      setResult(res.data)
    } catch {
      toast.error('Failed to generate forecast. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const chartData = result ? [
    { name: 'Shipment Value', amount: result.shipment_value, fill: '#1E3A5F' },
    { name: 'Duty Owed', amount: result.duty_due_amount, fill: '#C0392B' },
    { name: 'Cash Gap', amount: result.cash_gap_amount, fill: '#D4A843' },
  ] : []

  return (
    <div className="min-h-screen">
      <Navigation isAuthenticated={isAuthenticated} onLogout={() => { localStorage.removeItem('token'); navigate('/') }} />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="page-hero -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-6 mb-8">
          <button onClick={() => navigate('/dashboard')} className="flex items-center text-sm text-blue-300 hover:text-white mb-4 transition-colors">
            <ArrowLeft size={14} className="mr-1" /> Back to Dashboard
          </button>
          <div className="flex items-center space-x-4">
            <div className="rounded-2xl p-3 bg-white/15 backdrop-blur-sm">
              <DollarSign className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Cash Flow Forecaster</h1>
              <p className="text-blue-200 text-sm mt-0.5">Know your duty obligation before your shipment arrives</p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="card p-6 mb-6">
          <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Shipment Value (USD) *</label>
              <input
                type="number"
                required
                placeholder="e.g. 50000"
                value={form.shipment_value}
                onChange={e => setForm(f => ({ ...f, shipment_value: e.target.value }))}
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
                <option value="CN">China (CN)</option>
                <option value="MX">Mexico (MX)</option>
                <option value="CA">Canada (CA)</option>
                <option value="VN">Vietnam (VN)</option>
                <option value="IN">India (IN)</option>
                <option value="EU">European Union</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">HTS Code (optional)</label>
              <input
                type="text"
                placeholder="e.g. 8471.30"
                value={form.hts_code}
                onChange={e => setForm(f => ({ ...f, hts_code: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ship Date (optional)</label>
              <input
                type="date"
                value={form.ship_date}
                onChange={e => setForm(f => ({ ...f, ship_date: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Days Until Revenue</label>
              <input
                type="number"
                value={form.payment_terms_days}
                onChange={e => setForm(f => ({ ...f, payment_terms_days: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
              <p className="text-xs text-gray-400 mt-1">How many days until you receive payment for these goods</p>
            </div>

            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Product Description (optional)</label>
              <input
                type="text"
                placeholder="e.g. laptop computers, steel pipe fittings"
                value={form.product_description}
                onChange={e => setForm(f => ({ ...f, product_description: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
              />
            </div>

            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-brand-navy text-white py-3 rounded-lg font-medium text-sm hover:bg-brand-navy-dark transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {loading ? <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <TrendingDown size={16} />}
                <span>{loading ? 'Calculating...' : 'Forecast Cash Flow'}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Risk badge */}
            <div className={`rounded-xl border p-4 flex items-start space-x-3 ${RISK_COLORS[result.cash_gap_risk]}`}>
              {result.cash_gap_risk === 'high' ? <AlertTriangle size={20} className="flex-shrink-0 mt-0.5" /> : <CheckCircle size={20} className="flex-shrink-0 mt-0.5" />}
              <div>
                <p className="font-semibold capitalize">{result.cash_gap_risk} Cash Flow Risk</p>
                <p className="text-sm mt-0.5">{result.ai_recommendation}</p>
              </div>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Duty Rate', value: `${result.duty_rate_percent}%`, color: 'text-brand-navy' },
                { label: 'Duty Owed', value: `$${result.duty_due_amount.toLocaleString()}`, color: 'text-red-600' },
                { label: 'Cash Gap', value: `${result.cash_gap_days} days`, color: 'text-yellow-700' },
                { label: 'Gap Amount', value: `$${result.cash_gap_amount.toLocaleString()}`, color: 'text-red-600' },
              ].map(k => (
                <div key={k.label} className="bg-white rounded-xl border border-gray-100 shadow-card p-4 text-center">
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{k.label}</p>
                  <p className={`text-xl font-bold ${k.color}`}>{k.value}</p>
                </div>
              ))}
            </div>

            {/* Chart */}
            <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
              <h3 className="font-semibold text-brand-navy mb-4">Cash Flow Breakdown</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData} barSize={48}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v: number) => [`$${v.toLocaleString()}`, '']} />
                  <Bar dataKey="amount">
                    {chartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-3 text-xs text-gray-500">
                Due: {result.due_date} &nbsp;|&nbsp; Revenue estimated: {result.estimated_revenue_date}
              </div>
            </div>

            {/* Tariff programs */}
            {result.tariff_programs_applied.length > 0 && (
              <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
                <h3 className="font-semibold text-brand-navy mb-3">Tariff Programs Applied</h3>
                <div className="flex flex-wrap gap-2">
                  {result.tariff_programs_applied.map(p => (
                    <span key={p} className="px-3 py-1 bg-brand-navy text-white text-xs rounded-full">{p}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Financing options */}
            <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
              <h3 className="font-semibold text-brand-navy mb-4">Financing Options to Bridge the Gap</h3>
              <div className="space-y-3">
                {result.financing_options.map(opt => (
                  <div key={opt.name} className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-sm text-brand-navy">{opt.name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{opt.description}</p>
                    </div>
                    <span className="text-xs font-medium text-brand-blue ml-4 flex-shrink-0">~{opt.typical_cost_percent}% cost</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 mt-2">
              <SaveAnalysisButton
                toolType="cashflow"
                title={`Cash Flow — $${form.shipment_value} from ${form.country_of_origin}`}
                resultData={result}
                formData={form}
              />
              <ComplianceExportButton
                reportType="cashflow"
                title="Cash Flow Forecast Report"
                data={result}
                metadata={{ product_description: form.product_description, hts_code: form.hts_code }}
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
