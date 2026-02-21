import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CreditCard,
  Calendar,
  TrendingUp,
  Download,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { api } from '../services/api';
import toast from 'react-hot-toast';

interface Subscription {
  id: string;
  plan: string;
  status: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

interface UsageStats {
  plan: string;
  calculations: {
    used: number;
    limit: number;
    percentage: number;
    warning: boolean;
    exceeded: boolean;
    resets_in_days: number;
  };
  watchlists: {
    used: number;
    limit: number;
    percentage: number;
    warning: boolean;
    exceeded: boolean;
    unlimited: boolean;
  };
  saved_calculations: {
    used: number;
    limit: number;
    percentage: number;
    warning: boolean;
    exceeded: boolean;
    unlimited: boolean;
  };
}

interface Invoice {
  id: string;
  amount: number;
  currency: string;
  status: string;
  invoice_pdf_url?: string;
  created_at: string;
  paid_at?: string;
}

export default function Billing() {
  const navigate = useNavigate();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancelModalOpen, setCancelModalOpen] = useState(false);

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      setLoading(true);

      // Fetch subscription, usage, and invoices in parallel
      const [subRes, usageRes, invoicesRes] = await Promise.all([
        api.get('/subscriptions/current'),
        api.get('/subscriptions/usage'),
        api.get('/subscriptions/invoices?limit=10')
      ]);

