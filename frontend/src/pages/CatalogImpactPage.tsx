import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import {
  ArrowLeft,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Package,
  AlertTriangle,
  RefreshCw
} from 'lucide-react'
import { getCatalogImpact, type CatalogItem } from '../services/api'
import toast from 'react-hot-toast'

const COLORS = ['#4F46E5', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

export default function CatalogImpactPage() {
  const { catalogId } = useParams<{ catalogId: string }>()
  const navigate = useNavigate()
  const [destinationCountry, setDestinationCountry] = useState('CN')
  const [page, setPage] = useState(1)
  const pageSize = 50

  // Fetch impact analysis
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['catalogImpact', catalogId, destinationCountry],
    queryFn: () => getCatalogImpact(catalogId!, destinationCountry, false),
    enabled: !!catalogId,
  })

  const handleRecalculate = async () => {
    try {
      await getCatalogImpact(catalogId!, destinationCountry, true)
      refetch()
      toast.success('Calculations updated successfully')
    } catch (error) {
      toast.error('Failed to recalculate')
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <p className="text-center text-gray-600">Catalog not found</p>
      </div>
    )
  }

  const metrics = data.portfolio_metrics
  const paginatedItems = data.items.slice((page - 1) * pageSize, page * pageSize)
  const totalPages = Math.ceil(data.items.length / pageSize)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/catalogs')}
          className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Catalogs
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{data.catalog_name}</h1>
            <p className="text-gray-600 mt-2">
              Tariff Impact Analysis • {metrics.total_items} products
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Destination Country Selector */}
            <select
              value={destinationCountry}
              onChange={(e) => setDestinationCountry(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="CN">Import to China (CN)</option>
              <option value="US">Import to USA (US)</option>
              <option value="EU">Import to EU</option>
              <option value="JP">Import to Japan (JP)</option>
              <option value="KR">Import to Korea (KR)</option>
              <option value="MX">Import to Mexico (MX)</option>
              <option value="CA">Import to Canada (CA)</option>
            </select>
            <button
              onClick={handleRecalculate}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Recalculate
            </button>
          </div>
        </div>
      </div>

      {/* Portfolio Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          icon={<DollarSign className="w-6 h-6 text-red-600" />}
          title="Total Tariff Exposure"
          value={`$${metrics.total_tariff_exposure.toLocaleString()}`}
          subtitle="Annual tariff cost"
          color="red"
        />
        <MetricCard
          icon={<TrendingUp className="w-6 h-6 text-green-600" />}
          title="Total Revenue"
          value={`$${metrics.total_revenue.toLocaleString()}`}
          subtitle="Annual revenue"
          color="green"
        />
        <MetricCard
          icon={<TrendingDown className="w-6 h-6 text-blue-600" />}
          title="Average Margin"
          value={`${metrics.avg_margin_percent.toFixed(1)}%`}
          subtitle="Weighted average"
          color="blue"
        />
        <MetricCard
          icon={<AlertTriangle className="w-6 h-6 text-amber-600" />}
          title="Risk Products"
          value={metrics.negative_margin_count.toString()}
          subtitle="Negative margins"
          color="amber"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Bar Chart: Tariff by Category */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Tariff by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metrics.by_category}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
              <Bar dataKey="total_tariff" fill="#4F46E5" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart: Tariff by Origin */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Tariff by Origin Country</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={metrics.by_origin}
                dataKey="total_tariff"
                nameKey="origin_country"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {metrics.by_origin.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Product Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-bold text-gray-900">Product Details</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SKU
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  HS Code
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Origin
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  COGS
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tariff Cost
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Landed Cost
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Margin %
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Annual Exposure
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedItems.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.sku}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {item.product_name}
                    {item.category && (
                      <span className="ml-2 text-xs text-gray-500">({item.category})</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {item.hs_code}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {item.origin_country}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                    ${Number(item.cogs).toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-red-600">
                    ${Number(item.tariff_cost || 0).toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                    ${Number(item.landed_cost || 0).toFixed(2)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-medium ${
                    Number(item.margin_percent || 0) < 0 ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {Number(item.margin_percent || 0).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                    ${(item.annual_tariff_exposure || 0).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, data.items.length)} of {data.items.length} products
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Sub-component: Metric Card
interface MetricCardProps {
  icon: React.ReactNode
  title: string
  value: string
  subtitle: string
  color: 'red' | 'green' | 'blue' | 'amber'
}

function MetricCard({ icon, title, value, subtitle, color }: MetricCardProps) {
  const colorClasses = {
    red: 'bg-red-100',
    green: 'bg-green-100',
    blue: 'bg-blue-100',
    amber: 'bg-amber-100'
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-2">
        <div className={`w-12 h-12 ${colorClasses[color]} rounded-lg flex items-center justify-center`}>
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
      <p className="text-xs text-gray-500">{subtitle}</p>
    </div>
  )
}
