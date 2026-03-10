import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { Lock, Eye, EyeOff, Flame, CheckCircle } from 'lucide-react'
import { usePageTitle } from '../hooks/usePageTitle'
import Footer from '../components/Footer'

export default function ResetPasswordPage() {
  usePageTitle('Set New Password')
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token') || ''

  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  const apiUrl = import.meta.env.VITE_API_URL || 'https://tariffnavigator-backend.onrender.com/api/v1'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (password.length < 8) { setError('Password must be at least 8 characters'); return }
    if (password !== confirm) { setError('Passwords do not match'); return }
    if (!token) { setError('Invalid reset link. Please request a new one.'); return }

    setLoading(true)
    try {
      const res = await fetch(`${apiUrl}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Reset failed')
      setDone(true)
      setTimeout(() => navigate('/login'), 3000)
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 font-sans">
        <div className="bg-white rounded-2xl shadow-enterprise p-8 max-w-md w-full text-center">
          <p className="text-red-600 font-medium mb-4">Invalid or missing reset link.</p>
          <Link to="/forgot-password" className="text-brand-teal hover:underline text-sm font-medium">
            Request a new reset link →
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col font-sans">
      <div className="flex flex-1">
        {/* Left panel */}
        <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 relative overflow-hidden"
             style={{ background: 'linear-gradient(145deg, #152B47 0%, #1E3A5F 40%, #1a4a6a 100%)' }}>
          <div className="absolute top-0 right-0 w-72 h-72 bg-brand-teal/20 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-brand-blue/20 rounded-full translate-y-1/2 -translate-x-1/2 blur-3xl pointer-events-none" />

          <div className="relative z-10 flex items-center space-x-3">
            <div className="bg-brand-teal rounded-lg p-2 shadow-glow-teal">
              <Flame className="h-6 w-6 text-white" />
            </div>
            <div className="leading-tight">
              <span className="block text-white font-bold text-lg">TariffNavigator</span>
              <span className="block text-xs text-blue-300">DJ AI Business Consultant</span>
            </div>
          </div>

          <div className="relative z-10">
            <h1 className="text-3xl font-bold text-white leading-tight mb-4">
              Choose a strong new password
            </h1>
            <p className="text-blue-200 mb-8">
              Transforming Business, Rising Above the Challenges
            </p>
            <div className="space-y-4">
              {['Use at least 8 characters', 'Mix letters, numbers, and symbols', 'Don\'t reuse a password from another site'].map(tip => (
                <div key={tip} className="flex items-center space-x-3">
                  <div className="bg-brand-teal/20 text-brand-teal rounded-lg p-2 shrink-0">
                    <CheckCircle className="h-4 w-4" />
                  </div>
                  <p className="text-blue-100 text-sm">{tip}</p>
                </div>
              ))}
            </div>
          </div>

          <p className="relative z-10 text-blue-400 text-sm">DJ AI Business Consultant • Syracuse, NY</p>
        </div>

        {/* Right panel */}
        <div className="flex-1 flex items-center justify-center p-6 bg-gray-50/50">
          <div className="w-full max-w-md">
            <div className="lg:hidden flex items-center justify-center space-x-3 mb-8">
              <div className="bg-brand-navy rounded-lg p-2">
                <Flame className="h-6 w-6 text-white" />
              </div>
              <span className="text-brand-navy font-bold text-xl">TariffNavigator</span>
            </div>

            <div className="bg-white rounded-2xl shadow-enterprise p-8">
              {done ? (
                <div className="text-center py-4">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  </div>
                  <h2 className="text-xl font-bold text-brand-navy mb-2">Password updated!</h2>
                  <p className="text-gray-500 text-sm mb-4">Redirecting you to sign in…</p>
                  <Link to="/login" className="text-brand-teal hover:underline text-sm font-medium">
                    Sign in now →
                  </Link>
                </div>
              ) : (
                <>
                  <div className="mb-8">
                    <h2 className="text-2xl font-bold text-brand-navy">Set new password</h2>
                    <p className="text-gray-500 text-sm mt-1">Enter and confirm your new password below.</p>
                  </div>

                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">New Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                        <input
                          type={showPassword ? 'text' : 'password'}
                          required
                          value={password}
                          onChange={e => setPassword(e.target.value)}
                          className="w-full pl-10 pr-10 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
                          placeholder="Min. 8 characters"
                        />
                        <button type="button" onClick={() => setShowPassword(v => !v)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">Confirm Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                        <input
                          type={showPassword ? 'text' : 'password'}
                          required
                          value={confirm}
                          onChange={e => setConfirm(e.target.value)}
                          className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
                          placeholder="Repeat your password"
                        />
                      </div>
                    </div>

                    {error && (
                      <div className="flex items-start space-x-2 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                        <span className="mt-0.5 shrink-0">⚠</span>
                        <span>{error}</span>
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={loading}
                      style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #264875 100%)' }}
                      className="w-full py-3 text-white font-semibold rounded-xl hover:opacity-90 transition-all active:scale-[0.98] flex items-center justify-center space-x-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading
                        ? <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        : <span>Update Password</span>
                      }
                    </button>
                  </form>
                </>
              )}
            </div>

            <p className="text-center text-sm text-gray-500 mt-5">
              <Link to="/login" className="text-brand-teal hover:underline font-medium">← Back to sign in</Link>
            </p>
            <p className="text-center text-xs text-gray-400 mt-3">DJ AI Business Consultant • Syracuse, NY</p>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  )
}
