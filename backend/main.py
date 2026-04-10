from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api.v1.api import api_router
from app.core.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.license import LicenseMiddleware
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tariff Navigator", version="1.0.0")

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://(.*\.vercel\.app|.*\.onrender\.com|.*\.netlify\.app)",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(LicenseMiddleware)

app.include_router(api_router, prefix="/api/v1")


async def _seed_demo_user():
    import uuid, json, logging
    from passlib.context import CryptContext
    from sqlalchemy import text
    from app.db.session import async_session
    from datetime import datetime, timedelta
    _log = logging.getLogger(__name__)
    try:
        async with async_session() as db:
            result = await db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": "demo@tariffnavigator.com"}
            )
            existing = result.scalar_one_or_none()
            if existing:
                user_id = existing
            else:
                user_id = str(uuid.uuid4())
                pwd = CryptContext(schemes=["bcrypt"], deprecated="auto").hash("demo1234")
                await db.execute(
                    text("""INSERT INTO users (id, email, hashed_password, full_name, role, is_active, is_email_verified)
                            VALUES (:id, :email, :pw, :name, :role, :active, :verified)"""),
                    {"id": user_id, "email": "demo@tariffnavigator.com",
                     "pw": pwd, "name": "Demo User", "role": "pro", "active": True, "verified": True}
                )
                _log.info("Demo user created: demo@tariffnavigator.com")

            wl_check = await db.execute(
                text("SELECT COUNT(*) FROM watchlists WHERE user_id = :uid"), {"uid": user_id}
            )
            if wl_check.scalar() == 0:
                watchlists = [
                    {"id": str(uuid.uuid4()), "name": "China Electronics",
                     "description": "High-exposure consumer electronics from China",
                     "hs_codes": json.dumps(["8471.30", "8517.12", "8528.72"]),
                     "countries": json.dumps(["CN"]),
                     "alert_preferences": json.dumps({"email": True, "digest": "daily"})},
                    {"id": str(uuid.uuid4()), "name": "Steel & Aluminum (Sec. 232)",
                     "description": "Section 232 metals — tracking rate changes",
                     "hs_codes": json.dumps(["7208.10", "7606.11", "7601.10"]),
                     "countries": json.dumps(["CN", "MX", "CA", "DE"]),
                     "alert_preferences": json.dumps({"email": True, "digest": "weekly"})},
                    {"id": str(uuid.uuid4()), "name": "Apparel — Vietnam",
                     "description": "Monitoring IEEPA impact on Vietnam sourcing",
                     "hs_codes": json.dumps(["6109.10", "6203.42", "6204.62"]),
                     "countries": json.dumps(["VN"]),
                     "alert_preferences": json.dumps({"email": False, "digest": "weekly"})},
                ]
                for wl in watchlists:
                    await db.execute(text("""
                        INSERT INTO watchlists (id, user_id, name, description, hs_codes, countries, alert_preferences, is_active, created_at)
                        VALUES (:id, :uid, :name, :desc, :hs, :co, :ap, true, :ts)
                    """), {"id": wl["id"], "uid": user_id, "name": wl["name"], "desc": wl["description"],
                           "hs": wl["hs_codes"], "co": wl["countries"], "ap": wl["alert_preferences"],
                           "ts": datetime.utcnow().isoformat()})
                _log.info("Demo watchlists seeded")

            cat_check = await db.execute(
                text("SELECT id FROM catalogs WHERE user_id = :uid LIMIT 1"), {"uid": user_id}
            )
            if not cat_check.scalar_one_or_none():
                cat_id = str(uuid.uuid4())
                await db.execute(text("""
                    INSERT INTO catalogs (id, user_id, name, description, currency, total_skus, created_at, uploaded_at)
                    VALUES (:id, :uid, :name, :desc, 'USD', 6, :ts, :ts)
                """), {"id": cat_id, "uid": user_id, "name": "Q1 2026 Product Catalog",
                       "desc": "Core import SKUs — tariff exposure analysis", "ts": datetime.utcnow().isoformat()})

                items = [
                    ("SKU-001", "Laptop Computer 15\"",    "8471.30", "CN", 420, 899,  2400, "Electronics", 12.5, 3528,   432.60, 38.8),
                    ("SKU-002", "Wireless Earbuds",        "8518.30", "CN", 28,  79,   8500, "Electronics", 0.09, 14076,  238.00, 37.6),
                    ("SKU-003", "Men's Cotton T-Shirt",    "6109.10", "VN", 6,   24,   12000,"Apparel",     0.18, 3888,   72.00,  65.2),
                    ("SKU-004", "Aluminum Sheet 1mm",      "7606.11", "CN", 180, 310,  900,  "Metals",      8.2,  32400,  162.00, 45.1),
                    ("SKU-005", "USB-C Charging Cable 2m", "8544.42", "CN", 3.5, 14,   22000,"Electronics", 0.05, 9856,   77.00,  68.4),
                    ("SKU-006", "Running Shoes",           "6403.99", "VN", 22,  85,   5000, "Footwear",    0.85, 6600,   110.00, 60.2),
                ]
                for sku, name, hs, co, cogs, retail, vol, cat, wt, tariff_ann, tariff_unit, margin in items:
                    await db.execute(text("""
                        INSERT INTO catalog_items
                          (id, catalog_id, sku, product_name, hs_code, origin_country, cogs, retail_price,
                           annual_volume, category, weight_kg, annual_tariff_exposure, tariff_cost, margin_percent, created_at)
                        VALUES (:id, :cid, :sku, :name, :hs, :co, :cogs, :retail, :vol, :cat, :wt, :tann, :tunit, :margin, :ts)
                    """), {"id": str(uuid.uuid4()), "cid": cat_id, "sku": sku, "name": name, "hs": hs,
                           "co": co, "cogs": cogs, "retail": retail, "vol": vol, "cat": cat, "wt": wt,
                           "tann": tariff_ann, "tunit": tariff_unit, "margin": margin,
                           "ts": datetime.utcnow().isoformat()})
                _log.info("Demo catalog seeded with 6 SKUs")

            an_check = await db.execute(
                text("SELECT COUNT(*) FROM tool_analyses WHERE user_id = :uid"), {"uid": user_id}
            )
            if an_check.scalar() == 0:
                analyses = [
                    {
                        "tool_type": "sourcing",
                        "title": "Sourcing: Laptops (8471.30) — China vs Alternatives",
                        "form_data": {"hts_code": "8471.30", "current_country": "CN", "annual_import_value": 1008000},
                        "result_data": {
                            "current_rate": 145.0, "alternatives": [
                                {"country": "Vietnam", "rate": 46.0, "savings_pct": 68.3, "risk": "medium"},
                                {"country": "Mexico",  "rate": 0.0,  "savings_pct": 100.0,"risk": "low"},
                                {"country": "Taiwan",  "rate": 32.0, "savings_pct": 77.9, "risk": "low"},
                            ]
                        }
                    },
                    {
                        "tool_type": "hts_audit",
                        "title": "HTS Audit — Q1 2026 Product Line",
                        "form_data": {"products": ["Laptop", "Earbuds", "T-Shirt"]},
                        "result_data": {
                            "risk_score": 72, "flags": [
                                {"sku": "SKU-001", "issue": "Possible misclassification: 8471 vs 8473", "severity": "medium"},
                                {"sku": "SKU-004", "issue": "Section 232 — verify country-of-melt origin", "severity": "high"},
                            ]
                        }
                    },
                    {
                        "tool_type": "scenario",
                        "title": "Scenario: China rates revert to 145%",
                        "form_data": {"scenario": "china_145", "catalog_id": "demo"},
                        "result_data": {
                            "total_annual_impact": 86400, "affected_skus": 4,
                            "worst_sku": "SKU-001", "recommendation": "Accelerate Vietnam qualification for SKU-001 and SKU-002"
                        }
                    },
                ]
                for i, a in enumerate(analyses):
                    ts = (datetime.utcnow() - timedelta(days=i * 3)).isoformat()
                    await db.execute(text("""
                        INSERT INTO tool_analyses (id, user_id, tool_type, title, form_data, result_data, created_at)
                        VALUES (:id, :uid, :type, :title, :fd, :rd, :ts)
                    """), {"id": str(uuid.uuid4()), "uid": user_id, "type": a["tool_type"],
                           "title": a["title"], "fd": json.dumps(a["form_data"]),
                           "rd": json.dumps(a["result_data"]), "ts": ts})
                _log.info("Demo analyses seeded")

            await db.commit()
    except Exception as e:
        _log.warning("Could not seed demo user/data: %s", e)


