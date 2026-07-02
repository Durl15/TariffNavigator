# TariffNavigator — Claude Code Build Prompts
# Copy and paste these into Claude Code one phase at a time.
# Start with STEP 1, verify it works, then move to STEP 2, etc.
# Your CLAUDE.md file has the full spec — Claude Code will read it automatically.

================================================================
STEP 1: PROJECT SETUP & SCAFFOLDING
================================================================

Read CLAUDE.md thoroughly. This is our complete build specification.

Now set up the project structure for Phase 1. Do the following:

1. Assess what already exists in this project — list every file and folder
2. Preserve any existing working code — do NOT delete anything functional
3. Create this project structure (skip folders/files that already exist and work):

```
assets/
  logo_withtitle1.avif   — Phoenix logo (should already be here)
  logo.png               — Convert from avif if not present
backend/
  app/
    __init__.py
    main.py              — FastAPI app with CORS, logging, error middleware
    config.py            — Settings from .env using pydantic-settings
    database.py          — Async SQLAlchemy engine, session, Base
    dependencies.py      — Common dependencies (get_db, get_current_user)
    models/
      __init__.py
      user.py            — User, Organization models
      tariff.py          — HtsCode, TariffProgram, Country models
      watchlist.py       — Watchlist model
      catalog.py         — ProductCatalog, CatalogItem models
      scenario.py        — SavedScenario model
      lookup.py          — TariffLookup model
      alert.py           — Alert model
      audit.py           — AuditLog model
    schemas/
      __init__.py
      auth.py            — Register, Login, Token request/response schemas
      tariff.py          — Lookup request/response, HTS schemas
      user.py            — User response schemas
    routes/
      __init__.py
      auth.py            — /api/auth/* endpoints
      tariff.py          — /api/tariff/* endpoints
      health.py          — /api/health endpoint
    services/
      __init__.py
      tariff_engine.py   — Core stacking calculation logic
      ai_classifier.py   — Claude API integration for HTS classification
      auth_service.py    — JWT creation, password hashing
  alembic/
    env.py
    versions/
  alembic.ini
  requirements.txt       — All dependencies pinned
  .env                   — Environment variables (create template)
  .gitignore
frontend/                — Empty for now, Phase 2
docker/                  — Empty for now, Phase 4
docs/                    — Empty for now
README.md
```

4. Create .env with these variables (use placeholder values):
   - DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/tariffnav
   - ANTHROPIC_API_KEY=sk-ant-your-key-here
   - JWT_SECRET_KEY=generate-a-random-secret
   - JWT_ALGORITHM=HS256
   - JWT_EXPIRY_MINUTES=30
   - REDIS_URL=redis://localhost:6379
   - LOG_LEVEL=INFO
   - CORS_ORIGINS=http://localhost:3000

5. Create .gitignore covering: .env, __pycache__, *.pyc, .venv, node_modules, .next, *.db

6. Create requirements.txt with:
   fastapi, uvicorn[standard], sqlalchemy[asyncio], asyncpg, alembic,
   pydantic, pydantic-settings, python-jose[cryptography], passlib[bcrypt],
   anthropic, redis, celery, python-multipart, httpx, pytest, pytest-asyncio

7. Wire up main.py with:
   - CORS middleware using CORS_ORIGINS from config
   - Request logging middleware
   - Global exception handler returning proper JSON errors
   - Include all route routers
   - Startup/shutdown events for database

8. Set up Alembic config pointing to our async database

After creating everything, show me the complete project tree and verify the app starts with: uvicorn app.main:app --reload


================================================================
STEP 2: DATABASE MODELS & MIGRATION
================================================================

Now build all the database models from the schema in CLAUDE.md.

1. Create every model listed in the Database Schema section:
   - users table with UUID primary keys
   - organizations table
   - hts_codes table with proper indexing on code field
   - tariff_programs table
   - countries table
   - watchlists table
   - product_catalogs and catalog_items tables
   - saved_scenarios table
   - tariff_lookups table
   - alerts table
   - audit_log table

2. Use these patterns:
   - UUID primary keys (import uuid, use uuid4)
   - server_default for created_at timestamps
   - onupdate for updated_at timestamps
   - JSON columns for flexible data (use SQLAlchemy JSON type)
   - Proper foreign key relationships with back_populates
   - Indexes on frequently queried columns (email, hts_code, user_id, created_at)

3. Generate and run the initial Alembic migration

4. Verify by connecting to the database and confirming all tables exist

Show me the migration file and confirm all tables were created successfully.


================================================================
STEP 3: AUTH SYSTEM
================================================================

Build the authentication system:

1. auth_service.py:
   - Password hashing with passlib/bcrypt
   - JWT token creation (access + refresh tokens)
   - Token verification and user extraction
   - Token refresh logic

2. Auth schemas (schemas/auth.py):
   - RegisterRequest (email, password, name, company_name)
   - LoginRequest (email, password)
   - TokenResponse (access_token, refresh_token, token_type, expires_in)
   - UserResponse (id, email, name, company_name, role, subscription_tier)

3. Auth routes (routes/auth.py):
   - POST /api/auth/register — create user, return tokens
   - POST /api/auth/login — verify credentials, return tokens
   - POST /api/auth/refresh — refresh access token
   - GET /api/auth/me — get current user profile

4. Dependencies (dependencies.py):
   - get_db — async database session
   - get_current_user — extract user from JWT in Authorization header
   - require_role(role) — role-based access decorator

