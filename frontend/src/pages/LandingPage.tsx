import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Calculator, Shield, TrendingDown, Globe, Zap, FileText,
  DollarSign, Search, ArrowRight, CheckCircle, Flame,
  AlertTriangle, BarChart2, Clock
} from 'lucide-react'
import { getPublicStats, type PublicStats } from '../services/api'
import { usePageTitle } from '../hooks/usePageTitle'
import Footer from '../components/Footer'



const PROBLEMS = [
  { stat: '18%', label: 'Average effective tariff rate in 2026 (up from 2.4% in 2024)', color: 'text-red-500' },
  { stat: '$216B', label: 'CBP duty collections in FY2025 — record high', color: 'text-red-500' },
  { stat: '2,218', label: 'CBP trade penalties issued — misclassification, fraud, non-compliance', color: 'text-red-500' },
  { stat: '$500+', label: 'Monthly cost of enterprise tariff tools — out of reach for SMBs', color: 'text-red-500' },
]

const TOOLS = [
  {
    icon: Calculator,
    name: 'Smart Tariff Calculator',
    desc: 'Calculate stacked duty rates — Section 301, IEEPA, USMCA, AD/CVD — in one lookup.',
    color: 'bg-blue-100 text-blue-600',
    tier: 'Free',
  },
  {
    icon: DollarSign,
    name: 'Cash Flow Forecaster',
    desc: 'Know your duty obligation at port before your shipment arrives. Avoid $50K+ surprises.',
    color: 'bg-red-100 text-red-600',
    tier: 'Free',
  },
  {
    icon: DollarSign,
    name: 'Duty Drawback Finder',
    desc: 'Recover up to 99% of duties already paid. Billions go unclaimed every year.',
    color: 'bg-green-100 text-green-600',
    tier: 'Free',
  },
  {
    icon: FileText,
    name: 'USMCA Qualification Checker',
    desc: 'Find out if your Mexico/Canada goods qualify for 0% duty. Catch the documentation gap before CBP does.',
    color: 'bg-blue-100 text-blue-600',
    tier: 'Pro',
  },
  {
    icon: Shield,
    name: 'Supply Chain Risk Scanner',
    desc: 'Detect transshipment risk before CBP penalties land. Chinese components in Vietnam factories = hidden 301 exposure.',
    color: 'bg-orange-100 text-orange-600',
    tier: 'Pro',
  },
  {
    icon: Search,
    name: 'HTS Code Audit',
    desc: 'Supplier-provided HTS codes cost you money. AI catches misclassifications worth 3–20% overpayment.',
    color: 'bg-purple-100 text-purple-600',
    tier: 'Pro',
  },
  {
    icon: Globe,
    name: 'Alternative Sourcing Finder',
    desc: 'For any HTS code, rank 13 origin countries by tariff savings, supply reliability, and lead time.',
    color: 'bg-teal-100 text-teal-600',
    tier: 'Pro',
  },
  {
    icon: Zap,
    name: 'Scenario Planner',
    desc: '"What if China snaps back to 145%?" Run it against your real catalog data. Know your exposure before it hits.',
    color: 'bg-indigo-100 text-indigo-600',
    tier: 'Enterprise',
  },
  {
    icon: BarChart2,
    name: 'Cost Impact Modeler',
    desc: 'Upload your product catalog. Get per-SKU tariff exposure, margin analysis, and break-even pricing.',
    color: 'bg-yellow-100 text-yellow-600',
    tier: 'Pro',
  },
  {
    icon: AlertTriangle,
    name: 'Real-Time Change Alerts',
    desc: 'Be first to know when rates change for your HTS codes. Watchlists with push notifications and email digests.',
    color: 'bg-red-100 text-red-600',
    tier: 'Pro',
  },
]

