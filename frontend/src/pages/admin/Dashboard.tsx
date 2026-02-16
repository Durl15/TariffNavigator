import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSystemStats } from '../../services/adminApi';
import {
  Users,
  UserCheck,
  Building2,
  Calculator,
  TrendingUp,
  Share2,
  Key,
  Activity,
} from 'lucide-react';

interface StatCardProps {
  title: string;
  value: number | string;
  icon: React.ElementType;
  trend?: string;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, trend, color }) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
    indigo: 'bg-indigo-500',
    pink: 'bg-pink-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value.toLocaleString()}</p>
          {trend && (
            <p className="text-sm text-gray-500 mt-2">{trend}</p>
          )}
        </div>
        <div className={`p-4 rounded-full ${colorClasses[color as keyof typeof colorClasses] || colorClasses.blue}`}>
          <Icon className="text-white" size={24} />
        </div>
      </div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: getSystemStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Failed to load statistics. Please try again.</p>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
        <p className="text-gray-600">
          Welcome back! Here's an overview of your system.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Users"
          value={stats.total_users}
          icon={Users}
          trend={`+${stats.users_last_7_days} this week`}
          color="blue"
        />
        <StatCard
          title="Active Users"
          value={stats.active_users}
          icon={UserCheck}
          color="green"
        />
        <StatCard
          title="Organizations"
          value={stats.total_organizations}
          icon={Building2}
          color="purple"
        />
        <StatCard
          title="Total Calculations"
          value={stats.total_calculations}
          icon={Calculator}
          trend={`+${stats.calculations_last_7_days} this week`}
          color="orange"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Calculations Today"
          value={stats.calculations_today}
          icon={Activity}
          color="indigo"
        />
        <StatCard
          title="This Month"
          value={stats.calculations_this_month}
          icon={TrendingUp}
          color="pink"
        />
        <StatCard
          title="Shared Links"
          value={stats.total_shared_links}
          icon={Share2}
          color="yellow"
        />
        <StatCard
          title="Active API Keys"
          value={stats.active_api_keys}
          icon={Key}
          color="red"
        />
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Avg Calculation Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.avg_calculation_time_ms.toFixed(0)}ms
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg API Response Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.avg_api_response_time_ms.toFixed(0)}ms
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Storage</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Used</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.storage_used_mb.toFixed(2)} MB
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <a
              href="/admin/users"
              className="block w-full py-2 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-center"
            >
              Manage Users
            </a>
            <a
              href="/admin/organizations"
              className="block w-full py-2 px-4 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-center"
            >
              View Organizations
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
