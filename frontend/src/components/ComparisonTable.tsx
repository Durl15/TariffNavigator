import React from 'react'
import type { ComparisonCalculationItem } from '../services/api'

interface ComparisonTableProps {
  calculations: ComparisonCalculationItem[]
}

export default function ComparisonTable({ calculations }: ComparisonTableProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {calculations.map((calc) => (
        <ComparisonCard key={calc.id} calculation={calc} />
      ))}
    </div>
  )
}

interface ComparisonCardProps {
  calculation: ComparisonCalculationItem
}

function ComparisonCard({ calculation }: ComparisonCardProps) {
  // Color coding based on rank
  const borderColor = calculation.is_best
    ? 'border-green-500'
    : calculation.is_worst
    ? 'border-red-500'
    : 'border-gray-200'

  const bgColor = calculation.is_best
    ? 'bg-green-50'
    : calculation.is_worst
    ? 'bg-red-50'
    : 'bg-white'

  const rankBadgeColor = calculation.is_best
    ? 'bg-green-200 text-green-800'
    : calculation.is_worst
    ? 'bg-red-200 text-red-800'
    : 'bg-gray-200 text-gray-800'

  return (
    <div className={`${bgColor} rounded-lg shadow-md p-6 border-l-4 ${borderColor} transition-all hover:shadow-lg`}>
      {/* Rank Badge */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-bold text-lg text-gray-900 mb-1">
            {calculation.name || 'Untitled Calculation'}
          </h3>
          <p className="text-sm text-gray-600">
            {calculation.hs_code} • {calculation.origin_country} → {calculation.destination_country}
          </p>
          {calculation.product_description && (
            <p className="text-xs text-gray-500 mt-1 line-clamp-2">
              {calculation.product_description}
            </p>
          )}
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-bold ${rankBadgeColor} flex-shrink-0 ml-2`}
        >
          #{calculation.rank}
        </span>
      </div>

      {/* Cost Breakdown */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">CIF Value</span>
          <span className="font-medium text-gray-900">
            {calculation.currency} {calculation.cif_value.toLocaleString()}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Customs Duty</span>
          <span className="font-medium text-gray-900">
            {calculation.customs_duty
              ? `${calculation.currency} ${calculation.customs_duty.toLocaleString()}`
              : 'N/A'}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">VAT</span>
          <span className="font-medium text-gray-900">
            {calculation.vat_amount
              ? `${calculation.currency} ${calculation.vat_amount.toLocaleString()}`
              : 'N/A'}
          </span>
        </div>
      </div>

      {/* Total Cost */}
      <div className="pt-4 mt-4 border-t border-gray-200 flex justify-between items-center">
        <span className="font-bold text-gray-700">Total Cost</span>
        <span className="text-xl font-bold text-indigo-600">
          {calculation.currency} {calculation.total_cost.toLocaleString()}
        </span>
      </div>

      {/* Difference Badge */}
      <div className="mt-3 text-center">
        <span
          className={`inline-block text-sm px-3 py-1 rounded-full font-medium ${
            calculation.cost_vs_average_percent > 0
              ? 'bg-red-100 text-red-700'
              : calculation.cost_vs_average_percent < 0
              ? 'bg-green-100 text-green-700'
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          {calculation.cost_vs_average_percent > 0 ? '+' : ''}
          {calculation.cost_vs_average_percent.toFixed(1)}% vs avg
        </span>
      </div>

      {/* FTA Badge */}
      {calculation.fta_eligible && calculation.fta_savings && (
        <div className="mt-3 px-3 py-2 bg-green-100 text-green-800 rounded-lg text-sm text-center font-medium">
          ✓ FTA Eligible • Save {calculation.currency} {calculation.fta_savings.toLocaleString()}
        </div>
      )}
    </div>
  )
}
