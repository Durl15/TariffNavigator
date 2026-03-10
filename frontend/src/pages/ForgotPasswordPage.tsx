import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Flame, Mail, MailCheck, ArrowRight, Shield } from 'lucide-react';
import { usePageTitle } from '../hooks/usePageTitle';
import Footer from '../components/Footer';

type PageState = 'form' | 'sent';

const ForgotPasswordPage: React.FC = () => {
  usePageTitle('Reset Password');

  const [pageState, setPageState] = useState<PageState>('form');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'https://tariffnavigator-backend.onrender.com/api/v1';
      const response = await fetch(`${apiUrl}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to send reset link');
      }

      setPageState('sent');
    } catch (err: any) {
      setError(err.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const goBack = () => {
    setPageState('form');
    setError('');
  };

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
            Secure password recovery
          </h1>
          <p className="text-blue-200 text-lg mb-10">
            Transforming Business, Rising Above the Challenges
          </p>

          <div className="space-y-5">
            <div className="flex items-start space-x-3">
              <div className="bg-brand-teal/20 text-brand-teal rounded-lg p-2 mt-0.5 flex-shrink-0">
                <Shield className="h-4 w-4" />
              </div>
              <p className="text-blue-100 text-sm leading-relaxed">
                Reset link expires in 1 hour for security
              </p>
            </div>
          </div>
        </div>

        <p className="relative z-10 text-blue-400 text-sm">
          DJ AI Business Consultant • Syracuse, NY
        </p>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-6 bg-gray-50/50">
        <div className="w-full max-w-md">

          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center space-x-3 mb-8">
            <div className="bg-brand-navy rounded-lg p-2">
              <Flame className="h-6 w-6 text-white" />
            </div>
            <span className="text-brand-navy font-bold text-xl">TariffNavigator</span>
          </div>

          {pageState === 'form' ? (
            <div className="bg-white rounded-2xl shadow-enterprise p-8">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-brand-navy">Forgot your password?</h2>
                <p className="text-gray-500 text-sm mt-1">
                  Enter your email and we'll send you a reset link
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
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

                {error && (
                  <div className="flex items-start space-x-2 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                    <span className="mt-0.5 flex-shrink-0">⚠</span>
                    <span>{error}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #264875 100%)' }}
                  className="w-full py-3 text-white font-semibold rounded-xl hover:opacity-90 transition-all active:scale-[0.98] flex items-center justify-center space-x-2 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <span>Send Reset Link</span>
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
          ) : (
            <div className="bg-white rounded-2xl shadow-enterprise p-8 text-center">
              <div className="flex justify-center mb-5">
                <div className="bg-brand-teal/10 rounded-full p-4">
                  <MailCheck className="w-12 h-12 text-brand-teal" />
                </div>
              </div>

              <h2 className="text-2xl font-bold text-brand-navy mb-3">Check your inbox</h2>

              <p className="text-gray-600 text-sm leading-relaxed mb-6">
                We've sent a password reset link to{' '}
                <span className="font-semibold text-brand-navy">{email}</span>.{' '}
                It expires in 1 hour.
              </p>

              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm text-left">
                <p>
                  Didn't receive it? Check your spam folder or{' '}
                  <button
                    type="button"
                    onClick={goBack}
                    className="font-semibold underline hover:no-underline focus:outline-none"
                  >
                    try a different email
                  </button>
                  .
                </p>
              </div>

              <div className="mt-6 pt-5 border-t border-gray-100">
                <p className="text-xs text-gray-400">
                  Secured with 256-bit encryption
                </p>
              </div>
            </div>
          )}

          <p className="text-center text-sm text-gray-500 mt-5">
            <Link to="/login" className="text-brand-blue font-medium hover:underline">
              ← Back to sign in
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

export default ForgotPasswordPage;
