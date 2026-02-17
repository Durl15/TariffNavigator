from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.api.v1.api import api_router
from app.middleware.audit import AuditMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# CORS - Allow all for sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit logging middleware - logs all write operations
app.add_middleware(AuditMiddleware)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tariff Navigator</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f5f7fa;
                padding: 20px;
                line-height: 1.6;
            }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #667eea; margin-bottom: 10px; }
            .subtitle { color: #666; margin-bottom: 30px; }
            
            .card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .form-group { margin-bottom: 15px; }
            label { 
                display: block; 
                font-weight: 600; 
                margin-bottom: 5px; 
                color: #333; 
            }
            input, select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            
            button {
                background: #667eea;
                color: white;
                border: none;
                padding: 14px 28px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                margin-top: 10px;
                transition: background 0.3s;
            }
            button:hover { background: #5a67d8; }
            button:disabled { 
                background: #ccc; 
                cursor: not-allowed; 
            }
            
            .results {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 20px;
                margin-top: 20px;
                border-radius: 0 8px 8px 0;
                display: none;
            }
            .results.show { display: block; }
            
            .result-row {
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #e0e0e0;
            }
            .result-row:last-child { 
                border-bottom: none; 
                font-weight: bold; 
                font-size: 1.3em; 
                color: #667eea;
                margin-top: 10px;
                padding-top: 10px;
                border-top: 2px solid #667eea;
            }
            
            .error { 
                color: #e53e3e; 
                background: #fed7d7; 
                padding: 12px; 
                border-radius: 8px; 
                margin-top: 15px; 
            }
            
            .suggestions {
                background: white;
                border: 2px solid #e0e0e0;
                border-top: none;
                border-radius: 0 0 8px 8px;
                max-height: 250px;
                overflow-y: auto;
                position: absolute;
                width: 100%;
                z-index: 10;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .suggestion-item {
                padding: 12px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
                transition: background 0.2s;
            }
            .suggestion-item:hover { background: #f5f5f5; }
            .suggestion-code { 
                font-weight: bold; 
                color: #667eea; 
                font-size: 1.1em;
            }
            .suggestion-desc { 
                font-size: 0.9em; 
                color: #666; 
                margin-top: 2px;
            }
            .suggestion-rate {
                font-size: 0.8em;
                color: #999;
                margin-top: 2px;
            }
            
            .fta-box {
                background: #f0fff4;
                border: 2px solid #9ae6b4;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
            }
            .fta-box.not-eligible {
                background: #f7fafc;
                border-color: #e2e8f0;
            }
            .fta-title {
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .fta-eligible { color: #22543d; }
            .fta-not-eligible { color: #742a2a; }
            
            .grid-2 {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            
            .loading {
                text-align: center;
                color: #667eea;
                padding: 20px;
            }
            
            .api-link {
                font-size: 0.85em;
                color: #667eea;
                text-decoration: none;
                float: right;
            }
            
            h2 {
                margin-bottom: 20px;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚢 Tariff Navigator</h1>
            <p class="subtitle">AI-powered tariff calculator with FTA & multi-currency support</p>
            
            <div class="card">
                <h2>Tariff Calculator</h2>
                
                <div class="grid-2">
                    <div class="form-group">
                        <label>Destination Country</label>
                        <select id="country" onchange="clearSelection()">
                            <option value="CN">China (CN)</option>
                            <option value="EU">European Union (EU)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Display Currency</label>
                        <select id="currency">
                            <option value="USD">USD ($) - US Dollar</option>
                            <option value="CNY">CNY (CN¥) - Chinese Yuan</option>
                            <option value="EUR">EUR (€) - Euro</option>
                            <option value="JPY">JPY (JP¥) - Japanese Yen</option>
                            <option value="GBP">GBP (£) - British Pound</option>
                            <option value="KRW">KRW (₩) - Korean Won</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group" style="position: relative;">
                    <label>Search Product or HS Code</label>
                    <input 
                        type="text" 
                        id="search-input" 
                        placeholder="Type 'car' or '8703'..." 
                        autocomplete="off"
                        oninput="handleSearch(this.value)"
                        onblur="hideSuggestionsDelayed()"
                    >
                    <div id="suggestions" class="suggestions" style="display: none;"></div>
                </div>
                
                <div class="form-group">
                    <label>Selected HS Code</label>
                    <input 
                        type="text" 
                        id="hs-code" 
                        readonly 
                        placeholder="Select from search above"
                        style="background: #f5f5f5;"
                    >
                </div>
                
                <div class="form-group">
                    <label>CIF Value (USD)</label>
                    <input 
                        type="number" 
                        id="value" 
                        placeholder="50000" 
                        value="50000"
                    >
                </div>
                
                <button id="calc-btn" onclick="calculate()">Calculate Tariff</button>
                
                <div id="loading" class="loading" style="display: none;">Calculating...</div>
                <div id="error"></div>
                <div id="results" class="results"></div>
            </div>
            
            <div class="card" style="background: #667eea; color: white;">
                <h3 style="margin-bottom: 15px;">📋 API Endpoints</h3>
                <p style="margin-bottom: 10px;">Base URL: <code style="background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 4px;">http://192.168.0.115:8000/api/v1</code></p>
                <ul style="margin-left: 20px; line-height: 2;">
                    <li><a href="/api/v1/health" style="color: #fff; text-decoration: underline;">/health</a> - Check API status</li>
                    <li>/tariff/search?code=8703&country=CN - Search HS codes</li>
                    <li>/tariff/autocomplete?query=car&country=CN - Autocomplete</li>
                    <li>/tariff/calculate - Calculate tariff</li>
                    <li>/tariff/fta-check - Check FTA eligibility</li>
                    <li>/tariff/exchange-rate - Get exchange rates</li>
                </ul>
            </div>
        </div>
        
        <script>
            const API_URL = window.location.origin + '/api/v1';
            let debounceTimer;
            let selectedHsCode = '';
            
            function handleSearch(query) {
                clearTimeout(debounceTimer);
                if (query.length < 2) {
                    hideSuggestions();
                    return;
                }
                debounceTimer = setTimeout(() => fetchSuggestions(query), 300);
            }
            
            async function fetchSuggestions(query) {
                const country = document.getElementById('country').value;
                try {
                    const response = await fetch(`${API_URL}/tariff/autocomplete?query=${encodeURIComponent(query)}&country=${country}`);
                    const data = await response.json();
                    displaySuggestions(data);
                } catch (error) {
                    console.error('Search error:', error);
                }
            }
            
            function displaySuggestions(items) {
                const container = document.getElementById('suggestions');
                if (!items || items.length === 0) {
                    hideSuggestions();
                    return;
                }
                
                container.innerHTML = items.map(item => `
                    <div class="suggestion-item" onclick="selectItem('${item.code}', '${item.description.replace(/'/g, "\\'")}')">
                        <div class="suggestion-code">${item.code}</div>
                        <div class="suggestion-desc">${item.description}</div>
                        <div class="suggestion-rate">Duty: ${item.mfn_rate}%</div>
                    </div>
                `).join('');
                container.style.display = 'block';
            }
            
            function selectItem(code, description) {
                selectedHsCode = code;
                document.getElementById('hs-code').value = code;
                document.getElementById('search-input').value = description;
                hideSuggestions();
            }
            
            function hideSuggestions() {
                document.getElementById('suggestions').style.display = 'none';
            }
            
            function hideSuggestionsDelayed() {
                setTimeout(hideSuggestions, 200);
            }
            
            function clearSelection() {
                selectedHsCode = '';
                document.getElementById('hs-code').value = '';
                document.getElementById('search-input').value = '';
                hideSuggestions();
            }
            
            async function calculate() {
                const hsCode = selectedHsCode || document.getElementById('search-input').value;
                const country = document.getElementById('country').value;
                const value = document.getElementById('value').value;
                const currency = document.getElementById('currency').value;
                
                if (!hsCode || !value) {
                    showError('Please enter HS code and value');
                    return;
                }
                
                document.getElementById('calc-btn').disabled = true;
                document.getElementById('loading').style.display = 'block';
                document.getElementById('error').innerHTML = '';
                document.getElementById('results').classList.remove('show');
                
                try {
                    // Calculate with currency
                    const calcResponse = await fetch(
                        `${API_URL}/tariff/calculate-with-currency?hs_code=${hsCode}&country=${country}&value=${value}&from_currency=USD&to_currency=${currency}`
                    );
                    
                    if (!calcResponse.ok) {
                        const err = await calcResponse.json();
                        throw new Error(err.detail || 'Calculation failed');
                    }
                    
                    const calcData = await calcResponse.json();
                    
                    // Check FTA
                    const origin = prompt('Enter origin country code for FTA check (e.g., JP, US, DE):', 'US');
                    let ftaData = null;
                    if (origin) {
                        const ftaResponse = await fetch(
                            `${API_URL}/tariff/fta-check?hs_code=${hsCode}&origin_country=${origin}&dest_country=${country}`
                        );
                        ftaData = await ftaResponse.json();
                    }
                    
                    displayResults(calcData, ftaData, currency);
                    
                } catch (error) {
                    showError(error.message);
                }
                
                document.getElementById('calc-btn').disabled = false;
                document.getElementById('loading').style.display = 'none';
            }
            
            function displayResults(calc, fta, currency) {
                const resultsDiv = document.getElementById('results');
                const conv = calc.converted_calculation;
                
                const symbols = {
                    USD: '$', CNY: 'CN¥', EUR: '€', 
                    JPY: 'JP¥', GBP: '£', KRW: '₩'
                };
                const symbol = symbols[currency] || '$';
                
                let ftaHtml = '';
                if (fta) {
                    if (fta.eligible) {
                        ftaHtml = `
                            <div class="fta-box">
                                <div class="fta-title fta-eligible">✅ FTA Eligible: ${fta.fta_name}</div>
                                <p>Standard rate: <span style="text-decoration: line-through;">${fta.standard_rate}%</span></p>
                                <p>Preferential rate: <strong>${fta.preferential_rate}%</strong></p>
                                <p style="font-size: 1.2em; color: #22543d; margin-top: 10px;">
                                    <strong>You save: ${fta.savings_percent}%</strong>
                                </p>
                                <p style="margin-top: 10px; font-size: 0.9em;">
                                    Required: ${fta.requirements.join(', ')}
                                </p>
                            </div>
                        `;
                    } else {
                        ftaHtml = `
                            <div class="fta-box not-eligible">
                                <div class="fta-title fta-not-eligible">❌ No FTA Available</div>
                                <p>Route: ${fta.origin_country} → ${fta.destination_country}</p>
                                <p>Standard rate applies: ${fta.standard_rate}%</p>
                            </div>
                        `;
                    }
                }
                
                resultsDiv.innerHTML = `
                    <h3 style="margin-bottom: 15px; color: #333;">${calc.description}</h3>
                    <p style="color: #666; margin-bottom: 15px;">
                        HS: ${calc.hs_code} | Country: ${calc.country}
                        ${calc.exchange_rate !== 1 ? `<br>Rate: 1 USD = ${calc.exchange_rate} ${currency}` : ''}
                    </p>
                    
                    <div class="result-row">
                        <span>CIF Value:</span>
                        <span>${symbol}${conv.cif_value.toLocaleString()}</span>
                    </div>
                    <div class="result-row">
                        <span>Customs Duty (${calc.rates.mfn}%):</span>
                        <span>${symbol}${conv.customs_duty.toLocaleString()}</span>
                    </div>
                    <div class="result-row">
                        <span>VAT (${calc.rates.vat}%):</span>
                        <span>${symbol}${conv.vat.toLocaleString()}</span>
                    </div>
                    ${conv.consumption_tax > 0 ? `
                    <div class="result-row">
                        <span>Consumption Tax (${calc.rates.consumption}%):</span>
                        <span>${symbol}${conv.consumption_tax.toLocaleString()}</span>
                    </div>
                    ` : ''}
                    <div class="result-row">
                        <span>Total Landed Cost:</span>
                        <span>${symbol}${conv.total_cost.toLocaleString()}</span>
                    </div>
                    
                    ${ftaHtml}
                `;
                
                resultsDiv.classList.add('show');
            }
            
            function showError(message) {
                document.getElementById('error').innerHTML = `<div class="error">Error: ${message}</div>`;
            }
        </script>
    </body>
    </html>
    """

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "ip": "192.168.0.115"}