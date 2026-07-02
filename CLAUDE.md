# CLAUDE.md — TariffNavigator Build Specification

## Project Identity
**TariffNavigator** — AI-Powered Tariff Intelligence for American Businesses
**Company:** DJ AI Business Consultant (Syracuse, NY)
**Tagline:** Transforming Business, Rising Above the Challenges
**Logo:** Phoenix design — file at assets/logo_withtitle1.avif (also logo.png)
**Mission:** Help small businesses survive and thrive in the tariff chaos era
**Product Type:** Enterprise SaaS — web-based platform with tiered subscriptions

---

## The Problem We Solve

U.S. tariff rates jumped from 2.4% to 18% in under 12 months. CBP collected $216B in FY2025 and issued 2,218 trade penalties. Small businesses have no affordable tools to calculate stacked tariff rates, track policy changes, model cost impacts, find alternative sourcing, or avoid compliance penalties. Enterprise tariff tools cost $500-2,000/month and require trade expertise. TariffNavigator starts free, speaks plain English, and uses AI to make tariff intelligence accessible.

---

## Product Architecture — Six Core Modules

### Module 1: Smart Tariff Calculator
- User inputs product description OR HTS code + country of origin
- AI (Claude) classifies product to correct HTS code if description provided
- Engine calculates total stacked duty rate across ALL applicable programs:
  - Section 232 (national security — steel, aluminum, autos, copper, etc.)
  - Section 301 (unfair trade practices — primarily China)
  - IEEPA (emergency tariffs — reciprocal rates, Canada/Mexico/China)
  - Antidumping/Countervailing duties (AD/CVD)
  - USMCA/trade agreement exemptions
- Returns breakdown showing each layer and total effective rate
- Supports batch lookups (upload CSV of products)

### Module 2: Real-Time Change Alert System
- Background workers monitor: Federal Register, CBP bulletins, executive orders, trade agreement updates
- Users create watchlists of HTS codes and countries they care about
- Push notifications and email digests when rates change for watched items
- Deadline alerts for exclusion applications, comment periods, rate changes
- Supreme Court IEEPA ruling tracker
- USMCA renegotiation impact alerts (July 2026)

### Module 3: Cost Impact Modeler
- Upload product catalog with COGS, margins, volume data
- Calculate tariff impact per SKU and total portfolio impact
- Scenario planning engine:
  - "What if IEEPA tariffs are struck down by Supreme Court?"
  - "What if China rates snap back to 145%?"
  - "What if USMCA renegotiation removes current exemptions?"
  - Custom rate scenarios
- Pass-through pricing calculator: model price increases vs. margin absorption
- Break-even analysis: when does a tariff make a product line unprofitable?
- Visual dashboards with charts showing impact over time

### Module 4: Alternative Sourcing Finder
- For any HTS code, identify countries with lower tariff rates
- Rank alternatives by: tariff savings %, trade agreement coverage, supply reliability
- Show tariff differential (e.g., "Vietnam vs. China saves 115% in duties")
- Flag countries with pending tariff investigations or rate changes
- Country risk scoring (political stability, trade relationship status)

### Module 5: Compliance Risk Scanner
- AI-powered HTS classification review — catch misclassifications before CBP does
- Flag products that may qualify for exclusions or duty drawback
- Identify transshipment risks and country-of-origin issues
- Track record-keeping requirements and documentation gaps
- Generate audit-ready compliance reports
- Penalty risk scoring per product

### Module 6: Export Reports & Sharing
- Professional PDF reports with DJ AI Business Consultant branding (phoenix logo)
- Excel/CSV exports of tariff data, cost models, and watchlists
- Shareable dashboard links with expiration and access controls
- Pre-formatted reports for SBA loan applications showing tariff impact
- Quarterly trade outlook summaries powered by AI analysis

---

## Tech Stack

### Backend
- **Framework:** Python 3.11+ / FastAPI with async endpoints
- **Database:** PostgreSQL with SQLAlchemy async ORM
- **Migrations:** Alembic
- **Cache:** Redis for tariff rate caching and session management
- **Task Queue:** Celery with Redis broker for background jobs (monitoring, alerts, report generation)
- **AI:** Anthropic Claude API (Sonnet) for classification, analysis, natural language queries
- **Data Pipeline:** Scheduled scrapers for Federal Register, CBP, trade data sources
- **Auth:** JWT tokens with refresh, bcrypt password hashing
- **Email:** SMTP integration for alerts and notifications

### Frontend
- **Framework:** Next.js 14+ with React
- **UI Library:** Shadcn/UI components
- **Charts:** Recharts for data visualization
- **State:** React Query for server state, Zustand for client state
- **Styling:** Tailwind CSS
- **Forms:** React Hook Form with Zod validation

### Infrastructure (Phase 4)
- Docker + docker-compose
- AWS or Azure deployment
- GitHub Actions CI/CD
- Stripe for subscription billing
- Swagger/OpenAPI documentation

