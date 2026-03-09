import { useState } from 'react'
import { Bookmark, BookmarkCheck } from 'lucide-react'
import toast from 'react-hot-toast'
import { saveAnalysis } from '../services/api'

interface Props {
  toolType: 'cashflow' | 'drawback' | 'usmca' | 'supply_chain' | 'hts_audit' | 'sourcing' | 'scenario'
  title: string
  resultData: object
  formData?: object
  className?: string
}

export function SaveAnalysisButton({ toolType, title, resultData, formData, className = '' }: Props) {
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)

  const isAuthenticated = !!localStorage.getItem('token')

  if (!isAuthenticated) return null

  const handleSave = async () => {
    if (saved) return
    setSaving(true)
    try {
      await saveAnalysis(toolType, title, resultData, formData)
      setSaved(true)
      toast.success('Analysis saved! View in Saved Analyses.')
    } catch {
      toast.error('Could not save. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <button
      onClick={handleSave}
      disabled={saving || saved}
      className={`inline-flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors text-sm font-medium ${
        saved
          ? 'border-green-300 bg-green-50 text-green-700'
          : 'border-gray-200 bg-white text-gray-700 hover:border-brand-blue hover:text-brand-blue'
      } disabled:opacity-60 ${className}`}
    >
      {saved ? (
        <>
          <BookmarkCheck size={16} />
          <span>Saved</span>
        </>
      ) : saving ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current" />
          <span>Saving…</span>
        </>
      ) : (
        <>
          <Bookmark size={16} />
          <span>Save Analysis</span>
        </>
      )}
    </button>
  )
}
