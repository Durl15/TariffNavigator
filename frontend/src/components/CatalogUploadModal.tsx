import React, { useState, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { X, Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import { uploadCatalog, type CatalogUploadResponse, type UploadError } from '../services/api'
import toast from 'react-hot-toast'

interface CatalogUploadModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (catalogId: string) => void
}

export default function CatalogUploadModal({
  isOpen,
  onClose,
  onSuccess
}: CatalogUploadModalProps) {
  const [file, setFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [uploadResult, setUploadResult] = useState<CatalogUploadResponse | null>(null)

  const uploadMutation = useMutation({
    mutationFn: ({ file, name, description }: { file: File; name: string; description?: string }) =>
      uploadCatalog(file, name, description),
    onSuccess: (data) => {
      setUploadResult(data)
      if (data.error_count === 0) {
        // No errors - success
        onSuccess(data.catalog_id)
      }
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || 'Failed to upload catalog'
      toast.error(errorMessage)
    },
  })

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }, [])

  const handleFileSelect = (selectedFile: File) => {
    // Validate file type
    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      toast.error('Please upload a CSV file')
      return
    }

    // Validate file size (5MB)
    const maxSize = 5 * 1024 * 1024
    if (selectedFile.size > maxSize) {
      toast.error(`File too large. Maximum size is 5MB. Your file is ${(selectedFile.size / (1024 * 1024)).toFixed(2)}MB`)
      return
    }

    setFile(selectedFile)

    // Auto-populate name if empty
    if (!name) {
      const fileName = selectedFile.name.replace('.csv', '')
      setName(fileName)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      toast.error('Please select a file')
      return
    }

    if (!name.trim()) {
      toast.error('Please enter a catalog name')
      return
    }

    uploadMutation.mutate({
      file,
      name: name.trim(),
      description: description.trim() || undefined
    })
  }

  const handleClose = () => {
    if (!uploadMutation.isPending) {
      setFile(null)
      setName('')
      setDescription('')
      setUploadResult(null)
      onClose()
    }
  }

  const handleContinue = () => {
    if (uploadResult) {
      onSuccess(uploadResult.catalog_id)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Upload Product Catalog</h2>
          <button
            onClick={handleClose}
            disabled={uploadMutation.isPending}
            className="p-2 hover:bg-gray-100 rounded transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6">
          {!uploadResult ? (
            <>
              {/* File Upload Area */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CSV File *
                </label>
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    dragActive
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-300 hover:border-indigo-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  {file ? (
                    <div className="flex items-center justify-center gap-3">
                      <FileText className="w-8 h-8 text-indigo-600" />
                      <div className="text-left">
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-600">
                          {(file.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => setFile(null)}
                        className="ml-4 text-red-600 hover:text-red-700"
                      >
                        Remove
                      </button>
                    </div>
                  ) : (
                    <>
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 mb-2">
                        Drag and drop your CSV file here, or{' '}
                        <label className="text-indigo-600 hover:text-indigo-700 cursor-pointer">
                          browse
                          <input
                            type="file"
                            accept=".csv"
                            onChange={(e) => e.target.files && handleFileSelect(e.target.files[0])}
                            className="hidden"
                          />
                        </label>
                      </p>
                      <p className="text-sm text-gray-500">Maximum file size: 5MB</p>
                    </>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Required columns: sku, product_name, hs_code, origin_country, cogs, retail_price, annual_volume
                </p>
              </div>

              {/* Catalog Name */}
              <div className="mb-6">
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Catalog Name *
                </label>
                <input
                  type="text"
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Q1 2024 Product Catalog"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              {/* Description */}
              <div className="mb-6">
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Add notes about this catalog..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={uploadMutation.isPending}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!file || !name.trim() || uploadMutation.isPending}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {uploadMutation.isPending ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Upload
                    </>
                  )}
                </button>
              </div>
            </>
          ) : (
            /* Upload Result */
            <div>
              {/* Success Summary */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
                <div className="flex items-center gap-3 mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">Upload Complete!</h3>
                    <p className="text-gray-600">
                      {uploadResult.success_count} of {uploadResult.total_skus} products uploaded successfully
                    </p>
                  </div>
                </div>
              </div>

              {/* Errors */}
              {uploadResult.error_count > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
                  <div className="flex items-start gap-3 mb-4">
                    <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-900 mb-2">
                        {uploadResult.error_count} row{uploadResult.error_count !== 1 ? 's' : ''} skipped
                      </h4>
                      <div className="max-h-48 overflow-y-auto space-y-2">
                        {uploadResult.errors.slice(0, 10).map((error, idx) => (
                          <div key={idx} className="text-sm text-gray-700 bg-white p-2 rounded">
                            <span className="font-medium">Row {error.row}</span> (SKU: {error.sku}):{' '}
                            <span className="text-red-600">{error.error}</span>
                          </div>
                        ))}
                        {uploadResult.errors.length > 10 && (
                          <p className="text-sm text-gray-600 italic">
                            ...and {uploadResult.errors.length - 10} more error{uploadResult.errors.length - 10 !== 1 ? 's' : ''}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={handleClose}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Close
                </button>
                <button
                  type="button"
                  onClick={handleContinue}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  View Impact Analysis
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
