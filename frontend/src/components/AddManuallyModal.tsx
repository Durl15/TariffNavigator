import { useState } from 'react'
import { X, Plus, ArrowRight, Package } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { createCatalog, addCatalogItem } from '../services/api'

interface Props {
  isOpen: boolean
  onClose: () => void
  onSuccess: (catalogId: string) => void
  existingCatalogs?: { id: string; name: string }[]
}

const COUNTRIES = [
  { code: 'CN', name: 'China' },
  { code: 'MX', name: 'Mexico' },
  { code: 'CA', name: 'Canada' },
  { code: 'VN', name: 'Vietnam' },
  { code: 'IN', name: 'India' },
  { code: 'KR', name: 'South Korea' },
  { code: 'TW', name: 'Taiwan' },
  { code: 'TH', name: 'Thailand' },
  { code: 'MY', name: 'Malaysia' },
  { code: 'JP', name: 'Japan' },
  { code: 'BD', name: 'Bangladesh' },
  { code: 'ID', name: 'Indonesia' },
  { code: 'EU', name: 'European Union' },
  { code: 'US', name: 'United States' },
]

const CATEGORIES = ['Electronics', 'Apparel', 'Footwear', 'Hardware', 'Housewares', 'Fitness', 'Kitchen', 'Safety', 'Energy', 'Other']

const emptyItem = () => ({
  sku: '',
  product_name: '',
  hs_code: '',
  origin_country: 'CN',
  cogs: '',
  retail_price: '',
  annual_volume: '',
  category: '',
  notes: '',
})

