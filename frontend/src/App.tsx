import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import toast from 'react-hot-toast'
import './index.css'
import AdminLayout from './components/AdminLayout'
import Dashboard from './pages/admin/Dashboard'
import Users from './pages/admin/Users'
import Organizations from './pages/admin/Organizations'
import AuditLogs from './pages/admin/AuditLogs'
import Login from './pages/Login'
import UserDashboard from './pages/Dashboard'
import ComparisonPage from './pages/ComparisonPage'
import FTAWizardPage from './pages/FTAWizardPage'
import CatalogsPage from './pages/CatalogsPage'
import CatalogImpactPage from './pages/CatalogImpactPage'
import NotificationsPage from './pages/NotificationsPage'
import WatchlistsPage from './pages/WatchlistsPage'
import Pricing from './pages/Pricing'
import SubscriptionSuccess from './pages/SubscriptionSuccess'
import Billing from './pages/Billing'
import { exportPDF, downloadBlob, getCalculation } from './services/api'
import SearchFilters, { type SearchFilterValues } from './components/SearchFilters'
import SavedCalculationsSidebar from './components/SavedCalculationsSidebar'
import SaveCalculationModal from './components/SaveCalculationModal'
import NotificationBell from './components/NotificationBell'
import { Bookmark, Save } from 'lucide-react'