@app.on_event("startup")
async def startup_event():
    import subprocess
    import asyncio
    from app.services.scheduler import start_scheduler
    from app.services.hts_live import warm_cache

    logger.info("Starting TariffNavigator application...")

    # Run migrations
    try:
        result = subprocess.run(
            ["python", "-m", "alembic", "upgrade", "head"],
            capture_output=True, text=True
        )
        logger.info(f"Migrations: {result.stdout}")
        if result.returncode != 0:
            logger.error(f"Migration error: {result.stderr}")
    except Exception as e:
        logger.error(f"Migration failed: {e}")

   
    # Start scheduler and background tasks
    start_scheduler()
    asyncio.create_task(warm_cache())
    asyncio.create_task(_seed_demo_user())

    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    from app.services.scheduler import shutdown_scheduler
    logger.info("Shutting down TariffNavigator application...")
    shutdown_scheduler()
    logger.info("Application shutdown complete")


@app.get("/pricing", response_class=HTMLResponse)
async def pricing():
    return """<!DOCTYPE html><html><head><title>Pricing - Tariff Navigator</title>
    <style>body{font-family:Arial,sans-serif;margin:0;padding:0;background:#f5f5f5}.nav{text-align:center;padding:20px;background:white}.nav a{margin:0 20px;color:#667eea;text-decoration:none;font-weight:bold}.hero{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:60px 20px;text-align:center}.hero h1{font-size:2.5em;margin-bottom:10px}.hero p{font-size:1.2em;opacity:.9}.plans{max-width:1000px;margin:50px auto;padding:20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:30px}.plan{background:white;padding:35px;border-radius:12px;box-shadow:0 2px 15px rgba(0,0,0,.08);position:relative}.plan.featured{border:3px solid #667eea}.badge{position:absolute;top:-14px;left:50%;transform:translateX(-50%);background:#667eea;color:white;padding:4px 20px;border-radius:20px;font-size:13px;font-weight:bold;white-space:nowrap}.plan h2{color:#333;font-size:1.4em;margin-bottom:5px}.plan .sub{color:#888;font-size:13px;margin-bottom:20px}.price{font-size:2.8em;color:#667eea;font-weight:bold;margin:15px 0 5px}.price span{font-size:.35em;color:#888;font-weight:normal}.annual{font-size:13px;color:#48bb78;margin-bottom:20px}.features{list-style:none;padding:0;margin:20px 0}.features li{padding:9px 0;border-bottom:1px solid #f0f0f0;font-size:14px;color:#444}.features li:before{content:"✓ ";color:#48bb78;font-weight:bold}.button{display:block;text-align:center;background:#667eea;color:white;padding:14px;text-decoration:none;border-radius:8px;margin-top:25px;font-weight:bold;font-size:15px}.button:hover{background:#5a67d8}.button.outline{background:transparent;border:2px solid #667eea;color:#667eea}.footer{text-align:center;padding:40px 20px;color:#888;font-size:14px}.footer a{color:#667eea}</style></head>
    <body>
    <div class="nav"><a href="/">Home</a><a href="/app">Calculator</a><a href="/pricing">Pricing</a></div>
    <div class="hero"><h1>Simple, Transparent Pricing</h1><p>Save thousands on import duties. Pay a fraction of that to know how.</p></div>
    <div class="plans">
      <div class="plan">
        <h2>Starter</h2>
        <div class="sub">For small importers and trade consultants</div>
        <div class="price">$97<span>/month</span></div>
        <div class="annual">Or $970/year — save 2 months</div>
        <ul class="features">
          <li>Tariff lookup — 50+ countries</li>
          <li>HTS code search</li>
          <li>Basic FTA eligibility check</li>
          <li>100 calculations/month</li>
          <li>Email support</li>
        </ul>
        <a href="mailto:don@djaibc.com?subject=TariffNavigator Starter" class="button outline">Get Started</a>
      </div>
      <div class="plan featured">
        <div class="badge">Most Popular</div>
        <h2>Professional</h2>
        <div class="sub">For procurement managers and freight brokers</div>
        <div class="price">$297<span>/month</span></div>
        <div class="annual">Or $2,970/year — save 2 months</div>
        <ul class="features">
          <li>Everything in Starter</li>
          <li>Full catalog upload and analysis</li>
          <li>Watchlists and tariff alerts</li>
          <li>Scenario modeling</li>
          <li>Sourcing alternative finder</li>
          <li>API access</li>
          <li>Unlimited calculations</li>
          <li>Priority support</li>
        </ul>
        <a href="mailto:don@djaibc.com?subject=TariffNavigator Professional" class="button">Start Free Trial</a>
      </div>
      <div class="plan">
        <h2>Enterprise</h2>
        <div class="sub">For manufacturers and compliance teams</div>
        <div class="price">$797<span>/month</span></div>
        <div class="annual">Or $7,970/year — save 2 months</div>
        <ul class="features">
          <li>Everything in Professional</li>
          <li>White-label option</li>
          <li>Custom HS code database</li>
          <li>Unlimited users</li>
          <li>Dedicated account manager</li>
          <li>24/7 phone support</li>
          <li>SLA guarantee</li>
        </ul>
        <a href="mailto:don@djaibc.com?subject=TariffNavigator Enterprise" class="button outline">Contact Sales</a>
      </div>
    </div>
    <div class="footer">Questions? Email <a href="mailto:don@djaibc.com">don@djaibc.com</a> or call us in Syracuse, NY.<br><br>All plans include a 14-day free trial. No credit card required.</div>
    </body></html>"""

