import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Building2, CreditCard, BarChart2, ArrowLeft, Save, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import Navigation from '../components/Navigation'
import { getProfile, updateProfile, UserProfile } from '../services/api'
import { usePageTitle } from '../hooks/usePageTitle'
import Footer from '../components/Footer'



// ── Helpers ──────────────────────────────────────────────────────────────────

function formatMemberSince(dateStr: string | null): string {
  if (!dateStr) return 'Unknown'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
}

interface PlanMeta {
  label: string
  badgeClass: string
  price: string | null
}

function getPlanMeta(role: string): PlanMeta {
  switch (role) {
    case 'pro':
      return { label: 'Pro Plan', badgeClass: 'bg-blue-100 text-blue-800 border border-blue-200', price: '$49/mo' }
    case 'enterprise':
      return { label: 'Enterprise Plan', badgeClass: 'bg-yellow-100 text-yellow-800 border border-yellow-200', price: '$199/mo' }
    case 'consultant':
      return { label: 'Consultant Plan', badgeClass: 'bg-teal-100 text-teal-800 border border-teal-200', price: '$499/mo' }
    case 'admin':
    case 'superadmin':
      return { label: 'Admin', badgeClass: 'bg-red-100 text-red-800 border border-red-200', price: null }
    default:
      return { label: 'Free Plan', badgeClass: 'bg-gray-100 text-gray-700 border border-gray-200', price: null }
  }
}

