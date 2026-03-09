import { useQuery } from '@tanstack/react-query'
import { Calculator, TrendingUp, Clock, Globe, FileDown, ArrowUpRight, Bell, Package, Eye, Flame, Zap } from 'lucide-react'
import { getPublicStats, getPopularHSCodes, exportCSV, downloadBlob, getActionList, type PublicStats, type PopularHSCode, type ActionListResponse } from '../services/api'
import toast from 'react-hot-toast'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import Navigation from '../components/Navigation'

const URGENCY_BADGE: Record<string, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-blue-100 text-blue-700',
}

export default function Dashboard() {
  const [isExporting, setIsExporting] = useState(false)
  const isAuthenticated = !!localStorage.getItem('token')

  const { data: stats, isLoading: statsLoading } = useQuery<PublicStats>({
    queryKey: ['publicStats'],
    queryFn: getPublicStats,
    refetchInterval: 60000,
  })

  const { data: popularCodes, isLoading: codesLoading } = useQuery<PopularHSCode[]>({
    queryKey: ['popularHSCodes'],
    queryFn: getPopularHSCodes,
    refetchInterval: 300000,
  })

  const { data: actionList, isLoading: actionsLoading } = useQuery<ActionListResponse>({
    queryKey: ['actionList'],
    queryFn: getActionList,
    enabled: isAuthenticated,
    staleTime: 300000,
  })

  const handleExportCSV = async () => {
    setIsExporting(true)
    try {
      const blob = await exportCSV({ limit: 100 })
      const timestamp = new Date().toISOString().split('T')[0]
      downloadBlob(blob, `calculations_${timestamp}.csv`)
      toast.success('CSV exported successfully!')
    } catch {
      toast.error('Failed to export CSV. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/'
  }

  const kpiCards = [
    {
      label: 'Total Calculations',
      value: stats?.total_calculations,
      icon: Calculator,
      borderColor: 'border-brand-blue',
      bgColor: 'bg-blue-50',
      iconColor: 'text-brand-blue',
      gradient: 'kpi-blue',
    },
    {
      label: 'This Month',
      value: stats?.calculations_this_month,
      icon: TrendingUp,
      borderColor: 'border-brand-teal',
      bgColor: 'bg-teal-50',
      iconColor: 'text-brand-teal',
      gradient: 'kpi-teal',
    },
    {
      label: 'Today',
      value: stats?.calculations_today,
      icon: Clock,
      borderColor: 'border-purple-400',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      gradient: 'kpi-purple',
    },
    {
      label: 'HS Codes Indexed',
      value: stats?.total_hs_codes,
      icon: Globe,
      borderColor: 'border-brand-gold',
      bgColor: 'bg-yellow-50',
      iconColor: 'text-yellow-600',
      gradient: 'kpi-gold',
    },
  ]

  const quickActions = [
    { label: 'New Calculation', path: '/calculator',   icon: Calculator, primary: true  },
    { label: 'Manage Watchlists', path: '/watchlists', icon: Eye,        primary: false },
    { label: 'Upload Catalog',   path: '/catalogs',    icon: Package,    primary: false },
    { label: 'View Alerts',      path: '/notifications',icon: Bell,      primary: false },
  ]

  return (
    <div className="min-h-screen font-sans">
      <Navigation isAuthenticated={isAuthenticated} onLogout={handleLogout} />

      {/* Page hero header */}
      <div className="page-hero">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-300 text-xs font-semibold uppercase tracking-widest mb-1">TariffNavigator</p>
              <h1 className="text-3xl font-bold text-white">Intelligence Dashboard</h1>
              <p className="text-blue-200 text-sm mt-1">Real-time tariff activity and AI-powered insights</p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleExportCSV}
                disabled={isExporting}
                className="flex items-center space-x-2 px-4 py-2 border border-white/20 bg-white/10 text-white text-sm rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50"
              >
                {isExporting
                  ? <div className="h-4 w-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  : <FileDown className="h-4 w-4" />
                }
                <span>Export CSV</span>
              </button>
              <Link
                to="/calculator"
                className="flex items-center space-x-2 px-4 py-2 bg-brand-teal hover:bg-brand-teal/90 text-white text-sm font-medium rounded-lg transition-colors shadow-glow-teal"
              >
                <Calculator className="h-4 w-4" />
                <span>New Calculation</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Monday Morning Action List */}
        {isAuthenticated && (
          <div className="bg-gradient-navy rounded-2xl shadow-float p-6 mb-8 border border-white/5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-brand-gold" />
                <h2 className="font-bold text-white text-lg">Your Top Actions This Week</h2>
              </div>
              {actionList && actionList.total_opportunity > 0 && (
                <span className="px-3 py-1 bg-brand-teal text-white text-sm font-bold rounded-full shadow-glow-teal">
                  ${actionList.total_opportunity.toLocaleString()} opportunity
                </span>
              )}
            </div>
            {actionList && <p className="text-blue-200 text-sm mb-4">{actionList.summary}</p>}

            {actionsLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map(i => <div key={i} className="h-16 bg-white/[0.08] animate-pulse rounded-xl" />)}
              </div>
            ) : actionList?.actions && actionList.actions.length > 0 ? (
              <div className="space-y-2">
                {actionList.actions.map(action => (
                  <div key={action.id} className="bg-white/[0.08] rounded-xl p-4 flex items-start justify-between space-x-3">
                    <div className="flex items-start space-x-3 flex-1 min-w-0">
                      <span className="text-xl flex-shrink-0">{action.icon}</span>
                      <div className="min-w-0">
                        <div className="flex items-center space-x-2 mb-0.5">
                          <p className="text-white font-medium text-sm truncate">{action.title}</p>
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium flex-shrink-0 ${URGENCY_BADGE[action.urgency] || URGENCY_BADGE.low}`}>
                            {action.urgency}
                          </span>
                        </div>
                        <p className="text-blue-300 text-xs truncate">{action.description}</p>
                        {action.deadline && (
                          <p className="text-brand-gold text-xs mt-0.5">Deadline: {action.deadline}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0 flex flex-col items-end space-y-1">
                      {action.estimated_dollar_impact && (
                        <span className="text-brand-teal text-sm font-bold">${action.estimated_dollar_impact.toLocaleString()}</span>
                      )}
                      <Link
                        to={action.cta_url}
                        className="px-3 py-1.5 bg-brand-blue text-white text-xs font-medium rounded-lg hover:bg-brand-blue-dark transition-colors whitespace-nowrap"
                      >
                        {action.cta_label}
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-blue-300 text-sm">Upload a product catalog to get personalized action recommendations.</p>
            )}
          </div>
        )}

        {/* KPI cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          {kpiCards.map((card, i) => {
            const Icon = card.icon
            return (
              <div key={card.label} className={`${card.gradient} rounded-2xl p-6 animate-in`} style={{animationDelay: `${i * 60}ms`}}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-white/70 uppercase tracking-wider">{card.label}</p>
                    <p className="mt-2 text-3xl font-bold text-white tabular-nums">
                      {statsLoading
                        ? <span className="inline-block h-8 w-20 bg-white/20 animate-pulse rounded-lg" />
                        : (card.value ?? 0).toLocaleString()
                      }
                    </p>
                  </div>
                  <div className="bg-white/20 rounded-xl p-3">
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Popular HS codes table */}
          <div className="lg:col-span-2 card animate-in">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h2 className="font-semibold text-brand-navy">Most Queried HS Codes</h2>
                <p className="text-xs text-gray-400 mt-0.5">Last 30 days</p>
              </div>
              <Link
                to="/calculator"
                className="text-xs text-brand-blue hover:text-brand-blue-dark flex items-center space-x-1 font-medium"
              >
                <span>Search codes</span>
                <ArrowUpRight size={12} />
              </Link>
            </div>

            {codesLoading ? (
              <div className="p-6 space-y-3">
                {[1, 2, 3, 4, 5].map(i => (
                  <div key={i} className="h-12 bg-gray-100 animate-pulse rounded-lg" />
                ))}
              </div>
            ) : popularCodes && popularCodes.length > 0 ? (
              <div className="divide-y divide-gray-50">
                {popularCodes.map((code, index) => (
                  <div key={code.hs_code} className="flex items-center px-6 py-4 hover:bg-gray-50 transition-colors">
                    <span className="w-7 h-7 rounded-full bg-brand-navy text-white text-xs font-bold flex items-center justify-center flex-shrink-0">
                      {index + 1}
                    </span>
                    <div className="ml-4 flex-1 min-w-0">
                      <p className="font-mono text-sm font-semibold text-brand-navy">{code.hs_code}</p>
                      <p className="text-xs text-gray-500 truncate">{code.description}</p>
                    </div>
                    <div className="text-right flex-shrink-0 ml-4">
                      <p className="text-sm font-bold text-brand-blue">{code.usage_count.toLocaleString()}</p>
                      <p className="text-xs text-gray-400">lookups</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-gray-400">
                <Globe className="h-10 w-10 mb-3 opacity-40" />
                <p className="text-sm">No data yet. Start making calculations.</p>
              </div>
            )}
          </div>

          {/* Right sidebar */}
          <div className="space-y-5">

            {/* Quick actions */}
            <div className="card p-5 animate-in">
              <h3 className="font-semibold text-brand-navy text-sm mb-4">Quick Actions</h3>
              <div className="space-y-2">
                {quickActions.map(({ label, path, icon: Icon, primary }) => (
                  <Link
                    key={path}
                    to={path}
                    className={`flex items-center space-x-3 w-full px-4 py-3 rounded-xl text-sm font-medium transition-colors ${
                      primary
                        ? 'btn-navy'
                        : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon size={16} />
                    <span>{label}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* Active markets */}
            {stats?.supported_countries && stats.supported_countries.length > 0 && (
              <div className="kpi-navy rounded-2xl p-5 shadow-float">
                <div className="flex items-center space-x-2 mb-3">
                  <Flame className="h-4 w-4 text-brand-teal" />
                  <h3 className="font-semibold text-white text-sm">Active Markets</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {stats.supported_countries.map((country) => (
                    <span
                      key={country}
                      className="px-2.5 py-1 bg-white/[0.12] text-blue-200 rounded-lg text-xs font-medium"
                    >
                      {country}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t border-gray-200">
        <p className="text-center text-xs text-gray-400">
          DJ AI Business Consultant • Syracuse, NY • Transforming Business, Rising Above the Challenges
        </p>
      </footer>
    </div>
  )
}
