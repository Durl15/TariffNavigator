import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Star, Bookmark, Copy, Share2, Trash2, X } from 'lucide-react'
import {
  getSavedCalculations,
  getFavoriteCalculations,
  toggleFavorite,
  deleteCalculation,
  duplicateCalculation,
  createShareLink,
  type CalculationListItem
} from '../services/api'
import toast from 'react-hot-toast'

interface SavedCalculationsSidebarProps {
  isOpen: boolean
  onClose: () => void
  onLoadCalculation: (calcId: string) => void
}

type TabType = 'all' | 'favorites'

export default function SavedCalculationsSidebar({
  isOpen,
  onClose,
  onLoadCalculation
}: SavedCalculationsSidebarProps) {
  const [activeTab, setActiveTab] = useState<TabType>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const queryClient = useQueryClient()

  // Fetch saved calculations
  const { data: savedData, isLoading: savedLoading } = useQuery({
    queryKey: ['savedCalculations', searchQuery],
    queryFn: () => getSavedCalculations(1, 50, searchQuery),
    enabled: activeTab === 'all',
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  // Fetch favorites
  const { data: favoritesData, isLoading: favoritesLoading } = useQuery({
    queryKey: ['favoriteCalculations'],
    queryFn: () => getFavoriteCalculations(1, 50),
    enabled: activeTab === 'favorites',
    refetchInterval: 30000,
  })

  // Toggle favorite mutation with optimistic updates
  const favoriteMutation = useMutation({
    mutationFn: ({ id, isFavorite }: { id: string; isFavorite: boolean }) =>
      toggleFavorite(id, isFavorite),
    onMutate: async ({ id, isFavorite }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['savedCalculations'] })
      await queryClient.cancelQueries({ queryKey: ['favoriteCalculations'] })

      // Snapshot previous values
      const previousSaved = queryClient.getQueryData(['savedCalculations', searchQuery])
      const previousFavorites = queryClient.getQueryData(['favoriteCalculations'])

      // Optimistically update
      queryClient.setQueryData(
        ['savedCalculations', searchQuery],
        (old: any) => {
          if (!old) return old
          return {
            ...old,
            calculations: old.calculations.map((calc: CalculationListItem) =>
              calc.id === id ? { ...calc, is_favorite: isFavorite } : calc
            ),
          }
        }
      )

      return { previousSaved, previousFavorites }
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousSaved) {
        queryClient.setQueryData(['savedCalculations', searchQuery], context.previousSaved)
      }
      if (context?.previousFavorites) {
        queryClient.setQueryData(['favoriteCalculations'], context.previousFavorites)
      }
      toast.error('Failed to update favorite')
    },
    onSuccess: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['savedCalculations'] })
      queryClient.invalidateQueries({ queryKey: ['favoriteCalculations'] })
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteCalculation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['savedCalculations'] })
      queryClient.invalidateQueries({ queryKey: ['favoriteCalculations'] })
      toast.success('Calculation deleted')
    },
    onError: () => {
      toast.error('Failed to delete calculation')
    },
  })

  // Duplicate mutation
  const duplicateMutation = useMutation({
    mutationFn: duplicateCalculation,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['savedCalculations'] })
      toast.success('Calculation duplicated')
      onLoadCalculation(data.id)
    },
    onError: () => {
      toast.error('Failed to duplicate calculation')
    },
  })

  // Share mutation
  const shareMutation = useMutation({
    mutationFn: (id: string) => createShareLink(id),
    onSuccess: (data) => {
      navigator.clipboard.writeText(data.share_url)
      toast.success('Share link copied to clipboard!')
    },
    onError: () => {
      toast.error('Failed to create share link')
    },
  })

  const calculations = activeTab === 'favorites'
    ? favoritesData?.calculations
    : savedData?.calculations

  const isLoading = activeTab === 'favorites' ? favoritesLoading : savedLoading

  return (
    <div
      className={`fixed top-0 right-0 h-full w-96 bg-white shadow-2xl transform transition-transform duration-300 z-50 ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}
    >
      {/* Header */}
      <div className="bg-indigo-600 text-white p-4 flex items-center justify-between">
        <h2 className="text-lg font-bold flex items-center gap-2">
          <Bookmark size={20} />
          Saved Calculations
        </h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-indigo-700 rounded transition-colors"
        >
          <X size={20} />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('all')}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === 'all'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-600 hover:text-indigo-600'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setActiveTab('favorites')}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === 'favorites'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-600 hover:text-indigo-600'
          }`}
        >
          Favorites
        </button>
      </div>

      {/* Search */}
      {activeTab === 'all' && (
        <div className="p-4 border-b">
          <input
            type="text"
            placeholder="Search calculations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      )}

      {/* Calculations List */}
      <div className="overflow-y-auto h-[calc(100%-200px)]">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : calculations && calculations.length > 0 ? (
          <div className="divide-y">
            {calculations.map((calc) => (
              <CalculationCard
                key={calc.id}
                calculation={calc}
                onLoad={() => onLoadCalculation(calc.id)}
                onToggleFavorite={() =>
                  favoriteMutation.mutate({ id: calc.id, is_favorite: !calc.is_favorite })
                }
                onDelete={() => {
                  if (confirm('Are you sure you want to delete this calculation?')) {
                    deleteMutation.mutate(calc.id)
                  }
                }}
                onDuplicate={() => duplicateMutation.mutate(calc.id)}
                onShare={() => shareMutation.mutate(calc.id)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Bookmark size={48} className="mx-auto mb-4 opacity-50" />
            <p>No saved calculations yet</p>
            <p className="text-sm mt-2">Calculate a tariff and save it to see it here</p>
          </div>
        )}
      </div>
    </div>
  )
}

// Sub-component for calculation card
interface CalculationCardProps {
  calculation: CalculationListItem
  onLoad: () => void
  onToggleFavorite: () => void
  onDelete: () => void
  onDuplicate: () => void
  onShare: () => void
}

function CalculationCard({
  calculation,
  onLoad,
  onToggleFavorite,
  onDelete,
  onDuplicate,
  onShare,
}: CalculationCardProps) {
  const [showActions, setShowActions] = useState(false)

  return (
    <div className="p-4 hover:bg-gray-50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <button
          onClick={onLoad}
          className="flex-1 text-left"
        >
          <h3 className="font-semibold text-gray-900 hover:text-indigo-600 transition-colors">
            {calculation.name || 'Untitled Calculation'}
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {calculation.hs_code} • {calculation.origin_country} → {calculation.destination_country}
          </p>
          {calculation.product_description && (
            <p className="text-xs text-gray-500 mt-1 line-clamp-1">
              {calculation.product_description}
            </p>
          )}
        </button>
        <button
          onClick={onToggleFavorite}
          className={`p-1 transition-colors ${
            calculation.is_favorite
              ? 'text-yellow-500 hover:text-yellow-600'
              : 'text-gray-400 hover:text-yellow-500'
          }`}
        >
          <Star size={18} fill={calculation.is_favorite ? 'currentColor' : 'none'} />
        </button>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <p className="text-lg font-bold text-indigo-600">
            {calculation.currency} {calculation.total_cost.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500">
            {new Date(calculation.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Actions dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowActions(!showActions)}
            className="p-2 text-gray-600 hover:bg-gray-200 rounded transition-colors"
          >
            ⋮
          </button>

          {showActions && (
            <>
              {/* Backdrop to close menu */}
              <div
                className="fixed inset-0"
                onClick={() => setShowActions(false)}
              />

              {/* Menu */}
              <div className="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-lg border z-10">
                <button
                  onClick={() => {
                    onDuplicate()
                    setShowActions(false)
                  }}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <Copy size={16} />
                  Duplicate
                </button>
                <button
                  onClick={() => {
                    onShare()
                    setShowActions(false)
                  }}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <Share2 size={16} />
                  Share
                </button>
                <button
                  onClick={() => {
                    onDelete()
                    setShowActions(false)
                  }}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Tags */}
      {calculation.tags && calculation.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {calculation.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
