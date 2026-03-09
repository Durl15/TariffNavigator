import { useState } from 'react'
import { FileDown } from 'lucide-react'
import toast from 'react-hot-toast'
import { exportCompliancePDF, downloadBlob } from '../services/api'

interface Props {
  reportType: 'drawback' | 'supply_chain' | 'hts_audit' | 'usmca' | 'cashflow' | 'sourcing' | 'scenario'
  title: string
  data: object
  metadata?: object
  className?: string
}

export function ComplianceExportButton({ reportType, title, data, metadata, className = '' }: Props) {
  const [exporting, setExporting] = useState(false)

  const handleExport = async () => {
    setExporting(true)
    try {
      const blob = await exportCompliancePDF(reportType, title, data, metadata)
      const ts = new Date().toISOString().split('T')[0]
      downloadBlob(blob, `tariffnavigator_${reportType}_${ts}.pdf`)
      toast.success('PDF exported successfully!')
    } catch {
      toast.error('Export failed. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  return (
    <button
      onClick={handleExport}
      disabled={exporting}
      className={`inline-flex items-center space-x-2 px-4 py-2 bg-brand-navy text-white rounded-lg hover:bg-brand-navy-dark transition-colors disabled:opacity-50 text-sm font-medium ${className}`}
    >
      {exporting ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
          <span>Exporting…</span>
        </>
      ) : (
        <>
          <FileDown size={16} />
          <span>Export PDF</span>
        </>
      )}
    </button>
  )
}
