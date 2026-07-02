# TariffNavigator — Project Cheat Sheet
## Everything We've Done (Step by Step)

**Project:** TariffNavigator
**Location:** C:\Projects\TariffNavigator
**Owner:** Don Johnson — DJ AI Business Consultant (Syracuse, NY)
**Tagline:** Transforming Business, Rising Above the Challenges
**Logo:** Phoenix design (assets/logo_withtitle1.avif)

---

## STEP 1: Initial Claude Code Setup

**What we did:** Opened Claude Code and ran the first prompt to review the project.

```powershell
cd C:\Projects\TariffNavigator
npx @anthropic-ai/claude-code
```

**Problem encountered:** Claude Code uses a Linux/WSL shell, so Windows paths don't work.

| Format | Works? | Example |
|--------|--------|---------|
| Windows backslash | NO | `C:\Projects\TariffNavigator` |
| WSL mount path | YES | `/mnt/c/Projects/TariffNavigator` |
| Escaped backslash | YES | `C:\\Projects\\TariffNavigator` |

**Fix:** Always use `/mnt/c/Projects/TariffNavigator/` in Claude Code prompts.

---

## STEP 2: Market Research — Tariff Problems

**Key findings that shaped the product:**
- Tariff rates jumped from 2.4% to 18% in under 12 months
- CBP collected $216B in FY2025 (146% increase from 2024)
- 2,218 trade penalties issued for misclassification
- 80% of tariff costs absorbed by businesses in 2025 — flipping to consumers in 2026
- Small businesses hit first and hardest ("canary in the coal mine")
- Supreme Court reviewing IEEPA tariff legality — ruling expected 2026
- USMCA up for renegotiation July 2026
- No affordable tools exist for small businesses (enterprise tools = $500-2,000/month)

---

## STEP 3: Product Vision — Six Core Modules

| Module | What It Does |
|--------|-------------|
| 1. Smart Tariff Calculator | Stacked duty rates for any product + country |
| 2. Change Alert System | Real-time notifications when rates change |
| 3. Cost Impact Modeler | Scenario planning and pricing strategy tools |
| 4. Alt. Sourcing Finder | Find lower-tariff countries for same products |
| 5. Compliance Risk Scanner | AI classification review to prevent CBP penalties |
| 6. Export Reports | PDFs, CSVs, shareable dashboards |

---

## STEP 4: Enterprise Roadmap Created

**File:** `TariffNavigator_Enterprise_Roadmap.md`

Four phases: Foundation (Wk 1-4) → Web GUI (Wk 5-10) → Enterprise (Wk 11-18) → Scale (Wk 19-24)

**Pricing:**
| Tier | Price |
|------|-------|
| Free | $0/mo |
| Pro | $49/mo |
| Enterprise | $199/mo |
| Consultant | $499/mo |

---

## STEP 5: Pitch Deck Created

**File:** `TariffNavigator_PitchDeck.pptx` (10 slides with phoenix logo branding)

---

## STEP 6: CLAUDE.md Build Specification

