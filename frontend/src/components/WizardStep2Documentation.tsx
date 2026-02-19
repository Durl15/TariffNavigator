import React, { useState } from 'react'
import { ArrowLeft, ArrowRight, AlertCircle, CheckCircle, FileText, Truck, Shield, ChevronDown } from 'lucide-react'
import type { WizardState } from '../pages/FTAWizardPage'

interface Step2Props {
  state: WizardState
  onBack: () => void
  onNext: () => void
}

interface DocumentationSectionProps {
  id: string
  title: string
  icon: React.ReactNode
  expanded: boolean
  onToggle: () => void
  children: React.ReactNode
}

function DocumentationSection({ id, title, icon, expanded, onToggle, children }: DocumentationSectionProps) {
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="text-indigo-600">{icon}</div>
          <h3 className="font-medium text-gray-900">{title}</h3>
        </div>
        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </button>
      {expanded && (
        <div className="p-4 bg-white border-t border-gray-200">
          {children}
        </div>
      )}
    </div>
  )
}

export default function WizardStep2Documentation({ state, onBack, onNext }: Step2Props) {
  const [expandedSection, setExpandedSection] = useState<string | null>('certificate')

  if (!state.ftaEligible) {
    return (
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">FTA Status</h2>

        <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg mb-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-yellow-900 mb-2">No FTA Benefits Available</h3>
              <p className="text-yellow-800 text-sm">
                Unfortunately, there is no Free Trade Agreement between {state.originCountry} and {state.destinationCountry}
                {' '}for HS code {state.hsCode}. Standard MFN tariff rates will apply.
              </p>
            </div>
          </div>
        </div>

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
            onClick={onNext}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
          >
            Continue to Calculation
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    )
  }

  // FTA Eligible - show documentation
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Required Documentation</h2>

      {/* FTA Eligible Banner */}
      <div className="p-6 bg-green-50 border border-green-200 rounded-lg mb-6">
        <div className="flex items-start gap-3">
          <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
          <div>
            <h3 className="font-bold text-green-900 mb-1">✅ Eligible for {state.ftaName}!</h3>
            <p className="text-green-800 text-sm">
              Your shipment qualifies for preferential tariff rates under the {state.ftaName} agreement.
              To claim these benefits, you'll need to provide the following documentation:
            </p>
          </div>
        </div>
      </div>

      {/* Documentation Sections */}
      <div className="space-y-4 mb-6">
        {/* Certificate of Origin */}
        <DocumentationSection
          id="certificate"
          title="Certificate of Origin"
          icon={<FileText className="w-5 h-5" />}
          expanded={expandedSection === 'certificate'}
          onToggle={() => setExpandedSection(expandedSection === 'certificate' ? null : 'certificate')}
        >
          <p className="text-gray-700 mb-3">
            A Certificate of Origin (COO) is an official document certifying that goods in a shipment
            were produced, manufactured, or processed in a particular country.
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>Must be issued by an authorized chamber of commerce or government agency</li>
            <li>Valid for 12 months from date of issue</li>
            <li>Must include HS code, product description, and origin details</li>
            <li>Original document required (copy accepted for some agreements)</li>
          </ul>
        </DocumentationSection>

        {/* Direct Shipment Rules */}
        <DocumentationSection
          id="shipment"
          title="Direct Shipment Rules"
          icon={<Truck className="w-5 h-5" />}
          expanded={expandedSection === 'shipment'}
          onToggle={() => setExpandedSection(expandedSection === 'shipment' ? null : 'shipment')}
        >
          <p className="text-gray-700 mb-3">
            To qualify for FTA benefits, goods must be shipped directly from the origin country
            to the destination country without passing through non-member countries.
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>Direct shipment from {state.originCountry} to {state.destinationCountry} required</li>
            <li>Transit through third countries allowed if goods remain under customs control</li>
            <li>Transshipment prohibited unless goods do not undergo further processing</li>
            <li>Through bill of lading required as proof of direct shipment</li>
          </ul>
        </DocumentationSection>

        {/* Product-Specific Rules */}
        <DocumentationSection
          id="rules"
          title="Product-Specific Rules of Origin"
          icon={<Shield className="w-5 h-5" />}
          expanded={expandedSection === 'rules'}
          onToggle={() => setExpandedSection(expandedSection === 'rules' ? null : 'rules')}
        >
          <p className="text-gray-700 mb-3">
            Additional origin requirements specific to HS code {state.hsCode}:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 text-sm">
            <li>Product must undergo substantial transformation in origin country</li>
            <li>Minimum local content requirement: Check agreement-specific thresholds</li>
            <li>Change of tariff classification may be required</li>
            <li>Detailed manufacturing records must be maintained for verification</li>
          </ul>
        </DocumentationSection>
      </div>

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
          onClick={onNext}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
        >
          Calculate Savings
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
