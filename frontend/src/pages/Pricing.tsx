import React, { useState } from 'react';
import { Check, X, Zap, Shield, Star, Package, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../services/api';
import toast from 'react-hot-toast';
import Navigation from '../components/Navigation';

interface PlanFeature {
  name: string;
  included: boolean;
}

interface Plan {
  id: string;
  name: string;
  price: number;
  period: string;
  description: string;
  features: PlanFeature[];
  highlighted?: boolean;
  buttonText: string;
  buttonVariant: 'primary' | 'secondary' | 'outline' | 'disabled';
  accentClass: string;
  iconBg: string;
  Icon: React.ElementType;
  badgeLabel?: string;
}

const plans: Plan[] = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    period: 'forever',
    description: 'Try TariffNavigator with no commitment.',
    features: [
      { name: '10 lookups / month', included: true },
      { name: '1 watchlist', included: true },
      { name: 'Email-only alerts', included: true },
      { name: '0 product catalogs', included: false },
      { name: 'PDF / CSV exports', included: false },
      { name: 'Multiple users', included: false },
      { name: 'API access', included: false },
    ],
    buttonText: 'Current Plan',
    buttonVariant: 'disabled',
    accentClass: 'bg-gray-200',
    iconBg: 'bg-gray-100',
    Icon: Package,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 49,
    period: 'month',
    description: 'Unlimited lookups for growing importers.',
    features: [
      { name: 'Unlimited lookups', included: true },
      { name: '10 watchlists', included: true },
      { name: 'All alert types', included: true },
      { name: '3 product catalogs', included: true },
      { name: 'PDF / CSV exports', included: true },
      { name: '1 user seat', included: true },
      { name: 'API access', included: false },
    ],
    highlighted: true,
    badgeLabel: 'Most Popular',
    buttonText: 'Upgrade to Pro',
    buttonVariant: 'primary',
    accentClass: 'bg-gradient-teal',
    iconBg: 'bg-teal-50',
    Icon: Zap,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 199,
    period: 'month',
    description: 'Full platform for complex trade operations.',
    features: [
      { name: 'Unlimited lookups', included: true },
      { name: 'Unlimited watchlists', included: true },
      { name: 'All alert types', included: true },
      { name: 'Unlimited catalogs', included: true },
      { name: 'PDF / CSV exports', included: true },
      { name: '10 user seats', included: true },
      { name: 'API access', included: true },
    ],
    buttonText: 'Upgrade to Enterprise',
    buttonVariant: 'secondary',
    accentClass: 'bg-gradient-navy',
    iconBg: 'bg-blue-50',
    Icon: Shield,
  },
  {
    id: 'consultant',
    name: 'Consultant',
    price: 499,
    period: 'month',
    description: 'White-label power for trade consultants.',
    features: [
      { name: 'Unlimited lookups', included: true },
      { name: 'Unlimited watchlists', included: true },
      { name: 'All alert types', included: true },
      { name: 'Unlimited catalogs', included: true },
      { name: 'White-label exports', included: true },
      { name: '50 user seats', included: true },
      { name: 'API access + priority support', included: true },
    ],
    buttonText: 'Contact Sales',
    buttonVariant: 'outline',
    accentClass: 'bg-gradient-gold',
    iconBg: 'bg-amber-50',
    Icon: Star,
  },
];

const faqs = [
  {
    question: 'Can I change plans later?',
    answer:
      'Yes — upgrade or downgrade at any time. Changes take effect immediately and billing is prorated automatically.',
  },
  {
    question: 'What payment methods do you accept?',
    answer:
      'All major credit cards (Visa, Mastercard, American Express) via Stripe. All payments are secure and encrypted.',
  },
  {
    question: 'Can I cancel anytime?',
    answer:
      "Absolutely. Cancel from your billing settings at any time. You'll retain access until the end of the billing period.",
  },
  {
    question: 'Do you offer refunds?',
    answer:
      "We offer a 14-day money-back guarantee. If you're not satisfied within the first 14 days, contact us for a full refund.",
  },
];

