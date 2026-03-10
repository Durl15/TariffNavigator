import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle, ArrowRight, Zap, Shield, Star, LayoutDashboard } from 'lucide-react';
import Navigation from '../components/Navigation';
import { usePageTitle } from '../hooks/usePageTitle'
import Footer from '../components/Footer'



const PLAN_INFO: Record<string, { label: string; iconBg: string; icon: React.ReactNode; perks: string[] }> = {
  pro: {
    label: 'Pro',
    iconBg: 'linear-gradient(135deg,#0D9488,#14B8A6)',
    icon: <Zap className="w-5 h-5 text-white" />,
    perks: [
      'Unlimited tariff lookups',
      '10 watchlists',
      '3 product catalogs',
      'All alert types & email digests',
      'PDF & CSV exports',
    ],
  },
  enterprise: {
    label: 'Enterprise',
    iconBg: 'linear-gradient(135deg,#1E3A5F,#264875)',
    icon: <Shield className="w-5 h-5 text-white" />,
    perks: [
      'Unlimited everything',
      '10 team seats',
      'Full API access',
      'AI-powered insights',
      'Priority support',
    ],
  },
  consultant: {
    label: 'Consultant',
    iconBg: 'linear-gradient(135deg,#D4A843,#E8C066)',
    icon: <Star className="w-5 h-5 text-white" />,
    perks: [
      'White-label PDF exports',
      '50 team seats',
      'Full API access',
      'Custom integrations',
      'Dedicated account manager',
    ],
  },
};

export default function SubscriptionSuccess() {
  usePageTitle('Subscription Confirmed')
  const [searchParams] = useSearchParams();
  const plan = searchParams.get('plan') || 'pro';
  const info = PLAN_INFO[plan] || PLAN_INFO.pro;
  const [countdown, setCountdown] = useState(8);

  // Auto-redirect to dashboard
  useEffect(() => {
    if (countdown <= 0) { window.location.href = '/dashboard'; return; }
    const t = setTimeout(() => setCountdown(c => c - 1), 1000);
    return () => clearTimeout(t);
  }, [countdown]);

  const isAuthenticated = !!localStorage.getItem('token');
  const handleLogout = () => { localStorage.removeItem('token'); window.location.href = '/'; };

  return (
    <div>
      <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />

      {/* Hero */}
      <div className="page-hero py-16 text-center">
        <div className="max-w-xl mx-auto px-4">
          <div className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
               style={{ background: 'linear-gradient(135deg,#0D9488,#14B8A6)', boxShadow: '0 0 32px rgba(13,148,136,0.4)' }}>
            <CheckCircle className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-3">You're all set!</h1>
          <p className="text-blue-200 text-lg">
            Welcome to <span className="font-bold text-white">TariffNavigator {info.label}</span>.
            Your account has been upgraded.
          </p>
        </div>
      </div>

      <div className="max-w-xl mx-auto px-4 py-10 space-y-6">

        {/* Plan card */}
        <div className="card p-8 animate-in">
          {/* Plan badge */}
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                 style={{ background: info.iconBg }}>
              {info.icon}
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Active Plan</p>
              <p className="text-lg font-bold text-brand-navy">{info.label}</p>
            </div>
          </div>

          {/* Perks */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-8">
            {info.perks.map(perk => (
              <div key={perk} className="flex items-center gap-2 text-sm text-gray-700">
                <div className="w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0"
                     style={{ background: 'linear-gradient(135deg,#0D9488,#14B8A6)' }}>
                  <CheckCircle className="w-2.5 h-2.5 text-white" />
                </div>
                {perk}
              </div>
            ))}
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Link to="/dashboard"
                  className="btn btn-teal flex-1 py-3 text-sm flex items-center justify-center gap-2">
              <LayoutDashboard className="w-4 h-4" /> Go to Dashboard
            </Link>
            <Link to="/calculator"
                  className="btn btn-outline flex-1 py-3 text-sm flex items-center justify-center gap-2">
              Open Calculator <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <p className="text-center text-xs text-gray-400 mt-5">
            Redirecting to dashboard in {countdown}s…
          </p>
        </div>

        <p className="text-center text-sm text-gray-500">
          Questions?{' '}
          <a href="mailto:support@tariffnavigator.com" className="text-brand-teal hover:underline font-medium">
            support@tariffnavigator.com
          </a>
        </p>
      </div>
    </div>
  );
}
