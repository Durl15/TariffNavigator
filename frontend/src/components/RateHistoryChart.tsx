import { useQuery } from '@tanstack/react-query'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { TrendingUp } from 'lucide-react'
import { api } from '../services/api'

interface RatePoint {
  date: string
  label: string
  mfn: number
  s232: number
  s301: number
  ieepa: number
  total: number
}

interface Props {
  htsno: string
  country: string
  countryName: string
}

const COUNTRY_LABELS: Record<string, string> = {
  CN: 'China', VN: 'Vietnam', MX: 'Mexico', CA: 'Canada',
  DE: 'Germany', JP: 'Japan', KR: 'South Korea', IN: 'India',
}

async function fetchHistory(htsno: string, country: string): Promise<RatePoint[]> {
  const { data } = await api.get(`/tariff/hts/rate-history/${htsno}`, { params: { country } })
  return data.timeline
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload as RatePoint
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-lg p-4 text-sm min-w-[180px]">
      <p className="font-semibold text-brand-navy mb-1">{d.label}</p>
      <p className="text-gray-400 text-xs mb-3">{d.date}</p>
      {d.mfn > 0   && <p className="text-gray-600">MFN base: <span className="font-medium">{d.mfn}%</span></p>}
      {d.s232 > 0  && <p className="text-orange-600">Section 232: <span className="font-medium">+{d.s232}%</span></p>}
      {d.s301 > 0  && <p className="text-red-600">Section 301: <span className="font-medium">+{d.s301}%</span></p>}
      {d.ieepa > 0 && <p className="text-purple-600">IEEPA: <span className="font-medium">+{d.ieepa}%</span></p>}
      <div className="mt-2 pt-2 border-t border-gray-100">
        <p className="font-bold text-brand-navy">Total: {d.total}%</p>
      </div>
    </div>
  )
}

export default function RateHistoryChart({ htsno, country, countryName }: Props) {
  const { data, isLoading } = useQuery<RatePoint[]>({
    queryKey: ['rateHistory', htsno, country],
    queryFn: () => fetchHistory(htsno, country),
    staleTime: 3600_000,
    enabled: !!htsno && !!country,
  })

  if (isLoading) {
    return (
      <div className="card p-6 animate-pulse">
        <div className="h-4 bg-gray-100 rounded w-40 mb-4" />
        <div className="h-48 bg-gray-50 rounded-xl" />
      </div>
    )
  }

  if (!data?.length) return null

  // Format date labels short
  const chartData = data.map(d => ({
    ...d,
    shortDate: d.date.slice(0, 7), // "2025-04"
  }))

  const displayCountry = countryName || COUNTRY_LABELS[country] || country
  const current = data[data.length - 1]

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center"
               style={{ background: 'linear-gradient(135deg,#0D9488,#14B8A6)' }}>
            <TrendingUp className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="font-semibold text-brand-navy text-sm">Rate History</p>
            <p className="text-xs text-gray-400">{displayCountry} · HTS {htsno}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-brand-navy">{current.total}%</p>
          <p className="text-xs text-gray-400">current effective rate</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={chartData} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="mfnGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4A90D9" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#4A90D9" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="s232Grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#F97316" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#F97316" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="s301Grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="ieepaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="shortDate" tick={{ fontSize: 11, fill: '#9CA3AF' }} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#9CA3AF' }} tickLine={false} axisLine={false}
                 tickFormatter={(v) => `${v}%`} />
          <Tooltip content={<CustomTooltip />} />
          <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11 }} />
          <Area type="stepAfter" dataKey="mfn"   name="MFN Base"    stackId="1"
                stroke="#4A90D9" fill="url(#mfnGrad)"   strokeWidth={1.5} dot={false} />
          <Area type="stepAfter" dataKey="s232"  name="Section 232" stackId="1"
                stroke="#F97316" fill="url(#s232Grad)"  strokeWidth={1.5} dot={false} />
          <Area type="stepAfter" dataKey="s301"  name="Section 301" stackId="1"
                stroke="#EF4444" fill="url(#s301Grad)"  strokeWidth={1.5} dot={false} />
          <Area type="stepAfter" dataKey="ieepa" name="IEEPA"       stackId="1"
                stroke="#8B5CF6" fill="url(#ieepaGrad)" strokeWidth={1.5} dot={false} />
        </AreaChart>
      </ResponsiveContainer>

      <p className="text-xs text-gray-400 mt-3 text-center">
        Based on published Federal Register notices and executive orders
      </p>
    </div>
  )
}