export default function Pricing() {
  const [loading, setLoading] = useState<string | null>(null);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const handleUpgrade = async (planId: string) => {
    if (planId === 'free') return;
    if (planId === 'consultant') {
      window.location.href = 'mailto:hello@djaibc.com?subject=Consultant Plan Inquiry';
      return;
    }

    setLoading(planId);
    try {
      const response = await api.post('/subscriptions/checkout/create-session', {
        plan: planId,
      });
      window.location.href = response.data.checkout_url;
    } catch (error: any) {
      console.error('Checkout error:', error);
      if (error.response?.status === 403) {
        toast.error('Only organization admins can manage subscriptions');
      } else if (error.response?.status === 400) {
        toast.error(error.response.data.detail || 'Cannot create checkout session');
      } else {
        toast.error('Failed to start checkout. Please try again.');
      }
      setLoading(null);
    }
  };

  const isAuthenticated = !!localStorage.getItem('token');
  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  return (
    <div>
      <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />

      {/* ── Hero ───────────────────────────────────────────────────────────── */}
      <div className="page-hero py-16 px-4 text-center animate-in">
        <p className="section-label text-white/60 mb-3 tracking-widest">Pricing</p>
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 text-balance">
          Simple, Transparent Pricing
        </h1>
        <p className="text-lg text-white/75 max-w-2xl mx-auto text-balance">
          Tariff intelligence for every business size — from first-time importers to enterprise
          trade teams. Start free, upgrade when you're ready.
        </p>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">

        {/* ── Plan Cards ─────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6 mb-16 items-start">
          {plans.map((plan) => {
            const { Icon } = plan;
            return (
              <div
                key={plan.id}
                className={[
                  'relative bg-white rounded-2xl border border-gray-100 overflow-hidden',
                  'transition-all duration-300 hover:-translate-y-1 shadow-card hover:shadow-float',
                  plan.highlighted ? 'ring-2 ring-brand-teal md:scale-105' : '',
                ].join(' ')}
              >
                {/* Top accent bar */}
                <div className={`h-1 w-full ${plan.accentClass}`} />

                {/* Most Popular badge */}
                {plan.badgeLabel && (
                  <span className="badge badge-teal absolute top-4 right-4">
                    {plan.badgeLabel}
                  </span>
                )}

                <div className="p-7">
                  {/* Icon */}
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${plan.iconBg}`}
                  >
                    {plan.id === 'pro' && (
                      <Icon className="w-5 h-5 text-brand-teal" />
                    )}
                    {plan.id === 'enterprise' && (
                      <Icon className="w-5 h-5 text-brand-navy" />
                    )}
                    {plan.id === 'consultant' && (
                      <Icon className="w-5 h-5 text-amber-600" />
                    )}
                    {plan.id === 'free' && (
                      <Icon className="w-5 h-5 text-gray-400" />
                    )}
                  </div>

                  {/* Plan name + description */}
                  <h2 className="text-xl font-bold text-brand-navy mb-1">{plan.name}</h2>
                  <p className="text-sm text-gray-500 mb-5">{plan.description}</p>

                  {/* Price */}
                  <div className="flex items-end gap-1 mb-6">
                    <span className="text-5xl font-bold text-brand-navy leading-none">
                      ${plan.price}
                    </span>
                    <span className="text-gray-400 text-sm mb-1">/{plan.period}</span>
                  </div>

                  {/* CTA Button */}
                  {plan.buttonVariant === 'primary' && (
                    <button
                      onClick={() => handleUpgrade(plan.id)}
                      disabled={loading !== null}
                      className="btn btn-teal w-full"
                    >
                      {loading === plan.id ? 'Redirecting…' : plan.buttonText}
                    </button>
                  )}
                  {plan.buttonVariant === 'secondary' && (
                    <button
                      onClick={() => handleUpgrade(plan.id)}
                      disabled={loading !== null}
                      className="btn btn-navy w-full"
                    >
                      {loading === plan.id ? 'Redirecting…' : plan.buttonText}
                    </button>
                  )}
                  {plan.buttonVariant === 'outline' && (
                    <button
                      onClick={() => handleUpgrade(plan.id)}
                      className="btn btn-outline w-full border-brand-gold text-amber-700 hover:bg-amber-50"
                    >
                      {plan.buttonText}
                    </button>
                  )}
                  {plan.buttonVariant === 'disabled' && (
                    <button
                      disabled
                      className="btn btn-outline w-full opacity-60 cursor-not-allowed"
                    >
                      {plan.buttonText}
                    </button>
                  )}

                  {/* Features */}
                  <ul className="mt-6 space-y-3">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-3">
                        {feature.included ? (
                          <span className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-full bg-teal-50 flex items-center justify-center">
                            <Check className="w-3 h-3 text-brand-teal" strokeWidth={2.5} />
                          </span>
                        ) : (
                          <span className="mt-0.5 flex-shrink-0 w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center">
                            <X className="w-3 h-3 text-gray-300" strokeWidth={2.5} />
                          </span>
                        )}
                        <span
                          className={`text-sm ${feature.included ? 'text-gray-700' : 'text-gray-400'}`}
                        >
                          {feature.name}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Why TariffNavigator ─────────────────────────────────────────── */}
        <div className="mb-16 animate-in" style={{ animationDelay: '0.1s' }}>
          <p className="section-label text-center mb-6">Why TariffNavigator?</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="kpi-navy rounded-2xl p-6 text-white">
              <p className="text-4xl font-bold tabular-nums mb-1">$216B</p>
              <p className="text-white/80 text-sm font-medium">CBP duties collected in FY2025</p>
              <p className="text-white/50 text-xs mt-2">
                The highest in U.S. history — and rising.
              </p>
            </div>
            <div className="kpi-teal rounded-2xl p-6 text-white">
              <p className="text-4xl font-bold tabular-nums mb-1">2,218</p>
              <p className="text-white/80 text-sm font-medium">Trade penalties issued by CBP</p>
              <p className="text-white/50 text-xs mt-2">
                Misclassifications cost importers millions each year.
              </p>
            </div>
            <div className="kpi-blue rounded-2xl p-6 text-white">
              <p className="text-4xl font-bold tabular-nums mb-1">18%</p>
              <p className="text-white/80 text-sm font-medium">Average effective tariff rate</p>
              <p className="text-white/50 text-xs mt-2">
                Up from 2.4% in under 12 months.
              </p>
            </div>
          </div>
        </div>

        {/* ── FAQ ────────────────────────────────────────────────────────── */}
        <div className="max-w-3xl mx-auto mb-16 animate-in" style={{ animationDelay: '0.15s' }}>
          <p className="section-label text-center mb-6">FAQ</p>
          <div className="card p-8">
            <h2 className="text-2xl font-bold text-brand-navy mb-6">
              Frequently Asked Questions
            </h2>
            <div className="space-y-0">
              {faqs.map((faq, idx) => (
                <div key={idx} className="border-b border-gray-100 last:border-b-0">
                  <button
                    onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                    className="w-full flex items-center justify-between py-4 text-left gap-4 group"
                  >
                    <span className="font-semibold text-gray-900 group-hover:text-brand-navy transition-colors">
                      {faq.question}
                    </span>
                    {openFaq === idx ? (
                      <ChevronUp className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    )}
                  </button>
                  {openFaq === idx && (
                    <p className="pb-4 text-gray-600 text-sm leading-relaxed animate-fade">
                      {faq.answer}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Bottom CTA ─────────────────────────────────────────────────────── */}
      <div className="page-hero py-16 px-4 text-center">
        <h2 className="text-3xl sm:text-4xl font-bold text-white mb-3 text-balance">
          Ready to navigate tariffs with confidence?
        </h2>
        <p className="text-white/70 mb-8 max-w-xl mx-auto">
          Join businesses already using TariffNavigator to cut duty costs and stay ahead of
          policy changes.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={() => (window.location.href = '/register')}
            className="btn btn-teal px-8 py-3 text-base"
          >
            Start Free
          </button>
          <button
            onClick={() =>
              (window.location.href = 'mailto:hello@djaibc.com?subject=TariffNavigator Inquiry')
            }
            className="btn border border-white/40 text-white hover:bg-white/10 px-8 py-3 text-base"
          >
            Talk to Us
          </button>
        </div>
      </div>
    </div>
  );
}