---

## Database Schema

### Core Tables
```
users
  - id (UUID, PK)
  - email (unique, indexed)
  - password_hash
  - name
  - company_name
  - role (admin | user | viewer)
  - subscription_tier (free | pro | enterprise | consultant)
  - organization_id (FK, nullable)
  - created_at, updated_at

organizations
  - id (UUID, PK)
  - name
  - subscription_tier
  - max_users
  - created_at, updated_at
```

### Tariff Data Tables
```
hts_codes
  - id (PK)
  - code (indexed, e.g., "8471.30.0100")
  - description
  - unit_of_measure
  - general_rate
  - special_rates_json (trade agreements)
  - section_232_rate (nullable)
  - section_301_rate (nullable)
  - ieepa_rate (nullable)
  - ad_cvd_rates_json (nullable)
  - effective_date
  - last_updated
  - source_url

tariff_programs
  - id (PK)
  - name (e.g., "Section 232 Steel")
  - authority (232 | 301 | IEEPA | AD_CVD | USMCA)
  - status (active | paused | pending | expired)
  - affected_hts_codes_json
  - rate
  - country_scope_json
  - effective_date
  - expiration_date (nullable)
  - source_url
  - last_updated

countries
  - id (PK)
  - code (ISO 3166-1)
  - name
  - trade_agreements_json
  - current_tariff_status_json
  - risk_score
  - last_updated
```

### User Data Tables
```
watchlists
  - id (UUID, PK)
  - user_id (FK)
  - name
  - hts_codes_json
  - countries_json
  - alert_preferences_json
  - created_at, updated_at

product_catalogs
  - id (UUID, PK)
  - user_id (FK)
  - name
  - created_at, updated_at

catalog_items
  - id (UUID, PK)
  - catalog_id (FK)
  - product_name
  - hts_code (indexed)
  - country_of_origin
  - unit_cost
  - margin_percent
  - annual_volume
  - current_tariff_rate (calculated)
  - tariff_cost_annual (calculated)
  - created_at, updated_at

saved_scenarios
  - id (UUID, PK)
  - user_id (FK)
  - name
  - scenario_params_json
  - results_json
  - created_at

tariff_lookups
  - id (UUID, PK)
  - user_id (FK)
  - query_text
  - hts_code
  - country_of_origin
  - result_json
  - ai_classification_used (boolean)
  - created_at

alerts
  - id (UUID, PK)
  - user_id (FK)
  - alert_type (rate_change | deadline | new_program | exclusion)
  - title
  - body
  - hts_codes_json
  - read (boolean)
  - sent_at
  - created_at

audit_log
  - id (UUID, PK)
  - user_id (FK)
  - action (lookup | export | scenario | login)
  - details_json
  - ip_address
  - created_at
```

---

## API Endpoints

