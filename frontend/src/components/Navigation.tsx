import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Calculator, LayoutDashboard, Package, Eye, Bell, Settings, LogOut, Menu, X, Flame, DollarSign, Shield, Search, ChevronDown, Globe, Zap, BookmarkCheck, User } from 'lucide-react';
import { UsageBadge } from './UsageBadge';

interface NavigationProps {
  isAuthenticated?: boolean;
  onLogout?: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ isAuthenticated = false, onLogout }) => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const [toolsOpen, setToolsOpen] = React.useState(false);

  const navItems = [
    { path: '/calculator',   icon: Calculator,     label: 'Calculator'  },
    { path: '/dashboard',    icon: LayoutDashboard, label: 'Dashboard'   },
    { path: '/catalogs',     icon: Package,         label: 'Catalogs'    },
    { path: '/watchlists',   icon: Eye,             label: 'Watchlists'  },
    { path: '/notifications',icon: Bell,            label: 'Alerts'      },
  ];

  const toolItems = [
    { path: '/cashflow',     icon: DollarSign, label: 'Cash Flow Forecaster',    desc: 'Predict duty cash gaps' },
    { path: '/drawback',     icon: DollarSign, label: 'Drawback Finder',         desc: 'Recover up to 99% of duties' },
    { path: '/usmca-check',  icon: Search,     label: 'USMCA Checker',           desc: 'Verify 0% trade agreement rate' },
    { path: '/supply-chain', icon: Shield,     label: 'Supply Chain Scanner',    desc: 'Detect transshipment risk' },
    { path: '/hts-audit',    icon: Search,     label: 'HTS Code Audit',          desc: 'Find overpayment & misclassification' },
    { path: '/sourcing',     icon: Globe,      label: 'Alt. Sourcing Finder',    desc: 'Find lower-tariff origin countries' },
    { path: '/scenarios',    icon: Zap,        label: 'Scenario Planner',        desc: 'What-if tariff impact modeling' },
  ];

  const isToolPath = toolItems.some(t => location.pathname === t.path);

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="border-b border-white/10 sticky top-0 z-40"
         style={{background: 'linear-gradient(135deg, #152B47 0%, #1E3A5F 60%, #1a4060 100%)',
                 boxShadow: '0 1px 0 rgba(255,255,255,0.05), 0 4px 20px rgba(0,0,0,0.15)'}}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">

          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="rounded-xl p-2 flex-shrink-0 transition-all group-hover:scale-105"
                   style={{background: 'linear-gradient(135deg, #0D9488, #14B8A6)',
                           boxShadow: '0 0 12px rgba(13,148,136,0.4)'}}>
                <Flame className="h-4 w-4 text-white" />
              </div>
              <div className="leading-tight">
                <span className="block text-white font-bold text-sm tracking-tight">TariffNavigator</span>
                <span className="block text-[10px] text-blue-300/80 font-medium">DJ AI Business Consultant</span>
              </div>
            </Link>
          </div>

          {/* Desktop nav links */}
          <div className="hidden md:flex md:items-center md:space-x-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    active
                      ? 'text-white'
                      : 'text-blue-200/80 hover:text-white hover:bg-white/10'
                  }`}
                  style={active ? {background: 'linear-gradient(135deg, #0D9488, #14B8A6)',
                                   boxShadow: '0 0 12px rgba(13,148,136,0.3)'} : {}}
                >
                  <Icon size={14} />
                  <span>{item.label}</span>
                </Link>
              );
            })}

            {/* Compliance Tools dropdown */}
            <div className="relative">
              <button
                onClick={() => setToolsOpen(!toolsOpen)}
                onBlur={() => setTimeout(() => setToolsOpen(false), 150)}
                className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  isToolPath ? 'text-white' : 'text-blue-200/80 hover:text-white hover:bg-white/10'
                }`}
                style={isToolPath ? {background: 'linear-gradient(135deg, #0D9488, #14B8A6)',
                                     boxShadow: '0 0 12px rgba(13,148,136,0.3)'} : {}}
              >
                <Shield size={14} />
                <span>Tools</span>
                <ChevronDown size={11} className={`transition-transform duration-200 ${toolsOpen ? 'rotate-180' : ''}`} />
              </button>
              {toolsOpen && (
                <div className="absolute top-full left-0 mt-2 w-72 bg-white rounded-2xl shadow-float border border-gray-100 py-2 z-50 animate-fade">
                  <p className="px-4 py-1.5 text-[10px] font-semibold text-gray-400 uppercase tracking-widest">Compliance Tools</p>
                  {toolItems.map(t => {
                    const Icon = t.icon;
                    return (
                      <Link
                        key={t.path}
                        to={t.path}
                        className="flex items-start space-x-3 px-4 py-2.5 hover:bg-blue-50/60 transition-colors group"
                      >
                        <div className="w-7 h-7 rounded-lg bg-brand-navy/8 flex items-center justify-center flex-shrink-0 mt-0.5 group-hover:bg-brand-blue/10 transition-colors">
                          <Icon size={13} className="text-brand-blue" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-brand-navy">{t.label}</p>
                          <p className="text-xs text-gray-400 mt-0.5">{t.desc}</p>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Right actions */}
          <div className="hidden md:flex md:items-center md:space-x-2">
            <UsageBadge />
            <Link
              to="/pricing"
              className="text-sm font-bold px-3 py-1.5 rounded-lg transition-all hover:scale-105"
              style={{color: '#E8C066', textShadow: '0 0 12px rgba(212,168,67,0.4)'}}
            >
              Upgrade ✦
            </Link>

            {isAuthenticated ? (
              <>
                <Link to="/saved" className="flex items-center space-x-1.5 px-3 py-2 text-sm text-blue-200/80 hover:text-white hover:bg-white/10 rounded-lg transition-all">
                  <BookmarkCheck size={14} />
                  <span>Saved</span>
                </Link>
                <Link to="/account" className="flex items-center space-x-1.5 px-2.5 py-1.5 text-sm font-medium text-blue-200/80 hover:text-white border border-white/15 hover:border-white/30 rounded-lg transition-all">
                  <User size={14} />
                  <span>Account</span>
                </Link>
                <Link to="/admin" className="flex items-center space-x-1.5 px-3 py-2 text-sm text-blue-200/80 hover:text-white hover:bg-white/10 rounded-lg transition-all">
                  <Settings size={14} />
                </Link>
                <button onClick={onLogout} className="flex items-center space-x-1.5 px-3 py-2 text-sm text-red-300/80 hover:text-white hover:bg-red-500/20 rounded-lg transition-all">
                  <LogOut size={14} />
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 bg-brand-blue text-white text-sm font-medium hover:bg-brand-blue-dark rounded-lg transition-colors"
              >
                Sign In
              </Link>
            )}
          </div>

          {/* Mobile menu toggle */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-blue-200 hover:text-white hover:bg-brand-navy-light transition-colors"
            >
              {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-3 space-y-1 border-t border-brand-navy-light">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? 'bg-brand-teal text-white'
                      : 'text-blue-200 hover:bg-brand-navy-light hover:text-white'
                  }`}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
            <div className="border-t border-brand-navy-light pt-2 mt-1">
              <p className="px-4 py-1 text-xs text-blue-400 uppercase tracking-wider">Compliance Tools</p>
              {toolItems.map(t => {
                const Icon = t.icon;
                return (
                  <Link
                    key={t.path}
                    to={t.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center space-x-3 px-4 py-2.5 text-sm text-blue-200 hover:bg-brand-navy-light hover:text-white rounded-lg transition-colors"
                  >
                    <Icon size={15} />
                    <span>{t.label}</span>
                  </Link>
                );
              })}
            </div>

            <div className="border-t border-brand-navy-light pt-2 mt-2 space-y-1">
              <Link
                to="/pricing"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center px-4 py-3 text-sm font-semibold text-brand-gold"
              >
                Upgrade Plan
              </Link>
              {isAuthenticated ? (
                <>
                  <Link
                    to="/saved"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center space-x-3 px-4 py-3 text-sm text-blue-200 hover:bg-brand-navy-light rounded-lg"
                  >
                    <BookmarkCheck size={18} />
                    <span>Saved Analyses</span>
                  </Link>
                  <Link
                    to="/account"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center space-x-3 px-4 py-3 text-sm text-blue-200 hover:bg-brand-navy-light rounded-lg"
                  >
                    <User size={18} />
                    <span>My Account</span>
                  </Link>
                  <Link
                    to="/admin"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center space-x-3 px-4 py-3 text-sm text-blue-200 hover:bg-brand-navy-light rounded-lg"
                  >
                    <Settings size={18} />
                    <span>Admin Panel</span>
                  </Link>
                  <button
                    onClick={() => { setMobileMenuOpen(false); onLogout?.(); }}
                    className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-red-300 hover:bg-red-500/10 rounded-lg"
                  >
                    <LogOut size={18} />
                    <span>Logout</span>
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center px-4 py-3 bg-brand-blue text-white rounded-lg text-sm font-medium"
                >
                  Sign In
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
