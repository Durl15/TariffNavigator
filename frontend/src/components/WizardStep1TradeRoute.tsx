import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { ArrowRight, Loader2 } from 'lucide-react'
import type { WizardState } from '../pages/FTAWizardPage'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

interface Step1Props {
  state: WizardState
  onUpdate: (state: WizardState) => void
  onNext: () => void
}

interface HSCodeSuggestion {
  hs_code: string
  description: string
}

export default function WizardStep1TradeRoute({ state, onUpdate, onNext }: Step1Props) {
  const [hsQuery, setHsQuery] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)

  // HS Code autocomplete
  const { data: suggestions } = useQuery({
    queryKey: ['hsAutocomplete', hsQuery, state.originCountry],
    queryFn: async () => {
      const params = new URLSearchParams({
        query: hsQuery,
        ...(state.originCountry && { country: state.originCountry })
      })
      const token = localStorage.getItem('token')
      const headers: HeadersInit = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${API_BASE}/tariff/autocomplete?${params}`, { headers })
      if (!response.ok) throw new Error('Failed to fetch suggestions')
      const data = await response.json()
      return data.results as HSCodeSuggestion[]
    },
    enabled: hsQuery.length >= 4,
  })

  // FTA eligibility check
  const ftaCheckMutation = useMutation({
    mutationFn: async () => {
      const params = new URLSearchParams({
        hs_code: state.hsCode,
        origin_country: state.originCountry,
        dest_country: state.destinationCountry
      })
      const token = localStorage.getItem('token')
      const headers: HeadersInit = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${API_BASE}/tariff/fta-check?${params}`, { headers })
      if (!response.ok) throw new Error('Failed to check FTA eligibility')
      return response.json()
    },
    onSuccess: (data) => {
      onUpdate({
        ...state,
        ftaCheckResult: data,
        ftaEligible: data.is_eligible,
        ftaName: data.fta_name,
        standardRate: data.standard_rate,
        preferentialRate: data.preferential_rate
      })
      onNext()
    },
    onError: () => {
      toast.error('Failed to check FTA eligibility. Please try again.')
    }
  })

  const handleHSCodeSelect = (code: string, description: string) => {
    onUpdate({ ...state, hsCode: code, hsDescription: description })
    setHsQuery('')
    setShowSuggestions(false)
  }

  const handleNext = () => {
    // Validate
    if (!state.hsCode) {
      toast.error('Please select an HS code')
      return
    }
    if (!state.originCountry) {
      toast.error('Please select origin country')
      return
    }
    if (!state.destinationCountry) {
      toast.error('Please select destination country')
      return
    }

    // Check FTA eligibility
    ftaCheckMutation.mutate()
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Trade Route Details</h2>

      {/* HS Code Autocomplete */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          HS Code <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={state.hsCode || hsQuery}
          onChange={(e) => {
            if (!state.hsCode) {
              setHsQuery(e.target.value)
              setShowSuggestions(true)
            }
          }}
          onFocus={() => setShowSuggestions(true)}
          placeholder="Search HS code (e.g. 8517)"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        {state.hsCode && (
          <div className="mt-2 flex items-center justify-between px-4 py-2 bg-indigo-50 border border-indigo-200 rounded-lg">
            <div>
              <p className="font-medium text-indigo-900">{state.hsCode}</p>
              <p className="text-sm text-indigo-700">{state.hsDescription}</p>
            </div>
            <button
              onClick={() => {
                onUpdate({ ...state, hsCode: '', hsDescription: '' })
                setHsQuery('')
              }}
              className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
            >
              Change
            </button>
          </div>
        )}
        {/* Suggestions dropdown */}
        {!state.hsCode && showSuggestions && suggestions && suggestions.length > 0 && (
          <div className="mt-2 border border-gray-200 rounded-lg max-h-60 overflow-y-auto bg-white shadow-lg">
            {suggestions.map((item) => (
              <button
                key={item.hs_code}
                onClick={() => handleHSCodeSelect(item.hs_code, item.description)}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b last:border-b-0"
              >
                <div className="font-medium text-gray-900">{item.hs_code}</div>
                <div className="text-sm text-gray-600">{item.description}</div>
              </button>
            ))}
          </div>
        )}
        {!state.hsCode && hsQuery.length >= 4 && suggestions && suggestions.length === 0 && (
          <p className="mt-2 text-sm text-gray-500">No results found. Try a different search term.</p>
        )}
      </div>

      {/* Origin Country */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Origin Country <span className="text-red-500">*</span>
        </label>
        <select
          value={state.originCountry}
          onChange={(e) => onUpdate({ ...state, originCountry: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">Select Country</option>
          <option value="CN">China (CN)</option>
          <option value="US">United States (US)</option>
          <option value="EU">European Union (EU)</option>
          <option value="JP">Japan (JP)</option>
          <option value="KR">South Korea (KR)</option>
          <option value="MX">Mexico (MX)</option>
          <option value="CA">Canada (CA)</option>
        </select>
      </div>

      {/* Destination Country */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Destination Country <span className="text-red-500">*</span>
        </label>
        <select
          value={state.destinationCountry}
          onChange={(e) => onUpdate({ ...state, destinationCountry: e.target.value })}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">Select Country</option>
          <option value="CN">China (CN)</option>
          <option value="US">United States (US)</option>
          <option value="EU">European Union (EU)</option>
          <option value="JP">Japan (JP)</option>
          <option value="KR">South Korea (KR)</option>
          <option value="MX">Mexico (MX)</option>
          <option value="CA">Canada (CA)</option>
        </select>
      </div>

      {/* Selected Route Summary */}
      {state.hsCode && state.originCountry && state.destinationCountry && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-900">
            <strong>Route:</strong> {state.hsCode} • {state.originCountry} → {state.destinationCountry}
          </p>
          <p className="text-xs text-blue-700 mt-1">{state.hsDescription}</p>
        </div>
      )}

      {/* Next Button */}
      <div className="flex justify-end">
        <button
          onClick={handleNext}
          disabled={ftaCheckMutation.isPending}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {ftaCheckMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Checking FTA Eligibility...
            </>
          ) : (
            <>
              Next Step
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  )
}
