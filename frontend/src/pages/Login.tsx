import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame, Lock, Mail, ArrowRight, TrendingUp, Globe, Shield } from 'lucide-react';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'https://tariffnavigator-backend.onrender.com/api/v1';
      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Login failed');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setError('');
    setLoading(true);
    setEmail('demo@tariffnavigator.com');
    setPassword('demo1234');
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'https://tariffnavigator-backend.onrender.com/api/v1';
      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'demo@tariffnavigator.com', password: 'demo1234' }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Demo login failed');
      }
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Demo login failed — please try again');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    { icon: TrendingUp, text: 'Stacked tariff calculations across Section 232, 301, and IEEPA programs' },
    { icon: Globe,      text: 'Real-time change alerts for your watched HS codes and countries' },
    { icon: Shield,     text: 'AI-powered compliance risk scanning to avoid CBP penalties' },
  ];

  return (
    <div className="min-h-screen flex font-sans">

      {/* Left panel — branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12 relative overflow-hidden"
           style={{background: 'linear-gradient(145deg, #152B47 0%, #1E3A5F 40%, #1a4a6a 100%)'}}>
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
            AI-Powered Tariff Intelligence for American Businesses
          </h1>
          <p className="text-blue-200 text-lg mb-10">
            Transforming Business, Rising Above the Challenges
          </p>

          <div className="space-y-5">
            {features.map(({ icon: Icon, text }, idx) => {
              const iconStyles = [
                'bg-brand-teal/20 text-brand-teal',
                'bg-brand-blue/20 text-brand-blue',
                'bg-brand-gold/20 text-brand-gold',
              ]
              return (
                <div key={text} className="flex items-start space-x-3">
                  <div className={`${iconStyles[idx]} rounded-lg p-2 mt-0.5 flex-shrink-0`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <p className="text-blue-100 text-sm leading-relaxed">{text}</p>
                </div>
              )
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
              <h2 className="text-2xl font-bold text-brand-navy">Welcome back</h2>
              <p className="text-gray-500 text-sm mt-1">Sign in to your TariffNavigator account</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
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

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    id="password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all bg-white"
                    placeholder="••••••••"
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
                style={{background: 'linear-gradient(135deg, #1E3A5F 0%, #264875 100%)'}}
                className="w-full py-3 text-white font-semibold rounded-xl hover:opacity-90 transition-all active:scale-[0.98] flex items-center justify-center space-x-2 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Sign In</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            <div className="mt-4">
              <div className="relative flex items-center justify-center text-xs text-gray-400 mb-4">
                <span className="absolute inset-x-0 top-1/2 h-px bg-gray-100" />
                <span className="relative bg-white px-3">or</span>
              </div>
              <button
                type="button"
                onClick={handleDemoLogin}
                disabled={loading}
                className="w-full py-3 border-2 border-brand-teal text-brand-teal font-semibold rounded-xl hover:bg-brand-teal hover:text-white transition-all active:scale-[0.98] flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>Try Demo — No Account Needed</span>
              </button>
            </div>

            <div className="mt-5 pt-5 border-t border-gray-100 text-center">
              <p className="text-xs text-gray-400">
                Secured with 256-bit encryption
              </p>
            </div>
          </div>

          <p className="text-center text-xs text-gray-400 mt-5">
            DJ AI Business Consultant • Syracuse, NY
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