// COST CALCULATOR COMPONENT - With Autocomplete, FTA, and Currency
function CostCalculator() {
  const [country, setCountry] = useState('CN')
  const [currency, setCurrency] = useState('USD')
  const [hsCode, setHsCode] = useState('')
  const [value, setValue] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [ftaResult, setFtaResult] = useState(null)
  const [exchangeRate, setExchangeRate] = useState(null)
  const [isPdfExporting, setIsPdfExporting] = useState(false)

  // Saved calculations states
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [saveModalOpen, setSaveModalOpen] = useState(false)

  // Autocomplete states
  const [searchQuery, setSearchQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [searchLoading, setSearchLoading] = useState(false)

  // Filter states
  const [searchFilters, setSearchFilters] = useState<SearchFilterValues>({
    category: null,
    minRate: null,
    maxRate: null,
    sortBy: 'relevance'
  })

  // Fetch autocomplete suggestions with filters
  const fetchSuggestions = async (query) => {
    if (query.length < 2) {
      setSuggestions([])
      return
    }
    setSearchLoading(true)
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'https://tariffnavigator-backend.onrender.com/api/v1'

      // Build query params with filters
      const params = new URLSearchParams({
        query,
        country
      })

      if (searchFilters.category) params.append('category', searchFilters.category)
      if (searchFilters.minRate !== null) params.append('min_rate', searchFilters.minRate.toString())
      if (searchFilters.maxRate !== null) params.append('max_rate', searchFilters.maxRate.toString())
      if (searchFilters.sortBy) params.append('sort_by', searchFilters.sortBy)

      const response = await fetch(`${apiUrl}/tariff/autocomplete?${params.toString()}`)
      const data = await response.json()
      setSuggestions(data)
    } catch (error) {
      console.error('Error fetching suggestions:', error)
    }
    setSearchLoading(false)
  }

  // Debounce search - refetch when query, country, or filters change
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchSuggestions(searchQuery)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery, country, searchFilters])

  const selectSuggestion = (suggestion) => {
    setHsCode(suggestion.code)
    setSearchQuery(suggestion.description)
    setShowSuggestions(false)
  }

  const calculate = async () => {
    setLoading(true)
    setError('')
    setFtaResult(null)
    setExchangeRate(null)

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'https://tariffnavigator-backend.onrender.com/api/v1'

      // Calculate tariff with currency conversion
      const calcResponse = await fetch(
        `${apiUrl}/tariff/calculate?hs_code=${hsCode}&country=${country}&value=${value}&from_currency=USD&to_currency=${currency}`,
        { method: 'POST' }
      )

      if (!calcResponse.ok) {
        const err = await calcResponse.json()
        throw new Error(err.detail || 'Calculation failed')
      }

      const calcData = await calcResponse.json()
      console.log('API Response:', calcData)
      console.log('Selected currency:', currency)
      console.log('Has converted_calculation:', !!calcData.converted_calculation)
      setResult(calcData)

      // Set exchange rate if conversion happened
      if (calcData.exchange_rate && currency !== 'USD') {
        setExchangeRate(calcData.exchange_rate)
      }

    } catch (error) {
      console.error('Error:', error)
      setError(error.message || 'Error calculating tariff')
    }
    setLoading(false)
  }

  const handleExportPDF = async () => {
    if (!result) return

    setIsPdfExporting(true)
    try {
      const pdfData = {
        hs_code: result.hs_code,
        country: result.country,
        description: result.description,
        rates: result.rates,
        calculation: result.calculation,
        origin_country: result.origin_country,
        destination_country: result.destination_country,
        original_currency: result.original_currency,
        exchange_rate: result.exchange_rate,
        converted_calculation: result.converted_calculation
      }

      const blob = await exportPDF(pdfData)
      const timestamp = new Date().toISOString().split('T')[0]
      downloadBlob(blob, `tariff_report_${result.hs_code}_${timestamp}.pdf`)
      toast.success('PDF exported successfully!')
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Failed to export PDF. Please try again.')
    } finally {
      setIsPdfExporting(false)
    }
  }

  const loadCalculation = async (calcId: string) => {
    try {
      const calc = await getCalculation(calcId)
      // Populate form fields
      setCountry(calc.destination_country)
      setCurrency(calc.currency)
      setHsCode(calc.hs_code)
      setValue(calc.cif_value.toString())
      setSearchQuery(calc.product_description || '')
      setSidebarOpen(false)
      toast.success('Calculation loaded')
    } catch (error) {
      console.error('Load failed:', error)
      toast.error('Failed to load calculation')
    }
  }

  const fmt = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: currency }).format(val)
  const fmtUSD = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)

  const getCurrencyDisplay = () => {
    const displays = { 
      USD: '$', 
      CNY: 'CN¥',
      EUR: '€', 
      JPY: 'JP¥',
      GBP: '£', 
      KRW: '₩' 
    }
    return displays[currency] || '$'
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Tariff Calculator</h2>

      {/* Search Filters */}
      <SearchFilters
        onFilterChange={(filters) => {
          setSearchFilters(filters)
          // Trigger new search with updated filters
          if (searchQuery.length >= 2) {
            fetchSuggestions(searchQuery)
          }
        }}
        initialFilters={searchFilters}
      />

      <div className="grid grid-cols-1 gap-4 mb-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Destination</label>
            <select 
              className="w-full p-2 border rounded"
              value={country}
              onChange={(e) => {
                setCountry(e.target.value)
                setHsCode('')
                setSearchQuery('')
                setSuggestions([])
              }}
            >
              <option value="CN">China (CN)</option>
              <option value="EU">European Union (EU)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
            <select 
              className="w-full p-2 border rounded"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
            >
              <option value="USD">USD ($) - US Dollar</option>
              <option value="CNY">CNY (CN¥) - Chinese Yuan</option>
              <option value="EUR">EUR (€) - Euro</option>
              <option value="JPY">JPY (JP¥) - Japanese Yen</option>
              <option value="GBP">GBP (£) - British Pound</option>
              <option value="KRW">KRW (₩) - Korean Won</option>
            </select>
          </div>
        </div>

        <div className="relative">
          <label className="block text-sm font-medium text-gray-700 mb-1">Search Product or HS Code</label>
          <input 
            type="text" 
            placeholder="Type 'car' or '8703'..." 
            className="w-full p-2 border rounded"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              setShowSuggestions(true)
            }}
            onFocus={() => setShowSuggestions(true)}
          />
          {searchLoading && <span className="absolute right-3 top-8 text-gray-400">Loading...</span>}
          
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute z-10 w-full bg-white border rounded-md shadow-lg mt-1 max-h-60 overflow-auto">
              {suggestions.map((s, idx) => (
                <div 
                  key={idx}
                  className="p-3 hover:bg-gray-100 cursor-pointer border-b last:border-b-0"
                  onClick={() => selectSuggestion(s)}
                >
                  <div className="font-medium text-blue-600">{s.code}</div>
                  <div className="text-sm text-gray-600">{s.description}</div>
                  <div className="text-xs text-gray-400">Duty: {s.mfn_rate}%</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Selected HS Code</label>
          <input 
            type="text" 
            className="w-full p-2 border rounded bg-gray-50"
            value={hsCode}
            readOnly
            placeholder="Select from search above"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">CIF Value (USD)</label>
          <input 
            type="number" 
            placeholder="50000" 
            className="w-full p-2 border rounded"
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
        </div>
      </div>

      <button 
        onClick={calculate} 
        disabled={loading || !hsCode || !value}
        className="w-full bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 disabled:opacity-50"
      >
        {loading ? 'Calculating...' : `Calculate in ${currency}`}
      </button>

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 rounded">
          {error}
        </div>
      )}

      {result && (result.calculation || result.converted_calculation) && (
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <div className="mb-4 pb-2 border-b">
            <h3 className="font-bold text-lg">{result.description}</h3>
            <p className="text-gray-500 text-sm">HS: {result.hs_code} | Country: {result.country}</p>
            {exchangeRate && currency !== 'USD' && (
              <p className="text-xs text-blue-600 mt-1">
                Exchange Rate: 1 USD = {exchangeRate.toFixed(4)} {currency}
              </p>
            )}
          </div>

          <div className="space-y-2 mb-4">
            <div className="flex justify-between">
              <span className="text-gray-600">CIF Value</span>
              <span className="font-medium">{fmt((result.converted_calculation || result.calculation).cif_value)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Customs Duty ({result.rates?.mfn || 0}%)</span>
              <span className="font-medium">{fmt((result.converted_calculation || result.calculation).customs_duty)}</span>
            </div>
            {(result.converted_calculation || result.calculation).vat && (result.converted_calculation || result.calculation).vat > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600">VAT ({result.rates?.vat || 0}%)</span>
                <span className="font-medium">{fmt((result.converted_calculation || result.calculation).vat)}</span>
              </div>
            )}
            {(result.converted_calculation || result.calculation).consumption_tax && (result.converted_calculation || result.calculation).consumption_tax > 0 && (
              <div className="flex justify-between text-red-600">
                <span>Consumption Tax ({result.rates?.consumption || 0}%)</span>
                <span className="font-medium">{fmt((result.converted_calculation || result.calculation).consumption_tax)}</span>
              </div>
            )}
          </div>

          <div className="pt-2 border-t flex justify-between items-center">
            <span className="font-bold text-lg">Total Cost</span>
            <span className="text-2xl font-bold text-green-600">
              {fmt((result.converted_calculation || result.calculation).total_cost)}
            </span>
          </div>

          {/* Export Actions */}
          <div className="flex gap-2 mt-4">
            <button
              onClick={handleExportPDF}
              disabled={isPdfExporting}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isPdfExporting ? (
                <>
                  <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Generating...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Export PDF
                </>
              )}
            </button>

            <button
              onClick={() => setSaveModalOpen(true)}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
            >
              <Save size={18} />
              Save Calculation
            </button>
          </div>
        </div>
      )}

      {ftaResult && (
        <div className={`mt-4 p-4 rounded ${ftaResult.eligible ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}`}>
          <h4 className="font-bold mb-2">FTA Check: {ftaResult.origin_country} → {ftaResult.destination_country}</h4>
          {ftaResult.eligible ? (
            <div>
              <p className="text-green-700 font-medium">✅ Eligible for {ftaResult.fta_name}!</p>
              <div className="mt-2 space-y-1 text-sm">
                <p>Standard rate: <span className="line-through">{ftaResult.standard_rate}%</span></p>
                <p>Preferential rate: <span className="font-bold text-green-600">{ftaResult.preferential_rate}%</span></p>
                <p className="text-lg font-bold text-green-600">You save: {ftaResult.savings_percent}%</p>
              </div>
              <div className="mt-3 text-sm bg-white p-2 rounded">
                <p className="font-medium text-gray-700">Required documents:</p>
                <ul className="list-disc ml-5 mt-1 text-gray-600">
                  {ftaResult.requirements.map((req, i) => <li key={i}>{req}</li>)}
                </ul>
              </div>
            </div>
          ) : (
            <div>
              <p className="text-gray-600">❌ No FTA benefits available for this trade route.</p>
              <p className="text-sm text-gray-500 mt-1">Standard rate applies: {ftaResult.standard_rate}%</p>
            </div>
          )}
        </div>
      )}

      {/* Floating Saved Calculations Button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="fixed bottom-6 right-6 bg-indigo-600 text-white p-4 rounded-full shadow-lg hover:bg-indigo-700 transition-all hover:scale-110 z-40"
        aria-label="Saved Calculations"
      >
        <Bookmark size={24} />
      </button>

      {/* Saved Calculations Sidebar */}
      <SavedCalculationsSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onLoadCalculation={loadCalculation}
      />

      {/* Save Calculation Modal */}
      <SaveCalculationModal
        isOpen={saveModalOpen}
        onClose={() => setSaveModalOpen(false)}
        calculationData={result}
      />
    </div>
  )
}

