import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Loader2, AlertTriangle, CheckCircle, TrendingUp, DollarSign, Package, Percent } from 'lucide-react'
import { api } from '../services/api'
import RateHistoryChart from './RateHistoryChart'

// ============================================================================
// Interfaces
// ============================================================================

interface TariffProgram {
  name: string
  authority: string
  rate: number
  amount: number
  note?: string
  savings_vs_mfn?: number
}

interface UsImportResult {
  hs_code: string
  description: string
  origin_country: string
  cif_value: number
  programs: TariffProgram[]
  rates: {
    base_mfn: number
    fta_applied: string | null
    section_232: number
    section_301: number
    ieepa: number
    total_effective: number
  }
  calculation: {
    cif_value: number
    total_duty: number
    total_landed_cost: number
    effective_rate: number
    currency: string
  }
  fta_name: string | null
  usmca_qualifying: boolean | null
}

interface OriginCountry {
  code: string
  name: string
  flag: string
  note: string
}

interface AutocompleteSuggestion {
  code: string
  description: string
  mfn_rate: number | null
}

// ============================================================================
// Hardcoded fallback list of origin countries
// ============================================================================

const FALLBACK_COUNTRIES: OriginCountry[] = [
  { code: 'CN', name: 'China', flag: '🇨🇳', note: 'Section 301 + IEEPA tariffs apply' },
  { code: 'MX', name: 'Mexico', flag: '🇲🇽', note: 'USMCA partner — 0% if qualifying' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦', note: 'USMCA partner — 0% if qualifying' },
  { code: 'VN', name: 'Vietnam', flag: '🇻🇳', note: 'IEEPA reciprocal tariffs apply' },
  { code: 'IN', name: 'India', flag: '🇮🇳', note: 'IEEPA reciprocal tariffs apply' },
  { code: 'TH', name: 'Thailand', flag: '🇹🇭', note: 'IEEPA reciprocal tariffs apply' },
  { code: 'DE', name: 'Germany', flag: '🇩🇪', note: 'EU — IEEPA reciprocal tariffs apply' },
  { code: 'JP', name: 'Japan', flag: '🇯🇵', note: 'IEEPA reciprocal tariffs apply' },
  { code: 'KR', name: 'South Korea', flag: '🇰🇷', note: 'KORUS FTA — reduced rates may apply' },
  { code: 'TW', name: 'Taiwan', flag: '🇹🇼', note: 'IEEPA reciprocal tariffs apply' },
  { code: 'BD', name: 'Bangladesh', flag: '🇧🇩', note: 'IEEPA reciprocal tariffs apply' },
  { code: 'ID', name: 'Indonesia', flag: '🇮🇩', note: 'IEEPA reciprocal tariffs apply' },
  { code: 'MY', name: 'Malaysia', flag: '🇲🇾', note: 'IEEPA reciprocal tariffs apply' },
  { code: 'PH', name: 'Philippines', flag: '🇵🇭', note: 'IEEPA reciprocal tariffs apply' },
  { code: 'BR', name: 'Brazil', flag: '🇧🇷', note: 'MFN rates apply' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧', note: 'MFN rates apply' },
  { code: 'IT', name: 'Italy', flag: '🇮🇹', note: 'EU — IEEPA reciprocal tariffs apply' },
  { code: 'FR', name: 'France', flag: '🇫🇷', note: 'EU — IEEPA reciprocal tariffs apply' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺', note: 'AUSFTA — reduced rates may apply' },
  { code: 'SG', name: 'Singapore', flag: '🇸🇬', note: 'USSFTA — reduced rates may apply' },
]

// ============================================================================
// Helpers
// ============================================================================

const fmt = (v: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(v)

function getProgramColor(authority: string): {
  bar: string
  badge: string
  text: string
} {
  switch (authority.toUpperCase()) {
    case 'MFN':
    case 'BASE':
      return { bar: 'bg-slate-400', badge: 'bg-slate-100 text-slate-700 border-slate-200', text: 'text-slate-700' }
    case '232':
    case 'SECTION_232':
      return { bar: 'bg-orange-400', badge: 'bg-orange-100 text-orange-700 border-orange-200', text: 'text-orange-700' }
    case '301':
    case 'SECTION_301':
      return { bar: 'bg-red-400', badge: 'bg-red-100 text-red-700 border-red-200', text: 'text-red-700' }
    case 'IEEPA':
      return { bar: 'bg-red-700', badge: 'bg-red-200 text-red-900 border-red-300', text: 'text-red-900' }
    case 'USMCA':
    case 'FTA':
      return { bar: 'bg-green-400', badge: 'bg-green-100 text-green-700 border-green-200', text: 'text-green-700' }
    default:
      return { bar: 'bg-gray-400', badge: 'bg-gray-100 text-gray-700 border-gray-200', text: 'text-gray-700' }
  }
}

function getEffectiveRateColor(rate: number): string {
  if (rate > 20) return 'text-red-600'
  if (rate > 10) return 'text-yellow-600'
  return 'text-green-600'
}

function getBannerStyle(originCountry: string, usmcaQualifying: boolean): { wrapper: string; rateText: string } {
  if ((originCountry === 'MX' || originCountry === 'CA') && usmcaQualifying) {
    return {
      wrapper: 'bg-green-50 border border-green-200',
      rateText: 'text-green-800',
    }
  }
  if (originCountry === 'CN') {
    return {
      wrapper: 'bg-red-50 border border-red-200',
      rateText: 'text-red-800',
    }
  }
  return {
    wrapper: 'bg-yellow-50 border border-yellow-200',
    rateText: 'text-yellow-800',
  }
}

// ============================================================================
// Main Component
// ============================================================================

interface UsImportCalculatorProps {
  initialHsCode?: string
  initialCountry?: string
  initialCifValue?: string
  initialQuery?: string
}

export function UsImportCalculator({
  initialHsCode = '',
  initialCountry = 'CN',
  initialCifValue = '',
  initialQuery = '',
}: UsImportCalculatorProps = {}) {
  const [originCountry, setOriginCountry] = useState(initialCountry)
  const [hsCode, setHsCode] = useState(initialHsCode)
  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [cifValue, setCifValue] = useState(initialCifValue)
  const [usmcaQualifying, setUsmcaQualifying] = useState(true)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<UsImportResult | null>(null)
  const [suggestions, setSuggestions] = useState<AutocompleteSuggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [searchLoading, setSearchLoading] = useState(false)
  const [limitError, setLimitError] = useState<{ used: number; limit: number } | null>(null)
  const [originCountries, setOriginCountries] = useState<OriginCountry[]>(FALLBACK_COUNTRIES)

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // --------------------------------------------------------------------------
  // Fetch origin countries on mount
  // --------------------------------------------------------------------------
  useEffect(() => {
    api
      .get('/tariff/origin-countries')
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setOriginCountries(res.data)
        }
      })
      .catch(() => {
        // Silently fall back to hardcoded list
      })
  }, [])

  // --------------------------------------------------------------------------
  // Close dropdown when clicking outside
  // --------------------------------------------------------------------------
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // --------------------------------------------------------------------------
  // Autocomplete — debounced 300 ms, min 2 chars
  // --------------------------------------------------------------------------
  const fetchSuggestions = useCallback(
    (q: string) => {
      if (q.length < 2) {
        setSuggestions([])
        setShowSuggestions(false)
        return
      }
      setSearchLoading(true)
      api
        .get('/tariff/hts/search', {
          params: { q, limit: 12 },
        })
        .then((res) => {
          const items: AutocompleteSuggestion[] = (res.data?.results || []).map(
            (item: { htsno: string; description: string; general_rate?: number | null }) => ({
              code: item.htsno,
              description: item.description,
              mfn_rate: item.general_rate ?? null,
            })
          )
          setSuggestions(items)
          setShowSuggestions(items.length > 0)
        })
        .catch(() => {
          setSuggestions([])
        })
        .finally(() => setSearchLoading(false))
    },
    []
  )

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setSearchQuery(val)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => fetchSuggestions(val), 300)
  }

  const handleSuggestionSelect = (suggestion: AutocompleteSuggestion) => {
    setHsCode(suggestion.code)
    setSearchQuery(`${suggestion.code} — ${suggestion.description}`)
    setSuggestions([])
    setShowSuggestions(false)
  }

  const handleClearHsCode = () => {
    setHsCode('')
    setSearchQuery('')
    setSuggestions([])
    setShowSuggestions(false)
    setResult(null)
    setLimitError(null)
  }

  // --------------------------------------------------------------------------
  // Calculate
  // --------------------------------------------------------------------------
  const handleCalculate = async () => {
    if (!hsCode || !cifValue) return

    setLoading(true)
    setResult(null)
    setLimitError(null)

    try {
      const res = await api.post(
        '/tariff/us-import',
        null,
        {
          params: {
            hts_code: hsCode,
            origin_country: originCountry,
            cif_value: parseFloat(cifValue),
            usmca_qualifying: usmcaQualifying,
          },
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      )
      setResult(res.data)
      toast.success('Calculation complete')
    } catch (error: unknown) {
      const err = error as { response?: { status?: number; data?: { detail?: unknown } } }
      if (err.response?.status === 429) {
        const detail = err.response.data?.detail
        if (detail && typeof detail === 'object') {
          const d = detail as { used?: number; limit?: number }
          setLimitError({ used: d.used ?? 0, limit: d.limit ?? 10 })
        } else {
          setLimitError({ used: 10, limit: 10 })
        }
      } else {
        toast.error('Failed to calculate tariff. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  // --------------------------------------------------------------------------
  // Derived values
  // --------------------------------------------------------------------------
  const showUsmca = originCountry === 'MX' || originCountry === 'CA'

  const selectedCountry = originCountries.find((c) => c.code === originCountry)

  // ============================================================================
  // Render
  // ============================================================================
  return (
    <div className="space-y-6">
      {/* ------------------------------------------------------------------ */}
      {/* Input Form Card                                                      */}
      {/* ------------------------------------------------------------------ */}
      <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
        <h2 className="text-xl font-bold text-brand-navy mb-1">US Import Duty Calculator</h2>
        <p className="text-sm text-gray-500 mb-6">
          Full tariff stacking — Section 301, IEEPA, Section 232, USMCA
        </p>

        {/* Row 1: Country of Origin */}
        <div className="mb-5">
          <label className="block text-sm font-semibold text-gray-700 mb-1.5">
            Country of Origin
          </label>
          <select
            value={originCountry}
            onChange={(e) => {
              setOriginCountry(e.target.value)
              setResult(null)
              setLimitError(null)
            }}
            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent bg-white"
          >
            {originCountries.map((c) => (
              <option key={c.code} value={c.code}>
                {c.flag} {c.name} — {c.note}
              </option>
            ))}
          </select>

          {/* USMCA checkbox — shown only for MX / CA */}
          {showUsmca && (
            <label className="flex items-center gap-2 mt-3 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={usmcaQualifying}
                onChange={(e) => setUsmcaQualifying(e.target.checked)}
                className="w-4 h-4 rounded border-gray-300 text-brand-teal focus:ring-brand-teal"
              />
              <span className="text-sm text-gray-700">
                This shipment qualifies for{' '}
                <span className="font-semibold text-brand-teal">USMCA (0% rate)</span>
              </span>
            </label>
          )}
        </div>

        {/* Row 2: HTS Code search */}
        <div className="mb-5" ref={dropdownRef}>
          <label className="block text-sm font-semibold text-gray-700 mb-1.5">
            Search Product or US HTS Code
          </label>
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
              placeholder="e.g. solar panels, 8541.40, steel coils…"
              disabled={!!hsCode}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
            />
            {searchLoading && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
              </div>
            )}

            {/* Autocomplete dropdown */}
            {showSuggestions && suggestions.length > 0 && !hsCode && (
              <div className="absolute z-50 left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto">
                {suggestions.map((s) => (
                  <button
                    key={s.code}
                    type="button"
                    onMouseDown={(e) => {
                      e.preventDefault()
                      handleSuggestionSelect(s)
                    }}
                    className="w-full text-left px-4 py-3 hover:bg-brand-blue/5 border-b border-gray-100 last:border-b-0 transition-colors"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-sm font-semibold text-brand-navy">{s.code}</span>
                      <span className="text-xs text-gray-400 shrink-0">{s.mfn_rate != null ? `MFN ${s.mfn_rate}%` : 'MFN Free'}</span>
                    </div>
                    <div className="text-xs text-gray-600 mt-0.5 line-clamp-2">{s.description}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Selected code chip */}
          {hsCode && (
            <div className="mt-2 flex items-center justify-between px-3 py-2 bg-brand-navy/5 border border-brand-navy/20 rounded-lg">
              <div>
                <span className="font-mono text-sm font-bold text-brand-navy">{hsCode}</span>
                <span className="text-xs text-gray-500 ml-2 line-clamp-1">
                  {searchQuery.replace(`${hsCode} — `, '')}
                </span>
              </div>
              <button
                type="button"
                onClick={handleClearHsCode}
                className="text-xs text-brand-blue hover:text-brand-navy font-medium ml-3 shrink-0"
              >
                Change
              </button>
            </div>
          )}
        </div>

        {/* Row 3: Selected HTS (read-only display already above) + CIF Value */}
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-1.5">
            CIF Value (USD)
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm font-medium">$</span>
            <input
              type="number"
              value={cifValue}
              onChange={(e) => setCifValue(e.target.value)}
              placeholder="10000"
              min="0"
              step="100"
              className="w-full pl-7 pr-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent"
            />
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Cost + Insurance + Freight value at US port of entry
          </p>
        </div>

        {/* Calculate button */}
        <button
          type="button"
          onClick={handleCalculate}
          disabled={!hsCode || !cifValue || loading}
          className="w-full py-3 bg-brand-navy text-white rounded-lg font-semibold text-sm hover:bg-brand-navy/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Calculating…
            </>
          ) : (
            'Calculate US Import Duties'
          )}
        </button>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Limit Error State                                                   */}
      {/* ------------------------------------------------------------------ */}
      {limitError && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold text-yellow-800 mb-1">Monthly lookup limit reached</p>
              <p className="text-sm text-yellow-700 mb-1">
                You've used <span className="font-bold">{limitError.used}/{limitError.limit}</span> free lookups this month.
              </p>
              <p className="text-sm text-yellow-700 mb-4">
                Upgrade to Pro for unlimited lookups — $49/month.
              </p>
              <Link
                to="/pricing"
                className="inline-block px-4 py-2 bg-brand-gold text-white rounded-lg text-sm font-semibold hover:bg-brand-gold/90 transition-colors"
              >
                View Pricing Plans
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* Results                                                             */}
      {/* ------------------------------------------------------------------ */}
      {result && (
        <div className="space-y-4">

          {/* 1. Summary banner */}
          {(() => {
            const banner = getBannerStyle(result.origin_country, result.usmca_qualifying ?? false)
            const calc = result.calculation
            return (
              <div className={`rounded-xl p-5 ${banner.wrapper}`}>
                <p className={`text-lg font-bold ${banner.rateText}`}>
                  {result.calculation.effective_rate.toFixed(1)}% effective rate
                  {' '}on {result.description} from {selectedCountry?.name ?? result.origin_country}
                </p>
                <p className="text-sm mt-1 text-gray-700">
                  CIF Value: <span className="font-medium">{fmt(calc.cif_value)}</span>
                  {' '}→ Total Duty: <span className="font-medium">{fmt(calc.total_duty)}</span>
                  {' '}→ <span className="font-bold">Landed Cost: {fmt(calc.total_landed_cost)}</span>
                </p>
              </div>
            )
          })()}

          {/* 2. Tariff Programs list */}
          <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wide mb-4">
              Tariff Stack Breakdown
            </h3>
            <div className="space-y-3">
              {result.programs.map((prog, i) => {
                const colors = getProgramColor(prog.authority)
                const isSavings =
                  prog.authority.toUpperCase() === 'USMCA' ||
                  prog.authority.toUpperCase() === 'FTA'

                if (isSavings) {
                  return (
                    <div
                      key={i}
                      className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg"
                    >
                      <CheckCircle className="w-4 h-4 text-green-600 shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-sm font-semibold text-green-700">
                            {prog.name} applies — saves {fmt(prog.savings_vs_mfn ?? 0)}
                          </span>
                          <span className="text-sm font-bold text-green-700">
                            {prog.rate.toFixed(2)}%
                          </span>
                        </div>
                        {prog.note && (
                          <p className="text-xs text-green-600 mt-0.5">{prog.note}</p>
                        )}
                      </div>
                    </div>
                  )
                }

                return (
                  <div key={i} className="flex items-start gap-3">
                    {/* Color bar */}
                    <div className={`w-1 rounded-full self-stretch min-h-[2.5rem] ${colors.bar}`} />
                    <div className="flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <span className={`text-sm font-semibold ${colors.text}`}>
                          {prog.name}
                        </span>
                        <div className="flex items-center gap-3 shrink-0">
                          <span className={`text-xs font-mono px-2 py-0.5 rounded border ${colors.badge}`}>
                            {prog.rate.toFixed(2)}%
                          </span>
                          <span className="text-sm font-bold text-gray-700 min-w-[5rem] text-right">
                            {fmt(prog.amount)}
                          </span>
                        </div>
                      </div>
                      {prog.note && (
                        <p className="text-xs text-gray-500 mt-0.5">{prog.note}</p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* 3. KPI cards */}
          {(() => {
            const calc = result.calculation
            const dutyAsPct = calc.total_landed_cost > 0
              ? ((calc.total_duty / calc.total_landed_cost) * 100).toFixed(1)
              : '0.0'
            const rateColor = getEffectiveRateColor(result.rates.total_effective)
            return (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {/* Effective Rate */}
                <div className="bg-white rounded-xl shadow-card border border-gray-100 p-4 flex flex-col gap-1">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <Percent className="w-3.5 h-3.5" />
                    <span className="text-xs font-medium uppercase tracking-wide">Effective Rate</span>
                  </div>
                  <p className={`text-2xl font-bold ${rateColor}`}>
                    {result.rates.total_effective.toFixed(1)}%
                  </p>
                </div>

                {/* Total Duty */}
                <div className="bg-white rounded-xl shadow-card border border-gray-100 p-4 flex flex-col gap-1">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span className="text-xs font-medium uppercase tracking-wide">Total Duty</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-800">
                    {fmt(calc.total_duty)}
                  </p>
                </div>

                {/* Landed Cost */}
                <div className="bg-white rounded-xl shadow-card border border-gray-100 p-4 flex flex-col gap-1">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <Package className="w-3.5 h-3.5" />
                    <span className="text-xs font-medium uppercase tracking-wide">Landed Cost</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-800">
                    {fmt(calc.total_landed_cost)}
                  </p>
                </div>

                {/* Duty as % of Landed */}
                <div className="bg-white rounded-xl shadow-card border border-gray-100 p-4 flex flex-col gap-1">
                  <div className="flex items-center gap-1.5 text-gray-500">
                    <DollarSign className="w-3.5 h-3.5" />
                    <span className="text-xs font-medium uppercase tracking-wide">Duty / Landed</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-800">{dutyAsPct}%</p>
                </div>
              </div>
            )
          })()}

          {/* 4. China tariff alert (Section 301 or IEEPA) */}
          {(result.rates.section_301 > 0 || result.rates.ieepa > 0) && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-5">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-800 mb-1">China tariff alert</p>
                  <p className="text-sm text-red-700 mb-3">
                    Your goods are subject to
                    {result.rates.section_301 > 0 && (
                      <> Section 301 at <strong>{result.rates.section_301}%</strong></>
                    )}
                    {result.rates.section_301 > 0 && result.rates.ieepa > 0 && ' and '}
                    {result.rates.ieepa > 0 && (
                      <> IEEPA at <strong>{result.rates.ieepa}%</strong></>
                    )}
                    . Consider alternative sourcing or duty drawback to reduce costs.
                  </p>
                  <div className="flex items-center gap-3 flex-wrap">
                    <Link
                      to="/sourcing"
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition-colors"
                    >
                      Alternative Sourcing →
                    </Link>
                    <Link
                      to="/drawback"
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-red-300 text-red-700 rounded-lg text-xs font-semibold hover:bg-red-50 transition-colors"
                    >
                      Duty Drawback →
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 5. FTA / USMCA savings callout */}
          {result.fta_name && result.rates.fta_applied && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-5">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-green-800 mb-1">
                    {result.fta_name} savings applied
                  </p>
                  {(() => {
                    const savingsProg = result.programs.find(
                      (p) =>
                        p.authority.toUpperCase() === 'USMCA' ||
                        p.authority.toUpperCase() === 'FTA'
                    )
                    const savings = savingsProg?.savings_vs_mfn ?? 0
                    return (
                      <p className="text-sm text-green-700">
                        {fmt(savings)} saved vs. paying MFN + standard rates.
                      </p>
                    )
                  })()}
                </div>
              </div>
            </div>
          )}

        </div>

          {/* Rate history chart */}
          <RateHistoryChart
            htsno={result.hs_code}
            country={result.origin_country}
            countryName={selectedCountry?.name ?? result.origin_country}
          />

      </div>
      )}
    </div>
  )
}