5. Test all endpoints manually:
   - Register a test user
   - Login and get tokens
   - Use token to hit /api/auth/me
   - Verify invalid tokens are rejected

Show me curl commands to test each endpoint and confirm they all work.


================================================================
STEP 4: TARIFF ENGINE — THE CORE ALGORITHM
================================================================

Build the tariff stacking calculation engine. This is the heart of the product.

1. tariff_engine.py — TariffCalculator class:

   async def calculate_total_duty(hts_code: str, country_code: str) -> TariffResult:
     """
     Calculate the total stacked tariff rate for a product.
     
     Logic:
     a) Look up base HTS rate (general duty rate from hts_codes table)
     b) Check Section 232 — does this HTS code fall under steel/aluminum/auto tariffs?
     c) Check Section 301 — is this country (primarily China) subject to 301 tariffs for this code?
     d) Check IEEPA — what is the reciprocal/emergency rate for this country?
     e) Check AD/CVD — any antidumping or countervailing duties?
     f) Check trade agreements — does USMCA or another FTA provide exemption or reduced rate?
     g) Stack the rates:
        - Base rate applies first
        - 232 replaces base rate for covered products (not additive)
        - 301 is additive on top of base or 232
        - IEEPA is additive (the reciprocal tariff)
        - AD/CVD is additive
        - FTA exemptions may zero out base rate but NOT 232/301/IEEPA
     h) Return total effective rate + breakdown of each layer
     """

   The TariffResult should include:
   - hts_code, country, product_description
   - base_rate, section_232_rate, section_301_rate, ieepa_rate, ad_cvd_rate
   - fta_exemption (which agreement, what it exempts)
   - total_effective_rate (the final stacked number)
   - breakdown (list of each layer with rate and explanation)
   - confidence_score (if AI classification was used)
   - calculated_at timestamp

2. Seed data — create a seed script that populates:
   - At least 50 common HTS codes across steel, aluminum, electronics, textiles, automotive, medical devices, construction materials
   - Current Section 232 tariff rates (25% on steel, 25% on aluminum)
   - Current Section 301 tariff rates for China (varies by list: 7.5% to 100%)
   - Current IEEPA reciprocal rates by country (10% baseline, 30% China, etc.)
   - Key countries with their trade agreement status
   - USMCA coverage for Canada and Mexico

3. ai_classifier.py — Claude integration:
   
   async def classify_product(description: str) -> ClassificationResult:
     """
     Send product description to Claude API.
     System prompt constrains Claude to ONLY return:
     - Suggested HTS code
     - Confidence score (0-1)
     - Reasoning
     - Alternative codes if uncertain
     Claude should NOT make up tariff rates — only classify the code.
     """

4. Build the API endpoints (routes/tariff.py):
   - POST /api/tariff/lookup — accepts {product_description?, hts_code?, country_code}
   - GET /api/tariff/hts/{code} — return HTS code details
   - POST /api/tariff/classify — just the AI classification step
   - GET /api/tariff/programs — list all active tariff programs

5. Test the engine:
   - "Steel rebar from China" should return 25% (232) + some 301 rate + 30% IEEPA
   - "Laptop from Taiwan" should return different rates
   - "Auto parts from Canada" should show USMCA exemption analysis
   - "Medical devices from Germany" should show 10% IEEPA baseline

Run these test cases and show me the results. Fix any calculation errors.


================================================================
STEP 5: HEALTH CHECK & VERIFICATION
================================================================

1. Build GET /api/health that returns:
   - status: "healthy"
   - database: connected/disconnected
   - timestamp
   - version: "1.0.0"
   - tariff_data: {hts_codes_count, programs_count, countries_count}

2. Run the full application and verify:
   - App starts cleanly with no errors
   - Health check returns all green
   - Can register a user
   - Can login and get JWT
   - Can perform a tariff lookup with auth
   - Can use AI classification
   - Tariff stacking returns correct rates
   - All errors return proper JSON with status codes

3. Show me:
   - The complete project tree
   - A summary of everything built
   - Any issues or concerns
   - What needs to happen next for Phase 2

Create a PROGRESS.md file tracking what's been completed and what's remaining.


================================================================
PHASE 2 KICKOFF (use after Phase 1 is verified working)
================================================================

Read CLAUDE.md and PROGRESS.md. Phase 1 is complete. Begin Phase 2 — Web GUI.

Follow the Phase 2 tasks exactly as specified in CLAUDE.md. Start by:

1. Initialize Next.js 14 project in the frontend/ directory
2. Install and configure Tailwind CSS and Shadcn/UI
3. Set up the app layout with sidebar navigation featuring the phoenix logo from assets/logo.png
4. Build the login and register pages connected to our auth API
5. Build the main dashboard with tariff search as the hero feature

Branding requirements from CLAUDE.md:
- Phoenix logo in sidebar top-left and login page
- Tagline: "Transforming Business, Rising Above the Challenges"
- Primary: #1E3A5F (navy), Accent: #4A90D9 (blue), Secondary: #0D9488 (teal)
- Footer: "DJ AI Business Consultant • Syracuse, NY"

Make it look professional. This is a client-facing enterprise product, not a prototype. Every page should look like it belongs in a $199/month SaaS tool.

After each page is built, show me a screenshot or describe the layout so I can verify before moving to the next page.