// Main calculator page component
function CalculatorPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-3xl font-bold text-blue-600">Tariff Navigator</h1>
          <div className="flex items-center gap-4">
            <NotificationBell />
            <a
              href="/login"
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-medium"
            >
              Login
            </a>
            <a
              href="/dashboard"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              Dashboard
            </a>
          </div>
        </div>
        <p className="text-gray-600 mb-6">AI-powered tariff calculator with multi-currency support</p>
        <p className="text-xs text-gray-400 mb-4">v2.0.3 - Currency conversion enabled</p>

        <div className="bg-white rounded-lg shadow-md p-6">
          <CostCalculator />
        </div>
      </div>
    </div>
  )
}

// MAIN APP
function App() {
  return (
    <Router>
      <Routes>
        {/* Main calculator route */}
        <Route path="/" element={<CalculatorPage />} />

        {/* User dashboard route */}
        <Route path="/dashboard" element={<UserDashboard />} />

        {/* Comparison route */}
        <Route path="/comparison" element={<ComparisonPage />} />

        {/* FTA Wizard route */}
        <Route path="/fta-wizard" element={<FTAWizardPage />} />

        {/* Catalog routes */}
        <Route path="/catalogs" element={<CatalogsPage />} />
        <Route path="/catalogs/:catalogId/impact" element={<CatalogImpactPage />} />

        {/* Notification & Watchlist routes */}
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/watchlists" element={<WatchlistsPage />} />

        {/* Billing & Subscription routes */}
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/billing" element={<Billing />} />
        <Route path="/subscription/success" element={<SubscriptionSuccess />} />

        {/* Login route */}
        <Route path="/login" element={<Login />} />

        {/* Admin routes */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="users" element={<Users />} />
          <Route path="organizations" element={<Organizations />} />
          <Route path="audit-logs" element={<AuditLogs />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App