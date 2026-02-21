import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export default function SubscriptionSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState<any>(null);

  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Fetch current subscription to confirm upgrade
    const fetchSubscription = async () => {
      try {
        const response = await api.get('/subscriptions/current');
        setSubscription(response.data.subscription);
      } catch (error) {
        console.error('Error fetching subscription:', error);
      } finally {
        setLoading(false);
      }
    };

    // Wait a moment for webhook to process
    setTimeout(fetchSubscription, 2000);
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Processing your subscription...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        {/* Success Icon */}
        <div className="mb-6">
          <CheckCircle className="h-20 w-20 text-green-500 mx-auto" />
        </div>

        {/* Success Message */}
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Welcome to {subscription?.plan || 'Pro'}!
        </h1>

        <p className="text-gray-600 mb-8">
          Your subscription has been activated successfully. You now have access to all premium features.
        </p>

        {/* Subscription Details */}
        {subscription && (
          <div className="bg-gray-50 rounded-lg p-6 mb-8 text-left">
            <h2 className="font-semibold text-gray-900 mb-4">Subscription Details</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Plan:</span>
                <span className="font-semibold text-gray-900 capitalize">{subscription.plan}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="font-semibold text-green-600 capitalize">{subscription.status}</span>
              </div>
              {subscription.current_period_end && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Next billing:</span>
                  <span className="font-semibold text-gray-900">
                    {new Date(subscription.current_period_end).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* New Features */}
        <div className="bg-blue-50 rounded-lg p-6 mb-8 text-left">
          <h2 className="font-semibold text-gray-900 mb-4">What's New?</h2>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start">
              <CheckCircle className="h-4 w-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
              <span>Increased calculation limit</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-4 w-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
              <span>Create up to 10 watchlists</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-4 w-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
              <span>Email alerts for tariff changes</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-4 w-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
              <span>External monitoring (Federal Register, CBP)</span>
            </li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center"
          >
            Go to Dashboard
            <ArrowRight className="ml-2 h-5 w-5" />
          </button>

          <button
            onClick={() => navigate('/watchlists')}
            className="w-full bg-white text-gray-700 py-3 px-6 rounded-lg font-semibold border-2 border-gray-300 hover:bg-gray-50 transition-colors"
          >
            Create Your First Watchlist
          </button>
        </div>

        {/* Footer */}
        <p className="text-sm text-gray-500 mt-6">
          Need help getting started?{' '}
          <a href="/help" className="text-blue-600 hover:text-blue-700 font-medium">
            View our guide
          </a>
        </p>
      </div>
    </div>
  );
}
