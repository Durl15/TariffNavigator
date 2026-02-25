from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api.v1.api import api_router
from app.core.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tariff Navigator", version="1.0.0")

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f">>> REQUEST: {request.method} {request.url.path}")
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"<<< RESPONSE: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}s")
        return response
    except Exception as e:
        logger.error(f"!!! EXCEPTION in {request.url.path}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise

# CORS configuration - reads from CORS_ORIGINS environment variable
# In production, set: CORS_ORIGINS=https://yourfrontend.com,https://anotherdomain.com
# The Settings class automatically parses comma-separated values into a list
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Add rate limiting middleware (AFTER CORS, BEFORE routes)
app.add_middleware(RateLimitMiddleware)

app.include_router(api_router, prefix="/api/v1")


# ============================================================================
# APPLICATION LIFECYCLE EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    from app.services.scheduler import start_scheduler
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Starting TariffNavigator application...")

    # Start background scheduler
    start_scheduler()

    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on application shutdown."""
    from app.services.scheduler import shutdown_scheduler
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Shutting down TariffNavigator application...")

    # Shutdown background scheduler
    shutdown_scheduler()

    logger.info("Application shutdown complete")


# PRICING PAGE
@app.get("/pricing", response_class=HTMLResponse)
async def pricing():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pricing - Tariff Navigator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
            h1 { color: #667eea; text-align: center; }
            .plan { background: white; padding: 30px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .plan h2 { color: #333; }
            .price { font-size: 2.5em; color: #667eea; font-weight: bold; }
            .features { list-style: none; padding: 0; }
            .features li { padding: 10px 0; border-bottom: 1px solid #eee; }
            .features li:before { content: "✓ "; color: #48bb78; font-weight: bold; }
            .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 15px; }
            .featured { border: 3px solid #667eea; }
            .nav { text-align: center; margin-bottom: 30px; }
            .nav a { margin: 0 15px; color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/app">Calculator</a>
            <a href="/pricing">Pricing</a>
            <a href="/api/v1/health">API</a>
        </div>
        
        <h1>💰 Pricing Plans</h1>
        
        <div class="plan">
            <h2>Free</h2>
            <div class="price">$0<span style="font-size:0.4em;color:#666;">/month</span></div>
            <ul class="features">
                <li>100 calculations/month</li>
                <li>China & EU tariffs</li>
                <li>Basic currency conversion</li>
                <li>Email support</li>
            </ul>
            <a href="/app" class="button">Get Started</a>
        </div>
        
        <div class="plan featured">
            <h2>Professional ⭐</h2>
            <div class="price">$29<span style="font-size:0.4em;color:#666;">/month</span></div>
            <ul class="features">
                <li>10,000 calculations/month</li>
                <li>All countries (50+)</li>
                <li>FTA eligibility checking</li>
                <li>API access</li>
                <li>Real-time exchange rates</li>
                <li>Priority support</li>
            </ul>
            <a href="/app" class="button">Start Free Trial</a>
        </div>
        
        <div class="plan">
            <h2>Enterprise</h2>
            <div class="price">$299<span style="font-size:0.4em;color:#666;">/month</span></div>
            <ul class="features">
                <li>Unlimited calculations</li>
                <li>Custom HS code database</li>
                <li>White-label solution</li>
                <li>Dedicated account manager</li>
                <li>24/7 phone support</li>
            </ul>
            <a href="mailto:sales@tariffnavigator.com" class="button">Contact Sales</a>
        </div>
    </body>
    </html>
    """

# CALCULATOR APP
@app.get("/app", response_class=HTMLResponse)
async def app_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tariff Calculator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
            h1 { color: #667eea; }
            .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            label { display: block; margin: 15px 0 5px; font-weight: bold; }
            input, select { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; }
            button { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 20px; }
            button:hover { background: #5a67d8; }
            .result { background: #f0fff4; border: 2px solid #9ae6b4; padding: 20px; margin-top: 20px; border-radius: 5px; display: none; }
            .nav { text-align: center; margin-bottom: 30px; }
            .nav a { margin: 0 15px; color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/app">Calculator</a>
            <a href="/pricing">Pricing</a>
            <a href="/api/v1/health">API</a>
        </div>
        
        <div class="card">
            <h1>🚢 Tariff Calculator</h1>
            
            <label>Destination Country</label>
            <select id="country">
                <option value="CN">China (CN)</option>
                <option value="EU">European Union (EU)</option>
            </select>
            
            <label>Currency</label>
            <select id="currency">
                <option value="USD">USD ($)</option>
                <option value="CNY">CNY (¥)</option>
                <option value="EUR">EUR (€)</option>
            </select>
            
            <label>HS Code</label>
            <input type="text" id="hsCode" placeholder="8703230010" value="8703230010">
            
            <label>CIF Value (USD)</label>
            <input type="number" id="value" placeholder="50000" value="50000">
            
            <button onclick="calculate()">Calculate Tariff</button>
            
            <div id="result" class="result"></div>
        </div>
        
        <script>
            async function calculate() {
                const country = document.getElementById('country').value;
                const currency = document.getElementById('currency').value;
                const hsCode = document.getElementById('hsCode').value;
                const value = document.getElementById('value').value;
                
                try {
                    const response = await fetch(`/api/v1/tariff/calculate-with-currency?hs_code=${hsCode}&country=${country}&value=${value}&from_currency=USD&to_currency=${currency}`);
                    const data = await response.json();
                    
                    const symbol = currency === 'CNY' ? '¥' : currency === 'EUR' ? '€' : '$';
                    const total = data.converted_calculation.total_cost;
                    
                    document.getElementById('result').innerHTML = `
                        <h3>${data.description}</h3>
                        <p><strong>Total Cost: ${symbol}${total.toLocaleString()}</strong></p>
                        <p>Duty: ${data.rates.mfn}% | VAT: ${data.rates.vat}%</p>
                    `;
                    document.getElementById('result').style.display = 'block';
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """

# LANDING PAGE
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tariff Navigator - Smart Import Duty Calculator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
            .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 20px; text-align: center; }
            .hero h1 { font-size: 3em; margin-bottom: 20px; }
            .hero p { font-size: 1.3em; margin-bottom: 30px; }
            .button { display: inline-block; background: #48bb78; color: white; padding: 15px 40px; text-decoration: none; border-radius: 30px; font-size: 1.2em; margin: 10px; }
            .features { max-width: 1000px; margin: 50px auto; padding: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; }
            .feature { background: white; padding: 30px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .feature h3 { color: #667eea; }
            .cta { background: #667eea; color: white; padding: 80px 20px; text-align: center; }
            .cta h2 { font-size: 2.5em; margin-bottom: 20px; }
            .nav { text-align: center; padding: 20px; background: white; }
            .nav a { margin: 0 20px; color: #667eea; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/app">Calculator</a>
            <a href="/pricing">Pricing</a>
            <a href="/api/v1/health">API</a>
        </div>
        
        <div class="hero">
            <h1>🚢 Tariff Navigator</h1>
            <p>Calculate import duties in seconds. Save up to 15% with FTA detection.</p>
            <a href="/app" class="button">Try Free Calculator</a>
            <a href="/pricing" class="button" style="background: transparent; border: 2px solid white;">View Pricing</a>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>🧮 Accurate Calculations</h3>
                <p>Customs duties, VAT, and consumption taxes for 50+ countries.</p>
            </div>
            <div class="feature">
                <h3>💱 Multi-Currency</h3>
                <p>Real-time conversion to USD, CNY, EUR, JPY, GBP, KRW.</p>
            </div>
            <div class="feature">
                <h3>✅ FTA Checking</h3>
                <p>Automatically detect Free Trade Agreement savings.</p>
            </div>
            <div class="feature">
                <h3>⚡ Fast API</h3>
                <p>Sub-second response times. Easy integration.</p>
            </div>
        </div>
        
        <div class="cta">
            <h2>Start Saving Today</h2>
            <p>Free for up to 100 calculations per month.</p>
            <a href="/app" class="button" style="background: #48bb78;">Get Started Free</a>
        </div>
    </body>
    </html>
    """

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "ip": "10.153.69.163", "version": "1.0.0"}