const TESTIMONIALS = [
  {
    quote: "We were paying 25% on goods that qualified for USMCA 0%. TariffNavigator found the documentation gap in 5 minutes — saved us $84,000 in one quarter.",
    name: "Maria G.",
    title: "Owner, auto parts distributor, Texas",
  },
  {
    quote: "The cash flow forecaster alone is worth the subscription. I knew I needed $47,000 at the port two weeks before the shipment. We arranged a bridge loan in time.",
    name: "James K.",
    title: "Importer, consumer electronics, Ohio",
  },
  {
    quote: "My supplier had been giving me the wrong HTS code for 3 years. The HTS audit flagged it immediately. I filed for drawback and recovered $29,000.",
    name: "Susan W.",
    title: "Small manufacturer, apparel, New York",
  },
]

const PRICING = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    desc: 'Try the core tools. No credit card.',
    features: ['10 tariff lookups/month', 'Cash flow forecaster', 'Drawback finder', '1 watchlist'],
    cta: 'Start Free',
    href: '/login',
    highlight: false,
  },
  {
    name: 'Pro',
    price: '$49',
    period: '/month',
    desc: 'Everything an active importer needs.',
    features: ['Unlimited lookups', 'All 10 tools', 'Product catalog upload', 'Real-time alerts', 'PDF/CSV exports', '10 watchlists'],
    cta: 'Start Pro',
    href: '/pricing',
    highlight: true,
  },
  {
    name: 'Enterprise',
    price: '$199',
    period: '/month',
    desc: 'For growing teams with complex supply chains.',
    features: ['Everything in Pro', 'Scenario planner', 'Unlimited catalogs', 'API access', '10 users', 'Priority support'],
    cta: 'Start Enterprise',
    href: '/pricing',
    highlight: false,
  },
]

