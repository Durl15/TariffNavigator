import axios from 'axios'

// Use environment variable for API URL, fallback to production URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://tariffnavigator-backend.onrender.com/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface PublicStats {
  total_calculations: number
  calculations_this_month: number
  calculations_today: number
  total_hs_codes: number
  supported_countries: string[]
}

export interface PopularHSCode {
  hs_code: string
  description: string
  usage_count: number
}

export interface PDFExportData {
  hs_code: string
  country: string
  description: string
  rates: {
    mfn?: number
    vat?: number
    consumption?: number
  }
  calculation: {
    cif_value: number
    customs_duty?: number
    vat?: number
    consumption_tax?: number
    total_cost: number
    currency: string
  }
  origin_country?: string
  destination_country?: string
  original_currency?: string
  exchange_rate?: number
  converted_calculation?: any
}

export interface CSVExportFilters {
  calculation_ids?: string[]
  date_from?: string
  date_to?: string
  hs_code?: string
  limit?: number
}

// Public Stats
export async function getPublicStats(): Promise<PublicStats> {
  const response = await api.get('/stats/public')
  return response.data
}

export async function getPopularHSCodes(): Promise<PopularHSCode[]> {
  const response = await api.get('/stats/public/popular-hs-codes')
  return response.data
}

// PDF Export
export async function exportPDF(data: PDFExportData): Promise<Blob> {
  const response = await api.post('/export/pdf', data, {
    responseType: 'blob',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// CSV Export
export async function exportCSV(filters: CSVExportFilters = {}): Promise<Blob> {
  const response = await api.post('/export/csv', filters, {
    responseType: 'blob',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// Helper function to trigger browser download
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
