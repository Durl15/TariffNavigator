import React from 'react'

interface WizardProgressBarProps {
  currentStep: 1 | 2 | 3 | 4
}

const steps = [
  { number: 1, label: 'Trade Route' },
  { number: 2, label: 'Documentation' },
  { number: 3, label: 'Savings' },
  { number: 4, label: 'Review' }
]

export default function WizardProgressBar({ currentStep }: WizardProgressBarProps) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step, idx) => (
          <React.Fragment key={step.number}>
            {/* Step Circle */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div className={`
                w-12 h-12 rounded-full flex items-center justify-center font-bold text-base transition-colors
                ${step.number < currentStep ? 'bg-green-600 text-white' : ''}
                ${step.number === currentStep ? 'bg-indigo-600 text-white' : ''}
                ${step.number > currentStep ? 'border-2 border-gray-300 text-gray-400 bg-white' : ''}
              `}>
                {step.number < currentStep ? '✓' : step.number}
              </div>
              <span className="text-xs mt-2 text-gray-600 text-center">{step.label}</span>
            </div>

            {/* Connecting Line */}
            {idx < steps.length - 1 && (
              <div className={`
                flex-1 h-1 mx-2 transition-colors
                ${step.number < currentStep ? 'bg-green-600' : 'bg-gray-300'}
              `} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}