@app.get("/app", response_class=HTMLResponse)
async def app_page():
    return """<!DOCTYPE html><html><head><title>Tariff Calculator</title>
    <style>body{font-family:Arial,sans-serif;max-width:600px;margin:50px auto;padding:20px;background:#f5f5f5}h1{color:#667eea}.card{background:white;padding:30px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,.1)}label{display:block;margin:15px 0 5px;font-weight:bold}input,select{width:100%;padding:12px;border:2px solid #ddd;border-radius:5px;font-size:16px}button{background:#667eea;color:white;padding:15px 30px;border:none;border-radius:5px;font-size:16px;cursor:pointer;width:100%;margin-top:20px}.result{background:#f0fff4;border:2px solid #9ae6b4;padding:20px;margin-top:20px;border-radius:5px;display:none}.nav{text-align:center;margin-bottom:30px}.nav a{margin:0 15px;color:#667eea;text-decoration:none}</style></head>
    <body><div class="nav"><a href="/">Home</a><a href="/app">Calculator</a><a href="/pricing">Pricing</a></div>
    <div class="card"><h1>Tariff Calculator</h1>
    <label>Destination Country</label><select id="country"><option value="CN">China (CN)</option><option value="EU">European Union (EU)</option></select>
    <label>Currency</label><select id="currency"><option value="USD">USD ($)</option><option value="CNY">CNY (¥)</option><option value="EUR">EUR (€)</option></select>
    <label>HS Code</label><input type="text" id="hsCode" value="8703230010">
    <label>CIF Value (USD)</label><input type="number" id="value" value="50000">
    <button onclick="calculate()">Calculate Tariff</button>
    <div id="result" class="result"></div></div>
    <script>async function calculate(){const country=document.getElementById('country').value,currency=document.getElementById('currency').value,hsCode=document.getElementById('hsCode').value,value=document.getElementById('value').value;try{const r=await fetch(`/api/v1/tariff/calculate-with-currency?hs_code=${hsCode}&country=${country}&value=${value}&from_currency=USD&to_currency=${currency}`),data=await r.json(),symbol=currency==='CNY'?'¥':currency==='EUR'?'€':'$';document.getElementById('result').innerHTML=`<h3>${data.description}</h3><p><strong>Total Cost: ${symbol}${data.converted_calculation.total_cost.toLocaleString()}</strong></p><p>Duty: ${data.rates.mfn}% | VAT: ${data.rates.vat}%</p>`;document.getElementById('result').style.display='block'}catch(e){alert('Error: '+e.message)}}</script>
    </body></html>"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return """<!DOCTYPE html><html><head><title>Tariff Navigator</title>
    <style>body{font-family:Arial,sans-serif;margin:0;padding:0;background:#f5f5f5}.hero{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:100px 20px;text-align:center}.hero h1{font-size:3em;margin-bottom:20px}.hero p{font-size:1.3em;margin-bottom:30px}.button{display:inline-block;background:#48bb78;color:white;padding:15px 40px;text-decoration:none;border-radius:30px;font-size:1.2em;margin:10px}.features{max-width:1000px;margin:50px auto;padding:20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:30px}.feature{background:white;padding:30px;border-radius:10px;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,.1)}.feature h3{color:#667eea}.cta{background:#667eea;color:white;padding:80px 20px;text-align:center}.cta h2{font-size:2.5em;margin-bottom:20px}.nav{text-align:center;padding:20px;background:white}.nav a{margin:0 20px;color:#667eea;text-decoration:none;font-weight:bold}</style></head>
    <body><div class="nav"><a href="/">Home</a><a href="/app">Calculator</a><a href="/pricing">Pricing</a></div>
    <div class="hero"><h1>Tariff Navigator</h1><p>Calculate import duties in seconds. Save up to 15% with FTA detection.</p><a href="/app" class="button">Try Free Calculator</a><a href="/pricing" class="button" style="background:transparent;border:2px solid white">View Pricing</a></div>
    <div class="features"><div class="feature"><h3>Accurate Calculations</h3><p>Customs duties, VAT, and consumption taxes for 50+ countries.</p></div><div class="feature"><h3>Multi-Currency</h3><p>Real-time conversion to USD, CNY, EUR, JPY, GBP, KRW.</p></div><div class="feature"><h3>FTA Checking</h3><p>Automatically detect Free Trade Agreement savings.</p></div><div class="feature"><h3>Fast API</h3><p>Sub-second response times. Easy integration.</p></div></div>
    <div class="cta"><h2>Start Saving Today</h2><p>Free for up to 100 calculations per month.</p><a href="/app" class="button" style="background:#48bb78">Get Started Free</a></div>
    </body></html>"""


@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