export default function LandingPage() {
  usePageTitle('')
  const { data: stats } = useQuery<PublicStats>({
    queryKey: ['publicStats'],
    queryFn: getPublicStats,
  })

  const isAuthenticated = !!localStorage.getItem('token')

  return (
    <div className="min-h-screen bg-white font-sans">
      {/* ── NAV ── */}
      <nav className="bg-brand-navy border-b border-brand-navy-dark shadow-enterprise sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3">
            <div className="bg-brand-teal rounded-lg p-1.5">
              <Flame className="h-5 w-5 text-white" />
            </div>
            <div className="leading-tight">
              <span className="block text-white font-bold text-base">TariffNavigator</span>
              <span className="block text-xs text-blue-300">DJ AI Business Consultant</span>
            </div>
          </Link>

          <div className="hidden md:flex items-center space-x-6">
            <a href="#tools" className="text-blue-200 hover:text-white text-sm transition-colors">Tools</a>
            <a href="#pricing" className="text-blue-200 hover:text-white text-sm transition-colors">Pricing</a>
            <Link to="/pricing" className="text-sm font-semibold text-brand-gold hover:text-brand-gold-light">Upgrade</Link>
            {isAuthenticated ? (
              <Link to="/dashboard" className="px-4 py-2 bg-brand-teal text-white text-sm font-medium rounded-lg hover:bg-brand-teal-dark transition-colors">
                Dashboard →
              </Link>
            ) : (
              <Link to="/login" className="px-4 py-2 bg-brand-blue text-white text-sm font-medium rounded-lg hover:bg-brand-blue-dark transition-colors">
                Sign In
              </Link>
            )}
          </div>

          {/* Mobile */}
          <div className="md:hidden">
            <Link to="/login" className="px-4 py-2 bg-brand-blue text-white text-sm font-medium rounded-lg">
              Sign In
            </Link>
          </div>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section className="bg-brand-navy text-white py-20 lg:py-28 relative overflow-hidden">
        {/* Background texture */}
        <div className="absolute inset-0 opacity-5" style={{
          backgroundImage: 'radial-gradient(circle at 25% 50%, #4A90D9 0%, transparent 50%), radial-gradient(circle at 75% 20%, #0D9488 0%, transparent 40%)'
        }} />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative">
          <div className="inline-flex items-center space-x-2 px-3 py-1 bg-brand-teal/20 border border-brand-teal/40 rounded-full text-brand-teal text-xs font-semibold mb-6">
            <Flame size={12} />
            <span>Rising above the tariff challenge — DJ AI Business Consultant</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight mb-6">
            Stop Overpaying Tariffs.<br />
            <span className="text-brand-teal">Start Outsmarting Them.</span>
          </h1>

          <p className="text-blue-200 text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
            AI-powered tariff intelligence built for small businesses.
            Calculate stacked duties, recover drawback, find cheaper sourcing, and model tariff scenarios —
            all in plain English, starting free.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
            <Link
              to="/login"
              className="flex items-center space-x-2 px-8 py-4 bg-brand-teal text-white font-bold rounded-xl hover:bg-brand-teal-dark transition-all shadow-lg text-lg"
            >
              <span>Start Free — No Credit Card</span>
              <ArrowRight size={20} />
            </Link>
            <Link
              to="/calculator?hs=8471.30&country=CN&value=50000&q=laptop+computer"
              className="flex items-center space-x-2 px-8 py-4 border border-blue-400 text-blue-200 hover:bg-brand-navy-light rounded-xl transition-colors text-lg"
            >
              <Calculator size={18} />
              <span>Try Free — Laptop from China</span>
            </Link>
          </div>

          {/* Live stats */}
          {stats && (
            <div className="flex flex-wrap items-center justify-center gap-8 text-center">
              <div>
                <p className="text-3xl font-bold text-white">{stats.total_calculations.toLocaleString()}</p>
                <p className="text-blue-300 text-sm">Tariff Lookups</p>
              </div>
              <div className="w-px h-8 bg-blue-700 hidden sm:block" />
              <div>
                <p className="text-3xl font-bold text-white">{stats.total_hs_codes.toLocaleString()}</p>
                <p className="text-blue-300 text-sm">HTS Codes Indexed</p>
              </div>
              <div className="w-px h-8 bg-blue-700 hidden sm:block" />
              <div>
                <p className="text-3xl font-bold text-white">{stats.supported_countries?.length ?? 13}+</p>
                <p className="text-blue-300 text-sm">Countries Covered</p>
              </div>
              <div className="w-px h-8 bg-blue-700 hidden sm:block" />
              <div>
                <p className="text-3xl font-bold text-brand-gold">$0</p>
                <p className="text-blue-300 text-sm">To Start</p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ── PROBLEM ── */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-brand-navy mb-3">The Tariff Crisis Is Real</h2>
            <p className="text-gray-500 max-w-xl mx-auto">
              U.S. tariff rates surged 7x in under two years. Enterprise trade tools cost $500–2,000/month
              and require a trade lawyer to operate. Small businesses are getting crushed.
            </p>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
            {PROBLEMS.map(p => (
              <div key={p.stat} className="bg-white rounded-xl border border-gray-100 shadow-card p-6 text-center">
                <p className={`text-4xl font-extrabold ${p.color} mb-2`}>{p.stat}</p>
                <p className="text-gray-500 text-xs leading-relaxed">{p.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── TOOLS ── */}
      <section id="tools" className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-brand-navy mb-3">10 Tools. One Platform. Plain English.</h2>
            <p className="text-gray-500 max-w-xl mx-auto">
              Everything an American SMB needs to survive the tariff era — from free basic lookups
              to enterprise scenario modeling.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {TOOLS.map(tool => {
              const Icon = tool.icon
              return (
                <div key={tool.name} className="bg-white rounded-xl border border-gray-100 shadow-card p-5 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className={`rounded-xl p-2.5 ${tool.color}`}>
                      <Icon size={20} />
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      tool.tier === 'Free' ? 'bg-green-100 text-green-700' :
                      tool.tier === 'Pro' ? 'bg-blue-100 text-blue-700' :
                      'bg-purple-100 text-purple-700'
                    }`}>
                      {tool.tier}
                    </span>
                  </div>
                  <h3 className="font-semibold text-brand-navy mb-1">{tool.name}</h3>
                  <p className="text-gray-500 text-sm leading-relaxed">{tool.desc}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section className="py-16 bg-brand-navy text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-12">From Tariff Confusion to Clear Action in Minutes</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
            {[
              { step: '01', icon: Search, title: 'Describe Your Product', desc: 'Type a product name or HTS code. AI classifies it instantly — no trade expertise needed.' },
              { step: '02', icon: Calculator, title: 'Get Stacked Rate', desc: 'We calculate every applicable tariff layer — Section 301, IEEPA, USMCA, AD/CVD — all at once.' },
              { step: '03', icon: Zap, title: 'Take Action', desc: 'Your personalized action list ranks opportunities by dollar impact. Act on refunds, savings, and risks.' },
            ].map(s => {
              const Icon = s.icon
              return (
                <div key={s.step} className="flex flex-col items-center">
                  <div className="text-brand-teal font-mono text-sm font-bold mb-3">{s.step}</div>
                  <div className="bg-brand-navy-light rounded-full p-4 mb-4">
                    <Icon size={24} className="text-brand-teal" />
                  </div>
                  <h3 className="font-bold text-lg mb-2">{s.title}</h3>
                  <p className="text-blue-300 text-sm leading-relaxed">{s.desc}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS ── */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-brand-navy text-center mb-12">SMBs Fighting Back</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, i) => (
              <div key={i} className="bg-white rounded-xl shadow-card border border-gray-100 p-6">
                <div className="flex mb-3">
                  {[1,2,3,4,5].map(s => <span key={s} className="text-brand-gold text-sm">★</span>)}
                </div>
                <p className="text-gray-700 text-sm italic leading-relaxed mb-4">"{t.quote}"</p>
                <div>
                  <p className="font-semibold text-brand-navy text-sm">{t.name}</p>
                  <p className="text-gray-400 text-xs">{t.title}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── PRICING ── */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-brand-navy mb-3">Simple, Transparent Pricing</h2>
            <p className="text-gray-500">Start free. Upgrade when you're ready. Cancel anytime.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PRICING.map(plan => (
              <div
                key={plan.name}
                className={`rounded-xl border p-7 relative ${
                  plan.highlight
                    ? 'border-brand-blue shadow-lg shadow-blue-100 bg-blue-50'
                    : 'border-gray-200 bg-white shadow-card'
                }`}
              >
                {plan.highlight && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-0.5 bg-brand-blue text-white text-xs font-bold rounded-full whitespace-nowrap">
                    Most Popular
                  </div>
                )}
                <p className="font-bold text-brand-navy text-xl mb-0.5">{plan.name}</p>
                <p className="text-gray-400 text-sm mb-4">{plan.desc}</p>
                <div className="mb-6">
                  <span className="text-4xl font-extrabold text-brand-navy">{plan.price}</span>
                  <span className="text-gray-400 text-sm ml-1">{plan.period}</span>
                </div>
                <ul className="space-y-2 mb-8">
                  {plan.features.map(f => (
                    <li key={f} className="flex items-center space-x-2 text-sm text-gray-700">
                      <CheckCircle size={14} className="text-brand-teal flex-shrink-0" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to={plan.href}
                  className={`block w-full text-center py-3 rounded-lg font-semibold text-sm transition-colors ${
                    plan.highlight
                      ? 'bg-brand-blue text-white hover:bg-brand-blue-dark'
                      : 'border border-gray-200 text-brand-navy hover:bg-gray-50'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
          <p className="text-center text-xs text-gray-400 mt-6">
            Enterprise ($199/mo) and Consultant ($499/mo) plans also available. <Link to="/pricing" className="text-brand-blue hover:underline">View all plans →</Link>
          </p>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-20 bg-brand-navy text-white text-center">
        <div className="max-w-2xl mx-auto px-4">
          <div className="mb-6 flex justify-center">
            <div className="bg-brand-teal rounded-2xl p-4">
              <Flame className="h-10 w-10 text-white" />
            </div>
          </div>
          <h2 className="text-4xl font-extrabold mb-4">
            Your competitors are already using AI.<br />
            <span className="text-brand-teal">Start for free today.</span>
          </h2>
          <p className="text-blue-200 mb-8">
            Join businesses using TariffNavigator to survive and thrive in the tariff era.
            No credit card required. 10 free lookups to start.
          </p>
          <Link
            to="/login"
            className="inline-flex items-center space-x-2 px-10 py-4 bg-brand-teal text-white font-bold rounded-xl hover:bg-brand-teal-dark transition-all shadow-lg text-lg"
          >
            <span>Create Free Account</span>
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  )
}
