import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { Zap, ArrowLeft, TrendingUp, TrendingDown, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react'
import toast from 'react-hot-toast'
import Navigation from '../components/Navigation'
import { TierGate } from '../components/UpgradePrompt'
import { ComplianceExportButton } from '../components/ComplianceExportButton'
import { SaveAnalysisButton } from '../components/SaveAnalysisButton'
import { api, getCatalogs, type CatalogListResponse } from '../services/api'
import { usePageTitle } from '../hooks/usePageTitle'
import Footer from '../components/Footer'



interface Preset {
  id: string
  name: string
  description: string
  icon: string
  color: string
}

interface ItemImpact {
  sku: string
  product_name: string
  country: string
  annual_volume: number
  cogs: number
  current_tariff_rate: number
  scenario_tariff_rate: number
  current_annual_tariff: number
  scenario_annual_tariff: number
  delta: number
  margin_impact_pct: number
}

interface ScenarioResult {
  scenario_name: string
  scenario_description: string
  current_total_tariff: number
  scenario_total_tariff: number
  total_delta: number
  total_delta_pct: number
  items_worse: number
  items_better: number
  items_unchanged: number
  item_impacts: ItemImpact[]
  ai_executive_summary: string
  recommended_actions: string[]
}

const COLOR_MAP: Record<string, string> = {
  red: 'border-red-200 bg-red-50',
  green: 'border-green-200 bg-green-50',
  orange: 'border-orange-200 bg-orange-50',
  yellow: 'border-yellow-200 bg-yellow-50',
  blue: 'border-blue-200 bg-blue-50',
}

export default function ScenarioPage() {
  usePageTitle('Scenario Planner')
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ScenarioResult | null>(null)
  const [selectedPreset, setSelectedPreset] = useState<string>('')
  const [showItems, setShowItems] = useState(false)
  const [form, setForm] = useState({
    catalog_id: '',
    annual_import_value: '',
    country_of_origin: 'CN',
    // custom overrides
    custom_cn: '',
    custom_mx: '',
    custom_ca: '',
    custom_vn: '',
  })

  const isAuthenticated = !!localStorage.getItem('token')

  const { data: presetsData } = useQuery<Preset[]>({
    queryKey: ['scenario-presets'],
    queryFn: () => api.get('/scenarios/presets').then(r => r.data),
  })

  const { data: catalogs } = useQuery<CatalogListResponse>({
    queryKey: ['catalogs-list'],
    queryFn: () => getCatalogs(),
    enabled: isAuthenticated,
  })

  const handleRun = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedPreset && !form.custom_cn && !form.custom_mx) {
      toast.error('Select a preset scenario or enter custom rates.')
      return
    }
    setLoading(true)
    setResult(null)
    try {
      const body: any = {}

      if (selectedPreset && selectedPreset !== 'custom') {
        body.preset_id = selectedPreset
      } else {
        const overrides: Record<string, number> = {}
        if (form.custom_cn) overrides['CN'] = parseFloat(form.custom_cn) / 100
        if (form.custom_mx) overrides['MX'] = parseFloat(form.custom_mx) / 100
        if (form.custom_ca) overrides['CA'] = parseFloat(form.custom_ca) / 100
        if (form.custom_vn) overrides['VN'] = parseFloat(form.custom_vn) / 100
        body.custom_overrides = overrides
      }

      if (form.catalog_id) {
        body.catalog_id = form.catalog_id
      } else if (form.annual_import_value) {
        body.annual_import_value = parseFloat(form.annual_import_value)
        body.country_of_origin = form.country_of_origin
      } else {
        toast.error('Select a catalog or enter an annual import value.')
        setLoading(false)
        return
      }

      const res = await api.post('/scenarios/run', body, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setResult(res.data)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Scenario run failed.')
    } finally {
      setLoading(false)
    }
  }

  const chartData = result ? [
    { name: 'Current', value: result.current_total_tariff, fill: '#1E3A5F' },
    { name: 'Scenario', value: result.scenario_total_tariff, fill: result.total_delta > 0 ? '#C0392B' : '#0D9488' },
  ] : []

  const topItems = result?.item_impacts.slice(0, 10) ?? []

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
              <Zap className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Scenario Planner</h1>
              <p className="text-blue-200 text-sm mt-0.5">Model "what if" tariff changes against your real import data</p>
            </div>
          </div>
        </div>

        <TierGate requiredTier="enterprise" featureName="Scenario Planner" description="What-if scenario modeling against real catalog data requires an Enterprise subscription.">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left panel — config */}
          <div className="lg:col-span-1 space-y-4">
            <form onSubmit={handleRun} className="space-y-4">

              {/* Preset grid */}
              <div className="bg-white rounded-xl shadow-card border border-gray-100 p-5">
                <h3 className="font-semibold text-brand-navy text-sm mb-3">Select Scenario</h3>
                <div className="space-y-2">
                  {presetsData?.map(p => (
                    <button
                      type="button"
                      key={p.id}
                      onClick={() => setSelectedPreset(p.id)}
                      className={`w-full text-left p-3 rounded-lg border transition-all ${
                        selectedPreset === p.id
                          ? 'border-brand-blue bg-blue-50'
                          : 'border-gray-100 hover:border-gray-200 hover:bg-gray-50'
                      } ${COLOR_MAP[p.color] || ''}`}
                    >
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{p.icon}</span>
                        <p className="font-medium text-sm text-brand-navy">{p.name}</p>
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5 ml-7">{p.description}</p>
                    </button>
                  ))}

                  {/* Custom */}
                  <button
                    type="button"
                    onClick={() => setSelectedPreset('custom')}
                    className={`w-full text-left p-3 rounded-lg border transition-all ${
                      selectedPreset === 'custom' ? 'border-brand-blue bg-blue-50' : 'border-gray-100 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">⚙️</span>
                      <p className="font-medium text-sm text-brand-navy">Custom Rates</p>
                    </div>
                  </button>

                  {selectedPreset === 'custom' && (
                    <div className="pl-2 space-y-2 pt-1">
                      {[
                        { label: 'China (CN) %', key: 'custom_cn' },
                        { label: 'Mexico (MX) %', key: 'custom_mx' },
                        { label: 'Canada (CA) %', key: 'custom_ca' },
                        { label: 'Vietnam (VN) %', key: 'custom_vn' },
                      ].map(({ label, key }) => (
                        <div key={key}>
                          <label className="text-xs text-gray-500">{label}</label>
                          <input
                            type="number"
                            min="0" max="999"
                            placeholder="e.g. 25"
                            value={(form as any)[key]}
                            onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                            className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-brand-blue"
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Data source */}
              <div className="bg-white rounded-xl shadow-card border border-gray-100 p-5">
                <h3 className="font-semibold text-brand-navy text-sm mb-3">Apply To</h3>

                {isAuthenticated && catalogs?.catalogs?.length ? (
                  <div className="mb-3">
                    <label className="block text-xs text-gray-500 mb-1">Your Catalog</label>
                    <select
                      value={form.catalog_id}
                      onChange={e => setForm(f => ({ ...f, catalog_id: e.target.value }))}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                    >
                      <option value="">— Manual input —</option>
                      {catalogs.catalogs.map(c => (
                        <option key={c.id} value={c.id}>{c.name} ({c.total_skus} SKUs)</option>
                      ))}
                    </select>
                  </div>
                ) : null}

                {!form.catalog_id && (
                  <div className="space-y-2">
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Annual Import Value ($)</label>
                      <input
                        type="number"
                        placeholder="e.g. 500000"
                        value={form.annual_import_value}
                        onChange={e => setForm(f => ({ ...f, annual_import_value: e.target.value }))}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Country of Origin</label>
                      <select
                        value={form.country_of_origin}
                        onChange={e => setForm(f => ({ ...f, country_of_origin: e.target.value }))}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                      >
                        {['CN','MX','CA','VN','IN','KR','TW','TH','EU','JP'].map(c => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium text-sm hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {loading ? <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <Zap size={16} />}
                <span>{loading ? 'Running...' : 'Run Scenario'}</span>
              </button>
            </form>
          </div>

          {/* Right panel — results */}
          <div className="lg:col-span-2 space-y-5">
            {!result && !loading && (
              <div className="bg-white rounded-xl border border-gray-100 shadow-card flex flex-col items-center justify-center py-20 text-gray-400">
                <Zap size={40} className="opacity-30 mb-3" />
                <p className="text-sm">Select a scenario and run it to see impact</p>
              </div>
            )}

            {result && (
              <>
                {/* Summary KPIs */}
                <div className="bg-brand-navy text-white rounded-xl p-5">
                  <p className="text-blue-200 text-sm mb-1">{result.scenario_name}</p>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-blue-300">Current Tariffs</p>
                      <p className="text-2xl font-bold">${(result.current_total_tariff / 1000).toFixed(0)}k</p>
                    </div>
                    <div>
                      <p className="text-xs text-blue-300">Under Scenario</p>
                      <p className="text-2xl font-bold">${(result.scenario_total_tariff / 1000).toFixed(0)}k</p>
                    </div>
                    <div>
                      <p className="text-xs text-blue-300">Change</p>
                      <div className="flex items-center space-x-1">
                        {result.total_delta > 0
                          ? <TrendingUp size={18} className="text-red-400" />
                          : <TrendingDown size={18} className="text-green-400" />
                        }
                        <p className={`text-2xl font-bold ${result.total_delta > 0 ? 'text-red-400' : 'text-green-400'}`}>
                          {result.total_delta > 0 ? '+' : ''}${(result.total_delta / 1000).toFixed(0)}k
                        </p>
                      </div>
                      <p className="text-xs text-blue-300">{result.total_delta_pct.toFixed(1)}%</p>
                    </div>
                  </div>
                </div>

                {/* Chart */}
                <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
                  <h3 className="font-semibold text-brand-navy mb-4">Annual Tariff Cost Comparison</h3>
                  <ResponsiveContainer width="100%" height={160}>
                    <BarChart data={chartData} barSize={60}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                      <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 11 }} />
                      <Tooltip formatter={(v: number) => [`$${v.toLocaleString()}`, 'Tariff Cost']} />
                      <Bar dataKey="value">
                        {chartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* SKU breakdown */}
                <div className="bg-white rounded-xl shadow-card border border-gray-100 p-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <h3 className="font-semibold text-brand-navy">SKU Impact Breakdown</h3>
                      <div className="flex space-x-2 text-xs">
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded-full">{result.items_worse} worse</span>
                        <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded-full">{result.items_better} better</span>
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">{result.items_unchanged} unchanged</span>
                      </div>
                    </div>
                    {result.item_impacts.length > 5 && (
                      <button onClick={() => setShowItems(!showItems)} className="text-xs text-brand-blue flex items-center space-x-1">
                        <span>{showItems ? 'Show less' : 'Show all'}</span>
                        {showItems ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                      </button>
                    )}
                  </div>

                  <div className="divide-y divide-gray-50">
                    {(showItems ? result.item_impacts : topItems).map((item, i) => (
                      <div key={i} className="flex items-center justify-between py-2.5">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-brand-navy truncate">{item.product_name}</p>
                          <p className="text-xs text-gray-400">{item.country} · {item.current_tariff_rate}% → {item.scenario_tariff_rate}%</p>
                        </div>
                        <div className="text-right flex-shrink-0 ml-4">
                          <p className={`text-sm font-bold ${item.delta > 0 ? 'text-red-600' : item.delta < 0 ? 'text-green-600' : 'text-gray-400'}`}>
                            {item.delta > 0 ? '+' : ''}{item.delta < 0 ? '' : ''}{item.delta === 0 ? '—' : `$${Math.abs(item.delta).toLocaleString()}`}
                          </p>
                          {item.margin_impact_pct !== 0 && (
                            <p className="text-xs text-gray-400">{item.margin_impact_pct.toFixed(1)}% margin</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI summary */}
                <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-5">
                  <p className="font-semibold text-brand-navy text-sm mb-2">AI Executive Summary</p>
                  <p className="text-sm text-gray-700">{result.ai_executive_summary}</p>
                </div>

                {/* Recommended actions */}
                <div className="bg-white rounded-xl shadow-card border border-gray-100 p-5">
                  <h3 className="font-semibold text-brand-navy mb-3">Recommended Actions</h3>
                  <ul className="space-y-2">
                    {result.recommended_actions.map((action, i) => (
                      <li key={i} className="flex items-start space-x-2 text-sm">
                        <AlertTriangle size={14} className="text-brand-gold mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="flex items-center justify-end gap-3 mt-2">
                  <SaveAnalysisButton
                    toolType="scenario"
                    title={`Scenario — ${result.scenario_name}`}
                    resultData={result}
                    formData={form}
                  />
                  <ComplianceExportButton reportType="scenario" title="Scenario Analysis Report" data={result} metadata={{ preset_id: selectedPreset, scenario_name: result.scenario_name }} />
                </div>
              </>
            )}
          </div>
          </div>
        </TierGate>
      </div>
      <Footer />
    </div>
  )
}
