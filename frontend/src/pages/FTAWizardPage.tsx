import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import WizardProgressBar from '../components/WizardProgressBar'
import WizardStep1TradeRoute from '../components/WizardStep1TradeRoute'
import WizardStep2Documentation from '../components/WizardStep2Documentation'
import WizardStep3Savings from '../components/WizardStep3Savings'
import WizardStep4Review from '../components/WizardStep4Review'

export interface FTACheckResult {
  is_eligible: boolean
  fta_name: string | null
  standard_rate: number
  preferential_rate: number
  savings_percent: number
}

export interface WizardState {
  currentStep: 1 | 2 | 3 | 4
  // Step 1
  hsCode: string
  hsDescription: string
  originCountry: string
  destinationCountry: string
  ftaCheckResult: FTACheckResult | null
  ftaEligible: boolean
  ftaName: string | null
  standardRate: number
  preferentialRate: number
  // Step 3
  cifValue: number
  savings: number
  savingsPercent: number
  standardCalculation: {
    cifValue: number
    duty: number
    totalCost: number
  } | null
  ftaCalculation: {
    cifValue: number
    duty: number
    totalCost: number
  } | null
}

const initialState: WizardState = {
  currentStep: 1,
  hsCode: '',
  hsDescription: '',
  originCountry: '',
  destinationCountry: '',
  ftaCheckResult: null,
  ftaEligible: false,
  ftaName: null,
  standardRate: 0,
  preferentialRate: 0,
  cifValue: 0,
  savings: 0,
  savingsPercent: 0,
  standardCalculation: null,
  ftaCalculation: null
}

export default function FTAWizardPage() {
  const [state, setState] = useState<WizardState>(initialState)
  const navigate = useNavigate()

  const handleNext = () => {
    if (state.currentStep < 4) {
      setState({ ...state, currentStep: (state.currentStep + 1) as WizardState['currentStep'] })
    }
  }

  const handleBack = () => {
    if (state.currentStep > 1) {
      setState({ ...state, currentStep: (state.currentStep - 1) as WizardState['currentStep'] })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">FTA Wizard</h1>
          <p className="text-gray-600 mt-2">Check eligibility, understand requirements, calculate savings</p>
        </div>

        {/* Progress Bar */}
        <WizardProgressBar currentStep={state.currentStep} />

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          {state.currentStep === 1 && (
            <WizardStep1TradeRoute
              state={state}
              onUpdate={setState}
              onNext={handleNext}
            />
          )}
          {state.currentStep === 2 && (
            <WizardStep2Documentation
              state={state}
              onBack={handleBack}
              onNext={handleNext}
            />
          )}
          {state.currentStep === 3 && (
            <WizardStep3Savings
              state={state}
              onUpdate={setState}
              onBack={handleBack}
              onNext={handleNext}
            />
          )}
          {state.currentStep === 4 && (
            <WizardStep4Review
              state={state}
              onBack={handleBack}
            />
          )}
        </div>
      </div>
    </div>
  )
}
