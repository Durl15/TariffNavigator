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

// FTA Wizard Types
export interface FTACheckResult {
  is_eligible: boolean
  fta_name: string | null
  standard_rate: number
  preferential_rate: number
  savings_percent: number
}

export interface WizardState {
  currentStep: 1 | 2 | 3 | 4
  hsCode: string
  hsDescription: string
  originCountry: string
  destinationCountry: string
  ftaCheckResult: FTACheckResult | null
  ftaEligible: boolean
  ftaName: string | null
  standardRate: number
  preferentialRate: number
  cifValue: number
  savings: number
  savingsPercent: number
  standardCalculation: {
    cifValue: number
    duty: number
    totalCost: number
  } | null
  ftaCalculation: {
    cifValue: number
    duty: number
    totalCost: number
  } | null
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

// FTA Check
export async function checkFTAEligibility(
  hsCode: string,
  originCountry: string,
  destCountry: string
): Promise<FTACheckResult> {
  const params = new URLSearchParams({
    hs_code: hsCode,
    origin_country: originCountry,
    dest_country: destCountry
  })

  const response = await api.get(`/tariff/fta-check?${params.toString()}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
  return response.data
}

// ============================================================================
// SAVED CALCULATIONS & FAVORITES
// ============================================================================

// Types
export interface Calculation {
  id: string
  user_id: string
  organization_id?: string
  name?: string
  description?: string
  hs_code: string
  product_description?: string
  origin_country: string
  destination_country: string
  cif_value: number
  currency: string
  result: any
  total_cost: number
  customs_duty?: number
  vat_amount?: number
  fta_eligible: boolean
  fta_savings?: number
  is_favorite: boolean
  tags?: string[]
  view_count: number
  created_at: string
  updated_at?: string
}

export interface CalculationListItem {
  id: string
  name?: string
  hs_code: string
  product_description?: string
  origin_country: string
  destination_country: string
  total_cost: number
  currency: string
  is_favorite: boolean
  tags?: string[]
  created_at: string
}

export interface CalculationListResponse {
  calculations: CalculationListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface SaveCalculationRequest {
  name: string
  description?: string
  tags?: string[]
  hs_code: string
  product_description?: string
  origin_country: string
  destination_country: string
  cif_value: number
  currency: string
  result: any
  total_cost: number
  customs_duty?: number
  vat_amount?: number
  fta_eligible: boolean
  fta_savings?: number
}

// Get saved calculations
export async function getSavedCalculations(
  page: number = 1,
  pageSize: number = 20,
  search?: string,
  tag?: string,
  sortBy: 'created_at' | 'name' | 'total_cost' = 'created_at',
  sortOrder: 'asc' | 'desc' = 'desc'
): Promise<CalculationListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
    sort_by: sortBy,
    sort_order: sortOrder,
  })

  if (search) params.append('search', search)
  if (tag) params.append('tag', tag)

  const response = await api.get(`/calculations/saved?${params.toString()}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// Get favorite calculations
export async function getFavoriteCalculations(
  page: number = 1,
  pageSize: number = 20
): Promise<CalculationListResponse> {
  const response = await api.get(`/calculations/favorites?page=${page}&page_size=${pageSize}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// Get single calculation
export async function getCalculation(id: string): Promise<Calculation> {
  const response = await api.get(`/calculations/${id}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// Save calculation with metadata
export async function saveCalculation(
  data: SaveCalculationRequest
): Promise<Calculation> {
  const response = await api.post(`/calculations/save`, data, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// Toggle favorite status
export async function toggleFavorite(
  id: string,
  isFavorite: boolean
): Promise<{ id: string; is_favorite: boolean; message: string }> {
  const response = await api.put(
    `/calculations/${id}/favorite?is_favorite=${isFavorite}`,
    null,
    {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    }
  )
  return response.data
}

// Update calculation metadata
export async function updateCalculation(
  id: string,
  data: {
    name?: string
    description?: string
    tags?: string[]
  }
): Promise<Calculation> {
  const response = await api.put(`/calculations/${id}`, data, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// Delete calculation (soft delete)
export async function deleteCalculation(id: string): Promise<void> {
  await api.delete(`/calculations/${id}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
}

// Duplicate calculation
export async function duplicateCalculation(id: string): Promise<Calculation> {
  const response = await api.post(`/calculations/${id}/duplicate`, null, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// Create share link
export async function createShareLink(
  id: string,
  expiresHours?: number
): Promise<{ share_token: string; share_url: string; expires_at?: string; created_at: string }> {
  const url = expiresHours
    ? `/calculations/${id}/share?expires_hours=${expiresHours}`
    : `/calculations/${id}/share`

  const response = await api.post(url, null, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// ============================================================================
// COMPARISON
// ============================================================================

// Types
export interface ComparisonRequest {
  calculation_ids: string[]
}

export interface ComparisonMetrics {
  min_total_cost: number
  max_total_cost: number
  avg_total_cost: number
  cost_spread: number
  cost_spread_percent: number
  min_duty_rate?: number
  max_duty_rate?: number
  avg_duty_rate?: number
  best_option_id: string
  worst_option_id: string
  has_fta_eligible: boolean
  total_fta_savings?: number
  comparison_type: string
}

export interface ComparisonCalculationItem {
  id: string
  name?: string
  hs_code: string
  product_description?: string
  origin_country: string
  destination_country: string
  cif_value: number
  currency: string
  total_cost: number
  customs_duty?: number
  vat_amount?: number
  fta_eligible: boolean
  fta_savings?: number
  result: any
  created_at: string
  rank: number
  cost_vs_average: number
  cost_vs_average_percent: number
  is_best: boolean
  is_worst: boolean
}

export interface ComparisonResponse {
  calculations: ComparisonCalculationItem[]
  metrics: ComparisonMetrics
  comparison_date: string
  total_compared: number
}

// Compare calculations
export async function compareCalculations(
  calculationIds: string[]
): Promise<ComparisonResponse> {
  const response = await api.post('/comparisons/compare', {
    calculation_ids: calculationIds
  }, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// Export comparison as PDF
export async function exportComparisonPDF(calculationIds: string[]): Promise<Blob> {
  const response = await api.post('/export/comparison/pdf', {
    calculation_ids: calculationIds
  }, {
    responseType: 'blob',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}

// Export comparison as CSV
export async function exportComparisonCSV(calculationIds: string[]): Promise<Blob> {
  const response = await api.post('/export/comparison/csv', {
    calculation_ids: calculationIds
  }, {
    responseType: 'blob',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
  })
  return response.data
}
