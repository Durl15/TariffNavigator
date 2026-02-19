import { useState } from 'react'
import { X } from 'lucide-react'

export interface SearchFilterValues {
  category: string | null
  minRate: number | null
  maxRate: number | null
  sortBy: string
}

interface SearchFiltersProps {
  onFilterChange: (filters: SearchFilterValues) => void
  initialFilters?: SearchFilterValues
}

const CATEGORIES = [
  { value: 'electronics', label: 'Electronics' },
  { value: 'textiles', label: 'Textiles & Apparel' },
  { value: 'footwear', label: 'Footwear' },
  { value: 'machinery', label: 'Machinery' },
  { value: 'chemicals', label: 'Chemicals' },
  { value: 'food', label: 'Food & Beverages' },
  { value: 'vehicles', label: 'Vehicles & Parts' },
  { value: 'furniture', label: 'Furniture' },
  { value: 'plastics', label: 'Plastics' },
  { value: 'metals', label: 'Metals' },
]

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'rate_asc', label: 'Duty Rate: Low to High' },
  { value: 'rate_desc', label: 'Duty Rate: High to Low' },
  { value: 'code', label: 'HS Code' },
]

export default function SearchFilters({ onFilterChange, initialFilters }: SearchFiltersProps) {
  const [category, setCategory] = useState<string | null>(initialFilters?.category || null)
  const [minRate, setMinRate] = useState<number | null>(initialFilters?.minRate || null)
  const [maxRate, setMaxRate] = useState<number | null>(initialFilters?.maxRate || null)
  const [sortBy, setSortBy] = useState<string>(initialFilters?.sortBy || 'relevance')
  const [isExpanded, setIsExpanded] = useState(false)

  const handleCategoryChange = (value: string) => {
    const newCategory = value === category ? null : value
    setCategory(newCategory)
    applyFilters({ category: newCategory, minRate, maxRate, sortBy })
  }

  const handleMinRateChange = (value: string) => {
    const newMinRate = value ? parseFloat(value) : null
    setMinRate(newMinRate)
    applyFilters({ category, minRate: newMinRate, maxRate, sortBy })
  }

  const handleMaxRateChange = (value: string) => {
    const newMaxRate = value ? parseFloat(value) : null
    setMaxRate(newMaxRate)
    applyFilters({ category, minRate, maxRate: newMaxRate, sortBy })
  }

  const handleSortChange = (value: string) => {
    setSortBy(value)
    applyFilters({ category, minRate, maxRate, sortBy: value })
  }

  const applyFilters = (filters: SearchFilterValues) => {
    onFilterChange(filters)
  }

  const clearFilters = () => {
    setCategory(null)
    setMinRate(null)
    setMaxRate(null)
    setSortBy('relevance')
    onFilterChange({ category: null, minRate: null, maxRate: null, sortBy: 'relevance' })
  }

  const hasActiveFilters = category || minRate !== null || maxRate !== null || sortBy !== 'relevance'

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-gray-700 font-medium hover:text-gray-900"
        >
          <svg
            className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span>Filters {hasActiveFilters && `(${[category, minRate !== null || maxRate !== null, sortBy !== 'relevance'].filter(Boolean).length} active)`}</span>
        </button>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
          >
            <X className="w-4 h-4" />
            Clear all
          </button>
        )}
      </div>

      {/* Filters Content */}
      {isExpanded && (
        <div className="space-y-4 pt-3 border-t border-gray-200">
          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.value}
                  onClick={() => handleCategoryChange(cat.value)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    category === cat.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>

          {/* Duty Rate Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duty Rate Range (%)
            </label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Min</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  placeholder="0"
                  value={minRate ?? ''}
                  onChange={(e) => handleMinRateChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Max</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  placeholder="100"
                  value={maxRate ?? ''}
                  onChange={(e) => handleMaxRateChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Sort By */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => handleSortChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}
    </div>
  )
}