function isPaidTier(role: string): boolean {
  return ['pro', 'enterprise', 'consultant'].includes(role)
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function AccountPage() {
  usePageTitle('Account')
  const navigate = useNavigate()
  const isAuthenticated = !!localStorage.getItem('token')

  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [form, setForm] = useState({ full_name: '', company_name: '' })

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login')
      return
    }
    loadProfile()
  }, [])

  async function loadProfile() {
    setLoading(true)
    try {
      const data = await getProfile()
      setProfile(data)
      setForm({
        full_name: data.full_name ?? '',
        company_name: data.company_name ?? '',
      })
    } catch {
      toast.error('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/'
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    try {
      await updateProfile({ full_name: form.full_name, company_name: form.company_name })
      setSaved(true)
      toast.success('Profile updated')
      setTimeout(() => setSaved(false), 2500)
      // Refresh profile so header reflects new name
      await loadProfile()
    } catch {
      toast.error('Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  // ── Loading skeleton ───────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />
        <div className="max-w-3xl mx-auto px-4 py-10 space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-white rounded-xl shadow-card border border-gray-100 p-6 animate-pulse">
              <div className="h-5 bg-gray-200 rounded w-1/3 mb-4" />
              <div className="h-4 bg-gray-100 rounded w-2/3" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!profile) return null

  const plan = getPlanMeta(profile.role)
  const { usage } = profile
  const lookupPct =
    usage.lookup_limit != null && usage.lookup_limit > 0
      ? Math.min(100, Math.round((usage.monthly_calculations / usage.lookup_limit) * 100))
      : null

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />

      {/* Page header band */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center space-x-1.5 text-sm text-gray-500 hover:text-brand-navy transition-colors mb-3"
          >
            <ArrowLeft size={15} />
            <span>Back to Dashboard</span>
          </button>
          <div className="flex items-center space-x-3">
            <div className="bg-brand-navy/10 rounded-xl p-2.5">
              <User size={22} className="text-brand-navy" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-brand-navy">My Account</h1>
              <p className="text-sm text-gray-500">Manage your profile and subscription</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">

        {/* ── Profile Card ──────────────────────────────────────────────── */}
        <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
          <div className="flex items-center space-x-2 mb-5">
            <User size={18} className="text-brand-blue" />
            <h2 className="text-base font-semibold text-brand-navy">Profile Information</h2>
          </div>

          <form onSubmit={handleSave} className="space-y-4">
            {/* Email — read-only */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
              <input
                type="email"
                value={profile.email}
                readOnly
                className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 text-sm cursor-not-allowed"
              />
              <p className="text-xs text-gray-400 mt-1">Email cannot be changed</p>
            </div>

            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                value={form.full_name}
                onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
                placeholder="Your full name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/30 focus:border-brand-blue transition-colors"
              />
            </div>

            {/* Company Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <span className="inline-flex items-center space-x-1">
                  <Building2 size={13} className="text-gray-500" />
                  <span>Company Name</span>
                </span>
              </label>
              <input
                type="text"
                value={form.company_name}
                onChange={e => setForm(f => ({ ...f, company_name: e.target.value }))}
                placeholder="Your company name"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/30 focus:border-brand-blue transition-colors"
              />
            </div>

            <div className="pt-1">
              <button
                type="submit"
                disabled={saving}
                className="inline-flex items-center space-x-2 px-5 py-2 bg-brand-navy text-white text-sm font-medium rounded-lg hover:bg-brand-navy/90 transition-colors disabled:opacity-60"
              >
                {saved ? (
                  <>
                    <CheckCircle size={15} />
                    <span>Saved</span>
                  </>
                ) : saving ? (
                  <>
                    <div className="h-4 w-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save size={15} />
                    <span>Save Changes</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* ── Subscription Plan Card ────────────────────────────────────── */}
        <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
          <div className="flex items-center space-x-2 mb-5">
            <CreditCard size={18} className="text-brand-blue" />
            <h2 className="text-base font-semibold text-brand-navy">Subscription Plan</h2>
          </div>

          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center space-x-3">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${plan.badgeClass}`}>
                {plan.label}
              </span>
              {plan.price && (
                <span className="text-sm text-gray-500">{plan.price}</span>
              )}
            </div>

            <div>
              {isPaidTier(profile.role) ? (
                <button
                  onClick={() => navigate('/billing')}
                  className="px-4 py-2 text-sm font-medium border border-brand-blue text-brand-blue rounded-lg hover:bg-brand-blue/5 transition-colors"
                >
                  Manage Billing
                </button>
              ) : !['admin', 'superadmin'].includes(profile.role) ? (
                <button
                  onClick={() => navigate('/pricing')}
                  className="px-4 py-2 text-sm font-medium bg-brand-gold text-white rounded-lg hover:bg-brand-gold/90 transition-colors"
                >
                  Upgrade Plan
                </button>
              ) : null}
            </div>
          </div>

          {!isPaidTier(profile.role) && !['admin', 'superadmin'].includes(profile.role) && (
            <p className="text-xs text-gray-400 mt-3">
              Upgrade to Pro for unlimited lookups, more watchlists, and advanced exports.
            </p>
          )}
        </div>

        {/* ── Usage Stats Card ──────────────────────────────────────────── */}
        <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
          <div className="flex items-center space-x-2 mb-5">
            <BarChart2 size={18} className="text-brand-blue" />
            <h2 className="text-base font-semibold text-brand-navy">Usage Statistics</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Monthly Lookups */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Monthly Lookups</p>
              <p className="text-2xl font-bold text-brand-navy">
                {usage.monthly_calculations}
                <span className="text-sm font-normal text-gray-400 ml-1">
                  / {usage.lookup_limit != null ? usage.lookup_limit : '∞'}
                </span>
              </p>
              {lookupPct !== null && (
                <div className="mt-2">
                  <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        lookupPct >= 90 ? 'bg-red-500' : lookupPct >= 70 ? 'bg-brand-gold' : 'bg-brand-teal'
                      }`}
                      style={{ width: `${lookupPct}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{lookupPct}% used this month</p>
                </div>
              )}
            </div>

            {/* Saved Analyses */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Saved Analyses</p>
              <p className="text-2xl font-bold text-brand-navy">{usage.saved_analyses}</p>
              <p className="text-xs text-gray-400 mt-1">Across all tools</p>
            </div>

            {/* Member Since */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Member Since</p>
              <p className="text-lg font-bold text-brand-navy leading-tight">
                {formatMemberSince(profile.created_at)}
              </p>
              <p className="text-xs text-gray-400 mt-1">Account created</p>
            </div>
          </div>
        </div>

        {/* ── Quick Actions ─────────────────────────────────────────────── */}
        <div className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
          <h2 className="text-base font-semibold text-brand-navy mb-4">Quick Actions</h2>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => navigate('/saved')}
              className="px-4 py-2 text-sm font-medium bg-brand-blue/10 text-brand-blue rounded-lg hover:bg-brand-blue/20 transition-colors"
            >
              View Saved Analyses
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 text-sm font-medium bg-brand-navy/10 text-brand-navy rounded-lg hover:bg-brand-navy/20 transition-colors"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => navigate('/pricing')}
              className="px-4 py-2 text-sm font-medium bg-brand-gold/10 text-brand-gold rounded-lg hover:bg-brand-gold/20 transition-colors"
            >
              Pricing &amp; Plans
            </button>
          </div>
        </div>

      </div>
      <Footer />
    </div>
  )
}