export default function AddManuallyModal({ isOpen, onClose, onSuccess, existingCatalogs = [] }: Props) {
  const queryClient = useQueryClient()
  const [step, setStep] = useState<'catalog' | 'product'>('catalog')
  const [catalogMode, setCatalogMode] = useState<'new' | 'existing'>('new')
  const [catalogName, setCatalogName] = useState('')
  const [catalogDesc, setCatalogDesc] = useState('')
  const [selectedCatalogId, setSelectedCatalogId] = useState(existingCatalogs[0]?.id || '')
  const [activeCatalogId, setActiveCatalogId] = useState<string | null>(null)
  const [activeCatalogName, setActiveCatalogName] = useState('')
  const [item, setItem] = useState(emptyItem())
  const [savedCount, setSavedCount] = useState(0)

  const createCatalogMutation = useMutation({
    mutationFn: () => createCatalog({ name: catalogName.trim(), description: catalogDesc.trim() || undefined }),
    onSuccess: (catalog) => {
      setActiveCatalogId(catalog.id)
      setActiveCatalogName(catalog.name)
      queryClient.invalidateQueries({ queryKey: ['catalogs'] })
      setStep('product')
    },
    onError: () => toast.error('Failed to create catalog'),
  })

  const addItemMutation = useMutation({
    mutationFn: (catalogId: string) => addCatalogItem(catalogId, {
      sku: item.sku.trim(),
      product_name: item.product_name.trim() || undefined,
      hs_code: item.hs_code.trim() || undefined,
      origin_country: item.origin_country,
      cogs: parseFloat(item.cogs),
      retail_price: parseFloat(item.retail_price),
      annual_volume: parseInt(item.annual_volume),
      category: item.category || undefined,
      notes: item.notes.trim() || undefined,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['catalogs'] })
      setSavedCount(c => c + 1)
      toast.success('Product saved!')
    },
    onError: () => toast.error('Failed to add product'),
  })

  const handleCatalogNext = () => {
    if (catalogMode === 'new') {
      if (!catalogName.trim()) { toast.error('Enter a catalog name'); return }
      createCatalogMutation.mutate()
    } else {
      if (!selectedCatalogId) { toast.error('Select a catalog'); return }
      const cat = existingCatalogs.find(c => c.id === selectedCatalogId)
      setActiveCatalogId(selectedCatalogId)
      setActiveCatalogName(cat?.name || '')
      setStep('product')
    }
  }

  const handleSaveProduct = async (andAdd: boolean) => {
    if (!item.sku.trim()) { toast.error('SKU is required'); return }
    if (!item.cogs || isNaN(parseFloat(item.cogs))) { toast.error('COGS is required'); return }
    if (!item.retail_price || isNaN(parseFloat(item.retail_price))) { toast.error('Retail price is required'); return }
    if (!item.annual_volume || isNaN(parseInt(item.annual_volume))) { toast.error('Annual volume is required'); return }
    if (!activeCatalogId) return

    await addItemMutation.mutateAsync(activeCatalogId)
    if (andAdd) {
      setItem(emptyItem())
    } else {
      onSuccess(activeCatalogId)
    }
  }

  const handleClose = () => {
    setStep('catalog')
    setCatalogName('')
    setCatalogDesc('')
    setItem(emptyItem())
    setSavedCount(0)
    setActiveCatalogId(null)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto">

        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-brand-navy flex items-center justify-center">
              <Package size={15} className="text-white" />
            </div>
            <div>
              <h2 className="font-bold text-brand-navy text-lg">Add Products Manually</h2>
              {activeCatalogName && (
                <p className="text-xs text-gray-500">
                  Catalog: {activeCatalogName}{savedCount > 0 ? ` · ${savedCount} saved` : ''}
                </p>
              )}
            </div>
          </div>
          <button onClick={handleClose} className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
            <X size={18} className="text-gray-500" />
          </button>
        </div>

        <div className="px-6 py-5">

          {/* STEP 1: Catalog */}
          {step === 'catalog' && (
            <div className="space-y-5">
              {existingCatalogs.length > 0 && (
                <div className="flex rounded-xl border border-gray-200 overflow-hidden">
                  <button
                    onClick={() => setCatalogMode('new')}
                    className={`flex-1 py-2.5 text-sm font-medium transition-colors ${catalogMode === 'new' ? 'bg-brand-navy text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                  >
                    New Catalog
                  </button>
                  <button
                    onClick={() => setCatalogMode('existing')}
                    className={`flex-1 py-2.5 text-sm font-medium transition-colors ${catalogMode === 'existing' ? 'bg-brand-navy text-white' : 'text-gray-600 hover:bg-gray-50'}`}
                  >
                    Add to Existing
                  </button>
                </div>
              )}

              {catalogMode === 'new' ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Catalog Name *</label>
                    <input
                      autoFocus
                      type="text"
                      value={catalogName}
                      onChange={e => setCatalogName(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && handleCatalogNext()}
                      placeholder="e.g. Spring 2026 Product Line"
                      className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Description (optional)</label>
                    <input
                      type="text"
                      value={catalogDesc}
                      onChange={e => setCatalogDesc(e.target.value)}
                      placeholder="Notes about this catalog"
                      className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                    />
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Select Catalog</label>
                  <select
                    value={selectedCatalogId}
                    onChange={e => setSelectedCatalogId(e.target.value)}
                    className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
                  >
                    {existingCatalogs.map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <button
                onClick={handleCatalogNext}
                disabled={createCatalogMutation.isPending}
                className="w-full flex items-center justify-center space-x-2 py-3 bg-brand-navy text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all disabled:opacity-50"
              >
                {createCatalogMutation.isPending
                  ? <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  : <><span>Next — Add Products</span><ArrowRight size={15} /></>
                }
              </button>
            </div>
          )}

          {/* STEP 2: Product form */}
          {step === 'product' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">SKU *</label>
                  <input autoFocus type="text" value={item.sku}
                    onChange={e => setItem(i => ({ ...i, sku: e.target.value }))}
                    placeholder="e.g. SKU-001"
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Product Name</label>
                  <input type="text" value={item.product_name}
                    onChange={e => setItem(i => ({ ...i, product_name: e.target.value }))}
                    placeholder="e.g. Wireless Mouse"
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">HTS Code</label>
                  <input type="text" value={item.hs_code}
                    onChange={e => setItem(i => ({ ...i, hs_code: e.target.value }))}
                    placeholder="e.g. 8471.30"
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Origin Country *</label>
                  <select value={item.origin_country}
                    onChange={e => setItem(i => ({ ...i, origin_country: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue">
                    {COUNTRIES.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">COGS / Unit ($) *</label>
                  <input type="number" min="0" step="0.01" value={item.cogs}
                    onChange={e => setItem(i => ({ ...i, cogs: e.target.value }))}
                    placeholder="0.00"
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Retail Price ($) *</label>
                  <input type="number" min="0" step="0.01" value={item.retail_price}
                    onChange={e => setItem(i => ({ ...i, retail_price: e.target.value }))}
                    placeholder="0.00"
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Annual Volume (units) *</label>
                  <input type="number" min="0" value={item.annual_volume}
                    onChange={e => setItem(i => ({ ...i, annual_volume: e.target.value }))}
                    placeholder="1000"
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Category</label>
                  <select value={item.category}
                    onChange={e => setItem(i => ({ ...i, category: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue">
                    <option value="">— Select —</option>
                    {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Notes (optional)</label>
                <input type="text" value={item.notes}
                  onChange={e => setItem(i => ({ ...i, notes: e.target.value }))}
                  placeholder="e.g. Section 301 applies, check exclusions"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue" />
              </div>

              {savedCount > 0 && (
                <div className="flex items-center space-x-2 bg-green-50 border border-green-200 rounded-lg px-3 py-2 text-sm text-green-700">
                  <span>✓</span>
                  <span>{savedCount} product{savedCount > 1 ? 's' : ''} saved to catalog</span>
                </div>
              )}

              <div className="flex space-x-3 pt-1">
                <button
                  onClick={() => handleSaveProduct(true)}
                  disabled={addItemMutation.isPending}
                  className="flex-1 flex items-center justify-center space-x-2 py-2.5 border-2 border-brand-navy text-brand-navy rounded-xl font-semibold text-sm hover:bg-brand-navy hover:text-white transition-all disabled:opacity-50"
                >
                  {addItemMutation.isPending
                    ? <div className="h-4 w-4 border-2 border-current/30 border-t-current rounded-full animate-spin" />
                    : <><Plus size={15} /><span>Save &amp; Add Another</span></>
                  }
                </button>
                <button
                  onClick={() => handleSaveProduct(false)}
                  disabled={addItemMutation.isPending}
                  className="flex-1 flex items-center justify-center space-x-2 py-2.5 bg-brand-teal text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all disabled:opacity-50"
                >
                  <span>Save &amp; View Catalog</span>
                  <ArrowRight size={15} />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
