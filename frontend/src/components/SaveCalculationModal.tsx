import React, { useState } from 'react'
import { X, Save, Tag } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { saveCalculation, type SaveCalculationRequest } from '../services/api'
import toast from 'react-hot-toast'

interface SaveCalculationModalProps {
  isOpen: boolean
  onClose: () => void
  calculationData: any // The result object from the calculator
}

export default function SaveCalculationModal({
  isOpen,
  onClose,
  calculationData
}: SaveCalculationModalProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [tagInput, setTagInput] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const queryClient = useQueryClient()

  const saveMutation = useMutation({
    mutationFn: (data: SaveCalculationRequest) => saveCalculation(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['savedCalculations'] })
      toast.success('Calculation saved successfully!')
      onClose()
      resetForm()
    },
    onError: () => {
      toast.error('Failed to save calculation')
    },
  })

  const resetForm = () => {
    setName('')
    setDescription('')
    setTagInput('')
    setTags([])
  }

  const addTag = () => {
    const trimmed = tagInput.trim()
    if (trimmed && !tags.includes(trimmed) && tags.length < 10) {
      setTags([...tags, trimmed])
      setTagInput('')
    } else if (tags.length >= 10) {
      toast.error('Maximum 10 tags allowed')
    }
  }

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) {
      toast.error('Please enter a name')
      return
    }

    if (!calculationData) {
      toast.error('No calculation data available')
      return
    }

    // Build save request from calculation data
    const saveRequest: SaveCalculationRequest = {
      name: name.trim(),
      description: description.trim() || undefined,
      tags: tags.length > 0 ? tags : undefined,
      hs_code: calculationData.hs_code || '',
      product_description: calculationData.description || undefined,
      origin_country: calculationData.calculation?.origin_country || 'CN',
      destination_country: calculationData.country || calculationData.destination_country || 'CN',
      cif_value: calculationData.calculation?.cif_value || 0,
      currency: calculationData.calculation?.currency || 'USD',
      result: calculationData,
      total_cost: calculationData.calculation?.total_cost || calculationData.converted_calculation?.total_cost || 0,
      customs_duty: calculationData.calculation?.customs_duty,
      vat_amount: calculationData.calculation?.vat,
      fta_eligible: false,
      fta_savings: undefined,
    }

    saveMutation.mutate(saveRequest)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Save size={24} className="text-indigo-600" />
            Save Calculation
          </h2>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Name Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Calculation Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Electronics Import Q1 2024"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              maxLength={255}
              required
            />
          </div>

          {/* Description Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description (Optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add notes about this calculation..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              rows={3}
            />
          </div>

          {/* Tags Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags (Optional)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addTag()
                  }
                }}
                placeholder="Add a tag and press Enter"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                maxLength={50}
              />
              <button
                type="button"
                onClick={addTag}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                <Tag size={18} />
              </button>
            </div>

            {/* Tags Display */}
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 bg-indigo-100 text-indigo-700 text-sm rounded-full flex items-center gap-2"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="text-indigo-500 hover:text-indigo-700"
                    >
                      <X size={14} />
                    </button>
                  </span>
                ))}
              </div>
            )}
            <p className="text-xs text-gray-500 mt-2">
              {tags.length}/10 tags used
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saveMutation.isPending}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {saveMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Saving...
                </>
              ) : (
                <>
                  <Save size={18} />
                  Save
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
