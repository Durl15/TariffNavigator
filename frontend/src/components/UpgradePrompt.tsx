import { Link } from 'react-router-dom'
import { Lock, ArrowRight, X } from 'lucide-react'
import { useState } from 'react'

interface UpgradePromptProps {
  featureName: string
  requiredTier: 'Pro' | 'Enterprise'
  description?: string
  onDismiss?: () => void
  inline?: boolean  // true = inline banner, false = modal overlay
}

const TIER_PRICE: Record<string, string> = {
  Pro: '$49/mo',
  Enterprise: '$199/mo',
}

const TIER_PERKS: Record<string, string[]> = {
  Pro: ['All 10 compliance tools', 'Unlimited tariff lookups', 'Product catalog analysis', 'PDF/CSV exports', 'Email alerts'],
  Enterprise: ['Everything in Pro', 'Scenario planner', 'Unlimited catalogs & users', 'API access', 'Priority support'],
}

export function UpgradePrompt({ featureName, requiredTier, description, onDismiss, inline = false }: UpgradePromptProps) {
  if (inline) {
    return (
      <div className="bg-gradient-to-r from-brand-navy to-brand-blue rounded-xl p-6 text-white">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <div className="bg-white/10 rounded-lg p-2 flex-shrink-0">
              <Lock size={20} className="text-brand-gold" />
            </div>
            <div>
              <p className="font-bold text-lg">{featureName} — {requiredTier} Feature</p>
              <p className="text-blue-200 text-sm mt-1">
                {description || `Upgrade to ${requiredTier} to unlock ${featureName} and all other advanced tools.`}
              </p>
              <div className="flex flex-wrap gap-2 mt-3">
                {TIER_PERKS[requiredTier].map(perk => (
                  <span key={perk} className="text-xs px-2.5 py-1 bg-white/10 rounded-full text-blue-100">{perk}</span>
                ))}
              </div>
            </div>
          </div>
          {onDismiss && (
            <button onClick={onDismiss} className="text-blue-300 hover:text-white ml-4 flex-shrink-0">
              <X size={18} />
            </button>
          )}
        </div>
        <div className="mt-5 flex flex-col sm:flex-row gap-3">
          <Link
            to="/pricing"
            className="flex items-center justify-center space-x-2 px-6 py-2.5 bg-brand-gold text-brand-navy font-bold rounded-lg hover:bg-brand-gold-light transition-colors text-sm"
          >
            <span>Upgrade to {requiredTier} — {TIER_PRICE[requiredTier]}</span>
            <ArrowRight size={14} />
          </Link>
          <Link
            to="/pricing"
            className="text-center px-6 py-2.5 border border-white/20 text-blue-200 hover:bg-white/10 rounded-lg text-sm transition-colors"
          >
            View all plans
          </Link>
        </div>
      </div>
    )
  }

  // Modal overlay
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-brand-navy rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Lock size={28} className="text-brand-gold" />
          </div>
          <h2 className="text-2xl font-bold text-brand-navy mb-2">{requiredTier} Feature</h2>
          <p className="text-gray-500 text-sm">
            {featureName} requires a {requiredTier} subscription.
          </p>
        </div>

        <ul className="space-y-2 mb-6">
          {TIER_PERKS[requiredTier].map(perk => (
            <li key={perk} className="flex items-center space-x-2 text-sm text-gray-700">
              <div className="w-5 h-5 rounded-full bg-brand-teal/10 flex items-center justify-center flex-shrink-0">
                <ArrowRight size={10} className="text-brand-teal" />
              </div>
              <span>{perk}</span>
            </li>
          ))}
        </ul>

        <Link
          to="/pricing"
          className="block w-full text-center py-3 bg-brand-navy text-white font-bold rounded-xl hover:bg-brand-navy-dark transition-colors mb-3"
        >
          Upgrade to {requiredTier} — {TIER_PRICE[requiredTier]}
        </Link>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="block w-full text-center py-2 text-gray-400 hover:text-gray-600 text-sm"
          >
            Maybe later
          </button>
        )}
      </div>
    </div>
  )
}

// Hook: check tier from JWT (simple decode, no verification needed)
export function useUserTier(): 'free' | 'pro' | 'enterprise' | 'consultant' {
  try {
    const token = localStorage.getItem('token')
    if (!token) return 'free'
    const payload = JSON.parse(atob(token.split('.')[1]))
    const role = payload.role || 'user'
    if (role === 'superadmin' || role === 'admin') return 'enterprise'
    if (role === 'consultant') return 'consultant'
    if (role === 'pro') return 'pro'
    return 'free'
  } catch {
    return 'free'
  }
}

// Convenience: banner that auto-shows if tier is insufficient
interface TierGateProps {
  requiredTier: 'pro' | 'enterprise'
  featureName: string
  description?: string
  children: React.ReactNode
}

export function TierGate({ requiredTier, featureName, description, children }: TierGateProps) {
  const tier = useUserTier()
  const [dismissed, setDismissed] = useState(false)

  const tierRank: Record<string, number> = { free: 0, pro: 1, enterprise: 2, consultant: 3 }
  const required = tierRank[requiredTier] ?? 1
  const current = tierRank[tier] ?? 0
  const hasAccess = current >= required

  if (hasAccess) return <>{children}</>

  if (dismissed) {
    // Show children but with a subtle banner
    return (
      <>
        <div className="mb-4 px-4 py-2 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center justify-between">
          <p className="text-xs text-yellow-700">
            <strong>{featureName}</strong> requires {requiredTier.charAt(0).toUpperCase() + requiredTier.slice(1)}.
            Results may be limited on the free tier.
          </p>
          <Link to="/pricing" className="text-xs text-brand-blue font-medium hover:underline ml-2 whitespace-nowrap">Upgrade →</Link>
        </div>
        {children}
      </>
    )
  }

  return (
    <UpgradePrompt
      featureName={featureName}
      requiredTier={requiredTier.charAt(0).toUpperCase() + requiredTier.slice(1) as 'Pro' | 'Enterprise'}
      description={description}
      onDismiss={() => setDismissed(true)}
      inline
    />
  )
}
