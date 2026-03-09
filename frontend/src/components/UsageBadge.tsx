import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'

interface UsageData {
  used: number
  limit: number | null
  unlimited: boolean
  remaining: number | null
  upgrade_url: string | null
}

export function UsageBadge() {
  const [usage, setUsage] = useState<UsageData | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) return

    api.get('/tariff/us-import/usage', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => setUsage(r.data))
      .catch(() => {})
  }, [])

  if (!usage || usage.unlimited) return null

  const pct = usage.limit ? (usage.used / usage.limit) * 100 : 0
  const isWarning = pct >= 70
  const isDanger = pct >= 90

  return (
    <Link
      to="/pricing"
      title={`${usage.used}/${usage.limit} free lookups used this month`}
      className={`hidden md:flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
        isDanger
          ? 'border-red-400 bg-red-500/20 text-red-200 hover:bg-red-500/30'
          : isWarning
          ? 'border-yellow-400 bg-yellow-500/20 text-yellow-200 hover:bg-yellow-500/30'
          : 'border-blue-400/30 bg-white/10 text-blue-200 hover:bg-white/20'
      }`}
    >
      <span>{usage.used}/{usage.limit}</span>
      <span className="opacity-70">lookups</span>
    </Link>
  )
}
