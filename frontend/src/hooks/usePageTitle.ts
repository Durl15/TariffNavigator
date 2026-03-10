import { useEffect } from 'react'

export function usePageTitle(title: string) {
  useEffect(() => {
    const prev = document.title
    document.title = title ? `${title} — TariffNavigator` : 'TariffNavigator — AI-Powered Tariff Intelligence'
    return () => { document.title = prev }
  }, [title])
}