      setSubscription(subRes.data.subscription);
      setUsage(usageRes.data);
      setInvoices(invoicesRes.data.invoices || []);
    } catch (error: any) {
      console.error('Error fetching billing data:', error);
      toast.error('Failed to load billing information');
    } finally {
      setLoading(false);
    }
  };

  const openBillingPortal = async () => {
    try {
      const res = await api.get('/subscriptions/billing-portal', {
        params: { return_url: window.location.href }
      });
      window.location.href = res.data.url;
    } catch (error: any) {
      console.error('Error opening billing portal:', error);
      if (error.response?.status === 403) {
        toast.error('Only organization admins can manage billing');
      } else {
        toast.error('Failed to open billing portal');
      }
    }
  };

  const cancelSubscription = async () => {
    try {
      await api.post('/subscriptions/cancel');
      toast.success('Subscription will cancel at end of billing period');
      setCancelModalOpen(false);
      fetchBillingData();
    } catch (error: any) {
      console.error('Error canceling subscription:', error);
      if (error.response?.status === 403) {
        toast.error('Only organization admins can cancel subscription');
      } else {
        toast.error('Failed to cancel subscription');
      }
    }
  };

  const upgradeToEnterprise = async () => {
    try {
      const res = await api.post('/subscriptions/upgrade?new_plan=enterprise');

      if (res.data.checkout_url) {
        // New subscription - redirect to checkout
        window.location.href = res.data.checkout_url;
      } else {
        // Immediate upgrade
        toast.success('Successfully upgraded to Enterprise!');
        fetchBillingData();
      }
    } catch (error: any) {
      console.error('Error upgrading:', error);
      toast.error(error.response?.data?.detail || 'Failed to upgrade plan');
    }
  };

  const getUsageColor = (percentage: number, exceeded: boolean) => {
    if (exceeded) return 'bg-red-500';
    if (percentage >= 80) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      active: { color: 'bg-green-100 text-green-800', icon: CheckCircle, text: 'Active' },
      canceled: { color: 'bg-gray-100 text-gray-800', icon: XCircle, text: 'Canceled' },
      past_due: { color: 'bg-red-100 text-red-800', icon: AlertCircle, text: 'Past Due' },
    };

    const badge = badges[status as keyof typeof badges] || badges.active;
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${badge.color}`}>
        <Icon className="h-4 w-4 mr-1" />
        {badge.text}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading billing information...</p>
        </div>
      </div>
    );
  }

  const currentPlan = usage?.plan || 'free';

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Billing & Subscription</h1>
          <p className="text-gray-600 mt-2">Manage your subscription and view usage</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Current Plan */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Current Plan</h2>
              {subscription && getStatusBadge(subscription.status)}
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Plan</p>
                <p className="text-2xl font-bold text-gray-900 capitalize">{currentPlan}</p>
                {currentPlan === 'free' && (
                  <p className="text-sm text-gray-500 mt-1">Upgrade to unlock premium features</p>
                )}
              </div>

              {subscription && (
                <>
                  <div>
                    <p className="text-sm text-gray-600">Next Billing Date</p>
                    <p className="text-lg font-medium text-gray-900">
                      {new Date(subscription.current_period_end).toLocaleDateString()}
                    </p>
                    {subscription.cancel_at_period_end && (
                      <p className="text-sm text-red-600 mt-1">
                        ⚠️ Subscription will cancel on this date
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-sm text-gray-600">Amount</p>
                    <p className="text-lg font-medium text-gray-900">
                      ${currentPlan === 'pro' ? '49' : '199'}/month
                    </p>
                  </div>
                </>
              )}
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              {currentPlan === 'free' && (
                <button
                  onClick={() => navigate('/pricing')}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Upgrade Plan
                </button>
              )}

              {currentPlan === 'pro' && (
                <button
                  onClick={upgradeToEnterprise}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Upgrade to Enterprise
                </button>
              )}

              {subscription && !subscription.cancel_at_period_end && (
                <>
                  <button
                    onClick={openBillingPortal}
                    className="bg-white text-gray-700 px-6 py-2 rounded-lg font-semibold border-2 border-gray-300 hover:bg-gray-50 transition-colors"
                  >
                    <CreditCard className="inline h-5 w-5 mr-2" />
                    Manage Payment Method
                  </button>

                  <button
                    onClick={() => setCancelModalOpen(true)}
                    className="bg-white text-red-600 px-6 py-2 rounded-lg font-semibold border-2 border-red-300 hover:bg-red-50 transition-colors"
                  >
                    Cancel Subscription
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="space-y-4">
            <div className="bg-blue-50 rounded-lg p-6">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm text-gray-600">Current Plan</p>
                  <p className="text-2xl font-bold text-gray-900 capitalize">{currentPlan}</p>
                </div>
              </div>
            </div>

            {usage && usage.calculations.resets_in_days && (
              <div className="bg-green-50 rounded-lg p-6">
                <div className="flex items-center">
                  <Calendar className="h-8 w-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-600">Quota Resets In</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {usage.calculations.resets_in_days} days
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Usage Statistics */}
        {usage && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Usage Statistics</h2>

            <div className="space-y-6">
              {/* Calculations */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">Monthly Calculations</span>
                  <span className="text-sm text-gray-600">
                    {usage.calculations.used.toLocaleString()} / {usage.calculations.limit.toLocaleString()}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${getUsageColor(
                      usage.calculations.percentage,
                      usage.calculations.exceeded
                    )}`}
                    style={{ width: `${Math.min(usage.calculations.percentage, 100)}%` }}
                  ></div>
                </div>
                {usage.calculations.warning && (
                  <p className="text-sm text-yellow-600 mt-1">
                    ⚠️ You're approaching your monthly limit
                  </p>
                )}
                {usage.calculations.exceeded && (
                  <p className="text-sm text-red-600 mt-1">
                    ❌ Monthly limit exceeded. Upgrade for more calculations.
                  </p>
                )}
              </div>

              {/* Watchlists */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">Watchlists</span>
                  <span className="text-sm text-gray-600">
                    {usage.watchlists.used} / {usage.watchlists.unlimited ? '∞' : usage.watchlists.limit}
                  </span>
                </div>
                {!usage.watchlists.unlimited && (
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${getUsageColor(
                        usage.watchlists.percentage,
                        usage.watchlists.exceeded
                      )}`}
                      style={{ width: `${Math.min(usage.watchlists.percentage, 100)}%` }}
                    ></div>
                  </div>
                )}
                {usage.watchlists.exceeded && (
                  <p className="text-sm text-red-600 mt-1">
                    ❌ Watchlist limit reached. Upgrade for more watchlists.
                  </p>
                )}
              </div>

              {/* Saved Calculations */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">Saved Calculations</span>
                  <span className="text-sm text-gray-600">
                    {usage.saved_calculations.used} / {usage.saved_calculations.unlimited ? '∞' : usage.saved_calculations.limit}
                  </span>
                </div>
                {!usage.saved_calculations.unlimited && (
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${getUsageColor(
                        usage.saved_calculations.percentage,
                        usage.saved_calculations.exceeded
                      )}`}
                      style={{ width: `${Math.min(usage.saved_calculations.percentage, 100)}%` }}
                    ></div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Invoice History */}
        {invoices.length > 0 && (
          <div className="mt-6 bg-white rounded-lg shadow overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Invoice History</h2>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Invoice
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(invoice.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${invoice.amount.toFixed(2)} {invoice.currency}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          invoice.status === 'paid'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {invoice.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {invoice.invoice_pdf_url ? (
                          <a
                            href={invoice.invoice_pdf_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-700 flex items-center"
                          >
                            <Download className="h-4 w-4 mr-1" />
                            Download
                          </a>
                        ) : (
                          <span className="text-gray-400">N/A</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Cancel Modal */}
        {cancelModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Cancel Subscription
              </h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to cancel your subscription? You'll continue to have access
                until the end of your billing period.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setCancelModalOpen(false)}
                  className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Keep Subscription
                </button>
                <button
                  onClick={cancelSubscription}
                  className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700"
                >
                  Yes, Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
