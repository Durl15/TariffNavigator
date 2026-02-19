import { useQuery } from '@tanstack/react-query'
import { Calculator, TrendingUp, Clock, Globe, FileDown } from 'lucide-react'
import { getPublicStats, getPopularHSCodes, exportCSV, downloadBlob, type PublicStats, type PopularHSCode } from '../services/api'
import toast from 'react-hot-toast'
import { useState } from 'react'

export default function Dashboard() {
  const [isExporting, setIsExporting] = useState(false)

  // Fetch public stats
  const { data: stats, isLoading: statsLoading } = useQuery<PublicStats>({
    queryKey: ['publicStats'],
    queryFn: getPublicStats,
    refetchInterval: 60000, // Refetch every 60 seconds
  })

  // Fetch popular HS codes
  const { data: popularCodes, isLoading: codesLoading } = useQuery<PopularHSCode[]>({
    queryKey: ['popularHSCodes'],
    queryFn: getPopularHSCodes,
    refetchInterval: 300000, // Refetch every 5 minutes
  })

  const handleExportCSV = async () => {
    setIsExporting(true)
    try {
      const blob = await exportCSV({ limit: 100 })
      const timestamp = new Date().toISOString().split('T')[0]
      downloadBlob(blob, `calculations_${timestamp}.csv`)
      toast.success('CSV exported successfully!')
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Failed to export CSV. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Your Tariff Dashboard</h1>
          <p className="mt-2 text-gray-600">Track your calculations and explore tariff insights</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          {/* Total Calculations */}
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Calculations</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {statsLoading ? '...' : stats?.total_calculations.toLocaleString() || '0'}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <Calculator className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          {/* This Month */}
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">This Month</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {statsLoading ? '...' : stats?.calculations_this_month.toLocaleString() || '0'}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          {/* Today */}
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Today</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {statsLoading ? '...' : stats?.calculations_today.toLocaleString() || '0'}
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>

          {/* Total HS Codes */}
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">HS Codes</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">
                  {statsLoading ? '...' : stats?.total_hs_codes.toLocaleString() || '0'}
                </p>
              </div>
              <div className="p-3 bg-orange-100 rounded-full">
                <Globe className="h-6 w-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Popular HS Codes Section */}
        <div className="bg-white rounded-lg shadow mb-8 border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">Popular HS Codes</h2>
            <span className="text-sm text-gray-500">Last 30 days</span>
          </div>
          <div className="p-6">
            {codesLoading ? (
              <div className="text-center py-8">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Loading popular HS codes...</p>
              </div>
            ) : popularCodes && popularCodes.length > 0 ? (
              <div className="space-y-4">
                {popularCodes.map((code, index) => (
                  <div key={code.hs_code} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-mono font-semibold text-gray-900">{code.hs_code}</p>
                        <p className="text-sm text-gray-600">{code.description}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-blue-600">{code.usage_count}</p>
                      <p className="text-xs text-gray-500">calculations</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Globe className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                <p>No popular HS codes yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <a
              href="/"
              className="flex items-center justify-center px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Calculator className="mr-2 h-5 w-5" />
              New Calculation
            </a>
            <button
              onClick={handleExportCSV}
              disabled={isExporting}
              className="flex items-center justify-center px-6 py-4 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isExporting ? (
                <>
                  <div className="mr-2 inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-gray-700"></div>
                  Exporting...
                </>
              ) : (
                <>
                  <FileDown className="mr-2 h-5 w-5" />
                  Export CSV
                </>
              )}
            </button>
          </div>
        </div>

        {/* Supported Countries */}
        {stats && stats.supported_countries && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-sm font-semibold text-blue-900 mb-2">Supported Countries</h3>
            <div className="flex flex-wrap gap-2">
              {stats.supported_countries.map((country) => (
                <span
                  key={country}
                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                >
                  {country}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
