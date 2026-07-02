# TariffNavigator Enterprise Roadmap
## From Tariff Lookup Tool to Small Business Survival Platform

**DJ AI Business Consultant | Syracuse, NY**
**Transforming Business, Rising Above the Challenges**
**Document Version:** 2.1 | **Date:** February 2026

---

## Executive Summary

U.S. tariff policy has created unprecedented chaos for American businesses. Average tariff rates jumped from 2.4% to 18% in under a year. Small businesses are absorbing costs they can't sustain, facing compliance penalties they don't understand, and navigating a policy environment that changes weekly. TariffNavigator will become the AI-powered platform that helps businesses survive and thrive in this new tariff reality.

---

## Market Problem

**The tariff crisis by the numbers:**

- $216 billion collected by CBP in FY2025 — a 146% increase from 2024
- 2,218 trade penalties issued by CBP in FY2025 for misclassification and evasion
- 80% of tariff costs absorbed by businesses in 2025 — projected to flip to consumers in 2026
- Average $1,300 per household tax increase from tariffs in 2026
- 60% of business leaders report being negatively affected by tariffs

**Who is hurting most:** Small businesses importing goods, manufacturers relying on foreign materials, construction companies buying steel and aluminum, healthcare organizations sourcing medical equipment and supplies, and retailers with overseas supply chains.

**What they lack:** Real-time tariff tracking, cost impact modeling, classification compliance tools, and alternative sourcing intelligence. Enterprise tools exist for Fortune 500 companies but nothing serves the small business market affordably.

---

## Product Vision

TariffNavigator transforms from a tariff code lookup tool into a comprehensive **Tariff Survival Platform** with six core modules:

### Module 1: Smart Tariff Calculator
- Input any product + country of origin
- Returns total stacked duty rate across ALL applicable tariff programs (Section 232, Section 301, IEEPA, antidumping, USMCA)
- Shows the layered tariff breakdown so businesses understand exactly what they owe
- HTS code lookup with AI-assisted classification
- Handles the complex tariff-on-tariff stacking that confuses most importers

### Module 2: Real-Time Change Alert System
- Monitors Federal Register, CBP bulletins, executive orders, and trade agreement updates
- Push notifications when tariff rates change for products in a user's watchlist
- Email digests (daily/weekly) summarizing all changes relevant to their business
- Deadline alerts for comment periods, exclusion applications, and rate changes
- Supreme Court IEEPA ruling tracker with impact projections

### Module 3: Cost Impact Modeler
- Upload product catalog with COGS and margin data
- Model how current and proposed tariffs affect profitability per SKU
- Scenario planning: What if IEEPA tariffs are struck down? What if China rates snap back to 145%?
- Pass-through pricing calculator: How much to raise prices vs. absorb
- Break-even analysis showing when tariff costs make a product line unprofitable
- USMCA renegotiation impact modeling for July 2026

### Module 4: Alternative Sourcing Finder
- For any HTS code, identify countries with lower tariff rates
- Rank alternatives by: tariff savings, existing trade agreements, supply reliability
- Show tariff differential (e.g., "Switching from China to Vietnam saves 115% in duties")
- Flag countries with pending tariff changes or investigations
- Provide sourcing contacts and trade facilitation resources

### Module 5: Compliance Risk Scanner
- AI-powered HTS classification review
- Flag potential misclassification risks before CBP audits
- Identify products that may qualify for exclusions or duty drawback
- Track record-keeping requirements and documentation gaps
- Generate audit-ready compliance reports
- Monitor for transshipment risks and country-of-origin issues

### Module 6: Export Reports & Intelligence
- Professional PDF reports with DJ AI Business Consultant phoenix branding
- Excel/CSV exports of tariff data and cost models
- Shareable dashboard links with expiration controls
- Pre-formatted reports for SBA loan applications showing tariff impact
- Quarterly trade outlook summaries powered by AI analysis

---

## Technical Architecture

### Current State
- Python/FastAPI backend with Uvicorn
- PostgreSQL database with SQLAlchemy ORM
- Alembic database migrations
- Claude API integration for AI analysis
- Static HTML/JS frontend

### Target Architecture

**Backend (Phase 1-2)**
- FastAPI with async endpoints
- PostgreSQL with Redis caching layer
- Celery for background jobs (tariff monitoring, alert processing)
- Claude API for AI classification and analysis
- Automated data pipeline for Federal Register and CBP data

**Frontend (Phase 2)**
- Next.js with React
- Shadcn/UI component library
- Recharts for data visualization
- Responsive design (mobile-first)
- Role-based dashboards (admin, business user, viewer)

**Infrastructure (Phase 3-4)**
- Docker containerization
- AWS or Azure deployment
- CI/CD via GitHub Actions
- Monitoring with uptime alerts
- Stripe billing integration

---

## Implementation Phases

### Phase 1: Foundation & Core Engine (Weeks 1-4)
**Goal:** Bulletproof backend with the Smart Tariff Calculator working

