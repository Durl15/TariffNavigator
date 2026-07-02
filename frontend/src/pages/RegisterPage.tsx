import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Flame, Lock, Mail, User, ArrowRight, CheckCircle, Eye, EyeOff } from 'lucide-react';
import { usePageTitle } from '../hooks/usePageTitle';
import Footer from '../components/Footer';

const RegisterPage: React.FC = () => {
  usePageTitle('Create Account');
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [slowWarning, setSlowWarning] = useState(false);

  // Inline validation errors
  const passwordTooShort = password.length > 0 && password.length < 8;
  const passwordMismatch = confirmPassword.length > 0 && password !== confirmPassword;

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    setSlowWarning(false);
    const slowTimer = setTimeout(() => setSlowWarning(true), 6000);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'https://tariffnavigator-backend.onrender.com/api/v1';
      const response = await fetch(`${apiUrl}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });

      if (!response.ok) {
        const data = await response.json();
        const detail: string = data.detail || 'Registration failed';
        if (detail.toLowerCase().includes('already registered') || detail.toLowerCase().includes('already exists')) {
          throw new Error('An account with this email already exists. Sign in instead.');
        }
        throw new Error(detail);
      }

      const data = await response.json();
      clearTimeout(slowTimer);
      localStorage.setItem('token', data.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'An error occurred during registration');
    } finally {
      clearTimeout(slowTimer);
      setLoading(false);
      setSlowWarning(false);
    }
  };

  const features = [
    'Free forever — no credit card required',
    '10 tariff lookups per month on the free plan',
    'Upgrade anytime to Pro for unlimited lookups',
  ];

  return (
    <div className="min-h-screen flex font-sans">

      {/* Left panel — branding */}
      <div
        className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 relative overflow-hidden"
        style={{ background: 'linear-gradient(145deg, #152B47 0%, #1E3A5F 40%, #1a4a6a 100%)' }}
      >
        {/* Decorative blobs */}
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
          <h1 className="text-4xl font-bold text-white leading-tight mb-4">
            Start protecting your business from tariff chaos
          </h1>
          <p className="text-blue-200 text-lg mb-10">
            Transforming Business, Rising Above the Challenges
          </p>

          <div className="space-y-5">
            {features.map((text, idx) => {
              const iconStyles = [
                'bg-brand-teal/20 text-brand-teal',
                'bg-brand-blue/20 text-brand-blue',
                'bg-brand-gold/20 text-brand-gold',
              ];
              return (
                <div key={text} className="flex items-start space-x-3">
                  <div className={`${iconStyles[idx]} rounded-lg p-2 mt-0.5 flex-shrink-0`}>
                    <CheckCircle className="h-4 w-4" />
                  </div>
                  <p className="text-blue-100 text-sm leading-relaxed">{text}</p>
                </div>
              );
            })}
          </div>
        </div>

        <p className="relative z-10 text-blue-400 text-sm">
          DJ AI Business Consultant • Syracuse, NY
        </p>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-gray-50/50">
        <div className="w-full max-w-md">

          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center space-x-3 mb-8">
            <div className="bg-brand-navy rounded-lg p-2">
              <Flame className="h-6 w-6 text-white" />
            </div>
            <span className="text-brand-navy font-bold text-xl">TariffNavigator</span>
          </div>

          <div className="bg-white rounded-2xl shadow-enterprise p-8">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-brand-navy">Create your account</h2>
              <p className="text-gray-500 text-sm mt-1">Get started with TariffNavigator for free</p>
            </div>

            <form onSubmit={handleRegister} className="space-y-5">
              {/* Full Name */}
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    id="fullName"
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all bg-white"
                    placeholder="Jane Smith"
                  />
                </div>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all bg-white"
                    placeholder="you@company.com"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={`w-full pl-10 pr-10 py-3 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all bg-white ${
                      passwordTooShort ? 'border-red-300' : 'border-gray-200'
                    }`}
                    placeholder="At least 8 characters"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {passwordTooShort && (
                  <p className="mt-1.5 text-xs text-red-600">Password must be at least 8 characters.</p>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className={`w-full pl-10 pr-10 py-3 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all bg-white ${
                      passwordMismatch ? 'border-red-300' : 'border-gray-200'
                    }`}
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    tabIndex={-1}
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {passwordMismatch && (
                  <p className="mt-1.5 text-xs text-red-600">Passwords do not match.</p>
                )}
              </div>

              {slowWarning && !error && (
                <div className="flex items-start space-x-2 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg text-sm">
                  <div className="h-4 w-4 border-2 border-blue-400/40 border-t-blue-500 rounded-full animate-spin mt-0.5 flex-shrink-0" />
                  <span>Server is waking up — this takes up to 30 seconds on first use. Please wait…</span>
                </div>
              )}

              {error && (
                <div className="flex items-start space-x-2 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  <span className="mt-0.5 flex-shrink-0">⚠</span>
                  <span>
                    {error}{' '}
                    {error.includes('Sign in instead') && (
                      <Link to="/login" className="font-semibold underline hover:no-underline">
                        Sign in
                      </Link>
                    )}
                  </span>
                </div>
              )}

              <button
                type="submit"
                disabled={loading || passwordTooShort || passwordMismatch}
                style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #264875 100%)' }}
                className="w-full py-3 text-white font-semibold rounded-xl hover:opacity-90 transition-all active:scale-[0.98] flex items-center justify-center space-x-2 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Create Account</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            <div className="mt-5 pt-5 border-t border-gray-100 text-center">
              <p className="text-xs text-gray-400">
                Secured with 256-bit encryption
              </p>
            </div>
          </div>

          <p className="text-center text-sm text-gray-500 mt-5">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-blue font-medium hover:underline">
              Sign in
            </Link>
          </p>

          <p className="text-center text-xs text-gray-400 mt-3">
            DJ AI Business Consultant • Syracuse, NY
          </p>

          <Footer />
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
