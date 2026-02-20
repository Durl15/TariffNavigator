import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Upload, Folder, Trash2, Edit, BarChart3, Plus } from 'lucide-react'
import { getCatalogs, deleteCatalog, type CatalogListItem } from '../services/api'
import toast from 'react-hot-toast'
import CatalogUploadModal from '../components/CatalogUploadModal'

export default function CatalogsPage() {
  const [showUploadModal, setShowUploadModal] = useState(false)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Fetch catalogs
  const { data, isLoading } = useQuery({
    queryKey: ['catalogs'],
    queryFn: () => getCatalogs(1, 50),
    refetchInterval: 30000,
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteCatalog,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['catalogs'] })
      toast.success('Catalog deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete catalog')
    },
  })

  const handleDelete = (catalog: CatalogListItem) => {
    if (confirm(`Are you sure you want to delete "${catalog.name}"? This will remove all ${catalog.total_skus} products.`)) {
      deleteMutation.mutate(catalog.id)
    }
  }

  const handleViewImpact = (catalogId: string) => {
    navigate(`/catalogs/${catalogId}/impact`)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Product Catalogs</h1>
            <p className="text-gray-600 mt-2">
              Upload and analyze tariff impact across your product portfolio
            </p>
          </div>
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
          >
            <Upload className="w-5 h-5" />
            Upload Catalog
          </button>
        </div>
      </div>

      {/* Empty State */}
      {!isLoading && (!data || data.catalogs.length === 0) && (
        <div className="text-center py-16 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <Folder size={64} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No catalogs yet</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Upload a CSV of your product catalog to analyze tariff impact, calculate landed costs, and identify margin risks.
          </p>
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors inline-flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Upload Your First Catalog
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      )}

      {/* Catalog Grid */}
      {!isLoading && data && data.catalogs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.catalogs.map((catalog) => (
            <CatalogCard
              key={catalog.id}
              catalog={catalog}
              onViewImpact={() => handleViewImpact(catalog.id)}
              onDelete={() => handleDelete(catalog)}
            />
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <CatalogUploadModal
          isOpen={showUploadModal}
          onClose={() => setShowUploadModal(false)}
          onSuccess={(catalogId) => {
            setShowUploadModal(false)
            queryClient.invalidateQueries({ queryKey: ['catalogs'] })
            toast.success('Catalog uploaded successfully!')
            // Navigate to impact page
            navigate(`/catalogs/${catalogId}/impact`)
          }}
        />
      )}
    </div>
  )
}

// Sub-component: Catalog Card
interface CatalogCardProps {
  catalog: CatalogListItem
  onViewImpact: () => void
  onDelete: () => void
}

function CatalogCard({ catalog, onViewImpact, onDelete }: CatalogCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
            <Folder className="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 text-lg">{catalog.name}</h3>
            <p className="text-sm text-gray-600">
              {catalog.total_skus} product{catalog.total_skus !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      </div>

      {/* Description */}
      {catalog.description && (
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">{catalog.description}</p>
      )}

      {/* Metadata */}
      <div className="text-xs text-gray-500 mb-4">
        <p>Uploaded: {new Date(catalog.uploaded_at).toLocaleDateString()}</p>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={onViewImpact}
          className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2 text-sm"
        >
          <BarChart3 className="w-4 h-4" />
          View Impact
        </button>
        <button
          onClick={onDelete}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center"
          title="Delete catalog"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
