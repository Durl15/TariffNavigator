import React, { useState } from 'react';
import { Check, X } from 'lucide-react';
import { api } from '../services/api';
import toast from 'react-hot-toast';

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
  buttonVariant: 'primary' | 'secondary' | 'outline';
}

const plans: Plan[] = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    period: 'forever',
    description: 'Perfect for trying out TariffNavigator',
    features: [
      { name: '100 calculations per month', included: true },
      { name: '1 watchlist', included: true },
      { name: 'Basic tariff lookup', included: true },
      { name: 'Country comparison', included: true },
      { name: 'Email alerts', included: false },
      { name: 'External monitoring', included: false },
      { name: 'PDF/CSV export', included: false },
      { name: 'API access', included: false },
    ],
    buttonText: 'Current Plan',
    buttonVariant: 'outline',
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 49,
    period: 'month',
    description: 'For growing businesses tracking imports',
    features: [
      { name: '1,000 calculations per month', included: true },
      { name: '10 watchlists', included: true },
      { name: 'Basic tariff lookup', included: true },
      { name: 'Country comparison', included: true },
      { name: 'Email alerts', included: true },
      { name: 'External monitoring (Federal Register, CBP)', included: true },
      { name: 'PDF/CSV export', included: true },
      { name: 'API access', included: false },
    ],
    highlighted: true,
    buttonText: 'Upgrade to Pro',
    buttonVariant: 'primary',
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 199,
    period: 'month',
    description: 'For large operations with complex needs',
    features: [
      { name: '10,000 calculations per month', included: true },
      { name: 'Unlimited watchlists', included: true },
      { name: 'Basic tariff lookup', included: true },
      { name: 'Country comparison', included: true },
      { name: 'Email alerts', included: true },
      { name: 'External monitoring (Federal Register, CBP)', included: true },
      { name: 'PDF/CSV export', included: true },
      { name: 'API access', included: true },
      { name: 'AI-powered insights', included: true },
      { name: 'Priority support', included: true },
      { name: 'Custom integrations', included: true },
    ],
    buttonText: 'Upgrade to Enterprise',
    buttonVariant: 'secondary',
  },
];

export default function Pricing() {
  const [loading, setLoading] = useState<string | null>(null);

  const handleUpgrade = async (planId: string) => {
    if (planId === 'free') {
      return; // Can't upgrade to free
    }

    setLoading(planId);
    try {
      // Create checkout session
      const response = await api.post('/subscriptions/checkout/create-session', {
        plan: planId,
      });

      // Redirect to Stripe Checkout
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

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Select the perfect plan for your business needs. Upgrade or downgrade anytime.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`
                relative bg-white rounded-lg shadow-lg overflow-hidden
                ${plan.highlighted ? 'ring-2 ring-blue-500 transform scale-105' : ''}
              `}
            >
              {/* Highlighted Badge */}
              {plan.highlighted && (
                <div className="absolute top-0 right-0 bg-blue-500 text-white px-4 py-1 text-sm font-semibold rounded-bl-lg">
                  Most Popular
                </div>
              )}

              <div className="p-8">
                {/* Plan Name */}
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </h2>

                {/* Description */}
                <p className="text-gray-600 mb-6">
                  {plan.description}
                </p>

                {/* Price */}
                <div className="mb-6">
                  <span className="text-5xl font-bold text-gray-900">
                    ${plan.price}
                  </span>
                  <span className="text-gray-600 ml-2">
                    /{plan.period}
                  </span>
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={loading !== null || plan.id === 'free'}
                  className={`
                    w-full py-3 px-6 rounded-lg font-semibold text-center
                    transition-colors duration-200
                    ${
                      plan.buttonVariant === 'primary'
                        ? 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400'
                        : plan.buttonVariant === 'secondary'
                        ? 'bg-gray-900 text-white hover:bg-gray-800 disabled:bg-gray-400'
                        : 'bg-white text-gray-700 border-2 border-gray-300 cursor-not-allowed'
                    }
                  `}
                >
                  {loading === plan.id ? 'Redirecting...' : plan.buttonText}
                </button>

                {/* Features */}
                <ul className="mt-8 space-y-4">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      {feature.included ? (
                        <Check className="h-5 w-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                      ) : (
                        <X className="h-5 w-5 text-gray-300 mr-3 flex-shrink-0 mt-0.5" />
                      )}
                      <span
                        className={
                          feature.included ? 'text-gray-700' : 'text-gray-400'
                        }
                      >
                        {feature.name}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Frequently Asked Questions
          </h2>

          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Can I change plans later?
              </h3>
              <p className="text-gray-600">
                Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately,
                and we'll prorate your billing accordingly.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-gray-600">
                We accept all major credit cards (Visa, Mastercard, American Express) via Stripe.
                All payments are secure and encrypted.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Can I cancel anytime?
              </h3>
              <p className="text-gray-600">
                Absolutely. You can cancel your subscription at any time from your billing settings.
                You'll continue to have access until the end of your billing period.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Do you offer refunds?
              </h3>
              <p className="text-gray-600">
                We offer a 14-day money-back guarantee. If you're not satisfied within the first 14 days,
                contact us for a full refund.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
