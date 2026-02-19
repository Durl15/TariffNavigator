import React from 'react'
import { TrendingDown, TrendingUp, BarChart3, DollarSign } from 'lucide-react'
import type { ComparisonMetrics as ComparisonMetricsType } from '../services/api'

interface ComparisonMetricsProps {
  metrics: ComparisonMetricsType
}

export default function ComparisonMetrics({ metrics }: ComparisonMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {/* Best Option Card */}
      <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
        <div className="flex items-center gap-2 text-gray-600 text-sm mb-2">
          <TrendingDown size={18} className="text-green-500" />
          <span>Best Option</span>
        </div>
        <p className="text-2xl font-bold text-green-600">
          ${metrics.min_total_cost.toLocaleString()}
        </p>
        <p className="text-xs text-gray-500 mt-1">Lowest total cost</p>
      </div>

      {/* Worst Option Card */}
      <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
        <div className="flex items-center gap-2 text-gray-600 text-sm mb-2">
          <TrendingUp size={18} className="text-red-500" />
          <span>Worst Option</span>
        </div>
        <p className="text-2xl font-bold text-red-600">
          ${metrics.max_total_cost.toLocaleString()}
        </p>
        <p className="text-xs text-gray-500 mt-1">Highest total cost</p>
      </div>

      {/* Average Cost Card */}
      <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
        <div className="flex items-center gap-2 text-gray-600 text-sm mb-2">
          <BarChart3 size={18} className="text-blue-500" />
          <span>Average Cost</span>
        </div>
        <p className="text-2xl font-bold text-blue-600">
          ${metrics.avg_total_cost.toLocaleString()}
        </p>
        <p className="text-xs text-gray-500 mt-1">Mean of all options</p>
      </div>

      {/* Cost Spread Card */}
      <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
        <div className="flex items-center gap-2 text-gray-600 text-sm mb-2">
          <DollarSign size={18} className="text-purple-500" />
          <span>Cost Spread</span>
        </div>
        <p className="text-2xl font-bold text-purple-600">
          ${metrics.cost_spread.toLocaleString()}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {metrics.cost_spread_percent.toFixed(1)}% difference
        </p>
      </div>
    </div>
  )
}