**File:** `CLAUDE.md` — Drop in `C:\Projects\TariffNavigator\`

Master build spec with: database schema, all API endpoints, tech stack, branding (phoenix logo, colors), code standards, and phased implementation tasks.

---

## STEP 7: Claude Code Build Prompts

**File:** `CLAUDE_CODE_BUILD_PROMPTS.md`

| Prompt | What It Builds |
|--------|---------------|
| Step 1 | Folder structure, FastAPI app, .env, dependencies, middleware |
| Step 2 | All SQLAlchemy models, Alembic migration, table creation |
| Step 3 | JWT auth (register, login, refresh, roles, middleware) |
| Step 4 | Core stacking algorithm, AI classifier, seed data, API endpoints |
| Step 5 | Health check, full test, progress tracking |
| Phase 2 Kickoff | Next.js frontend with phoenix-branded dashboard |

---

## TESTING URLs

**Backend** (after `uvicorn app.main:app --reload`):

| Endpoint | URL | Method |
|----------|-----|--------|
| Health Check | `http://localhost:8000/api/health` | GET |
| Swagger Docs | `http://localhost:8000/docs` | GET |
| ReDoc | `http://localhost:8000/redoc` | GET |
| Register | `http://localhost:8000/api/auth/register` | POST |
| Login | `http://localhost:8000/api/auth/login` | POST |
| My Profile | `http://localhost:8000/api/auth/me` | GET (JWT) |
| Tariff Lookup | `http://localhost:8000/api/tariff/lookup` | POST (JWT) |
| AI Classify | `http://localhost:8000/api/tariff/classify` | POST (JWT) |
| HTS Code Detail | `http://localhost:8000/api/tariff/hts/{code}` | GET (JWT) |
| Active Programs | `http://localhost:8000/api/tariff/programs` | GET (JWT) |
| Watchlists | `http://localhost:8000/api/watchlists` | GET (JWT) |
| Alerts | `http://localhost:8000/api/alerts` | GET (JWT) |

**Frontend** (after `npm run dev` from frontend/):

| Page | URL |
|------|-----|
| Dashboard | `http://localhost:3000` |
| Login | `http://localhost:3000/login` |
| Register | `http://localhost:3000/register` |
| Tariff Search | `http://localhost:3000/search` |
| Watchlists | `http://localhost:3000/watchlists` |
| Cost Modeler | `http://localhost:3000/modeler` |
| Alerts | `http://localhost:3000/alerts` |
| Settings | `http://localhost:3000/settings` |

---

## QUICK TEST COMMANDS (curl)

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"don@djai.com","password":"testpass123","name":"Don Johnson","company_name":"DJ AI Business Consultant"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"don@djai.com","password":"testpass123"}'
```

**Tariff Lookup (replace YOUR_TOKEN):**
```bash
curl -X POST http://localhost:8000/api/tariff/lookup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"product_description":"steel rebar","country_code":"CN"}'
```

**AI Classification (replace YOUR_TOKEN):**
```bash
curl -X POST http://localhost:8000/api/tariff/classify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"description":"stainless steel bolts and fasteners for construction"}'
```

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

---

## FILES DELIVERED

| File | Purpose | Location |
|------|---------|----------|
| CLAUDE.md | Master build spec for Claude Code | Drop in C:\Projects\TariffNavigator\ |
| CLAUDE_CODE_BUILD_PROMPTS.md | Step-by-step build prompts | Reference — paste from it |
| TariffNavigator_Enterprise_Roadmap.md | Business roadmap | For planning/investors |
| TariffNavigator_PitchDeck.pptx | 10-slide pitch deck | For investor/client meetings |
| logo_withtitle1.avif | Phoenix logo | Drop in C:\Projects\TariffNavigator\assets\ |

---

## GIT BASICS

| Command | What It Does |
|---------|-------------|
| `git status` | See what's changed |
| `git add .` | Stage all changes |
| `git commit -m "message"` | Save changes locally |
| `git push origin master` | Upload to GitHub |
| `git pull origin master` | Download latest from GitHub |
| `git log --oneline` | See commit history |

**"Your branch is 1 commit ahead of origin/master"** = Local changes not yet pushed to GitHub. Run `git push origin master` to sync.

---

## WHAT TO DO NEXT

1. Create folder: `C:\Projects\TariffNavigator\assets\`
2. Copy `logo_withtitle1.avif` into `assets\`
3. Drop `CLAUDE.md` into `C:\Projects\TariffNavigator\`
4. Open PowerShell: `cd C:\Projects\TariffNavigator`
5. Launch Claude Code: `npx @anthropic-ai/claude-code`
6. Paste **Step 1** from `CLAUDE_CODE_BUILD_PROMPTS.md`
7. Verify, then paste Step 2, continue through Step 5
8. After Phase 1 is solid, paste the **Phase 2 Kickoff** prompt

---

*DJ AI Business Consultant — Transforming Business, Rising Above the Challenges*
*Syracuse, NY*
