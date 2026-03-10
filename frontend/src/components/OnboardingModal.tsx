import { useState } from 'react'
import {
  Zap,
  Scissors,
  Layers,
  Car,
  Home,
  Leaf,
  Droplets,
  Package,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  X,
  Flame,
} from 'lucide-react'
import { api } from '../services/api'

interface Props {
  show: boolean
  onComplete: () => void
}

// ---------------------------------------------------------------------------
// Step 1 — import categories
// ---------------------------------------------------------------------------
const CATEGORIES = [
  { id: 'electronics',   label: 'Electronics',         Icon: Zap      },
  { id: 'apparel',       label: 'Apparel & Footwear',  Icon: Scissors },
  { id: 'metals',        label: 'Metals & Steel',      Icon: Layers   },
  { id: 'auto',          label: 'Auto Parts',          Icon: Car      },
  { id: 'furniture',     label: 'Furniture',           Icon: Home     },
  { id: 'food',          label: 'Food & Agriculture',  Icon: Leaf     },
  { id: 'chemicals',     label: 'Chemicals',           Icon: Droplets },
  { id: 'other',         label: 'Other',               Icon: Package  },
]

// ---------------------------------------------------------------------------
// Step 2 — source countries
// ---------------------------------------------------------------------------
const COUNTRIES = [
  { code: 'CN', label: 'China',       flag: '🇨🇳' },
  { code: 'VN', label: 'Vietnam',     flag: '🇻🇳' },
  { code: 'MX', label: 'Mexico',      flag: '🇲🇽' },
  { code: 'CA', label: 'Canada',      flag: '🇨🇦' },
  { code: 'DE', label: 'Germany',     flag: '🇩🇪' },
  { code: 'JP', label: 'Japan',       flag: '🇯🇵' },
  { code: 'IN', label: 'India',       flag: '🇮🇳' },
  { code: 'KR', label: 'South Korea', flag: '🇰🇷' },
  { code: 'TW', label: 'Taiwan',      flag: '🇹🇼' },
  { code: 'BD', label: 'Bangladesh',  flag: '🇧🇩' },
]

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function primaryCategory(selectedIds: string[]): string {
  if (selectedIds.length === 0) return 'My'
  const first = CATEGORIES.find(c => c.id === selectedIds[0])
  return first ? first.label : 'My'
}

