// Search context — persists the original calculator submission across navigation.
// Alternative/scenario pages read this on mount to pre-populate fields.
// Changes in alternative views write to their own local state only — never here.

const KEY = 'tn_search_context'

export interface SearchContext {
  hts_code: string
  product_description: string
  country: string
  cif_value: string
  duty_rate: number
  timestamp: number
}

export function saveSearchContext(ctx: Omit<SearchContext, 'timestamp'>): void {
  try {
    sessionStorage.setItem(KEY, JSON.stringify({ ...ctx, timestamp: Date.now() }))
  } catch {
    // sessionStorage unavailable — silently skip
  }
}

export function getSearchContext(): SearchContext | null {
  try {
    const raw = sessionStorage.getItem(KEY)
    if (!raw) return null
    return JSON.parse(raw) as SearchContext
  } catch {
    return null
  }
}

export function clearSearchContext(): void {
  try {
    sessionStorage.removeItem(KEY)
  } catch {
    // ignore
  }
}
