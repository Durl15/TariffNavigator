import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './index.css'
import AdminLayout from './components/AdminLayout'
import Dashboard from './pages/admin/Dashboard'
import Users from './pages/admin/Users'
import Organizations from './pages/admin/Organizations'
import AuditLogs from './pages/admin/AuditLogs'

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
  
  // Autocomplete states
  const [searchQuery, setSearchQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [searchLoading, setSearchLoading] = useState(false)

  // Fetch autocomplete suggestions
  const fetchSuggestions = async (query) => {
    if (query.length < 2) {
      setSuggestions([])
      return
    }
    setSearchLoading(true)
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiUrl}/tariff/autocomplete?query=${query}&country=${country}`)
      const data = await response.json()
      setSuggestions(data)
    } catch (error) {
      console.error('Error fetching suggestions:', error)
    }
    setSearchLoading(false)
  }

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchSuggestions(searchQuery)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery, country])

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
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

      // Calculate tariff with currency conversion
      const calcResponse = await fetch(
        `${apiUrl}/tariff/calculate-with-currency?hs_code=${hsCode}&country=${country}&value=${value}&from_currency=USD&to_currency=${currency}`,
        { method: 'POST' }
      )

      if (!calcResponse.ok) {
        const err = await calcResponse.json()
        throw new Error(err.detail || 'Calculation failed')
      }

      const calcData = await calcResponse.json()
      setResult(calcData)
      setExchangeRate(calcData.exchange_rate)

      // Check FTA
      const originCountry = prompt("Enter origin country code (e.g., JP, US, DE, VN):") || "US"
      const ftaResponse = await fetch(
        `${apiUrl}/tariff/fta-check?hs_code=${hsCode}&origin_country=${originCountry}&dest_country=${country}`
      )
      const ftaData = await ftaResponse.json()
      setFtaResult(ftaData)

    } catch (error) {
      console.error('Error:', error)
      setError(error.message || 'Error calculating tariff')
    }
    setLoading(false)
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

      {result && (
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <div className="mb-4 pb-2 border-b">
            <h3 className="font-bold text-lg">{result.description}</h3>
            <p className="text-gray-500 text-sm">HS: {result.hs_code} | Country: {result.country}</p>
            {exchangeRate && currency !== 'USD' && (
              <p className="text-xs text-blue-600 mt-1">
                Exchange Rate: 1 USD = {exchangeRate} {currency}
              </p>
            )}
          </div>
          
          <div className="space-y-2 mb-4">
            <div className="flex justify-between">
              <span className="text-gray-600">CIF Value</span>
              <div className="text-right">
                <div className="font-medium">{fmt(result.converted_calculation.cif_value)}</div>
                {currency !== 'USD' && (
                  <div className="text-xs text-gray-500">{fmtUSD(result.calculation.cif_value)}</div>
                )}
              </div>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Customs Duty ({result.rates.mfn}%)</span>
              <span className="font-medium">{fmt(result.converted_calculation.customs_duty)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">VAT ({result.rates.vat}%)</span>
              <span className="font-medium">{fmt(result.converted_calculation.vat)}</span>
            </div>
            {result.converted_calculation.consumption_tax > 0 && (
              <div className="flex justify-between text-red-600">
                <span>Consumption Tax ({result.rates.consumption}%)</span>
                <span className="font-medium">{fmt(result.converted_calculation.consumption_tax)}</span>
              </div>
            )}
          </div>

          <div className="pt-2 border-t flex justify-between items-center">
            <span className="font-bold text-lg">Total Cost</span>
            <div className="text-right">
              <span className="text-2xl font-bold text-green-600">
                {getCurrencyDisplay()}{result.converted_calculation.total_cost.toLocaleString()}
              </span>
              {currency !== 'USD' && (
                <div className="text-xs text-gray-500">{fmtUSD(result.calculation.total_cost)}</div>
              )}
            </div>
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
    </div>
  )
}

// Main calculator page component
function CalculatorPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-blue-600 mb-2">Tariff Navigator</h1>
        <p className="text-gray-600 mb-8">AI-powered tariff calculator with FTA & multi-currency support</p>

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