// ---------------------------------------------------------------------------
// Progress indicator
// ---------------------------------------------------------------------------
function StepDots({ step }: { step: number }) {
  return (
    <div className="flex items-center justify-center space-x-2 py-4">
      {[1, 2, 3].map(s => (
        <div
          key={s}
          className={`rounded-full transition-all duration-300 ${
            s === step
              ? 'w-6 h-2.5 bg-brand-teal'
              : s < step
              ? 'w-2.5 h-2.5 bg-brand-teal/50'
              : 'w-2.5 h-2.5 bg-gray-200'
          }`}
        />
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export function OnboardingModal({ show, onComplete }: Props) {
  const [step, setStep] = useState(1)
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [selectedCountries, setSelectedCountries] = useState<string[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  if (!show) return null

  // ---- shared skip / complete ----
  const skip = () => {
    localStorage.setItem('onboarding_done', '1')
    onComplete()
  }

  // ---- toggle helpers ----
  const toggleCategory = (id: string) => {
    setSelectedCategories(prev =>
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    )
  }

  const toggleCountry = (code: string) => {
    setSelectedCountries(prev =>
      prev.includes(code) ? prev.filter(c => c !== code) : [...prev, code]
    )
  }

  // ---- step 3 derived values ----
  const watchlistName = `My ${primaryCategory(selectedCategories)} Imports`
  const watchedCountryLabels = selectedCountries
    .map(code => COUNTRIES.find(c => c.code === code))
    .filter(Boolean)
    .map(c => `${c!.flag} ${c!.label}`)

  // ---- final action ----
  const handleCreateWatchlist = async () => {
    setSaving(true)
    setError('')
    try {
      await api.post('/watchlists', {
        name: watchlistName,
        hs_codes: [],
        countries: selectedCountries,
        alert_preferences: { email: true, digest: 'daily' },
      })
    } catch {
      // Non-fatal — proceed even if watchlist creation fails
    } finally {
      setSaving(false)
      localStorage.setItem('onboarding_done', '1')
      onComplete()
    }
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <div
      className="fixed inset-0 bg-brand-navy/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={e => { if (e.target === e.currentTarget) skip() }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">

        {/* ── Top progress bar ─────────────────────────────────────── */}
        <div className="h-1.5 bg-gray-100">
          <div
            className="h-full bg-brand-teal transition-all duration-500"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>

        {/* ── Header ───────────────────────────────────────────────── */}
        <div className="flex items-center justify-between px-6 pt-5 pb-3">
          <div className="flex items-center space-x-2">
            <div className="bg-brand-teal rounded-lg p-1.5">
              <Flame size={15} className="text-white" />
            </div>
            <span className="font-bold text-brand-navy text-sm tracking-tight">
              TariffNavigator Setup
            </span>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-xs text-gray-400">Step {step} of 3</span>
            <button
              onClick={skip}
              className="text-gray-300 hover:text-gray-500 transition-colors"
              aria-label="Close"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* ── Step dots ────────────────────────────────────────────── */}
        <StepDots step={step} />

        {/* ================================================================
            STEP 1 — What do you import?
        ================================================================ */}
        {step === 1 && (
          <div className="px-6 pb-6">
            <h2 className="text-xl font-bold text-brand-navy mb-1">
              What do you import?
            </h2>
            <p className="text-sm text-gray-500 mb-5">
              Select all categories that apply. We'll pre-load relevant HTS codes for you.
            </p>

            <div className="grid grid-cols-4 gap-2.5 mb-6">
              {CATEGORIES.map(({ id, label, Icon }) => {
                const active = selectedCategories.includes(id)
                return (
                  <button
                    key={id}
                    onClick={() => toggleCategory(id)}
                    className={`relative flex flex-col items-center justify-center gap-1.5 py-4 px-2 rounded-xl border-2 transition-all text-center ${
                      active
                        ? 'border-brand-teal bg-teal-50 shadow-sm'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {active && (
                      <CheckCircle
                        size={13}
                        className="absolute top-1.5 right-1.5 text-brand-teal"
                      />
                    )}
                    <Icon
                      size={22}
                      className={active ? 'text-brand-teal' : 'text-gray-400'}
                    />
                    <span
                      className={`text-xs font-medium leading-tight ${
                        active ? 'text-brand-teal' : 'text-gray-600'
                      }`}
                    >
                      {label}
                    </span>
                  </button>
                )
              })}
            </div>

            <div className="flex items-center justify-between">
              <button
                onClick={skip}
                className="text-xs text-gray-400 hover:text-gray-600 underline underline-offset-2"
              >
                Skip for now
              </button>
              <button
                onClick={() => setStep(2)}
                disabled={selectedCategories.length === 0}
                className="flex items-center space-x-2 px-5 py-2.5 bg-brand-navy text-white text-sm font-bold rounded-xl hover:bg-brand-navy/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <span>Next</span>
                <ArrowRight size={15} />
              </button>
            </div>
          </div>
        )}

        {/* ================================================================
            STEP 2 — Which countries do you source from?
        ================================================================ */}
        {step === 2 && (
          <div className="px-6 pb-6">
            <h2 className="text-xl font-bold text-brand-navy mb-1">
              Which countries do you source from?
            </h2>
            <p className="text-sm text-gray-500 mb-5">
              We'll monitor tariff changes for these origins and alert you to rate changes.
            </p>

            <div className="grid grid-cols-2 gap-2 mb-6">
              {COUNTRIES.map(({ code, label, flag }) => {
                const active = selectedCountries.includes(code)
                return (
                  <label
                    key={code}
                    className={`flex items-center space-x-3 p-3 rounded-xl border-2 cursor-pointer transition-all ${
                      active
                        ? 'border-brand-teal bg-teal-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={active}
                      onChange={() => toggleCountry(code)}
                      className="sr-only"
                    />
                    <div
                      className={`w-4 h-4 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors ${
                        active ? 'border-brand-teal bg-brand-teal' : 'border-gray-300'
                      }`}
                    >
                      {active && (
                        <svg
                          viewBox="0 0 10 8"
                          fill="none"
                          className="w-2.5 h-2"
                        >
                          <path
                            d="M1 4l2.5 2.5L9 1"
                            stroke="white"
                            strokeWidth="1.6"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      )}
                    </div>
                    <span className="text-lg leading-none">{flag}</span>
                    <span
                      className={`text-sm font-medium ${
                        active ? 'text-brand-teal' : 'text-gray-700'
                      }`}
                    >
                      {label}
                    </span>
                  </label>
                )
              })}
            </div>

            <div className="flex items-center justify-between">
              <button
                onClick={skip}
                className="text-xs text-gray-400 hover:text-gray-600 underline underline-offset-2"
              >
                Skip for now
              </button>
              <div className="flex space-x-2">
                <button
                  onClick={() => setStep(1)}
                  className="flex items-center space-x-1 px-4 py-2.5 border border-gray-200 text-gray-600 text-sm rounded-xl hover:bg-gray-50 transition-colors"
                >
                  <ArrowLeft size={14} />
                  <span>Back</span>
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={selectedCountries.length === 0}
                  className="flex items-center space-x-2 px-5 py-2.5 bg-brand-navy text-white text-sm font-bold rounded-xl hover:bg-brand-navy/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <span>Next</span>
                  <ArrowRight size={15} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================
            STEP 3 — Create your first watchlist
        ================================================================ */}
        {step === 3 && (
          <div className="px-6 pb-6">
            <h2 className="text-xl font-bold text-brand-navy mb-1">
              Create your first watchlist
            </h2>
            <p className="text-sm text-gray-500 mb-5">
              We'll set up alerts so you're notified the moment tariff rates change.
            </p>

            {/* Watchlist preview card */}
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-5 space-y-3">
              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                  Watchlist Name
                </p>
                <p className="text-base font-bold text-brand-navy">{watchlistName}</p>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                  Monitoring Countries
                </p>
                {watchedCountryLabels.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {watchedCountryLabels.map(c => (
                      <span
                        key={c}
                        className="inline-flex items-center px-2.5 py-1 bg-teal-50 border border-brand-teal/30 text-brand-teal text-xs font-medium rounded-full"
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 italic">No countries selected</p>
                )}
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">
                  Alert Preferences
                </p>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <CheckCircle size={13} className="text-brand-teal flex-shrink-0" />
                  <span>Email alerts enabled &mdash; daily digest</span>
                </div>
              </div>
            </div>

            {error && (
              <p className="text-xs text-red-500 mb-3">{error}</p>
            )}

            <button
              onClick={handleCreateWatchlist}
              disabled={saving}
              className="w-full flex items-center justify-center space-x-2 py-3 bg-brand-teal text-white text-sm font-bold rounded-xl hover:bg-brand-teal/90 transition-colors disabled:opacity-60 disabled:cursor-not-allowed mb-3"
            >
              {saving ? (
                <>
                  <svg
                    className="animate-spin h-4 w-4 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v8H4z"
                    />
                  </svg>
                  <span>Creating Watchlist…</span>
                </>
              ) : (
                <>
                  <CheckCircle size={16} />
                  <span>Create Watchlist &amp; Get Started</span>
                </>
              )}
            </button>

            <div className="flex items-center justify-between">
              <button
                onClick={skip}
                className="text-xs text-gray-400 hover:text-gray-600 underline underline-offset-2"
              >
                Skip for now
              </button>
              <button
                onClick={() => setStep(2)}
                className="flex items-center space-x-1 px-4 py-2 border border-gray-200 text-gray-600 text-sm rounded-xl hover:bg-gray-50 transition-colors"
              >
                <ArrowLeft size={14} />
                <span>Back</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
