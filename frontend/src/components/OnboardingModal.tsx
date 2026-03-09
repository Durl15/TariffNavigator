import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Flame, ArrowRight, CheckCircle, X } from 'lucide-react'

const STORAGE_KEY = 'tn_onboarding_v1'

const PERSONAS = [
  { id: 'importer', label: 'Product Importer', desc: 'I buy goods from overseas and import to the US', icon: '📦' },
  { id: 'manufacturer', label: 'Manufacturer', desc: 'I use imported materials or components in production', icon: '🏭' },
  { id: 'consultant', label: 'Trade Consultant / Broker', desc: 'I advise clients on customs and trade compliance', icon: '💼' },
  { id: 'ecommerce', label: 'E-Commerce Seller', desc: 'I sell products online that ship from overseas', icon: '🛒' },
]

const CHALLENGES = [
  { id: 'costs', label: 'Tariff Costs Are Crushing My Margins', icon: '💸', tool: '/calculator' },
  { id: 'compliance', label: 'Worried About CBP Penalties', icon: '⚖️', tool: '/supply-chain' },
  { id: 'cashflow', label: 'Cash Flow Stress at Port', icon: '🏦', tool: '/cashflow' },
  { id: 'sourcing', label: 'Need to Find Cheaper Sourcing', icon: '🌏', tool: '/sourcing' },
]

const TOOL_ROUTES: Record<string, { path: string; label: string }> = {
  costs: { path: '/calculator', label: 'Open Tariff Calculator' },
  compliance: { path: '/supply-chain', label: 'Scan Supply Chain Risk' },
  cashflow: { path: '/cashflow', label: 'Forecast Cash Flow' },
  sourcing: { path: '/sourcing', label: 'Find Alternative Sourcing' },
}

export function OnboardingModal() {
  const navigate = useNavigate()
  const [visible, setVisible] = useState(false)
  const [step, setStep] = useState(1)
  const [persona, setPersona] = useState('')
  const [challenge, setChallenge] = useState('')

  useEffect(() => {
    const seen = localStorage.getItem(STORAGE_KEY)
    const token = localStorage.getItem('token')
    if (!seen && token) {
      // Small delay so the page renders first
      const t = setTimeout(() => setVisible(true), 800)
      return () => clearTimeout(t)
    }
  }, [])

  const dismiss = () => {
    localStorage.setItem(STORAGE_KEY, 'done')
    setVisible(false)
  }

  const finish = () => {
    localStorage.setItem(STORAGE_KEY, 'done')
    setVisible(false)
    const route = TOOL_ROUTES[challenge]
    if (route) navigate(route.path)
    else navigate('/calculator')
  }

  if (!visible) return null

  const totalSteps = 3

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={e => { if (e.target === e.currentTarget) dismiss() }}>
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden">
        {/* Progress bar */}
        <div className="h-1 bg-gray-100">
          <div
            className="h-full bg-brand-teal transition-all duration-500"
            style={{ width: `${(step / totalSteps) * 100}%` }}
          />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div className="flex items-center space-x-2">
            <div className="bg-brand-teal rounded-lg p-1.5">
              <Flame size={16} className="text-white" />
            </div>
            <span className="font-bold text-brand-navy text-sm">TariffNavigator Setup</span>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-xs text-gray-400">Step {step} of {totalSteps}</span>
            <button onClick={dismiss} className="text-gray-400 hover:text-gray-600">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Step 1: Welcome */}
        {step === 1 && (
          <div className="px-6 py-8 text-center">
            <div className="w-16 h-16 bg-brand-navy rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Flame size={32} className="text-brand-teal" />
            </div>
            <h2 className="text-2xl font-bold text-brand-navy mb-2">Welcome to TariffNavigator</h2>
            <p className="text-gray-500 mb-6">
              AI-powered tariff intelligence for American businesses. Let's get you set up in 60 seconds.
            </p>
            <div className="text-left space-y-3 mb-8">
              {[
                'Calculate stacked duties — Section 301, IEEPA, USMCA, all at once',
                'Recover up to 99% of duties you\'ve already paid',
                'Catch HTS misclassifications before CBP does',
                '"What if China snaps back to 145%?" — model it in seconds',
              ].map((item, i) => (
                <div key={i} className="flex items-center space-x-3">
                  <CheckCircle size={16} className="text-brand-teal flex-shrink-0" />
                  <p className="text-sm text-gray-700">{item}</p>
                </div>
              ))}
            </div>
            <button
              onClick={() => setStep(2)}
              className="w-full py-3 bg-brand-navy text-white font-bold rounded-xl hover:bg-brand-navy-dark transition-colors flex items-center justify-center space-x-2"
            >
              <span>Get Started</span>
              <ArrowRight size={16} />
            </button>
          </div>
        )}

        {/* Step 2: Persona */}
        {step === 2 && (
          <div className="px-6 py-7">
            <h2 className="text-xl font-bold text-brand-navy mb-1">What best describes you?</h2>
            <p className="text-gray-500 text-sm mb-5">We'll personalize your experience.</p>
            <div className="grid grid-cols-2 gap-3 mb-6">
              {PERSONAS.map(p => (
                <button
                  key={p.id}
                  onClick={() => setPersona(p.id)}
                  className={`text-left p-4 rounded-xl border transition-all ${
                    persona === p.id
                      ? 'border-brand-blue bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-2xl mb-2 block">{p.icon}</span>
                  <p className="font-semibold text-sm text-brand-navy">{p.label}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{p.desc}</p>
                </button>
              ))}
            </div>
            <div className="flex space-x-3">
              <button onClick={() => setStep(1)} className="px-4 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-sm hover:bg-gray-50">
                Back
              </button>
              <button
                onClick={() => persona ? setStep(3) : null}
                disabled={!persona}
                className="flex-1 py-2.5 bg-brand-navy text-white font-bold rounded-xl hover:bg-brand-navy-dark transition-colors disabled:opacity-40 flex items-center justify-center space-x-2"
              >
                <span>Continue</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Challenge */}
        {step === 3 && (
          <div className="px-6 py-7">
            <h2 className="text-xl font-bold text-brand-navy mb-1">What's your biggest challenge right now?</h2>
            <p className="text-gray-500 text-sm mb-5">We'll show you the most relevant tool first.</p>
            <div className="space-y-2 mb-6">
              {CHALLENGES.map(c => (
                <button
                  key={c.id}
                  onClick={() => setChallenge(c.id)}
                  className={`w-full text-left p-4 rounded-xl border flex items-center space-x-3 transition-all ${
                    challenge === c.id
                      ? 'border-brand-blue bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-2xl flex-shrink-0">{c.icon}</span>
                  <p className="font-medium text-sm text-brand-navy">{c.label}</p>
                  {challenge === c.id && <CheckCircle size={16} className="text-brand-blue ml-auto flex-shrink-0" />}
                </button>
              ))}
            </div>
            <div className="flex space-x-3">
              <button onClick={() => setStep(2)} className="px-4 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-sm hover:bg-gray-50">
                Back
              </button>
              <button
                onClick={finish}
                disabled={!challenge}
                className="flex-1 py-3 bg-brand-teal text-white font-bold rounded-xl hover:bg-brand-teal-dark transition-colors disabled:opacity-40 flex items-center justify-center space-x-2"
              >
                <span>{challenge ? TOOL_ROUTES[challenge]?.label : 'Go to Dashboard'}</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
