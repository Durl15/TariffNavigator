import { useState } from 'react'

function CostCalculator() {
  const [formData, setFormData] = useState({
    customs_value: '',
    hts_rate: '',
    section_301_rate: '',
    freight_cost: ''
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const calculateCosts = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/costs/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customs_value: parseFloat(formData.customs_value),
          hts_rate: parseFloat(formData.hts_rate),
          section_301_rate: parseFloat(formData.section_301_rate) / 100,
          freight_cost: parseFloat(formData.freight_cost)
        })
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Error:', error)
    }
    setLoading(false)
  }

  const formatCurrency = (val) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-blue-600 mb-8">Landed Cost Calculator</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Customs Value (USD)
            </label>
            <input
              type="number"
              className="w-full p-2 border border-gray-300 rounded-md"
              placeholder="10000"
              value={formData.customs_value}
              onChange={(e) => setFormData({...formData, customs_value: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              HTS Rate (%)
            </label>
            <input
              type="number"
              step="0.1"
              className="w-full p-2 border border-gray-300 rounded-md"
              placeholder="2.5"
              value={formData.hts_rate}
              onChange={(e) => setFormData({...formData, hts_rate: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Section 301 Rate (%)
            </label>
            <input
              type="number"
              step="0.1"
              className="w-full p-2 border border-gray-300 rounded-md"
              placeholder="25"
              value={formData.section_301_rate}
              onChange={(e) => setFormData({...formData, section_301_rate: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Freight Cost (USD)
            </label>
            <input
              type="number"
              className="w-full p-2 border border-gray-300 rounded-md"
              placeholder="1500"
              value={formData.freight_cost}
              onChange={(e) => setFormData({...formData, freight_cost: e.target.value})}
            />
          </div>
        </div>
        
        <button
          onClick={calculateCosts}
          disabled={loading || !formData.customs_value}
          className="w-full bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? 'Calculating...' : 'Calculate Landed Cost'}
        </button>
      </div>

      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6 pb-4 border-b">
            <h2 className="text-xl font-semibold">Total Landed Cost</h2>
            <span className="text-3xl font-bold text-green-600">
              {formatCurrency(result.total_landed_cost)}
            </span>
          </div>
          
          <h3 className="text-lg font-medium mb-4">Cost Breakdown</h3>
          <div className="space-y-2 mb-6">
            {Object.entries(result.breakdown).map(([key, value]) => (
              <div key={key} className="flex justify-between py-1">
                <span className="text-gray-600 capitalize">
                  {key.replace(/_/g, ' ')}
                </span>
                <span className={`font-medium ${
                  key === 'section_301' && (value as number) > 0 ? 'text-red-600' : ''
                }`}>
                  {formatCurrency(value)}
                </span>
              </div>
            ))}
          </div>
          
          {result.recommendation && (
            <div className={`p-4 rounded-md ${
              result.recommendation.includes('alternative') 
                ? 'bg-yellow-50 border border-yellow-200 text-yellow-800' 
                : 'bg-blue-50 text-blue-800'
            }`}>
              <strong>Recommendation:</strong> {result.recommendation}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default CostCalculator
