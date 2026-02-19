import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { ArrowLeft, Save, Download, RefreshCw, Globe, Shield, DollarSign, FileText, CheckCircle } from 'lucide-react'
import type { WizardState } from '../pages/FTAWizardPage'
import SaveCalculationModal from './SaveCalculationModal'
import { exportPDF } from '../services/api'

interface Step4Props {
  state: WizardState
  onBack: () => void
}

export default function WizardStep4Review({ state, onBack }: Step4Props) {
  const [showSaveModal, setShowSaveModal] = useState(false)
  const navigate = useNavigate()

  const handleSave = () => {
    setShowSaveModal(true)
  }

  const handleExportPDF = async () => {
    try {
      const blob = await exportPDF({
        hs_code: state.hsCode,
        country: state.destinationCountry,
        description: state.hsDescription,
        rates: {
          mfn: state.standardRate,
          vat: 0,
          consumption: 0
        },
        calculation: {
          cif_value: state.cifValue,
          customs_duty: state.ftaEligible ? (state.ftaCalculation?.duty || 0) : (state.standardCalculation?.duty || 0),
          vat: 0,
          consumption_tax: 0,
          total_cost: state.ftaEligible ? (state.ftaCalculation?.totalCost || 0) : (state.standardCalculation?.totalCost || 0),
          currency: 'USD'
        },
        origin_country: state.originCountry,
        destination_country: state.destinationCountry
      })

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `fta-wizard-${state.hsCode}-${Date.now()}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('PDF exported successfully!')
    } catch (error) {
      console.error('Export error:', error)
      toast.error('Failed to export PDF')
    }
  }

  const handleStartNew = () => {
    navigate('/fta-wizard', { replace: true })
    window.location.reload() // Reset state
  }

  const calculationData = {
    hs_code: state.hsCode,
    product_description: state.hsDescription,
    origin_country: state.originCountry,
    destination_country: state.destinationCountry,
    cif_value: state.cifValue,
    currency: 'USD',
    total_cost: state.ftaEligible ? (state.ftaCalculation?.totalCost || 0) : (state.standardCalculation?.totalCost || 0),
    customs_duty: state.ftaEligible ? (state.ftaCalculation?.duty || 0) : (state.standardCalculation?.duty || 0),
    vat_amount: 0,
    fta_eligible: state.ftaEligible,
    fta_savings: state.savings,
    result: { wizardData: state }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Review Summary</h2>

      {/* Summary Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Trade Route Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <Globe className="w-5 h-5 text-indigo-600" />
            </div>
            <h3 className="font-bold text-gray-900">Trade Route</h3>
          </div>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600">HS Code:</span>
              <span className="ml-2 font-medium">{state.hsCode}</span>
            </div>
            <div>
              <span className="text-gray-600">Description:</span>
              <p className="text-gray-900 mt-1">{state.hsDescription}</p>
            </div>
            <div>
              <span className="text-gray-600">Route:</span>
              <span className="ml-2 font-medium">{state.originCountry} → {state.destinationCountry}</span>
            </div>
          </div>
        </div>

        {/* FTA Agreement Card */}
        <div className={`border rounded-lg p-6 ${state.ftaEligible ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
          <div className="flex items-center gap-3 mb-4">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${state.ftaEligible ? 'bg-green-100' : 'bg-gray-100'}`}>
              <Shield className={`w-5 h-5 ${state.ftaEligible ? 'text-green-600' : 'text-gray-600'}`} />
            </div>
            <h3 className="font-bold text-gray-900">FTA Status</h3>
          </div>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-700">Eligible:</span>
              <span className={`ml-2 font-medium ${state.ftaEligible ? 'text-green-700' : 'text-gray-700'}`}>
                {state.ftaEligible ? `✅ Yes (${state.ftaName})` : '❌ No'}
              </span>
            </div>
            <div>
              <span className="text-gray-700">Standard Rate:</span>
              <span className="ml-2 font-medium">{state.standardRate}%</span>
            </div>
            {state.ftaEligible && (
              <div>
                <span className="text-gray-700">FTA Rate:</span>
                <span className="ml-2 font-medium text-green-700">{state.preferentialRate}%</span>
              </div>
            )}
          </div>
        </div>

        {/* Cost Savings Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="font-bold text-gray-900">Cost Summary</h3>
          </div>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600">CIF Value:</span>
              <span className="ml-2 font-medium">${state.cifValue?.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-gray-600">Standard Cost:</span>
              <span className="ml-2 font-medium">${state.standardCalculation?.totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
            {state.ftaEligible && (
              <>
                <div>
                  <span className="text-gray-600">FTA Cost:</span>
                  <span className="ml-2 font-medium text-green-700">${state.ftaCalculation?.totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                </div>
                <div className="pt-2 border-t border-gray-200">
                  <span className="text-gray-900 font-bold">Savings:</span>
                  <span className="ml-2 font-bold text-green-600 text-lg">${state.savings?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                  <span className="ml-2 text-sm text-gray-600">({state.savingsPercent?.toFixed(1)}%)</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Required Documents Card */}
        {state.ftaEligible && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-amber-600" />
              </div>
              <h3 className="font-bold text-gray-900">Required Documents</h3>
            </div>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">Certificate of Origin</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">Direct Shipment Proof</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">Rules of Origin Compliance</span>
              </li>
            </ul>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
        <h3 className="font-bold text-gray-900 mb-4">What would you like to do?</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            onClick={handleSave}
            className="px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
          >
            <Save className="w-4 h-4" />
            Save Calculation
          </button>
          <button
            onClick={handleExportPDF}
            className="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export PDF
          </button>
          <button
            onClick={handleStartNew}
            className="px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Start New
          </button>
        </div>
      </div>

      {/* Back Button */}
      <div>
        <button
          onClick={onBack}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Savings
        </button>
      </div>

      {/* Save Modal */}
      {showSaveModal && (
        <SaveCalculationModal
          isOpen={showSaveModal}
          onClose={() => setShowSaveModal(false)}
          calculationData={calculationData}
        />
      )}
    </div>
  )
}
