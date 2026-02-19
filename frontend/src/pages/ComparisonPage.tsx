import React from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Download, FileText } from 'lucide-react'
import { compareCalculations, exportComparisonPDF, exportComparisonCSV } from '../services/api'
import ComparisonMetrics from '../components/ComparisonMetrics'
import ComparisonTable from '../components/ComparisonTable'
import toast from 'react-hot-toast'

export default function ComparisonPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const ids = searchParams.get('ids')?.split(',') || []

  // Fetch comparison data
  const { data, isLoading, error } = useQuery({
    queryKey: ['comparison', ids],
    queryFn: () => compareCalculations(ids),
    enabled: ids.length >= 2 && ids.length <= 5,
  })

  // Export handlers
  const handleExportPDF = async () => {
    try {
      const blob = await exportComparisonPDF(ids)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `comparison-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success('PDF downloaded successfully')
    } catch (err) {
      toast.error('Failed to export PDF')
    }
  }

  const handleExportCSV = async () => {
    try {
      const blob = await exportComparisonCSV(ids)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `comparison-${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success('CSV downloaded successfully')
    } catch (err) {
      toast.error('Failed to export CSV')
    }
  }

  // Validation checks
  if (ids.length < 2) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Invalid Comparison</h2>
          <p className="text-gray-600 mb-4">Please select at least 2 calculations to compare.</p>
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  if (ids.length > 5) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Too Many Calculations</h2>
          <p className="text-gray-600 mb-4">Maximum 5 calculations can be compared at once.</p>
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading comparison...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-2">Error Loading Comparison</h2>
          <p className="text-gray-600 mb-4">{(error as Error).message || 'Failed to load comparison'}</p>
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  // Check for mixed currencies
  const currencies = new Set(data?.calculations.map(c => c.currency) || [])
  const hasMixedCurrencies = currencies.size > 1

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft size={20} />
            <span>Back to Calculations</span>
          </button>

          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Calculation Comparison
              </h1>
              <p className="text-gray-600">
                Comparing {data?.total_compared || 0} calculations •{' '}
                {data?.metrics.comparison_type === 'same_hs_different_countries'
                  ? 'Same HS Code, Different Countries'
                  : data?.metrics.comparison_type === 'different_hs_same_country'
                  ? 'Different HS Codes, Same Country'
                  : 'Mixed Comparison'}
              </p>
            </div>

            {/* Export Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleExportCSV}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <FileText size={18} />
                <span>Export CSV</span>
              </button>
              <button
                onClick={handleExportPDF}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Download size={18} />
                <span>Export PDF</span>
              </button>
            </div>
          </div>
        </div>

        {/* Mixed Currency Warning */}
        {hasMixedCurrencies && (
          <div className="bg-yellow-50 border border-yellow-400 rounded-lg p-4 mb-6 flex items-start gap-3">
            <span className="text-yellow-600 text-xl">⚠️</span>
            <div>
              <p className="font-medium text-yellow-800">Mixed Currencies Detected</p>
              <p className="text-sm text-yellow-700 mt-1">
                Calculations use different currencies ({Array.from(currencies).join(', ')}).
                Values are shown in their original currencies. For accurate comparison,
                consider converting to a common currency.
              </p>
            </div>
          </div>
        )}

        {/* Metrics Summary */}
        {data && <ComparisonMetrics metrics={data.metrics} />}

        {/* Comparison Table */}
        {data && (
          <>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Detailed Comparison</h2>
            <ComparisonTable calculations={data.calculations} />
          </>
        )}

        {/* FTA Summary */}
        {data && data.metrics.has_fta_eligible && (
          <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="font-bold text-green-900 mb-2">🎉 FTA Savings Available</h3>
            <p className="text-green-800">
              {data.calculations.filter(c => c.fta_eligible).length} of {data.total_compared} calculations
              are eligible for Free Trade Agreement benefits.
              {data.metrics.total_fta_savings && (
                <span className="font-semibold">
                  {' '}Total potential savings: ${data.metrics.total_fta_savings.toLocaleString()}
                </span>
              )}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
