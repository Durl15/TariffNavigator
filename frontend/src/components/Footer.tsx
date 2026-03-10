import { Flame } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="bg-brand-navy mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">

          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="bg-brand-teal rounded-lg p-1.5 shrink-0">
              <Flame className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-white font-bold text-sm">TariffNavigator™</p>
              <p className="text-blue-300 text-xs">DJ AI Business Consultant · Syracuse, NY</p>
            </div>
          </div>

          {/* Links */}
          <nav className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-blue-300">
            <Link to="/calculator"   className="hover:text-white transition-colors">Calculator</Link>
            <Link to="/pricing"      className="hover:text-white transition-colors">Pricing</Link>
            <Link to="/dashboard"    className="hover:text-white transition-colors">Dashboard</Link>
            <Link to="/watchlists"   className="hover:text-white transition-colors">Watchlists</Link>
            <a href="mailto:support@tariffnavigator.com" className="hover:text-white transition-colors">Support</a>
          </nav>
        </div>

        <div className="mt-8 pt-6 border-t border-blue-900 space-y-1">
          <p className="text-xs text-blue-400 text-center">
            © 2025 DJ AI Business Consultant LLC. All rights reserved.
          </p>
          <p className="text-xs text-blue-500 text-center">
            TariffNavigator™ is a product of DJ AI Business Consultant.
            Unauthorized reproduction or distribution is prohibited.
          </p>
          <p className="text-xs text-blue-600 text-center mt-2">
            Transforming Business, Rising Above the Challenges
          </p>
        </div>
      </div>
    </footer>
  )
}