### Public
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
GET    /api/health
```

### Tariff Calculator (Module 1)
```
POST   /api/tariff/lookup
POST   /api/tariff/batch
GET    /api/tariff/hts/{code}
POST   /api/tariff/classify
GET    /api/tariff/programs
```

### Alerts & Watchlists (Module 2)
```
GET    /api/watchlists
POST   /api/watchlists
PUT    /api/watchlists/{id}
DELETE /api/watchlists/{id}
GET    /api/alerts
PUT    /api/alerts/{id}/read
GET    /api/alerts/preferences
PUT    /api/alerts/preferences
```

### Cost Modeler (Module 3)
```
POST   /api/catalog/upload
GET    /api/catalog/{id}/impact
POST   /api/scenarios
GET    /api/scenarios/{id}
POST   /api/scenarios/{id}/run
```

### Alternative Sourcing (Module 4)
```
GET    /api/sourcing/{hts_code}
GET    /api/sourcing/compare
```

### Compliance (Module 5)
```
POST   /api/compliance/review
GET    /api/compliance/risks
POST   /api/compliance/report
```

### Exports (Module 6)
```
POST   /api/export/pdf
POST   /api/export/csv
POST   /api/export/excel
POST   /api/share/link
```

### Admin
```
GET    /api/admin/users
GET    /api/admin/audit-log
GET    /api/admin/usage-stats
POST   /api/admin/tariff-data/refresh
```

---

## Implementation Phases

### PHASE 1: Foundation & Core Engine (Weeks 1-4)
Tasks in order:
1. Set up project structure (backend/, frontend/, docker/, docs/, assets/)
2. Copy logo files into assets/ directory
3. Configure FastAPI app with proper middleware (CORS, logging, error handling)
4. Set up PostgreSQL with SQLAlchemy async and Alembic migrations
5. Create all database models from schema above
6. Run initial migration
7. Build HTS code database — seed with current tariff data
8. Build tariff stacking calculation engine
9. Integrate Claude API for AI-assisted product classification
10. Build REST API endpoints for Module 1
11. Add JWT authentication (register, login, refresh)
12. Add health check endpoint
13. Add comprehensive logging throughout
14. Write unit tests for tariff calculation engine
15. Create requirements.txt with pinned versions
16. Set up proper .env and .gitignore

**Exit Criteria:** API accepts a product + country and returns accurate stacked tariff rate.

### PHASE 2: Web GUI (Weeks 5-10)
Tasks in order:
1. Initialize Next.js project with Tailwind and Shadcn/UI
2. Build layout: sidebar with phoenix logo, navigation, header with user menu
3. Build login/register pages
4. Build main dashboard page with summary stats
5. Build tariff search interface with AI classification toggle
6. Build AI chat interface for natural language tariff queries
7. Build watchlist management page
8. Build product catalog upload and management
9. Build data tables with sorting, filtering, pagination
10. Apply branding (phoenix logo, colors, "Transforming Business, Rising Above the Challenges")
11. Make fully responsive for mobile
12. Connect all frontend pages to backend API
13. Add loading states, error handling, empty states

**Exit Criteria:** Users can register, search tariffs, save watchlists, and interact with AI through a professional web interface.

### PHASE 3: Enterprise Features (Weeks 11-18)
Tasks in order:
1. Build Cost Impact Modeler (Module 3)
2. Build Change Alert System (Module 2)
3. Build Alternative Sourcing Finder (Module 4)
4. Build Compliance Risk Scanner (Module 5)
5. Build Export Reports with phoenix logo branding (Module 6)
6. Add role-based access control (admin, user, viewer)
7. Add multi-tenant organization support
8. Add audit logging for all actions
9. Add subscription tier enforcement

**Exit Criteria:** All six modules operational with subscription tier gating.

### PHASE 4: Scale & Monetize (Weeks 19-24)
Tasks in order:
1. Create Dockerfile and docker-compose.yml
2. Set up CI/CD with GitHub Actions
3. Deploy to AWS or Azure
4. Integrate Stripe for subscription billing
5. Build onboarding flow for new users
6. Generate Swagger/OpenAPI documentation
7. Add rate limiting and API throttling
8. Set up monitoring, alerting, and uptime checks
9. Build marketing landing page with phoenix branding
10. Performance optimization and load testing

**Exit Criteria:** Production-ready SaaS generating revenue.

---

## Pricing Tiers (Enforce in Code)

| Tier | Lookups/mo | Watchlists | Catalogs | Alerts | Exports | Users | API |
|------|-----------|------------|----------|--------|---------|-------|-----|
| Free | 10 | 1 | 0 | Email only | No | 1 | No |
| Pro ($49/mo) | Unlimited | 10 | 3 | All | Yes | 1 | No |
| Enterprise ($199/mo) | Unlimited | Unlimited | Unlimited | All | Yes | 10 | Yes |
| Consultant ($499/mo) | Unlimited | Unlimited | Unlimited | All | White-label | 50 | Yes |

---

## Branding

- **Company:** DJ AI Business Consultant
- **Location:** Syracuse, NY
- **Tagline:** Transforming Business, Rising Above the Challenges
- **Logo:** Phoenix design (assets/logo_withtitle1.avif + assets/logo.png)
- **Logo Usage:** Sidebar top-left, login page, PDF exports, marketing landing page, email headers
- **Primary Color:** #1E3A5F (navy)
- **Accent Color:** #4A90D9 (blue)
- **Secondary:** #0D9488 (teal)
- **Warning:** #D4A843 (gold)
- **Error:** #C0392B (red)
- **Footer:** "DJ AI Business Consultant • Syracuse, NY"

---

## Code Standards

- **Python:** PEP 8, type hints on all functions, async/await throughout
- **Error Handling:** Every endpoint wrapped in try/except with proper HTTP status codes
- **Logging:** Python logging module — INFO for operations, ERROR for failures, DEBUG for dev
- **No Hardcoded Values:** All config in .env
- **Input Validation:** Pydantic models for all request/response schemas
- **Security:** Never expose API keys, parameterized queries, CORS for production domains only
- **Database:** All changes through Alembic migrations, async sessions, proper indexing
- **AI Integration:** Token budgeting, response caching, domain-constrained system prompts
- **Testing:** Unit tests for core calculation engine, integration tests for API endpoints
- **Git:** Meaningful commit messages, feature branches, .gitignore protecting sensitive files

---

## Important Notes

- **WSL Path:** `/mnt/c/Projects/TariffNavigator/`
- **Windows Path:** `C:\Projects\TariffNavigator\`
- **Don't delete existing functionality** — extend and improve
- **Ask before breaking changes** to database schema
- **Test after every change** — run the app and verify
- **Keep UI professional** — this is client-facing, not a prototype
- **Mobile-first responsive design** — many users will be on phones
- **Accessibility matters** — proper labels, contrast ratios, keyboard navigation
