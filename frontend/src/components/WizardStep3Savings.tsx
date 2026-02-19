import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { ArrowLeft, ArrowRight, DollarSign } from 'lucide-react'
import type { WizardState } from '../pages/FTAWizardPage'

interface Step3Props {
  state: WizardState
  onUpdate: (state: WizardState) => void
  onBack: () => void
  onNext: () => void
}

export default function WizardStep3Savings({ state, onUpdate, onBack, onNext }: Step3Props) {
  const [cifValue, setCifValue] = useState(state.cifValue || 10000)

  // Calculate costs
  const standardDuty = cifValue * (state.standardRate / 100)
  const ftaDuty = state.ftaEligible ? cifValue * (state.preferentialRate / 100) : standardDuty
  const savings = standardDuty - ftaDuty
  const savingsPercent = cifValue > 0 ? (savings / cifValue) * 100 : 0

  const handleNext = () => {
    if (!cifValue || cifValue <= 0) {
      toast.error('Please enter a valid CIF value')
      return
    }
    if (cifValue > 10000000) {
      toast.error('CIF value cannot exceed $10,000,000')
      return
    }

    // Update state with calculations
    onUpdate({
      ...state,
      cifValue,
      savings,
      savingsPercent,
      standardCalculation: {
        cifValue,
        duty: standardDuty,
        totalCost: cifValue + standardDuty
      },
      ftaCalculation: state.ftaEligible ? {
        cifValue,
        duty: ftaDuty,
        totalCost: cifValue + ftaDuty
      } : null
    })

    onNext()
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Cost Savings Projection</h2>

      {/* CIF Value Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          CIF Value (USD) <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">$</span>
          <input
            type="number"
            value={cifValue}
            onChange={(e) => setCifValue(Number(e.target.value))}
            placeholder="Enter shipment value"
            min="0"
            max="10000000"
            step="100"
            className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">Cost, Insurance, and Freight value of your shipment</p>
      </div>

      {/* Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Standard MFN Card */}
        <div className="border-2 border-gray-300 rounded-lg p-6 bg-gray-50">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900">Standard Rate</h3>
            <span className="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm font-medium">
              MFN
            </span>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">CIF Value:</span>
              <span className="font-medium">${cifValue.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Duty Rate:</span>
              <span className="font-medium">{state.standardRate}%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Customs Duty:</span>
              <span className="font-medium">${standardDuty.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
            <div className="pt-3 border-t border-gray-300 flex justify-between">
              <span className="font-bold text-gray-900">Total Cost:</span>
              <span className="font-bold text-gray-900 text-lg">${(cifValue + standardDuty).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
          </div>
        </div>

        {/* FTA Card */}
        {state.ftaEligible && (
          <div className="border-2 border-green-500 rounded-lg p-6 bg-green-50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-green-900">FTA Rate</h3>
              <span className="px-3 py-1 bg-green-200 text-green-800 rounded-full text-sm font-medium">
                {state.ftaName}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-700">CIF Value:</span>
                <span className="font-medium text-gray-900">${cifValue.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-700">Duty Rate:</span>
                <span className="font-medium text-green-700">{state.preferentialRate}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-700">Customs Duty:</span>
                <span className="font-medium text-gray-900">${ftaDuty.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
              <div className="pt-3 border-t border-green-300 flex justify-between">
                <span className="font-bold text-green-900">Total Cost:</span>
                <span className="font-bold text-green-900 text-lg">${(cifValue + ftaDuty).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Savings Highlight */}
      {state.ftaEligible && savings > 0 && (
        <div className="p-6 bg-gradient-to-r from-green-50 to-green-100 border-2 border-green-500 rounded-lg mb-6 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <DollarSign className="w-6 h-6 text-green-600" />
            <h3 className="text-2xl font-bold text-green-900">
              Save ${savings.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </h3>
          </div>
          <p className="text-green-800 font-medium">
            {savingsPercent.toFixed(1)}% savings with {state.ftaName}
          </p>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
        <button
          onClick={handleNext}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
        >
          Review Summary
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