| Task | Effort | Impact |
|------|--------|--------|
| Fix all bugs, broken imports, missing error handling | Easy | High |
| Secure API keys, add .gitignore, environment config | Easy | High |
| Add comprehensive logging and health check endpoint | Easy | Medium |
| Build HTS code database with all current tariff rates | Medium | Critical |
| Implement tariff stacking logic (232 + 301 + IEEPA + AD/CVD) | Hard | Critical |
| Build AI-assisted product classification using Claude | Medium | High |
| Create REST API endpoints for tariff lookups | Medium | High |
| Pin all dependencies in requirements.txt | Easy | Medium |
| Write unit tests for tariff calculation engine | Medium | Medium |

**Deliverable:** Working API that accepts a product description or HTS code + country and returns the complete stacked tariff rate with breakdown.

---

### Phase 2: Web GUI & User Experience (Weeks 5-10)
**Goal:** Professional web dashboard that clients can use

| Task | Effort | Impact |
|------|--------|--------|
| Set up Next.js project with Shadcn/UI | Medium | High |
| Build main dashboard with tariff search interface | Medium | Critical |
| Create tariff results cards with rate breakdowns | Medium | High |
| Build AI chat interface for natural language queries | Medium | High |
| Add product watchlist functionality | Medium | High |
| Implement data tables with sorting, filtering, export | Medium | High |
| Create responsive mobile layout | Medium | Medium |
| Add dark/light mode | Easy | Low |
| DJ AI Business Consultant phoenix branding and styling | Easy | Medium |

**Deliverable:** Fully functional web app where users can search tariffs, save products, and interact with AI for tariff guidance.

---

### Phase 3: Enterprise Features (Weeks 11-18)
**Goal:** Features that make businesses pay for subscriptions

| Task | Effort | Impact |
|------|--------|--------|
| User authentication with JWT + role-based access | Hard | Critical |
| Cost Impact Modeler with scenario planning | Hard | Critical |
| Real-Time Change Alert System (Federal Register monitoring) | Hard | Critical |
| Alternative Sourcing Finder module | Medium | High |
| Compliance Risk Scanner with AI classification review | Hard | High |
| Export to PDF, CSV, Excel | Medium | High |
| Shareable report links with expiration | Medium | Medium |
| Audit logging (who searched what, when) | Medium | Medium |
| Email notification system | Medium | Medium |
| Multi-tenant workspaces for different client orgs | Hard | Medium |
| IEEPA Supreme Court scenario planner | Medium | High |
| USMCA renegotiation impact tool | Medium | High |

**Deliverable:** Full enterprise platform with all six core modules operational.

---

### Phase 4: Scale & Monetize (Weeks 19-24)
**Goal:** Production deployment with revenue

| Task | Effort | Impact |
|------|--------|--------|
| Docker containerization | Medium | High |
| Deploy to AWS/Azure | Medium | Critical |
| CI/CD pipeline with GitHub Actions | Medium | Medium |
| Stripe subscription billing (Free/Pro/Enterprise tiers) | Hard | Critical |
| API documentation with Swagger/OpenAPI | Medium | Medium |
| Rate limiting and throttling | Medium | Medium |
| Performance monitoring and alerting | Medium | Medium |
| Onboarding flow for new users | Medium | High |
| Customer support integration | Easy | Medium |
| Marketing landing page | Medium | High |

**Deliverable:** Production-ready SaaS platform generating revenue.

---

## Pricing Model

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0/month | 10 tariff lookups/month, basic HTS search, no exports |
| **Pro** | $49/month | Unlimited lookups, watchlists, alerts, PDF/CSV exports, cost modeler |
| **Enterprise** | $199/month | Everything in Pro + multi-user, API access, compliance scanner, custom reports |
| **Consultant** | $499/month | White-label option for trade consultants serving multiple clients |

---

## Target Market Segments

1. **Small Importers/Retailers** — Need to understand what they owe and when rates change
2. **Construction Companies** — Steel, aluminum, and materials tariff tracking
3. **Healthcare Organizations** — Medical device and pharmaceutical supply chain costs
4. **Manufacturers** — Raw material sourcing and cost management
5. **Trade Consultants & Customs Brokers** — White-label tools for their clients
6. **Accounting/CPA Firms** — Tariff impact reporting for business clients

---

## Key Milestones

| Date | Milestone |
|------|-----------|
| Month 1 | Phase 1 complete — Core tariff engine working |
| Month 2.5 | Phase 2 complete — Web GUI live for beta testers |
| Month 4.5 | Phase 3 complete — All six modules operational |
| Month 6 | Phase 4 complete — Production launch with paid subscriptions |
| Month 7 | First 50 paying customers |
| Month 12 | 500+ users, $15K+ MRR |

---

## Competitive Advantage

1. **AI-Powered:** Claude integration provides natural language tariff queries and intelligent classification — competitors require manual HTS code knowledge
2. **Small Business Focus:** Enterprise tools cost $500-2,000/month and require trade expertise — TariffNavigator starts free and speaks plain English
3. **Real-Time Alerts:** Most tools show static data — TariffNavigator monitors changes and proactively notifies users
4. **Scenario Planning:** No competing small business tool offers "what if" modeling for Supreme Court rulings, USMCA renegotiation, or rate snapbacks

---

*DJ AI Business Consultant — Transforming Business, Rising Above the Challenges*
*Syracuse, NY*
